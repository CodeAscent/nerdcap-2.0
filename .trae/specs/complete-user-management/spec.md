# Complete User Management Flow Spec

## Why
The user management page currently only displays a read-only table of users. Admins cannot create, edit, or deactivate users through the UI, despite the backend APIs being fully implemented. This forces admins to use API tools or direct database access for user administration.

## What Changes
- Add User modal with form for creating new users
- Edit User modal for modifying existing users
- Deactivate/Reactivate user functionality
- Actions column in the users table
- Form validation and error handling
- Success/error toast notifications

## Impact
- Affected specs: User Management, Authentication
- Affected code: 
  - Frontend: Users.tsx, api/client.ts

---

## ADDED Requirements

### Requirement: Create User Modal
The system SHALL provide a modal dialog for creating new users.

#### Scenario: Admin creates new user
- **WHEN** admin clicks "Add User" button
- **THEN** a modal SHALL appear with form fields:
  - Email (required, valid email format)
  - Password (required, min 6 characters)
  - Full Name (optional)
  - Role (dropdown: developer, officer, admin, default: developer)
  - Department (optional, text)
  - District (optional, text)
- **AND** "Create" button SHALL be disabled until required fields are valid
- **AND** clicking "Create" SHALL call POST /api/users
- **AND** on success, modal SHALL close and user list SHALL refresh
- **AND** success toast SHALL display "User created successfully"

#### Scenario: Email already exists
- **WHEN** admin submits form with existing email
- **THEN** error toast SHALL display "Email already registered"

### Requirement: Edit User Modal
The system SHALL provide a modal dialog for editing existing users.

#### Scenario: Admin edits user
- **WHEN** admin clicks "Edit" button on a user row
- **THEN** a modal SHALL appear pre-filled with user data
- **AND** form SHALL include fields:
  - Full Name (optional)
  - Role (dropdown)
  - Department (optional)
  - District (optional)
- **AND** Email and Password SHALL NOT be editable
- **AND** clicking "Save" SHALL call PATCH /api/users/{user_id}
- **AND** on success, modal SHALL close and user list SHALL refresh
- **AND** success toast SHALL display "User updated successfully"

### Requirement: Deactivate/Reactivate User
The system SHALL allow admins to toggle user active status.

#### Scenario: Admin deactivates active user
- **WHEN** admin clicks "Deactivate" button on an active user row
- **THEN** a confirmation dialog SHALL appear
- **AND** confirming SHALL call DELETE /api/users/{user_id}
- **AND** user's status SHALL change to "Inactive"
- **AND** success toast SHALL display "User deactivated"

#### Scenario: Admin reactivates inactive user
- **WHEN** admin clicks "Reactivate" button on an inactive user row
- **THEN** SHALL call PATCH /api/users/{user_id} with is_active: true
- **AND** user's status SHALL change to "Active"
- **AND** success toast SHALL display "User reactivated"

### Requirement: Actions Column
The users table SHALL include an Actions column.

#### Scenario: Viewing actions
- **WHEN** admin views the users table
- **THEN** an "Actions" column SHALL be visible
- **AND** each row SHALL have Edit and Deactivate/Reactivate buttons
- **AND** buttons SHALL use appropriate icons (Edit2, UserX/UserCheck)

### Requirement: Form Validation
The system SHALL validate user form inputs.

#### Scenario: Invalid email
- **WHEN** admin enters invalid email format
- **THEN** email field SHALL show error state
- **AND** "Create" button SHALL be disabled

#### Scenario: Short password
- **WHEN** admin enters password less than 6 characters
- **THEN** password field SHALL show error state with message "Password must be at least 6 characters"
- **AND** "Create" button SHALL be disabled

### Requirement: Loading States
The system SHALL show loading states during operations.

#### Scenario: Creating user
- **WHEN** admin submits create form
- **THEN** "Create" button SHALL show spinner and be disabled
- **AND** form fields SHALL be disabled

#### Scenario: Loading users
- **WHEN** users data is being fetched
- **THEN** skeleton rows SHALL display instead of table

---

## MODIFIED Requirements

### Requirement: Users Table
The users table SHALL include an Actions column with Edit and Toggle Status buttons.

**Previous**: Table had columns: User, Role, Department, District, Status
**Modified**: Table has columns: User, Role, Department, District, Status, Actions

---

## REMOVED Requirements

None - all existing functionality is retained.
