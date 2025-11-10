# Testing Maintenance Reference

## Overview

This reference provides standards, patterns, and detection criteria specifically for maintaining and improving existing test code. Use this when performing test quality improvements, code reviews, or systematic test refactoring.

**Scope**: Maintenance-specific requirements for existing test code. For writing NEW tests, see core testing standards.

## Forbidden Test Anti-Patterns

### Overview

Test code must be deterministic and straightforward. The following patterns are **strictly forbidden** in unit tests as they compromise test reliability and readability.

### No Conditional Testing

**Strict Requirements**:

* **NO if-else statements**: Tests must not contain conditional logic that changes test behavior
* **NO switch statements**: Test flow must be linear without branching logic
* **NO Optional.orElse()**: Using Optional.orElse() or Optional.orElseGet() is an error - test the Optional state explicitly
* **NO ternary operators**: Avoid `condition ? value1 : value2` in test assertions

**Rationale**: Conditional logic in tests creates multiple execution paths, making it unclear what is actually being tested. Tests should have a single, deterministic path from setup through verification.

#### Correct Patterns

**Separate Tests for Different Scenarios**:

```java
// ❌ WRONG - Conditional logic in test
@Test
void testUserAccess() {
    User user = getUser();
    if (user.hasRole("admin")) {
        assertTrue(user.canAccessAllResources());
    } else {
        assertFalse(user.canAccessAdminPanel());
    }
}

// ✅ CORRECT - Separate focused tests
@Test
void adminUserShouldAccessAllResources() {
    User adminUser = createAdminUser();
    assertTrue(adminUser.canAccessAllResources(),
        "Admin user should have access to all resources");
}

@Test
void regularUserShouldNotAccessAdminPanel() {
    User regularUser = createRegularUser();
    assertFalse(regularUser.canAccessAdminPanel(),
        "Regular user should not access admin panel");
}
```

**Optional Testing**:

```java
// ❌ WRONG - Using Optional.orElse in assertions
@Test
void testOptionalValue() {
    Optional<String> result = service.findValue();
    assertEquals("default", result.orElse("default"));
}

// ✅ CORRECT - Test Optional state explicitly
@Test
void shouldReturnEmptyOptionalWhenValueNotFound() {
    Optional<String> result = service.findValue();
    assertFalse(result.isPresent(),
        "Should return empty Optional when value not found");
}

@Test
void shouldReturnOptionalWithValueWhenFound() {
    Optional<String> result = service.findExistingValue();
    assertTrue(result.isPresent(),
        "Should return Optional with value when found");
    result.ifPresent(value ->
        assertEquals("expected", value,
            "Optional should contain expected value"));
}
```

**Switch Statement Alternative**:

```java
// ❌ WRONG - Switch in test
@Test
void testStatusHandling() {
    Status status = getStatus();
    switch (status) {
        case ACTIVE -> assertTrue(service.isActive());
        case INACTIVE -> assertFalse(service.isActive());
        case PENDING -> assertNull(service.getActiveDate());
    }
}

// ✅ CORRECT - Parameterized test
@ParameterizedTest
@EnumSource(Status.class)
void shouldHandleAllStatusValues(Status status) {
    service.setStatus(status);

    boolean expectedActive = (status == Status.ACTIVE);
    assertEquals(expectedActive, service.isActive(),
        "Service active state should match status: " + status);
}
```

**Ternary Operator Alternative**:

```java
// ❌ WRONG - Ternary operator in assertion
@Test
void testResult() {
    Result result = service.process();
    assertEquals(
        result.isSuccess() ? "success" : "failure",
        result.getMessage()
    );
}

// ✅ CORRECT - Explicit assertions
@Test
void shouldReturnSuccessMessageWhenProcessingSucceeds() {
    Result result = service.processValidInput();
    assertTrue(result.isSuccess(), "Processing should succeed");
    assertEquals("success", result.getMessage(),
        "Success message should match expected value");
}

@Test
void shouldReturnFailureMessageWhenProcessingFails() {
    Result result = service.processInvalidInput();
    assertFalse(result.isSuccess(), "Processing should fail");
    assertEquals("failure", result.getMessage(),
        "Failure message should match expected value");
}
```

### Proper Exception Handling

