"""Callback-only sandbox listener. No workspace, sessions, files or docs are public.

Run with `python -m uvicorn scripts.webhook_listener:app --port 8013`.
By default it uses the configured execution store. For the persistent provider
fixture, set WEBHOOK_CHECK_FIXTURE=1 in this process only before starting it.
"""

import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from backend import db
from backend.api.webhooks import router
from backend.config import ROOT, settings
from backend.integrations.paypal import PaymentError

if os.getenv("WEBHOOK_CHECK_FIXTURE") == "1":
    directory = ROOT / "data" / "provider-checks"
    database = directory / "paypal-sandbox.sqlite"
    if not database.exists():
        raise RuntimeError(
            "Prepare the isolated provider fixture before starting its listener."
        )
    context = json.loads(
        (directory / "paypal-sandbox-context.json").read_text(encoding="utf-8")
    )
    settings.paypal_invoice_prefix = context["invoice_prefix"]
    db.engine = db.build_engine(f"sqlite:///{database.as_posix()}")


@asynccontextmanager
async def lifespan(app):
    settings.validate()
    if settings.payment_mode != "sandbox":
        raise RuntimeError("The callback listener is sandbox-only.")
    db.initialize()
    yield


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok", "purpose": "paypal_sandbox_callback_only"}


@app.exception_handler(PaymentError)
async def provider_unavailable(request, error):
    # A non-2xx lets PayPal retry; never acknowledge an unverified event.
    return JSONResponse(
        status_code=503,
        content={"detail": "Provider verification unavailable; retry later."},
    )
