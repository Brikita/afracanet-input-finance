"""Credit workflow API. Lender authority is separate from graph recommendations."""

import asyncio
import contextlib
import json
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
from . import advisory, delivery, graph_context, identity, store, workflow


async def worker():
    while True:
        try:
            await asyncio.to_thread(delivery.tick)
        except Exception:
            pass  # Durable outbox remains visible; never log credential-bearing exceptions.
        await asyncio.sleep(10)


@asynccontextmanager
async def lifespan(app):
    store.initialize()
    task = (
        asyncio.create_task(worker())
        if os.getenv("CREDIT_DELIVERY_WORKER", "0") == "1"
        else None
    )
    yield
    if task:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


app = FastAPI(title="AFRACANet Credit Intelligence", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv(
        "CREDIT_CORS_ORIGINS", "http://127.0.0.1:5174,http://localhost:5174"
    ).split(","),
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Login(Strict):
    officer_id: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


class Application(Strict):
    farmer_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,99}$")
    input_farmer_id: str = Field(pattern=r"^farmer-[a-z0-9][a-z0-9-]{0,59}$")
    provenance: Literal["synthetic", "real", "mixed", "unavailable"]
    request_id: str = Field(min_length=16, max_length=100)


class Decision(Strict):
    decision: Literal["APPROVED", "REJECTED"]
    reason: str = Field(min_length=5, max_length=500)
    confirm_lender_authorization: Literal[True]
    limit_cents: int | None = Field(default=None, strict=True, ge=1, le=100_000_000)
    expires_at: datetime | None = None

    @field_validator("confirm_lender_authorization", mode="before")
    @classmethod
    def confirmation(cls, value):
        if value is not True:
            raise ValueError("Explicit lender authorization required")
        return value

    @field_validator("expires_at", mode="before")
    @classmethod
    def timestamp(cls, value):
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("Use an ISO timestamp with timezone")
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            raise ValueError("Timezone required")
        return parsed


class Revocation(Strict):
    reason: str = Field(min_length=5, max_length=500)


@app.exception_handler(IntegrityError)
async def conflict(request, error):
    return JSONResponse(
        status_code=409,
        content={"detail": "Concurrent change or duplicate record. Refresh and retry."},
    )


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "authority": "individual_local_officer_accounts",
        "payments": "input_finance_module",
    }


@app.get("/api/dataset")
def dataset(officer=Depends(identity.actor)):
    from .replay import summary

    return summary(officer["lender_id"])


@app.post("/api/session")
def login(body: Login):
    return identity.login(body.officer_id, body.password)


@app.delete("/api/session")
def logout(officer=Depends(identity.actor), authorization: str = Header()):
    identity.logout(authorization)
    return {"ok": True}


