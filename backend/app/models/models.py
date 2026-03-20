import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Float, DateTime, Text, Enum as SAEnum, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from app.database import Base


class ProjectType(str, enum.Enum):
    solar = "solar"
    wind = "wind"
    hybrid = "hybrid"


class ProposalStatus(str, enum.Enum):
    pending = "pending"
    analyzing = "analyzing"
    analyzed = "analyzed"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"
    escalated = "escalated"


class GradeEnum(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class ConflictSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class UserRole(str, enum.Enum):
    developer = "developer"
    officer = "officer"
    admin = "admin"


# ---------------------------------------------------------------------------
# Land Parcel
# ---------------------------------------------------------------------------
class LandParcel(Base):
    __tablename__ = "land_parcels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    survey_number = Column(String(100))
    district = Column(String(100), nullable=False)
    mandal = Column(String(100))
    village = Column(String(100))
    area_ha = Column(Float, nullable=False)
    geometry = Column(Geometry("POLYGON", srid=4326), nullable=False)
    ownership_type = Column(String(50))  # private / government / pattadar
    land_use_type = Column(String(100))  # barren / agricultural / waste land
    elevation_m = Column(Float)
    slope_degrees = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    proposals = relationship("Proposal", back_populates="land_parcel")


# ---------------------------------------------------------------------------
# Developer
# ---------------------------------------------------------------------------
class Developer(Base):
    __tablename__ = "developers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    company = Column(String(200))
    email = Column(String(255), unique=True)
    trust_score = Column(Float, default=50.0)
    track_record_json = Column(JSONB, default={})  # past projects, completion rates
    financial_cert_url = Column(String(500))
    state_registration = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    proposals = relationship("Proposal", back_populates="developer")


# ---------------------------------------------------------------------------
# Proposal
# ---------------------------------------------------------------------------
class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    developer_id = Column(UUID(as_uuid=True), ForeignKey("developers.id"), nullable=False)
    land_parcel_id = Column(UUID(as_uuid=True), ForeignKey("land_parcels.id"))
    project_type = Column(SAEnum(ProjectType), nullable=False)
    capacity_mw = Column(Float, nullable=False)
    district = Column(String(100), nullable=False)
    boundary_geojson = Column(JSONB, nullable=False)  # submitted boundary
    boundary_geometry = Column(Geometry("POLYGON", srid=4326))
    status = Column(SAEnum(ProposalStatus), default=ProposalStatus.pending)
    analysis_task_id = Column(String(200))  # Celery task ID
    agent_results_json = Column(JSONB)  # raw per-agent results
    council_decision_json = Column(JSONB)  # FTM Council output
    officer_notes = Column(Text)
    decided_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    submitted_at = Column(DateTime, default=datetime.utcnow)
    analyzed_at = Column(DateTime)
    decided_at = Column(DateTime)

    developer = relationship("Developer", back_populates="proposals")
    land_parcel = relationship("LandParcel", back_populates="proposals")
    trust_score = relationship("TrustScore", back_populates="proposal", uselist=False)
    conflicts = relationship("Conflict", back_populates="proposal")
    audit_logs = relationship("AuditLog", back_populates="proposal", order_by="AuditLog.timestamp")


# ---------------------------------------------------------------------------
# Trust Score
# ---------------------------------------------------------------------------
class TrustScore(Base):
    __tablename__ = "trust_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proposal_id = Column(UUID(as_uuid=True), ForeignKey("proposals.id"), unique=True, nullable=False)
    overall_score = Column(Float, nullable=False)  # 0–100
    grade = Column(SAEnum(GradeEnum), nullable=False)
    factor_breakdown = Column(JSONB, nullable=False)
    # {"clean_title": 22.5, "no_disputes": 18.0, "env_clearance": 16.0, ...}
    computed_at = Column(DateTime, default=datetime.utcnow)

    proposal = relationship("Proposal", back_populates="trust_score")


# ---------------------------------------------------------------------------
# Conflict
# ---------------------------------------------------------------------------
class Conflict(Base):
    __tablename__ = "conflicts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proposal_id = Column(UUID(as_uuid=True), ForeignKey("proposals.id"), nullable=False)
    conflict_type = Column(String(100), nullable=False)
    # e.g. "existing_project_overlap", "forest_zone", "transmission_line", "eia_zone", "disputed_title"
    severity = Column(SAEnum(ConflictSeverity), nullable=False)
    description = Column(Text)
    overlap_area_ha = Column(Float)
    conflict_geometry = Column(Geometry("POLYGON", srid=4326))
    source_department = Column(String(100))

    proposal = relationship("Proposal", back_populates="conflicts")


# ---------------------------------------------------------------------------
# Audit Log (hash-chain)
# ---------------------------------------------------------------------------
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proposal_id = Column(UUID(as_uuid=True), ForeignKey("proposals.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    action = Column(String(200), nullable=False)
    payload_json = Column(JSONB)
    payload_hash = Column(String(64), nullable=False)   # SHA-256 of payload
    prev_hash = Column(String(64))                       # previous log entry's hash
    chain_hash = Column(String(64), nullable=False)      # SHA-256(payload_hash + prev_hash)
    timestamp = Column(DateTime, default=datetime.utcnow)

    proposal = relationship("Proposal", back_populates="audit_logs")


# ---------------------------------------------------------------------------
# User (Officers / Developers / Admins)
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.developer)
    department = Column(String(200))
    district = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class OfficerScore(Base):
    __tablename__ = "officer_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    score = Column(Float, nullable=False)
    avg_response_time_hours = Column(Float)
    proposals_decided = Column(Integer, default=0)
    data_freshness_score = Column(Float, default=0.0)
    escalation_resolution_rate = Column(Float, default=0.0)
    collaboration_index = Column(Float, default=0.0)
    computed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
