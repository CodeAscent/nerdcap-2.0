"""
Conflict Detector
Extracts conflict records from FTM Council decision and persists them.
Also performs basic GIS overlap detection and stores spatial conflicts.
"""
import uuid
from typing import Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.models import Conflict
from app.models.models import ConflictSeverity


def store_from_council(proposal_id: str, council_decision: dict, db: Session, spatial_conflicts: dict | None = None) -> list[Conflict]:
    """
    Parse conflict_matrix from FTM Council decision and persist.
    Also includes spatial conflicts if provided.
    """
    conflict_matrix = council_decision.get("conflict_matrix", [])
    conflicts = []

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

    if spatial_conflicts and spatial_conflicts.get("has_spatial_conflicts"):
        spatial_conflict_list = store_spatial_conflicts(proposal_id, spatial_conflicts, db)
        conflicts.extend(spatial_conflict_list)

    db.flush()
    return conflicts


def store_spatial_conflicts(proposal_id: str, spatial_results: dict[str, Any], db: Session) -> list[Conflict]:
    """
    Store spatial conflicts from the spatial analysis results.
    Creates Conflict records with geometry data for each spatial conflict.
    """
    conflicts = []
    all_conflicts = spatial_results.get("all_conflicts", [])

    for conflict_data in all_conflicts:
        severity_str = conflict_data.get("severity", "low")
        try:
            severity = ConflictSeverity(severity_str)
        except ValueError:
            severity = ConflictSeverity.low

        conflict_type = conflict_data.get("conflict_type", "spatial_overlap")
        description = conflict_data.get("description", "")

        if conflict_type == "existing_project_overlap":
            description = (
                f"Overlaps with approved {conflict_data.get('project_type', 'project')} "
                f"({conflict_data.get('capacity_mw', 0)}MW) by {conflict_data.get('developer_name', 'Unknown')} "
                f"in {conflict_data.get('district', 'Unknown')} district. "
                f"Overlap area: {conflict_data.get('overlap_area_ha', 0):.2f} hectares."
            )
            source_department = "NREDCAP"
        elif conflict_type == "transmission_line_overlap":
            description = (
                f"Overlaps with {conflict_data.get('voltage_kv', 0)}kV transmission line "
                f"'{conflict_data.get('line_name', 'Unknown')}'. "
                f"Buffer zone: {conflict_data.get('buffer_m', 0)}m. "
                f"Overlap area: {conflict_data.get('overlap_area_ha', 0):.2f} hectares."
            )
            source_department = "APTRANSCO"
        elif conflict_type == "protected_area_overlap":
            description = (
                f"Overlaps with {conflict_data.get('protection_type', 'Protected Area')}: "
                f"'{conflict_data.get('area_name', 'Unknown')}'. "
                f"Overlap: {conflict_data.get('overlap_percentage', 0):.1f}% of proposal "
                f"({conflict_data.get('overlap_area_ha', 0):.2f} hectares)."
            )
            source_department = "Forest Department"
        else:
            source_department = conflict_data.get("source_department", "GIS Analysis")

        conflict = Conflict(
            id=uuid.uuid4(),
            proposal_id=proposal_id,
            conflict_type=conflict_type,
            severity=severity,
            description=description,
            source_department=source_department,
            overlap_area_ha=conflict_data.get("overlap_area_ha"),
        )
        db.add(conflict)
        conflicts.append(conflict)

    return conflicts


def get_conflicts_for_proposal(proposal_id: str, db: Session) -> list[dict]:
    """
    Retrieve all conflicts for a proposal, including geometry data if available.
    """
    conflicts = db.query(Conflict).filter(Conflict.proposal_id == proposal_id).all()
    result = []
    
    for c in conflicts:
        conflict_dict = {
            "id": str(c.id),
            "conflict_type": c.conflict_type,
            "severity": c.severity.value if c.severity else "low",
            "description": c.description,
            "source_department": c.source_department,
            "overlap_area_ha": c.overlap_area_ha,
        }
        result.append(conflict_dict)
    
    return result


def get_critical_conflicts(proposal_id: str, db: Session) -> list[Conflict]:
    """
    Get all critical or high severity conflicts for a proposal.
    """
    return db.query(Conflict).filter(
        Conflict.proposal_id == proposal_id,
        Conflict.severity.in_([ConflictSeverity.critical, ConflictSeverity.high])
    ).all()
