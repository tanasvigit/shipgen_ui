import { test, expect } from '@playwright/test';

const email = process.env.E2E_EMAIL ?? 'admin@techliv.net';
const password = process.env.E2E_PASSWORD ?? 'admin123';

test.describe('ShipGen smoke', () => {
  test('login → dashboard → open vendors → logout', async ({ page }) => {
    test.setTimeout(60_000);

    await page.goto('/#/login');
    await expect(page.getByTestId('login-email')).toBeVisible();
    await page.getByTestId('login-email').fill(email);
    await page.getByTestId('login-password').fill(password);
    await page.getByTestId('login-submit').click();

    await expect(page).toHaveURL(/#\/(?!login)/, { timeout: 30_000 });

    await page.goto('/#/fleet/vendors');
    await expect(page.getByRole('heading', { name: 'Vendors' })).toBeVisible({ timeout: 15_000 });

    await page.getByTestId('logout').click();
    await expect(page).toHaveURL(/#\/login/, { timeout: 15_000 });
  });
});
