#!/bin/bash
# Mock npm: Simulate successful test run
# Used for testing execute-npm-build.py

# Simulate a successful test run
cat << 'EOF'
> test-project@1.0.0 test
> jest

PASS  src/utils/validator.test.js
  ✓ validates email format (3ms)
  ✓ validates phone format (2ms)
  ✓ rejects invalid email (1ms)

PASS  src/components/Button.test.js
  ✓ renders button correctly (15ms)
  ✓ handles click events (5ms)
  ✓ supports disabled state (3ms)

Test Suites: 2 passed, 2 total
Tests:       6 passed, 6 total
Snapshots:   0 total
Time:        2.345 s
Ran all test suites.
EOF

exit 0
