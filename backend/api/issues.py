from fastapi import APIRouter, Depends
from ..auth import actor
from ..schemas import IssueRequest, IssueResolution
from ..services import issues

router = APIRouter(prefix="/api", tags=["issues"])


@router.post('/orders/{order_id}/issues', status_code=201)
def report_issue(order_id: int, body: IssueRequest, user=Depends(actor)):
    return issues.report_issue(order_id, body, user)


@router.post('/orders/{order_id}/issues/{issue_id}/resolve')
def resolve_issue(order_id: int, issue_id: int, body: IssueResolution, user=Depends(actor)):
    return issues.resolve_issue(order_id, issue_id, body, user)


