# TechLiv API - Detailed Test Data Documentation

This document provides comprehensive details about all test data generated for the TechLiv API, including actual values, database mappings, and usage examples.

## Table of Contents

1. [Overview](#overview)
2. [Authentication Credentials](#authentication-credentials)
3. [Users](#users)
4. [Companies](#companies)
5. [Roles & Permissions](#roles--permissions)
6. [Contacts](#contacts)
7. [Vendors](#vendors)
8. [Places](#places)
9. [Drivers](#drivers)
10. [Vehicles](#vehicles)
11. [Orders](#orders)
12. [Service Rates](#service-rates)
13. [Devices](#devices)
14. [Storefront Data](#storefront-data)
15. [Using Test Data in API Calls](#using-test-data-in-api-calls)

---

## Overview

The test data generator creates a complete set of test records across all major modules of the TechLiv API. All data is validated against the database schema to ensure correct mapping.

**Total Test Records Created:**
- 3 Users
- 2 Companies
- 3 Roles
- 5 Permissions
- 2 Contacts
- 2 Vendors
- 2 Places
- 2 Drivers (with associated Users)
- 2 Vehicles
- 2 Orders
- 1 Service Rate (with rate fees)
- 1 Device
- 1 Storefront Customer
- 1 Storefront Product
- 1 Storefront Cart

---

## Authentication Credentials

### Initial Users (Created by `create_initial_users.py`)

| User Type | Email | Password | UUID Field | Role |
|-----------|-------|----------|------------|------|
| Super Admin | `admin@techliv.net` | `admin123` | `admin_uuid` | super-admin |
| Regular User | `user@techliv.net` | `user123` | `regular_uuid` | user |

### Test Users (Created by `generate_test_data.py`)

| User Type | Email | Password | UUID Field | Type |
|-----------|-------|----------|------------|------|
| Manager | `manager@test.techliv.net` | `Test123` | `manager_uuid` | manager |
| Dispatcher | `dispatcher@test.techliv.net` | `Test123` | `dispatcher_uuid` | dispatcher |
| Driver User 1 | `mike.johnson@test.com` | `Test123` | `driver1_user_uuid` | driver |
| Driver User 2 | `sarah.williams@test.com` | `Test123` | `driver2_user_uuid` | driver |

**Login Example:**
```bash
curl -X POST http://localhost:9001/int/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identity": "manager@test.techliv.net",
    "password": "Test123"
  }'
```

**Database Mapping:**
- `users.email` → Email address
- `users.password` → Bcrypt hashed password
- `users.type` → User type (admin, manager, dispatcher, driver, user)
- `users.company_uuid` → Links to company
- `users.status` → "active"

---

## Users

### Test Users Created

#### 1. Manager User
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "user_<hex>",
  "name": "Test Manager",
  "email": "manager@test.techliv.net",
  "phone": "+1234567890",
  "type": "manager",
  "status": "active",
  "company_uuid": "<company-uuid>",
  "timezone": "UTC",
  "country": "US"
}
```

**Database Table:** `users`
**Key Fields:**
- `uuid` (VARCHAR(191), UNIQUE, INDEX)
- `public_id` (VARCHAR(191), UNIQUE, INDEX)
- `email` (VARCHAR(255))
- `phone` (VARCHAR(255))
- `type` (VARCHAR(191), INDEX)
- `company_uuid` (VARCHAR(36), INDEX)

#### 2. Dispatcher User
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "user_<hex>",
  "name": "Test Dispatcher",
  "email": "dispatcher@test.techliv.net",
  "phone": "+1234567891",
  "type": "dispatcher",
  "status": "active"
}
```

#### 3. Driver Users
Two driver users are created, one for each driver record.

**API Endpoint:** `GET /int/v1/users`
**Response includes:** All user fields with relationships

---

## Companies

### Test Companies Created

#### 1. Test Company (Default)
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "comp_<hex>",
  "name": "Test Company",
  "description": "Test company for API testing",
  "phone": "+1234567890",
  "timezone": "UTC",
  "country": "US",
  "currency": "USD",
  "status": "active"
}
```

#### 2. Acme Logistics
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "comp_<hex>",
  "name": "Acme Logistics",
  "description": "Logistics company for testing",
  "phone": "+1987654321",
  "currency": "USD",
  "country": "US",
  "timezone": "America/New_York"
}
```

#### 3. Global Shipping Co
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "comp_<hex>",
  "name": "Global Shipping Co",
  "description": "International shipping company",
  "phone": "+1987654322",
  "currency": "EUR",
  "country": "DE",
  "timezone": "Europe/Berlin"
}
```

**Database Table:** `companies`
**Key Fields:**
- `uuid` (VARCHAR(191), UNIQUE, INDEX)
- `public_id` (VARCHAR(191), UNIQUE, INDEX)
- `name` (VARCHAR(255))
- `currency` (VARCHAR(10))
- `country` (VARCHAR(255))
- `timezone` (VARCHAR(255))

**API Endpoint:** `GET /int/v1/companies`
**Create Example:**
```bash
curl -X POST http://localhost:9001/int/v1/companies \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Test Company",
    "currency": "USD",
    "country": "US",
    "timezone": "UTC"
  }'
```

---

## Roles & Permissions

### Roles Created

#### 1. Fleet Manager Role
```json
{
  "id": "<generated-uuid>",
  "name": "fleet-manager",
  "guard_name": "web"
}
```

#### 2. Dispatcher Role
```json
{
  "id": "<generated-uuid>",
  "name": "dispatcher",
  "guard_name": "web"
}
```

#### 3. Driver Role
```json
{
  "id": "<generated-uuid>",
  "name": "driver",
  "guard_name": "web"
}
```

**Database Table:** `roles`
**Key Fields:**
- `id` (VARCHAR(36), PRIMARY KEY)
- `name` (VARCHAR(255))
- `guard_name` (VARCHAR(255))

### Permissions Created

1. `orders.create` - Create orders
2. `orders.view` - View orders
3. `orders.update` - Update orders
4. `drivers.manage` - Manage drivers
5. `vehicles.manage` - Manage vehicles

**Database Table:** `permissions`
**Key Fields:**
- `id` (VARCHAR(36), PRIMARY KEY)
- `name` (VARCHAR(255))
- `guard_name` (VARCHAR(255))

**Role-Permission Assignment:**
Roles and permissions are linked via `role_has_permissions` table:
- `role_id` (VARCHAR(36))
- `permission_id` (VARCHAR(36))

**API Endpoints:**
- `GET /int/v1/roles` - List all roles
- `POST /int/v1/roles` - Create role
- `GET /int/v1/permissions` - List all permissions

---

## Contacts

### Test Contacts Created

#### 1. John Doe (Customer)
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "contact_<hex>",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+1555123456",
  "type": "customer",
  "company_uuid": "<company-uuid>"
}
```

#### 2. Jane Smith (Vendor)
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "contact_<hex>",
  "name": "Jane Smith",
  "email": "jane.smith@example.com",
  "phone": "+1555123457",
  "type": "vendor",
  "company_uuid": "<company-uuid>"
}
```

**Database Table:** `contacts`
**Key Fields:**
- `uuid` (VARCHAR(191), UNIQUE, INDEX)
- `public_id` (VARCHAR(191), UNIQUE, INDEX)
- `name` (VARCHAR(255))
- `email` (VARCHAR(255))
- `phone` (VARCHAR(255))
- `type` (VARCHAR(255)) - "customer", "vendor", etc.
- `company_uuid` (VARCHAR(36), INDEX)

**API Endpoint:** `GET /fleetops/v1/contacts`
**Create Example:**
```bash
curl -X POST http://localhost:9001/fleetops/v1/contacts \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Contact",
    "email": "contact@example.com",
    "phone": "+1555999999",
    "type": "customer",
    "company_uuid": "<company-uuid>"
  }'
```

---

## Vendors

### Test Vendors Created

#### 1. Fast Fuel Co
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "vendor_<hex>",
  "name": "Fast Fuel Co",
  "email": "contact@fastfuel.com",
  "phone": "+1555987654",
  "company_uuid": "<company-uuid>"
}
```

#### 2. Quick Parts Supply
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "vendor_<hex>",
  "name": "Quick Parts Supply",
  "email": "sales@quickparts.com",
  "phone": "+1555987655",
  "company_uuid": "<company-uuid>"
}
```

**Database Table:** `vendors`
**Key Fields:**
- `uuid` (VARCHAR(191), UNIQUE, INDEX)
- `public_id` (VARCHAR(191), UNIQUE, INDEX)
- `name` (VARCHAR(255))
- `email` (VARCHAR(255))
- `phone` (VARCHAR(255))
- `company_uuid` (VARCHAR(36), INDEX)

**API Endpoint:** `GET /fleetops/v1/vendors`

---

## Places

### Test Places Created

#### 1. Main Warehouse
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "place_<hex>",
  "name": "Main Warehouse",
  "street1": "123 Main St",
  "city": "New York",
  "province": "NY",
  "postal_code": "10001",
  "country": "US",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "company_uuid": "<company-uuid>"
}
```

#### 2. Distribution Center
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "place_<hex>",
  "name": "Distribution Center",
  "street1": "456 Oak Ave",
  "city": "Los Angeles",
  "province": "CA",
  "postal_code": "90001",
  "country": "US",
  "latitude": 34.0522,
  "longitude": -118.2437,
  "company_uuid": "<company-uuid>"
}
```

**Database Table:** `places`
**Key Fields:**
- `uuid` (VARCHAR(191), UNIQUE, INDEX)
- `public_id` (VARCHAR(191), UNIQUE, INDEX)
- `name` (VARCHAR(255))
- `street1` (VARCHAR(255))
- `city` (VARCHAR(255))
- `province` (VARCHAR(255))
- `postal_code` (VARCHAR(255))
- `country` (VARCHAR(255))
- `latitude` (DECIMAL)
- `longitude` (DECIMAL)
- `company_uuid` (VARCHAR(36), INDEX)

**API Endpoint:** `GET /fleetops/v1/places`
**Create Example:**
```bash
curl -X POST http://localhost:9001/fleetops/v1/places \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Location",
    "street1": "789 Test St",
    "city": "Chicago",
    "province": "IL",
    "postal_code": "60601",
    "country": "US",
    "latitude": 41.8781,
    "longitude": -87.6298,
    "company_uuid": "<company-uuid>"
  }'
```

---

## Drivers

### Test Drivers Created

#### 1. Mike Johnson
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "driver_<hex>",
  "user_uuid": "<user-uuid>",
  "drivers_license_number": "DL123456",
  "status": "active",
  "company_uuid": "<company-uuid>"
}
```

**Associated User:**
```json
{
  "uuid": "<user-uuid>",
  "name": "Mike Johnson",
  "email": "mike.johnson@test.com",
  "phone": "+1555111111",
  "type": "driver"
}
```

#### 2. Sarah Williams
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "driver_<hex>",
  "user_uuid": "<user-uuid>",
  "drivers_license_number": "DL789012",
  "status": "active",
  "company_uuid": "<company-uuid>"
}
```

**Associated User:**
```json
{
  "uuid": "<user-uuid>",
  "name": "Sarah Williams",
  "email": "sarah.williams@test.com",
  "phone": "+1555222222",
  "type": "driver"
}
```

**Database Tables:**
- `drivers` - Driver-specific data
- `users` - Personal information (name, email, phone)

**Key Fields in `drivers`:**
- `uuid` (VARCHAR(191), INDEX)
- `public_id` (VARCHAR(191), INDEX)
- `user_uuid` (VARCHAR(36)) - Links to `users.uuid`
- `drivers_license_number` (VARCHAR(255))
- `status` (VARCHAR(191), INDEX)
- `company_uuid` (VARCHAR(36), INDEX)

**API Endpoint:** `GET /fleetops/v1/drivers`
**Create Example:**
```bash
curl -X POST http://localhost:9001/fleetops/v1/drivers \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Driver",
    "phone": "+1555333333",
    "email": "newdriver@test.com",
    "license_number": "DL-NEW-001",
    "company_uuid": "<company-uuid>"
  }'
```

**Note:** The API endpoint creates both a User and Driver record automatically.

---

## Vehicles

### Test Vehicles Created

#### 1. Delivery Van 1
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "vehicle_<hex>",
  "make": "Ford",
  "model": "Transit",
  "year": "2020",
  "vin": "1HGBH41JXMN109186",
  "plate_number": "ABC-1234",
  "type": "van",
  "status": "active",
  "company_uuid": "<company-uuid>"
}
```

#### 2. Delivery Truck 1
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "vehicle_<hex>",
  "make": "Ford",
  "model": "F-150",
  "year": "2021",
  "vin": "1FTFW1ET5DFC12345",
  "plate_number": "XYZ-5678",
  "type": "truck",
  "status": "active",
  "company_uuid": "<company-uuid>"
}
```

**Database Table:** `vehicles`
**Key Fields:**
- `uuid` (VARCHAR(191), INDEX)
- `public_id` (VARCHAR(191), INDEX)
- `make` (VARCHAR(191))
- `model` (VARCHAR(191))
- `year` (VARCHAR(191))
- `vin` (VARCHAR(255))
- `plate_number` (VARCHAR(255))
- `type` (VARCHAR(255))
- `status` (VARCHAR(255))
- `company_uuid` (VARCHAR(36), INDEX)

**Note:** Driver assignment is done via `Driver.vehicle_uuid`, not `Vehicle.driver_uuid`.

**API Endpoint:** `GET /fleetops/v1/vehicles`
**Create Example:**
```bash
curl -X POST http://localhost:9001/fleetops/v1/vehicles \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "make": "Toyota",
    "model": "Camry",
    "year": "2023",
    "vin": "4T1BF1FK5EU123456",
    "plate_number": "NEW-1234",
    "type": "sedan",
    "company_uuid": "<company-uuid>"
  }'
```

---

## Orders

### Test Orders Created

#### 1. Order ORD-001
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "order_<hex>",
  "internal_id": "ORD-001",
  "type": "delivery",
  "status": "pending",
  "dispatched": false,
  "started": false,
  "company_uuid": "<company-uuid>",
  "driver_assigned_uuid": "<driver-uuid>" (if driver exists)
}
```

#### 2. Order ORD-002
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "order_<hex>",
  "internal_id": "ORD-002",
  "type": "pickup",
  "status": "assigned",
  "dispatched": false,
  "started": false,
  "company_uuid": "<company-uuid>",
  "driver_assigned_uuid": "<driver-uuid>" (if driver exists)
}
```

**Database Table:** `orders`
**Key Fields:**
- `uuid` (VARCHAR(191), INDEX)
- `public_id` (VARCHAR(191), INDEX)
- `internal_id` (VARCHAR(255))
- `type` (VARCHAR(255)) - "delivery", "pickup", etc.
- `status` (VARCHAR(191), INDEX) - "pending", "assigned", "dispatched", "completed", etc.
- `dispatched` (BOOLEAN, DEFAULT FALSE)
- `started` (BOOLEAN, DEFAULT FALSE)
- `driver_assigned_uuid` (VARCHAR(36)) - Links to `drivers.uuid`
- `company_uuid` (VARCHAR(36), INDEX)

**API Endpoint:** `GET /fleetops/v1/orders`
**Create Example:**
```bash
curl -X POST http://localhost:9001/fleetops/v1/orders \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "internal_id": "ORD-003",
    "type": "delivery",
    "status": "pending",
    "company_uuid": "<company-uuid>"
  }'
