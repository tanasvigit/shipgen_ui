# Logistics Platform Functional Documentation

## 1. Overview

This workspace contains two primary applications:

- `fastapi-app`: backend REST API for authentication, IAM, fleet operations, storefront, and operational utilities.
- `shipgen-dashboard`: frontend web application (React + Vite) used by internal/admin/logistics users.

Together they provide an end-to-end logistics management platform with:

- user authentication and role-based access,
- operational fleet and order management,
- optional storefront modules,
- reporting and administrative tooling.

---

## 2. System Context

### 2.1 High-Level Architecture

- **UI (`shipgen-dashboard`)** runs in browser and calls backend APIs via HTTP.
- **API (`fastapi-app`)** exposes grouped endpoints under `/int/v1`, `/fleetops/v1`, `/storefront/v1`, and `/v1`.
- **PostgreSQL** is primary persistent store.
- **Redis** is used for lightweight cache/session helpers in backend flows.
- **Socket integration** in UI supports near-real-time vehicle/location updates.

### 2.2 Deployment Model (Current Docker Setup)

Root `docker-compose.yml` orchestrates:

- `postgres` (port `5432`)
- `api` from `fastapi-app` (port `9001`)
- `ui` from `shipgen-dashboard` served by Nginx (port `5173` externally)

---

## 3. Backend Functional Document (`fastapi-app`)

## 3.1 Business Purpose

The API provides business capabilities for:

- identity and access management (auth, roles, permissions),
- fleet logistics lifecycle (orders, drivers, vehicles, tracking, service rates),
- operational admin (companies, users, notifications, schedules, reports),
- storefront modules (products, carts, orders, checkout),
- integration/utilities (files, webhooks, comments, chat, API credentialing).

## 3.2 API Domain Structure

### 3.2.1 Internal Admin APIs (`/int/v1/*`)

Used by dashboard/internal users for management operations:

- `auth`, `me`, `users`, `companies`
- `roles`, `permissions`, `policies`
- `twofa`, `notifications`
- `reports`, `dashboards`, `settings`
- `api-credentials`, `api-events`, `api-request-logs`
- `activities`, `extensions`, `custom-fields`, `custom-field-values`
- `schedules` and related schedule tables
- `groups`, `user-devices`, `installer`, `onboard`, `lookup`

### 3.2.2 Fleet Operations APIs (`/fleetops/v1/*`)

Primary logistics execution module:

- orders and order status progression
- drivers, vehicles, contacts
- vendors, places, issues, fuel reports
- entities, payloads
- zones, service areas, fleets
- tracking numbers and tracking statuses
- service rates and service quotes

### 3.2.3 Storefront APIs (`/storefront/v1/*`)

Commerce/ordering side capabilities:

- customers
- products, categories, reviews
- carts and checkout
- storefront orders
- stores, food trucks, store networks

### 3.2.4 Utility/Public-style APIs (`/v1/*`)

- files
- comments
- selected shared utility endpoints

## 3.3 Authentication and Authorization

### 3.3.1 Authentication

- JWT bearer token model.
- Login endpoint: `POST /int/v1/auth/login`
- Token contains user UUID (`sub`) and type.
- Password hashing/verification handled in backend security utilities.

### 3.3.2 Authorization (RBAC)

- Role and permission entities are persisted in dedicated tables.
- Access checks support:
  - direct role/permission assignment,
  - role-derived permission checks via pivot tables.
- Super-admin and admin-style capabilities are role driven.

### 3.3.3 Session/Caching

- Redis is used in selected auth/bootstrap flows (short-lived cached responses/session support patterns).

## 3.4 Data and Persistence Model

### 3.4.1 Core Entities

- `users`
- `companies`
- `company_users`
- `api_credentials`

### 3.4.2 IAM Entities

- `roles`
- `permissions`
- `policies`
- pivots such as role/user and role/permission mappings

### 3.4.3 Fleet Entities

- `orders`, `drivers`, `vehicles`
- `contacts`, `vendors`, `places`
- `issues`, `fuel_reports`
- `fleets`, `zones`, `service_areas`
- `tracking_numbers`, `tracking_statuses`
- service pricing/quote entities

### 3.4.4 Storefront Entities

- products, categories, variants/addons
- carts, orders, checkouts
- stores, networks, reviews

### 3.4.5 Supporting Entities

- reports, dashboards
- webhooks
- files, comments, chat
- activities, transactions
- schedules, groups, user devices

## 3.5 Core Functional Flows

### 3.5.1 Platform Startup Flow

1. API container starts.
2. DB readiness check is executed.
3. Alembic migrations are applied (`alembic upgrade head`).
4. Uvicorn starts serving API.

### 3.5.2 Login Flow

