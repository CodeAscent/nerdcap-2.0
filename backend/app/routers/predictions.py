"""
Predictions Router
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


@router.get("/conflicts")
def predict_conflicts(
    parcel_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.services.prediction_engine import predict_conflict_risk
    return predict_conflict_risk(parcel_id, db)


@router.get("/grid-congestion")
def predict_grid_congestion(
    district: str = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.services.prediction_engine import forecast_grid_congestion
    return forecast_grid_congestion(district, db)


@router.get("/environmental-risk")
def predict_environmental_risk(
    parcel_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.services.prediction_engine import forecast_environmental_risk
    return forecast_environmental_risk(parcel_id, db)


@router.get("/demand-supply-gap")
def demand_supply_gap(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.services.prediction_engine import get_demand_supply_gap
    return get_demand_supply_gap(db)
