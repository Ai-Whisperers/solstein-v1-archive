import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
    testDir: './e2e',
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    workers: process.env.CI ? 1 : undefined,
    reporter: 'html',

    use: {
        baseURL: 'http://localhost:3007',
        trace: 'on-first-retry',
    },

    projects: [
        {
            name: 'chromium',
            use: { ...devices['Desktop Chrome'] },
        },
    ],

    // Run the local web server before tests
    webServer: [
        {
            command: 'PORT=3007 npm run dev',
            url: 'http://localhost:3007',
            reuseExistingServer: !process.env.CI,
            timeout: 120 * 1000,
        },
        {
            command: 'cd ../ && ./venv/bin/python -m uvicorn solstein.api.main:app --port 8000',
            url: 'http://localhost:8000/health',
            reuseExistingServer: !process.env.CI,
            timeout: 120 * 1000,
        }
    ],
});
