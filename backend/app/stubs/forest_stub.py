"""
AP Forest Department Stub
Returns mock forest coverage, wildlife corridor proximity, and protected area data.
In production, replace with AP Forest Department GIS API.
"""
import random
from typing import Any


IS_LIVE = False


def query(parcel_id: str, geometry: dict | None = None) -> dict[str, Any]:
    """
    Simulate Forest Department query for ecological constraints.
    """
    seed = sum(ord(c) for c in str(parcel_id)) + 1000
    rng = random.Random(seed)

    forest_pct = round(rng.uniform(0, 35), 2)
    has_corridor = rng.random() < 0.25
    protected_buffer_km = round(rng.uniform(0.5, 15.0), 2)

    wildlife_corridors = []
    if has_corridor:
        wildlife_corridors = [
            {
                "name": rng.choice([
                    "Nagarjunasagar-Srisailam Tiger Reserve Buffer",
                    "Papikonda Wildlife Sanctuary Corridor",
                    "Lankamalai Reserve Forest",
                ]),
                "distance_km": round(rng.uniform(0.2, 5.0), 2),
                "category": rng.choice(["wildlife_sanctuary", "tiger_reserve_buffer", "reserve_forest"]),
            }
        ]

    return {
        "source": "AP Forest Department (Stub)",
        "is_live": IS_LIVE,
        "parcel_id": str(parcel_id),
        "forest_coverage_pct": forest_pct,
        "vegetation_density": "high" if forest_pct > 20 else ("medium" if forest_pct > 8 else "low"),
        "protected_area_buffer_km": protected_buffer_km,
        "inside_protected_area": protected_buffer_km < 1.0,
        "wildlife_corridors": wildlife_corridors,
        "tree_density_per_ha": rng.randint(0, 120),
        "eco_sensitivity_zone": rng.choice(["ESZ-I", "ESZ-II", "ESZ-III", "none"]),
        "forest_clearance_required": forest_pct > 5 or protected_buffer_km < 2.0,
    }
