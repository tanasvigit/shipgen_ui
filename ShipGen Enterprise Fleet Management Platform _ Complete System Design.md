# ShipGen Enterprise Fleet Management Platform — Complete System Design

### TL;DR

ShipGen is transforming from a basic fleet SaaS into a robust, enterprise-grade fleet management and logistics platform—tailored for regional SaaS scale, serving hundreds of tenants and leveraging mobile-first telemetry. The platform focuses on completing the critical advanced modules needed to rival Samsara, Fleetio, and Uber Freight, emphasizing operational intelligence, cost optimization, and modern user experience. IoT hardware support and global marketplace features are deferred for later phases.

---

## Goals

### Business Goals

* Capture a dominant share of the regional enterprise fleet market within 18 months.
* Increase average revenue per user (ARPU) by 35% through upsell of advanced operational modules.
* Reduce annual tenant churn below 6% by embedding sticky compliance and operations tools.
* Achieve a Net Promoter Score (NPS) of 50+ via differentiated user experience and reliability.

### User Goals

* Dispatchers benefit from AI-assisted, low-friction trip assignment, cutting time-to-dispatch by 40%.
* Drivers manage all daily tasks from a single mobile app, including live navigation and proof-of-delivery (POD).
* Fleet managers gain full, real-time visibility and actionable KPIs across vehicles, trips, compliance, and costs.
* Operators easily track maintenance, fuel, and driver safety to proactively reduce downtime and risk.
* Customers/shippers receive accurate, self-service insights—minimizing support requests and calls.

### Non-Goals

* IoT hardware/GPS tracker integration (deferred to Phase 4+).
* Consumer-facing marketplace or public load board (Phase 4).
* International multi-currency billing and taxation (future—out of current scope).

---

## Missing Modules Overview

| \# | Module Name | Purpose |
| --- | --- | --- |
| 1 | Real-Time Vehicle Tracking | Live map view, geofencing, historical route replay, speed/dwell analytics for fleet assets. |
| 2 | Trip & Route Management | End-to-end trip lifecycle: plan, optimize, track, and analyze all shipments and vehicle runs. |
| 3 | Maintenance Management | Preventive/reactive maintenance, service history, work orders, cost/cycle tracking. |
| 4 | Fuel Management | Monitor, analyze, and optimize fuel usage—including fraud detection and cost allocation. |
| 5 | Driver Behavior & Safety | Score and report on driver safety (speeding, braking), create coaching and incident logs. |
| 6 | Compliance & Document Management | Central document vault, expiry tracking, audit trail, and automated compliance reminders. |
| 7 | Alerts & Event Engine | Rule-based, cross-module notifications and workflows per tenant, with flexible delivery. |
| 8 | Advanced Billing & Costing | Trip-/customer-based costing, margin/profitability, and auto-invoicing per advanced tariff. |
| 9 | Warehouse–Fleet Integration | Connects dock/yard events to fleet trips, manifests, turnaround metrics, and scheduling. |
| 10 | Customer/Shipper Portal | Branded portal for shipment tracking, POD, invoices, and self-service issue management. |
| 11 | AI Dispatch & Optimization | Data-driven assignment of trips, multi-stop TSP, demand prediction, with dispatcher override. |
| 12 | IoT Device Integration Platform | Foundation for future hardware GPS/OBD support, data contracts, and device health stubs. |
| 13 | Marketplace (Stub) | Phase 4: Matchmaking, capacity listing, shipper RFQ, ratings/bids—enabling network effects. |

---

## Module 1: Real-Time Vehicle Tracking

**Purpose:** Provide a live fleet map per tenant with rich geospatial and route history data.

* **Key Features:**
  * Live map with vehicle pins/status
  * Create/manage geofences (polygons, alert triggers)
  * Route replay/time slider
  * Speed/dwell time analytics
