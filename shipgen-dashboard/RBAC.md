# Logistics RBAC — Developer Reference

This document describes the **role-based access control** system for the logistics stack: **FastAPI backend** (`fastapi-app/`) and **ShipGen dashboard** (`shipgen-dashboard/`). Use it when extending APIs, adding routes, or changing UI permissions.

---

## 1. Roles

Five fixed string roles (stored on the user, enforced on the API, mirrored in the UI):

| Role | Purpose |
|------|---------|
| `ADMIN` | Full access, including user management and destructive actions. |
| `OPERATIONS_MANAGER` | Operations: orders, assignment, transitions, customers; **no** user admin. |
| `DISPATCHER` | Create/update orders, assign, transition status, manage customer records; **no** user admin; **no** soft-delete of orders (admin only). |
| `DRIVER` | **Only** orders assigned to their driver profile; **one-step forward** status transitions only; **no** contacts/customers API; **no** assign/dispatch/exceptions. |
| `VIEWER` | Read-only: no mutating fleetops order/contact endpoints (except where explicitly allowed as GET). |

**Default when missing or invalid:** `DISPATCHER` (see `effective_user_role()` below).

---

## 2. Backend — Core Module

**File:** `fastapi-app/app/core/roles.py`

- **Constants:** `ADMIN`, `OPERATIONS_MANAGER`, `DISPATCHER`, `DRIVER`, `VIEWER`, `ALL_ROLES`, `STAFF_ORDER_MUTATORS` (staff who can run most order mutations outside driver-specific rules).
- **`effective_user_role(user)`**  
  - Reads `user.role`, normalizes uppercase.  
  - Empty / unknown values → **`DISPATCHER`**.  
  - Use this anywhere you need a stable role string (login payload, checks, logging).
- **`require_roles(*allowed_roles)`**  
  - Returns a FastAPI dependency: if `effective_user_role(current_user)` ∉ `allowed_roles` → **HTTP 403** with `"Insufficient permissions"`.  
  - Usage: `current: User = Depends(require_roles(ADMIN, OPERATIONS_MANAGER))`  
  - Implemented with a **lazy import** of `_get_current_user` to avoid circular imports with `auth`.

Do **not** duplicate role literals across the codebase; import from `app.core.roles` where possible.

---

## 3. Database

- **Column:** `users.role` — nullable `String(64)` (see model `app/models/user.py`).
- **Migration:** `fastapi-app/alembic/versions/0017_user_role_rbac.py`  
  - Apply with: `alembic upgrade head` (from `fastapi-app/`).

**Existing rows:** `NULL` or invalid values behave as **DISPATCHER** until you set a proper role, e.g.:

```sql
UPDATE users SET role = 'ADMIN' WHERE email = 'your-admin@example.com';
```

---

## 4. API Surfaces — Who Can Do What

### 4.1 Auth / identity

- **`POST /int/v1/auth/login`** — `LoginResponse.user.role` is set via `effective_user_role`.
- **`GET /int/v1/me`** — `MeUser.role` includes the same normalized value.

### 4.2 Users (`/int/v1/users`)

| Action | Roles |
|--------|--------|
| `GET /` (list), `GET /{id}`, `POST /`, `PUT\|PATCH /{id}`, `DELETE /{id}` | **ADMIN** only (list scoped by `current_user.company_uuid` when set). |
| `GET /me` (or equivalent current-user route), password / 2FA / locale helpers | Authenticated user (not restricted to admin). |

### 4.3 Fleetops contacts / customers (`/fleetops/v1/contacts`)

| Action | Roles |
|--------|--------|
| `GET /`, `GET /{id}` | All **except** **DRIVER** (403 for drivers). |
| `POST /`, `PUT\|PATCH /{id}` | **ADMIN**, **OPERATIONS_MANAGER**, **DISPATCHER** |
| `DELETE /{id}` | **ADMIN** only |

### 4.4 Fleetops orders (`/fleetops/v1/orders`)

**Driver data scope:** for **DRIVER**, list and detail only include orders where `orders.driver_assigned_uuid` equals the **`drivers.uuid`** row linked to `drivers.user_uuid == current_user.uuid` (same company, not deleted). If no driver row exists, the driver sees **no** orders.

| Endpoint / verb | Roles |
|-------------------|--------|
| `GET /` (list), `GET /{id}`, read-only sub-paths (e.g. distance, eta, tracker) | All roles **with** driver filter for **DRIVER**. |
| `POST /` (create), `PUT\|PATCH /{id}` | **ADMIN**, **OPERATIONS_MANAGER**, **DISPATCHER** |
| `DELETE /{id}`, `DELETE /{id}/delete` | **ADMIN** only |
| `POST` start, complete, `DELETE` cancel, schedule, dispatch | **ADMIN**, **OPERATIONS_MANAGER**, **DISPATCHER** (not **DRIVER** / **VIEWER**) |

### 4.5 Order flow (same prefix, separate router)

**File:** `fastapi-app/app/api/v1/routers/fleetops_order_flow.py`

- Uses **`_get_scoped_order`** from `fleetops_orders` so **DRIVER** scoping matches list/detail.
- **`POST .../assign`:** **ADMIN**, **OPERATIONS_MANAGER**, **DISPATCHER**
- **`POST .../exceptions`:** same staff roles
- **`POST .../transition`:**
  - **VIEWER** → 403
  - **DRIVER** → only **single forward** step on the main lifecycle list; no terminal/special statuses; must be assigned driver on the order
  - **ADMIN**, **OPERATIONS_MANAGER**, **DISPATCHER** → existing transition validation (forward / allowed specials as implemented)

