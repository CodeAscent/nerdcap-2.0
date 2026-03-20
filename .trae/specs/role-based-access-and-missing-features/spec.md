# Role-Based Access Control & Missing Features Spec

## Why
The system currently treats all user roles (admin, officer, developer) identically with the same UI and features. Additionally, several requirements from the NREDCAP specification document are not implemented, including GIS spatial analysis, satellite imagery integration, officer responsiveness scoring, developer tracking dashboard, and choropleth map visualization.

## What Changes
- **Role-based UI differentiation** - Different navigation, dashboards, and capabilities per role
- **GIS Spatial Analysis** - Actual PostGIS queries for overlap detection
- **Satellite imagery integration** - Vegetation/slope analysis from imagery data
- **Officer/Department Responsiveness Score** - Track and display department performance
- **Developer-wise allocation tracking** - Dashboard section for developer allocations
- **Choropleth map visualization** - Visual district map on dashboard
- **BREAKING**: Sidebar navigation will change based on user role

## Impact
- Affected specs: User authentication, Dashboard, Proposals, Recommendations
- Affected code: 
  - Frontend: Sidebar.tsx, Dashboard.tsx, App.tsx, all page components
  - Backend: routers/dashboard.py, routers/proposals.py, services/conflict_detector.py

---

## ADDED Requirements

### Requirement: Role-Based Navigation
The system SHALL provide different navigation menus based on user role.

#### Scenario: Developer Navigation
- **WHEN** a user with role "developer" logs in
- **THEN** they SHALL see: Dashboard, Proposals (own only), New Proposal, Recommendations (sites only), API Status

#### Scenario: Officer Navigation
- **WHEN** a user with role "officer" logs in
- **THEN** they SHALL see: Dashboard, Proposals (all), Recommendations (all), Predictions, Users (view), API Status

#### Scenario: Admin Navigation
- **WHEN** a user with role "admin" logs in
- **THEN** they SHALL see: Dashboard, Proposals (all), New Proposal, Recommendations (all), Predictions, Users (manage), System Settings, API Status

---

### Requirement: Role-Based Dashboard Content
The system SHALL display different dashboard content based on user role.

#### Scenario: Developer Dashboard
- **WHEN** a developer views the dashboard
- **THEN** they SHALL see:
  - Their own proposal count and status breakdown
  - Their approved MW capacity
  - Quick actions: Submit New Proposal, View Recommendations

#### Scenario: Officer Dashboard
- **WHEN** an officer views the dashboard
- **THEN** they SHALL see:
  - All proposals pending review
  - Conflict alerts requiring attention
  - District breakdown chart
  - Officer responsiveness scores
  - Developer-wise allocation tracking table

#### Scenario: Admin Dashboard
- **WHEN** an admin views the dashboard
- **THEN** they SHALL see:
  - Full system statistics
  - User management summary
  - System health metrics
  - All officer dashboards combined

---

### Requirement: Role-Based Proposal Access
The system SHALL restrict proposal access based on user role.

#### Scenario: Developer Proposal List
- **WHEN** a developer requests the proposals list
- **THEN** they SHALL only see proposals where they are the submitter/developer

#### Scenario: Officer Proposal Access
- **WHEN** an officer requests proposals
- **THEN** they SHALL see all proposals
- **AND** they SHALL be able to filter by district matching their assignment

#### Scenario: Decision Authority
- **WHEN** a proposal is in "analyzed" or "under_review" status
- **THEN** only officers and admins SHALL see decision buttons (Approve/Reject/Escalate)

---

### Requirement: GIS Spatial Analysis
The system SHALL perform actual GIS spatial queries for conflict detection.

#### Scenario: Boundary Overlap Detection
- **WHEN** a proposal is analyzed
- **THEN** the system SHALL use PostGIS ST_Intersects to detect overlaps with:
  - Existing approved proposals
  - Forest boundaries (stub data)
  - Protected areas (stub data)
  - Transmission line corridors (stub data)

#### Scenario: Conflict Geometry Storage
- **WHEN** a conflict is detected
- **THEN** the conflict record SHALL include the actual overlapping geometry

---

### Requirement: Satellite Imagery Analysis
The system SHALL analyze satellite-derived characteristics for land parcels.

#### Scenario: Vegetation Analysis
- **WHEN** a proposal boundary is submitted
- **THEN** the system SHALL compute:
  - Vegetation density percentage (simulated from NDVI-like calculation)
  - Slope analysis from elevation data
  - Water body proximity

#### Scenario: Satellite Score Integration
- **WHEN** the FTM Council deliberates
- **THEN** the satellite_characteristics score SHALL be derived from actual computed values

---

### Requirement: Officer/Department Responsiveness Score
The system SHALL track and display officer/department performance metrics.

#### Scenario: Response Time Tracking
- **WHEN** a proposal requires officer decision
- **THEN** the system SHALL track time from "analyzed" to final decision

#### Scenario: Responsiveness Score Calculation
- **WHEN** viewing officer performance
- **THEN** the score SHALL be computed from:
  - Average response time (50% weight)
  - Data freshness score (20% weight)
  - Escalation resolution rate (20% weight)
  - Cross-department collaboration index (10% weight)

#### Scenario: Dashboard Display
- **WHEN** an officer or admin views the dashboard
- **THEN** they SHALL see a responsiveness leaderboard

---

### Requirement: Developer-wise Allocation Tracking
The system SHALL provide developer allocation tracking on the dashboard.

#### Scenario: Developer Tracking Table
- **WHEN** an officer or admin views the dashboard
- **THEN** they SHALL see a table showing:
  - Developer name
  - Total approved MW
  - Number of proposals (approved/pending/rejected)
  - Average trust score of their proposals

#### Scenario: Developer Detail View
- **WHEN** clicking on a developer in the tracking table
- **THEN** the system SHALL show their proposal history

---

### Requirement: Choropleth Map Visualization
The system SHALL display a choropleth map of Andhra Pradesh districts.

#### Scenario: District Map Rendering
- **WHEN** the dashboard loads
- **THEN** a map of AP districts SHALL be rendered
- **AND** districts SHALL be color-coded by proposal density or approved MW

#### Scenario: Map Interactivity
- **WHEN** hovering over a district
- **THEN** a tooltip SHALL show district statistics

---

### Requirement: Recommendations Role Restriction
The system SHALL restrict recommendation features based on role.

#### Scenario: Developer Recommendations
- **WHEN** a developer accesses Recommendations
- **THEN** they SHALL only see "Find Sites" tab
- **AND** "Find Developers" and "Policy Insights" SHALL be hidden

#### Scenario: Officer Recommendations
- **WHEN** an officer accesses Recommendations
- **THEN** they SHALL see all tabs (Sites, Developers, Policy Insights)

---

## MODIFIED Requirements

### Requirement: Proposal List API
The proposal list endpoint SHALL support role-based filtering.

**Previous**: Returns all proposals for authenticated users
**Modified**: 
- Developers: Returns only their own proposals
- Officers/Admins: Returns all proposals with optional district filter

### Requirement: Dashboard Summary API
The dashboard summary SHALL include role-specific metrics.

**Previous**: Returns aggregate statistics
**Modified**:
- Add `developer_tracking` array for officer/admin roles
- Add `officer_scores` array for officer/admin roles
- Add `my_proposals` summary for developer role

---

## REMOVED Requirements

None - all existing features are retained with role-based access.