* **DB Entities:**
  * telemetry_events (id, vehicle_uuid, driver_uuid, company_uuid, lat, lng, speed, heading, accuracy, battery, event_type, timestamp)
  * geofences (id, company_uuid, name, geometry, alert_on_entry, alert_on_exit, active)
  * geofence_events (id, geofence_uuid, vehicle_uuid, event_type, timestamp)
* **APIs:**
  * POST /telemetry/ingest
  * GET /vehicles/{id}/location/live /history
  * POST/GET/PUT /geofences
  * GET /geofences/{id}/events
* **UI:**
  * LiveMapPage (Mapbox/Leaflet), VehiclePin, GeofenceDrawTool, RouteReplaySlider, DwellTimeReport
* **RBAC:**
  * DRIVER: Only ingest own telemetry
  * DISPATCHER/Ops/ADMIN: View all
  * VIEWER: Read-only
* **Integration:**
  * Telemetry feeds Alerts, Driver Behavior, Trips (live ETA)

---

## Module 2: Trip & Route Management

**Purpose:** Central hub for planning, dispatching, tracking, and analyzing all fleet movements.

* **Key Features:**
  * Multi-stop trip planning & drag-drop stop sequencing
  * ETA calculation, live trip timeline (planned vs. actual)
  * Integrated route optimization (OSRM/Google Maps API)
  * Trip view/updates in driver mobile app
* **DB Entities:**
  * trips, trip_stops, trip_telemetry_snapshots
* **APIs:**
  * POST/GET/PATCH /trips, /trip_stops, /eta, /replay
* **UI:**
  * TripPlannerPage, StopSequenceEditor, LiveTripTracker, TripTimelineView, ETAWidget
* **RBAC:**
  * DISPATCHER creates/assigns; DRIVER updates stops via app
* **Integration:**
  * Orders (trip spawn), Telemetry (live ETA), Billing (cost), Customer Portal

---

## Module 3: Maintenance Management

**Purpose:** Eliminate unplanned downtime by tracking all preventive and reactive service events.

* **Key Features:**
  * Schedule-based triggers (km/time), work order lifecycle, parts cost tracking, vendor assignments, expiry reminders
* **DB Entities:**
  * maintenance_schedules, work_orders, work_order_items, maintenance_vendors
* **APIs:**
  * POST/GET/PATCH /maintenance/schedules, /work-orders, /history, /due-soon
* **UI:**
  * MaintenanceSchedulePage, WorkOrderBoard, VehicleMaintenanceHistory, DueSoonWidget
* **RBAC:**
  * ADMIN/Ops manages; DRIVER reports defects
* **Integration:**
  * Vehicle (odometer), Alerts (due soon), Billing (cost allocation)

---

## Module 4: Fuel Management

**Purpose:** Unify and audit all fuel spend—preventing fraud and benchmarking efficiency.

* **Key Features:**
  * Manual/carded entry, deviation/fraud flags, efficiency metric, per-trip allocation
* **DB Entities:**
  * fuel_logs, fuel_efficiency_snapshots
* **APIs:**
  * POST/GET /fuel/logs, /analytics, /anomalies, /vehicles/{id}/fuel/efficiency
* **UI:**
  * FuelLogPage, FuelAnalyticsDashboard, AnomalyAlertList
* **RBAC:**
  * DRIVER logs; ADMIN/Ops analyzes
* **Integration:**
  * Telemetry (odometer), Alerts (fraud), Billing, Trips

---

## Module 5: Driver Behavior & Safety

**Purpose:** Quantitatively assess and coach drivers on unsafe behaviors.

* **Key Features:**
  * Real-time detection (speeding, harsh brake), driver scoring (0–100), leaderboard, coaching flags
* **DB Entities:**
  * driver_behavior_events, driver_safety_scores, driver_coaching_flags
* **APIs:**
  * POST /behavior/events, GET /drivers/{id}/behavior/events/score/leaderboard, POST /drivers/{id}/coaching-flags
* **UI:**
  * DriverSafetyDashboard, SafetyScoreCard, BehaviorEventTimeline, DriverLeaderboard, CoachingFlagReview
