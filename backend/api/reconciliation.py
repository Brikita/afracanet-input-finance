from fastapi import APIRouter, Depends

from ..auth import actor
from ..services import reconciliation

router = APIRouter(prefix="/api", tags=["reconciliation"])


@router.get("/reconciliation.csv")
def export(user=Depends(actor)):
    return reconciliation.export_csv(user)
