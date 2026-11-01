import json

import httpx
import pytest
from Backend.tests.test_workflow import application, auth, client
from fastapi import HTTPException
from sqlalchemy import select

from Backend import advisory, graph_context, store

EVIDENCE = {
    "farmer_id": "F-101",
    "provenance": "synthetic_replay",
    "relationship_count": 3,
    "relationship_types": [],
    "public_weather_context": [],
}
VALID = {
    "headline": "Synthetic evidence needs lender review.",
    "observations": [
        {
            "text": "Three retrieved relationships are available.",
            "evidence_ids": ["graph"],
        }
    ],
    "missing_evidence": [
        "Verified income and observed real-world repayment outcomes are missing."
    ],
}


def provider(monkeypatch, result):
    monkeypatch.setenv("CREDIT_AI_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "isolated-test-key")
    monkeypatch.setenv("CREDIT_RECOMMENDATION_MODEL", "gemini-3.5-flash-lite")
    original = httpx.Client
    requests = []

    def respond(request):
        requests.append(json.loads(request.content))
        return httpx.Response(
            200,
            json={
                "candidates": [{"content": {"parts": [{"text": json.dumps(result)}]}}]
            },
        )

    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kwargs: original(transport=httpx.MockTransport(respond), **kwargs),
    )
    return requests


def test_summary_uses_only_known_evidence_and_preserves_no_decision_authority(
    client, monkeypatch
):
    headers = auth(client)
    case = application(client, headers)
    monkeypatch.setattr(graph_context, "context", lambda *args: EVIDENCE)
    captured = provider(monkeypatch, VALID)
    result = client.post(
        f"/api/applications/{case['id']}/recommendation", headers=headers
    )
    assert result.status_code == 200
    assert result.json()["authority"] == "advisory_only"
    assert result.json()["observations"][0]["evidence_ids"] == ["graph"]
    assert captured and "systemInstruction" in captured[0]
    with store.engine.connect() as conn:
        assert conn.execute(select(store.decisions)).first() is None
        assert conn.execute(select(store.outbox)).first() is None
        assert conn.execute(select(store.evaluations)).first() is not None


@pytest.mark.parametrize(
    "result",
    [
        {**VALID, "score": 850},
        {
            **VALID,
            "observations": [
                {"text": "Invented citation", "evidence_ids": ["unretrieved-record"]}
            ],
        },
        {**VALID, "missing_evidence": []},
    ],
)
def test_invalid_or_uncited_model_results_are_unavailable(monkeypatch, result):
    provider(monkeypatch, result)
    with pytest.raises(HTTPException) as error:
        advisory.summarize(EVIDENCE, "synthetic")
    assert error.value.status_code == 502


def test_real_case_does_not_send_data_to_the_prototype_provider(monkeypatch):
    requests = provider(monkeypatch, VALID)
    with pytest.raises(HTTPException) as error:
        advisory.summarize(EVIDENCE, "real")
    assert error.value.status_code == 409 and not requests


def test_minor_units_are_formatted_before_provider_and_wrong_scale_is_rejected(monkeypatch):
    evidence = {
        **EVIDENCE,
        "repayment_history": {
            "available": True,
            "currency": "KES",
            "loan_count": 2,
            "principal_minor": 9600000,
            "repaid_minor": 9600000,
            "outstanding_minor": 0,
        },
    }
    wrong = {
        **VALID,
        "observations": [
            {"text": "Principal is KES 9,600,000.00.", "evidence_ids": ["repayment"]}
        ],
    }
    captured = provider(monkeypatch, wrong)
    with pytest.raises(HTTPException) as error:
        advisory.summarize(evidence, "synthetic")
    assert error.value.status_code == 502
    facts = json.loads(captured[0]["contents"][0]["parts"][0]["text"])
    history = next(f["value"] for f in facts if f["id"] == "repayment")
    assert history["principal_amount"] == "KES 96,000.00"
    assert "principal_minor" not in history


def test_summary_and_evidence_routes_enforce_lender_scope(client, monkeypatch):
    case = application(client, auth(client))

    def forbidden(*args):
        raise AssertionError("Cross-lender requests must not retrieve graph records")

    monkeypatch.setattr(graph_context, "context", forbidden)
    monkeypatch.setattr(graph_context, "record", forbidden)
    other = auth(client, "b")
    assert (
        client.post(
            f"/api/applications/{case['id']}/recommendation", headers=other
        ).status_code
        == 404
    )
    assert (
        client.get(
            f"/api/applications/{case['id']}/evidence/record-1", headers=other
        ).status_code
        == 404
    )
