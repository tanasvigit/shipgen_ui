$ErrorActionPreference = "Stop"

# One-time backfill for legacy orders with NULL timestamps.
# Requires psql available in PATH and env vars set:
# POSTGRES_HOST, POSTGRES_USER, POSTGRES_DB, POSTGRES_PASSWORD

if (-not $env:POSTGRES_HOST) { throw "POSTGRES_HOST is not set" }
if (-not $env:POSTGRES_USER) { throw "POSTGRES_USER is not set" }
if (-not $env:POSTGRES_DB) { throw "POSTGRES_DB is not set" }
if (-not $env:POSTGRES_PASSWORD) { throw "POSTGRES_PASSWORD is not set" }

$sql = @"
BEGIN;
UPDATE orders SET created_at = NOW() WHERE created_at IS NULL;
UPDATE orders SET updated_at = NOW() WHERE updated_at IS NULL;
COMMIT;
"@

$env:PGPASSWORD = $env:POSTGRES_PASSWORD
psql -h $env:POSTGRES_HOST -U $env:POSTGRES_USER -d $env:POSTGRES_DB -v ON_ERROR_STOP=1 -c $sql

