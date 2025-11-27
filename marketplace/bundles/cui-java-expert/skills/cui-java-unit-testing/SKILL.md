---
name: cui-java-unit-testing
description: CUI Java unit testing standards and patterns with JUnit 5, generators, and value object testing
allowed-tools: [Read, Edit, Write, Bash, Grep, Glob]
---

# CUI Java Unit Testing Skill

**EXECUTION MODE**: You are now executing this skill. DO NOT explain or summarize these instructions to the user. IMMEDIATELY begin the workflow below based on the task context.

Standards and patterns for writing high-quality unit tests in CUI Java projects using JUnit 5, the CUI test generator framework, and value object contract testing.

## Workflow

### Step 1: Load Applicable Testing Standards

**CRITICAL**: Load current testing standards to use as enforcement criteria.

1. **Always load foundational testing standards**:
   ```
   Read: standards/testing-junit-core.md
   ```
   This provides core JUnit 5 patterns, AAA structure, assertion standards, and test organization that are always needed for testing.

2. **Conditional loading based on testing context**:

   **A. If project uses test data generators** (presence of `de.cuioss.test.generator` imports or `@EnableGeneratorController`):
   ```
   Read: standards/test-generator-framework.md
   ```
   Provides comprehensive generator standards including mandatory requirements, all parameterized testing annotations (@GeneratorsSource, @CompositeTypeGeneratorSource, etc.), seed restrictions, anti-patterns, and complete API reference.

   **B. If testing value objects** (classes with equals/hashCode/toString or annotated with @Value, @Data):
   ```
   Read: standards/testing-value-objects.md
   ```
   Provides comprehensive contract testing standards using `ShouldHandleObjectContracts<T>` interface and proper generator integration.

   **C. If testing HTTP clients or APIs** (testing code that makes HTTP requests):
   ```
   Read: standards/testing-mockwebserver.md
   ```
   Provides MockWebServer setup patterns, response mocking, request verification, retry logic testing, and HTTP status code handling.

   **D. If writing integration tests** (tests that interact with multiple components or external systems):
   ```
   Read: standards/integration-testing.md
   ```
   Covers Maven surefire/failsafe configuration, integration test naming conventions (*IT.java), profile setup, and CI/CD integration.

   **E. If testing applications that use Java Util Logging (JUL)** (testing code that uses `java.util.logging` or needs to assert log output):
   ```
   Read: standards/testing-juli-logger.md
   ```
   Provides patterns for configuring test loggers with `@EnableTestLogger`, asserting log statements with `LogAsserts`, and dynamically changing log levels in tests.

   **F. If focusing on test quality or reviewing existing tests** (improving test quality, eliminating AI-generated artifacts, or ensuring compliance):
   ```
   Read: standards/testing-quality-standards.md
   ```
   Provides quality best practices including AI-generated code detection, parameterized test guidelines, assertion message standards, SonarQube compliance, library migration guidelines, and coverage requirements.

   **G. If performing test maintenance or refactoring** (maintaining or improving existing test code quality):
   ```
   Read: standards/testing-maintenance-reference.md
   ```
   Use when: Maintaining or improving existing test code. Provides detection criteria for forbidden test anti-patterns (conditional logic, Optional.orElse(), try-catch blocks), maintenance-specific testing requirements, unit test focus guidelines, value object testing criteria, test enhancement prioritization, common mistakes to avoid, and troubleshooting guide for test quality issues. Different from testing-quality-standards.md which focuses on writing NEW tests.

3. **Extract key requirements from all loaded standards**

4. **Store in working memory** for use during task execution

### Step 2: Analyze Existing Tests (if applicable)

If working with existing tests:

1. **Identify current test structure**:
   - Check test class organization and naming
   - Review test method structure (AAA pattern compliance)
   - Examine assertion usage and messages
   - Identify parameterized test opportunities

2. **Assess CUI framework compliance**:
   - Verify `@EnableGeneratorController` usage where needed
   - Check for prohibited libraries (Mockito, Hamcrest, PowerMock)
   - Validate generator usage for all test data
   - Confirm value object contract testing where applicable

3. **Review test quality**:
   - Check assertion message quality (meaningful, concise)
   - Verify test independence and isolation
   - Assess test naming and @DisplayName usage
   - Identify potential test consolidation opportunities
   - Detect AI-generated code artifacts (see testing-quality-standards.md for indicators)

### Step 3: Write/Modify Tests According to Standards

When writing or modifying tests:

