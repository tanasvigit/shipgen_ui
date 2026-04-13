# ShipGen Logistics Platform — Product Requirements Document

### TL;DR

ShipGen is a multi-tenant logistics platform designed for internal fleet and transportation teams. It equips dispatchers, operations managers, drivers, and admins with a unified React dashboard (with FastAPI backend) to seamlessly manage orders, drivers, vehicles, customers, and key fleet KPIs. The platform ensures operational continuity, strong data isolation, structured workflows, granular access controls, and a clear, auditable record of order lifecycles and exceptions.

---

## Goals

### Business Goals

* **Reduce Dispatch Cycle Time:** Enable fast order creation and assignment to eliminate manual tool-switching and bottlenecks.
* **Increase Fleet Utilization:** Surface actionable KPIs for unassigned drivers and vehicles, enabling effective capacity management.
* **Enforce Data Isolation:** Ensure strict cross-tenant company data separation for robust multi-tenant SaaS scalability.
* **Minimize Operational Errors:** Reduce mistakes via role-based controls so users only do what they’re entitled to.
* **Enable Auditable Operations:** Provide timestamped status transitions and exception logs for compliance and process auditability.

### User Goals

* **Fast, Accurate Order Handling:** Dispatchers can create and assign orders in under three minutes, with reliable location validation.
* **Instant Fleet Visibility:** Operations managers get at-a-glance readiness with single-click drilldown to detailed driver/vehicle queues.
* **Focused Workflows:** Drivers only see their own orders and can progress statuses efficiently; no clutter or confusion.
* **Frictionless Onboarding:** Admins have user and company onboarding tools with zero engineering involvement.
* **Seamless Navigation:** All roles enjoy predictable, consistent navigation without dead-end or unauthorized screens.

### Non-Goals

* **No Live Vehicle Maps:** Real-time GPS tracking with live map rendering is not included (telemetry is still collected).
* **Not Customer-Facing:** No portal for customer delivery tracking; all interfaces are internal operations-only.
* **No Automated Routing:** Shipment route optimization is not implemented; related flags exist for future.

---

## User Stories

**ADMIN**

* As an Admin, I want to create and manage user accounts with assigned roles, so that I can control platform access.
* As an Admin, I want to onboard new tenant companies with complete profile data, so all company data is properly isolated.
* As an Admin, I want destructive actions (delete user/order/company) to require confirmation, preventing accidental data loss.

**OPERATIONS MANAGER**

* As an Operations Manager, I want to see all driver/vehicle KPIs at once, so I don’t need to piece data from multiple screens.
* As an Operations Manager, I want to drill into specific KPI cards to actionable lists, so I can quickly fix capacity gaps.
* As an Operations Manager, I want to handle full order workflows (create, assign, transition) without waiting for admin, ensuring operational independence.

**DISPATCHER**

* As a Dispatcher, I want to enter validated pickup/delivery addresses, so every order has exact location data before dispatch.
* As a Dispatcher, I want to allocate drivers and vehicles instantly, so no double-assignments or missed resources.
* As a Dispatcher, I want to log exceptions directly against orders so delivery issues are always visible and can be reassigned quickly.
* As a Dispatcher, I want to create new customers on the fly during order entry, so the workflow is never blocked.

**DRIVER**

* As a Driver, I want to see only my assigned orders, so I’m not distracted by irrelevant work.
* As a Driver, I want to progress assigned orders one step at a time, giving the dispatch team real-time status without risk of skipping or mistakes.

**VIEWER**

* As a Viewer, I want to access all fleet/order data without mutation rights, so I can safely report and analyze.

---

## Functional Requirements

* **Authentication and Session Management** (Priority: P0)

  * Login form (email and password), JWT-based session, client-side storage of token and profile, with protected routing and session expiration handling.
  * VITE_DISABLE_AUTH flag for local/demo only.

* **Role-Based Access Control (RBAC)** (Priority: P0)

  * Roles: ADMIN, OPERATIONS_MANAGER, DISPATCHER, DRIVER, VIEWER enforced on navigation, API, and UI.
  * Navigation elements filtered by role; RoleGuard enforces protected routes.
  * Segmented write/read access per role, backend as authority.

