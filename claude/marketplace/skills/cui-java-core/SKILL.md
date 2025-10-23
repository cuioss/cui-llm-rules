---
name: cui-java-core
description: Core Java development standards for CUI projects including coding patterns, null safety, Lombok, modern features, DSL constants, and logging
tools: [Read, Edit, Write, Bash, Grep, Glob]
---

# CUI Java Core Development Skill

Foundational Java development standards for all CUI projects, covering core patterns, null safety, Lombok usage, modern Java features, DSL-style constants, and the CUI logging framework.

## Workflow

### Step 1: Load Core Java Standards

**CRITICAL**: Load all foundational Java standards (always required for Java development).

```
Read: standards/java-core-patterns.md
Read: standards/java-null-safety.md
Read: standards/java-lombok-patterns.md
Read: standards/java-modern-features.md
Read: standards/dsl-constants.md
Read: standards/logging-standards.md
```

These standards are fundamental to all CUI Java development and should be loaded together for consistent, comprehensive guidance.

### Step 2: Extract Key Requirements

From all loaded standards, extract and organize:

1. **Core Patterns**:
   - Code organization (packages, classes, methods)
   - Naming conventions
   - Exception handling patterns
   - Best practices for immutability and collections
   - Parameter object guidelines

2. **Null Safety**:
   - @NullMarked package configuration
   - API return type patterns (non-null vs Optional)
   - Implementation requirements
   - Nullable parameter handling

3. **Lombok Patterns**:
   - @Delegate for delegation over inheritance
   - @Builder for complex objects
   - @Value for immutable objects
   - When to use each annotation

4. **Modern Features**:
   - Records for data carriers
   - Switch expressions
   - Stream processing patterns
   - Text blocks and pattern matching
   - Optional enhancements

5. **DSL Constants**:
   - Hierarchical organization with nested static classes
   - @UtilityClass usage
   - Naming conventions
   - Static import patterns

6. **Logging**:
   - CuiLogger configuration
   - LogRecord usage and organization
   - Log level guidelines
   - Exception logging patterns

### Step 3: Analyze Existing Code (if applicable)

If working with existing Java code:

1. **Assess standards compliance**:
   - Check null-safety annotations (@NullMarked in package-info.java)
   - Verify logger configuration (CuiLogger, not SLF4J)
   - Review Lombok usage (appropriate annotations)
   - Check for modern Java features (records, switch expressions)
   - Verify DSL-style constants organization
   - Review exception handling patterns

2. **Identify improvement opportunities**:
   - Missing null-safety annotations
   - Legacy logging (System.out, SLF4J annotations)
   - Inefficient patterns (deep inheritance, god classes)
   - Missing modern features (classic switch, manual data classes)
   - Flat constant organization
   - Verbose boilerplate that Lombok could handle

3. **Check code organization**:
   - Package structure (feature-based)
   - Class responsibilities (Single Responsibility Principle)
   - Method sizes (< 50 lines preferred)
   - Parameter counts (≤ 3 preferred)

### Step 4: Write/Refactor Java Code According to Standards

When writing or refactoring Java code:

1. **Apply core patterns**:
   - Organize packages by feature
   - Keep classes focused and small
   - Use meaningful names throughout
   - Handle exceptions appropriately
   - Prefer immutability
   - Use parameter objects for 3+ parameters

2. **Implement null safety**:
   - Add @NullMarked to package-info.java
   - Never use @Nullable for return types (use Optional instead)
   - Add defensive null checks at API boundaries
   - Use Objects.requireNonNull() for validation
   - Document null-safety contracts

3. **Use Lombok appropriately**:
   - @Delegate for composition over inheritance
   - @Builder for classes with 3+ parameters or optional parameters
   - @Value for immutable value objects and DTOs
   - @UtilityClass for utility classes
   - Consider records vs @Value for simple data carriers

4. **Apply modern Java features**:
   - Use records for simple immutable data carriers
   - Replace classic switch with switch expressions
   - Use streams for complex data transformations
   - Apply text blocks for multi-line strings
   - Use pattern matching for instanceof
   - Leverage modern collection factories (List.of(), Set.of())

5. **Organize constants properly**:
   - Use DSL-style nested structure for related constants
   - Apply @UtilityClass at all levels
   - Group by logical dimensions (log level, feature, etc.)
   - Keep hierarchy depth reasonable (≤ 4 levels)
   - Use static imports at category level