---

## 5. Schemas

- **`app/schemas/user.py`** — `role` on create/update/out; `LogisticsRole` literal for typing.
- **`app/schemas/auth.py`** — `role` on `LoginUser` and `MeUser`.

---

## 6. Frontend (`shipgen-dashboard`)

### 6.1 Types

**File:** `shipgen-dashboard/src/types.ts`

- Enum **`UserRole`**: `ADMIN`, `OPERATIONS_MANAGER`, `DISPATCHER`, `DRIVER`, `VIEWER`
- **`normalizeUserRole(raw)`** — maps API strings and legacy names (`SUPER_ADMIN` → `ADMIN`, etc.). Unknown → **DISPATCHER**.

### 6.2 Central behavior

**File:** `shipgen-dashboard/src/utils/roleAccess.ts`

- **`SECTION_ACCESS`** — coarse nav sections (dashboard, logistics, fleet, …) per role.
- **`canAccessRoute(role, path)`** — pathname rules, including:
  - `/analytics/users` → **ADMIN** only
  - `/logistics/customers` → not **DRIVER**
  - `/logistics/orders/dispatch-board` → not **DRIVER** or **VIEWER**
- **`getStoredUserRole()`** — reads `localStorage.user.role` and normalizes.
- Small helpers: `canCreateOrders`, `canEditOrders`, `canDeleteOrders`, `canMutateCustomers`, `canDeleteCustomers`, `canAssignOrDispatchOrders`, `canManageUsers`, etc.

**Login** (`Login.tsx`) persists **`role`** from the API into `localStorage` under `user`.

### 6.3 Route guard

**`RoleGuard`** — optional **`requiredRole`** array; always combines with **`canAccessRoute`**.

Example: **`/analytics/users`** is wrapped with **`requiredRole={[UserRole.ADMIN]}`** in `App.tsx`.

### 6.4 UI patterns

- **Orders / customers / order detail** use `getStoredUserRole()` and the helpers to hide buttons (create, edit, delete, dispatch, assign, exceptions).
- Backend remains the **source of truth**; the UI is a convenience layer only.

---

## 7. Extending the System

### Add a new API that should be role-gated

1. Import **`require_roles`** and role constants from **`app.core.roles`**.
2. Add `current: User = Depends(require_roles(...))` on the endpoint (or a small helper dependency).
3. For **list/read** that must be scoped (e.g. driver-only data), reuse **`effective_user_role`** and existing helpers in **`fleetops_orders`** (`_driver_uuid_for_user`, `_apply_driver_order_filters`, `_get_scoped_order`) or mirror the same pattern.

### Add a new dashboard route

1. Extend **`canAccessRoute`** if the path needs special rules.
2. Optionally wrap the route in **`RoleGuard`** with **`requiredRole`**.
3. Hide destructive controls with the same helpers you use elsewhere (or add a new helper in **`roleAccess.ts`**).

### Add a sixth role

1. Add constant + **`ALL_ROLES`** in **`roles.py`**.
2. New Alembic migration **not** required if `users.role` stays a free string (already `String(64)`).
3. Update **`LogisticsRole`** / **`UserRole`** / **`normalizeUserRole`** / **`SECTION_ACCESS`** / **`canAccessRoute`** as needed.
4. Update this document and any permission matrices in tests.

---

## 8. Testing

- **`app/tests/conftest.py`** — default **`test_user`** sets **`role="ADMIN"`** so user-management and admin-only tests pass.
- When adding tests for **403** behavior, create users with **`DISPATCHER`**, **`DRIVER`**, etc., and assert status codes.

---

## 9. Quick File Index

| Area | Path |
|------|------|
| Role constants & dependency | `fastapi-app/app/core/roles.py` |
| User model field | `fastapi-app/app/models/user.py` |
| Migration | `fastapi-app/alembic/versions/0017_user_role_rbac.py` |
| Orders + scoping | `fastapi-app/app/api/v1/routers/fleetops_orders.py` |
| Assign / transition / exceptions | `fastapi-app/app/api/v1/routers/fleetops_order_flow.py` |
| Contacts | `fastapi-app/app/api/v1/routers/fleetops_contacts.py` |
| Users CRUD | `fastapi-app/app/api/v1/routers/users.py` |
| Login / Me payload | `fastapi-app/app/api/v1/routers/auth.py`, `me.py` |
| Frontend types | `shipgen-dashboard/src/types.ts` |
| Frontend matrix & routes | `shipgen-dashboard/src/utils/roleAccess.ts` |
| Route + UI | `shipgen-dashboard/src/App.tsx`, orders/customer components |

---

## 10. Principle

**Always enforce authorization on the server.** The UI hides actions to reduce confusion, but **must not** be relied on for security. Unauthorized calls should receive **403** (or **404** where driver scope intentionally hides resource existence).

---

## 11. Demo login accounts (local testing)

Seed script (idempotent): from `fastapi-app/` run:

`python scripts/seed_rbac_demo_users.py`

**Same password for all five:** `RbacDemo123`

| Role | Email (use as login identity) |
|------|-------------------------------|
| ADMIN | `admin@demo.local` |
| OPERATIONS_MANAGER | `operations@demo.local` |
| DISPATCHER | `dispatcher@demo.local` |
| DRIVER | `driver@demo.local` |
| VIEWER | `viewer@demo.local` |

The script attaches users to an existing company when possible, creates a **driver** row for the DRIVER account (so assigned orders can show up), and ensures **company_users** links. Do not use these emails/passwords in production.
