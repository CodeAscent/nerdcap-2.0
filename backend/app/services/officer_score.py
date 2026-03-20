"""
Officer Score Service
Computes officer responsiveness scores based on proposal handling metrics.
"""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from app.models import Proposal, User
from app.models.models import ProposalStatus, UserRole, OfficerScore
import uuid


def calculate_response_time(proposal: Proposal) -> Optional[float]:
    """
    Calculate the response time in hours from analyzed_at to decided_at.
    Returns None if either timestamp is missing.
    """
    if proposal.analyzed_at and proposal.decided_at:
        delta = proposal.decided_at - proposal.analyzed_at
        return delta.total_seconds() / 3600
    return None


def _normalize_response_time(avg_hours: float) -> float:
    """
    Normalize response time to a 0-100 score.
    Lower response time = higher score.
    0 hours = 100 score
    24 hours = 80 score
    48 hours = 60 score
    72 hours = 40 score
    96+ hours = 20 score (floor)
    """
    if avg_hours <= 0:
        return 100.0
    elif avg_hours <= 24:
        return 100.0 - (avg_hours / 24) * 20
    elif avg_hours <= 48:
        return 80.0 - ((avg_hours - 24) / 24) * 20
    elif avg_hours <= 72:
        return 60.0 - ((avg_hours - 48) / 24) * 20
    elif avg_hours <= 96:
        return 40.0 - ((avg_hours - 72) / 24) * 20
    else:
        return max(20.0, 40.0 - ((avg_hours - 72) / 24) * 2.5)


def _compute_data_freshness(user: User, db: Session) -> float:
    """
    Compute data freshness score based on recent activity.
    Score from 0-100 based on how recently the officer has been active.
    """
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    recent_decisions = (
        db.query(func.count(Proposal.id))
        .filter(
            Proposal.decided_by_user_id == user.id,
            Proposal.decided_at >= seven_days_ago
        )
        .scalar() or 0
    )
    
    monthly_decisions = (
        db.query(func.count(Proposal.id))
        .filter(
            Proposal.decided_by_user_id == user.id,
            Proposal.decided_at >= thirty_days_ago
        )
        .scalar() or 0
    )
    
    if recent_decisions >= 10:
        return 100.0
    elif recent_decisions >= 5:
        return 90.0
    elif recent_decisions >= 1:
        return 70.0 + (recent_decisions * 2)
    elif monthly_decisions >= 1:
        days_since = (
            db.query(func.max(Proposal.decided_at))
            .filter(Proposal.decided_by_user_id == user.id)
            .scalar()
        )
        if days_since:
            days_ago = (datetime.utcnow() - days_since).days
            return max(30.0, 70.0 - days_ago)
    return 30.0


def _compute_escalation_resolution_rate(user: User, db: Session) -> float:
    """
    Compute the percentage of escalated proposals that were resolved by the officer.
    Returns a score from 0-100.
    """
    resolved_escalations = (
        db.query(func.count(Proposal.id))
        .filter(
            Proposal.decided_by_user_id == user.id,
            Proposal.status.in_([ProposalStatus.approved, ProposalStatus.rejected])
        )
        .scalar() or 0
    )
    
    if resolved_escalations == 0:
        return 50.0
    
    total_decided = (
        db.query(func.count(Proposal.id))
        .filter(Proposal.decided_by_user_id == user.id)
        .scalar() or 0
    )
    
    if total_decided == 0:
        return 50.0
    
    return min(100.0, (resolved_escalations / total_decided) * 100)


def _compute_collaboration_index(user: User, db: Session) -> float:
    """
    Compute collaboration index based on cross-district work.
    Officers who review proposals from districts other than their own get higher scores.
    """
    if not user.district:
        return 50.0
    
    same_district_proposals = (
        db.query(func.count(Proposal.id))
        .filter(
            Proposal.decided_by_user_id == user.id,
            Proposal.district == user.district
        )
        .scalar() or 0
    )
    
    other_district_proposals = (
        db.query(func.count(Proposal.id))
        .filter(
            Proposal.decided_by_user_id == user.id,
            Proposal.district != user.district
        )
        .scalar() or 0
    )
    
    total = same_district_proposals + other_district_proposals
    if total == 0:
        return 50.0
    
    cross_district_ratio = other_district_proposals / total
    return min(100.0, 50.0 + cross_district_ratio * 50)