* **RBAC:**
  * DRIVER: own score only; Ops/ADMIN: all drivers
* **Integration:**
  * Trip, Alerts, Reports

---

## Module 6: Compliance & Document Management

**Purpose:** Centralize all regulatory and contract document handling, with expiry tracking.

* **Key Features:**
  * Document vault (vehicle/driver), expiry alerts, traffic-light dashboard, OCR stub
* **DB Entities:**
  * compliance_documents, compliance_alerts
* **APIs:**
  * POST/GET/PATCH /compliance/documents/dashboard/expiring
* **UI:**
  * ComplianceDashboardPage, DocumentVaultPage, ExpiryAlertList
* **RBAC:**
  * ADMIN/Ops uploads; DRIVER views own
* **Integration:**
  * Alerts (expiry), Vehicles, Drivers, Notifications (email/SMS)

---

## Module 7: Alerts & Event Engine

**Purpose:** Cross-platform, rule-based notification and workflow engine.

* **Key Features:**
  * Tenant-specific rules, channels (in-app, email, SMS, webhook), alert history, per-role routing
* **DB Entities:**
  * alert_rules, alert_events, alert_subscriptions
* **APIs:**
  * POST/GET/PATCH/DELETE /alerts/rules; /alerts/events; /alerts/events/summary
* **UI:**
  * AlertRuleBuilderPage, AlertInboxPage, AlertBadge, AlertHistoryTimeline
* **RBAC:**
  * ADMIN: manage rules; Ops/Dispatcher: receive/ack; DRIVER: own alerts
* **Integration:**
  * All modules (event input), Notification module

---

## Module 8: Advanced Billing & Costing

**Purpose:** Provide granular, accurate revenue/cost modeling for all logistics activity.

* **Key Features:**
  * Trip cost breakdown (fuel, driver, tolls, maintenance), custom rate cards, margin reporting, invoice auto-gen
* **DB Entities:**
  * billing_rate_cards, trip_cost_breakdowns, invoice_line_items
* **APIs:**
  * POST/GET /billing/rate-cards, /cost-breakdown, /profitability, /invoices/generate-from-trips
* **UI:**
  * RateCardBuilderPage, TripCostBreakdownPanel, ProfitabilityDashboard, InvoiceAutoGenWizard
* **RBAC:**
  * ADMIN: manage; Ops: analyze; Dispatcher: view costs
* **Integration:**
  * Trips, Fuel, Drivers, Billing extension

---

## Module 9: Warehouse–Fleet Integration

**Purpose:** Bridge warehouse/yard processes with vehicle trip lifecycle.

* **Key Features:**
  * Dock scheduling, load manifests, yard event logs, turnaround analysis
* **DB Entities:**
  * dock_schedules, load_manifests, yard_events
* **APIs:**
  * POST/GET/PATCH /warehouse/dock-schedules, /load-manifests, /yard/active-vehicles
* **UI:**
  * DockSchedulerPage, YardViewPage, LoadManifestForm, WarehouseFleetDashboard
* **RBAC:**
  * ADMIN/Ops: manage schedules; Dispatcher: assign; DRIVER: check-in
* **Integration:**
  * Trips, Vehicles, Orders, Extended Warehouse

---

## Module 10: Customer / Shipper Portal

**Purpose:** Self-service, branded interface for shippers to track, verify, and manage shipments.

* **Key Features:**
  * Order/trip tracking, live maps, status/ETA updates, POD (photo/signature), invoices, issue management
* **DB Entities:**
  * portal_users, portal_sessions, pod_records, portal_notifications
* **APIs:**
  * /portal/auth, /orders, /orders/{id}/tracking+poc, /invoices, /issues, /notifications
* **UI:**
  * CustomerPortal SPA, OrderTrackingPage, PODViewer, InvoiceListPage, IssueSubmitForm
* **RBAC:**
  * Separate auth; strictly role-scoped
* **Integration:**
  * Orders, Trips, Invoices, Issues, Notifications

---

## Module 11: AI Dispatch & Optimization

