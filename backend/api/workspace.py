from fastapi import APIRouter, Depends

from ..auth import actor
from ..services import workspace

router = APIRouter(prefix="/api", tags=["workspace"])


@router.get("/health")
def health():
    return workspace.health()


@router.get("/state")
def state(user=Depends(actor)):
    return workspace.state(user)
