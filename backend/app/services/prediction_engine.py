"""
Prediction Engine
GPT-4o powered forecasting for conflict risk, grid congestion,
environmental risk, and demand-supply gaps.
"""
import asyncio
import json
from sqlalchemy.orm import Session
from app.models import Proposal, Conflict, TrustScore, LandParcel
from app.models.models import ProposalStatus


def _run_async(coro):
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(coro)
    loop.close()
    return result


def predict_conflict_risk(parcel_id: str, db: Session) -> dict:
    from app.agents.base import call_gpt
    from app.stubs import revenue_stub, forest_stub, seiaa_stub

    rev = revenue_stub.query(parcel_id)
    forest = forest_stub.query(parcel_id)
    env = seiaa_stub.query(parcel_id)

    system_prompt = """You are a conflict prediction agent. Based on land data, predict conflict risk.
Respond ONLY with JSON:
{
  "conflict_risk_score": <0-100>,
  "risk_level": "low" | "medium" | "high" | "critical",
  "predicted_conflict_types": [str],
  "confidence": <0-100>,
  "risk_drivers": [str],
  "recommendation": str
}"""

    user_content = f"Parcel: {parcel_id}\nRevenue: {json.dumps(rev)}\nForest: {json.dumps(forest)}\nEnv: {json.dumps(env)}"

    async def _call():
        return await call_gpt(system_prompt, user_content, "conflict_prediction")

    return _run_async(_call())


def forecast_grid_congestion(district: str, db: Session) -> dict:
    from app.agents.base import call_gpt

    # Get approved MW in district
    approved_mw = (
        db.query(Proposal)
        .filter(Proposal.district.ilike(f"%{district}%"), Proposal.status == ProposalStatus.approved)
        .all()
    )
    total_mw = sum(p.capacity_mw for p in approved_mw)

    from app.stubs import aptransco_stub
    grid_data = aptransco_stub.query(district)

    system_prompt = """You are a grid forecasting agent for APTRANSCO / NREDCAP.
Respond ONLY with JSON:
{
  "current_utilization_pct": <0-100>,
  "forecast_12_months": <0-100>,
  "forecast_24_months": <0-100>,
  "congestion_risk": "low" | "medium" | "high" | "critical",
  "bottleneck_substations": [str],
  "recommended_upgrades": [str],
  "summary": str
}"""

    user_content = f"District: {district}\nApproved pipeline MW: {total_mw}\nGrid data: {json.dumps(grid_data)}"

    async def _call():
        return await call_gpt(system_prompt, user_content, "grid_congestion")

    return _run_async(_call())


def forecast_environmental_risk(parcel_id: str, db: Session) -> dict:
    from app.agents.base import call_gpt
    from app.stubs import forest_stub, seiaa_stub

    forest = forest_stub.query(parcel_id)
    env = seiaa_stub.query(parcel_id)

    system_prompt = """You are an environmental risk forecasting agent.
Respond ONLY with JSON:
{
  "current_risk_level": "low" | "medium" | "high",
  "risk_3_years": "low" | "medium" | "high",
  "risk_5_years": "low" | "medium" | "high",
  "risk_drivers": [str],
  "vegetation_change_risk": str,
  "water_table_risk": str,
  "slope_stability_risk": str,
  "recommendation": str
}"""

    user_content = f"Parcel: {parcel_id}\nForest: {json.dumps(forest)}\nEnv: {json.dumps(env)}"

    async def _call():
        return await call_gpt(system_prompt, user_content, "env_risk")

    return _run_async(_call())


def get_demand_supply_gap(db: Session) -> dict:
    from app.agents.base import call_gpt

    # District-wise stats
    districts = {}
    rows = db.query(Proposal.district, Proposal.capacity_mw, Proposal.status).all()
    for d, mw, s in rows:
        if d not in districts:
            districts[d] = {"district": d, "total_proposed_mw": 0, "approved_mw": 0, "rejected": 0}
        districts[d]["total_proposed_mw"] += mw
        if str(s) == "approved":
            districts[d]["approved_mw"] += mw
        elif str(s) == "rejected":
            districts[d]["rejected"] += 1

    system_prompt = """You are a demand-supply gap analyst for NREDCAP renewable energy.
Respond ONLY with JSON:
{
  "scarcity_risk_districts": [{"district": str, "risk": "low"|"medium"|"high", "gap_mw": int}],
  "surplus_districts": [{"district": str, "unallocated_potential_mw": int}],
  "overall_assessment": str,
  "proactive_land_banking_recommendations": [str]
}"""

    user_content = f"District stats:\n{json.dumps(list(districts.values()), indent=2)}"

    async def _call():
        return await call_gpt(system_prompt, user_content, "demand_supply")

    return _run_async(_call())
