#!/bin/bash
# Mock npm: Simulate ESLint errors
# Used for testing execute-npm-build.py

# Simulate ESLint errors
cat << 'EOF'
> test-project@1.0.0 lint
> eslint src/

/path/to/src/components/Button.js
  15:3  error  'PropTypes' is defined but never used  no-unused-vars
  42:10 error  Unexpected console statement           no-console

/path/to/src/utils/helpers.js
  23:1  warning  Line exceeds 100 characters  max-len
  45:5  error    Missing return statement     consistent-return

✖ 4 problems (3 errors, 1 warning)
  2 errors and 0 warnings potentially fixable with the `--fix` option.
EOF

exit 1
