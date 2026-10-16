from sqlalchemy import update

from backend import db
from backend.config import settings
from test_workflow import auth, client, prepared, request, valid_invoice


def report(client, order_id, headers, key="issue-request-01"):
    return client.post(f"/api/orders/{order_id}/issues", headers=headers, json={
        "client_request_id": key, "category": "stock", "detail": "Dealer needs to confirm the seed batch.",
    })


def test_issue_report_retries_do_not_duplicate_and_resolutions_are_lender_only(client):
    order_id, farmer, lender, supplier = prepared(client)
    path = f"/api/orders/{order_id}/issues"
    issue_id = report(client, order_id, farmer).json()["id"]
    assert report(client, order_id, farmer).json()["id"] == issue_id
    assert client.post(path, headers=farmer, json={"client_request_id": "issue-request-01", "category": "stock", "detail": "A different report"}).status_code == 409
    other = auth(client, "farmer-kiptoo")
    assert report(client, order_id, other).status_code == 404
    resolution_path = f"{path}/{issue_id}/resolve"
    payload = {"resolution": "Dealer confirmed the correct batch is available."}
    for headers in [farmer, supplier]:
        assert client.post(resolution_path, headers=headers, json=payload).status_code == 403
    assert client.post(resolution_path, headers=lender, json=payload).status_code == 200
    assert client.post(resolution_path, headers=lender, json=payload).status_code == 200
    assert client.post(resolution_path, headers=lender, json={"resolution": "Changed resolution"}).status_code == 409
    events = client.get(f"/api/orders/{order_id}/timeline", headers=farmer).json()
    assert sum(e["action"] == "ISSUE_REPORTED" for e in events) == 1
    assert sum(e["action"] == "ISSUE_RESOLVED" for e in events) == 1


def test_issue_pauses_approval_and_invoice_but_allows_preinvoice_cancellation(client):
    farmer, lender, supplier = [auth(client, p) for p in ["farmer-amina", "lender-demo", "supplier-demo"]]
    order_id = request(client, farmer).json()["id"]
    issue_id = report(client, order_id, supplier).json()["id"]
    assert client.post(f"/api/orders/{order_id}/approve", headers=lender).status_code == 409
    assert client.post(f"/api/orders/{order_id}/issues/{issue_id}/resolve", headers=lender, json={"resolution": "Stock confirmed with the supplier."}).status_code == 200
    assert client.post(f"/api/orders/{order_id}/approve", headers=lender).status_code == 200
    assert report(client, order_id, farmer, key="second-issue-request").status_code == 201
    assert client.post(f"/api/orders/{order_id}/invoice", headers=supplier).status_code == 409
    assert client.post(f"/api/orders/{order_id}/cancel", headers=farmer).status_code == 200
    data = client.get("/api/state", headers=farmer).json()
    assert data["farmers"][0]["reserved_cents"] == 0
    assert len(data["orders"][0]["issues"]) == 2


def test_issue_holds_payment_initiation_and_collection_without_changing_money(client):
    order_id, farmer, lender, supplier = prepared(client)
    issue_id = report(client, order_id, farmer).json()["id"]
    assert client.post(f"/api/orders/{order_id}/demo-pay", headers=lender).status_code == 409
    assert client.post(f"/api/orders/{order_id}/issues/{issue_id}/resolve", headers=lender, json={"resolution": "Supplier and farmer agreed the stock is correct."}).status_code == 200
    assert client.post(f"/api/orders/{order_id}/demo-pay", headers=lender).status_code == 200
    code = client.get("/api/state", headers=farmer).json()["orders"][0]["pickup_code"]
    issue_id = report(client, order_id, supplier, key="collection-issue-request").json()["id"]
    assert "pickup_code" not in client.get("/api/state", headers=farmer).json()["orders"][0]
    assert client.post(f"/api/orders/{order_id}/collect", headers=supplier, json={"code": code}).status_code == 409
    assert client.post(f"/api/orders/{order_id}/issues/{issue_id}/resolve", headers=lender, json={"resolution": "Collection arranged with farmer for tomorrow."}).status_code == 200
    state = client.get("/api/state", headers=farmer).json()
    assert state["farmers"][0]["spent_cents"] == 9000 and state["orders"][0]["status"] == "READY_FOR_COLLECTION"
    assert client.post(f"/api/orders/{order_id}/collect", headers=supplier, json={"code": code}).status_code == 200
    assert client.post(f"/api/orders/{order_id}/collect", headers=supplier, json={"code": code}).status_code == 200
    final = client.get("/api/state", headers=supplier).json()
    assert next(p for p in final["products"] if p["id"] == "dap-50")["stock"] == 38
    assert sum(e["action"] == "COLLECTED" for e in client.get(f"/api/orders/{order_id}/timeline", headers=farmer).json()) == 1


def test_incoming_real_payment_is_reconciled_even_when_issue_is_open(client, monkeypatch):
    order_id, farmer, lender, supplier = prepared(client)
    report(client, order_id, farmer)
    with db.engine.begin() as conn:
        conn.execute(update(db.orders).where(db.orders.c.id == order_id).values(payment_mode="sandbox", invoice_id="INV2-TEST", payment_url="https://www.sandbox.paypal.com/invoice/p/#test"))
    monkeypatch.setattr(settings, "payment_mode", "sandbox")
    monkeypatch.setattr("backend.main.PayPal.get", lambda *args: valid_invoice())
    assert client.post(f"/api/orders/{order_id}/reconcile", headers=lender).json()["confirmed"]
    assert client.post(f"/api/orders/{order_id}/reconcile", headers=lender).json()["confirmed"]
    state = client.get("/api/state", headers=farmer).json()
    assert state["farmers"][0]["spent_cents"] == 9000
    assert "pickup_code" not in state["orders"][0]
    assert "payment_url" not in client.get("/api/state", headers=lender).json()["orders"][0]
    assert len(client.get("/api/state", headers=auth(client, "farmer-kiptoo")).json()["orders"]) == 0


def test_blank_reports_and_resolutions_rejected_and_wrong_issue_scoped(client):
    order_id, farmer, lender, supplier = prepared(client)
    assert client.post(f"/api/orders/{order_id}/issues", headers=farmer, json={"client_request_id": "blank-issue-request", "category": "other", "detail": "      "}).status_code == 422
    issue_id = report(client, order_id, farmer).json()["id"]
    assert client.post(f"/api/orders/{order_id}/issues/{issue_id}/resolve", headers=lender, json={"resolution": "     "}).status_code == 422
    assert client.post(f"/api/orders/{order_id}/issues/99999/resolve", headers=lender, json={"resolution": "Confirmed with participants."}).status_code == 404
