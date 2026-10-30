import json

from fastapi import APIRouter, HTTPException, Request
from starlette.concurrency import run_in_threadpool

from ..config import settings
from ..services.webhooks import process_webhook

router = APIRouter(prefix="/api", tags=["webhooks"])


@router.post("/webhooks/paypal")
async def paypal_webhook(request: Request):
    if settings.payment_mode != "sandbox":
        raise HTTPException(403, "PayPal webhooks are disabled in simulated mode.")
    body = await request.body()
    if len(body) > 1_000_000:
        raise HTTPException(413, "Event is too large.")
    try:
        event = json.loads(body)
    except ValueError as exc:
        raise HTTPException(400, "Invalid event.") from exc
    if not isinstance(event, dict) or not isinstance(event.get("id"), str):
        raise HTTPException(400, "Event ID is required.")
    # Network operations stay off the async event loop.
    return await run_in_threadpool(process_webhook, dict(request.headers), event)
