"""
GIS Spatial Analysis Service
Uses PostGIS functions to detect spatial conflicts for land allocation proposals.
"""
import json
from typing import Any
from sqlalchemy import text
from sqlalchemy.orm import Session


STUB_TRANSMISSION_CORRIDORS = [
    {
        "name": "400kV Kurnool-Hyderabad Twin Circuit",
        "voltage_kv": 400,
        "geometry": "LINESTRING(78.0347 15.8281, 78.4744 16.5089, 78.9234 17.3844, 79.0832 17.6868, 78.4749 17.4246)",
        "buffer_m": 60,
    },
    {
        "name": "220kV Vijayawada-Guntur Line",
        "voltage_kv": 220,
        "geometry": "LINESTRING(80.6234 16.5063, 80.6442 16.3064, 80.4567 16.2378)",
        "buffer_m": 40,
    },
    {
        "name": "765kV Raichur-Nellore Corridor",
        "voltage_kv": 765,
        "geometry": "LINESTRING(77.3463 16.2076, 78.2345 15.8765, 79.4567 15.4321, 80.1234 14.9876)",
        "buffer_m": 90,
    },
    {
        "name": "132kV Tirupati-Chittoor Feeder",
        "voltage_kv": 132,
        "geometry": "LINESTRING(79.4192 13.6288, 79.3456 13.5678, 79.2345 13.2345)",
        "buffer_m": 25,
    },
    {
        "name": "400kV Vizag-Srikakulam Line",
        "voltage_kv": 400,
        "geometry": "LINESTRING(83.2185 17.6381, 83.4567 18.1234, 83.7890 18.4567)",
        "buffer_m": 60,
    },
]

STUB_PROTECTED_AREAS = [
    {
        "name": "Nagarjunasagar Srisailam Tiger Reserve",
        "type": "Tiger Reserve",
        "geometry": "POLYGON((78.8 16.3, 79.2 16.3, 79.2 16.7, 78.8 16.7, 78.8 16.3))",
        "area_ha": 356000,
    },
    {
        "name": "Coringa Wildlife Sanctuary",
        "type": "Wildlife Sanctuary",
        "geometry": "POLYGON((82.2 16.7, 82.5 16.7, 82.5 16.9, 82.2 16.9, 82.2 16.7))",
        "area_ha": 23570,
    },
    {
        "name": "Papikonda National Park",
        "type": "National Park",
        "geometry": "POLYGON((81.2 17.4, 81.6 17.4, 81.6 17.8, 81.2 17.8, 81.2 17.4))",
        "area_ha": 101159,
    },
    {
        "name": "Sri Venkateswara National Park",
        "type": "National Park",
        "geometry": "POLYGON((79.0 13.5, 79.5 13.5, 79.5 14.0, 79.0 14.0, 79.0 13.5))",
        "area_ha": 35362,
    },
    {
        "name": "Rollapadu Wildlife Sanctuary",
        "type": "Wildlife Sanctuary",
        "geometry": "POLYGON((78.3 15.6, 78.6 15.6, 78.6 15.9, 78.3 15.9, 78.3 15.6))",
        "area_ha": 614,
    },
    {
        "name": "Koundinya Wildlife Sanctuary",
        "type": "Wildlife Sanctuary",
        "geometry": "POLYGON((78.6 13.2, 79.0 13.2, 79.0 13.6, 78.6 13.6, 78.6 13.2))",
        "area_ha": 35800,
    },
    {
        "name": "Nellapattu Bird Sanctuary",
        "type": "Bird Sanctuary",
        "geometry": "POLYGON((79.9 14.4, 80.1 14.4, 80.1 14.6, 79.9 14.6, 79.9 14.4))",
        "area_ha": 404,
    },
]


def _geometry_to_wkt(geometry: dict | str) -> str:
    if isinstance(geometry, str):
        return geometry
    if isinstance(geometry, dict):
        if geometry.get("type") == "Polygon":
            coords = geometry.get("coordinates", [[]])
            rings = []
            for ring in coords:
                points = [f"{pt[0]} {pt[1]}" for pt in ring]
                rings.append(f"({', '.join(points)})")
            return f"POLYGON({', '.join(rings)})"
        elif geometry.get("type") == "MultiPolygon":
            coords = geometry.get("coordinates", [])
            polygons = []
            for poly in coords:
                rings = []
                for ring in poly:
                    points = [f"{pt[0]} {pt[1]}" for pt in ring]
                    rings.append(f"({', '.join(points)})")
                polygons.append(f"({', '.join(rings)})")
            return f"MULTIPOLYGON({', '.join(polygons)})"
    return ""


