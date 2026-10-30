from fastapi import APIRouter, Depends

from ..auth import actor, require
from ..contracts import handoffs as handoff_contracts
from ..contracts.allocations import ApprovalImport
from ..services import allocations, handoffs

router = APIRouter(prefix="/api", tags=["Lender approvals"])


def lender(user=Depends(actor)):
    require(user, "lender")
    return user


@router.post("/approvals/import")
def approval_import(body: ApprovalImport, user=Depends(lender)):
    return allocations.import_approvals(body, user)


@router.get("/approval-mappings")
def mappings(user=Depends(lender)):
    return handoffs.mappings(user)


@router.post("/approval-mappings")
def mapping_create(body: handoff_contracts.MappingRequest, user=Depends(lender)):
    return handoffs.save_mapping(body, user)


@router.post("/approval-handoffs/preview")
def preview(body: handoff_contracts.Handoff, user=Depends(lender)):
    return handoffs.preview(body, user)


@router.post("/approval-handoffs")
def apply(body: handoff_contracts.HandoffApply, user=Depends(lender)):
    return handoffs.apply(body, user)


@router.get("/approval-handoffs")
def history(reference: str | None = None, user=Depends(lender)):
    return handoffs.history(user, reference)


@router.post("/approval-handoffs/{handoff_id}/revoke")
def revoke(handoff_id: str, body: handoff_contracts.Revocation, user=Depends(lender)):
    return handoffs.revoke(handoff_id, body, user)