def compute_officer_score(user: User, db: Session) -> OfficerScore:
    """
    Calculate weighted officer score with components:
    - Response time (50%): Lower is better, normalized to 0-100
    - Data freshness (20%): Based on recent activity
    - Escalation resolution (20%): % of escalated proposals resolved
    - Collaboration (10%): Cross-district work
    """
    proposals_decided = (
        db.query(func.count(Proposal.id))
        .filter(Proposal.decided_by_user_id == user.id)
        .scalar() or 0
    )
    
    avg_response_hours = None
    try:
        avg_response_time = (
            db.query(
                func.avg(
                    func.extract('epoch', (Proposal.decided_at - Proposal.analyzed_at)) / 3600
                )
            )
            .filter(
                Proposal.decided_by_user_id == user.id,
                Proposal.decided_at.isnot(None),
                Proposal.analyzed_at.isnot(None)
            )
            .scalar()
        )
        avg_response_hours = float(avg_response_time) if avg_response_time else None
    except Exception:
        avg_response_hours = None
    
    response_time_score = _normalize_response_time(avg_response_hours) if avg_response_hours else 50.0
    data_freshness_score = _compute_data_freshness(user, db)
    escalation_rate = _compute_escalation_resolution_rate(user, db)
    collaboration_index = _compute_collaboration_index(user, db)
    
    weighted_score = (
        response_time_score * 0.50 +
        data_freshness_score * 0.20 +
        escalation_rate * 0.20 +
        collaboration_index * 0.10
    )
    
    existing = db.query(OfficerScore).filter(OfficerScore.user_id == user.id).first()
    if existing:
        existing.score = round(weighted_score, 2)
        existing.avg_response_time_hours = round(avg_response_hours, 2) if avg_response_hours else None
        existing.proposals_decided = proposals_decided
        existing.data_freshness_score = round(data_freshness_score, 2)
        existing.escalation_resolution_rate = round(escalation_rate, 2)
        existing.collaboration_index = round(collaboration_index, 2)
        existing.computed_at = datetime.utcnow()
        db.flush()
        return existing
    
    officer_score = OfficerScore(
        id=uuid.uuid4(),
        user_id=user.id,
        score=round(weighted_score, 2),
        avg_response_time_hours=round(avg_response_hours, 2) if avg_response_hours else None,
        proposals_decided=proposals_decided,
        data_freshness_score=round(data_freshness_score, 2),
        escalation_resolution_rate=round(escalation_rate, 2),
        collaboration_index=round(collaboration_index, 2),
        computed_at=datetime.utcnow(),
    )
    db.add(officer_score)
    db.flush()
    return officer_score


def update_all_officer_scores(db: Session) -> List[OfficerScore]:
    """
    Recompute scores for all officers.
    """
    officers = (
        db.query(User)
        .filter(User.role == UserRole.officer, User.is_active == True)
        .all()
    )
    
    updated_scores = []
    for officer in officers:
        score = compute_officer_score(officer, db)
        updated_scores.append(score)
    
    db.commit()
    return updated_scores


def get_officer_leaderboard(db: Session, limit: int = 10) -> List[dict]:
    """
    Return top officers by score with user details.
    """
    results = (
        db.query(OfficerScore, User)
        .join(User, OfficerScore.user_id == User.id)
        .filter(User.is_active == True)
        .order_by(OfficerScore.score.desc())
        .limit(limit)
        .all()
    )
    
    leaderboard = []
    for score, user in results:
        leaderboard.append({
            "user_id": str(user.id),
            "name": user.full_name or user.email,
            "department": user.department or "NREDCAP",
            "district": user.district or "Unassigned",
            "score": score.score,
            "proposals_decided": score.proposals_decided,
            "avg_response_time_hours": score.avg_response_time_hours,
        })
    
    return leaderboard