**Strict Requirements**:

* **NO try-catch blocks**: Never use try-catch in unit tests
* **Checked exceptions**: Add `throws` declaration to test method
* **Expected exceptions**: Use `assertThrows()` for expected exceptions
* **No exceptions expected**: Use `assertDoesNotThrow()` when verifying no exceptions

**Rationale**: Try-catch blocks in tests hide failures and make test intent unclear. JUnit provides better mechanisms for exception handling.

#### Exception Handling Patterns

**Checked Exceptions**:

```java
// ❌ WRONG - Using try-catch in test
@Test
void testFileReading() {
    try {
        String content = fileReader.read("test.txt");
        assertEquals("expected", content);
    } catch (IOException e) {
        fail("Should not throw exception");
    }
}

// ✅ CORRECT - Declare throws
@Test
void shouldReadFileContent() throws IOException {
    String content = fileReader.read("test.txt");
    assertEquals("expected", content,
        "File content should match expected value");
}
```

**Expected Exceptions**:

```java
// ❌ WRONG - Catching expected exception
@Test
void testInvalidFile() {
    try {
        fileReader.read("invalid.txt");
        fail("Should have thrown IllegalArgumentException");
    } catch (IllegalArgumentException e) {
        assertEquals("File not found: invalid.txt", e.getMessage());
    }
}

// ✅ CORRECT - Using assertThrows
@Test
void shouldThrowExceptionForInvalidFile() {
    IllegalArgumentException exception = assertThrows(
        IllegalArgumentException.class,
        () -> fileReader.read("invalid.txt"),
        "Should throw IllegalArgumentException for invalid file"
    );
    assertEquals("File not found: invalid.txt", exception.getMessage(),
        "Exception message should indicate file not found");
}
```

**Explicit No Exception Verification**:

```java
// ❌ WRONG - Implicit assumption
@Test
void testValidInput() {
    validator.validate("valid-input");
    // Test passes if no exception - unclear intent
}

// ✅ CORRECT - Explicit verification
@Test
void shouldNotThrowExceptionForValidInput() {
    assertDoesNotThrow(
        () -> validator.validate("valid-input"),
        "Should not throw exception for valid input"
    );
}
```

**Multiple Exception Cases**:

```java
// ✅ CORRECT - Parameterized test for multiple exception cases
@ParameterizedTest
@MethodSource("invalidInputProvider")
void shouldThrowExceptionForInvalidInputs(String input, String expectedMessage) {
    ValidationException exception = assertThrows(
        ValidationException.class,
        () -> validator.validate(input),
        "Should throw ValidationException for invalid input: " + input
    );
    assertTrue(exception.getMessage().contains(expectedMessage),
        "Exception message should contain: " + expectedMessage);
}

static Stream<Arguments> invalidInputProvider() {
    return Stream.of(
        Arguments.of(null, "must not be null"),
        Arguments.of("", "must not be empty"),
        Arguments.of("  ", "must not be blank")
    );
}
```

## Unit Test Focus Requirements

### Overview

Each type in the codebase MUST have a separate, dedicated unit test that focuses **exclusively** on that class. This ensures comprehensive coverage and prevents test duplication.

### Requirements

**Dedicated Unit Tests**:

* Each class must have its own unit test class
* Unit tests must focus exclusively on the class under test
* Include comprehensive corner cases and edge cases
* Test all public methods and their contracts

**Avoid Test Duplication**:

* Verify that aspects testable within a unit are not duplicated in other unit tests
* Integration tests should test integration, not repeat unit-level testing
* If functionality is tested in a unit test, don't repeat it in integration tests

**Example Structure**:

```java
// ✅ CORRECT - Dedicated unit test
class TokenValidatorTest {

    @Test
    void shouldValidateValidToken() {
        // Test happy path
    }

    @Test
    void shouldRejectExpiredToken() {
        // Test edge case: expiration
    }

    @Test
    void shouldRejectTokenWithInvalidSignature() {
        // Test edge case: signature validation
    }

    @Test
    void shouldRejectNullToken() {
        // Test corner case: null handling
    }

    @Test
    void shouldRejectEmptyToken() {
        // Test corner case: empty input
    }
}

// ✅ CORRECT - Integration test doesn't duplicate unit tests
class AuthenticationIntegrationTest {

    @Test
    void shouldAuthenticateUserWithValidTokenAndLoadPermissions() {
        // Tests the integration between validator, user service, and permissions
        // Does NOT re-test token validation logic (already covered in unit test)
    }
}
```

