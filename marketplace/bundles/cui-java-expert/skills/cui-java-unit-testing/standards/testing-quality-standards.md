# Test Quality Standards

## Overview

This document defines quality standards for CUI test code, focusing on maintainability, readability, and effectiveness. These standards ensure tests provide value while remaining clean and efficient.

## Core Quality Principles

### Test Value
* Every test must verify meaningful behavior
* Tests should catch real bugs, not verify framework functionality
* Focus on business logic and edge cases

### Code Quality
* Test code follows same quality standards as production code
* Clear, descriptive naming without excessive verbosity
* Minimal comments - code should be self-explanatory
* DRY principle applies - extract common test utilities

### Maintainability
* Tests remain easy to understand and modify
* Changes to production code don't require extensive test rewrites
* Test failures clearly indicate what broke

## AI-Generated Code Detection

LLMs often generate test code with characteristic patterns that reduce quality. Identify and eliminate these artifacts.

### Critical Indicators

* **Method names exceeding 75 characters**
* **Excessive inline comments** explaining obvious operations
* **Repetitive test patterns** with only minor variations
* **Verbose @DisplayName annotations** (54+ characters)
* **Over-documentation** with redundant explanations
* **Meaningless constructor tests** verifying trivial functionality

### Test Categories to Eliminate

**Meaningless Tests**
```java
// REMOVE - No business value
@Test
void shouldCreateWithValidParameters() {
    assertNotNull(new AccessTokenContent(validClaims));
}
```

**Framework Behavior Tests**
```java
// REMOVE - Testing framework, not application
@Test
void shouldLogInfoMessageWhenTokenValidatorIsInitialized() {
    // Tests framework logging behavior
}
```

**Over-Commented Tests**
```java
// REMOVE excessive comments
@Test
void shouldValidateToken() {
    // Create a token holder for testing purposes
    TestTokenHolder holder = new TestTokenHolder();
    // Set the token type to access token for validation
    holder.setTokenType(ACCESS_TOKEN);
    // Perform validation and check result
    assertTrue(validator.validate(holder.build()).isValid());
}

// CORRECT - Self-explanatory code
@Test
void shouldValidateAccessToken() {
    TestTokenHolder holder = new TestTokenHolder()
        .setTokenType(ACCESS_TOKEN);

    assertTrue(validator.validate(holder.build()).isValid(),
        "Valid access token should pass validation");
}
```

### Cleanup Actions

* **ELIMINATE**: Tests verifying trivial functionality
* **REMOVE**: Comments explaining obvious operations
* **SIMPLIFY**: Overly verbose method and test names
* **CONSOLIDATE**: Identical patterns into parameterized tests
* **REPLACE**: Verbose @DisplayName with focused descriptions (<50 chars)
* **PRESERVE**: Meaningful assertion messages (see Assertion Standards below)

## Parameterized Test Guidelines

### Mandatory Usage

Use parameterized tests when testing **3 or more similar variants** of the same behavior. This consolidates code and improves coverage.

### Annotation Preference Order

Choose annotations in this order:

**1. @GeneratorsSource (Most Preferred)**
* Use CUI test generators for complex object creation
* Provides comprehensive test data coverage
* Maintains consistency with framework standards
* Example: Testing various token configurations, user objects

**2. @CompositeTypeGeneratorSource**
* For testing with multiple related complex types
* Combines generators for comprehensive scenarios
* Ideal for integration-style unit tests

**3. @CsvSource (Standard Choice)**
* Simple data combinations
* Easy to read input/output pairs
* Good maintainability

```java
@ParameterizedTest
@CsvSource({
    "https://example.com, https://example.com/.well-known/openid-configuration",
    "https://api.example.com, https://api.example.com/.well-known/openid-configuration"
})
void shouldValidateMatchingIssuer(String issuer, String wellKnownUrl) {
    URL wellKnown = URI.create(wellKnownUrl).toURL();
    assertDoesNotThrow(() -> parser.validateIssuer(issuer, wellKnown));
}
```

**4. @ValueSource (Simple Cases)**
* Single parameter variations
* Boundary value testing
* Simple string/number sets

