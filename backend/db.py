from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import (
    JSON, CheckConstraint, Column, ForeignKey, Identity, Integer, MetaData,
    String, Table, Text, UniqueConstraint, create_engine, event, insert, select,
)

from .config import ROOT, settings

metadata = MetaData()
farmers = Table(
    "farmers", metadata,
    Column("id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("location", String, nullable=False),
    Column("lender_id", String, nullable=False, index=True),
    Column("limit_cents", Integer, nullable=False),
    Column("reserved_cents", Integer, nullable=False, default=0),
    Column("spent_cents", Integer, nullable=False, default=0),
    Column("expires_at", String, nullable=False),
    Column("approval_reference", String, nullable=False),
    CheckConstraint("reserved_cents >= 0 AND spent_cents >= 0 AND limit_cents >= reserved_cents + spent_cents"),
)
products = Table(
    "products", metadata,
    Column("id", String, primary_key=True),
    Column("supplier_id", String, nullable=False, index=True),
    Column("name", String, nullable=False),
    Column("category", String, nullable=False),
    Column("unit", String, nullable=False),
    Column("price_cents", Integer, nullable=False),
    Column("stock", Integer, nullable=False),
    Column("reserved", Integer, nullable=False, default=0),
    CheckConstraint("price_cents > 0 AND reserved >= 0 AND stock >= reserved"),
)
orders = Table(
    "orders", metadata,
    Column("id", Integer, Identity(), primary_key=True),
    Column("farmer_id", ForeignKey("farmers.id"), nullable=False, index=True),
    Column("lender_id", String, nullable=False, index=True),
    Column("supplier_id", String, nullable=False, index=True),
    Column("client_request_id", String, nullable=False),
    Column("items", JSON, nullable=False),
    Column("amount_cents", Integer, nullable=False),
    Column("currency", String, nullable=False, default="USD"),
    Column("status", String, nullable=False, index=True),
    Column("payment_mode", String, nullable=False),
    Column("invoice_id", String, unique=True),
    Column("payment_url", Text),
    Column("payment_reference", String),
    Column("pickup_code", String),
    Column("created_at", String, nullable=False),
    Column("updated_at", String, nullable=False),
    UniqueConstraint("farmer_id", "client_request_id"),
    CheckConstraint("amount_cents > 0"),
)
audit = Table(
    "audit_events", metadata,
    Column("id", Integer, Identity(), primary_key=True),
    Column("order_id", ForeignKey("orders.id"), nullable=False, index=True),
    Column("actor", String, nullable=False),
    Column("action", String, nullable=False),
    Column("detail", Text, nullable=False),
    Column("created_at", String, nullable=False),
)
sessions = Table(
    "sessions", metadata,
    Column("token_hash", String, primary_key=True),
    Column("role", String, nullable=False),
    Column("subject", String, nullable=False),
    Column("expires_at", String, nullable=False),
)
webhook_events = Table(
    "webhook_events", metadata,
    Column("id", String, primary_key=True),
    Column("received_at", String, nullable=False),
)
management_events = Table(
    "management_events", metadata,
    Column("id", Integer, Identity(), primary_key=True),
    Column("actor", String, nullable=False, index=True),
    Column("action", String, nullable=False),
    Column("detail", JSON, nullable=False),
    Column("created_at", String, nullable=False),
)
issues = Table(
    "order_issues", metadata,
    Column("id", Integer, Identity(), primary_key=True),
    Column("order_id", ForeignKey("orders.id"), nullable=False, index=True),
    Column("client_request_id", String, nullable=False),
    Column("category", String, nullable=False),
    Column("detail", Text, nullable=False),
    Column("reported_by", String, nullable=False),
    Column("created_at", String, nullable=False),
    Column("resolved_by", String),
    Column("resolved_at", String),
    Column("resolution", Text),
    UniqueConstraint("order_id", "client_request_id"),
)
contacts = Table(
    "farmer_contacts", metadata,
    Column("farmer_id", ForeignKey("farmers.id"), primary_key=True),
    Column("phone", String, nullable=False, unique=True),
    Column("language", String, nullable=False),
    Column("consented_at", String),
    Column("verified_at", String),
    Column("verification_hash", String),
    Column("verification_expires_at", String),
    Column("verification_attempts", Integer, nullable=False, default=0),
    Column("verification_mode", String, nullable=False),
    Column("updated_at", String, nullable=False),
)
sms_outbox = Table(
    "sms_outbox", metadata,
    Column("id", Integer, Identity(), primary_key=True),
    Column("farmer_id", ForeignKey("farmers.id"), nullable=False, index=True),
    Column("order_id", ForeignKey("orders.id")),
    Column("event_key", String, nullable=False, unique=True),
    Column("action", String, nullable=False),
    Column("phone", String, nullable=False),
    Column("body", Text, nullable=False),
    Column("mode", String, nullable=False),
    Column("status", String, nullable=False, default="QUEUED", index=True),
    Column("provider_id", String),
    Column("detail", String),
    Column("created_at", String, nullable=False),
    Column("updated_at", String, nullable=False),
)


def now():
    return datetime.now(timezone.utc).isoformat()


def build_engine(url):
    options = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        (ROOT / "data").mkdir(exist_ok=True)
        options["connect_args"] = {"check_same_thread": False, "timeout": 30}
    result = create_engine(url, **options)
    if url.startswith("sqlite"):
        @event.listens_for(result, "connect")
        def sqlite_settings(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA journal_mode=WAL")
    return result


engine = build_engine(settings.database_url)


def initialize():
    metadata.create_all(engine)
    with engine.begin() as conn:
        if conn.execute(select(farmers.c.id).limit(1)).first():
            return
        expires = (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()
        conn.execute(insert(farmers), [
            {"id": "farmer-amina", "name": "Amina Wanjiku", "location": "Nakuru · Maize",
             "lender_id": "lender-demo", "limit_cents": 15000, "reserved_cents": 0,
             "spent_cents": 0, "expires_at": expires, "approval_reference": "DEMO-APP-001"},
            {"id": "farmer-kiptoo", "name": "David Kiptoo", "location": "Uasin Gishu · Maize",
             "lender_id": "lender-demo", "limit_cents": 7500, "reserved_cents": 0,
             "spent_cents": 0, "expires_at": expires, "approval_reference": "DEMO-APP-002"},
        ])
        conn.execute(insert(products), [
            {"id": "dap-50", "supplier_id": "supplier-demo", "name": "DAP fertilizer",
             "category": "Fertilizer", "unit": "50 kg bag", "price_cents": 4500, "stock": 40, "reserved": 0},
            {"id": "dap-25", "supplier_id": "supplier-demo", "name": "DAP fertilizer",
             "category": "Fertilizer", "unit": "25 kg bag", "price_cents": 2400, "stock": 30, "reserved": 0},
            {"id": "seed-2", "supplier_id": "supplier-demo", "name": "Maize seed",
             "category": "Seed", "unit": "2 kg pack", "price_cents": 1800, "stock": 60, "reserved": 0},
        ])


def record(conn, order_id, actor, action, detail):
    event_id = conn.execute(insert(audit).values(
        order_id=order_id, actor=actor, action=action, detail=detail, created_at=now(),
    )).inserted_primary_key[0]
    from .notifications import enqueue_event
    enqueue_event(conn, order_id, event_id, action)