@app.get("/api/workspace")
def workspace(
    q: str = "", status: str = "", selected: str = "", officer=Depends(identity.actor)
):
    with store.engine.connect() as conn:
        query = select(store.applications).where(
            store.applications.c.lender_id == officer["lender_id"]
        )
        if q:
            query = query.where(
                store.applications.c.farmer_id.contains(q[:100], autoescape=True)
            )
        if status:
            query = query.where(store.applications.c.status == status)
        apps = [
            dict(r)
            for r in conn.execute(
                query.order_by(
                    store.applications.c.created_at.desc(), store.applications.c.id
                ).limit(100)
            ).mappings()
        ]
        selected_row = (
            conn.execute(
                select(store.applications).where(
                    store.applications.c.id == selected,
                    store.applications.c.lender_id == officer["lender_id"],
                )
            )
            .mappings()
            .first()
            if selected
            else None
        )
        visible_ids = [a["id"] for a in apps] + (
            [selected_row["id"]] if selected_row else []
        )
        counts = dict(
            conn.execute(
                select(store.applications.c.status, func.count())
                .where(store.applications.c.lender_id == officer["lender_id"])
                .group_by(store.applications.c.status)
            ).all()
        )
        decisions = [
            dict(r)
            for r in conn.execute(
                select(store.decisions)
                .where(
                    store.decisions.c.lender_id == officer["lender_id"],
                    store.decisions.c.application_id.in_(visible_ids),
                )
                .order_by(store.decisions.c.created_at.desc())
                .limit(200)
            ).mappings()
        ]
        events = [
            dict(r)
            for r in conn.execute(
                select(
                    store.outbox.c.id,
                    store.outbox.c.decision_id,
                    store.outbox.c.kind,
                    store.outbox.c.status,
                    store.outbox.c.attempts,
                    store.outbox.c.last_error,
                    store.outbox.c.next_attempt,
                    store.outbox.c.receipt,
                )
                .where(
                    store.outbox.c.lender_id == officer["lender_id"],
                    store.outbox.c.decision_id.in_([d["id"] for d in decisions]),
                )
                .order_by(store.outbox.c.next_attempt.desc())
                .limit(400)
            ).mappings()
        ]
    return {
        "officer_id": officer["id"],
        "lender_id": officer["lender_id"],
        "selected_application": dict(selected_row) if selected_row else None,
        "counts": counts,
        "applications": apps,
        "decisions": decisions,
        "deliveries": events,
        "input_finance_url": os.getenv(
            "INPUT_FINANCE_BROWSER_URL", "http://127.0.0.1:5173/"
        ),
        "message": "Lender approval permits an input request. Collection requires verified payment in input finance. No SMS was sent by this module.",
    }


@app.post("/api/applications", status_code=201)
def create(body: Application, officer=Depends(identity.actor)):
    return workflow.create_application(body, officer)


@app.post("/api/applications/{identifier}/decisions")
def decide(identifier: str, body: Decision, officer=Depends(identity.actor)):
    return workflow.decide(identifier, body, officer)


@app.post("/api/decisions/{identifier}/revoke")
def revoke(identifier: str, body: Revocation, officer=Depends(identity.actor)):
    return workflow.revoke(identifier, body.reason, officer)


@app.post("/api/deliveries/{identifier}/retry")
def retry(identifier: str, officer=Depends(identity.actor)):
    result = delivery.dispatch(identifier, officer["lender_id"])
    if result is None:
        raise HTTPException(404, "Delivery not found in your lender workspace.")
    return result


@app.get("/api/applications/{identifier}/context")
def context(
    identifier: str, relationship: str | None = None, officer=Depends(identity.actor)
):
    with store.engine.connect() as conn:
        application = workflow.scoped_application(conn, identifier, officer)
    return graph_context.context(
        application["farmer_id"], officer["lender_id"], relationship
    )


@app.post("/api/applications/{identifier}/recommendation")
def recommend(identifier: str, officer=Depends(identity.actor)):
    evidence = context(identifier, officer=officer)
    with store.engine.connect() as conn:
        application = workflow.scoped_application(conn, identifier, officer)
    response = advisory.summarize(evidence, application["provenance"])
    with store.engine.begin() as conn:
        conn.execute(
            store.evaluations.insert().values(
                id=str(uuid.uuid4()),
                application_id=identifier,
                officer_id=officer["id"],
                result=json.dumps(response),
                created_at=store.now(),
            )
        )
    return response


@app.get("/api/applications/{identifier}/evidence/{record_id}")
def evidence_record(identifier: str, record_id: str, officer=Depends(identity.actor)):
    with store.engine.connect() as conn:
        application = workflow.scoped_application(conn, identifier, officer)
    return graph_context.record(
        application["farmer_id"], officer["lender_id"], record_id
    )


# Unauthenticated legacy financial endpoints are retired, not silently kept active.
@app.post("/api/approve")
@app.post("/api/reject")
@app.post("/api/evaluate")
@app.get("/api/pending_loans")
@app.post("/api/ussd")
def retired():
    raise HTTPException(
        410,
        "Use the authenticated application workflow. USSD intake requires a separately verified provider adapter.",
    )
