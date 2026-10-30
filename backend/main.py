"""Application composition. Feature routes and transaction services own behavior."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from starlette.middleware.trustedhost import TrustedHostMiddleware

from . import db
from .api import (
    approvals,
    catalogue,
    credit_delivery,
    issues,
    notifications,
    orders,
    payments,
    reconciliation,
    sessions,
    webhooks,
    workspace,
)
from .config import ROOT, settings
from .integrations.paypal import PaymentError


@asynccontextmanager
async def lifespan(app):
    settings.validate()
    db.initialize()
    yield


app = FastAPI(title="AFRACANet Input Finance", version="0.1.0", lifespan=lifespan)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
for routes in (
    approvals,
    catalogue,
    credit_delivery,
    issues,
    notifications,
    orders,
    payments,
    reconciliation,
    sessions,
    webhooks,
    workspace,
):
    app.include_router(routes.router)


@app.exception_handler(IntegrityError)
async def database_conflict(request, exc):
    return JSONResponse(
        status_code=409,
        content={
            "detail": "A concurrent request changed this record. Refresh and retry."
        },
    )


@app.exception_handler(PaymentError)
async def payment_error(request, exc):
    return JSONResponse(status_code=502, content={"detail": str(exc)})


if (ROOT / "dist").exists():
    app.mount("/", StaticFiles(directory=ROOT / "dist", html=True), name="frontend")