* **Multi-Tenancy** (Priority: P0)

  * All operational data scoped by company_uuid.
  * Cross-company queries denied (404); onboarding and provisioning tied to company.

* **Order Lifecycle Management** (Priority: P0)

  * Required fields: internal_id, type, customer_uuid, scheduled_at, pickup/delivery address/lat/lng with validation.
  * Status steps: created → assigned → dispatched → arrived_at_pickup → picked_up → in_transit → out_for_delivery → delivered → completed.
  * DRIVERs advance own orders only one step at a time; Admin, Ops, Dispatcher have full control.
  * Lifecycle events and soft-delete supported.

* **Dispatch Assignment** (Priority: P0)

  * Assign drivers/vehicles, ensure resource availability.
  * Assignment creates lifecycle event + optional notification.

* **Customer Management** (Priority: P1)

  * Customers as contact records, searchable/paged, inline creation during order workflow.

* **Driver Management** (Priority: P1)

  * Filter and manage drivers (by status, online, unassigned); detail view includes telemetry and assignment.

* **Vehicle Management** (Priority: P1)

  * Manage and filter vehicles (status, assignment); metadata support; links to driver assignment.

* **Fleet Dashboard** (Priority: P1)

  * KPIs loaded via single fetch; clickable KPI cards route to filtered lists; interpretive guidance for warning states.

* **Supporting Modules** (Priority: P2)

  * Standard list/detail patterns for contacts, vendors, issues, fuel, schedules, files, logs—role-based write gates.

* **Location Input Component** (Priority: P0)

  * Search, map-pin, manual entry with geocoding and validation; explicit error feedback; debounce and result discarding to avoid flicker/race conditions.

* **Embedded Mode** (Priority: P2)

  * ?embed=1 param for minimal layout (no sidebar/topbar/footer), for widget embedding in external containers.

* **Error Handling** (Priority: P0)

  * Inline alerts, stackable toasts, distinct empty/error states, filtered permission redirects.

---

## User Experience

**Entry Point & First-Time User Experience**

* User lands on dashboard URL; if not authenticated, immediately sees a clean login form (email/password) centered onscreen.
* On login failure, inline red error banner clearly describes the issue.
* Successful login stores JWT/profile and routes to /dashboard; UI adapts immediately to user role with tailored navigation.
* No tutorial required: navigation and permissions are self-explanatory via visible options.

**Core Experience**

***Morning Dispatch Cycle (Operations Manager)***

* **Step 1: Review Fleet Dashboard**
  * User clicks sidebar ‘Fleet > Dashboard.’
  * One API request fetches all KPIs and tables.
  * Dashboard shows clickable KPI cards: drivers/vehicles total, active, online, unassigned, in use, with color cues on risks (e.g., many unassigned = warning).
* **Step 2: KPI Drilldown**
  * Clicking ‘Drivers Unassigned’ routes to prefocused driver list.
  * List table shows driver status, assignment, and lets user change status or online toggle inline via modal.
  * Clear ‘Back’ and side navigation paths offered.
* **Step 3: Order Creation**
  * Sidebar → Logistics > Orders; user clicks ‘New Order.’
  * Modal form (not full page) with all required/optional fields clearly marked.
  * LocationInput: as user types, typeahead (Google Places/OSM fallback) provides choices, or manual entry is validated/geocoded.
  * Form blocks bad data (identical pickup/delivery), shows inline errors, disables Save until valid.
  * Submit button shows spinner while saving; on success, modal closes, success toast appears, and order list updates.
* **Step 4: Dispatch Assignment**
  * User opens order detail, clicks ‘Assign Driver/Vehicle,’ modal pops with available resources.
  * Selections update status, cause lifecycle event, and may trigger driver notification.

***Driver Order Progression (Driver Role)***