```

---

## Service Rates

### Test Service Rate Created

#### Standard Delivery Rate
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "rate_<hex>",
  "service_name": "Standard Delivery",
  "service_type": "delivery",
  "base_fee": 500,
  "per_meter_flat_rate_fee": 10,
  "per_meter_unit": "m",
  "rate_calculation_method": "per_meter",
  "currency": "USD",
  "has_cod_fee": true,
  "cod_calculation_method": "flat",
  "cod_flat_fee": 200,
  "company_uuid": "<company-uuid>"
}
```

**Associated Rate Fee:**
```json
{
  "uuid": "<generated-uuid>",
  "service_rate_uuid": "<service-rate-uuid>",
  "distance": 1000,
  "distance_unit": "m",
  "fee": 1000,
  "currency": "USD"
}
```

**Database Tables:**
- `service_rates` - Main rate configuration
- `service_rate_fees` - Distance-based pricing tiers

**Key Fields in `service_rates`:**
- `uuid` (VARCHAR(191), UNIQUE, INDEX)
- `public_id` (VARCHAR(191), UNIQUE, INDEX)
- `service_name` (VARCHAR(255))
- `service_type` (VARCHAR(191), INDEX)
- `base_fee` (INTEGER) - In cents (500 = $5.00)
- `per_meter_flat_rate_fee` (INTEGER) - In cents per meter
- `per_meter_unit` (VARCHAR(50)) - "m" or "km"
- `rate_calculation_method` (VARCHAR(50)) - "per_meter", "fixed_meter", etc.
- `currency` (VARCHAR(10))
- `has_cod_fee` (BOOLEAN)
- `cod_flat_fee` (INTEGER) - In cents
- `company_uuid` (VARCHAR(36), INDEX)

