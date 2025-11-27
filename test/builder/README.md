# Builder Test Suite

Test infrastructure for the unified builder bundle.

## Structure

```
test/builder/
├── gradle/                    # Gradle build tool tests
│   ├── fixtures/             # Test fixtures
│   ├── mocks/               # Mock scripts
│   └── test-*.sh            # Test scripts
├── maven/                    # Maven build tool tests
│   ├── fixtures/            # Test fixtures
│   ├── mocks/              # Mock scripts
│   └── test-*.sh           # Test scripts
├── npm/                      # npm build tool tests
│   ├── fixtures/            # Test fixtures
│   ├── mocks/              # Mock scripts
│   └── test-*.sh           # Test scripts
└── run-all-tests.sh         # Run all test suites
```

## Running Tests

### Run All Tests

```bash
cd test/builder
./run-all-tests.sh
```

### Run Tests by Build Tool

```bash
# Gradle tests
cd test/builder/gradle
for test in test-*.sh; do bash "$test"; done

# Maven tests
cd test/builder/maven
for test in test-*.sh; do bash "$test"; done

# npm tests
cd test/builder/npm
for test in test-*.sh; do bash "$test"; done
```

### Run Individual Tests

```bash
# Example: Run Gradle parse output test
bash test/builder/gradle/test-parse-gradle-output.sh

# Example: Run Maven find module test
bash test/builder/maven/test-find-module-path.sh

# Example: Run npm execute build test
bash test/builder/npm/test-execute-npm-build.sh
```

## Test Coverage

### Gradle Tests

- `test-parse-gradle-output.sh` - Output parsing
- `test-execute-gradle-build.sh` - Build execution
- `test-find-gradle-project.sh` - Project detection
- `test-check-acceptable-warnings.sh` - Warning filtering
- `test-search-openrewrite-markers.sh` - OpenRewrite marker detection

### Maven Tests

- `test-parse-maven-output.sh` - Output parsing
- `test-execute-maven-build.sh` - Build execution
- `test-find-module-path.sh` - Module path resolution
- `test-check-acceptable-warnings.sh` - Warning filtering
- `test-search-openrewrite-markers.sh` - OpenRewrite marker detection

### npm Tests

- `test-parse-npm-output.sh` - Output parsing
- `test-execute-npm-build.sh` - Build execution

## Related

- Bundle: [marketplace/bundles/builder/](../../marketplace/bundles/builder/)
- Skills: builder-maven-rules, builder-gradle-rules, builder-npm-rules
