#!/bin/bash
# Mock npx playwright: Simulate successful E2E tests
# Used for testing execute-npm-build.py

# Simulate successful Playwright tests
cat << 'EOF'
Running 5 tests using 3 workers

  ✓  tests/login.spec.js:15:5 › should login successfully (1234ms)
  ✓  tests/login.spec.js:28:5 › should logout correctly (567ms)
  ✓  tests/dashboard.spec.js:10:5 › should display dashboard (890ms)
  ✓  tests/profile.spec.js:15:5 › should update profile (1122ms)
  ✓  tests/settings.spec.js:20:5 › should save settings (445ms)

  5 passed (4.3s)
EOF

exit 0
