from fastapi import APIRouter, Depends

from ..auth import actor
from ..contracts.requests import Login
from ..services import sessions

router = APIRouter(prefix="/api", tags=["sessions"])


@router.get("/personas")
def personas():
    return sessions.personas()


@router.get("/participants")
def participant_choices(user=Depends(actor)):
    return sessions.participant_choices(user)


@router.post("/session")
def login(body: Login):
    return sessions.login(body)


@router.delete("/session")
def logout(user=Depends(actor)):
    return sessions.logout(user)
