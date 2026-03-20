"""
Recommendations Router
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import LandParcel, Developer

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.get("/sites")
def recommend_sites(
    project_type: str = Query(..., description="solar | wind | hybrid"),
    capacity_mw: float = Query(..., gt=0),
    districts: str = Query("", description="Comma-separated district names"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.services.recommendation_engine import recommend_sites_for_developer
    preferred = [d.strip() for d in districts.split(",") if d.strip()] if districts else []
    results = recommend_sites_for_developer(project_type, capacity_mw, preferred, db)
    return results


from uuid import UUID

@router.get("/developers")
def recommend_developers(
    parcel_id: UUID = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.services.recommendation_engine import recommend_developers_for_site
    results = recommend_developers_for_site(parcel_id, db)
    return results


@router.get("/policy-insights")
def policy_insights(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.services.recommendation_engine import get_policy_insights
    return get_policy_insights(db)
