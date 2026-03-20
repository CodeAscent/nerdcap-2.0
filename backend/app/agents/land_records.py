"""Land Records Agent — queries Revenue stub, reasons via GPT-4o"""
import json
from app.agents.base import call_gpt
from app.agents.orchestrator import AgentResult
from app.stubs import revenue_stub

SYSTEM_PROMPT = """You are the Land Records Agent in the NREDCAP AI Land Allocation System.
You analyze land ownership records from the Revenue Department and assess title risk for a proposed renewable energy project.

Respond ONLY with a JSON object containing:
{
  "confidence": <0-100 float>,
  "title_risk": "low" | "medium" | "high",
  "clean_title_score": <0-25 float, max contribution to trust score>,
  "no_disputes_score": <0-20 float, max contribution>,
  "findings": {<key facts about ownership, mutation, encumbrance>},
  "flags": [<list of risk flags, e.g. "disputed_title", "pending_litigation">],
  "recommendation": "<brief recommendation>",
  "summary": "<2-3 sentence human-readable summary>"
}"""


async def run(proposal_id: str, proposal_data: dict) -> AgentResult:
    stub_data = revenue_stub.query(proposal_id, proposal_data.get("boundary_geojson"))

    user_content = f"""
Proposal ID: {proposal_id}
District: {proposal_data.get('district', 'Unknown')}
Project Type: {proposal_data.get('project_type', 'solar')}
Capacity: {proposal_data.get('capacity_mw', 0)} MW

Revenue Department Data:
{json.dumps(stub_data, indent=2)}

Analyze the title risk and compute trust score contributions.
"""
    result = await call_gpt(SYSTEM_PROMPT, user_content, "land_records")
    return AgentResult(
        agent_name="Land Records Agent",
        confidence=result.get("confidence", 50),
        findings=result.get("findings", stub_data),
        flags=result.get("flags", []),
        raw_response=json.dumps(result),
        success="error" not in result,
        error=result.get("error"),
    )