6. **Implement CUI logging**:
   - Declare logger: `private static final CuiLogger LOGGER = new CuiLogger(YourClass.class);`
   - Create LogMessages class for structured logging
   - Use LogRecord for INFO/WARN/ERROR/FATAL
   - Exception parameter always comes first
   - Use %s for all string substitutions
   - Organize identifiers by log level ranges

### Step 5: Verify Standards Compliance

Before completing the task:

1. **Core patterns check**:
   - [ ] Classes follow Single Responsibility Principle
   - [ ] Methods are short and focused (< 50 lines)
   - [ ] Meaningful names used throughout
   - [ ] Exception handling is appropriate
   - [ ] Immutability used where possible
   - [ ] No magic numbers or god classes

2. **Null safety check**:
   - [ ] @NullMarked in package-info.java
   - [ ] No @Nullable used for return types
   - [ ] Optional used for "no result" scenarios
   - [ ] Defensive null checks at API boundaries
   - [ ] Unit tests verify non-null contracts

3. **Lombok check**:
   - [ ] @Builder used for complex construction
   - [ ] @Value used for immutable objects
   - [ ] @Delegate used for composition
   - [ ] No @Slf4j or logging annotations (use CuiLogger)

4. **Modern features check**:
   - [ ] Records used for simple data carriers
   - [ ] Switch expressions used instead of statements
   - [ ] Streams used appropriately
   - [ ] Text blocks used for multi-line strings
   - [ ] Modern collection factories used

5. **DSL constants check**:
   - [ ] Related constants organized hierarchically
   - [ ] @UtilityClass used at all levels
   - [ ] Consistent naming conventions
   - [ ] Static imports at category level

6. **Logging check**:
   - [ ] CuiLogger used (not SLF4J/Log4j)
   - [ ] Logger is private static final named LOGGER
   - [ ] LogRecord used for important messages
   - [ ] LogMessages follows DSL pattern
   - [ ] Exception parameter comes first
   - [ ] %s used for substitutions
   - [ ] No System.out or System.err

7. **Run build and tests**:
   ```bash
   ./mvnw clean verify
   ```

### Step 6: Report Results

Provide summary of:

1. **Standards applied**: Which core Java standards were followed
2. **Code improvements**: Changes made to align with standards
3. **Null safety**: Package-level @NullMarked and Optional usage
4. **Lombok usage**: Which annotations were applied and why
5. **Modern features**: Records, switch expressions, streams implemented
6. **DSL constants**: Hierarchical organization applied
7. **Logging**: CuiLogger and LogRecord implementation
8. **Build verification**: Confirm successful build and test execution

## Common Patterns and Examples

### Complete Class Example

```java
// package-info.java
@NullMarked
package de.cuioss.portal.authentication;

import org.jspecify.annotations.NullMarked;

// TokenValidator.java
import de.cuioss.tools.logging.CuiLogger;
import static de.cuioss.portal.authentication.TokenLogMessages.INFO;
import static de.cuioss.portal.authentication.TokenLogMessages.ERROR;

@Value
@Builder
public class TokenValidator {
    private static final CuiLogger LOGGER = new CuiLogger(TokenValidator.class);

    String issuer;
    @Builder.Default
    Duration validity = Duration.ofHours(1);

    public ValidationResult validate(String token) {
        Objects.requireNonNull(token, "token must not be null");

        try {
            String userId = extractUserId(token);
            boolean isValid = performValidation(token);

            if (isValid) {
                LOGGER.info(INFO.VALIDATION_SUCCESS, userId);
                return ValidationResult.valid();
            }

            LOGGER.error(ERROR.VALIDATION_FAILED, userId, "Invalid signature");
            return ValidationResult.invalid("Invalid signature");

        } catch (TokenException e) {
            LOGGER.error(e, ERROR.VALIDATION_FAILED, "unknown", e.getMessage());
            throw new ValidationException("Validation failed", e);
        }
    }

    public Optional<UserInfo> extractUserInfo(String token) {
        return parseToken(token).map(this::extractUser);
    }
}
```

### LogMessages Example

