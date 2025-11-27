#!/bin/bash
# Mock npm: Simulate test failures
# Used for testing execute-npm-build.py

# Simulate test failures
cat << 'EOF'
> test-project@1.0.0 test
> jest

FAIL  src/utils/validator.test.js
  ● validates email format

    expect(received).toBe(expected)

    Expected: true
    Received: false

      15 |   it('validates email format', () => {
      16 |     const result = validateEmail('test@example.com');
    > 17 |     expect(result).toBe(true);
         |                    ^
      18 |   });

    at Object.<anonymous> (src/utils/validator.test.js:17:20)

  ✘ validates email format (15ms)
  ✓ validates phone format (2ms)

PASS  src/components/Button.test.js
  ✓ renders button correctly (12ms)

Test Suites: 1 failed, 1 passed, 2 total
Tests:       1 failed, 2 passed, 3 total
Snapshots:   0 total
Time:        2.123 s
Ran all test suites.
EOF

exit 1
