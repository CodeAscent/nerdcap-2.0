"""
Hash-Chain Audit Log Service
Each entry's chain_hash = SHA-256(payload_hash + prev_chain_hash).
Immutable by design — ensures audit trail integrity.
"""
import hashlib
import json
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session
from app.models import AuditLog


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def append(
    proposal_id: str,
    agent_name: str,
    action: str,
    payload: Any,
    db: Session,
) -> AuditLog:
    """
    Append a new audit log entry linked to the previous entry's chain hash.
    """
    payload_str = json.dumps(payload, default=str)
    payload_hash = _sha256(payload_str)

    # Get previous hash
    last = (
        db.query(AuditLog)
        .filter(AuditLog.proposal_id == proposal_id)
        .order_by(AuditLog.timestamp.desc())
        .first()
    )
    prev_hash = last.chain_hash if last else "0" * 64
    chain_hash = _sha256(payload_hash + prev_hash)

    log = AuditLog(
        id=uuid.uuid4(),
        proposal_id=proposal_id,
        agent_name=agent_name,
        action=action,
        payload_json=payload if isinstance(payload, dict) else {"data": str(payload)},
        payload_hash=payload_hash,
        prev_hash=prev_hash,
        chain_hash=chain_hash,
        timestamp=datetime.utcnow(),
    )
    db.add(log)
    db.flush()
    return log


def verify_chain(proposal_id: str, db: Session) -> dict:
    """
    Verify the integrity of the entire audit chain for a proposal.
    Returns {"valid": bool, "entries_verified": int, "broken_at": None | log_id}
    """
    logs = (
        db.query(AuditLog)
        .filter(AuditLog.proposal_id == proposal_id)
        .order_by(AuditLog.timestamp)
        .all()
    )

    prev_hash = "0" * 64
    for i, log in enumerate(logs):
        expected_chain = _sha256(log.payload_hash + prev_hash)
        if expected_chain != log.chain_hash:
            return {"valid": False, "entries_verified": i, "broken_at": str(log.id)}
        prev_hash = log.chain_hash

    return {"valid": True, "entries_verified": len(logs), "broken_at": None}