```java
@UtilityClass
public final class TokenLogMessages {
    public static final String PREFIX = "TOKEN";

    @UtilityClass
    public static final class INFO {
        public static final LogRecord VALIDATION_SUCCESS = LogRecordModel.builder()
            .template("Token validated successfully for user %s")
            .prefix(PREFIX)
            .identifier(1)
            .build();
    }

    @UtilityClass
    public static final class ERROR {
        public static final LogRecord VALIDATION_FAILED = LogRecordModel.builder()
            .template("Token validation failed for user %s: %s")
            .prefix(PREFIX)
            .identifier(200)
            .build();
    }
}
```

### Record with Validation Example

```java
public record TokenConfig(String issuer, Duration validity, Set<String> requiredClaims) {
    public TokenConfig {
        Objects.requireNonNull(issuer, "issuer must not be null");
        Objects.requireNonNull(validity, "validity must not be null");
        if (validity.isNegative() || validity.isZero()) {
            throw new IllegalArgumentException("Validity must be positive");
        }
        requiredClaims = Set.copyOf(requiredClaims);  // Defensive copy
    }

    public static TokenConfig defaultConfig() {
        return new TokenConfig(
            "https://auth.example.com",
            Duration.ofHours(1),
            Set.of("sub", "exp")
        );
    }
}
```

### Delegation Example

```java
public class CachedTokenValidator implements TokenValidator {
    @Delegate
    private final TokenValidator delegate;
    private final Cache<String, ValidationResult> cache;

    public CachedTokenValidator(TokenValidator delegate) {
        this.delegate = delegate;
        this.cache = CacheBuilder.newBuilder()
            .expireAfterWrite(Duration.ofMinutes(5))
            .build();
    }

    @Override
    public ValidationResult validate(String token) {
        return cache.get(token, () -> delegate.validate(token));
    }
}
```

### Switch Expression Example

```java
ValidationResult validate(Token token) {
    return switch (token.getType()) {
        case JWT -> jwtValidator.validate(token);
        case OAUTH2 -> oauth2Validator.validate(token);
        case LEGACY -> ValidationResult.invalid("Legacy tokens not supported");
    };
}
```

### Stream Processing Example

```java
List<String> activeUserNames = users.stream()
    .filter(User::isActive)
    .map(User::getName)
    .sorted()
    .toList();

Map<String, List<User>> usersByRole = users.stream()
    .collect(Collectors.groupingBy(User::getRole));
```

## Common Development Tasks

### Task: Create a new service class

1. Load all core Java standards
2. Add @NullMarked to package-info.java
3. Define class with appropriate Lombok annotations (@Value/@Builder if immutable)
4. Declare CuiLogger
5. Create LogMessages class following DSL pattern
6. Implement methods with proper null safety
7. Use modern Java features (records for DTOs, switch expressions, streams)
8. Write unit tests verifying behavior
9. Run build: `./mvnw clean verify`

### Task: Refactor existing code to standards

1. Load all core Java standards
2. Add @NullMarked to package-info.java if missing
3. Replace SLF4J/Log4j with CuiLogger
4. Convert flat constants to DSL-style nested structure
5. Apply Lombok where appropriate (@Builder, @Value, @Delegate)
6. Replace classic patterns with modern features (records, switch expressions)
7. Add null checks at API boundaries
8. Update tests to verify compliance
9. Run build and verify no regressions

### Task: Add comprehensive logging

1. Load logging standards
2. Create LogMessages class with DSL structure
3. Define LogRecord for each important message
4. Organize by log level (INFO, WARN, ERROR, FATAL)
5. Use correct identifier ranges
6. Apply static imports in service classes
7. Use LogRecord with proper exception handling
8. Add test verification for log messages
9. Verify no System.out or System.err usage

## Error Handling

If encountering issues:

1. **Null pointer exceptions**: Review null-safety implementation, add @NullMarked and defensive checks
2. **Lombok not working**: Check Lombok dependency, IDE plugin, and annotation placement
3. **Logger errors**: Verify CuiLogger setup, check exception parameter order and %s usage
4. **Build failures**: Check modern Java feature compatibility with target Java version
5. **Complex refactoring**: Break into smaller steps, focus on one standard at a time

## References

* Core Patterns: standards/java-core-patterns.md
* Null Safety: standards/java-null-safety.md
* Lombok Patterns: standards/java-lombok-patterns.md
* Modern Features: standards/java-modern-features.md
* DSL Constants: standards/dsl-constants.md
* Logging: standards/logging-standards.md
