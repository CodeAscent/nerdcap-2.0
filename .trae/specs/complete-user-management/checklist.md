# Checklist

## Create User Flow
- [x] "Add User" button opens modal when clicked
- [x] Modal shows form with Email, Password, Full Name, Role, Department, District fields
- [x] Role dropdown has options: developer, officer, admin
- [x] Form validates email format
- [x] Form requires password minimum 6 characters
- [x] Submitting valid form calls POST /api/users
- [x] Success closes modal and refreshes user list
- [x] Success shows toast notification "User created successfully"
- [x] Duplicate email shows error toast "Email already registered"

## Edit User Flow
- [x] Edit button exists in Actions column for each user row
- [x] Clicking Edit opens modal pre-filled with user data
- [x] Email field is disabled/not shown in edit mode
- [x] Password field is disabled/not shown in edit mode
- [x] Submitting valid form calls PATCH /api/users/{user_id}
- [x] Success closes modal and refreshes user list
- [x] Success shows toast notification "User updated successfully"

## Deactivate/Reactivate Flow
- [x] Actions column shows Deactivate button for active users
- [x] Actions column shows Reactivate button for inactive users
- [x] Clicking Deactivate shows confirmation dialog
- [x] Confirming deactivation calls DELETE /api/users/{user_id}
- [x] User status changes to Inactive after deactivation
- [x] Success shows toast notification "User deactivated"
- [x] Clicking Reactivate calls PATCH /api/users/{user_id} with is_active: true
- [x] User status changes to Active after reactivation
- [x] Success shows toast notification "User reactivated"

## UI/UX
- [x] Loading spinner shows on buttons during mutations
- [x] Table refreshes after any successful mutation
- [x] Actions column is only visible to admin role
- [x] Officer role can view users but not edit (hide Actions column)
