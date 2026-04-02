import { test, expect, type Page } from '@playwright/test';

const email = process.env.E2E_EMAIL ?? 'admin@techliv.net';
const password = process.env.E2E_PASSWORD ?? 'admin123';

async function login(page: Page) {
  await page.goto('/#/login');
  await page.getByTestId('login-email').fill(email);
  await page.getByTestId('login-password').fill(password);
  await page.getByTestId('login-submit').click();
  await expect(page).toHaveURL(/#\/(?!login)/, { timeout: 30_000 });
}

test.describe('Fleet & vendor CRUD', () => {
  test('fleet create → update → delete', async ({ page }) => {
    test.setTimeout(120_000);
    const suffix = Date.now();
    const name = `E2E Fleet ${suffix}`;
    const renamed = `E2E Fleet ${suffix} updated`;

    await login(page);
    await page.goto('/#/fleet/fleets/create');
    await page.getByTestId('fleet-form-name').fill(name);
    await page.getByTestId('fleet-form-description').fill('e2e description');
    await page.getByTestId('fleet-form-submit').click();
    await expect(page).toHaveURL(/#\/fleet\/fleets/, { timeout: 30_000 });
    await expect(page.getByText(name, { exact: false })).toBeVisible({ timeout: 30_000 });

    const row = page.locator('tbody tr').filter({ hasText: name });
    await row.getByTestId(/^fleet-edit-/).click();
    await page.getByTestId('fleet-edit-name').fill(renamed);
    await page.getByTestId('fleet-edit-submit').click();
    await expect(page).toHaveURL(/#\/fleet\/fleets/, { timeout: 30_000 });

    const rowUpdated = page.locator('tbody tr').filter({ hasText: renamed });
    page.once('dialog', (d) => d.accept());
    await rowUpdated.getByTestId(/^fleet-delete-/).click();
    await expect(rowUpdated).toHaveCount(0, { timeout: 30_000 });
  });

  test('vendor create → update → delete', async ({ page }) => {
    test.setTimeout(120_000);
    const suffix = Date.now();
    const name = `E2E Vendor ${suffix}`;
    const renamed = `E2E Vendor ${suffix} renamed`;

    await login(page);
    await page.goto('/#/fleet/vendors/create');
    await page.getByTestId('vendor-create-name').fill(name);
    await page.getByTestId('vendor-create-submit').click();
    await expect(page).toHaveURL(/#\/fleet\/vendors\//, { timeout: 30_000 });

    await page.getByTestId('vendor-detail-edit').click();
    await page.getByTestId('vendor-page-edit-name').fill(renamed);
    await page.getByTestId('vendor-page-edit-submit').click();
    await expect(page).toHaveURL(/#\/fleet\/vendors\//, { timeout: 30_000 });
    await expect(page.getByText(renamed, { exact: false })).toBeVisible({ timeout: 15_000 });

    page.once('dialog', (d) => d.accept());
    await page.getByTestId('vendor-detail-delete').click();
    await expect(page.getByRole('heading', { name: 'Vendors' })).toBeVisible({ timeout: 30_000 });
  });
});