**Key Fields in `service_rate_fees`:**
- `uuid` (VARCHAR(191), UNIQUE, INDEX)
- `service_rate_uuid` (VARCHAR(36), FOREIGN KEY → `service_rates.uuid`)
- `distance` (INTEGER) - Distance in meters/kilometers
- `distance_unit` (VARCHAR(50)) - "m" or "km"
- `fee` (INTEGER) - Fee in cents

**API Endpoint:** `GET /fleetops/v1/service-rates`
**Create Example:**
```bash
curl -X POST http://localhost:9001/fleetops/v1/service-rates \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "service_name": "Express Delivery",
    "service_type": "delivery",
    "base_fee": 1000,
    "per_meter_flat_rate_fee": 20,
    "per_meter_unit": "m",
    "rate_calculation_method": "per_meter",
    "currency": "USD",
    "company_uuid": "<company-uuid>"
  }'
```

**Pricing Calculation:**
- Base fee: $5.00 (500 cents)
- Per meter: $0.10 (10 cents per meter)
- COD fee: $2.00 (200 cents) if COD is selected
- Distance tier: $10.00 (1000 cents) for 1km (1000m)

---

## Devices

### Test Device Created

#### GPS Tracker 1
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "device_<hex>",
  "name": "GPS Tracker 1",
  "model": "GPS-2024",
  "manufacturer": "TechLiv",
  "type": "gps_tracker",
  "device_id": "GPS-001",
  "imei": "123456789012345",
  "status": "active",
  "online": true,
  "attachable_type": "App\\Models\\Vehicle",
  "attachable_uuid": "<vehicle-uuid>",
  "company_uuid": "<company-uuid>"
}
```

**Database Table:** `devices`
**Key Fields:**
- `uuid` (VARCHAR(191), UNIQUE, INDEX)
- `public_id` (VARCHAR(191), UNIQUE, INDEX)
- `name` (VARCHAR(255))
- `model` (VARCHAR(255))
- `manufacturer` (VARCHAR(255))
- `type` (VARCHAR(255))
- `device_id` (VARCHAR(255))
- `imei` (VARCHAR(255), INDEX)
- `status` (VARCHAR(255), INDEX)
- `online` (BOOLEAN)
- `attachable_type` (VARCHAR(255)) - Polymorphic relationship type
- `attachable_uuid` (VARCHAR(36)) - Polymorphic relationship UUID
- `company_uuid` (VARCHAR(36), INDEX)

**Polymorphic Relationships:**
Devices can be attached to different entity types:
- `attachable_type`: "App\\Models\\Vehicle", "App\\Models\\Driver", etc.
- `attachable_uuid`: UUID of the attached entity

**API Endpoint:** `GET /fleetops/v1/devices`
**Create Example:**
```bash
curl -X POST http://localhost:9001/fleetops/v1/devices \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New GPS Device",
    "model": "GPS-2025",
    "manufacturer": "TechLiv",
    "type": "gps_tracker",
    "device_id": "GPS-002",
    "imei": "987654321098765",
    "attachable_type": "App\\Models\\Vehicle",
    "attachable_uuid": "<vehicle-uuid>",
    "company_uuid": "<company-uuid>"
  }'
