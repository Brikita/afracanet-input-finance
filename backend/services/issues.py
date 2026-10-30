"""Issues behavior; API dependencies are supplied by the route layer."""

from fastapi import HTTPException
from sqlalchemy import insert, select, update
from .. import db
from ..auth import require
from ..schemas import IssueRequest, IssueResolution
from .orders import get_order


def report_issue(order_id: int, body: IssueRequest, user):
    detail = body.detail.strip()
    if len(detail) < 5:
        raise HTTPException(422, "Describe the issue in at least five characters.")
    with db.engine.begin() as conn:
        get_order(conn, order_id, user, lock=True)
        existing = conn.execute(select(db.issues).where(
            db.issues.c.order_id == order_id, db.issues.c.client_request_id == body.client_request_id,
        )).mappings().first()
        if existing:
            if existing["detail"] != detail or existing["category"] != body.category or existing["reported_by"] != user["subject"]:
                raise HTTPException(409, "This issue reference belongs to a different report.")
            return {"id": existing["id"], "message": "Issue already recorded."}
        issue_id = conn.execute(insert(db.issues).values(
            order_id=order_id, client_request_id=body.client_request_id, category=body.category,
            detail=detail, reported_by=user["subject"], created_at=db.now(),
        )).inserted_primary_key[0]
        db.record(conn, order_id, user["subject"], "ISSUE_REPORTED", f"{body.category}: {detail}")
    return {"id": issue_id, "message": "Issue recorded. The lender must resolve it before further approval, invoicing, payment initiation, or collection."}


def resolve_issue(order_id: int, issue_id: int, body: IssueResolution, user):
    require(user, "lender")
    resolution = body.resolution.strip()
    if len(resolution) < 5:
        raise HTTPException(422, "Record the resolution in at least five characters.")
    with db.engine.begin() as conn:
        get_order(conn, order_id, user, lock=True)
        issue = conn.execute(select(db.issues).where(db.issues.c.id == issue_id, db.issues.c.order_id == order_id)).mappings().first()
        if not issue:
            raise HTTPException(404, "Issue not found.")
        if issue["resolved_at"]:
            if issue["resolution"] != resolution:
                raise HTTPException(409, "This issue already has a recorded resolution.")
            return {"message": "Issue already resolved."}
        conn.execute(update(db.issues).where(db.issues.c.id == issue_id).values(
            resolved_by=user["subject"], resolved_at=db.now(), resolution=resolution,
        ))
        db.record(conn, order_id, user["subject"], "ISSUE_RESOLVED", f"Issue {issue_id}: {resolution}")
    return {"message": "Resolution recorded. Financial and collection status still follow their verified transaction records."}
