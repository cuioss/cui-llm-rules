# JUnit Core Testing Standards

## Core Testing Principles

### Test Coverage

* All public methods must have unit tests
* All business logic must have appropriate test coverage
* Edge cases and error conditions must be tested
* Minimum 80% line coverage
* Minimum 80% branch coverage
* Critical paths must have 100% coverage
* All public APIs must be tested
* No coverage regressions allowed

### Test Independence

* Tests must be independent and not rely on other tests
* Tests must not depend on execution order
* Tests must clean up after themselves
* Tests must not have side effects that affect other tests
* Each test should test one specific behavior

### Test Clarity

* Test names must clearly describe what is being tested
* Test methods should follow the Arrange-Act-Assert (AAA) pattern (see AAA Pattern section below)
* Comments should explain complex test setups or assertions
* Use descriptive `@DisplayName` annotations for readable test names

### Test Maintenance

* Tests must be maintained alongside production code
* Failing tests must be fixed promptly
* Tests should be refactored when production code changes
* Test code should follow the same quality standards as production code
* Regular test review and quality checks

## Test Structure and Organization

### AAA Pattern (Arrange-Act-Assert)

All tests must follow the AAA pattern:

```java
@Test
@DisplayName("Should validate token with correct issuer")
void shouldValidateTokenWithCorrectIssuer() {
    String issuer = "https://example.com";
    Token token = createTokenWithIssuer(issuer);

    ValidationResult result = validator.validate(token);

    assertTrue(result.isValid(), "Token with correct issuer should be valid");
}
```

**Key Requirements:**

* One logical assertion per test
* Clear separation of test phases
* Descriptive variable names

## JUnit 5 Framework Standards

### Required Framework

* **JUnit 5 (Jupiter)** is the mandatory testing framework for all CUI projects
* Use `junit-jupiter` for all test execution and assertions
* Leverage JUnit 5 features (parameterized tests, nested tests, lifecycle annotations)

### Test Annotations

```java
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Nested;

@DisplayName("Token Validator Tests")
class TokenValidatorTest {

    @BeforeEach
    void setUp() {
        // Initialize test fixtures
    }

    @AfterEach
    void tearDown() {
        // Clean up resources
    }

    @Test
    @DisplayName("Should validate valid token successfully")
    void shouldValidateValidToken() {
        // Test implementation
    }
}
```

### Assertion Standards

**Use JUnit 5 assertions exclusively - Hamcrest is forbidden.**

All assertions must include meaningful, concise failure messages:

```java
// Good - Meaningful assertion messages
assertTrue(result.isPresent(), "User should be found by valid ID");
assertEquals(expected, actual, "Token should contain correct issuer");
assertFalse(errors.isEmpty(), "Validation should detect invalid input");
assertNotNull(response, "API should return non-null response");

// Bad - Missing or meaningless messages
assertTrue(result.isPresent()); // Missing context
assertTrue(result.isPresent(), "Should be true"); // Meaningless
```

**Assertion Message Requirements:**

* Include WHY the assertion should pass
* Keep messages concise but informative (20-60 characters)
* Provide debugging context
* Use consistent language patterns

**Standard Message Patterns:**

* For presence checks: `"X should be present"`, `"X should not be null"`
* For equality: `"X should equal Y"`, `"X should match expected value"`
* For collections: `"Collection should contain X"`, `"List should have Y elements"`
* For exceptions: `"X should throw Y exception"`, `"Invalid X should trigger Y"`

### Exception Testing

Use `assertThrows` for exception testing with proper SonarQube compliance:

```java
@Test
@DisplayName("Should throw exception on invalid input")
void shouldThrowExceptionOnInvalidInput() {
    // given
    String input = "invalid";
    service.validateInput(input);

    // when/then - Only one throwing statement in lambda
    TokenValidationException exception = assertThrows(
        TokenValidationException.class,
        () -> service.processInput(input),
        "Invalid token should trigger validation exception"
    );

    assertEquals("Invalid input", exception.getMessage());
}
```

**Key Principles:**

* Move setup code outside the lambda expression
* Keep only the single method call that should throw the exception
* Lambda should contain only one statement that can throw the expected exception

## Test Types

### Unit Tests

* Focus on testing a single unit of code in isolation
* Mock or stub dependencies
* Should be fast and lightweight
* Should cover all code paths
* Test classes named `*Test.java`

### Integration Tests

* Test interaction between components
* May use real dependencies or test doubles
* Should verify correct integration behavior
* Should be isolated from external systems when possible
* Test classes named `*IT.java` or `*ITCase.java`
* See integration-testing.md for detailed Maven configuration

### System Tests

* Test the entire system as a whole
* Verify end-to-end functionality
* May involve multiple components and services
* Should simulate real-world usage

## Testing Library Requirements

### Allowed Libraries

* **cui-test-libs**: All CUI testing utilities and frameworks (required)
* **junit-jupiter**: JUnit 5 for all test execution and assertions
* **awaitility**: For asynchronous testing and waiting conditions
* **rest-assured**: For REST API testing and HTTP request/response validation

### Forbidden Libraries

* **Mockito**: Do NOT use - use CUI framework alternatives or EasyMock for simple mocking
* **PowerMock**: Do NOT use - refactor to use dependency injection or EasyMock
* **Hamcrest**: Do NOT use - use JUnit 5 assertions exclusively

## Best Practices

### Test Organization

* Group related tests in the same test class
* Use descriptive test method names or `@DisplayName` annotations
* Follow a consistent naming convention
* Use nested test classes for organizing related test groups

```java
@DisplayName("Token Validator Tests")
class TokenValidatorTest {

    @Nested
    @DisplayName("Access Token Validation")
    class AccessTokenTests {
        @Test
        void shouldValidateAccessToken() {
            // Test implementation
        }
    }

    @Nested
    @DisplayName("ID Token Validation")
    class IdTokenTests {
        @Test
        void shouldValidateIdToken() {
            // Test implementation
        }
    }
}
```

### Test Documentation

* Use `@DisplayName` for readable test descriptions
* Document complex test setups with comments
* Explain business rules being tested
* Keep test documentation focused and concise

### Code Quality

* Test code should follow the same quality standards as production code
* Regular code reviews for tests
* Refactor duplicated test code
* Use test utilities and helper methods for common operations

## Quality Verification

### Coverage Verification

Use the Maven coverage profile to verify coverage requirements:

```bash
./mvnw clean verify -Pcoverage
```

This profile will:
* Enable JaCoCo code coverage analysis
* Generate detailed coverage reports
* Enforce minimum coverage thresholds (80% line/branch)
* Fail the build if coverage requirements are not met

### Quality Analysis Tools

* SonarCloud for static code analysis
* JUnit for unit testing execution
* Mutation testing for test quality verification
* Regular code reviews
* Continuous integration checks

## Scope of Changes

* Make targeted changes with single, clear purpose
* Avoid unrelated refactoring or improvements
* Focus on specific test requirements
* Document purpose of test changes

## Important Notes

* All rules are normative and must be applied unconditionally
* Test code should be treated with the same care as production code
* Tests should be maintainable and readable
* Focus on testing behavior, not implementation details
* Maintain test independence and isolation
