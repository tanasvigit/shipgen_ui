# Missing Features Analysis

Based on comparison with Laravel routes.php, here are the features still not implemented:

## 1. API Management
- **API Credentials** (`/int/v1/api-credentials`)
  - CRUD operations
  - `bulk-delete` endpoint
  - `roll/{id}` endpoint (roll API key)
  - `export` endpoint

- **API Events** (`/int/v1/api-events`)
  - CRUD operations
  - Model: ApiEvent

- **API Request Logs** (`/int/v1/api-request-logs`)
  - CRUD operations
  - Model: ApiRequestLog

## 2. Activity Logging
- **Activities** (`/int/v1/activities`)
  - CRUD operations
  - Model: Activity (extends Spatie ActivityLog)

## 3. Extensions System
- **Extensions** (`/int/v1/extensions`)
  - CRUD operations
  - Model: Extension
  - Related: ExtensionInstall

## 4. Custom Fields System
- **Custom Fields** (`/int/v1/custom-fields`)
  - CRUD operations
  - Model: CustomField

- **Custom Field Values** (`/int/v1/custom-field-values`)
  - CRUD operations
  - Model: CustomFieldValue

## 5. Transactions
- **Transactions** (`/int/v1/transactions`)
  - CRUD operations
  - Model: Transaction
  - Related: TransactionItem

## 6. Scheduling System
- **Schedules** (`/int/v1/schedules`)
  - CRUD operations
  - Model: Schedule

- **Schedule Items** (`/int/v1/schedule-items`)
  - CRUD operations
  - Model: ScheduleItem

- **Schedule Templates** (`/int/v1/schedule-templates`)
  - CRUD operations
  - Model: ScheduleTemplate

- **Schedule Availability** (`/int/v1/schedule-availability`)
  - CRUD operations
  - Model: ScheduleAvailability

- **Schedule Constraints** (`/int/v1/schedule-constraints`)
  - CRUD operations
  - Model: ScheduleConstraint

- **Schedule Monitor** (`/int/v1/schedule-monitor`)
  - `GET /tasks` endpoint
  - `GET /{id}/logs` endpoint

## 7. User Management
- **User Devices** (`/int/v1/user-devices`)
  - CRUD operations
  - Model: UserDevice

- **Groups** (`/int/v1/groups`)
  - CRUD operations
  - Model: Group
  - Related: GroupUser (pivot table)

## 8. Lookup/Utility Endpoints
- **Lookup** (`/int/v1/lookup/*`)
  - `GET /timezones`
  - `GET /whois`
  - `GET /currencies`
  - `GET /countries`
  - `GET /country/{code}`
  - `GET /techliv-blog`
  - `GET /font-awesome-icons`
  - `POST /refresh-blog-cache` (protected)

## 9. Installation/Setup
- **Installer** (`/int/v1/installer/*`)
  - `GET /initialize`
  - `POST /createdb`
  - `POST /migrate`
  - `POST /seed`

- **Onboard** (`/int/v1/onboard/*`)
  - `GET /should-onboard`
  - `POST /create-account`
  - `POST /verify-email`
  - `POST /send-verification-sms`
  - `POST /send-verification-email`

## 10. Organizations
- **Organizations** (`/v1/organizations`)
  - `GET /current` endpoint

## 11. Additional Settings Endpoints
- **Settings** (`/int/v1/settings/*`)
  - `GET /overview` (admin overview)
  - `GET /filesystem-config`
  - `POST /filesystem-config`
  - `POST /test-filesystem-config`
  - `GET /mail-config`
  - `POST /mail-config`
  - `POST /test-mail-config`
  - `GET /queue-config`
  - `POST /queue-config`
  - `POST /test-queue-config`
  - `GET /services-config`
  - `POST /services-config`
  - `POST /test-twilio-config`
  - `POST /test-sentry-config`
  - `POST /test-socket` (test SocketCluster)
  - `GET /notification-channels-config`
  - `POST /notification-channels-config`
  - `POST /test-notification-channels-config`

## 12. Additional Metrics Endpoints
- **Metrics** (`/int/v1/metrics/*`)
  - `GET /iam` endpoint
  - `GET /iam-dashboard` endpoint

## 13. Additional Report Endpoints
- **Reports** (`/int/v1/reports/*`)
  - `POST /validate-computed-column`
  - `POST /analyze-query`
  - `POST /export-query`
  - `GET /query-recommendations`
  - `GET /export-formats`

## 14. Additional Company Endpoints
- **Companies** (`/int/v1/companies/*`)
  - `GET /two-fa` (get 2FA settings)
  - `POST /two-fa` (save 2FA settings)
  - `POST /transfer-ownership`
  - `POST /leave` (leave organization)
  - `GET|POST /export`
  - `GET /{id}/users`

## 15. Additional User Endpoints
- **Users** (`/int/v1/users/*`)
  - `GET /me` (current user)
  - `GET|POST /export`
  - `PATCH /deactivate/{id}`
  - `PATCH /activate/{id}`
  - `PATCH /verify/{id}`
  - `DELETE /remove-from-company/{id}`
  - `DELETE /bulk-delete`
  - `POST /resend-invite`
  - `POST /set-password`
  - `POST /validate-password`
  - `POST /change-password`
  - `POST /locale` (set user locale)
  - `GET /locale` (get user locale)

## 16. Additional Two-FA Endpoints
- **Two-FA** (`/int/v1/two-fa/*`)
  - `POST /config` (save system config)
  - `GET /config` (get system config)
  - `GET /enforce` (should enforce 2FA)

## Summary
**Total Missing Modules: ~16 major modules**
**Total Missing Endpoints: ~50+ endpoints**

Most critical missing features:
1. API Credentials management
2. Activities/Activity Logging
3. Scheduling system (schedules, items, templates, availability, constraints)
4. Custom Fields system
5. Transactions
6. Extensions
7. Groups and User Devices
8. Lookup utilities
9. Installer/Onboard flows
10. Additional settings/config endpoints

