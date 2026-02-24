import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
    await page.goto('/');

    // Expect a title "to contain" a substring.
    await expect(page).toHaveTitle(/Solstein/);
});

test('can view the attractiveness board', async ({ page }) => {
    await page.goto('/');

    // Wait for the main dashboard heading
    const heading = page.locator('h1').filter({ hasText: 'Solstein Attractiveness Board' });
    await expect(heading).toBeVisible();
});