**Purpose:** ML-driven dispatch and route optimization to maximize efficiency and minimize manual work.

* **Key Features:**
  * Driver/vehicle matching, multi-stop TSP, ETA/demand ML prediction, dispatcher override
* **DB Entities:**
  * dispatch_recommendations, route_optimization_jobs
* **APIs:**
  * POST /ai/dispatch/recommend, /ai/routes/optimize, GET /ai/demand/forecast, PATCH /ai/dispatch/recommendations/accept/override
* **UI:**
  * AIDispatchPanel, RouteOptimizerWidget, DemandForecastChart
* **RBAC:**
  * DISPATCHER: act on AI; ADMIN: configure
* **Integration:**
  * Drivers, Vehicles, Trips, Orders, Telemetry

---

## Module 12: IoT Device Integration Platform (Stub)

**Purpose:** Ready the platform for hardware GPS/OBD and unified device-vehicle mapping.

* **Key Features:**
  * Device registry, schema contract, MQTT topic design, device health monitoring stub
* **DB Entities:**
  * iot_devices, iot_device_logs
* **APIs:**
  * POST/GET/PATCH /iot/devices, POST /iot/telemetry/ingest
* **Integration:**
  * Telemetry (schema unification), Vehicles, Alerts (device offline)

---

## Module 13: Marketplace (Stub — Phase 4)

**Purpose:** Lay the foundations for a full load/capacity exchange in future phases.

* **Key Features:**
  * Capacity listings, RFQ/bidding, ratings, commission
* **DB Entities:**
  * marketplace_listings, marketplace_bids, marketplace_ratings
* **Integration:**
  * Orders, Billing, Company

---

## Complete System Architecture

* **Microservices Split:**
  * **Phase 1:** Modular monolith (separate Telemetry Ingestion microservice due to high throughput)
  * **Core Services:** API Gateway, Auth, Core Fleet (orders, vehicles, drivers), Telemetry Ingestion, Trip & Dispatch, Alerts & Event, Billing, Portal, AI/ML
* **Event-Driven Approach:**
  * Phase 1: Redis Streams for key domains (`telemetry.raw`, `trips.status_changed`, `alerts.triggered`, etc.)
  * Upgrade to Kafka in Phase 3+
* **Telemetry Pipeline:**
  * Mobile App → POST /telemetry/ingest → Telemetry Ingestion Service → Redis Streams → Telemetry Processor → PostgreSQL + TimescaleDB
* **API Gateway:**
  * Single entry, JWT validation, tenant context (company_uuid), per-tenant rate limiting
* **Multi-Tenancy:**
  * Shared DB, schema-per-company or strict RLS on company_uuid
* **Scalability:**
  * Horizontally scalable ingest; Redis for live vehicle cache (TTL 60s); static assets on CDN; TimescaleDB hypertables

---

## Complete Data Model — ER Diagram (Textual)

* **Company (1)** → (N) **Vehicles**
* **Company (1)** → (N) **Drivers**
* **Company (1)** → (N) **Orders**
* **Company (1)** → (N) **Trips**
* **Order (1)** → (1) **Trip**
* **Trip (1)** → (N) **TripStops**
* **Trip (1)** → (N) **TelemetryEvents** (via `trip_telemetry_snapshots`)
* **Trip (1)** → (N) **FuelLogs**
* **Trip (1)** → (N) **DriverBehaviorEvents**
* **Trip (1)** → (1) **TripCostBreakdown**
* **Vehicle (1)** → (N) **TelemetryEvents**, **FuelLogs**, **MaintenanceSchedules**, **WorkOrders**, **ComplianceDocuments**, **IoTDevices**
* **Driver (1)** → (N) **Trips**, **DriverBehaviorEvents**, **DriverSafetyScores**, **FuelLogs**, **ComplianceDocuments**
* **AlertRule (1)** → (N) **AlertEvents**
* **Geofence (1)** → (N) **GeofenceEvents**
* **DockSchedule (1)** → (1) **Trip**, (1) **Warehouse**, (1) **Vehicle**
* **LoadManifest (1)** → (1) **Trip**
* **PortalUser (N)** → (1) **Customer**
* **PODRecord (1)** → (1) **TripStop**
* **DispatchRecommendation (1)** → (1) **Order**
* **MarketplaceListing (1)** → (N) **MarketplaceBids**