**5. @MethodSource (Last Resort)**
* Only when other options insufficient
* Complex data setup not handled by generators
* Document justification

### Quality Requirements

* Use descriptive `@DisplayName` annotations
* Choose meaningful parameter names
* Document complex parameter combinations
* Always consolidate duplicate test patterns
* Prefer generators over manual data creation

## Assertion Message Standards

**Requirement**: ALL assertions must include meaningful, concise failure messages.

### Key Principles

* **Include WHY**: Explain expected behavior being verified
* **Be concise**: Aim for 20-60 characters
* **Provide context**: Help identify what went wrong
* **Use consistent language**: Follow established patterns

### Standard Message Patterns

**Presence checks**
```java
assertTrue(result.isPresent(), "User should be found by valid ID");
assertNotNull(response, "API should return non-null response");
```

**Equality**
```java
assertEquals(expected, actual, "Token should contain correct issuer");
assertEquals(3, list.size(), "List should have 3 elements");
```

**Collections**
```java
assertTrue(list.contains(item), "Collection should contain item");
assertFalse(errors.isEmpty(), "Validation should detect invalid input");
```

**Exceptions**
```java
TokenValidationException exception = assertThrows(
    TokenValidationException.class,
    () -> validator.validate(invalidToken),
    "Invalid token should trigger validation exception"
);
```

### Anti-Patterns (DO NOT USE)

```java
// Missing context
assertTrue(result.isPresent());

// Meaningless
assertTrue(result.isPresent(), "Should be true");

// Too verbose (>60 characters)
assertTrue(result.isPresent(),
    "This assertion verifies that the result optional contains a value as expected when...");
```

## SonarQube Compliance

### Exception Testing

For complete exception testing patterns including `assertThrows` best practices and SonarQube compliance, see [JUnit Core Testing Standards - Exception Testing](testing-junit-core.md#exception-testing).

## Testing Library Compliance

For complete testing library requirements, allowed/forbidden libraries, and migration guidelines, see [JUnit Core Testing Standards - Testing Library Requirements](testing-junit-core.md#testing-library-requirements).

## Performance Standards

### Execution Speed

* Unit tests should execute in <1 second each
* Fast feedback loop for development
* Identify and optimize slow tests

### Resource Efficiency

* Minimize memory allocation in tests
* Clean up resources properly (`@AfterEach`)
* Avoid unnecessary object creation

### Test Independence

* Tests run successfully in any order
* No shared mutable state between tests
* Parallel execution supported where possible

## Coverage Requirements

### Minimum Thresholds

* **80% line coverage** minimum
* **80% branch coverage** minimum
* **100% coverage** for critical paths
* **All public APIs** must be tested

### Coverage Verification

Execute coverage verification with Maven:

```bash
./mvnw clean verify -Pcoverage > target/coverage-verify.log 2>&1
```

Inspect coverage results and ensure minimum 80% line/branch coverage is met. Address any coverage gaps.

### Coverage Quality

* No coverage regressions allowed
* Focus on meaningful coverage, not just numbers
* Test behavior, not implementation details
* Regular coverage review in code reviews

## Quality Verification Checklist

Before completing test implementation:

### Code Quality
- [ ] No AI-generated artifacts (verbose names, excessive comments)
- [ ] All assertions have meaningful messages (20-60 chars)
- [ ] Test names clearly describe behavior
- [ ] No hardcoded test data (use generators)
- [ ] No forbidden libraries (Mockito, Hamcrest, PowerMock)

### Standards Compliance
- [ ] Parameterized tests used for 3+ variants
- [ ] assertThrows follows SonarQube rules
- [ ] Testing library restrictions followed
- [ ] AAA pattern applied consistently

### Test Execution
- [ ] All tests pass
- [ ] Tests are independent (run in any order)
- [ ] Fast execution (<1 second per unit test)
- [ ] Coverage meets minimum requirements (80%)

### Maintainability
- [ ] Tests easy to understand and modify
- [ ] Common utilities extracted (DRY)
- [ ] Clear documentation where needed
- [ ] Follows project conventions
