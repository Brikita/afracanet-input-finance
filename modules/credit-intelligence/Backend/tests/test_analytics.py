import pytest
from Backend.tests.test_workflow import application, auth, terms
from Backend.tests.test_workflow import client as credit_client
from sqlalchemy import select

from Backend import analytics, store

client = credit_client


def result(lender, farmer, identifier):
    return {
        "id": identifier,
        "lender_id": lender,
        "created_at": "2026-11-02T10:00:00+00:00",
        "manifest_sha256": "a" * 64,
        "source_kind": "synthetic_replay",
        "authority": "descriptive_analytics_only",
        "calibrated_credit_score": None,
        "nodes": [{"id": farmer, "page_rank": 1.0, "community": 0}],
        "links": [],
    }


def test_read_analytics_is_scoped_and_never_creates_authority(client):
    headers = auth(client)
    app = application(client, headers)
    path = f"/api/applications/{app['id']}/analytics"
    assert client.get(path).status_code == 401
    assert client.get(path, headers=auth(client, "b")).status_code == 404
    assert client.get(path, headers=headers).json()["available"] is False
    analytics.save(result("lender-b", "F-101", "foreign"))
    assert client.get(path, headers=headers).json()["available"] is False
    analytics.save(result("lender-a", "F-101", "own"))
    response = client.get(path, headers=headers)
    assert response.json()["id"] == "own"
    assert response.json()["calibrated_credit_score"] is None
    with store.engine.connect() as conn:
        assert conn.execute(select(store.decisions)).first() is None
        assert conn.execute(select(store.outbox)).first() is None


def test_missing_farmer_is_not_given_another_nodes_metric(client):
    analytics.save(result("lender-a", "another-farmer", "other"))
    assert analytics.read("F-101", "lender-a")["available"] is False


def test_historical_run_and_saved_summary_are_scoped_and_do_not_call_ai(
    client, monkeypatch
):
    import json

    from sqlalchemy import insert

    from Backend import advisory

    headers = auth(client)
    app = application(client, headers)
    analytics.save(result("lender-a", "F-101", "historical"))
    newer = result("lender-a", "F-101", "newer")
    newer["created_at"] = "2026-11-03T00:00:00+00:00"
    analytics.save(newer)
    path = f"/api/applications/{app['id']}"
    assert client.get(path + "/analytics", headers=headers).json()["id"] == "newer"
    assert (
        client.get(path + "/analytics?run_id=historical", headers=headers).json()["id"]
        == "historical"
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("Reading a stored evaluation must not call a provider")

    monkeypatch.setattr(advisory, "summarize", forbidden)
    with store.engine.begin() as conn:
        conn.execute(
            insert(store.evaluations).values(
                id="saved",
                application_id=app["id"],
                officer_id="officer-a",
                result=json.dumps({"headline": "Recorded advisory evidence"}),
                created_at=store.now(),
            )
        )
    assert (
        client.get(path + "/evaluations/saved", headers=headers).json()["headline"]
        == "Recorded advisory evidence"
    )
    assert (
        client.get(path + "/evaluations/saved", headers=auth(client, "b")).status_code
        == 404
    )


def test_decision_rejects_foreign_analytics_and_pins_reviewed_manifest(client):
    import json

    headers = auth(client)
    app = application(client, headers)
    path = f"/api/applications/{app['id']}/decisions"
    analytics.save(result("lender-b", "F-101", "foreign"))
    body = {**terms(), "analytics_run_id": "foreign"}
    assert client.post(path, headers=headers, json=body).status_code == 409
    analytics.save(result("lender-a", "F-101", "reviewed"))
    body["analytics_run_id"] = "reviewed"
    body["evaluation_id"] = "missing-evaluation"
    assert client.post(path, headers=headers, json=body).status_code == 409
    body.pop("evaluation_id")
    response = client.post(path, headers=headers, json=body)
    assert response.status_code == 200
    recorded = json.loads(response.json()["terms"])
    assert recorded["analytics_run_id"] == "reviewed"
    assert recorded["evidence_manifest_sha256"] == "a" * 64
    assert (
        client.post(path, headers=headers, json=body).json()["id"]
        == response.json()["id"]
    )


class FakeRow:
    def __init__(self, value):
        self.value = value

    def single(self):
        return self.value


class OversizedSession:
    def run(self, query, **parameters):
        if "gds.version" in query:
            return FakeRow({"version": "test"})
        if "JudgeDataset" in query:
            return FakeRow({"fingerprint": "a" * 64, "as_of": "2026-10-26"})
        if "AS nodes" in query:
            return FakeRow({"nodes": 10001})
        if "AS edges" in query:
            return FakeRow({"edges": 1})
        raise AssertionError("GDS projection must not start for an oversized graph")


def test_oversized_projection_is_rejected_before_creation():
    with pytest.raises(ValueError, match="bounded judge limits"):
        analytics.compute(OversizedSession(), "lender-a")