1. UI sends identity/password to `/int/v1/auth/login`.
2. API validates user and password.
3. API returns JWT and user profile payload.
4. UI stores token and uses it in subsequent authenticated requests.

### 3.5.3 Fleet Operations Flow (Typical)

1. User creates or updates core resources (driver/vehicle/vendor/place).
2. Order is created under FleetOps.
3. Order gets linked with operational resources and tracking statuses.
4. Dashboards/reports consume resulting data for visibility.

### 3.5.4 Admin/User Provisioning Flow

- Seeder script can create initial company/users and assign super-admin role.
- Useful for first-time environment setup or local/dev bootstrap.

## 3.6 Integrations and External Dependencies

- PostgreSQL (`psycopg2` + SQLAlchemy)
- Redis
- S3-compatible storage support (`boto3`) via file utility
- push notifications (`pyfcm`) with fallback/stub patterns
- CSV/Excel support (`openpyxl`) where needed
- WHOIS/feed parsing utilities in lookup-oriented modules

## 3.7 Non-Functional and Operational Notes

- CORS is enabled with configured origin allow-list (e.g., `localhost:5173`).
- OpenAPI docs available from API (`/docs`, `/redoc`).
- Health endpoint: `/health`.
- Backend has broad module coverage and migration history; production hardening should include rigorous endpoint-level authorization review and integration hardening where placeholders exist.

---

## 4. Frontend Functional Document (`shipgen-dashboard`)

## 4.1 Business Purpose

The dashboard is the operational UI for:

- authentication and user session handling,
- fleet/logistics execution workflows,
- reporting and operational monitoring,
- administrative configuration and platform management.

## 4.2 Navigation and Routing

### 4.2.1 Router Model

- SPA built with `HashRouter` (`/#/path`), suitable for static serving.
- Root route redirects based on authentication state.

### 4.2.2 Access Control in UI

- `ProtectedRoute` enforces authenticated access.
- `RoleGuard` applies role-based visibility and route constraints.
- Sidebar navigation is role-filtered and grouped by domain.

## 4.3 Functional Modules

### 4.3.1 Authentication

- Login form with backend call to `/int/v1/auth/login`.
- Persists token and user in browser storage.
- Logout clears session and redirects to login.

### 4.3.2 Dashboard/Analytics

- KPI cards and trend visualizations.
- Charts include line/pie/bar using `recharts`.
- periodic refresh behavior for near-live stats.

### 4.3.3 Fleet and Logistics

- Orders list/detail workflows.
- Fleet resources management:
  - drivers, vehicles, vendors, contacts, places
  - fleets, zones, service areas
  - tracking numbers/statuses
  - issues/fuel reporting

### 4.3.4 Warehouse and Billing

- Warehouse operational pages (zones/inventory/GRN).
- Billing pages (invoices, payments, payment capture flows).

### 4.3.5 Admin and Configuration

- Users, companies, groups
- API credentials/events/logs
- custom fields and values
- schedules and transactions
- notifications, files, comments, activities, devices
- reports and extensions

### 4.3.6 Live Operations

- Real-time updates page(s) with socket integration hooks.
- map display currently uses embedded OpenStreetMap iframe pattern.

### 4.3.7 AI Assistant

- Browser-side assistant component using Google GenAI SDK integration pattern.

## 4.4 Data Access and State Handling

### 4.4.1 API Layer

- Central `axios` client wrapper:
  - reads API base URL from env,
  - injects bearer token,
  - handles unauthorized responses (session cleanup + redirect).

### 4.4.2 Service Layer

- Domain-specific services under `src/services`.
- Common helpers normalize backend response shapes and CRUD patterns.

### 4.4.3 State Layer

- Primarily React hooks and local/component state.
- Reusable list/CRUD hooks for loading, error, and mutation behaviors.

## 4.5 Environment and Feature Flags

- `VITE_API_BASE_URL` (preferred backend URL)
- `VITE_API_BASE` (legacy alias)
- `VITE_USE_MOCK_API=true` enables mock API mode
- `VITE_DISABLE_AUTH=true` bypasses auth guards (dev-only)
- `VITE_DEV_AUTH=true` supports development auth fallback logic

## 4.6 Build, Runtime, and Deployment

### 4.6.1 Development

- Vite dev server (`npm run dev`)

### 4.6.2 Production Build

- `npm run build` (Vite bundling with manual chunk strategy)

### 4.6.3 Docker Runtime

- Multi-stage Dockerfile:
  - build static bundle with Node
  - serve with Nginx
- Nginx config supports SPA fallback (`try_files ... /index.html`)

## 4.7 Testing Approach

- Automated E2E tests via Playwright.
- Includes smoke path (login/navigation/logout) and CRUD journey cases.
- No extensive unit-test harness observed in UI codebase; quality currently leans on E2E and manual validation.

