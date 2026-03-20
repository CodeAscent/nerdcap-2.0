# Tasks

## Phase 1: Role-Based UI Differentiation

- [ ] Task 1: Implement role-based sidebar navigation
  - [ ] SubTask 1.1: Create navigation configuration per role (developer, officer, admin)
  - [ ] SubTask 1.2: Update Sidebar.tsx to filter nav items by role
  - [ ] SubTask 1.3: Add role-specific icons and labels
  - [ ] SubTask 1.4: Add Users and Settings links for admin role

- [ ] Task 2: Create role-based dashboard variants
  - [ ] SubTask 2.1: Extract common dashboard components (KPI cards, charts)
  - [ ] SubTask 2.2: Create DeveloperDashboard with own proposals summary
  - [ ] SubTask 2.3: Create OfficerDashboard with full statistics, alerts, officer scores
  - [ ] SubTask 2.4: Create AdminDashboard with system-wide metrics
  - [ ] SubTask 2.5: Update Dashboard.tsx to render correct variant based on role

- [ ] Task 3: Implement role-based proposal filtering
  - [ ] SubTask 3.1: Add developer_id filter to backend proposals list endpoint
  - [ ] SubTask 3.2: Update frontend Proposals.tsx to pass role context
  - [ ] SubTask 3.3: Hide decision buttons for developer role in ProposalDetail.tsx
  - [ ] SubTask 3.4: Add district filter for officers based on their assigned district

- [ ] Task 4: Restrict recommendations by role
  - [ ] SubTask 4.1: Hide "Find Developers" and "Policy Insights" tabs for developers
  - [ ] SubTask 4.2: Show all recommendation tabs for officers and admins

## Phase 2: GIS Spatial Analysis

- [ ] Task 5: Implement PostGIS spatial overlap detection
  - [ ] SubTask 5.1: Create spatial_analysis.py service with PostGIS query functions
  - [ ] SubTask 5.2: Implement ST_Intersects query for proposal boundary overlaps
  - [ ] SubTask 5.3: Add function to detect transmission line corridor overlaps
  - [ ] SubTask 5.4: Add function to detect forest/protected area overlaps
  - [ ] SubTask 5.5: Store conflict geometry in Conflict model

- [ ] Task 6: Integrate spatial analysis into agent pipeline
  - [ ] SubTask 6.1: Update orchestrator to call spatial_analysis before FTM Council
  - [ ] SubTask 6.2: Pass spatial conflict results to FTM Council prompt
  - [ ] SubTask 6.3: Update conflict_detector to use spatial results

## Phase 3: Satellite Imagery Analysis

- [ ] Task 7: Implement satellite characteristic analysis
  - [ ] SubTask 7.1: Create satellite_analysis.py service
  - [ ] SubTask 7.2: Implement vegetation density calculation from boundary coordinates
  - [ ] SubTask 7.3: Implement slope analysis from elevation data (simulated)
  - [ ] SubTask 7.4: Implement water body proximity check
  - [ ] SubTask 7.5: Return satellite_characteristics score (0-10)

- [ ] Task 8: Integrate satellite analysis into Cadastral agent
  - [ ] SubTask 8.1: Update cadastral agent to call satellite_analysis
  - [ ] SubTask 8.2: Include satellite metrics in agent findings

## Phase 4: Officer Responsiveness Score

- [ ] Task 9: Create officer responsiveness tracking
  - [ ] SubTask 9.1: Add response_time_hours field to Proposal model
  - [ ] SubTask 9.2: Create officer_score.py service
  - [ ] SubTask 9.3: Implement score calculation with weights (response time 50%, data freshness 20%, escalation rate 20%, collaboration 10%)
  - [ ] SubTask 9.4: Create OfficerScore model to store computed scores
  - [ ] SubTask 9.5: Add API endpoint /api/dashboard/officer-scores

- [ ] Task 10: Display officer scores on dashboard
  - [ ] SubTask 10.1: Fetch officer scores in Dashboard component
  - [ ] SubTask 10.2: Create OfficerLeaderboard component
  - [ ] SubTask 10.3: Display in OfficerDashboard and AdminDashboard

## Phase 5: Developer Allocation Tracking

- [ ] Task 11: Implement developer tracking backend
  - [ ] SubTask 11.1: Add /api/dashboard/developer-tracking endpoint
  - [ ] SubTask 11.2: Aggregate proposals by developer with stats (approved MW, counts, avg trust)
  - [ ] SubTask 11.3: Sort by total approved MW descending

- [ ] Task 12: Display developer tracking on dashboard
  - [ ] SubTask 12.1: Create DeveloperTrackingTable component
  - [ ] SubTask 12.2: Show developer name, company, approved MW, proposal counts, avg trust
  - [ ] SubTask 12.3: Add click-through to developer's proposals
  - [ ] SubTask 12.4: Display in OfficerDashboard and AdminDashboard

## Phase 6: Choropleth Map

- [ ] Task 13: Implement AP district choropleth map
  - [ ] SubTask 13.1: Add GeoJSON for Andhra Pradesh 26 districts
  - [ ] SubTask 13.2: Install react-simple-maps or similar library
  - [ ] SubTask 13.3: Create DistrictMap component with color scale
  - [ ] SubTask 13.4: Bind district data from /api/dashboard/district-map
  - [ ] SubTask 13.5: Add hover tooltips with district statistics

- [ ] Task 14: Integrate map into dashboard
  - [ ] SubTask 14.1: Replace or augment district bar chart with choropleth map
  - [ ] SubTask 14.2: Ensure responsive sizing

## Phase 7: Testing and Validation

- [ ] Task 15: Verify role-based access control
  - [ ] SubTask 15.1: Test developer can only see own proposals
  - [ ] SubTask 15.2: Test officer can see all proposals and make decisions
  - [ ] SubTask 15.3: Test admin has full access
  - [ ] SubTask 15.4: Verify navigation changes per role

- [ ] Task 16: Verify GIS and satellite features
  - [ ] SubTask 16.1: Test spatial overlap detection returns conflicts
  - [ ] SubTask 16.2: Verify conflict geometry is stored
  - [ ] SubTask 16.3: Test satellite analysis returns valid scores

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
