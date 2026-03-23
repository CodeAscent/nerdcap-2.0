"""
Celery Background Task: Full AI Analysis Pipeline
Runs the 5-agent orchestration and stores all results in DB.
"""
import asyncio
import logging
import traceback
from datetime import datetime

from app.database import SessionLocal
from app.models import Proposal
from app.models.models import ProposalStatus


def run_analysis_background(proposal_id: str):
    """
    Background task (runs in FastAPI BackgroundTasks, or can be Celery task).
    Runs the full multi-agent analysis and persists results.
    """
    db = SessionLocal()
    try:
        from app.agents.orchestrator import run_analysis
        from app.services import trust_score_engine, conflict_detector, audit_chain

        proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
        if not proposal:
            return

        # Build proposal context dict
        proposal_data = {
            "proposal_id": proposal_id,
            "project_type": proposal.project_type.value,
            "capacity_mw": proposal.capacity_mw,
            "district": proposal.district,
            "boundary_geojson": proposal.boundary_geojson,
        }

        # Log: analysis started
        audit_chain.append(proposal_id, "Orchestrator", "analysis_started", proposal_data, db)

        # Run async orchestration in sync context
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(run_analysis(proposal_id, proposal_data, db))
        finally:
            loop.close()

        # After the async pipeline, explicitly rollback any aborted transaction that
        # may have been caused by a SQL error inside run_analysis (e.g. a bad PostGIS
        # query). This resets the session to a clean state so subsequent writes work.
        try:
            db.rollback()
        except Exception:
            pass

        # Persist agent results
        agent_results_dict = []
        for ar in result.agent_results:
            agent_results_dict.append({
                "agent_name": ar.agent_name,
                "confidence": ar.confidence,
                "findings": ar.findings,
                "flags": ar.flags,
                "success": ar.success,
            })
            # Log each agent result
            audit_chain.append(proposal_id, ar.agent_name, "agent_result", {
                "confidence": ar.confidence, "flags": ar.flags
            }, db)

        # Re-fetch proposal after rollback so we're working with a fresh ORM object
        proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
        # Persist council decision
        proposal.agent_results_json = {"agents": agent_results_dict}
        proposal.council_decision_json = result.council_decision

        # Compute trust score
        trust_score_engine.compute_and_store(proposal_id, result.council_decision, db)

        # Store conflicts (including spatial conflicts)
        conflict_detector.store_from_council(proposal_id, result.council_decision, db, result.spatial_conflicts)

        # Log: council completed
        audit_chain.append(proposal_id, "FTM Council", "deliberation_completed", {
            "overall_score": result.overall_score,
            "grade": result.grade,
            "conflict_status": result.council_decision.get("conflict_status"),
        }, db)

        # Mark as analyzed
        proposal.status = ProposalStatus.analyzed
        proposal.analyzed_at = datetime.utcnow()

        db.commit()

    except Exception as e:
        logging.error(f"[Analysis {proposal_id}] FAILED: {type(e).__name__}: {e}")
        logging.error(traceback.format_exc())
        db.rollback()
        try:
            proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
            if proposal:
                proposal.status = ProposalStatus.pending
                db.commit()
        except Exception:
            pass
        raise e
    finally:
        db.close()
