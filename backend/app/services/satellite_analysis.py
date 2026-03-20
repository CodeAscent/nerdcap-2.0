"""
Satellite Imagery Analysis Service
Simulates satellite-derived characteristics for land parcels in Andhra Pradesh.
In production, replace with actual satellite imagery APIs (Sentinel-2, Landsat, etc.)
"""
import math
import hashlib
from typing import Any


ANDHRA_PRADESH_WATER_BODIES = [
    {"name": "Bay of Bengal Coastline", "type": "coastal", "lat": 15.5, "lon": 80.5, "is_coastline": True},
    {"name": "Krishna River", "type": "river", "lat": 16.2, "lon": 80.6, "is_coastline": False},
    {"name": "Godavari River", "type": "river", "lat": 16.9, "lon": 81.8, "is_coastline": False},
    {"name": "Penna River", "type": "river", "lat": 14.4, "lon": 79.8, "is_coastline": False},
    {"name": "Tungabhadra River", "type": "river", "lat": 15.8, "lon": 78.0, "is_coastline": False},
    {"name": "Nagarjuna Sagar Reservoir", "type": "reservoir", "lat": 16.5, "lon": 79.3, "is_coastline": False},
    {"name": "Srisailam Reservoir", "type": "reservoir", "lat": 16.1, "lon": 78.9, "is_coastline": False},
    {"name": "Pulicat Lake", "type": "lake", "lat": 13.6, "lon": 80.2, "is_coastline": False},
    {"name": "Kolleru Lake", "type": "lake", "lat": 16.5, "lon": 81.2, "is_coastline": False},
]


def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _deterministic_hash(*args) -> float:
    data = "|".join(str(arg) for arg in args)
    hash_digest = hashlib.sha256(data.encode()).hexdigest()
    return int(hash_digest[:8], 16) / 0xFFFFFFFF


def compute_centroid(geometry_geojson: dict[str, Any]) -> tuple[float, float]:
    coords = geometry_geojson.get("coordinates", [])
    geom_type = geometry_geojson.get("type", "").lower()

    if geom_type == "polygon" and coords:
        exterior_ring = coords[0] if coords else []
        if not exterior_ring:
            return 16.0, 80.0
        lon_sum = sum(pt[0] for pt in exterior_ring)
        lat_sum = sum(pt[1] for pt in exterior_ring)
        n = len(exterior_ring)
        return lat_sum / n, lon_sum / n

    elif geom_type == "multipolygon" and coords:
        all_lons = []
        all_lats = []
        for polygon in coords:
            if polygon and polygon[0]:
                for pt in polygon[0]:
                    all_lons.append(pt[0])
                    all_lats.append(pt[1])
        if all_lons and all_lats:
            return sum(all_lats) / len(all_lats), sum(all_lons) / len(all_lons)

    return 16.0, 80.0


def simulate_ndvi(centroid: tuple[float, float]) -> dict[str, Any]:
    lat, lon = centroid
    seed_value = _deterministic_hash(lat, lon, "ndvi")
    base_vegetation = 35.0

    coastal_boost = max(0, (81.0 - abs(lon - 81.0)) * 2)
    latitude_effect = (lat - 12.0) * 1.5
    variation = seed_value * 40.0
    vegetation_pct = base_vegetation + coastal_boost + latitude_effect + variation
    vegetation_pct = max(0, min(100, vegetation_pct))

    if vegetation_pct > 70:
        category = "dense_forest"
    elif vegetation_pct > 50:
        category = "moderate_vegetation"
    elif vegetation_pct > 30:
        category = "sparse_vegetation"
    elif vegetation_pct > 15:
        category = "scrubland"
    else:
        category = "barren"

    return {
        "ndvi_percentage": round(vegetation_pct, 2),
        "vegetation_category": category,
        "suitability_for_solar": "high" if vegetation_pct < 30 else "medium" if vegetation_pct < 50 else "low",
    }


