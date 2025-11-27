# CUI Frontend Expert Test Data

Test fixtures and data files for cui-frontend-expert bundle.

> **Note**: The npm/npx build execution tests have been moved to `test/builder/`.

## Structure

```
test/cui-frontend-expert/
├── build/                     # Build analysis test data
├── coverage/                  # Coverage report test data
└── jsdoc/                     # JSDoc validation test data
```

## Test Data Directories

### build/

Test fixtures for build analysis:
- Build output logs for success/failure scenarios
- TOON format analysis files

### coverage/

Test fixtures for coverage analysis:
- Coverage summary JSON files
- LCOV coverage reports

### jsdoc/

Test fixtures for JSDoc validation:
- JavaScript files with various JSDoc states
- JSDoc violation reports

## Related Test Suites

For npm/npx build execution tests, see [test/builder/](../builder-npm/).
