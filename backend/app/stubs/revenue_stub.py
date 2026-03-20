"""
Revenue Department Stub
Returns mock land ownership, title status, and dispute records.
In production, replace with actual AP Revenue Department API call.
"""
import random
from typing import Any
from datetime import date


IS_LIVE = False  # Set to True when real API keys are available


MOCK_RECORDS = {
    "clean": {
        "title_status": "clean",
        "dispute_records": [],
        "litigation_pending": False,
    },
    "disputed": {
        "title_status": "disputed",
        "dispute_records": [
            {"case_number": "RC-2021-0482", "court": "District Court, Kurnool", "status": "pending"}
        ],
        "litigation_pending": True,
    },
}

OWNER_NAMES = [
    "Sri Venkata Ramaiah", "Smt. Lakshmi Devi", "Sri Ranga Rao",
    "Government of Andhra Pradesh", "Sri Srinivasa Reddy", "Smt. Padmavathi"
]


def query(parcel_id: str, geometry: dict | None = None) -> dict[str, Any]:
    """
    Simulate Revenue Department query for land ownership and dispute status.
    """
    seed = sum(ord(c) for c in str(parcel_id))
    rng = random.Random(seed)

    title_key = rng.choice(["clean", "clean", "clean", "disputed"])  # 75% clean
    base = MOCK_RECORDS[title_key].copy()

    return {
        "source": "Revenue Department (Stub)",
        "is_live": IS_LIVE,
        "parcel_id": str(parcel_id),
        "owner_name": rng.choice(OWNER_NAMES),
        "pattadar_passbook": f"PP-{rng.randint(100000, 999999)}",
        "mutation_date": str(date(rng.randint(2015, 2023), rng.randint(1, 12), rng.randint(1, 28))),
        "ownership_type": rng.choice(["pattadar", "government", "inam", "assigned"]),
        "encumbrance_status": rng.choice(["clear", "clear", "mortgaged"]),
        **base,
    }