```

---

## Storefront Data

### Storefront Customers

#### Retail Customer
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "cust_<hex>",
  "name": "Retail Customer",
  "email": "customer@example.com",
  "phone": "+1555999999",
  "company_uuid": "<company-uuid>"
}
```

**Database Table:** `storefront_customers`
**Key Fields:**
- `uuid` (VARCHAR(191), UNIQUE, INDEX)
- `public_id` (VARCHAR(191), UNIQUE, INDEX)
- `name` (VARCHAR(255))
- `email` (VARCHAR(255))
- `phone` (VARCHAR(255))
- `company_uuid` (VARCHAR(36), INDEX)

**API Endpoint:** `GET /storefront/v1/customers`

### Storefront Products

#### Test Product
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "prod_<hex>",
  "name": "Test Product",
  "description": "A test product for API testing",
  "price": 1999,
  "sale_price": 1499,
  "is_on_sale": true,
  "currency": "USD",
  "sku": "PROD-001",
  "company_uuid": "<company-uuid>"
}
```

**Database Table:** `storefront_products`
**Key Fields:**
- `uuid` (VARCHAR(191), UNIQUE, INDEX)
- `public_id` (VARCHAR(191), UNIQUE, INDEX)
- `name` (VARCHAR(255))
- `description` (TEXT)
- `price` (INTEGER) - In cents (1999 = $19.99)
- `sale_price` (INTEGER) - In cents (1499 = $14.99)
- `is_on_sale` (BOOLEAN)
- `currency` (VARCHAR(10))
- `sku` (VARCHAR(255))
- `company_uuid` (VARCHAR(36), INDEX)

**API Endpoint:** `GET /storefront/v1/products`

### Storefront Carts

#### Test Cart
```json
{
  "uuid": "<generated-uuid>",
  "public_id": "cart_<hex>",
  "customer_uuid": "<customer-uuid>",
  "items": [
    {
      "product_uuid": "<product-uuid>",
      "quantity": 2,
      "price": 1999
    }
  ],
  "company_uuid": "<company-uuid>"
}
```

**Database Table:** `storefront_carts`
**Key Fields:**
- `uuid` (VARCHAR(191), UNIQUE, INDEX)
- `public_id` (VARCHAR(191), UNIQUE, INDEX)
- `customer_uuid` (VARCHAR(36), INDEX)
- `items` (JSON) - Array of cart items
- `company_uuid` (VARCHAR(36), INDEX)

**API Endpoint:** `GET /storefront/v1/carts`

---

## Using Test Data in API Calls

### Step 1: Get Authentication Token

```bash
# Login as manager
TOKEN=$(curl -s -X POST http://localhost:9001/int/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "identity": "manager@test.techliv.net",
    "password": "Test123"
  }' | jq -r '.token')

