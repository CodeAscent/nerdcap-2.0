"""
APTRANSCO / DISCOM Grid Infrastructure Stub
Returns substation proximity, available evacuation capacity, and transmission conflict data.
In production, replace with APTRANSCO API / GIS service.
"""
import random
from typing import Any


IS_LIVE = False

SUBSTATION_NAMES = [
    "Kurnool 220kV Substation", "Nandyal 132kV Substation",
    "Anantapur 220kV Substation", "Kadapa 132kV Substation",
    "Hindupur 33kV Substation", "Tirupati 220kV Substation",
    "Ongole 132kV Substation", "Nellore 220kV Substation",
]

DISCOM_NAMES = ["APSPDCL", "APCPDCL", "APEPDCL"]


def query(parcel_id: str, geometry: dict | None = None) -> dict[str, Any]:
    """
    Simulate APTRANSCO query for grid infrastructure.
    """
    seed = sum(ord(c) for c in str(parcel_id)) + 3000
    rng = random.Random(seed)

    nearest_km = round(rng.uniform(1.5, 45.0), 2)
    capacity_mw = round(rng.uniform(10, 500), 1)
    has_transmission_conflict = rng.random() < 0.2

    transmission_conflicts = []
    if has_transmission_conflict:
        transmission_conflicts = [
            {
                "line_name": f"{rng.randint(66, 400)}kV Transmission Line",
                "voltage_kv": rng.choice([66, 132, 220, 400]),
                "overlap_km": round(rng.uniform(0.1, 3.0), 2),
                "right_of_way_m": rng.choice([30, 52, 65]),
            }
        ]

    return {
        "source": "APTRANSCO (Stub)",
        "is_live": IS_LIVE,
        "parcel_id": str(parcel_id),
        "nearest_substation": rng.choice(SUBSTATION_NAMES),
        "nearest_substation_km": nearest_km,
        "substation_voltage_kv": rng.choice([33, 132, 220]),
        "available_evacuation_capacity_mw": capacity_mw,
        "grid_connectivity_feasibility": (
            "excellent" if nearest_km < 5 else
            ("good" if nearest_km < 15 else
             ("moderate" if nearest_km < 30 else "poor"))
        ),
        "estimated_transmission_cost_cr": round(nearest_km * rng.uniform(0.8, 1.5), 2),
        "transmission_line_conflicts": transmission_conflicts,
        "discom": rng.choice(DISCOM_NAMES),
        "grid_congestion_risk": rng.choice(["low", "low", "medium", "high"]),
        "peak_demand_mw": round(rng.uniform(200, 2000), 1),
    }
