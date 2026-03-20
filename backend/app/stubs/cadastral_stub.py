"""
Cadastral / Survey & Land Records Stub
Returns boundary verification, area discrepancy, and survey record data.
In production, replace with AP cadastral GIS API (Survey Settlement & Land Records Dept).
"""
import random
from typing import Any


IS_LIVE = False


def query(parcel_id: str, geometry: dict | None = None, submitted_area_ha: float | None = None) -> dict[str, Any]:
    """
    Simulate Cadastral verification query.
    """
    seed = sum(ord(c) for c in str(parcel_id)) + 4000
    rng = random.Random(seed)

    boundary_verified = rng.random() < 0.85
    discrepancy_pct = round(rng.uniform(0, 12.0), 2) if not boundary_verified else round(rng.uniform(0, 2.0), 2)
    survey_number = f"{rng.randint(100, 999)}/{rng.randint(1, 50)}"

    return {
        "source": "Cadastral Survey (Stub)",
        "is_live": IS_LIVE,
        "parcel_id": str(parcel_id),
        "survey_number": survey_number,
        "village_map_reference": f"VMP-{rng.randint(1000, 9999)}",
        "boundary_verified": boundary_verified,
        "area_discrepancy_pct": discrepancy_pct,
        "recorded_area_ha": (
            round((submitted_area_ha or 50) * (1 - discrepancy_pct / 100), 2)
            if submitted_area_ha else round(rng.uniform(20, 200), 2)
        ),
        "last_survey_year": rng.randint(2010, 2024),
        "boundary_disputes": not boundary_verified and rng.random() < 0.3,
        "sub_division_pending": rng.random() < 0.1,
        "phodi_sketch_available": rng.random() < 0.7,
    }
