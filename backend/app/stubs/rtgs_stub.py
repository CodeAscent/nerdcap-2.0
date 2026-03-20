"""
RTGS (Real Time Governance Society) Stub
Simulates the AP RTGS data lake endpoint for pushing allocation decisions.
In production, replace with actual RTGS API endpoint.
"""
from typing import Any
from datetime import datetime


IS_LIVE = False

# In-memory store of synced records (for demo purposes)
_synced_records: list[dict] = []


def sync_allocation(proposal_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """
    Sync an approved allocation decision to RTGS data lake.
    """
    record = {
        "rtgs_sync_id": f"RTGS-{len(_synced_records) + 1:06d}",
        "proposal_id": str(proposal_id),
        "synced_at": datetime.utcnow().isoformat(),
        "status": "synced",
        "data": data,
    }
    _synced_records.append(record)
    return {
        "source": "RTGS (Stub)",
        "is_live": IS_LIVE,
        "synced": True,
        "rtgs_sync_id": record["rtgs_sync_id"],
        "message": "Allocation data successfully pushed to RTGS data lake (stub)",
    }


def get_all_synced() -> list[dict]:
    """
    Return all synced records (for dashboard aggregation).
    """
    return _synced_records


def get_status() -> dict[str, Any]:
    """
    Return stub status information.
    """
    return {
        "source": "RTGS (Stub)",
        "is_live": IS_LIVE,
        "total_synced": len(_synced_records),
        "last_sync": _synced_records[-1]["synced_at"] if _synced_records else None,
    }
