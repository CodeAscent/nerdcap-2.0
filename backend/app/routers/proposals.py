"""
Land Parcels & Proposals Router
"""
import json
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping, shape

from app.auth import get_current_user, require_officer
from app.database import get_db
from app.models import LandParcel, Developer, Proposal, User
from app.models.models import ProposalStatus
from app.schemas import (
    ProposalCreate, ProposalResponse, ProposalDetailResponse,
    LandParcelResponse, LandParcelGeoResponse, DecisionRequest,
    AnalysisStatusResponse, DeveloperResponse
)

router = APIRouter(prefix="/api", tags=["Proposals"])


# ---------------------------------------------------------------------------
# Developers & Land Parcels
# ---------------------------------------------------------------------------
@router.get("/developers", response_model=list[DeveloperResponse])
def list_developers(db: Session = Depends(get_db)):
    return db.query(Developer).all()

@router.get("/land-parcels", response_model=list[LandParcelResponse])
def list_land_parcels(
    district: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    q = db.query(LandParcel)
    if district:
        q = q.filter(LandParcel.district.ilike(f"%{district}%"))
    return q.offset(skip).limit(limit).all()


@router.get("/land-parcels/{parcel_id}", response_model=LandParcelGeoResponse)
def get_land_parcel(parcel_id: UUID, db: Session = Depends(get_db)):
    parcel = db.query(LandParcel).filter(LandParcel.id == parcel_id).first()
    if not parcel:
        raise HTTPException(status_code=404, detail="Land parcel not found")
    response = LandParcelGeoResponse.model_validate(parcel)
    if parcel.geometry is not None:
        try:
            geom = to_shape(parcel.geometry)
            response.geometry_geojson = mapping(geom)
        except Exception:
            pass
    return response


# ---------------------------------------------------------------------------
# Proposals
# ---------------------------------------------------------------------------
@router.post("/proposals", response_model=ProposalResponse, status_code=201)
def create_proposal(
    payload: ProposalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Validate developer exists
    dev = db.query(Developer).filter(Developer.id == payload.developer_id).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Developer not found")

    # Convert GeoJSON to WKT for PostGIS
    boundary_wkt = None
    try:
        geom = shape(payload.boundary_geojson if payload.boundary_geojson.get("type") == "Polygon"
                     else payload.boundary_geojson.get("geometry", payload.boundary_geojson))
        boundary_wkt = f"SRID=4326;{geom.wkt}"
    except Exception:
        pass

    proposal = Proposal(
        developer_id=payload.developer_id,
        project_type=payload.project_type,
        capacity_mw=payload.capacity_mw,
        district=payload.district,
        boundary_geojson=payload.boundary_geojson,
        boundary_geometry=boundary_wkt,
        status=ProposalStatus.pending,
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


@router.get("/proposals", response_model=list[ProposalResponse])
def list_proposals(
    status_filter: Optional[str] = Query(None, alias="status"),
    district: Optional[str] = None,
    project_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Proposal)
    if status_filter:
        q = q.filter(Proposal.status == status_filter)
    if district:
        q = q.filter(Proposal.district.ilike(f"%{district}%"))
    if project_type:
        q = q.filter(Proposal.project_type == project_type)
    q = q.order_by(Proposal.submitted_at.desc())
    return q.offset(skip).limit(limit).all()


@router.get("/proposals/{proposal_id}", response_model=ProposalDetailResponse)
def get_proposal(proposal_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return proposal


@router.post("/proposals/{proposal_id}/analyze", response_model=AnalysisStatusResponse)
def trigger_analysis(
    proposal_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if proposal.status == ProposalStatus.analyzing:
        return AnalysisStatusResponse(
            proposal_id=proposal_id,
            status=proposal.status,
            message="Analysis already in progress",
        )

    # Import here to avoid circular imports
    from app.tasks.analysis_tasks import run_analysis_background
    proposal.status = ProposalStatus.analyzing
    db.commit()

    background_tasks.add_task(run_analysis_background, str(proposal_id))

    return AnalysisStatusResponse(
        proposal_id=proposal_id,
        status=ProposalStatus.analyzing,
        message="Analysis started",
        progress_pct=0,
    )


@router.get("/proposals/{proposal_id}/analysis-status", response_model=AnalysisStatusResponse)
def get_analysis_status(
    proposal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    pct_map = {
        ProposalStatus.pending: 0,
        ProposalStatus.analyzing: 60,
        ProposalStatus.analyzed: 100,
        ProposalStatus.under_review: 100,
        ProposalStatus.approved: 100,
        ProposalStatus.rejected: 100,
        ProposalStatus.escalated: 100,
    }
    return AnalysisStatusResponse(
        proposal_id=proposal_id,
        status=proposal.status,
        progress_pct=pct_map.get(proposal.status, 0),
    )


@router.patch("/proposals/{proposal_id}/decision")
def record_decision(
    proposal_id: UUID,
    payload: DecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_officer),
):
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if proposal.status not in (ProposalStatus.analyzed, ProposalStatus.under_review, ProposalStatus.escalated):
        raise HTTPException(status_code=400, detail="Proposal is not ready for a decision")

    status_map = {
        "approve": ProposalStatus.approved,
        "reject": ProposalStatus.rejected,
        "escalate": ProposalStatus.escalated,
        "request_more_info": ProposalStatus.under_review,
    }
    proposal.status = status_map[payload.action]
    proposal.officer_notes = payload.notes
    proposal.decided_by_user_id = current_user.id
    proposal.decided_at = datetime.utcnow()
    db.commit()

    # If approved, sync to RTGS
    if payload.action == "approve":
        from app.stubs import rtgs_stub
        rtgs_stub.sync_allocation(str(proposal_id), {
            "district": proposal.district,
            "capacity_mw": proposal.capacity_mw,
            "project_type": proposal.project_type.value,
        })

    return {"message": f"Proposal {payload.action}d successfully", "status": proposal.status}


@router.get("/proposals/{proposal_id}/report")
def download_report(
    proposal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from fastapi.responses import Response
    from app.services.report_generator import generate_allocation_report

    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    if proposal.status == ProposalStatus.pending:
        raise HTTPException(status_code=400, detail="Proposal has not been analyzed yet")

    pdf_bytes = generate_allocation_report(proposal, db)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{proposal_id}.pdf"},
    )


@router.get("/proposals/{proposal_id}/audit-log")
def get_audit_log(
    proposal_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.models import AuditLog
    logs = db.query(AuditLog).filter(AuditLog.proposal_id == proposal_id).order_by(AuditLog.timestamp).all()
    return logs
