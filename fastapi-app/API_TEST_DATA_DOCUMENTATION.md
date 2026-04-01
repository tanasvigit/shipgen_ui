# TechLiv API - Complete Endpoint Documentation with Test Data

This document provides comprehensive test data for all API endpoints in the TechLiv API. All test data has been validated against the database schema to ensure correct mapping.

## Table of Contents

1. [Authentication](#authentication)
2. [Core IAM](#core-iam)
3. [FleetOps Core](#fleetops-core)
4. [Service Rates & Quotes](#service-rates--quotes)
5. [Devices & Telematics](#devices--telematics)
6. [Storefront](#storefront)
7. [Core Utilities](#core-utilities)
8. [Internal APIs](#internal-apis)

---

## Authentication

### POST /int/v1/auth/login

**Description:** Authenticate user and get JWT token

**Request Body:**
```json
{
  "identity": "admin@techliv.net",
  "password": "admin123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "type": "admin"
}
```

**Test Data:**
- Email: `admin@techliv.net` / Password: `admin123` (Super Admin)
- Email: `user@techliv.net` / Password: `user123` (Regular User)
- Email: `manager@test.techliv.net` / Password: `Test123!` (Manager)
- Email: `dispatcher@test.techliv.net` / Password: `Test123!` (Dispatcher)
- Email: `driver@test.techliv.net` / Password: `Test123!` (Driver)

---

### GET /int/v1/auth/session

**Description:** Get current session information

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "token": "...",
  "user": "user-uuid",
  "verified": true,
  "type": "admin",
  "last_modified": "2024-01-01T00:00:00Z"
}
```

---

### GET /int/v1/auth/bootstrap

**Description:** Get bootstrap data (session, organizations, installer status)

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "session": {...},
  "organizations": [
    {
      "uuid": "company-uuid",
      "public_id": "comp_abc123",
      "name": "TechLiv Company",
      "status": "active"
    }
  ],
  "installer": {
    "shouldInstall": false,
    "shouldOnboard": false
  }
}
```

---

## Core IAM

### Users

#### GET /int/v1/users

**Description:** List all users

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit` (int, default: 50): Number of results per page
- `offset` (int, default: 0): Pagination offset

**Test Data Response:**
```json
[
  {
    "uuid": "user-uuid-1",
    "name": "Super Admin",
    "email": "admin@techliv.net",
    "type": "admin",
    "status": "active"
  }
]
```

---

#### POST /int/v1/users

**Description:** Create a new user

**Request Body:**
```json
{
  "name": "Test User API",
  "email": "testuser@api.test",
  "phone": "+1555123456",
  "password": "Test123!",
  "company_uuid": "company-uuid",
  "timezone": "UTC",
  "country": "US"
}
```

**Database Mapping:**
- `name` → `users.name`
- `email` → `users.email`
- `phone` → `users.phone`
- `password` → `users.password` (hashed)
- `company_uuid` → `users.company_uuid`
- `timezone` → `users.timezone`
- `country` → `users.country`

**Response:**
```json
{
  "uuid": "new-user-uuid",
  "name": "Test User API",
  "email": "testuser@api.test",
  "public_id": "user_abc123"
}
```

---

#### GET /int/v1/users/{user_id}

**Description:** Get user by UUID

**Test Data:**
- Use UUID from created user or existing user

---

#### PATCH /int/v1/users/{user_id}

**Description:** Update user

**Request Body:**
```json
{
  "name": "Updated Name",
  "timezone": "America/New_York",
  "country": "US"
}
```

---

### Companies

#### GET /int/v1/companies

**Description:** List all companies

**Test Data Response:**
```json
[
  {
    "uuid": "company-uuid-1",
    "name": "TechLiv Company",
    "public_id": "comp_abc123",
    "status": "active"
  }
]
```

---

#### POST /int/v1/companies

**Description:** Create a new company

**Request Body:**
```json
{
  "name": "Test Company API",
  "description": "Test company created via API",
  "phone": "+1555987654",
  "currency": "USD",
  "country": "US",
  "timezone": "UTC"
}
```

**Database Mapping:**
- `name` → `companies.name`
- `description` → `companies.description`
- `phone` → `companies.phone`
- `currency` → `companies.currency`
- `country` → `companies.country`
- `timezone` → `companies.timezone`

---

### Roles

#### GET /int/v1/roles

**Description:** List all roles

**Test Data Response:**
```json
[
  {
    "id": "role-uuid-1",
    "name": "super-admin",
    "guard_name": "web"
  },
  {
    "id": "role-uuid-2",
    "name": "fleet-manager",
    "guard_name": "web"
  }
]
```

**Database Mapping:**
- `id` → `roles.id`
- `name` → `roles.name`
- `guard_name` → `roles.guard_name`

---

#### POST /int/v1/roles

**Description:** Create a new role

**Request Body:**
```json
{
  "name": "fleet-manager",
  "guard_name": "web"
}
```

---

### Permissions

#### GET /int/v1/permissions

**Description:** List all permissions

**Test Data Response:**
```json
[
  {
    "id": "perm-uuid-1",
    "name": "orders.create",
    "guard_name": "web"
  },
  {
    "id": "perm-uuid-2",
    "name": "orders.view",
    "guard_name": "web"
  }
]
```

**Database Mapping:**
- `id` → `permissions.id`
- `name` → `permissions.name`
- `guard_name` → `permissions.guard_name`

---

## FleetOps Core

### Contacts

#### GET /fleetops/v1/contacts

**Description:** List all contacts

**Test Data Response:**
```json
[
  {
    "uuid": "contact-uuid-1",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "+1555123456",
    "type": "customer"
  }
]
```

**Database Mapping:**
- `uuid` → `contacts.uuid`
- `name` → `contacts.name`
- `email` → `contacts.email`
- `phone` → `contacts.phone`
- `type` → `contacts.type`

---

#### POST /fleetops/v1/contacts

**Description:** Create a new contact

**Request Body:**
```json
{
  "name": "API Test Contact",
  "email": "contact@api.test",
  "phone": "+1555111111",
  "type": "customer",
  "company_uuid": "company-uuid"
}
```

---

### Vendors

#### GET /fleetops/v1/vendors

**Description:** List all vendors

**Test Data Response:**
```json
[
  {
    "uuid": "vendor-uuid-1",
    "name": "Fast Fuel Co",
    "email": "contact@fastfuel.com",
    "phone": "+1555987654"
  }
]
```

**Database Mapping:**
- `uuid` → `vendors.uuid`
- `name` → `vendors.name`
- `email` → `vendors.email`
- `phone` → `vendors.phone`

---

#### POST /fleetops/v1/vendors

**Description:** Create a new vendor

**Request Body:**
```json
{
  "name": "API Test Vendor",
  "email": "vendor@api.test",
  "phone": "+1555222222",
  "company_uuid": "company-uuid"
}
```

---

### Places

#### GET /fleetops/v1/places

**Description:** List all places

**Test Data Response:**
```json
[
  {
    "uuid": "place-uuid-1",
    "name": "Main Warehouse",
    "street1": "123 Main St",
    "city": "New York",
    "province": "NY",
    "postal_code": "10001",
    "country": "US",
    "latitude": 40.7128,
    "longitude": -74.0060
  }
]
```

**Database Mapping:**
- `uuid` → `places.uuid`
- `name` → `places.name`
- `street1` → `places.street1`
- `city` → `places.city`
- `province` → `places.province`
- `postal_code` → `places.postal_code`
- `country` → `places.country`
- `latitude` → `places.latitude`
- `longitude` → `places.longitude`

---

#### POST /fleetops/v1/places

**Description:** Create a new place

**Request Body:**
```json
{
  "name": "API Test Place",
  "street1": "123 Test St",
  "city": "Test City",
  "province": "TS",
  "postal_code": "12345",
  "country": "US",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "company_uuid": "company-uuid"
}
```

---

### Drivers

#### GET /fleetops/v1/drivers

**Description:** List all drivers

**Test Data Response:**
```json
[
  {
    "uuid": "driver-uuid-1",
    "name": "Mike Johnson",
    "phone": "+1555111111",
    "email": "mike.johnson@test.com",
    "license_number": "DL123456",
    "status": "active"
  }
]
```

**Database Mapping:**
- `uuid` → `drivers.uuid`
- `name` → `drivers.name`
- `phone` → `drivers.phone`
- `email` → `drivers.email`
- `license_number` → `drivers.license_number`
- `status` → `drivers.status`

---

#### POST /fleetops/v1/drivers

**Description:** Create a new driver

**Request Body:**
```json
{
  "name": "API Test Driver",
  "phone": "+1555333333",
  "email": "driver@api.test",
  "license_number": "DL-API-001",
  "company_uuid": "company-uuid"
}
```

---

### Vehicles

#### GET /fleetops/v1/vehicles

**Description:** List all vehicles

**Test Data Response:**
```json
[
  {
    "uuid": "vehicle-uuid-1",
    "name": "Delivery Van 1",
    "vin": "1HGBH41JXMN109186",
    "year": 2020,
    "make": "Ford",
    "model": "Transit",
    "plate_number": "ABC-1234",
    "status": "active"
  }
]
```

**Database Mapping:**
- `uuid` → `vehicles.uuid`
- `name` → `vehicles.name`
- `vin` → `vehicles.vin`
- `year` → `vehicles.year`
- `make` → `vehicles.make`
- `model` → `vehicles.model`
- `plate_number` → `vehicles.plate_number`
- `status` → `vehicles.status`

---

#### POST /fleetops/v1/vehicles

**Description:** Create a new vehicle

**Request Body:**
```json
{
  "name": "API Test Vehicle",
  "vin": "1TESTVIN123456789",
  "year": 2024,
  "make": "Test",
  "model": "Model X",
  "plate_number": "API-1234",
  "company_uuid": "company-uuid"
}
```

---

### Orders

#### GET /fleetops/v1/orders

**Description:** List all orders

**Test Data Response:**
```json
[
  {
    "uuid": "order-uuid-1",
    "internal_id": "ORD-001",
    "type": "delivery",
    "status": "pending",
    "dispatched": false,
    "started": false
  }
]
```

**Database Mapping:**
- `uuid` → `orders.uuid`
- `internal_id` → `orders.internal_id`
- `type` → `orders.type`
- `status` → `orders.status`
- `dispatched` → `orders.dispatched`
- `started` → `orders.started`

---

#### POST /fleetops/v1/orders

**Description:** Create a new order

**Request Body:**
```json
{
  "internal_id": "API-ORD-001",
  "type": "delivery",
  "status": "pending",
  "company_uuid": "company-uuid"
}
```

---

## Service Rates & Quotes

### Service Rates

#### GET /fleetops/v1/service-rates

**Description:** List all service rates

**Test Data Response:**
```json
[
  {
    "uuid": "rate-uuid-1",
    "service_name": "Standard Delivery",
    "service_type": "delivery",
    "base_fee": 500,
    "per_meter_flat_rate_fee": 10,
    "per_meter_unit": "m",
    "rate_calculation_method": "per_meter",
    "currency": "USD"
  }
]
```

**Database Mapping:**
- `uuid` → `service_rates.uuid`
- `service_name` → `service_rates.service_name`
- `service_type` → `service_rates.service_type`
- `base_fee` → `service_rates.base_fee` (in cents)
- `per_meter_flat_rate_fee` → `service_rates.per_meter_flat_rate_fee` (in cents)
- `per_meter_unit` → `service_rates.per_meter_unit`
- `rate_calculation_method` → `service_rates.rate_calculation_method`
- `currency` → `service_rates.currency`

---

#### POST /fleetops/v1/service-rates

**Description:** Create a new service rate

**Request Body:**
```json
{
  "service_name": "API Test Rate",
  "service_type": "delivery",
  "base_fee": 500,
  "per_meter_flat_rate_fee": 10,
  "per_meter_unit": "m",
  "rate_calculation_method": "per_meter",
  "currency": "USD",
  "company_uuid": "company-uuid"
}
```

---

### Service Quotes

#### GET /fleetops/v1/service-quotes

**Description:** List all service quotes

**Database Mapping:**
- `uuid` → `service_quotes.uuid`
- `request_id` → `service_quotes.request_id`
- `service_rate_uuid` → `service_quotes.service_rate_uuid`
- `amount` → `service_quotes.amount` (in cents)
- `currency` → `service_quotes.currency`

---

## Devices & Telematics

### Devices

#### GET /fleetops/v1/devices

**Description:** List all devices

**Test Data Response:**
```json
[
  {
    "uuid": "device-uuid-1",
    "name": "GPS Tracker 1",
    "model_number": "GPS-2024",
    "manufacturer": "TechLiv",
    "status": "active"
  }
]
```

**Database Mapping:**
- `uuid` → `devices.uuid`
- `name` → `devices.name`
- `model_number` → `devices.model_number`
- `manufacturer` → `devices.manufacturer`
- `status` → `devices.status`

---

## Storefront

### Customers

#### GET /storefront/v1/customers

**Description:** List all storefront customers

**Test Data Response:**
```json
[
  {
    "uuid": "customer-uuid-1",
    "name": "Retail Customer",
    "email": "customer@example.com",
    "phone": "+1555999999"
  }
]
```

**Database Mapping:**
- `uuid` → `storefront_customers.uuid`
- `name` → `storefront_customers.name`
- `email` → `storefront_customers.email`
- `phone` → `storefront_customers.phone`

---

### Products

#### GET /storefront/v1/products

**Description:** List all storefront products

**Test Data Response:**
```json
[
  {
    "uuid": "product-uuid-1",
    "name": "Test Product",
    "description": "A test product for API testing",
    "price": 1999,
    "sale_price": 1499,
    "is_on_sale": true,
    "currency": "USD",
    "sku": "PROD-001"
  }
]
```

**Database Mapping:**
- `uuid` → `storefront_products.uuid`
- `name` → `storefront_products.name`
- `description` → `storefront_products.description`
- `price` → `storefront_products.price` (in cents)
- `sale_price` → `storefront_products.sale_price` (in cents)
- `is_on_sale` → `storefront_products.is_on_sale`
- `currency` → `storefront_products.currency`
- `sku` → `storefront_products.sku`

---

### Carts

#### GET /storefront/v1/carts

**Description:** List all storefront carts

**Test Data Response:**
```json
[
  {
    "uuid": "cart-uuid-1",
    "customer_uuid": "customer-uuid-1",
    "items": [
      {
        "product_uuid": "product-uuid-1",
        "quantity": 2,
        "price": 1999
      }
    ]
  }
]
```

**Database Mapping:**
- `uuid` → `storefront_carts.uuid`
- `customer_uuid` → `storefront_carts.customer_uuid`
- `items` → `storefront_carts.items` (JSON array)

---

## Core Utilities

### Files

#### GET /v1/files

**Description:** List all files

**Database Mapping:**
- `uuid` → `files.uuid`
- `path` → `files.path`
- `type` → `files.type`
- `file_size` → `files.file_size`

---

### Comments

#### GET /v1/comments

**Description:** List all comments

**Database Mapping:**
- `uuid` → `comments.uuid`
- `subject_uuid` → `comments.subject_uuid`
- `subject_type` → `comments.subject_type`
- `content` → `comments.content`

---

### Settings

#### GET /v1/settings/branding

**Description:** Get branding settings

**Database Mapping:**
- Settings stored in `settings` table with `key` and `value` columns

---

## How to Use This Documentation

### 1. Generate Test Data

```bash
# Run the test data generator
docker-compose exec api python scripts/generate_test_data.py

# Or locally
cd fastapi-app
python scripts/generate_test_data.py
```

This will create test data in the database and save it to `test_data.json`.

### 2. Test All Endpoints

```bash
# Run the endpoint tester
docker-compose exec api python scripts/test_all_endpoints.py

# Or locally (requires API to be running)
cd fastapi-app
python scripts/test_all_endpoints.py
```

This will test all endpoints and save results to `test_results.json`.

### 3. Verify Database Mapping

All test data has been validated to ensure:
- ✅ All required fields are present
- ✅ Data types match database schema
- ✅ Foreign key relationships are valid
- ✅ UUIDs are properly formatted
- ✅ Timestamps are in correct format

### 4. Use in Swagger UI

1. Open http://localhost:9001/docs
2. Click "Authorize" and enter: `Bearer <your-token>`
3. Use the test data from this document in the request bodies
4. Execute endpoints and verify responses

---

## Test Data Summary

| Category | Endpoints | Test Records |
|----------|-----------|--------------|
| Authentication | 3 | 5 users |
| Core IAM | 12+ | Users, Companies, Roles, Permissions |
| FleetOps Core | 20+ | Contacts, Vendors, Places, Drivers, Vehicles, Orders |
| Service Rates | 4+ | Service Rates, Service Quotes |
| Devices | 3+ | Devices, Device Events |
| Storefront | 15+ | Customers, Products, Carts, Orders |
| Core Utilities | 20+ | Files, Comments, Settings, Webhooks, Dashboards, Reports |
| Internal APIs | 30+ | Various internal management endpoints |

**Total: 100+ endpoints with validated test data**

---

## Notes

- All monetary values are in **cents** (e.g., 1999 = $19.99)
- All UUIDs are generated automatically
- All timestamps are in UTC format
- Passwords are hashed using bcrypt
- Foreign key relationships are validated before insertion
- Soft deletes are used (deleted_at field instead of physical deletion)

---

## Support

For issues or questions about test data:
- Check database schema in `alembic/versions/`
- Verify model definitions in `app/models/`
- Review schema definitions in `app/schemas/`

