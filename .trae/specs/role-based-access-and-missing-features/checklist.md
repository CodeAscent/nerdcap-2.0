# Checklist

## Role-Based UI

- [x] Developer role shows limited navigation (Dashboard, Proposals, New Proposal, Recommendations, API Status)
- [x] Officer role shows full navigation (Dashboard, Proposals, Recommendations, Predictions, Users, API Status)
- [x] Admin role shows all navigation including Users and Settings
- [x] Developer dashboard shows only their own proposals and quick actions
- [x] Officer dashboard shows all proposals, conflict alerts, officer scores, developer tracking
- [x] Admin dashboard shows system-wide metrics and user management options
- [x] Developer can only see their own proposals in the list
- [x] Officer can filter proposals by their assigned district
- [x] Decision buttons (Approve/Reject/Escalate) are hidden for developers
- [x] Developer can only access "Find Sites" in Recommendations
- [x] Officer and Admin can access all Recommendation tabs

## GIS Spatial Analysis

- [x] Spatial analysis service exists and is called during proposal analysis
- [x] PostGIS ST_Intersects detects overlaps with existing proposals
- [x] PostGIS ST_Intersects detects overlaps with forest zones (stub data)
- [x] PostGIS ST_Intersects detects overlaps with transmission corridors (stub data)
- [x] Conflict records include actual overlapping geometry
- [x] Conflict detector returns spatial conflicts in addition to council-parsed conflicts

## Satellite Imagery Analysis

- [x] satellite_analysis.py service exists
- [x] Vegetation density is calculated from boundary coordinates
- [x] Slope analysis is computed from elevation data
- [x] Water body proximity is calculated
- [x] Satellite characteristics score (0-10) is returned
- [x] Cadastral agent includes satellite metrics in findings

## Officer Responsiveness Score

- [x] Proposal model has response_time_hours field
- [x] officer_score.py service exists with weighted calculation
- [x] OfficerScore model stores computed scores
- [x] /api/dashboard/officer-scores endpoint returns officer performance data
- [x] Officer leaderboard component displays on officer/admin dashboard

## Developer Allocation Tracking

- [x] /api/dashboard/developer-tracking endpoint exists
- [x] Endpoint aggregates proposals by developer with stats
- [x] DeveloperTrackingTable component displays developer stats
- [x] Clicking developer shows their proposal history
- [x] Table displays in officer/admin dashboard

## Choropleth Map

- [x] AP district GeoJSON data is available in project
- [x] DistrictMap component renders choropleth map
- [x] Map uses color scale based on proposal density or MW
- [x] Hover tooltips show district statistics
- [x] Map displays in officer/admin dashboard

## Integration Tests

- [x] Full role-based flow works: developer login -> limited nav -> own proposals only
- [x] Full role-based flow works: officer login -> full nav -> decision buttons visible
- [x] Full role-based flow works: admin login -> all features accessible
- [x] GIS overlap detection correctly identifies conflicts with existing proposals
- [x] Satellite analysis returns valid metrics for test boundaries
