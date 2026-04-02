## Dashboard Migration - Files to Copy

### Root-level files
- `App.tsx` (entire routing + ProtectedLayout + sidebar/header definitions)
- `index.css`, Tailwind config, icons referenced by dashboard
- `public/logo_logistic.png`, favicon (reuse until new asset available)

### Components (dashboard only)
- `components/Dashboard/*`
- `components/Orders/*`
- `components/Shipments/*`
- `components/Warehouse/*`
- `components/Fleet/*`
- `components/Billing/*`
- `components/Reports/*`
- `components/LiveOperations/*` (authenticated version)
- `components/Analytics.tsx`
- `components/AIAssistant.tsx` (dashboard AI module)
- `components/MasterData.tsx`
- `components/Logistics.tsx`
- `components/Warehouse.tsx`, `components/WarehouseManagement.tsx`
- `components/Billing.tsx`, `components/Billing/*`
- `components/Fleet.tsx`, `components/Fleet/*`
- `components/RoleGuard.tsx`
- `components/ui/*` (shared dashboard UI)
- `components/SubNavigation.tsx`
- `components/CreateShipmentModal.tsx`

### Utilities & State
- `services/api.ts`
- `services/mockData.ts`
- `services/stateManager.ts`
- Any other files under `services/`
- `constants/index.ts` (navigation definitions)
- `types/index.ts` (UserRole, etc.)
- `utils/roleAccess.ts`

### Supporting modules
- `components/Login.tsx` (dashboard entry before auth)
- `components/Dashboard.tsx` (legacy aggregator still used)
- `components/AIAssistant.tsx`
- `components/MasterData.tsx`
- `components/Fleet.tsx`, `components/Logistics.tsx`, etc. (top-level wrappers)

### Assets
- `/public/logo_logistic.png`
- `/public/customer-service.png` if referenced inside dashboard

> Note: Marketing-only components (Landing, Features, demos, builtFor, Contact, Navbar Footer default) stay in `logistics-ui` for now. Do **not** delete them until dashboard build succeeds independently.
