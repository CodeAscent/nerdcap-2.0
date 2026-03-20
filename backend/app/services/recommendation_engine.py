"""
Recommendation Engine
Site and developer recommendations using trust score × match score.
Policy insights via GPT-4o pattern analysis.
"""
import json
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import LandParcel, Developer, TrustScore, Proposal
from app.models.models import ProposalStatus


def recommend_sites_for_developer(
    project_type: str,
    capacity_mw: float,
    preferred_districts: list[str],
    db: Session,
) -> list[dict]:
    """
    Rank land parcels by trust score estimate × area match for a developer's requirements.
    """
    query = db.query(LandParcel)
    if preferred_districts:
        query = query.filter(LandParcel.district.in_(preferred_districts))

    parcels = query.limit(20).all()

    # Estimate trust from existing proposals on same parcel
    results = []
    for parcel in parcels:
        # Area suitability: 1MW solar needs ~2ha; 1MW wind needs ~4ha
        area_needed = capacity_mw * (2.0 if project_type == "solar" else 4.0)
        area_match = min(1.0, parcel.area_ha / max(area_needed, 1))

        # Trust estimate from existing proposal scores or default 60
        avg_score = 60.0
        proposals = db.query(Proposal).filter(
            Proposal.land_parcel_id == parcel.id,
            Proposal.status == ProposalStatus.approved,
        ).all()
        if proposals:
            scores = [p.trust_score.overall_score for p in proposals if p.trust_score]
            if scores:
                avg_score = sum(scores) / len(scores)

        match_score = round(avg_score * area_match, 1)
        results.append({
            "land_parcel_id": str(parcel.id),
            "name": parcel.name,
            "district": parcel.district,
            "area_ha": parcel.area_ha,
            "ownership_type": parcel.ownership_type,
            "match_score": match_score,
            "trust_score_estimate": round(avg_score, 1),
            "recommendation_reason": (
                f"Area suitable for {capacity_mw}MW {project_type} project. "
                f"District match: {'preferred' if parcel.district in preferred_districts else 'alternative'}. "
                f"Estimated trust score: {round(avg_score, 1)}"
            ),
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:10]


def recommend_developers_for_site(parcel_id: UUID, db: Session) -> list[dict]:
    """
    Rank developers by trust score × financial readiness for a given site.
    """
    developers = db.query(Developer).order_by(desc(Developer.trust_score)).limit(10).all()

    results = []
    for dev in developers:
        results.append({
            "developer_id": str(dev.id),
            "name": dev.name,
            "company": dev.company,
            "trust_score": dev.trust_score,
            "match_score": dev.trust_score,
            "recommendation_reason": (
                f"Developer trust score {dev.trust_score:.1f}/100. "
                f"Registered: {dev.state_registration or 'AP'}. "
                f"Track record: {len(dev.track_record_json or {})} projects."
            ),
        })

    return results


def get_policy_insights(db: Session) -> dict:
    """
    Use GPT-4o to analyze allocation patterns and generate policy insights.
    """
    import asyncio
    from app.agents.base import call_gpt

    # Gather stats
    district_rows = (
        db.query(Proposal.district, Proposal.project_type, Proposal.status)
        .all()
    )
    stats: dict[str, Any] = {}
    for d, pt, s in district_rows:
        key = f"{d}_{pt}"
        if key not in stats:
            stats[key] = {"district": d, "type": pt, "total": 0, "approved": 0}
        stats[key]["total"] += 1
        if str(s) == "approved":
            stats[key]["approved"] += 1

    system_prompt = """You are a policy analysis agent for NREDCAP, the Andhra Pradesh renewable energy authority.
Analyze the given allocation statistics and produce actionable policy insights.

Respond ONLY with JSON:
{
  "key_insights": [<3-5 string insights with district names and MW figures>],
  "underutilized_districts": [{"district": str, "potential_mw": int, "reason": str}],
  "emerging_conflict_zones": [{"district": str, "risk_level": str, "reason": str}],
  "recommendations": [<3 policy recommendations for NREDCAP officers>],
  "summary": "<2-3 sentence executive summary>"
}"""

    user_content = f"Allocation statistics:\n{json.dumps(list(stats.values()), indent=2)}"

    async def _call():
        return await call_gpt(system_prompt, user_content, "policy_insights")

    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(_call())
        loop.close()
    except Exception as e:
        result = {"error": str(e), "summary": "Unable to generate insights at this time."}

    return result