* On login, drivers see only assigned orders. List is clean and focused.
* Tapping an order opens its detail; driver sees only actionable ‘Advance Status’ to next logical step.
* Cannot skip steps; cannot regress.
* If Proof of Delivery (POD) required, must submit information to unlock ‘Completed’ step.

***Exception Handling (Dispatcher Role)***

* Dispatcher opens order mid-life (e.g., ‘in_transit’).
* Clicks ‘Raise Exception,’ fills issue form; on submit, order can be marked delayed or reassigned as needed, with events logged.
* Reassignment is explicit and recorded in detail timeline.

**Advanced Features & Edge Cases**

* Embedded mode removes shell chrome for widget use, host must manage navigation.
* Mock API mode uses local data—must be flagged as demo, and non-production safe.
* Pagination derives count from backend ‘total’ field for accuracy; no calculation from row mapping.
* Search is debounced; loader and error handling for stale results.
* Unauthorized route access never lands on a 403 or dead-end; user is redirected to a safe default (/dashboard).
* Orphan assignments (e.g., deleted driver/vehicle) flagged in data quality views.
* Explicit empty states guide user and distinguish between ‘no records yet’ vs. ‘no results.’

**UI/UX Highlights**

* Sidebar: Collapsible on desktop, drawer on mobile (closes on backdrop).
* TopNavbar: Notifications, settings, logout.
* All create/edit forms are modal; no page reloads for CRUD.
* Whole table rows clickable for context; action buttons stop propagation.
* Table is responsive—tabular or card views.
* Status badges: Semantic color + text (Blue=active, Red=error, Gray=readonly); text always used for AA compliance.
* Required fields marked with \*, errors visible below fields, toasts stack and fade after \~2.5s.
* Icon-only buttons have ARIA labels, strong keyboard path through all modals.
* WCAG AA contrast tested for all key controls, particularly status badges and alerts.

---

## Narrative

It’s 7:45 AM at a bustling mid-size logistics provider. Amara, the morning dispatcher, has a problem: a delivery exception from last night—a driver didn’t close out a delivery and the customer is calling about the delay. Amara logs into ShipGen and lands on the Fleet Dashboard. In seconds, she sees three drivers are online but two are unassigned, with visual warnings prompting action.

She clicks the ‘Drivers Unassigned’ KPI and jumps directly to a filtered driver list. There, Amara finds the driver in question, sees his last delivery is still marked ‘in_transit,’ and opens the order. With two clicks, she raises an ‘exception,’ logs the failed delivery, and quickly reassigns the order to an available, currently unassigned driver. Everything is captured in the order’s event log.

A new pickup request comes in from a new customer. From the orders module, Amara starts a ‘New Order,’ types the customer’s name—found instantly—inputs valid pickup and delivery addresses using smart typeahead, marks the priority as ‘high,’ and submits. It takes less than two minutes. The new driver gets notified, advances the order’s status through each phase, providing real-time visibility to the office. By noon, the delivery is done.

In the afternoon, Amara reviews the day: the timeline for each order clearly tracks every assignment, status change, and exception. No more spreadsheets, no frantic phone calls—ShipGen kept the operation on track from a single, unified screen.

---

## Success Metrics

### User-Centric Metrics

* **Order Creation Completion Rate:** Target: >90%; track start vs. saved order forms.
* **Dispatch Assignment Time:** Median time from order creation to assignment <3 minutes; timestamped transition events.
* **Exception Resolution Time:** Median time from exception logged to new assignment <15 minutes.
* **Role Navigation Error Rate:** Users hitting permission rejections <2%.

### Business Metrics

* **Fleet Utilization:** Active vehicle utilization above 75% during operation; measured from dashboard KPIs.
* **Order Completion Rate:** >85% orders reach ‘completed’ without manual rework.
* **Unassigned Driver Reduction:** 20% drop in daily unassigned drivers within 30 days post-launch.

### Technical Metrics

* **Fleet Dashboard Load Performance:** p95 dashboard API under 800ms.
* **Pagination Accuracy:** 0 instances of table row count overestimating pages.
* **Form Error Rate:** <5% API failure on form submissions.

