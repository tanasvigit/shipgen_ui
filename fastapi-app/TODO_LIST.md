# TODO List - ShipGen FastAPI Implementation

This document lists all TODO comments found in the codebase, organized by module.

## 📋 Table of Contents
1. [Lookup & Utility Endpoints](#lookup--utility-endpoints)
2. [Reports Module](#reports-module)
3. [Onboard Module](#onboard-module)
4. [Installer Module](#installer-module)
5. [File Management](#file-management)
6. [Storefront Orders (Internal)](#storefront-orders-internal)
7. [Storefront Orders (Public)](#storefront-orders-public)
8. [Storefront Customers](#storefront-customers)
9. [Chat & Messaging](#chat--messaging)
10. [Settings](#settings)
11. [Webhooks](#webhooks)
12. [Storefront Actions & Metrics](#storefront-actions--metrics)
13. [Schedule Monitor](#schedule-monitor)
14. [API Credentials](#api-credentials)
15. [Storefront Products](#storefront-products)
16. [Storefront Networks](#storefront-networks)

---

## 🔍 Lookup & Utility Endpoints

**File:** `app/api/v1/routers/lookup.py`

### 1. Timezones Endpoint
- **Line 19:** Use `pytz` or `zoneinfo` for full timezone list
- **Current:** Returns hardcoded list of common timezones
- **Action:** Implement comprehensive timezone list using Python timezone libraries

### 2. WHOIS Lookup
- **Line 41:** Implement actual WHOIS lookup
- **Current:** Returns stub response
- **Action:** Integrate with WHOIS library (e.g., `python-whois`)

### 3. Blog Feed Fetching
- **Line 163:** Implement actual blog feed fetching
- **Current:** Returns empty array
- **Action:** Fetch RSS/Atom feed from ShipGen blog

### 4. Blog Cache Refresh
- **Line 190:** Implement actual blog cache refresh
- **Current:** Returns stub response
- **Action:** Implement caching mechanism for blog feed

---

## 📊 Reports Module

**File:** `app/api/v1/routers/reports.py`

### 1. XLSX Export
- **Line 293:** Implement XLSX export using `openpyxl`
- **Current:** Returns error message about missing library
- **Action:** 
  - Add `openpyxl` to `requirements.txt`
  - Implement XLSX export functionality

---

## 🚀 Onboard Module

**File:** `app/api/v1/routers/onboard.py`

### 1. Onboarding Check
- **Line 35:** Implement actual onboarding check
- **Current:** Returns hardcoded `should_onboard: True`
- **Action:** Check if users exist in system, check company setup status

### 2. Account Creation
- **Line 47:** Implement actual account creation
- **Current:** Returns stub response
- **Action:** Create user, company, assign roles, send verification email

### 3. Email Verification
- **Line 60:** Implement actual email verification
- **Current:** Returns stub response
- **Action:** Verify verification code, mark email as verified

### 4. SMS Verification
- **Line 73:** Implement actual SMS verification
- **Current:** Returns stub response
- **Action:** Send SMS verification code, verify code

### 5. Email Verification Sending
- **Line 86:** Implement actual email verification sending
- **Current:** Returns stub response
- **Action:** Generate verification code, send email via SMTP

---

## 🛠️ Installer Module

**File:** `app/api/v1/routers/installer.py`

### 1. Initialization Check
- **Line 25:** Implement actual initialization check
- **Current:** Returns hardcoded values
- **Action:** Check database connection, migration status, seed status

### 2. Database Creation
- **Line 39:** Implement actual database creation
- **Current:** Returns stub response
- **Action:** Create PostgreSQL database programmatically

### 3. Migration Runner
- **Line 51:** Implement actual migration runner
- **Current:** Returns stub response
- **Action:** Run Alembic migrations programmatically

### 4. Database Seeding
- **Line 62:** Implement actual database seeding
- **Current:** Returns stub response
- **Action:** Seed initial data (roles, permissions, default settings)

---

## 📁 File Management

**Files:** 
- `app/api/v1/routers/files.py`
- `app/api/v1/routers/int_files.py`

### 1. File Download from Storage
- **Line 88 (files.py), Line 91 (int_files.py):** Implement actual file download from storage (S3, local, etc.)
- **Current:** Returns stub message
- **Action:** 
  - Implement S3 download (if using S3)
  - Implement local filesystem download
  - Return file stream with proper headers

### 2. File Upload to Storage
- **Line 124 (files.py), Line 126 (int_files.py):** Implement actual file upload to storage
- **Current:** Creates file record but doesn't store file
- **Action:** 
  - Implement S3 upload (if using S3)
  - Implement local filesystem upload
  - Store file metadata

### 3. Base64 File Upload
- **Line 124 (files.py), Line 148 (int_files.py):** Implement base64 file upload and storage
- **Current:** Creates file record but doesn't decode/store file
- **Action:** 
  - Decode base64 string
  - Store decoded file to storage
  - Update file record with actual path

---

## 🛒 Storefront Orders (Internal)

**File:** `app/api/v1/routers/int_storefront_orders.py`

### 1. Order Creation Schema
- **Line 12:** Define `OrderCreate` schema based on order creation requirements
- **Current:** Empty schema class
- **Action:** Define all required fields for storefront order creation

### 2. Order Update Schema
- **Line 15:** Define `OrderUpdate` schema based on order update requirements
- **Current:** Empty schema class
- **Action:** Define all fields that can be updated

### 3. Order Creation Logic
- **Line 61:** Implement order creation logic
- **Current:** Returns 501 Not Implemented
- **Action:** 
  - Create order from cart/checkout
  - Link to customer, store, products
  - Calculate totals
  - Create payment transaction

### 4. Order Update Logic
- **Line 81:** Implement order update logic
- **Current:** Basic field update only
- **Action:** 
  - Validate update permissions
  - Handle status transitions
  - Update related entities

### 5. Accept Order Logic
- **Line 128:** Implement `Storefront.patchOrderConfig` and `createAcceptedActivity`
- **Current:** Only updates status
- **Action:** 
  - Update order configuration
  - Create activity log entry
  - Send notifications

### 6. Mark Order as Ready Logic
- **Line 161:** Implement full logic including pickup handling, adhoc toggle, driver assignment
- **Current:** Basic status update
- **Action:** 
  - Handle pickup vs delivery
  - Toggle adhoc flag
  - Assign driver if provided
  - Update order configuration

### 7. Driver Assignment
- **Line 167:** Assign driver if provided
- **Current:** Comment only
- **Action:** Link driver to order, update order status

### 8. Mark Order as Preparing Logic
- **Line 196:** Implement `Storefront.patchOrderConfig` and activity insertion
- **Current:** Only updates status
- **Action:** 
  - Update order configuration
  - Create activity log entry

### 9. Mark Order as Completed Logic
- **Line 224:** Implement `Storefront.patchOrderConfig`
- **Current:** Only updates status
- **Action:** 
  - Update order configuration
  - Finalize payment
  - Create completion activity

---

## 🛍️ Storefront Orders (Public)

**File:** `app/api/v1/routers/storefront_orders.py`

### 1. Storefront Token Extraction
- **Line 17:** Implement storefront token extraction
- **Current:** Returns `None`
- **Action:** 
  - Extract token from Authorization header
  - Validate token
  - Return customer object

### 2. Get Customer from Token (Complete Pickup)
- **Line 27:** Get customer from token
- **Current:** Commented out
- **Action:** Use `_get_current_customer()` helper

### 3. Verify Customer Owns Order (Complete Pickup)
- **Line 43:** Verify customer owns this order
- **Current:** Commented out
- **Action:** Check `order_obj.customer_uuid == customer.uuid`

### 4. Get Customer from Token (Receipt)
- **Line 65:** Get customer from token
- **Current:** Commented out
- **Action:** Use `_get_current_customer()` helper

### 5. Verify Customer Owns Order (Receipt)
- **Line 81:** Verify customer owns this order
- **Current:** Commented out
- **Action:** Check `order_obj.customer_uuid == customer.uuid`

---

## 👥 Storefront Customers

**File:** `app/api/v1/routers/storefront_customers.py`

### 1. Storefront Token Extraction
- **Line 27:** Implement storefront token extraction
- **Current:** Returns `None`
- **Action:** 
  - Extract token from Authorization header
  - Validate token
  - Return customer object

---

## 💬 Chat & Messaging

**Files:**
- `app/api/v1/routers/chat_channels.py`
- `app/api/v1/routers/chat_messages.py`
- `app/api/v1/routers/int_chat_channels.py`

### 1. Notify Other Participants (Chat Channels)
- **Line 200 (chat_channels.py):** Notify other participants when message is sent
- **Current:** No notification
- **Action:** Send push notifications/websocket messages to channel participants

### 2. Notify Other Participants (Chat Messages)
- **Line 97 (chat_messages.py):** Notify other participants when message is sent
- **Current:** No notification
- **Action:** Send push notifications/websocket messages to channel participants

### 3. Unread Count Calculation (Channel)
- **Line 139 (int_chat_channels.py):** Implement unread count calculation
- **Current:** Returns 0
- **Action:** 
  - Query `ChatReceipt` table
  - Count unread messages for user in channel

### 4. Total Unread Count Calculation
- **Line 148 (int_chat_channels.py):** Implement total unread count calculation
- **Current:** Returns 0
- **Action:** 
  - Query all channels user participates in
  - Sum unread counts across all channels

---

## ⚙️ Settings

**File:** `app/api/v1/routers/settings.py`

### 1. Branding Settings Retrieval
- **Line 94:** Implement full branding settings retrieval
- **Current:** Returns hardcoded values
- **Action:** 
  - Query `settings` table for branding keys
  - Return icon_url, logo_url, theme, etc.

### 2. Branding Settings Save
- **Line 109:** Implement full branding settings save
- **Current:** Returns stub response
- **Action:** 
  - Save branding settings to `settings` table
  - Handle file uploads for icon/logo
  - Update company branding metadata

---

## 🔗 Webhooks

**File:** `app/api/v1/routers/webhook_endpoints.py`

### 1. Available Webhook Events
- **Line 185:** Return available webhook events from config
- **Current:** Returns empty array
- **Action:** 
  - Define webhook event types
  - Return from configuration or database

### 2. Available Webhook Versions
- **Line 194:** Return available webhook versions
- **Current:** Returns empty array
- **Action:** 
  - Define supported webhook API versions
  - Return from configuration

---

## 📈 Storefront Actions & Metrics

**Files:**
- `app/api/v1/routers/int_storefront_actions.py`
- `app/api/v1/routers/int_storefront_metrics.py`

### 1. Push Notification Sending
- **Line 171 (int_storefront_actions.py):** Implement actual push notification sending
- **Current:** Returns success without sending
- **Action:** 
  - Integrate with FCM/APNS
  - Send push notifications to customer devices
  - Handle delivery status

### 2. Full Metrics Calculation
- **Line 22 (int_storefront_metrics.py):** Implement full metrics calculation using Metrics service
- **Current:** Returns stub structure
- **Action:** 
  - Implement `Metrics.forCompany()` equivalent
  - Calculate order metrics, revenue, customer counts
  - Support date range filtering

---

## ⏰ Schedule Monitor

**File:** `app/api/v1/routers/schedule_monitor.py`

### 1. Schedule Monitor Tasks
- **Line 18:** Implement actual schedule monitor tasks
- **Current:** Returns empty array
- **Action:** 
  - Query scheduled tasks from `schedules` table
  - Return task status, next run times, last execution

### 2. Schedule Monitor Logs
- **Line 31:** Implement actual schedule monitor logs
- **Current:** Returns empty array
- **Action:** 
  - Query execution logs for specific scheduled task
  - Return execution history, errors, durations

---

## 🔑 API Credentials

**File:** `app/api/v1/routers/api_credentials.py`

### 1. Export Logic
- **Line 210:** Implement actual export logic
- **Current:** Returns stub response
- **Action:** 
  - Export API credentials to CSV/JSON
  - Include secret keys (masked) and metadata

---

## 🏪 Storefront Products

**File:** `app/api/v1/routers/int_storefront_products.py`

### 1. Import Processing Logic
- **Line 152:** Implement full import processing logic from Laravel
- **Current:** Basic stub
- **Action:** 
  - Parse CSV/Excel file
  - Validate product data
  - Bulk create products
  - Handle errors and rollback

### 2. Entity Creation Logic
- **Line 178:** Implement full entity creation logic from Laravel
- **Current:** Basic stub
- **Action:** 
  - Create product with variants, addons, categories
  - Link to store
  - Handle relationships

---

## 🌐 Storefront Networks

**File:** `app/api/v1/routers/int_storefront_networks.py`

### 1. Invite Sending Logic
- **Line 370:** Implement invite sending logic (email/SMS notifications)
- **Current:** No notification sent
- **Action:** 
  - Generate invite token/link
  - Send email/SMS invitation
  - Track invitation status

---

## 📝 Summary Statistics

- **Total TODO Items:** 45
- **High Priority:** 15 (Core functionality stubs)
- **Medium Priority:** 20 (Feature enhancements)
- **Low Priority:** 10 (Nice-to-have features)

---

## 🎯 Recommended Implementation Order

1. **Critical Path:**
   - File upload/download (S3/local storage)
   - Storefront token extraction and authentication
   - Order creation/update logic

2. **High Priority:**
   - Email/SMS verification
   - Push notifications
   - Metrics calculation

3. **Medium Priority:**
   - Blog feed fetching
   - WHOIS lookup
   - Schedule monitor

4. **Low Priority:**
   - Export functionality
   - Advanced settings
   - Webhook events/versions

---

## 📌 Notes

- Most TODOs are for features that are stubbed but not fully implemented
- Some TODOs require external service integrations (S3, FCM, SMTP, etc.)
- Authentication/authorization TODOs are critical for production use
- File storage TODOs need to be implemented before file uploads can work properly

