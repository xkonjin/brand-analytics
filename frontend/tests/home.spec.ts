/**
 * Home Page E2E Tests
 * 
 * Tests for the landing page with URL input form.
 */

import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display the page title and hero content', async ({ page }) => {
    // Check page has proper title
    await expect(page).toHaveTitle(/Brand Analytics/i);

    // Check hero headline is visible
    await expect(
      page.getByRole('heading', { name: /360° Audit/i })
    ).toBeVisible();

    // Check subheadline is visible
    await expect(
      page.getByText(/Analyze your SEO, social media/i)
    ).toBeVisible();
  });

  test('should display the URL input field', async ({ page }) => {
    // Check input placeholder
    const input = page.getByPlaceholder(/Enter your website URL/i);
    await expect(input).toBeVisible();
    await expect(input).toBeEnabled();
  });

  test('should display the analyze button', async ({ page }) => {
    const button = page.getByRole('button', { name: /Analyze Now/i });
    await expect(button).toBeVisible();
    await expect(button).toBeEnabled();
  });

  test('should display feature cards', async ({ page }) => {
    // Check all three feature cards are visible
    await expect(page.getByText('SEO & Performance')).toBeVisible();
    await expect(page.getByText('Brand & Messaging')).toBeVisible();
    await expect(page.getByText('Social & Engagement')).toBeVisible();
  });

  test('should display trust indicators', async ({ page }) => {
    await expect(page.getByText(/Free analysis/i)).toBeVisible();
    await expect(page.getByText(/No signup required/i)).toBeVisible();
  });

  test('should show error when submitting empty URL', async ({ page }) => {
    // Click submit without entering URL
    await page.getByRole('button', { name: /Analyze Now/i }).click();

    // Error message should appear
    await expect(page.getByText(/Please enter a website URL/i)).toBeVisible();
  });

  test('should accept URL input', async ({ page }) => {
    const input = page.getByPlaceholder(/Enter your website URL/i);
    
    // Type a URL
    await input.fill('example.com');
    
    // Verify input value
    await expect(input).toHaveValue('example.com');
  });

  test('should have proper form structure', async ({ page }) => {
    // Form should exist
    const form = page.locator('form');
    await expect(form).toBeVisible();

    // Form should contain input and button
    await expect(form.getByPlaceholder(/Enter your website URL/i)).toBeVisible();
    await expect(form.getByRole('button', { name: /Analyze Now/i })).toBeVisible();
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Core elements should still be visible
    await expect(
      page.getByRole('heading', { name: /360° Audit/i })
    ).toBeVisible();
    await expect(page.getByPlaceholder(/Enter your website URL/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /Analyze Now/i })).toBeVisible();
  });
});