### Tracking Plan

* Track ‘login_success’ and ‘login_failure’ (role, error code).
* Track order form open/submit/error (with field errors).
* Track status changes (from/to, role, order).
* Track assignment events, exception logs, and reassignments.
* Track all navigation events on KPI card clicks and role redirections.
* Track usage of location input (mode/success/failure).

---

## Technical Considerations

### Technical Needs

* **API**: FastAPI backend, with versioned endpoints for core features and admin/internal functions.
* **Frontend**: React SPA, hash-based routing for static host compatibility.
* **Session**: JWT tokens; apiClient injects and refreshes/invalidates as needed.
* **Frontend Componentization**: Standard CRUD table layouts, shared hooks, responsive components; consistent local state pattern.

### Integration Points

* Google Places API (fallback: OSM Nominatim) for address/typeahead.
* VIN decode API to automatically populate vehicle metadata.
* Notification system to alert assigned drivers and key staff.
* Telemetry endpoints for real-time driver data: `lat`, `lng`, `heading`, `speed`, `altitude`.

### Data Storage & Privacy

* All records strictly scoped by `company_uuid` for SaaS multi-tenancy.
* No cross-tenant data exposure; unauthorized API requests 404.
* JWTs stored in browser storage; auto-expire on 401.
* Customer addresses stored as JSON block.
* Compliance includes region-specific time zones and locales.

### Scalability & Performance

* All list endpoints server-paginated; frontend reads authoritative `total` field.
* Fleet Dashboard loads full metrics in a single API fetch for performance.
* Large-table modules virtualized and/or use memoized row rendering.
* Debounce and cache on repetitive API calls like search/typeahead.

### Potential Challenges

* **Pagination Consistency:** Standardization needed; cannot estimate row count from display in any module.
* **Hybrid API Mode:** Local mock (VITE_USE_MOCK_API) can drift from production—must be documented and never mixed with real data in production.
* **Unauthorized Access:** All production builds must block auth bypass flags via CI/CD.
* **Data Quality:** Orphan assignments (e.g., driver/vehicle deleted while assigned) require visibility and surfacing in review dashboards.
* **Accessibility:** Painstaking WCAG AA color contrast/labeling for all controls, status badges, and navigation.

---

## Milestones & Sequencing

### Project Estimate

* **Large:** 4–8 weeks for production-ready, full platform with core modules, UX refinement, and hardening.

### Team Size & Composition

* **Medium Team (3–4):**
  * 1 Full-Stack Engineer (FastAPI + React)
  * 1 Frontend Engineer (UX-focused)
  * 1 Product/QA Hybrid

### Suggested Phases

**Phase 1 — Core Hardening (Weeks 1–2)**

* Standardize backend-driven pagination.
* Refine all edge cases in LocationInput and error handling.
* Confirm RBAC navigation and route access for all roles.
* Ensure inline validation on all CRUD modals.
* Implement error layers: inline, toast, and page states.
* *Dependencies:* Backend list endpoints expose accurate total.

**Phase 2 — UX Completion (Weeks 3–4)**

* Add skeleton loaders, unsaved-change prompts, and order status ribbons.
* Implement breadcrumbs for deep navigation.
* Refine all empty/error states across modules.
* Deliver embed mode for iframed use.
* *Dependencies:* All core modules from Phase 1; component styling tokens.

**Phase 3 — Accessibility & Performance (Weeks 5–6)**

* ARIA labeling audit, modal keyboard flow testing.
* WCAG status badge color audit.
* Virtualize heavy tables (orders, API logs).
* Memoize row rendering, cache reference data for dropdowns.
* *Dependencies:* Stable design system from Phase 2.

**Phase 4 — Appendices & Release Readiness (Weeks 7–8)**

* Document API/auth modes, role-to-route permissions, form criteria.
* Block production CI/CD on disableAuth flag.
* Run data quality audit tools; automate orphan assignment checks.
* Final go-live prep and operational review.
* *Dependencies:* All functionally complete, backend and deployment greenlit.

---