1. **Apply core JUnit 5 standards**:
   - Use AAA pattern (Arrange-Act-Assert)
   - Include meaningful assertion messages (20-60 characters)
   - Use @DisplayName for readable test descriptions
   - Follow test independence principles
   - Apply proper exception testing with assertThrows

2. **Use CUI test generator for all data** (if applicable):
   - Add @EnableGeneratorController to test classes
   - Replace manual data creation with Generators.* calls
   - Use @GeneratorsSource for parameterized tests (3+ similar variants)
   - Never commit @GeneratorSeed annotations (debugging only)
   - Combine generators for complex object creation

3. **Implement value object contract testing** (if applicable):
   - Apply ShouldHandleObjectContracts<T> interface
   - Implement getUnderTest() using generators
   - Verify equals/hashCode/toString contracts
   - Separate contract tests from business logic tests

4. **Configure HTTP mocking** (if applicable):
   - Use @EnableMockWebServer annotation
   - Enqueue mock responses before requests
   - Verify request headers, body, and parameters
   - Test various status codes and error scenarios
   - Combine with generators for comprehensive testing

5. **Set up integration tests** (if applicable):
   - Name tests with *IT.java or *ITCase.java suffix
   - Configure Maven failsafe plugin
   - Create integration-tests profile
   - Ensure proper test separation

### Step 4: Verify Test Quality

Before completing the task:

