"""
Trust Score Engine
Computes weighted Land Parcel Trust Score from agent/council results.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import TrustScore, Proposal
from app.models.models import GradeEnum
import uuid


def compute_grade(score: float) -> GradeEnum:
    if score >= 85:
        return GradeEnum.A
    elif score >= 70:
        return GradeEnum.B
    elif score >= 50:
        return GradeEnum.C
    return GradeEnum.D


def compute_and_store(proposal_id: str, council_decision: dict, db: Session) -> TrustScore:
    """
    Extract trust score from FTM Council decision and persist to DB.
    """
    overall = min(100.0, max(0.0, float(council_decision.get("overall_trust_score", 50.0))))
    grade = compute_grade(overall)
    factor_breakdown = council_decision.get("factor_breakdown", {
        "clean_title": 15.0,
        "no_disputes": 12.0,
        "environmental_clearance": 10.0,
        "grid_connectivity": 8.0,
        "satellite_characteristics": 5.0,
        "historical_allocation": 7.0,
    })

    # Remove existing trust score if any (re-analysis)
    existing = db.query(TrustScore).filter(TrustScore.proposal_id == proposal_id).first()
    if existing:
        db.delete(existing)
        db.flush()

    ts = TrustScore(
        id=uuid.uuid4(),
        proposal_id=proposal_id,
        overall_score=overall,
        grade=grade,
        factor_breakdown=factor_breakdown,
        computed_at=datetime.utcnow(),
    )
    db.add(ts)
    db.flush()
    return ts