def detect_proposal_overlaps(
    proposal_id: str,
    boundary_geometry: dict | str,
    db: Session,
) -> list[dict[str, Any]]:
    wkt = _geometry_to_wkt(boundary_geometry)
    if not wkt:
        return []

    sql = text("""
        SELECT
            p.id,
            p.project_type,
            p.capacity_mw,
            p.district,
            d.name as developer_name,
            d.company as developer_company,
            ST_Area(
                ST_Transform(
                    ST_Intersection(p.boundary_geometry, ST_GeomFromText(:wkt, 4326))::geography
                )
            ) / 10000.0 AS overlap_area_ha
        FROM proposals p
        JOIN developers d ON p.developer_id = d.id
        WHERE p.id != :proposal_id::uuid
          AND p.status = 'approved'
          AND p.boundary_geometry IS NOT NULL
          AND ST_IsValid(p.boundary_geometry)
          AND ST_Intersects(p.boundary_geometry, ST_GeomFromText(:wkt, 4326))
    """)

    result = db.execute(sql, {"proposal_id": proposal_id, "wkt": wkt})
    overlaps = []

    for row in result:
        overlap_area = row.overlap_area_ha or 0
        if overlap_area > 0:
            overlaps.append({
                "conflict_type": "existing_project_overlap",
                "proposal_id": str(row.id),
                "project_type": row.project_type,
                "capacity_mw": row.capacity_mw,
                "district": row.district,
                "developer_name": row.developer_name,
                "developer_company": row.developer_company,
                "overlap_area_ha": round(overlap_area, 4),
                "severity": _get_overlap_severity(overlap_area),
            })

    return overlaps


def detect_transmission_conflicts(boundary_geometry: dict | str) -> list[dict[str, Any]]:
    wkt = _geometry_to_wkt(boundary_geometry)
    if not wkt:
        return []

    conflicts = []

    for corridor in STUB_TRANSMISSION_CORRIDORS:
        sql = text(f"""
            SELECT
                ST_Area(
                    ST_Transform(
                        ST_Intersection(
                            ST_Buffer(ST_GeomFromText(:line, 4326)::geography, :buffer_m)::geometry,
                            ST_GeomFromText(:boundary, 4326)
                        )::geography
                    )
                ) / 10000.0 AS overlap_area_ha
            WHERE ST_IsValid(ST_GeomFromText(:boundary, 4326))
              AND ST_Intersects(
                  ST_Buffer(ST_GeomFromText(:line, 4326)::geography, :buffer_m)::geometry,
                  ST_GeomFromText(:boundary, 4326)
              )
        """)

        from sqlalchemy import create_engine
        from app.config import get_settings
        settings = get_settings()
        engine = create_engine(settings.database_url)

        with engine.connect() as conn:
            result = conn.execute(sql, {
                "line": corridor["geometry"],
                "buffer_m": corridor["buffer_m"],
                "boundary": wkt,
            })
            row = result.fetchone()

            if row and row.overlap_area_ha and row.overlap_area_ha > 0:
                conflicts.append({
                    "conflict_type": "transmission_line_overlap",
                    "line_name": corridor["name"],
                    "voltage_kv": corridor["voltage_kv"],
                    "buffer_m": corridor["buffer_m"],
                    "overlap_area_ha": round(row.overlap_area_ha, 4),
                    "severity": _get_transmission_severity(corridor["voltage_kv"], row.overlap_area_ha),
                    "description": f"Proposal overlaps with {corridor['voltage_kv']}kV transmission corridor: {corridor['name']}",
                })

    return conflicts


