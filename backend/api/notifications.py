from fastapi import APIRouter, Depends

from ..auth import actor, require
from ..contracts import notifications as contact_contracts
from ..services import notifications

router = APIRouter(prefix="/api", tags=["notifications"])


@router.get("/sms")
def sms_preferences(user=Depends(actor)):
    require(user, "farmer")
    return notifications.preferences(user)


@router.put("/sms/contact")
def sms_contact(body: contact_contracts.ContactRequest, user=Depends(actor)):
    require(user, "farmer")
    return notifications.save_contact(user, body)


@router.post("/sms/verify")
def sms_verify(body: contact_contracts.VerifyRequest, user=Depends(actor)):
    require(user, "farmer")
    return notifications.verify_contact(user, body)


@router.post("/sms/dispatch")
def sms_dispatch(user=Depends(actor)):
    require(user, "farmer")
    count = notifications.dispatch_pending(user["subject"], limit=1)
    return {
        "message": f"Processed {count} queued SMS update(s). Check its recorded status; acceptance is not delivery."
    }
