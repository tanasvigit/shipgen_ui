# ShipGen Dashboard

React + TypeScript + Vite logistics operations dashboard. Connects to a ShipGen / FastAPI-style backend for auth, fleet, vendors, orders, and related modules.

## Prerequisites

- Node 18+  
- Backend API reachable from the browser (CORS configured for your dev origin)

## Setup

```bash
npm install
```

Create a local env file from the template:

```bash
cp .env.example .env
```

Edit `VITE_API_BASE_URL` to match your API origin (no trailing slash). Examples:

- `http://127.0.0.1:8000`
- `https://api.example.com/api`

## Scripts

| Command | Description |
|--------|-------------|
| `npm run dev` | Dev server (HMR) |
| `npm run build` | Production bundle |
| `npm run preview` | Serve `dist/` locally |
| `npm run lint` | ESLint |
| `npm run test:e2e` | Playwright (starts dev server; needs backend for login) |

## Production build

1. Set `VITE_API_BASE_URL` in the environment used by your CI or host (many platforms support “environment variables” in the build step).
2. Run `npm run build`.
3. Deploy the `dist/` folder as static assets (nginx, S3+CloudFront, Netlify, etc.).
4. Use **history-friendly** hosting or keep the app on hash routing (`/#/...`) as configured.

Do **not** set `VITE_DISABLE_AUTH=true` or `VITE_USE_MOCK_API=true` on public production deploys unless you intend that behavior.

## Manual QA checklist (pre-release)

- **Login** — valid credentials; invalid shows error; 2FA message if backend requires it.
- **Navigation** — sidebar / fleet / logistics sections load without console errors.
- **CRUD** — create → read → update → delete on at least one fleet module and one core entity you rely on (e.g. vendors).
- **Logout** — returns to login; protected routes redirect when unauthenticated.

Automated smoke: `npx playwright test` (see `e2e/`).

## Project docs

- Module integration patterns: `docs/module-integration-checklist.md`

## Backend maintenance (timestamps)

If you have legacy `orders` rows with `NULL created_at/updated_at`, date-based filters can exclude them.
Run the one-time backfill script in the backend repo:

- `fastapi-app/scripts/backfill_orders_timestamps.sql` (generic SQL)
- `fastapi-app/scripts/backfill_orders_timestamps.ps1` (PowerShell helper for Postgres + `psql`)
