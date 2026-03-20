# Tasks

## Phase 1: Create Modal Components

- [x] Task 1: Create UserFormModal component
  - [x] SubTask 1.1: Create /frontend/src/components/UserFormModal.tsx with form fields (email, password, full_name, role, department, district)
  - [x] SubTask 1.2: Add form validation using react-hook-form or controlled state
  - [x] SubTask 1.3: Support both create mode (all fields) and edit mode (exclude email/password)
  - [x] SubTask 1.4: Add proper TypeScript interfaces for props (isOpen, onClose, mode, userData?, onSuccess)

## Phase 2: Implement Create User Flow

- [x] Task 2: Add create user functionality to Users.tsx
  - [x] SubTask 2.1: Add useState for isCreateModalOpen
  - [x] SubTask 2.2: Connect "Add User" button to open modal
  - [x] SubTask 2.3: Add mutation using @tanstack/react-query for POST /api/users
  - [x] SubTask 2.4: On success, close modal, invalidate users query, show toast

## Phase 3: Implement Edit User Flow

- [x] Task 3: Add edit user functionality to Users.tsx
  - [x] SubTask 3.1: Add useState for editingUser (null when closed, user object when editing)
  - [x] SubTask 3.2: Add "Edit" button with icon in Actions column
  - [x] SubTask 3.3: Add mutation for PATCH /api/users/{user_id}
  - [x] SubTask 3.4: On success, close modal, invalidate users query, show toast

## Phase 4: Implement Deactivate/Reactivate Flow

- [x] Task 4: Add user status toggle functionality
  - [x] SubTask 4.1: Add confirmation dialog for deactivate action (use window.confirm or custom dialog)
  - [x] SubTask 4.2: Add mutation for DELETE /api/users/{user_id} (deactivate)
  - [x] SubTask 4.3: Add mutation for PATCH /api/users/{user_id} with is_active: true (reactivate)
  - [x] SubTask 4.4: Add Deactivate/Reactivate button in Actions column with appropriate icon
  - [x] SubTask 4.5: Show success toast on status change

## Phase 5: Add Actions Column and Polish

- [x] Task 5: Complete table with Actions column
  - [x] SubTask 5.1: Add "Actions" column header to table
  - [x] SubTask 5.2: Add Edit button (Edit2 icon from lucide-react)
  - [x] SubTask 5.3: Add Deactivate/Reactivate button (UserX/UserCheck icons)
  - [x] SubTask 5.4: Add loading states for mutations (spinner on buttons)
  - [x] SubTask 5.5: Add toast notifications using existing toast system or alert

---

# Task Dependencies
- [Task 2] depends on [Task 1] (need modal component)
- [Task 3] depends on [Task 1] (need modal component)
- [Task 4] can run in parallel with [Task 2, 3] (independent functionality)
- [Task 5] depends on [Task 3, 4] (needs the edit/toggle functions)

# Parallelizable Work
- Task 1 can start immediately
- Tasks 2, 3, 4 can be developed in parallel after Task 1
