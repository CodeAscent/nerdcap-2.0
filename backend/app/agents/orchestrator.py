"""
AI Agent Orchestrator
Dispatches all 5 sub-agents in parallel and sends results to FTM Council.
Also runs GIS spatial analysis before FTM Council deliberation.
"""
import asyncio
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.orm import Session

from app.config import get_settings
from app.services.spatial_analysis import run_spatial_analysis

settings = get_settings()


@dataclass
class AgentResult:
    agent_name: str
    confidence: float  # 0–100
    findings: dict[str, Any]
    flags: list[str]
    raw_response: str
    success: bool = True
    error: str | None = None


@dataclass
class OrchestrationResult:
    proposal_id: str
    agent_results: list[AgentResult]
    spatial_conflicts: dict[str, Any]
    council_decision: dict[str, Any]
    overall_score: float
    grade: str
    success: bool = True


async def run_analysis(proposal_id: str, proposal_data: dict, db: Session) -> OrchestrationResult:
    """
    Run all agents in parallel, perform spatial analysis, then deliberate via FTM Council.
    """
    from app.agents.land_records import run as land_agent
    from app.agents.eco_compliance import run as eco_agent
    from app.agents.env_clearance import run as env_agent
    from app.agents.grid_infrastructure import run as grid_agent
    from app.agents.cadastral import run as cadastral_agent
    from app.agents.ftm_council import deliberate

    results = await asyncio.gather(
        land_agent(proposal_id, proposal_data),
        eco_agent(proposal_id, proposal_data),
        env_agent(proposal_id, proposal_data),
        grid_agent(proposal_id, proposal_data),
        cadastral_agent(proposal_id, proposal_data),
        return_exceptions=True,
    )

    agent_results = []
    for r in results:
        if isinstance(r, Exception):
            agent_results.append(AgentResult(
                agent_name="unknown",
                confidence=0,
                findings={},
                flags=["agent_failed"],
                raw_response=str(r),
                success=False,
                error=str(r),
            ))
        else:
            agent_results.append(r)

    spatial_conflicts = {"has_spatial_conflicts": False, "all_conflicts": []}
    boundary_geometry = proposal_data.get("boundary_geojson") or proposal_data.get("boundary_geometry")
    if boundary_geometry and db:
        try:
            spatial_conflicts = run_spatial_analysis(proposal_id, boundary_geometry, db)
        except Exception as e:
            spatial_conflicts = {
                "has_spatial_conflicts": False,
                "all_conflicts": [],
                "error": str(e),
            }

    council_decision = await deliberate(proposal_id, proposal_data, agent_results, spatial_conflicts)

    overall_score = council_decision.get("overall_trust_score", 50.0)
    grade = council_decision.get("grade", "C")

    return OrchestrationResult(
        proposal_id=proposal_id,
        agent_results=agent_results,
        spatial_conflicts=spatial_conflicts,
        council_decision=council_decision,
        overall_score=overall_score,
        grade=grade,
    )