def simulate_slope_analysis(geometry_geojson: dict[str, Any]) -> dict[str, Any]:
    coords = geometry_geojson.get("coordinates", [])
    geom_type = geometry_geojson.get("type", "").lower()

    if geom_type == "polygon" and coords and coords[0]:
        points = coords[0]
    elif geom_type == "multipolygon" and coords and coords[0] and coords[0][0]:
        points = coords[0][0]
    else:
        points = []

    if len(points) < 2:
        return {
            "average_slope_degrees": 5.0,
            "slope_percentage": 8.75,
            "terrain_type": "flat",
            "suitability_for_construction": "excellent",
        }

    lon_values = [pt[0] for pt in points]
    lat_values = [pt[1] for pt in points]
    lon_variance = sum((x - sum(lon_values) / len(lon_values)) ** 2 for x in lon_values) / len(lon_values)
    lat_variance = sum((y - sum(lat_values) / len(lat_values)) ** 2 for y in lat_values) / len(lat_values)
    terrain_roughness = (lon_variance + lat_variance) * 10000

    centroid = compute_centroid(geometry_geojson)
    seed_value = _deterministic_hash(centroid[0], centroid[1], "slope")
    base_slope = 5.0
    roughness_contribution = min(terrain_roughness * 0.1, 25.0)
    random_contribution = seed_value * 15.0
    avg_slope = base_slope + roughness_contribution + random_contribution
    avg_slope = max(0, min(45, avg_slope))

    if avg_slope < 5:
        terrain_type = "flat"
        suitability = "excellent"
    elif avg_slope < 15:
        terrain_type = "rolling"
        suitability = "good"
    elif avg_slope < 25:
        terrain_type = "hilly"
        suitability = "moderate"
    else:
        terrain_type = "steep"
        suitability = "poor"

    slope_pct = math.tan(math.radians(avg_slope)) * 100

    return {
        "average_slope_degrees": round(avg_slope, 2),
        "slope_percentage": round(slope_pct, 2),
        "terrain_type": terrain_type,
        "suitability_for_construction": suitability,
    }


def compute_water_body_proximity(geometry_geojson: dict[str, Any]) -> dict[str, Any]:
    centroid = compute_centroid(geometry_geojson)
    lat, lon = centroid

    min_distance = float("inf")
    nearest_water_body = None
    nearest_type = None
    is_coastal = False

    for water_body in ANDHRA_PRADESH_WATER_BODIES:
        distance = _haversine_distance(lat, lon, water_body["lat"], water_body["lon"])
        if distance < min_distance:
            min_distance = distance
            nearest_water_body = water_body["name"]
            nearest_type = water_body["type"]
            is_coastal = water_body.get("is_coastline", False)

    proximity_score = max(0, 10 - (min_distance / 20))
    if is_coastal and min_distance < 50:
        proximity_score = min(10, proximity_score + 2)

    if min_distance < 5:
        zone = "immediate_vicinity"
        risk_level = "high"
    elif min_distance < 15:
        zone = "nearby"
        risk_level = "moderate"
    elif min_distance < 50:
        zone = "regional"
        risk_level = "low"
    else:
        zone = "distant"
        risk_level = "minimal"

    return {
        "nearest_water_body": nearest_water_body,
        "water_body_type": nearest_type,
        "distance_km": round(min_distance, 2),
        "water_proximity_score": round(proximity_score, 2),
        "proximity_zone": zone,
        "flood_risk_level": risk_level,
        "is_coastal_area": is_coastal and min_distance < 100,
    }


def analyze_satellite_characteristics(geometry_geojson: dict[str, Any]) -> dict[str, Any]:
    centroid = compute_centroid(geometry_geojson)
    ndvi_result = simulate_ndvi(centroid)
    slope_result = simulate_slope_analysis(geometry_geojson)
    water_result = compute_water_body_proximity(geometry_geojson)

    vegetation_score = 10 - (ndvi_result["ndvi_percentage"] / 10)
    vegetation_score = max(0, min(10, vegetation_score))

    slope_degrees = slope_result["average_slope_degrees"]
    slope_score = 10 - (slope_degrees / 4.5)
    slope_score = max(0, min(10, slope_score))

    water_distance = water_result["distance_km"]
    water_score = min(10, water_distance / 10)
    if water_result.get("is_coastal_area", False) and water_distance < 30:
        water_score = max(0, water_score - 3)

    vegetation_weight = 0.40
    slope_weight = 0.30
    water_weight = 0.30

    satellite_score = (
        vegetation_score * vegetation_weight
        + slope_score * slope_weight
        + water_score * water_weight
    )
    satellite_score = max(0, min(10, satellite_score))

    if satellite_score >= 7:
        overall_suitability = "excellent"
    elif satellite_score >= 5:
        overall_suitability = "good"
    elif satellite_score >= 3:
        overall_suitability = "moderate"
    else:
        overall_suitability = "poor"

    return {
        "centroid": {
            "latitude": round(centroid[0], 6),
            "longitude": round(centroid[1], 6),
        },
        "vegetation_analysis": ndvi_result,
        "slope_analysis": slope_result,
        "water_proximity": water_result,
        "satellite_characteristics_score": round(satellite_score, 2),
        "overall_site_suitability": overall_suitability,
        "score_breakdown": {
            "vegetation_contribution": round(vegetation_score * vegetation_weight, 2),
            "slope_contribution": round(slope_score * slope_weight, 2),
            "water_proximity_contribution": round(water_score * water_weight, 2),
        },
        "analysis_source": "Satellite Imagery Analysis (Simulated)",
        "is_live": False,
    }
