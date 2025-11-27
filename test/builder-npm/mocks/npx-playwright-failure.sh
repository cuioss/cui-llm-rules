#!/bin/bash
# Mock npx playwright: Simulate E2E test failures
# Used for testing execute-npm-build.py

# Simulate Playwright test failures
cat << 'EOF'
Running 5 tests using 3 workers

  ✓  tests/login.spec.js:15:5 › should login successfully (1234ms)

  ✘  tests/login.spec.js:28:5 › should logout correctly (30245ms)

    Error: page.goto: Timeout 30000ms exceeded
    Call log:
      - navigating to "http://localhost:3000/logout", waiting until "load"

      25 |   test('should logout correctly', async ({ page }) => {
      26 |     await page.goto('/login');
    > 27 |     await page.goto('/logout');
         |               ^
      28 |   });

    at tests/login.spec.js:27:15

  ✓  tests/dashboard.spec.js:10:5 › should display dashboard (890ms)

  ✘  tests/profile.spec.js:15:5 › should update profile (5122ms)

    Error: locator.click: Timeout 5000ms exceeded
    Locator: button#save-profile

      15 |   test('should update profile', async ({ page }) => {
      16 |     await page.fill('#name', 'New Name');
    > 17 |     await page.click('#save-profile');
         |               ^
      18 |   });

    at tests/profile.spec.js:17:15

  ✓  tests/settings.spec.js:20:5 › should save settings (445ms)

  3 passed (7.8s)
  2 failed
EOF

exit 1
