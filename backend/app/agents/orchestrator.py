"""
AI Agent Orchestrator
Dispatches all 5 sub-agents in parallel and sends results to FTM Council.
"""
import asyncio
from dataclasses import dataclass, field
from typing import Any

from app.config import get_settings

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
    council_decision: dict[str, Any]
    overall_score: float
    grade: str
    success: bool = True


async def run_analysis(proposal_id: str, proposal_data: dict) -> OrchestrationResult:
    """
    Run all agents in parallel then deliberate via FTM Council.
    """
    from app.agents.land_records import run as land_agent
    from app.agents.eco_compliance import run as eco_agent
    from app.agents.env_clearance import run as env_agent
    from app.agents.grid_infrastructure import run as grid_agent
    from app.agents.cadastral import run as cadastral_agent
    from app.agents.ftm_council import deliberate

    # Dispatch all 5 agents in parallel
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

    # FTM Council deliberation
    council_decision = await deliberate(proposal_id, proposal_data, agent_results)

    overall_score = council_decision.get("overall_trust_score", 50.0)
    grade = council_decision.get("grade", "C")

    return OrchestrationResult(
        proposal_id=proposal_id,
        agent_results=agent_results,
        council_decision=council_decision,
        overall_score=overall_score,
        grade=grade,
    )
