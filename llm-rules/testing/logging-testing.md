# Logging Testing Guide

> **Note:** This document has been migrated to the standards directory. Please refer to the [Logging Testing Guide](/standards/logging/testing-guide.adoc) for the current version.

## Migration Notice
The detailed logging testing guide has been migrated to the standards directory in AsciiDoc format. Please refer to the following documents for the current standards:

- [Logging Testing Guide](/standards/logging/testing-guide.adoc)
- [Logging Core Standards](/standards/logging/core-standards.adoc)
- [Logging Implementation Guide](/standards/logging/implementation-guide.adoc)
- [Testing-Specific Logging Standards](/standards/testing/logging-testing.adoc)

## Testing Requirements

### 1. Required Coverage
- All INFO level messages
- All WARN level messages
- All ERROR level messages
- All FATAL level messages
- Parameter substitution cases
- Exception logging cases
- Template-based logging

### 2. Optional Coverage
- DEBUG level messages
- TRACE level messages
- Test logging itself

## Testing Tools

### 1. Core Components
- `cui-test-juli-logger`: Primary testing framework
- `de.cuioss.test.juli.TestLogLevel`: Log level constants
- `de.cuioss.test.juli.LogAsserts`: Assertion methods
- `@EnableTestLogger`: Test class annotation

### 2. LogAsserts Methods
```java
// Exact message match
assertLogMessagePresent(TestLogLevel level, String message)

// Partial message match
assertLogMessagePresentContaining(TestLogLevel level, String partialMessage)

// Verify no message exists
assertNoLogMessagePresent(TestLogLevel level, Logger logger)

// Verify exactly one message exists
assertSingleLogMessagePresent(TestLogLevel level, String message)
```

## Testing Patterns

### 1. Basic Test Structure
```java
@EnableTestLogger
class ResourceBundleLocatorTest {
    private static final CuiLogger LOGGER = new CuiLogger(ResourceBundleLocator.class);

    @Test
    void shouldLogSuccessfulOperation() {
        // given
        var resourceName = "test.properties";

        // when
        loadResource(resourceName);

        // then
        assertSingleLogMessagePresent(
            TestLogLevel.INFO,
            BUNDLE.INFO.RESOURCE_LOADED.format(resourceName));
    }
}
```

### 2. Testing Exception Logging
```java
@Test
void shouldLogException() {
    // given
    var errorMessage = "Invalid configuration";
    var exception = new IllegalStateException(errorMessage);

    // when
    try {
        throw exception;
    } catch (Exception e) {
        LOGGER.error(ERROR.CONFIGURATION_ERROR.format(errorMessage), e);
    }

    // then
    assertSingleLogMessagePresent(
        TestLogLevel.ERROR,
        ERROR.CONFIGURATION_ERROR.format(errorMessage));
}
```

### 3. Testing Multiple Parameters
```java
@Test
void shouldLogMultipleParameters() {
    // given
    var userId = "user123";
    var role = "admin";

    // when
    LOGGER.info(INFO.USER_ROLE_ASSIGNED.format(userId, role));

    // then
    assertSingleLogMessagePresent(
        TestLogLevel.INFO,
        INFO.USER_ROLE_ASSIGNED.format(userId, role));
}
```

### 4. Testing No Logging
```java
@Test
void shouldNotLogInNormalCase() {
    // when
    performNormalOperation();

    // then
    assertNoLogMessagePresent(TestLogLevel.WARN, LOGGER);
    assertNoLogMessagePresent(TestLogLevel.ERROR, LOGGER);
}
```

## Best Practices

### 1. Test Organization
- One test method per logging scenario
- Clear test method names describing the scenario
- Follow given/when/then pattern
- Keep tests focused on logging verification

### 2. Assertion Usage
- Use most specific assertion method available
- Verify both presence and absence of messages
- Check exact message content when possible
- Use resolveIdentifierString() for ID verification

### 3. Test Data
- Use meaningful test data
- Avoid hardcoded strings
- Consider edge cases
- Test all parameter combinations

### 4. Common Pitfalls
- Not testing parameter substitution
- Missing exception logging tests
- Not verifying absence of unexpected logs
- Using wrong log levels in assertions

## Important Notes
- All rules are normative and must be applied unconditionally
- Test all required log levels (INFO/WARN/ERROR/FATAL)
- Always verify both presence and absence of messages
- Keep tests focused on logging verification
- Reference these rules with '@llm-rules'

## Success Criteria
1. All required messages are tested
2. Tests verify both success and failure cases
3. Parameter substitution is tested
4. Exception logging is verified
5. No unexpected logging occurs

## See Also
- [Logging Standards](../core/standards/logging-standards.md): Core standards and requirements
- [Logging Implementation Guide](../java/logging-implementation.md): Implementation to test
- [Testing Standards](../core/standards/testing-standards.md): Core testing standards
- [Project Standards](../core/standards/project-standards.md): Overall project standards
