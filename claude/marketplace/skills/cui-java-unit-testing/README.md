# CUI Java Unit Testing Skill

High-quality unit testing standards and patterns for CUI Java projects.

## Overview

The `cui-java-unit-testing` skill provides comprehensive testing standards covering:

- **Core Testing**: JUnit 5 patterns, AAA structure, assertion standards, test organization
- **Value Object Testing**: Contract testing for equals/hashCode/toString with `ShouldHandleObjectContracts<T>`
- **Generator Framework**: CUI test generator usage, parameterized testing, seed restrictions
- **HTTP Testing**: MockWebServer patterns for testing HTTP clients and APIs
- **Integration Testing**: Maven failsafe configuration, naming conventions, CI/CD integration

## When to Use This Skill

Use `cui-java-unit-testing` when:

- Writing new unit tests for Java classes
- Testing value objects with equals/hashCode contracts
- Using the CUI test generator framework for test data
- Testing HTTP clients or REST APIs with MockWebServer
- Setting up integration tests separate from unit tests
- Ensuring test coverage meets quality standards (80% minimum)

## Prerequisites

**Required**:
- Java 17 or later
- Maven build system
- JUnit 5 (Jupiter)
- CUI test generator framework (`de.cuioss.test.generator`)
- cui-test-value-objects (for contract testing)

**Optional**:
- OkHttp MockWebServer (for HTTP testing)
- cui-test-juli-logger (for logging tests)

## Standards Included

### 1. Core JUnit Testing (`testing-junit-core.md`)

**Always loaded** - Foundation for all testing:

- AAA pattern (Arrange-Act-Assert) for test structure
- Assertion messages (20-60 characters, meaningful)
- @DisplayName for test descriptions
- Test independence and isolation
- Exception testing with assertThrows
- Lifecycle methods (@BeforeEach, @AfterEach)
- Parameterized tests with @ParameterizedTest
- **NO Mockito, Hamcrest, or PowerMock** (use CUI frameworks)

### 2. Value Object Testing (`testing-value-objects.md`)

**Load when**: Testing classes with equals/hashCode/toString

- `ShouldHandleObjectContracts<T>` interface
- Generator-based contract testing
- Automatic verification of equals/hashCode/toString
- Separation of contract tests from business logic tests
- Comprehensive coverage of object contracts

### 3. Generator Framework (`testing-generators.md`)

**Load when**: Using test data generators

- @EnableGeneratorController annotation
- Generators.* for all test data (mandatory)
- @GeneratorsSource for parameterized tests
- **NEVER commit @GeneratorSeed** (debugging only)
- Generator composition for complex objects
- Type-safe generator usage

### 4. MockWebServer Testing (`testing-mockwebserver.md`)

**Load when**: Testing HTTP clients or APIs

- @EnableMockWebServer annotation
- Mock response setup with enqueue
- Request verification (headers, body, params)
- Testing various HTTP status codes
- Retry logic and error handling tests
- Integration with generators

### 5. Integration Testing (`integration-testing.md`)

**Load when**: Writing integration tests

- Maven surefire vs failsafe configuration
- *IT.java or *ITCase.java naming conventions
- Integration test profiles
- Separation from unit tests
- CI/CD pipeline integration

## Quick Start

### 1. Basic Unit Test with Generators

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

### 2. Value Object Contract Testing

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

    // Contract tests (equals/hashCode/toString) run automatically
}
```

### 3. Parameterized Test with Generators

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

### 4. HTTP Client Testing

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

### 5. Integration Test Setup

```java
// File: src/test/java/.../SomeServiceIT.java
@QuarkusIntegrationTest
@DisplayName("Integration tests for SomeService")
class SomeServiceIT {

