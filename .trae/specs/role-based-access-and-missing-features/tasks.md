# Tasks

## Phase 1: Role-Based UI Differentiation

- [x] Task 1: Implement role-based sidebar navigation
  - [x] SubTask 1.1: Create navigation configuration per role (developer, officer, admin)
  - [x] SubTask 1.2: Update Sidebar.tsx to filter nav items by role
  - [x] SubTask 1.3: Add role-specific icons and labels
  - [x] SubTask 1.4: Add Users and Settings links for admin role

- [x] Task 2: Create role-based dashboard variants
  - [x] SubTask 2.1: Extract common dashboard components (KPI cards, charts)
  - [x] SubTask 2.2: Create DeveloperDashboard with own proposals summary
  - [x] SubTask 2.3: Create OfficerDashboard with full statistics, alerts, officer scores
  - [x] SubTask 2.4: Create AdminDashboard with system-wide metrics
  - [x] SubTask 2.5: Update Dashboard.tsx to render correct variant based on role

- [x] Task 3: Implement role-based proposal filtering
  - [x] SubTask 3.1: Add developer_id filter to backend proposals list endpoint
  - [x] SubTask 3.2: Update frontend Proposals.tsx to pass role context
  - [x] SubTask 3.3: Hide decision buttons for developer role in ProposalDetail.tsx
  - [x] SubTask 3.4: Add district filter for officers based on their assigned district

- [x] Task 4: Restrict recommendations by role
  - [x] SubTask 4.1: Hide "Find Developers" and "Policy Insights" tabs for developers
  - [x] SubTask 4.2: Show all recommendation tabs for officers and admins

## Phase 2: GIS Spatial Analysis

- [x] Task 5: Implement PostGIS spatial overlap detection
  - [x] SubTask 5.1: Create spatial_analysis.py service with PostGIS query functions
  - [x] SubTask 5.2: Implement ST_Intersects query for proposal boundary overlaps
  - [x] SubTask 5.3: Add function to detect transmission line corridor overlaps
  - [x] SubTask 5.4: Add function to detect forest/protected area overlaps
  - [x] SubTask 5.5: Store conflict geometry in Conflict model

- [x] Task 6: Integrate spatial analysis into agent pipeline
  - [x] SubTask 6.1: Update orchestrator to call spatial_analysis before FTM Council
  - [x] SubTask 6.2: Pass spatial conflict results to FTM Council prompt
  - [x] SubTask 6.3: Update conflict_detector to use spatial results

## Phase 3: Satellite Imagery Analysis

- [x] Task 7: Implement satellite characteristic analysis
  - [x] SubTask 7.1: Create satellite_analysis.py service
  - [x] SubTask 7.2: Implement vegetation density calculation from boundary coordinates
  - [x] SubTask 7.3: Implement slope analysis from elevation data (simulated)
  - [x] SubTask 7.4: Implement water body proximity check
  - [x] SubTask 7.5: Return satellite_characteristics score (0-10)

- [x] Task 8: Integrate satellite analysis into Cadastral agent
  - [x] SubTask 8.1: Update cadastral agent to call satellite_analysis
  - [x] SubTask 8.2: Include satellite metrics in agent findings

## Phase 4: Officer Responsiveness Score

- [x] Task 9: Create officer responsiveness tracking
  - [x] SubTask 9.1: Add response_time_hours field to Proposal model
  - [x] SubTask 9.2: Create officer_score.py service
  - [x] SubTask 9.3: Implement score calculation with weights (response time 50%, data freshness 20%, escalation rate 20%, collaboration 10%)
  - [x] SubTask 9.4: Create OfficerScore model to store computed scores
  - [x] SubTask 9.5: Add API endpoint /api/dashboard/officer-scores

- [x] Task 10: Display officer scores on dashboard
  - [x] SubTask 10.1: Fetch officer scores in Dashboard component
  - [x] SubTask 10.2: Create OfficerLeaderboard component
  - [x] SubTask 10.3: Display in OfficerDashboard and AdminDashboard

## Phase 5: Developer Allocation Tracking

- [x] Task 11: Implement developer tracking backend
  - [x] SubTask 11.1: Add /api/dashboard/developer-tracking endpoint
  - [x] SubTask 11.2: Aggregate proposals by developer with stats (approved MW, counts, avg trust)
  - [x] SubTask 11.3: Sort by total approved MW descending

- [x] Task 12: Display developer tracking on dashboard
  - [x] SubTask 12.1: Create DeveloperTrackingTable component
  - [x] SubTask 12.2: Show developer name, company, approved MW, proposal counts, avg trust
  - [x] SubTask 12.3: Add click-through to developer's proposals
  - [x] SubTask 12.4: Display in OfficerDashboard and AdminDashboard

## Phase 6: Choropleth Map

- [x] Task 13: Implement AP district choropleth map
  - [x] SubTask 13.1: Add GeoJSON for Andhra Pradesh 26 districts
  - [x] SubTask 13.2: Install react-simple-maps or similar library
  - [x] SubTask 13.3: Create DistrictMap component with color scale
  - [x] SubTask 13.4: Bind district data from /api/dashboard/district-map
  - [x] SubTask 13.5: Add hover tooltips with district statistics

- [x] Task 14: Integrate map into dashboard
  - [x] SubTask 14.1: Replace or augment district bar chart with choropleth map
  - [x] SubTask 14.2: Ensure responsive sizing

## Phase 7: Testing and Validation

- [x] Task 15: Verify role-based access control
  - [x] SubTask 15.1: Test developer can only see own proposals
  - [x] SubTask 15.2: Test officer can see all proposals and make decisions
  - [x] SubTask 15.3: Test admin has full access
  - [x] SubTask 15.4: Verify navigation changes per role

- [x] Task 16: Verify GIS and satellite features
  - [x] SubTask 16.1: Test spatial overlap detection returns conflicts
  - [x] SubTask 16.2: Verify conflict geometry is stored
  - [x] SubTask 16.3: Test satellite analysis returns valid scores

---

# Task Dependencies
- [Task 2] depends on [Task 1] (need role context for dashboards)
- [Task 5] depends on nothing (can start parallel)
- [Task 6] depends on [Task 5] (spatial analysis needed for integration)
- [Task 7] depends on nothing (can start parallel)
- [Task 8] depends on [Task 7] (satellite analysis needed for integration)
- [Task 10] depends on [Task 9] (backend API needed)
- [Task 12] depends on [Task 11] (backend API needed)
- [Task 14] depends on [Task 13] (map component needed)
- [Task 15] depends on [Task 1, 2, 3, 4] (all role-based features)
- [Task 16] depends on [Task 5, 6, 7, 8] (all GIS/satellite features)

# Parallelizable Work
The following can be done in parallel:
- Phase 1 (Tasks 1-4) - Role-based UI
- Phase 2 (Tasks 5-6) - GIS Spatial Analysis
- Phase 3 (Tasks 7-8) - Satellite Analysis
- Phase 4 (Tasks 9-10) - Officer Scores
- Phase 5 (Tasks 11-12) - Developer Tracking
- Phase 6 (Tasks 13-14) - Choropleth Map
