# Checklist

## Role-Based UI

- [ ] Developer role shows limited navigation (Dashboard, Proposals, New Proposal, Recommendations, API Status)
- [ ] Officer role shows full navigation (Dashboard, Proposals, Recommendations, Predictions, Users, API Status)
- [ ] Admin role shows all navigation including Users and Settings
- [ ] Developer dashboard shows only their own proposals and quick actions
- [ ] Officer dashboard shows all proposals, conflict alerts, officer scores, developer tracking
- [ ] Admin dashboard shows system-wide metrics and user management options
- [ ] Developer can only see their own proposals in the list
- [ ] Officer can filter proposals by their assigned district
- [ ] Decision buttons (Approve/Reject/Escalate) are hidden for developers
- [ ] Developer can only access "Find Sites" in Recommendations
- [ ] Officer and Admin can access all Recommendation tabs

## GIS Spatial Analysis

- [ ] Spatial analysis service exists and is called during proposal analysis
- [ ] PostGIS ST_Intersects detects overlaps with existing proposals
- [ ] PostGIS ST_Intersects detects overlaps with forest zones (stub data)
- [ ] PostGIS ST_Intersects detects overlaps with transmission corridors (stub data)
- [ ] Conflict records include actual overlapping geometry
- [ ] Conflict detector returns spatial conflicts in addition to council-parsed conflicts

## Satellite Imagery Analysis

- [ ] satellite_analysis.py service exists
- [ ] Vegetation density is calculated from boundary coordinates
- [ ] Slope analysis is computed from elevation data
- [ ] Water body proximity is calculated
- [ ] Satellite characteristics score (0-10) is returned
- [ ] Cadastral agent includes satellite metrics in findings

## Officer Responsiveness Score

- [ ] Proposal model has response_time_hours field
- [ ] officer_score.py service exists with weighted calculation
- [ ] OfficerScore model stores computed scores
- [ ] /api/dashboard/officer-scores endpoint returns officer performance data
- [ ] Officer leaderboard component displays on officer/admin dashboard

## Developer Allocation Tracking

- [ ] /api/dashboard/developer-tracking endpoint exists
- [ ] Endpoint aggregates proposals by developer with stats
- [ ] DeveloperTrackingTable component displays developer stats
- [ ] Clicking developer shows their proposal history
- [ ] Table displays in officer/admin dashboard

## Choropleth Map

- [ ] AP district GeoJSON data is available in project
- [ ] DistrictMap component renders choropleth map
- [ ] Map uses color scale based on proposal density or MW
- [ ] Hover tooltips show district statistics
- [ ] Map displays in officer/admin dashboard

## Integration Tests

- [ ] Full role-based flow works: developer login -> limited nav -> own proposals only
- [ ] Full role-based flow works: officer login -> full nav -> decision buttons visible
- [ ] Full role-based flow works: admin login -> all features accessible
- [ ] GIS overlap detection correctly identifies conflicts with existing proposals
- [ ] Satellite analysis returns valid metrics for test boundaries