## Value Object Testing Criteria

### When to Apply ShouldHandleObjectContracts<T>

**Apply to classes that**:

* Implement custom equals()/hashCode() methods
* Represent domain data with value semantics
* Are used in collections or as map keys
* Participate in caching or persistence operations
* Are DTOs with structural equality requirements

### When NOT to Apply

**Do NOT apply to**:

* **Enums**: Already have proper equals/hashCode from Java
* **Utility classes**: Classes with only static methods
* **Infrastructure classes**: Parsers, validators, builders, factories
* **Classes without value semantics**: Services, controllers, managers
* **Builder pattern classes**: Test the built object instead, not the builder

### Common Mistakes

❌ **Applying contracts to enums**:
```java
// WRONG - Enums don't need contract testing
class UserRoleTest implements ShouldHandleObjectContracts<UserRole> {
    // Unnecessary - Java enums already have correct equals/hashCode
}
```

❌ **Testing infrastructure classes as value objects**:
```java
// WRONG - Parsers are not value objects
class TokenParserTest implements ShouldHandleObjectContracts<TokenParser> {
    // Parser is infrastructure, not a value object
}
```

❌ **Mixing business logic with contract tests**:
```java
// WRONG - Don't mix concerns
class UserDataTest implements ShouldHandleObjectContracts<UserData> {
    @Test
    void shouldValidateEmailFormat() {
        // Business logic test in contract test class
    }
}

// CORRECT - Separate concerns
class UserDataContractTest implements ShouldHandleObjectContracts<UserData> {
    // Only contract tests
}

class UserDataTest {
    @Test
    void shouldValidateEmailFormat() {
        // Business logic tests separate
    }
}
```

## Test Quality Issue Detection

### AI-Generated Code Artifacts

**Detection Criteria** (from quality standards):

* Method names exceeding 75 characters
* Excessive comments that state the obvious
* Verbose @DisplayName annotations
* Boilerplate comments like "// Arrange", "// Act", "// Assert"
* Generic assertion messages

**Action**: Systematically remove during maintenance cycles. See testing-quality-standards.md for complete detection rules.

### Reflection Workarounds

**CRITICAL**: Workaround tests using reflection to change internal state are always a bug.

```java
// ❌ ALWAYS A BUG - Reflection to change private state
@Test
void testInternalState() throws Exception {
    Field field = MyClass.class.getDeclaredField("internalState");
    field.setAccessible(true);
    field.set(instance, "modified");

    assertEquals("modified", instance.getInternalState());
}
```

**Action**: These tests indicate design problems. Refactor production code to be testable without reflection, or test through public API only.

### Non-Sensible Tests

**Tests to Remove**:

* **Meaningless constructor tests**: Testing that `new Object()` doesn't throw
* **Framework behavior tests**: Testing that Spring autowires correctly
* **Getter/setter only tests**: If no validation logic exists
* **Tests that don't assert anything meaningful**

```java
// ❌ Non-sensible - remove these
@Test
void testConstructor() {
    assertNotNull(new UserData());
}

@Test
void testGetterSetter() {
    UserData data = new UserData();
    data.setName("test");
    assertEquals("test", data.getName());
}
```

### Test Duplication

**Detection Criteria**:

* Multiple unit tests testing the same method with same inputs
* Integration tests repeating unit test scenarios
* Similar test names across different test classes
* Copy-pasted test methods with minor variations

**Action**: Consolidate duplicates, use parameterized tests, ensure clear separation between unit and integration tests.

## Test Enhancement Prioritization

### High Priority - Business Logic Tests

Focus maintenance efforts on:

* **Domain object tests**: Token content, claims, validators
* **Business rule validation**: Core business logic verification
* **API contract and behavior**: Public API contract testing
* **User-facing functionality**: Features directly used by users
* **Security and compliance**: Security-critical functionality

**Criteria**: These tests verify core business value and are most likely to catch real bugs.

