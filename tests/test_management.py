from datetime import datetime, timedelta, timezone

from sqlalchemy import insert, select, update

from backend import db
from test_workflow import auth, client, request


def approval_csv(*rows):
    expiry = (datetime.now(timezone.utc) + timedelta(days=60)).isoformat()
    return "farmer_id,name,location,limit_cents,expires_at,approval_reference\n" + "\n".join(
        f"{farmer_id},{name},Nakuru,{limit},{expiry},BANK-001" for farmer_id, name, limit in rows
    )


def test_approval_preview_then_import_and_new_farmer_login(client):
    lender = auth(client, "lender-demo")
    content = approval_csv(("farmer-new", "New Farmer", 12000))
    preview = client.post("/api/approvals/import", headers=lender, json={"csv_text": content}).json()
    assert preview["rows"][0]["change"] == "create"
    assert len(client.get("/api/state", headers=lender).json()["farmers"]) == 2
    assert client.post("/api/approvals/import", headers=lender, json={"csv_text": content, "preview": False}).status_code == 200
    # Reimport updates without resetting spent/reserved balances.
    newcomer = auth(client, "farmer-new")
    assert request(client, newcomer).status_code == 201
    assert client.post("/api/approvals/import", headers=lender, json={"csv_text": content, "preview": False}).status_code == 200
    farmer = client.get("/api/state", headers=newcomer).json()["farmers"][0]
    assert farmer["reserved_cents"] == 9000 and farmer["name"] == "New Farmer"
    assert client.get("/api/state", headers=newcomer).json()["user"]["name"] == "New Farmer"
    assert any(row["id"] == "farmer-new" for row in client.get("/api/participants", headers=lender).json())
    assert not any(row["id"] == "farmer-new" for row in client.get("/api/personas").json())


def test_approval_import_is_atomic_and_rechecks_after_preview(client):
    lender, farmer = auth(client, "lender-demo"), auth(client, "farmer-amina")
    content = approval_csv(("farmer-new", "New Farmer", 10000), ("farmer-amina", "Amina Wanjiku", 8000))
    assert client.post("/api/approvals/import", headers=lender, json={"csv_text": content}).status_code == 200
    assert request(client, farmer).status_code == 201
    response = client.post("/api/approvals/import", headers=lender, json={"csv_text": content, "preview": False})
    assert response.status_code == 409
    data = client.get("/api/state", headers=lender).json()
    assert len(data["farmers"]) == 2
    assert next(row for row in data["farmers"] if row["id"] == "farmer-amina")["limit_cents"] == 15000


def test_import_rejects_duplicate_malformed_expired_and_foreign_approvals(client):
    lender = auth(client, "lender-demo")
    content = approval_csv(("farmer-amina", "Amina", 10000))
    for invalid in [content + "\n" + content.splitlines()[1], content.replace("10000", "1e4"),
                    content.replace("10000", "10.00"), content.replace("Nakuru", ""),
                    "bad,header\nx,y", content.replace(content.splitlines()[1].split(',')[4], "2020-01-01T00:00:00Z")]:
        assert client.post("/api/approvals/import", headers=lender, json={"csv_text": invalid, "preview": False}).status_code == 422
    with db.engine.begin() as conn:
        conn.execute(update(db.farmers).where(db.farmers.c.id == "farmer-amina").values(lender_id="other-lender"))
    assert client.post("/api/approvals/import", headers=lender, json={"csv_text": content}).status_code == 403
    assert client.post("/api/approvals/import", headers=auth(client, "supplier-demo"), json={"csv_text": content}).status_code == 403


def test_catalogue_edit_preserves_order_snapshot_and_reserved_stock(client):
    farmer, supplier = auth(client, "farmer-amina"), auth(client, "supplier-demo")
    order = request(client, farmer).json()
    product = next(p for p in client.get("/api/state", headers=supplier).json()["products"] if p["id"] == "dap-50")
    values = {key: product[key] for key in ["name", "category", "unit", "price_cents", "stock", "revision"]}
    assert client.put("/api/products/dap-50", headers=supplier, json={**values, "stock": 1}).status_code == 409
    assert client.put("/api/products/dap-50", headers=supplier, json={**values, "price_cents": 5500, "stock": 50}).status_code == 200
    # Same stale form cannot overwrite a new price/count.
    assert client.put("/api/products/dap-50", headers=supplier, json=values).status_code == 409
    saved = client.get("/api/state", headers=farmer).json()
    assert saved["orders"][0]["amount_cents"] == order["amount_cents"] == 9000
    assert saved["orders"][0]["items"][0]["price_cents"] == 4500
    assert next(p for p in saved["products"] if p["id"] == "dap-50")["reserved"] == 2


def test_catalogue_new_product_permissions_and_concurrent_reservation(client):
    supplier, farmer = auth(client, "supplier-demo"), auth(client, "farmer-amina")
    values = {"name": "Beans", "category": "Seed", "unit": "1 kg pack", "price_cents": 800, "stock": 10}
    assert client.put("/api/products/beans-1", headers=farmer, json=values).status_code == 403
    assert client.put("/api/products/beans-1", headers=supplier, json={**values, "price_cents": 1.5}).status_code == 422
    assert client.put("/api/products/beans-1", headers=supplier, json=values).status_code == 200
    product = next(p for p in client.get("/api/state", headers=supplier).json()["products"] if p["id"] == "beans-1")
    assert request(client, farmer, product="beans-1").status_code == 201
    assert client.put("/api/products/beans-1", headers=supplier, json={**values, "revision": product["revision"]}).status_code == 409
    with db.engine.begin() as conn:
        conn.execute(insert(db.products).values(id="foreign-product", supplier_id="another-supplier", name="Other", category="Seed", unit="Pack", price_cents=100, stock=10))
    assert client.put("/api/products/foreign-product", headers=supplier, json=values).status_code == 404
    assert all(p["id"] != "foreign-product" for p in client.get("/api/state", headers=supplier).json()["products"])
    with db.engine.connect() as conn:
        assert conn.execute(select(db.management_events).where(db.management_events.c.action == "PRODUCT_SAVED")).mappings().first()
