"""
Conflict Detector
Extracts conflict records from FTM Council decision and persists them.
Also performs basic GIS overlap detection.
"""
import uuid
from typing import Any
from sqlalchemy.orm import Session
from app.models import Conflict
from app.models.models import ConflictSeverity


def store_from_council(proposal_id: str, council_decision: dict, db: Session) -> list[Conflict]:
    """
    Parse conflict_matrix from FTM Council decision and persist.
    """
    conflict_matrix = council_decision.get("conflict_matrix", [])
    conflicts = []

    # Remove existing conflicts (re-analysis)
    db.query(Conflict).filter(Conflict.proposal_id == proposal_id).delete()
    db.flush()

    for item in conflict_matrix:
        severity_str = item.get("severity", "low")
        try:
            severity = ConflictSeverity(severity_str)
        except ValueError:
            severity = ConflictSeverity.low

        conflict = Conflict(
            id=uuid.uuid4(),
            proposal_id=proposal_id,
            conflict_type=item.get("conflict_type", "unknown"),
            severity=severity,
            description=item.get("description", ""),
            source_department=item.get("source_department", ""),
            overlap_area_ha=item.get("overlap_area_ha"),
        )
        db.add(conflict)
        conflicts.append(conflict)

    db.flush()
    return conflicts
