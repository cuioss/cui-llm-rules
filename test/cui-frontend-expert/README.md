# CUI Frontend Expert Test Suite

Test infrastructure for cui-frontend-expert bundle, specifically for the cui-npm-rules skill scripts.

## Structure

```
test/cui-frontend-expert/
├── mocks/                       # Mock npm/npx executables
│   ├── npm-success.sh          # Simulates successful test run
│   ├── npm-failure.sh          # Simulates test failures
│   ├── npm-lint-error.sh       # Simulates ESLint errors
│   ├── npx-playwright-success.sh  # Simulates successful Playwright tests
│   └── npx-playwright-failure.sh  # Simulates Playwright failures
├── fixtures/                    # Sample build output files
│   ├── sample-npm-success.log
│   ├── sample-npm-test-failure.log
│   ├── sample-npm-lint-errors.log
│   ├── sample-npm-compilation-error.log
│   ├── sample-npm-playwright-failure.log
│   └── sample-npm-dependency-error.log
├── test-execute-npm-build.sh   # Tests for execute-npm-build.py
├── test-parse-npm-output.sh    # Tests for parse-npm-output.py
└── run-all-tests.sh            # Run all test suites
```

## Running Tests

### Run All Tests

```bash
cd test/cui-frontend-expert
./run-all-tests.sh
```

### Run Individual Test Suites

```bash
# Test execute-npm-build.py
./test-execute-npm-build.sh

# Test parse-npm-output.py
./test-parse-npm-output.sh
```

## Test Coverage

### execute-npm-build.py Tests

1. ✅ Successful npm test execution
2. ✅ Failed npm test execution
3. ✅ npm command type detection
4. ✅ npx command type detection
5. ✅ Log file creation
6. ✅ Workspace parameter handling
7. ✅ Environment variables
8. ✅ Command execution timing
9. ✅ Timeout handling
10. ✅ [EXEC] output generation

### parse-npm-output.py Tests

1. ✅ Parse successful build
2. ✅ Parse test failures
3. ✅ Parse lint errors
4. ✅ Parse compilation errors
5. ✅ Parse Playwright failures
6. ✅ Parse dependency errors
7. ✅ Default mode output
8. ✅ Errors-only mode
9. ✅ File location extraction
10. ✅ Issue categorization accuracy
11. ✅ Lint error with line and column extraction
12. ✅ Multiple error types in single file

## Mock Scripts

Mock scripts simulate npm/npx behavior without requiring actual installations:

- **npm-success.sh** - Simulates successful Jest test run with passing tests
- **npm-failure.sh** - Simulates Jest test failures with error details
- **npm-lint-error.sh** - Simulates ESLint errors with file locations
- **npx-playwright-success.sh** - Simulates successful Playwright E2E tests
- **npx-playwright-failure.sh** - Simulates Playwright timeout and selector errors

## Fixture Files

Fixture files contain realistic npm/npx output for parser testing:

- **sample-npm-success.log** - Clean successful test run
- **sample-npm-test-failure.log** - Test failures with stack traces
- **sample-npm-lint-errors.log** - ESLint errors and warnings
- **sample-npm-compilation-error.log** - TypeScript compilation errors
- **sample-npm-playwright-failure.log** - Playwright timeout and selector errors
- **sample-npm-dependency-error.log** - Module not found errors

## Testing Pattern

Tests follow the builder-maven testing pattern:

1. **Setup** - Create temporary directory, set up PATH with mocks
2. **Execute** - Run script with test parameters
3. **Assert** - Verify output using assertion helpers
4. **Teardown** - Clean up temporary files

### Assertion Helpers

- `assert_equals` - Compare exact values
- `assert_contains` - Check substring presence
- `assert_json_field` - Extract and compare JSON field values
- `assert_file_exists` - Verify file creation
- `assert_json_greater_than` - Compare numeric JSON values

## Adding New Tests

To add a new test:

1. Create a test function following the pattern:
   ```bash
   test_feature_name() {
       # Setup test scenario
       # Execute script
       # Assert results
       return 0 or 1
   }
   ```

2. Register the test:
   ```bash
   run_test "Feature description" test_feature_name
   ```

3. If needed, add new mock scripts or fixtures

## Integration with CI/CD

These tests can be integrated into CI/CD pipelines:

```bash
# In CI/CD pipeline
cd test/cui-frontend-expert
./run-all-tests.sh
```

Exit codes:
- 0 - All tests passed
- 1 - One or more tests failed

## Comparison with builder-maven Tests

| Aspect | builder-maven | cui-frontend-expert |
|--------|-----------|---------------------|
| **Mock tool** | mvnw | npm/npx |
| **Mock scripts** | mvnw-success.sh, mvnw-failure.sh | npm-success.sh, npm-failure.sh, etc. |
| **Fixtures** | Maven build logs | npm/npx output logs |
| **Test pattern** | Bash with assertions | Same pattern |
| **Test runner** | Individual test scripts | run-all-tests.sh orchestrator |

## Notes

- Mock scripts use `exec` to replace the shell process for realistic simulation
- Tests run in isolated temporary directories
- PATH manipulation ensures mocks are used instead of real npm/npx
- Tests are completely self-contained - no real npm/npx installation needed
- All scripts are POSIX-compatible for cross-platform execution
