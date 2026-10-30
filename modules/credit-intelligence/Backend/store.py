"""Durable lender workflow, isolated from graph research and payment execution."""

import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    create_engine,
    event,
)

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
metadata = MetaData()
officers = Table(
    "officers",
    metadata,
    Column("id", String, primary_key=True),
    Column("lender_id", String, nullable=False),
    Column("password_hash", String, nullable=False),
    Column("enabled", Integer, nullable=False, default=1),
    Column("failures", Integer, nullable=False, default=0),
    Column("locked_until", String, nullable=False, default=""),
)
sessions = Table(
    "officer_sessions",
    metadata,
    Column("token_hash", String, primary_key=True),
    Column("officer_id", String, nullable=False),
    Column("expires_at", String, nullable=False),
)
applications = Table(
    "applications",
    metadata,
    Column("id", String, primary_key=True),
    Column("farmer_id", String, nullable=False, index=True),
    Column("input_farmer_id", String, nullable=False),
    Column("lender_id", String, nullable=False, index=True),
    Column("status", String, nullable=False),
    Column("provenance", String, nullable=False),
    Column("created_at", String, nullable=False),
    Column("request_id", String, nullable=False),
    UniqueConstraint("lender_id", "request_id"),
)
decisions = Table(
    "lender_decisions",
    metadata,
    Column("id", String, primary_key=True),
    Column("application_id", String, nullable=False, unique=True),
    Column("lender_id", String, nullable=False, index=True),
    Column("officer_id", String, nullable=False),
    Column("decision", String, nullable=False),
    Column("terms", Text, nullable=False),
    Column("reason", Text, nullable=False),
    Column("created_at", String, nullable=False),
    Column("revoked_at", String),
    Column("revocation_reason", Text),
)
outbox = Table(
    "decision_outbox",
    metadata,
    Column("id", String, primary_key=True),
    Column("decision_id", String, nullable=False),
    Column("lender_id", String, nullable=False),
    Column("kind", String, nullable=False),
    Column("body", Text, nullable=False),
    Column("status", String, nullable=False),
    Column("attempts", Integer, nullable=False, default=0),
    Column("next_attempt", String, nullable=False),
    Column("lease_until", String, nullable=False, default=""),
    Column("last_error", Text),
    Column("receipt", Text),
    UniqueConstraint("decision_id", "kind"),
)
evaluations = Table(
    "recommendation_records",
    metadata,
    Column("id", String, primary_key=True),
    Column("application_id", String, nullable=False),
    Column("officer_id", String, nullable=False),
    Column("result", Text, nullable=False),
    Column("created_at", String, nullable=False),
)


def now():
    return datetime.now(timezone.utc).isoformat()


def make_engine(url):
    engine = create_engine(
        url,
        connect_args={"check_same_thread": False, "timeout": 30}
        if url.startswith("sqlite")
        else {},
        pool_pre_ping=True,
    )
    if url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def configure(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA journal_mode=WAL")

    return engine


(ROOT / "data").mkdir(exist_ok=True)
engine = make_engine(
    os.getenv(
        "CREDIT_DATABASE_URL", f"sqlite:///{ROOT / 'data' / 'credit-workflow.db'}"
    )
)


def initialize():
    metadata.create_all(engine)
