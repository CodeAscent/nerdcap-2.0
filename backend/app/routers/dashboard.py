"""
Dashboard & RTGS Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Proposal, TrustScore
from app.models.models import ProposalStatus
from app.schemas import DashboardSummary
from app.stubs import rtgs_stub

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    counts = {s.value: 0 for s in ProposalStatus}
    rows = db.query(Proposal.status, func.count()).group_by(Proposal.status).all()
    for status, count in rows:
        counts[status] = count

    total = sum(counts.values())

    # Approved MW
    approved_mw = (
        db.query(func.sum(Proposal.capacity_mw))
        .filter(Proposal.status == ProposalStatus.approved)
        .scalar() or 0.0
    )

    # Avg trust score
    avg_score = db.query(func.avg(TrustScore.overall_score)).scalar() or 0.0

    # Conflict rate (proposals with at least one conflict / total analyzed)
    from app.models import Conflict
    conflicted_proposal_ids = db.query(Conflict.proposal_id).distinct().count()
    analyzed = counts.get("analyzed", 0) + counts.get("approved", 0) + counts.get("rejected", 0)
    conflict_rate = round((conflicted_proposal_ids / analyzed * 100) if analyzed > 0 else 0, 1)

    # District breakdown
    district_rows = (
        db.query(Proposal.district, func.count())
        .group_by(Proposal.district)
        .all()
    )
    district_breakdown = {d: c for d, c in district_rows}

    return DashboardSummary(
        total_proposals=total,
        pending=counts.get("pending", 0),
        analyzing=counts.get("analyzing", 0),
        approved=counts.get("approved", 0),
        rejected=counts.get("rejected", 0),
        escalated=counts.get("escalated", 0),
        total_approved_mw=round(float(approved_mw), 2),
        avg_trust_score=round(float(avg_score), 1),
        conflict_rate_pct=conflict_rate,
        district_breakdown=district_breakdown,
    )


@router.get("/conflict-alerts")
def conflict_alerts(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    from app.models import Conflict
    from app.models.models import ConflictSeverity
    alerts = (
        db.query(Conflict)
        .filter(Conflict.severity.in_([ConflictSeverity.high, ConflictSeverity.critical]))
        .order_by(Conflict.proposal_id)
        .limit(50)
        .all()
    )
    return alerts


@router.get("/district-map")
def district_map(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Return per-district statistics for choropleth map."""
    rows = (
        db.query(
            Proposal.district,
            func.count().label("total"),
            func.sum(Proposal.capacity_mw).label("total_mw"),
        )
        .group_by(Proposal.district)
        .all()
    )
    return [
        {"district": r.district, "total_proposals": r.total, "total_mw": float(r.total_mw or 0)}
        for r in rows
    ]


@router.get("/rtgs-status")
def rtgs_status():
    return rtgs_stub.get_status()


@router.post("/rtgs-sync/{proposal_id}")
def manual_rtgs_sync(
    proposal_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.models import Proposal as P
    from uuid import UUID
    proposal = db.query(P).filter(P.id == UUID(proposal_id)).first()
    if not proposal:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Proposal not found")
    result = rtgs_stub.sync_allocation(proposal_id, {
        "district": proposal.district,
        "capacity_mw": proposal.capacity_mw,
        "project_type": proposal.project_type.value,
    })
    return result
