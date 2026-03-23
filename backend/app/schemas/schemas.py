from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator
from app.models.models import ProjectType, ProposalStatus, GradeEnum, ConflictSeverity, UserRole


# ---------------------------------------------------------------------------
# Shared
# ---------------------------------------------------------------------------
class PaginatedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[Any]


# ---------------------------------------------------------------------------
# Land Parcel
# ---------------------------------------------------------------------------
class LandParcelBase(BaseModel):
    name: str
    district: str
    mandal: Optional[str] = None
    village: Optional[str] = None
    area_ha: float
    ownership_type: Optional[str] = None
    land_use_type: Optional[str] = None
    elevation_m: Optional[float] = None
    slope_degrees: Optional[float] = None


class LandParcelResponse(LandParcelBase):
    id: UUID
    survey_number: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LandParcelGeoResponse(LandParcelResponse):
    geometry_geojson: Optional[dict] = None  # serialized from geometry


# ---------------------------------------------------------------------------
# Developer
# ---------------------------------------------------------------------------
class DeveloperCreate(BaseModel):
    name: str
    company: Optional[str] = None
    email: EmailStr
    state_registration: Optional[str] = None
    track_record_json: Optional[dict] = {}


class DeveloperResponse(BaseModel):
    id: UUID
    name: str
    company: Optional[str] = None
    email: str
    trust_score: float
    state_registration: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Proposal
# ---------------------------------------------------------------------------
class ProposalCreate(BaseModel):
    developer_id: UUID
    project_type: ProjectType
    capacity_mw: float = Field(..., gt=0, le=5000, description="Project capacity in MW")
    district: str
    boundary_geojson: dict = Field(..., description="GeoJSON Polygon of the proposed boundary")

    @field_validator("boundary_geojson")
    @classmethod
    def validate_geojson(cls, v):
        if v.get("type") not in ("Polygon", "Feature", "FeatureCollection"):
            raise ValueError("boundary_geojson must be a GeoJSON Polygon, Feature, or FeatureCollection")
        return v


class ProposalResponse(BaseModel):
    id: UUID
    developer_id: UUID
    project_type: ProjectType
    capacity_mw: float
    district: str
    status: ProposalStatus
    boundary_geojson: dict
    submitted_at: datetime
    analyzed_at: Optional[datetime] = None
    decided_at: Optional[datetime] = None
    analysis_task_id: Optional[str] = None

    class Config:
        from_attributes = True


class ProposalDetailResponse(ProposalResponse):
    agent_results_json: Optional[dict] = None
    council_decision_json: Optional[dict] = None
    officer_notes: Optional[str] = None
    trust_score: Optional["TrustScoreResponse"] = None
    conflicts: list["ConflictResponse"] = []


# ---------------------------------------------------------------------------
# Trust Score
# ---------------------------------------------------------------------------
class TrustScoreResponse(BaseModel):
    id: UUID
    proposal_id: UUID
    overall_score: float
    grade: GradeEnum
    factor_breakdown: dict
    computed_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Conflict
# ---------------------------------------------------------------------------
class ConflictResponse(BaseModel):
    id: UUID
    proposal_id: UUID
    conflict_type: str
    severity: ConflictSeverity
    description: Optional[str] = None
    overlap_area_ha: Optional[float] = None
    source_department: Optional[str] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Audit Log
# ---------------------------------------------------------------------------
class AuditLogEntry(BaseModel):
    id: UUID
    agent_name: str
    action: str
    payload_hash: str
    prev_hash: Optional[str] = None
    chain_hash: str
    timestamp: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------
class AnalysisStatusResponse(BaseModel):
    proposal_id: UUID
    status: ProposalStatus
    task_id: Optional[str] = None
    task_state: Optional[str] = None  # PENDING / STARTED / SUCCESS / FAILURE
    progress_pct: Optional[int] = None
    message: Optional[str] = None


class DecisionRequest(BaseModel):
    action: str = Field(..., pattern="^(approve|reject|request_more_info|escalate)$")
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    role: UserRole = UserRole.developer
    department: Optional[str] = None
    district: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: Optional[str] = None
    role: UserRole
    department: Optional[str] = None
    district: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------
class SiteRecommendationRequest(BaseModel):
    project_type: ProjectType
    capacity_mw: float
    preferred_districts: list[str] = []


class SiteRecommendation(BaseModel):
    land_parcel: LandParcelResponse
    match_score: float
    trust_score_estimate: float
    recommendation_reason: str


class DeveloperRecommendation(BaseModel):
    developer: DeveloperResponse
    match_score: float
    recommendation_reason: str


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
class DashboardSummary(BaseModel):
    total_proposals: int
    pending: int
    analyzing: int
    approved: int
    rejected: int
    escalated: int
    total_approved_mw: float
    avg_trust_score: float
    conflict_rate_pct: float
    district_breakdown: dict[str, int]
    user_summary: Optional[list[dict]] = None


ProposalDetailResponse.model_rebuild()
