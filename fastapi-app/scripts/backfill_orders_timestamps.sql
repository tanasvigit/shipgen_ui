-- One-time backfill for legacy orders with NULL timestamps.
-- Safe to run multiple times (only updates NULL fields).
--
-- Recommended: run during a maintenance window.

BEGIN;

UPDATE orders
SET created_at = NOW()
WHERE created_at IS NULL;

UPDATE orders
SET updated_at = NOW()
WHERE updated_at IS NULL;

COMMIT;

