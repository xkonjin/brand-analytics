/**
 * Analysis Flow E2E Tests
 * 
 * Tests for the analysis submission and progress tracking flow.
 * Uses API mocking to simulate backend responses.
 */

import { test, expect } from '@playwright/test';

test.describe('Analysis Flow', () => {
  test('should submit URL and navigate to analysis page', async ({ page }) => {
    // Mock the analyze API endpoint
    await page.route('**/api/v1/analyze', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'test-analysis-123',
          status: 'pending',
          url: 'https://example.com',
        }),
      });
    });

    // Go to home page
    await page.goto('/');

    // Fill in URL and submit
    await page.getByPlaceholder(/Enter your website URL/i).fill('example.com');
    await page.getByRole('button', { name: /Analyze Now/i }).click();

    // Should navigate to analysis page
    await expect(page).toHaveURL(/\/analyze\/test-analysis-123/);
  });

  test('should show loading state when submitting', async ({ page }) => {
    // Mock the API with a delay
    await page.route('**/api/v1/analyze', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'test-analysis-123',
          status: 'pending',
        }),
      });
    });

    await page.goto('/');
    await page.getByPlaceholder(/Enter your website URL/i).fill('example.com');
    await page.getByRole('button', { name: /Analyze Now/i }).click();

    // Should show loading state
    await expect(page.getByText(/Analyzing.../i)).toBeVisible();
  });

  test('should handle API error gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/api/v1/analyze', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Invalid URL provided',
        }),
      });
    });

    await page.goto('/');
    await page.getByPlaceholder(/Enter your website URL/i).fill('invalid');
    await page.getByRole('button', { name: /Analyze Now/i }).click();

    // Should show error message
    await expect(page.getByText(/Invalid URL provided/i)).toBeVisible();
  });

  test('should normalize URL without protocol', async ({ page }) => {
    let capturedBody: string | null = null;

    await page.route('**/api/v1/analyze', async (route) => {
      capturedBody = route.request().postData();
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'test-123',
          status: 'pending',
        }),
      });
    });

    await page.goto('/');
    await page.getByPlaceholder(/Enter your website URL/i).fill('example.com');
    await page.getByRole('button', { name: /Analyze Now/i }).click();

    // Verify URL was normalized with https://
    expect(capturedBody).toContain('https://example.com');
  });
});

test.describe('Analysis Progress Page', () => {
  test('should display progress UI elements', async ({ page }) => {
    // Mock the progress endpoint
    await page.route('**/api/v1/analysis/*/progress', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'test-123',
          status: 'processing',
          completion_percentage: 25,
          modules: {
            seo: 'completed',
            social_media: 'running',
            brand_messaging: 'pending',
            website_ux: 'pending',
            ai_discoverability: 'pending',
            content: 'pending',
            team_presence: 'pending',
            channel_fit: 'pending',
          },
        }),
      });
    });

    await page.goto('/analyze/test-123');

    // Should show analyzing header
    await expect(page.getByText(/Analyzing Your Brand/i)).toBeVisible();

    // Should show progress percentage
    await expect(page.getByText('25%')).toBeVisible();

    // Should show module statuses
    await expect(page.getByText('SEO Performance')).toBeVisible();
    await expect(page.getByText('Social Media')).toBeVisible();
  });

  test('should show completed module status', async ({ page }) => {
    await page.route('**/api/v1/analysis/*/progress', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'test-123',
          status: 'processing',
          completion_percentage: 50,
          modules: {
            seo: 'completed',
            social_media: 'completed',
            brand_messaging: 'running',
            website_ux: 'pending',
            ai_discoverability: 'pending',
            content: 'pending',
            team_presence: 'pending',
            channel_fit: 'pending',
          },
        }),
      });
    });

    await page.goto('/analyze/test-123');

    // Should show completed badges
    const completedBadges = page.locator('text=Completed');
    await expect(completedBadges.first()).toBeVisible();
  });

  test('should redirect to report when analysis completes', async ({ page }) => {
    let requestCount = 0;

    await page.route('**/api/v1/analysis/*/progress', async (route) => {
      requestCount++;

      // First request: processing, second request: completed
      const status = requestCount === 1 ? 'processing' : 'completed';
      const percentage = requestCount === 1 ? 50 : 100;

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'test-123',
          status,
          completion_percentage: percentage,
          modules: {
            seo: 'completed',
            social_media: 'completed',
            brand_messaging: 'completed',
            website_ux: 'completed',
            ai_discoverability: 'completed',
            content: 'completed',
            team_presence: 'completed',
            channel_fit: 'completed',
            scorecard: status === 'completed' ? 'completed' : 'running',
          },
        }),
      });
    });

    await page.goto('/analyze/test-123');

    // Wait for redirect to report page (with some timeout for the delay)
    await expect(page).toHaveURL(/\/report\/test-123/, { timeout: 10000 });
  });

  test('should show error state for failed analysis', async ({ page }) => {
    await page.route('**/api/v1/analysis/*/progress', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'test-123',
          status: 'failed',
          completion_percentage: 25,
          modules: {
            seo: 'completed',
            social_media: 'failed',
            brand_messaging: 'pending',
          },
        }),
      });
    });

    await page.goto('/analyze/test-123');

    // Should show failure message
    await expect(page.getByText(/Analysis failed/i)).toBeVisible();

    // Should show try again button
    await expect(page.getByRole('button', { name: /Try Again/i })).toBeVisible();
  });

  test('should handle non-existent analysis', async ({ page }) => {
    await page.route('**/api/v1/analysis/*/progress', async (route) => {
      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Analysis not found',
        }),
      });
    });

    await page.goto('/analyze/non-existent-id');

    // Should show error state
    await expect(page.getByText(/Analysis Not Found/i)).toBeVisible();

    // Should have button to start new analysis
    await expect(
      page.getByRole('button', { name: /Start New Analysis/i })
    ).toBeVisible();
  });
});