### Medium Priority - Value Objects

* Data transfer objects with equals/hashCode contracts
* Configuration objects used in business logic
* Domain enums with complex behavior

**Criteria**: Important for data integrity but less critical than business logic.

### Low Priority - Infrastructure Tests

* HTTP client/server communication tests
* JWKS loading and caching tests
* Security infrastructure tests (if already comprehensive)
* Build and deployment infrastructure tests
* Framework integration tests

**Criteria**: Infrastructure is important but usually well-tested by the framework itself. Focus on business logic first.

## Common Mistakes to Avoid

### Excessive AAA Comments

```java
// ❌ WRONG - Unnecessary comments in clear test
@Test
void shouldCalculateTotal() {
    // Arrange
    Order order = new Order();
    order.addItem(new Item("Product", 10.0));

    // Act
    double total = order.calculateTotal();

    // Assert
    assertEquals(10.0, total);
}

// ✅ CORRECT - Self-documenting structure
@Test
void shouldCalculateTotal() {
    Order order = new Order();
    order.addItem(new Item("Product", 10.0));

    double total = order.calculateTotal();

    assertEquals(10.0, total, "Total should equal item price");
}
```

**Rule**: Only add AAA comments when test structure is genuinely unclear. Properly structured tests are self-documenting.

### Mixing Test Concerns

```java
// ❌ WRONG - Testing multiple concerns in one test
@Test
void testUserService() {
    // Tests creation, validation, and persistence all at once
    User user = service.createUser("test");
    assertTrue(service.validateUser(user));
    assertTrue(service.saveUser(user));
    assertNotNull(service.findUser(user.getId()));
}

// ✅ CORRECT - Focused tests
@Test
void shouldCreateValidUser() {
    User user = service.createUser("test");
    assertNotNull(user, "Created user should not be null");
    assertEquals("test", user.getName(), "User name should match input");
}

@Test
void shouldValidateCorrectlyFormattedUser() {
    User validUser = createValidUser();
    assertTrue(service.validateUser(validUser),
        "Valid user should pass validation");
}
```

### Testing Through Wrong Abstraction Level

```java
// ❌ WRONG - Unit test testing integration
@Test
void testSaveUser() {
    // Unit test shouldn't interact with database
    User user = new User("test");
    repository.save(user);
    assertNotNull(repository.findById(user.getId()));
}

// ✅ CORRECT - Unit test at appropriate level
@Test
void shouldCreateUserWithValidData() {
    User user = new User("test");
    assertEquals("test", user.getName());
    assertTrue(user.isValid());
}
```

## Coverage Requirements

### Quality Gates

* **Maintain minimum 80% line coverage**
* **Preserve existing coverage levels** - no regressions
* **Identify untested critical paths**
* **Document coverage gaps** with justification

### Coverage vs Quality

**Remember**: Coverage percentage is not the goal. Quality tests that verify behavior are the goal. Prefer:

* Meaningful tests with slightly lower coverage
* Over meaningless tests with 100% coverage

## Maintenance-Specific Notes

### Production Code Protection

**STRICT REQUIREMENTS**:

* **NO PRODUCTION CHANGES** except confirmed bugs
* **Bug Discovery**: Must ask user for approval before fixing production code
* **Test-Only Changes**: Focus solely on test improvement
* **Behavior Preservation**: All existing tests must continue to pass

### When Bugs Are Discovered

If you discover production code bugs during test maintenance:

1. **Stop maintenance process**
2. **Document bug details** (location, issue, impact)
3. **Ask user for approval** to fix production code
4. **Wait for confirmation** before proceeding
5. **Create separate commit** for bug fix

### Module-by-Module Strategy

Process modules systematically:

* Complete one module entirely before moving to next
* Test execution: `./mvnw clean test -pl module-name`
* Coverage check: `./mvnw clean verify -Pcoverage -pl module-name`
* Commit per module completion

## References

* **Core Testing Standards**: testing-junit-core.md - Fundamental testing requirements for new tests
* **Quality Standards**: testing-quality-standards.md - Quality requirements and AI detection
* **CUI Framework Guide**: test-generator-framework.md - CUI testing framework usage
* **Value Object Testing**: testing-value-objects.md - Complete value object testing guide
