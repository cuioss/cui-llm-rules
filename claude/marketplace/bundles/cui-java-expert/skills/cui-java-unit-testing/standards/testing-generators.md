# Test Data Generator Standards

## Overview

The CUI Test Generator framework (`cui-test-generator`) is **mandatory** for ALL test data generation in CUI projects. This framework provides robust and reproducible test data generation, combining random data with the ability to reproduce specific test scenarios during debugging.

## Mandatory Requirements

### Required for All Test Data

* **MANDATORY**: Use cui-test-generator for ALL test data generation
* **FORBIDDEN**: Do NOT use manual data creation, Random, Faker, or other data tools
* **REQUIRED ANNOTATION**: `@EnableGeneratorController` MUST be added to every test class using generators
* **GENERATOR METHODS**: Use `Generators.strings()`, `integers()`, `booleans()`, etc. for all values

### Maven Dependency

```xml
<dependency>
    <groupId>de.cuioss.test</groupId>
    <artifactId>cui-test-generator</artifactId>
</dependency>
```

## Basic Generator Usage

### Built-in Generators

```java
@EnableGeneratorController
class GeneratorExamples {

    @Test
    void shouldDemonstrateBasicGenerators() {
        // Basic types
        String text = Generators.strings().next();
        Integer number = Generators.integers().next();
        Boolean flag = Generators.booleans().next();
        LocalDateTime dateTime = Generators.localDateTimes().next();

        // Configured generation
        String letters = Generators.letterStrings(5, 10).next();
        List<Integer> numbers = Generators.integers(1, 100).list(5);
        Float decimal = Generators.floats(0.0f, 100.0f).next();
    }

    @Test
    void shouldUseFixedAndEnumValues() {
        // Fixed values (for controlled variation)
        var urlGen = Generators.fixedValues(String.class,
            "https://cuioss.de", "https://example.com");
        String url = urlGen.next();

        // Enum generation
        var enumGen = Generators.enumValues(TimeUnit.class);
        TimeUnit timeUnit = enumGen.next();
    }
}
```

## Parameterized Tests with Generators

### When to Use Parameterized Tests

Parameterized tests are **mandatory** when testing at least 3 similar variants of the same behavior.

### @GeneratorsSource (Most Preferred)

Use `@GeneratorsSource` with built-in generator types:

```java
@EnableGeneratorController
class ParameterizedGeneratorTests {

    // String generator with parameters
    @ParameterizedTest
    @DisplayName("Should validate strings with length constraints")
    @GeneratorsSource(generator = GeneratorType.STRINGS, minSize = 3, maxSize = 10, count = 5)
    void shouldValidateStringLength(String value) {
        assertTrue(value.length() >= 3 && value.length() <= 10,
            "String should meet length constraints");
    }

    // Number generator with range
    @ParameterizedTest
    @DisplayName("Should process numbers within valid range")
    @GeneratorsSource(generator = GeneratorType.INTEGERS, low = "1", high = "100", count = 5)
    void shouldProcessValidNumbers(Integer value) {
        assertTrue(value >= 1 && value <= 100,
            "Number should be within valid range");
    }

    // Simple generator without parameters
    @ParameterizedTest
    @GeneratorsSource(generator = GeneratorType.NON_EMPTY_STRINGS, count = 3)
    void shouldHandleNonEmptyStrings(String value) {
        assertFalse(value.isEmpty(), "String should not be empty");
    }

    // Domain-specific generators
    @ParameterizedTest
    @GeneratorsSource(generator = GeneratorType.DOMAIN_EMAIL, count = 3)
    void shouldValidateEmailFormat(String email) {
        assertTrue(email.contains("@"), "Email should contain @");
    }
}
```

### @CompositeTypeGeneratorSource (Highly Preferred)

Use for testing with multiple related types:

```java
@EnableGeneratorController
class CompositeGeneratorTests {

    // Multiple generators combined
    @ParameterizedTest
    @DisplayName("Should process text and number combinations")
    @CompositeTypeGeneratorSource(
        generators = {GeneratorType.NON_EMPTY_STRINGS, GeneratorType.INTEGERS},
        count = 3
    )
    void shouldProcessCombinations(String text, Integer number) {
        assertNotNull(text, "Text should not be null");
        assertNotNull(number, "Number should not be null");
    }

    // Domain-specific combinations
    @ParameterizedTest
    @DisplayName("Should validate user contact information")
    @CompositeTypeGeneratorSource(
        generators = {GeneratorType.DOMAIN_EMAIL, GeneratorType.DOMAIN_ZIP_CODE},
        count = 3
    )
    void shouldValidateContactInfo(String email, String zipCode) {
        assertTrue(email.contains("@"), "Email should be valid");
        assertNotNull(zipCode, "Zip code should not be null");
    }
}
```

### Custom Type Generators

For complex domain objects, create custom TypeGenerator implementations:

```java
public class TokenConfigGenerator implements TypedGenerator<TokenConfig> {

    @Override
    public TokenConfig next() {
        return TokenConfig.builder()
            .issuer(Generators.strings().next())
            .clientId(Generators.strings().next())
            .audience(Generators.fixedValues(String.class, "api", "web").next())
            .expirationMinutes(Generators.integers(1, 60).next())
            .build();
    }

    @Override
    public Class<TokenConfig> getType() {
        return TokenConfig.class;
    }
}

@EnableGeneratorController
class TokenConfigTest {

    @ParameterizedTest
    @DisplayName("Should validate tokens with different configurations")
    @TypeGeneratorSource(value = TokenConfigGenerator.class, count = 5)
    void shouldValidateWithDifferentConfigs(TokenConfig config) {
        assertDoesNotThrow(() -> validator.validate(token, config),
            "Valid configuration should pass validation");
    }
}
```

## Test Reproducibility

### Seed Usage Restrictions

**CRITICAL RULES:**

* **Fixed seeds are ONLY for reproducing test failures during debugging**
* **NEVER commit tests with hardcoded @GeneratorSeed values**
* **REMOVE all @GeneratorSeed annotations before check-in/commit**
* **Use seeds temporarily for local debugging only**

Fixed seeds defeat the purpose of random testing and reduce test coverage over time.

**Temporary Seed Usage Example (Debugging Only):**

```java
@EnableGeneratorController
@GeneratorSeed(8042L) // Class-level seed - REMOVE BEFORE COMMIT!
class ReproducibleTest {

    @Test
    @GeneratorSeed(4711L) // Method-level override - REMOVE BEFORE COMMIT!
    void shouldGenerateSpecificData() {
        String data = Generators.strings().next(); // Always same data for debugging
        // Debug the test failure, then REMOVE @GeneratorSeed annotation
    }
}
```

## Generator Composition

### Combining Multiple Generators

```java
@EnableGeneratorController
class GeneratorCompositionTest {

    @Test
    void shouldComposeComplexObjects() {
        User user = User.builder()
            .username(Generators.strings(5, 20).next())
            .email(Generators.emailAddress().next())
            .age(Generators.integers(18, 100).next())
            .roles(Generators.fixedValues(Role.class, Role.USER, Role.ADMIN).list(2))
            .createdAt(Generators.localDateTimes().next())
            .build();

        assertNotNull(user, "Generated user should not be null");
    }

    @Test
    void shouldGenerateLists() {
        // Generate list of values
        List<String> usernames = Generators.strings(5, 15).list(10);
        assertEquals(10, usernames.size(), "Should generate 10 usernames");

        // Generate list with specific range
        List<Integer> ages = Generators.integers(18, 65).list(5);
        assertTrue(ages.stream().allMatch(age -> age >= 18 && age <= 65),
            "All ages should be within range");
    }
}
```

## Common Generator Types

### String Generators

```java
Generators.strings()              // Any string
Generators.strings(5, 10)         // String with length 5-10
Generators.letterStrings(5, 10)   // Letters only, length 5-10
Generators.nonEmptyStrings()      // Non-empty strings
Generators.emailAddress()         // Valid email addresses
```

### Numeric Generators

```java
Generators.integers()             // Any integer
Generators.integers(1, 100)       // Integer between 1 and 100
Generators.floats(0.0f, 1.0f)    // Float between 0.0 and 1.0
Generators.doubles(0.0, 1.0)     // Double between 0.0 and 1.0
Generators.longs()                // Any long
```

### Date/Time Generators

```java
Generators.localDateTimes()       // Any LocalDateTime
Generators.localDates()           // Any LocalDate
Generators.instants()             // Any Instant
```

### Collection Generators

```java
generator.list(5)                 // Generate list of 5 elements
generator.set(5)                  // Generate set of 5 elements
```

## Anti-Patterns to Avoid

### ❌ Manual Data Creation

```java
// WRONG - Manual data creation
@Test
void shouldValidateUser() {
    User user = new User("john.doe", "john@example.com", 30);
    // This is hardcoded and doesn't test variability
}

// CORRECT - Generator-based
@Test
void shouldValidateUser() {
    User user = new User(
        Generators.strings().next(),
        Generators.emailAddress().next(),
        Generators.integers(18, 100).next()
    );
}
```

### ❌ Using Java Random or Other Libraries

```java
// WRONG - Using Random
@Test
void shouldProcessRandomData() {
    Random random = new Random();
    String value = "test-" + random.nextInt();
    // Not reproducible, not integrated with framework
}

// WRONG - Using Faker or other tools
@Test
void shouldProcessFakeData() {
    Faker faker = new Faker();
    String name = faker.name().firstName();
    // Wrong framework, inconsistent with CUI standards
}
```

### ❌ Committed Generator Seeds

```java
// WRONG - Never commit this!
@EnableGeneratorController
@GeneratorSeed(42L) // DO NOT COMMIT - defeats random testing
class UserTest {
    // Tests always run with same data
}
```

## Migration from Manual Data

When migrating existing tests:

1. **Identify Violations**: Find manual data creation, hardcoded values, non-CUI frameworks
2. **Apply Generators**: Replace with appropriate Generators.* calls
3. **Add Annotations**: Ensure @EnableGeneratorController is present
4. **Verify Tests**: Ensure all tests pass with generated data
5. **Remove Seeds**: Remove any @GeneratorSeed annotations used during debugging

For general test quality requirements including naming, documentation, and code quality standards, see [testing-junit-core.md](testing-junit-core.md).

## Additional Resources

* CUI Test Generator Framework: https://github.com/cuioss/cui-test-generator
* Complete Usage Guide: https://gitingest.com/github.com/cuioss/cui-test-generator