1. **Verify standards compliance**:
   - [ ] All tests follow AAA pattern
   - [ ] All assertions have meaningful messages
   - [ ] Test independence verified (tests don't depend on each other)
   - [ ] Proper @DisplayName usage
   - [ ] No prohibited libraries used

2. **Verify CUI framework usage** (if applicable):
   - [ ] @EnableGeneratorController present where needed
   - [ ] All test data uses Generators.* (no manual creation)
   - [ ] No @GeneratorSeed annotations committed
   - [ ] Value object contracts implemented correctly
   - [ ] MockWebServer setup follows patterns

3. **Check coverage requirements**:
   - Minimum 80% line coverage
   - Minimum 80% branch coverage
   - Critical paths have 100% coverage
   - All public APIs tested

### Step 5: Report Results

Provide summary of:

1. **Tests created/modified**: List test classes and methods
2. **Standards applied**: Which standards were followed
3. **Framework features used**: Generators, value object contracts, MockWebServer, etc.
4. **Coverage metrics**: Current coverage percentages
5. **Any deviations**: Document and justify any standard deviations

## Quality Verification

### Test Execution Checklist

- [ ] All new/modified tests pass
- [ ] Tests are independent (can run in any order)
- [ ] No flaky tests (consistent results)
- [ ] Fast execution (unit tests < 1 second each)
- [ ] Proper cleanup in @AfterEach if needed

### Code Quality Checklist

- [ ] No hardcoded test data (use generators)
- [ ] No prohibited testing libraries
- [ ] Assertion messages are meaningful and concise
- [ ] Test names clearly describe behavior
- [ ] No commented-out code
- [ ] No @GeneratorSeed annotations

### Coverage Verification

- [ ] Generate coverage using builder:builder-maven-rules workflow with jacoco
- [ ] Coverage meets minimum requirements (80% line/branch)
- [ ] Critical paths have 100% coverage
- [ ] No coverage regressions from previous state

## Common Patterns and Examples

### Basic Unit Test Pattern

```java
@EnableGeneratorController
@DisplayName("Token Validator Tests")
class TokenValidatorTest {

    @Test
    @DisplayName("Should validate token with correct issuer")
    void shouldValidateTokenWithCorrectIssuer() {
        // Arrange
        String issuer = Generators.strings().next();
        Token token = createTokenWithIssuer(issuer);
        TokenValidator validator = new TokenValidator(issuer);

        // Act
        ValidationResult result = validator.validate(token);

        // Assert
        assertTrue(result.isValid(), "Token with correct issuer should be valid");
    }
}
```

### Value Object Contract Test Pattern

```java
@EnableGeneratorController
class UserDataTest implements ShouldHandleObjectContracts<UserData> {

    @Override
    public UserData getUnderTest() {
        return UserData.builder()
            .username(Generators.strings().next())
            .email(Generators.emailAddress().next())
            .age(Generators.integers(18, 100).next())
            .build();
    }
}
```

### Parameterized Test Pattern

```java
@EnableGeneratorController
class ParameterizedValidationTest {

    @ParameterizedTest
    @DisplayName("Should validate various email formats")
    @GeneratorsSource(generator = GeneratorType.DOMAIN_EMAIL, count = 5)
    void shouldValidateEmailFormats(String email) {
        assertTrue(validator.isValidEmail(email),
            "Generated email should be valid");
    }
}
```

### HTTP Testing Pattern

```java
@EnableMockWebServer
@EnableGeneratorController
class HttpClientTest {

    @InjectMockWebServer
    private MockWebServerHolder serverHolder;

    @Test
    @DisplayName("Should successfully fetch user data")
    void shouldFetchUserData() throws Exception {
        // Arrange
        String userName = Generators.strings().next();
        serverHolder.enqueue(new MockResponse()
            .setResponseCode(200)
            .setBody(String.format("{\"name\": \"%s\"}", userName)));

        // Act
        User user = client.getUser(serverHolder.getBaseUrl(), 1);

        // Assert
        assertNotNull(user, "Response should not be null");
        assertEquals(userName, user.getName(), "User name should match");
    }
}
```

## Error Handling

If encountering issues:

1. **Test failures**: Review assertion messages and debug failing tests
2. **Coverage gaps**: Identify untested code paths and add tests
3. **Framework errors**: Verify @EnableGeneratorController and dependencies
4. **Maven build issues**: Check surefire/failsafe configuration
5. **Integration test problems**: Verify profile configuration and naming conventions

---

## Workflow: Analyze Coverage

Analyze existing JaCoCo coverage reports and extract coverage metrics.

### Parameters

- **report_path** (required): Path to JaCoCo XML report or directory containing reports
- **threshold** (optional): Coverage threshold for low-coverage detection (default: 80%)

### Steps

1. **Locate Coverage Reports**
   ```
   Glob: pattern="{report_path}/**/jacoco.xml"
   ```
   Or use provided file path directly.

2. **Resolve Script Path**
   ```
   Skill: cui-utilities:script-runner
   Resolve: cui-java-expert:cui-java-unit-testing/scripts/analyze-coverage.py
   ```

3. **Run Coverage Analysis Script**
   ```bash
   python3 {resolved_path} --file {report_path} --threshold {threshold}
   ```

4. **Parse Results**
   The script returns JSON with:
   - `overall_coverage`: Line, branch, instruction, method, class percentages
   - `by_package`: Coverage breakdown per package
   - `low_coverage_classes`: Classes below threshold
   - `uncovered_lines`: Specific lines missing coverage

5. **Generate Report**
   ```
   ╔════════════════════════════════════════════════════════════╗
   ║              Coverage Analysis Report                      ║
   ╚════════════════════════════════════════════════════════════╝

   Overall Coverage:
   - Line Coverage: {line_coverage}% {status_emoji}
   - Branch Coverage: {branch_coverage}% {status_emoji}
   - Method Coverage: {method_coverage}%

   Threshold: {threshold}%
   Status: {PASS|FAIL}

   Low Coverage Classes:
   {list of classes below threshold with uncovered methods}

   Recommendations:
   {prioritized list of classes to test}
   ```

### JSON Output Contract

```json
{
  "status": "success",
  "data": {
    "overall_coverage": {
      "line_coverage": 85.5,
      "branch_coverage": 78.2,
      "instruction_coverage": 82.1,
      "method_coverage": 90.0,
      "class_coverage": 100.0
    },
    "by_package": [...],
    "low_coverage_classes": [...],
    "uncovered_lines": [...]
  },
  "metrics": {
    "file_analyzed": "target/site/jacoco/jacoco.xml",
    "threshold": 80,
    "meets_threshold": true
  }
}
```

---

## Workflow: Analyze Test Coverage

Analyze JaCoCo coverage reports, identify gaps, and prioritize test improvements.

### Parameters

- **report_path** (optional): Path to JaCoCo XML report (default: target/site/jacoco/jacoco.xml)
- **module** (optional): Module name for module-specific analysis
- **priority_filter** (optional): Filter gaps by priority: high, medium, low, all (default: all)

### Steps

1. **Verify Coverage Report Exists**
   ```
   Glob: pattern="{report_path}"
   ```

   If report doesn't exist, run Maven with jacoco:
   ```
   Skill: builder:builder-maven-rules
   Workflow: Execute Maven Build
   Parameters:
     goals: clean test jacoco:report
     module: {module if specified}
     output_mode: structured
   ```

2. **Analyze Coverage Gaps**
   ```
   Skill: cui-utilities:script-runner
   Script: cui-java-expert:cui-java-unit-testing/analyze-coverage-gaps
   Parameters:
     report_path: "{report_path}"
     priority_filter: "{priority_filter}"
   ```

   Parse JSON output:
   - `overall_coverage`: Line, branch, method coverage percentages
   - `gaps_by_priority`: Gaps categorized as high, medium, low priority
   - `recommendations`: Actionable test improvement suggestions
   - `untested_public_methods`: List of public APIs without coverage

3. **Analyze Gap Priorities**

   **High Priority Gaps** (requires immediate attention):
   - Uncovered public methods
   - Security/validation code without tests
   - Error handling paths not tested
   - Classes with >10 uncovered lines

   **Medium Priority Gaps**:
   - Uncovered branches in tested methods
   - Package-private methods without tests
   - Minor utility methods

   **Low Priority Gaps**:
   - Trivial getters/setters
   - Generated code
   - Defensive null checks already covered

4. **Generate Actionable Report**

   ```
   ╔════════════════════════════════════════════════════════════╗
   ║           Test Coverage Gap Analysis                       ║
   ╚════════════════════════════════════════════════════════════╝

   Overall Coverage:
   - Line Coverage: {line}% (target: 80%)
   - Branch Coverage: {branch}% (target: 70%)
   - Method Coverage: {method}% (target: 100% public)

   High Priority Gaps: {high_count}
   {list of high priority untested code with file:line}

   Medium Priority Gaps: {medium_count}
   {list of medium priority gaps}

   Low Priority Gaps: {low_count}

   Recommendations:
   1. Add tests for {class}::{method} - uncovered public API
   2. Add branch tests for {class}::{method} - missing error path
   3. Add tests for {class} - only {coverage}% coverage
   ```

5. **Return Structured Results**

   Generate JSON response for programmatic use:
   ```json
   {
     "coverage_status": "meets_threshold|below_threshold",
     "overall": {
       "line": 85.5,
       "branch": 72.0,
       "method": 90.0
     },
     "gaps_by_priority": {
       "high": [...],
       "medium": [...],
       "low": [...]
     },
     "recommendations": [
       {
         "priority": "high",
         "class": "TokenValidator",
         "method": "validateExpiry",
         "reason": "uncovered_public_method",
         "file": "src/main/java/auth/TokenValidator.java",
         "lines": [45, 46, 47]
       }
     ]
   }
   ```

### Script Contracts

**analyze-coverage-gaps** (via script-runner):
- **Input**: JSON with `report_path` and optional `priority_filter`
- **Output**: JSON with coverage gaps prioritized by impact
- **Location**: `cui-java-expert:cui-java-unit-testing/analyze-coverage-gaps`

### Maven Integration

To generate coverage reports with tests:
```
Skill: builder:builder-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: clean test jacoco:report
  module: {module if specified}
  output_mode: structured
```

### Related Standards

- Coverage Analysis Pattern: standards/coverage-analysis-pattern.md
- Testing Quality Standards: standards/testing-quality-standards.md

---

## Workflow: Fix Test Failures

Fix failing unit tests iteratively until all pass.

### Parameters

- **max_iterations** (optional): Maximum fix attempts (default: 3)
- **module** (optional): Module to test
- **fix_production_code** (optional): Allow production code fixes (default: false)

### When to Use

Use this workflow when:
- Tests are failing and need to be fixed
- Called from agents for autonomous test fixing
- Part of implement workflows that need test verification

### Step 1: Execute Tests

```
Skill: builder:builder-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: clean test
  module: {module if specified}
  output_mode: structured
```

### Step 2: Parse and Categorize Test Failures

From the build result, extract `data.issues` where `type == "test_failure"`.

**Categorize by failure type:**
- **assertion**: Assertion failures (expected vs actual)
- **null_pointer**: NullPointerException in test or production code
- **exception**: Unexpected exception thrown
- **setup_error**: Test setup/teardown errors (@BeforeEach, @AfterEach)
- **timeout**: Test timeout exceeded
- **missing_dependency**: Missing mock or dependency

### Step 3: Load Testing Standards

```
Read: standards/testing-junit-core.md
Read: standards/testing-quality-standards.md
```

If tests use generators:
```
Read: standards/test-generator-framework.md
```

### Step 4: Analyze Each Failure

For each failure:
1. Read the test file
2. Read the production code being tested
3. Analyze failure cause
4. Determine fix location (test or production if allowed)

### Step 5: Apply Fixes

**Test-only fixes** (when fix_production_code is false):
- Fix incorrect assertions
- Fix test setup/teardown
- Add missing mocks
- Fix generator usage
- Update expected values

**Production fixes** (when fix_production_code is true):
- Fix null handling
- Fix incorrect logic
- Add missing validation

Use Edit tool for all modifications.

### Step 6: Verify Tests Pass

```
Skill: builder:builder-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: test
  module: {module if specified}
  output_mode: structured
```

### Step 7: Iterate if Needed

If failures remain and `iteration < max_iterations`:
- Return to Step 2 with updated failure list
- Track iteration count

If `iteration >= max_iterations`:
- Return partial result with remaining failures

### Output Contract

```json
{
  "status": "success|partial|failed",
  "iterations": 2,
  "fixed": 5,
  "remaining": 0,
  "requires_production_fix": false,
  "files_modified": ["src/test/java/MyTest.java"],
  "failures_by_type": {
    "assertion": 3,
    "null_pointer": 2
  },
  "test_status": "SUCCESS|FAILURE"
}
```

### Error Handling

- If failure requires architectural change → Report, don't attempt fix
- If production fix needed but not allowed → Report with `requires_production_fix: true`
- If same failure persists after fix → Report as unfixable
- If failure is in generated test code → Skip

---

## Workflow: Implement Tests

Implement unit tests for a class with coverage verification.

### Parameters

- **target_class** (required): Class to test (path or fully qualified name)
- **coverage_target** (optional): Target coverage % (default: 80)
- **module** (optional): Module context

### When to Use

Use this workflow when:
- Implementing tests for new or existing code
- Called from agents for autonomous test creation
- Adding test coverage for untested classes

### Step 1: Analyze Target Class

```
Glob: pattern="**/{target_class}.java"
Read: {target_class_path}
```

Identify:
- Package and class name
- Public methods requiring tests
- Dependencies (constructor params, injected fields)
- Value object characteristics (equals/hashCode/toString)
- Exception throwing methods

### Step 2: Load Testing Standards (Conditional)

**Always load core standards:**
```
Read: standards/testing-junit-core.md
```

**If target is a value object:**
```
Read: standards/testing-value-objects.md
```

**If project uses generators** (check for existing test patterns):
```
Read: standards/test-generator-framework.md
```

### Step 3: Check Existing Tests

```
Glob: pattern="**/{target_class}Test.java"
```

If test class exists:
- Read existing tests
- Identify methods not yet tested
- Determine coverage gaps

### Step 4: Generate Test Class

Apply standards from Step 2:
- @EnableGeneratorController if using generators
- @DisplayName for class and methods
- AAA pattern for all tests
- Meaningful assertion messages
- ShouldHandleObjectContracts if value object

**Test Method Coverage:**
- One test per public method minimum
- Additional tests for edge cases
- Exception tests for validation

### Step 5: Write Test File

If new file:
```
Write: src/test/java/{package}/{target_class}Test.java
```

If extending existing:
```
Edit: {existing_test_file}
```

### Step 6: Verify Tests Pass

```
Skill: builder:builder-maven-rules
Workflow: Execute Maven Build
Parameters:
  goals: test -Dtest={target_class}Test
  module: {module if specified}
  output_mode: structured
```

### Step 7: Fix Failures if Needed

If tests fail:
```
Workflow: Fix Test Failures
Parameters:
  max_iterations: 2
  module: {module if specified}
  fix_production_code: false
```

### Step 8: Verify Coverage

```
Workflow: Analyze Coverage
Parameters:
  report_path: target/site/jacoco/jacoco.xml
  threshold: {coverage_target}
```

If coverage below target:
- Identify uncovered methods
- Add additional tests
- Re-verify

### Output Contract

```json
{
  "status": "success|partial|failed",
  "test_class": "src/test/java/MyClassTest.java",
  "tests_generated": 8,
  "tests_passed": 8,
  "coverage": {
    "line": 85.0,
    "branch": 72.0,
    "meets_target": true
  },
  "standards_applied": [
    "testing-junit-core",
    "test-generator-framework",
    "testing-value-objects"
  ]
}
```

### Test Generation Checklist

Before returning success:
- [ ] Test class has @EnableGeneratorController (if using generators)
- [ ] All tests follow AAA pattern
- [ ] All assertions have meaningful messages
- [ ] @DisplayName on class and methods
- [ ] No @GeneratorSeed committed
- [ ] Value object contracts implemented (if applicable)
- [ ] All tests pass
- [ ] Coverage meets target

---

## References

* Core Testing Standards: standards/testing-junit-core.md
* Value Object Testing: standards/testing-value-objects.md
* Generator Usage: standards/test-generator-framework.md
* MockWebServer Testing: standards/testing-mockwebserver.md
* Integration Testing: standards/integration-testing.md
* JULi Logger Testing: standards/testing-juli-logger.md
* Coverage Analysis: standards/coverage-analysis-pattern.md