**Critical Entity Fields:**

* **trips:** id, company_uuid, order_uuid, driver_uuid, vehicle_uuid, status (ENUM), planned_start, actual_start, planned_end, actual_end, total_planned_km, total_actual_km, polyline
* **telemetry_events:** id, vehicle_uuid, driver_uuid, company_uuid, lat, lng, speed, heading, accuracy, battery, event_type, timestamp
* **driver_safety_scores:** id, driver_uuid, company_uuid, period_start, period_end, score, total_events, overspeed_count, harsh_brake_count, accel_count, corner_count, trips_analyzed
* **work_orders:** id, company_uuid, vehicle_uuid, schedule_uuid, type, status, description, assigned_to, opened_at, closed_at, total_cost
* **alert_events:** id, company_uuid, rule_uuid, entity_type, entity_uuid, message, severity, status, triggered_at, acknowledged_by, acknowledged_at, resolved_at

---

## End-to-End Workflows

1. **Trip Lifecycle:**  

  Order created → Dispatcher reviews AI suggestions → Assignment → Trip created (stops auto/sequenced) → Assigned Driver starts (mobile app) → Telemetry stream begins → Status update at each stop → POD captured (photo/signature) → Trip ends → Automated cost breakdown → Invoice generated

2. **AI Dispatch Workflow:**  

  New order → AI engine scores drivers (proximity, safety, capacity, legal hours) → Top 3 surfaced → Dispatcher accepts/overrides → Confirmation triggers assignment & user notifications

3. **Maintenance Lifecycle:**  

  Telemetry odometer→ Maintenance schedule check → Alert if close/overdue → Work order auto-generated → Assigned to vendor/tech → Work performed/logged → Schedule/odometer reset

4. **Alert Generation Flow:**  

  Telemetry/other event → Engine evaluates rules per tenant → If triggered, creates AlertEvent → Routed by role/subscription/channel → User acknowledges → Resolved and audit logged

5. **Driver Safety Monitoring:**  

  Telemetry → Behavior event detection (e.g., overspeed, harsh brake) → Event logged/score updated → Safety score drops under threshold → Coaching flag auto-created → Ops/Manager reviews/coaches → Compliance & improvement tracked

---

## AI/ML Capabilities

1. **Predictive Maintenance:**

  * Features: vehicle age, odometer, last service, behavior counts, fuel efficiency
  * Model: Gradient boosting (phase 2), risk score + recommended service date
  * Phase 1: rules, Phase 2: trained model

2. **Smart Dispatch:**

  * Score: proximity (40%), safety (25%), capacity (20%), hours-of-service (15%)
  * Phase 1: deterministic, Phase 2: learned weights (dispatcher feedback loop)

3. **Demand Forecasting:**

  * Prophet/LSTM on past order volumes per lane/region
  * Output: load prediction, supports vehicle pre-staging

4. **Route Optimization:**

  * Phase 1: OSRM/Google shortest path, Phase 2: custom TSP w/ constraints

5. **Anomaly Detection:**

  * Isolation Forest on fuel logs for fraud patterning; also for stop anomalies in trip telemetry

6. **ETA Prediction:**

  * Hybrid: OSRM ETA + historical correction factor per route type

---

## Technology Recommendations

* **Backend:**
  * FastAPI (existing, keep)
  * Dedicated Telemetry Ingestion service w/ async
* **Streaming/Event Bus:**
  * Redis Streams (fast, low ops) Phase 1-2
  * Kafka (Phase 3+, if >10k events/sec)
* **Database:**
  * PostgreSQL w/ RLS for tenancy
  * TimescaleDB extension for telemetry_events
  * Redis for live vehicle cache/session/event bus