echo "Token: $TOKEN"
```

### Step 2: Get Company UUID

```bash
# Get bootstrap data to find company UUID
COMPANY_UUID=$(curl -s -X GET http://localhost:9001/int/v1/auth/bootstrap \
  -H "Authorization: Bearer $TOKEN" | jq -r '.organizations[0].uuid')

echo "Company UUID: $COMPANY_UUID"
```

### Step 3: Use Test Data in API Calls

#### Example: Create an Order

```bash
curl -X POST http://localhost:9001/fleetops/v1/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"internal_id\": \"ORD-TEST-001\",
    \"type\": \"delivery\",
    \"status\": \"pending\",
    \"company_uuid\": \"$COMPANY_UUID\"
  }"
```

#### Example: Get All Drivers

```bash
curl -X GET http://localhost:9001/fleetops/v1/drivers \
  -H "Authorization: Bearer $TOKEN"
```

#### Example: Get All Vehicles

```bash
curl -X GET http://localhost:9001/fleetops/v1/vehicles \
  -H "Authorization: Bearer $TOKEN"
```

### Step 4: Query Test Data from Database

```sql
-- Get all test users
SELECT uuid, email, name, type FROM users WHERE email LIKE '%test%';

-- Get all test companies
SELECT uuid, name, currency FROM companies WHERE name LIKE '%Test%' OR name LIKE '%Acme%' OR name LIKE '%Global%';

