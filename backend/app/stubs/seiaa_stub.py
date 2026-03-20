"""
SEIAA-AP (State Environment Impact Assessment Authority) Stub
Returns EIA zone classification, CRZ overlap, and clearance pathway info.
In production, replace with SEIAA-AP API.
"""
import random
from typing import Any


IS_LIVE = False


EIA_ZONES = ["A", "B1", "B2"]
CLEARANCE_STATUS = ["pre_clearance_required", "no_objection", "detailed_eia_required"]


def query(parcel_id: str, geometry: dict | None = None) -> dict[str, Any]:
    """
    Simulate SEIAA-AP query for environmental constraints.
    """
    seed = sum(ord(c) for c in str(parcel_id)) + 2000
    rng = random.Random(seed)

    crz_overlap = round(rng.uniform(0, 15), 2)
    eia_zone = rng.choice(["A", "A", "B1", "B1", "B2"])  # weighted toward B1
    eco_sensitive = rng.random() < 0.2

    sensitivity = "high" if eco_sensitive or eia_zone == "A" else ("medium" if eia_zone == "B1" else "low")

    return {
        "source": "SEIAA-AP (Stub)",
        "is_live": IS_LIVE,
        "parcel_id": str(parcel_id),
        "eia_zone": eia_zone,
        "eia_zone_description": {
            "A": "Category A — mandatory EIA + public hearing",
            "B1": "Category B1 — state-level EIA required",
            "B2": "Category B2 — simplified screening only",
        }[eia_zone],
        "crz_overlap_pct": crz_overlap,
        "crz_category": rng.choice(["CRZ-I", "CRZ-II", "CRZ-III", "none"]) if crz_overlap > 0 else "none",
        "eco_sensitive_zone": eco_sensitive,
        "ecological_sensitivity_index": round(rng.uniform(1.0, 10.0), 2),
        "clearance_status": rng.choice(CLEARANCE_STATUS),
        "estimated_clearance_months": rng.randint(3, 24),
        "air_quality_zone": rng.choice(["industrial", "residential", "sensitive", "eco-sensitive"]),
        "water_body_distance_km": round(rng.uniform(0.5, 20.0), 2),
        "sensitivity_level": sensitivity,
    }