* **Frontend:**
  * React SPA (existing, keep)
  * Mapbox GL JS for maps
  * React Query, Socket.IO/SSE for live
* **Mobile Driver App:**
  * React Native (code sharing)
  * Key: background telemetry, trip, POD, fuel logs
* **IoT:**
  * HTTP REST (today); MQTT/EMQX (device/IoT, future)
* **Deployment:**
  * Docker Compose now, move to K8s/EKS/GKE Phase 3; Cloud RDS; CDN (CloudFront/CloudFlare)
* **Monitoring:**
  * Prometheus, Grafana, Sentry, structured logging

---

## Phase-Wise Implementation Roadmap

* **Phase 1:** Weeks 1-12, 3-4 engineers
  * Real-Time Tracking, Trip & Route, Alerts, Compliance, Driver Behavior, Maintenance
* **Phase 2:** Weeks 13-24, 3-4 engineers
  * Fuel + Anomaly, Advanced Billing, Warehouse–Fleet, Customer Portal MVP, event bus w/ Redis Streams
* **Phase 3:** Weeks 25-36, 4-5 engineers
  * AI Dispatch v1, OSRM Routing, ML basic models, IoT stub, TimescaleDB, perf hardening
* **Phase 4:** Weeks 37-52, 5+ engineers
  * Marketplace, IoT hardware, advanced ML, multi-region, developer API marketplace

*Critical Path:* Ship telemetry ingestion & Alerts Engine in Phase 1—foundation for nearly every other module.

---

## User Stories

**Fleet Manager/Admin**

* As an ADMIN, I want to review compliance status for all vehicles and drivers, so that we never operate out-of-license.
* As an ADMIN, I want to view maintenance schedules and service costs, so that downtime and spend are minimized.
* As an ADMIN, I want profitability dashboards per customer/trip, so that we focus on high-margin business.

**Operations Manager**

* As an OPERATIONS_MANAGER, I want alerts for urgent incidents and required acknowledgment, so that nothing is missed during my shift.
* As an OPERATIONS_MANAGER, I want to review unsafe driver behavior events, so that I can coach and enforce safety policies.
* As an OPERATIONS_MANAGER, I want to monitor active vehicles’ yard status and dock scheduling, so that logistics flows smoothly.

**Dispatcher**

* As a DISPATCHER, I want AI-suggested trip assignments, so that I save time and reduce errors.
* As a DISPATCHER, I want to plan and optimize multi-stop trips with drag-drop, so that routes are efficient.
* As a DISPATCHER, I want to track all vehicles live on a map, so I can quickly respond to customer calls.

**Driver**

* As a DRIVER, I want a mobile app showing my current trip and assigned stops, so that I never miss a delivery.
* As a DRIVER, I want to submit POD (photo/signature) and fuel logs easily, so my work is verified and expenses reimbursed.
* As a DRIVER, I want to get alerted if any of my documents are about to expire, so I stay compliant.

**Customer/Shipper**

* As a SHIPPER, I want to track my shipment in real time on a branded portal, so that I don't need to call dispatch.
* As a SHIPPER, I want to view/download invoices and POD per order, so my records are up to date.
* As a SHIPPER, I want to raise issues or support requests directly, so they are resolved faster.

---

## Success Metrics

* **User-Centric Metrics:**
  * Dispatcher time-to-assign reduced by 40% (time stamps, task logs)
  * Driver App DAU exceeds 80% of all assigned active drivers (app analytics)
  * Customer portal self-service rate exceeds 60% of tracking queries (portal vs manual support logs)
* **Business Metrics:**
  * ARPU lifted as tenants implement 3+ advanced modules (billing logs)
  * Annual churn under 6% (tenant logouts/data retention)
  * NPS over 50 (quarterly survey, customer feedback)
* **Technical Metrics:**
  * Telemetry ingestion end-to-end <2 seconds
  * Live map update frequency: 10s intervals
  * API response (p95) <300ms
  * System uptime >99.9% (monitoring)