---

## 5. Cross-Project End-to-End Flows

## 5.1 Login and Session

1. User opens UI (`localhost:5173`).
2. UI sends credentials to API (`localhost:9001`).
3. API validates and returns JWT.
4. UI stores token and unlocks protected routes.

## 5.2 Authenticated CRUD

1. User performs create/update/delete in module (e.g., vendors/orders).
2. UI service calls corresponding API endpoint with bearer token.
3. API validates auth/permissions and persists to DB.
4. UI updates list/detail state and shows success/failure feedback.

## 5.3 Live Operational Visibility

1. UI connects to socket endpoint (configured using API base).
2. incoming events update in-memory location/status panels.
3. users visualize ongoing activity in live operations screens.

---

## 6. Roles and Access (Functional View)

Current platform supports role-oriented operation at backend and frontend:

- backend enforces role/permission checks through RBAC tables and dependency guards,
- frontend uses role access maps to conditionally expose pages/actions.

Typical functional role categories in UI include:

- super admin
- company admin
- operations manager
- role-limited/read-only profiles

---

## 7. Current Known Gaps / Caveats

- Some integrations are scaffolded and may be partially implemented (e.g., certain notification/payment/provider flows).
- Initial environment requires migrations and seed steps before login/functional use.
- Frontend test strategy is E2E-heavy; unit-level coverage may need expansion for critical modules.
- Data model breadth is high; governance around permissions and module ownership should be documented per domain for production programs.

---

## 8. Operational Runbook (Quick)

### 8.1 Start full stack

```bash
docker compose up --build
```

### 8.2 Ensure schema

```bash
docker compose exec api alembic upgrade head
```

### 8.3 Create initial admin

```bash
docker compose exec api python scripts/create_initial_users.py
```

### 8.4 Endpoints

- UI: `http://localhost:5173`
- API health: `http://localhost:9001/health`
- API docs: `http://localhost:9001/docs`

---

## 9. Suggested Next Documentation Additions

- module-wise API catalog (endpoint-by-endpoint with request/response examples),
- role-permission matrix (business approval ready),
- data dictionary (table + business definitions),
- non-functional targets (SLA, scalability, security controls),
- release and change-management process.

---

## 10. FleetBase Gap Assessment and Implemented Enhancements

Based on FleetBase-style operational lifecycle requirements, the following platform gaps were identified and addressed in this iteration.

### 10.1 Gaps Identified (Before Changes)

- Order status handling existed but was not standardized as a guarded lifecycle engine.
- Assignment existed as data fields but had no dedicated orchestration endpoint (auto/manual assignment policy).
- Lifecycle event timeline was missing (no single event stream for order state transitions).
- Exception handling existed (`issues`) but was not directly tied to order lifecycle transitions/reassignment.
- Driver notification on assignment was not consistently emitted from orchestration flow.

### 10.2 Implemented Modules (Now Added)

- **Order Lifecycle Event Store**
  - New model: `app/models/order_event.py`
  - New migration: `alembic/versions/0015_order_lifecycle_events.py`
  - Captures status changes and operational events with actor + payload.

- **Fleet Orchestration Router**
  - New router: `app/api/v1/routers/fleetops_order_flow.py`
  - Wired into API router registry.
  - Endpoints added:
    - `POST /fleetops/v1/orders/{order_id}/assign`
    - `POST /fleetops/v1/orders/{order_id}/transition`
    - `POST /fleetops/v1/orders/{order_id}/exceptions`
    - `GET /fleetops/v1/orders/{order_id}/lifecycle`

- **Assignment Engine (Foundational)**
  - Supports manual assignment (`driver_uuid`) and auto-assignment fallback using available/active drivers.
  - Updates order assignment and emits `order_assigned` lifecycle event.

- **Lifecycle Transition Guard**
  - Introduces a valid status path:
    - `created -> assigned -> dispatched -> arrived_at_pickup -> picked_up -> in_transit -> out_for_delivery -> delivered -> completed`
  - Blocks backward transitions and terminal-state misuse.
  - Emits `order_status_changed` events.

- **Exception-to-Orchestration Bridge**
  - Raising an exception now:
    - creates an `Issue`,
    - updates order status to `delayed` or `reassigned`,
    - logs an `order_exception_raised` lifecycle event.

- **Driver Notification on Assignment**
  - Creates notification records for assigned driver users in assignment flow.

### 10.3 Operational Notes for New Modules

- Apply latest migrations before using new lifecycle APIs:
  - `docker compose exec api alembic upgrade head`
- New lifecycle APIs are additive and compatible with existing orders CRUD routes.
- Existing pages can now consume `/lifecycle` timeline and new assignment/transition endpoints to realize dispatcher-centric flows.

