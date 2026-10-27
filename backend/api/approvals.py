from fastapi import APIRouter, Depends

from .. import handoffs, management
from ..auth import actor, require

router = APIRouter(prefix="/api", tags=["Lender approvals"])


def lender(user=Depends(actor)):
    require(user, "lender")
    return user


@router.post("/approvals/import")
def approval_import(body: management.ApprovalImport, user=Depends(lender)):
    return management.import_approvals(body, user)


@router.get("/approval-mappings")
def mappings(user=Depends(lender)):
    return handoffs.mappings(user)


@router.post("/approval-mappings")
def mapping_create(body: handoffs.MappingRequest, user=Depends(lender)):
    return handoffs.save_mapping(body, user)


@router.post("/approval-handoffs/preview")
def preview(body: handoffs.Handoff, user=Depends(lender)):
    return handoffs.preview(body, user)


@router.post("/approval-handoffs")
def apply(body: handoffs.HandoffApply, user=Depends(lender)):
    return handoffs.apply(body, user)


@router.get("/approval-handoffs")
def history(user=Depends(lender)):
    return handoffs.history(user)


@router.post("/approval-handoffs/{handoff_id}/revoke")
def revoke(handoff_id: str, body: handoffs.Revocation, user=Depends(lender)):
    return handoffs.revoke(handoff_id, body, user)