* **Tracking Plan:**
  * Log: trip create/complete, driver app open/action, fuel log, maintenance/alert ack, AI dispatch override, portal login, POD submit

---

## Technical Considerations

### Technical Needs

* Modular backend (FastAPI) with separated Telemetry Ingestion microservice
* RESTful, multi-tenant APIs; SRP per module
* React SPA front-end with Mapbox GL
* React Native driver app for full mobility

### Integration Points

* Existing modules: Users, Vehicles, Orders, Customers, Billing
* 3rd Party APIs: OSRM/Google Maps (routing/ETAs), Email/SMS, OCR for docs (stub), future RFID/fuel cards
* Push notifications, cloud storage (POD/image/docs), payment gateways

### Data Storage & Privacy

* PostgreSQL, RLS for company isolation
* TimescaleDB for telemetry events (time-partitioned)
* Cloud blob storage for images/docs
* Full audit logs for RBAC actions
* Encrypted at rest/in transit; GDPR-ready fields

### Scalability & Performance

* Separate Telemetry service horizontally scalable
* Redis for live location (TTL), event streams
* Analytics/jobs offloaded from main API
* Multi-tenant queries optimized with indexed company_uuid and partitioning

### Potential Challenges

* Integration with external devices (future-proofing schema)
* High volume telemetry handling (future scaling strategy)
* Data privacy/isolation between tenants
* Synchronous alert/action routing
* User experience on legacy devices/networks (driver app)

---

## Milestones & Sequencing

### Project Estimate

* **Phase 1:** 12 weeks (Medium Team: 3–4 engineers)
* **Phase 2:** 12 weeks (3–4 engineers)
* **Phase 3:** 12 weeks (4–5 engineers)
* **Phase 4:** 16 weeks+ (5+ engineers)

### Team Size & Composition

* Phase 1–2: 3–4 total (lead backend, front end, mobile fullstack, plus part-time design/QA)
* Phase 3: 4–5 engineers (additional ML/AI expertise)
* Phase 4: 5+ (devops, SRE, partner/BD support)

### Suggested Phases

**Phase 1 – Core Operational Platform (12 weeks)**

* *Deliverables:*
  * Real-Time Tracking (mobile telemetry ingestion, live maps)
  * Trip & Route Management (multi-stop, planner)
  * Alerts & Event Engine (rule builder, global alerts)
  * Compliance & Document Management
  * Driver Behavior/Safety scoring and dashboard
  * Maintenance Management (scheduler, work orders)
* *Dependencies:*
  * Existing fleet/vehicle/order modules; Map SDK; Redis/DB setup

**Phase 2 – Analytics & Self-Service Expansion (12 weeks)**

* *Deliverables:*
  * Fuel Management (logs, efficiency, anomaly detection)
  * Advanced Billing & Profitability
  * Warehouse-Fleet Integration (dock/yard scheduling)
  * Customer/Shipper Portal (tracking, POD, invoices)
  * Redis Streams event bus
* *Dependencies:*
  * Phase 1 modules/API foundation

**Phase 3 – AI & Automation (12 weeks)**

* *Deliverables:*
  * AI Dispatch & Recommendation engine (v1, rule-based)
  * Route Optimization (OSRM integration)
  * ML: Predictive maintenance, demand forecasting (initial)
  * IoT Device stub/API; TimescaleDB migration/performance tuning
* *Dependencies:*
  * Fuel, Trips, Telemetry groundwork

**Phase 4 – Platform/Marketplace Expansion (16 weeks+)**

* *Deliverables:*
  * Marketplace (listing, bids, ratings), IoT hardware support
  * Advanced ML/AI (dispatch v2, anomaly detection), multi-region, developer API marketplace
* *Dependencies:*
  * Matured core modules, stable event bus, stakeholder engagement

---

This system design ensures that ShipGen can not only match but also surpass regional and global competitors in operational depth, modular growth, and SaaS readiness—delivering a truly next-generation platform for modern fleet operations.