-- Get all drivers with their user info
SELECT d.uuid, d.drivers_license_number, u.name, u.email, u.phone
FROM drivers d
JOIN users u ON d.user_uuid = u.uuid;

-- Get all vehicles
SELECT uuid, make, model, year, plate_number FROM vehicles;

-- Get all orders
SELECT uuid, internal_id, type, status FROM orders;
```

---

## Data Relationships

### User → Company Relationship
- `users.company_uuid` → `companies.uuid`
- Also linked via `company_users` table:
  - `company_users.company_uuid` → `companies.uuid`
  - `company_users.user_uuid` → `users.uuid`

### Driver → User Relationship
- `drivers.user_uuid` → `users.uuid`
- Driver personal info (name, email, phone) stored in `users` table
- Driver-specific info (license number) stored in `drivers` table

### Driver → Vehicle Relationship
- `drivers.vehicle_uuid` → `vehicles.uuid`
- One driver can be assigned to one vehicle

### Device → Entity Relationship (Polymorphic)
- `devices.attachable_type` → Entity type (e.g., "App\\Models\\Vehicle")
- `devices.attachable_uuid` → Entity UUID
- Devices can attach to Vehicles, Drivers, or other entities

### Service Rate → Service Rate Fee Relationship
- `service_rate_fees.service_rate_uuid` → `service_rates.uuid`
- One service rate can have multiple rate fees (distance tiers)

### Order Relationships
- `orders.company_uuid` → `companies.uuid`
- `orders.driver_assigned_uuid` → `drivers.uuid`
- `orders.customer_uuid` → Can link to contacts or storefront customers

---

## Test Data File

The test data is saved to `test_data.json` in the project root. This file contains all UUIDs and references for easy lookup.

**File Location:** `fastapi-app/test_data.json`

**Example Structure:**
```json
{
  "users": [
    {
      "uuid": "user-uuid-1",
      "email": "manager@test.techliv.net",
      "password": "Test123",
      "name": "Test Manager"
    }
  ],
  "companies": [
    {
      "uuid": "company-uuid-1",
      "name": "Test Company",
      "public_id": "comp_abc123"
    }
  ],
  ...
}
```

---

## Quick Reference

### Most Common Test Data

| Entity | Count | Example UUID Field | Example Email/Name |
|--------|-------|-------------------|-------------------|
| Users | 3 | `users[0].uuid` | `manager@test.techliv.net` |
| Companies | 2 | `companies[0].uuid` | `Test Company` |
| Drivers | 2 | `drivers[0].uuid` | `mike.johnson@test.com` |
| Vehicles | 2 | `vehicles[0].uuid` | `Ford Transit` |
| Orders | 2 | `orders[0].uuid` | `ORD-001` |
| Contacts | 2 | `contacts[0].uuid` | `John Doe` |
| Vendors | 2 | `vendors[0].uuid` | `Fast Fuel Co` |
| Places | 2 | `places[0].uuid` | `Main Warehouse` |

### Authentication Tokens

All test users use password: `Test123` (except initial users which use `admin123` and `user123`)

### Database Validation

All test data has been validated to ensure:
- ✅ All required fields are present
- ✅ Data types match database schema
- ✅ Foreign key relationships are valid
- ✅ UUIDs are properly formatted
- ✅ Timestamps are in correct format
- ✅ Monetary values are in cents

---

## Support

For questions about test data:
- Check `test_data.json` for actual UUIDs
- Review model definitions in `app/models/`
- Check database schema in `alembic/versions/`
- Review API documentation in `API_TEST_DATA_DOCUMENTATION.md`