def detect_protected_area_conflicts(boundary_geometry: dict | str) -> list[dict[str, Any]]:
    wkt = _geometry_to_wkt(boundary_geometry)
    if not wkt:
        return []

    conflicts = []

    from sqlalchemy import create_engine
    from app.config import get_settings
    settings = get_settings()
    engine = create_engine(settings.database_url)

    for area in STUB_PROTECTED_AREAS:
        sql = text("""
            SELECT
                ST_Area(
                    ST_Transform(
                        ST_Intersection(
                            ST_GeomFromText(:protected, 4326),
                            ST_GeomFromText(:boundary, 4326)
                        )::geography
                    )
                ) / 10000.0 AS overlap_area_ha,
                ST_Area(ST_Transform(ST_GeomFromText(:boundary, 4326)::geography)) / 10000.0 AS proposal_area_ha
            WHERE ST_IsValid(ST_GeomFromText(:boundary, 4326))
              AND ST_IsValid(ST_GeomFromText(:protected, 4326))
              AND ST_Intersects(
                  ST_GeomFromText(:protected, 4326),
                  ST_GeomFromText(:boundary, 4326)
              )
        """)

        with engine.connect() as conn:
            result = conn.execute(sql, {
                "protected": area["geometry"],
                "boundary": wkt,
            })
            row = result.fetchone()

            if row and row.overlap_area_ha and row.overlap_area_ha > 0:
                overlap_pct = 0
                if row.proposal_area_ha and row.proposal_area_ha > 0:
                    overlap_pct = (row.overlap_area_ha / row.proposal_area_ha) * 100

                conflicts.append({
                    "conflict_type": "protected_area_overlap",
                    "area_name": area["name"],
                    "protection_type": area["type"],
                    "protected_area_ha": area["area_ha"],
                    "overlap_area_ha": round(row.overlap_area_ha, 4),
                    "overlap_percentage": round(overlap_pct, 2),
                    "severity": _get_protected_area_severity(area["type"], overlap_pct),
                    "description": f"Proposal overlaps {overlap_pct:.1f}% with {area['type']}: {area['name']}",
                })

    return conflicts


def _get_overlap_severity(overlap_area_ha: float) -> str:
    if overlap_area_ha > 50:
        return "critical"
    elif overlap_area_ha > 20:
        return "high"
    elif overlap_area_ha > 5:
        return "medium"
    return "low"


def _get_transmission_severity(voltage_kv: int, overlap_area_ha: float) -> str:
    if voltage_kv >= 765:
        return "critical"
    elif voltage_kv >= 400 or overlap_area_ha > 10:
        return "high"
    elif voltage_kv >= 220 or overlap_area_ha > 5:
        return "medium"
    return "low"


def _get_protected_area_severity(protection_type: str, overlap_pct: float) -> str:
    high_protection = ["Tiger Reserve", "National Park"]
    medium_protection = ["Wildlife Sanctuary", "Biosphere Reserve"]

    if protection_type in high_protection:
        if overlap_pct > 10:
            return "critical"
        elif overlap_pct > 1:
            return "high"
        return "medium"
    elif protection_type in medium_protection:
        if overlap_pct > 20:
            return "high"
        elif overlap_pct > 5:
            return "medium"
        return "low"
    else:
        if overlap_pct > 30:
            return "high"
        elif overlap_pct > 10:
            return "medium"
        return "low"


def run_spatial_analysis(
    proposal_id: str,
    boundary_geometry: dict | str,
    db: Session,
) -> dict[str, Any]:
    proposal_overlaps = detect_proposal_overlaps(proposal_id, boundary_geometry, db)
    transmission_conflicts = detect_transmission_conflicts(boundary_geometry)
    protected_area_conflicts = detect_protected_area_conflicts(boundary_geometry)

    all_conflicts = proposal_overlaps + transmission_conflicts + protected_area_conflicts

    has_critical = any(c["severity"] == "critical" for c in all_conflicts)
    has_high = any(c["severity"] == "high" for c in all_conflicts)

    if has_critical:
        overall_severity = "critical"
    elif has_high:
        overall_severity = "high"
    elif all_conflicts:
        overall_severity = "medium"
    else:
        overall_severity = "none"

    total_overlap_area = sum(c.get("overlap_area_ha", 0) for c in all_conflicts)

    return {
        "proposal_id": proposal_id,
        "proposal_overlaps": proposal_overlaps,
        "transmission_conflicts": transmission_conflicts,
        "protected_area_conflicts": protected_area_conflicts,
        "all_conflicts": all_conflicts,
        "conflict_count": len(all_conflicts),
        "overall_severity": overall_severity,
        "total_overlap_area_ha": round(total_overlap_area, 4),
        "has_spatial_conflicts": len(all_conflicts) > 0,
    }