    @Test
    @DisplayName("Should integrate with external system")
    void shouldIntegrateWithExternalSystem() {
        // Integration test logic
    }
}
```

```xml
<!-- pom.xml - Maven configuration -->
<build>
    <plugins>
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-failsafe-plugin</artifactId>
            <executions>
                <execution>
                    <goals>
                        <goal>integration-test</goal>
                        <goal>verify</goal>
                    </goals>
                </execution>
            </executions>
        </plugin>
    </plugins>
</build>
```

## Integration with Other Skills

**Recommended skill combinations**:

```yaml
# Complete Java testing
skills:
  - cui-java-core           # Java patterns and logging
  - cui-java-unit-testing   # Testing standards (this skill)
  - cui-javadoc             # Test documentation

# CDI/Quarkus testing
skills:
  - cui-java-core
  - cui-java-cdi            # CDI testing patterns
  - cui-java-unit-testing
```

## Common Development Tasks

### Write Unit Tests for New Service

1. Add @EnableGeneratorController to test class
2. Use Generators.* for all test data
3. Follow AAA pattern in each test
4. Add meaningful assertion messages (20-60 chars)
5. Use @DisplayName for test descriptions
6. Verify coverage: `./mvnw clean verify -Pcoverage`

### Add Contract Testing for Value Object

1. Implement `ShouldHandleObjectContracts<T>`
2. Override `getUnderTest()` using generators
3. Run tests - equals/hashCode/toString verified automatically
4. Add business logic tests separately if needed

### Test HTTP Client

1. Add @EnableMockWebServer to test class
2. Inject MockWebServerHolder
3. Enqueue mock responses before making requests
4. Verify request details (headers, body, status)
5. Test error scenarios (404, 500, timeouts)

### Set Up Integration Tests

1. Name test classes with *IT.java suffix
2. Configure Maven failsafe plugin
3. Create integration-tests profile
4. Run: `./mvnw clean verify -Pintegration-tests`

## Prohibited Practices

**DO NOT**:
- Use Mockito, Hamcrest, or PowerMock (use CUI frameworks instead)
- Create manual test data (use Generators.*)
- Commit @GeneratorSeed annotations (debugging only)
- Write tests that depend on execution order
- Hardcode test data values
- Skip assertion messages
- Use field injection in tests

## Verification Checklist

After applying this skill:

**Test Execution**:
- [ ] All tests pass: `./mvnw clean test`
- [ ] Integration tests pass: `./mvnw clean verify -Pintegration-tests`
- [ ] Coverage meets requirements: `./mvnw clean verify -Pcoverage`

**Code Quality**:
- [ ] @EnableGeneratorController present where needed
- [ ] All test data uses Generators.* (no hardcoded values)
- [ ] AAA pattern followed in all tests
- [ ] Assertion messages are meaningful (20-60 characters)
- [ ] @DisplayName used for test descriptions
- [ ] No @GeneratorSeed annotations committed
- [ ] No prohibited libraries (Mockito, Hamcrest, PowerMock)

**Coverage Requirements**:
- [ ] Minimum 80% line coverage
- [ ] Minimum 80% branch coverage
- [ ] Critical paths have 100% coverage
- [ ] All public APIs tested

## Quality Standards

This skill enforces:

- **Test independence**: Tests can run in any order
- **Fast execution**: Unit tests < 1 second each
- **Meaningful assertions**: Clear failure messages
- **Generator usage**: All test data from generators
- **Contract verification**: Automatic for value objects
- **Coverage requirements**: 80% minimum line/branch

## Examples

See `SKILL.md` for comprehensive examples including:

- Basic unit test patterns with AAA structure
- Value object contract testing
- Parameterized tests with @GeneratorsSource
- HTTP client testing with MockWebServer
- Integration test configuration
- Generator composition for complex objects

## Support

For issues or questions:

1. Review detailed standards in `standards/` directory
2. Check `VALIDATION.md` for quality verification
3. Verify prerequisites are met
4. Ensure @EnableGeneratorController is present
5. Check Maven surefire/failsafe configuration

## License

Part of the CUI LLM Rules documentation system for CUI OSS projects.
