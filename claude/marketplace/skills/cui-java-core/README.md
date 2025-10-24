# CUI Java Core Development Skill

Core Java development standards and patterns for all CUI projects.

## Overview

The `cui-java-core` skill provides comprehensive Java development standards covering:

- **Core Patterns**: Code organization, naming conventions, exception handling, best practices
- **Null Safety**: JSpecify annotations, package-level @NullMarked, API contract patterns
- **Lombok Patterns**: @Delegate, @Builder, @Value, composition over inheritance
- **Modern Features**: Records, switch expressions, streams, text blocks, pattern matching
- **DSL Constants**: Hierarchical constant organization with nested static classes
- **Logging**: CuiLogger framework, LogRecord usage, structured logging patterns

## When to Use This Skill

Use `cui-java-core` when:

- Starting a new Java project in the CUI ecosystem
- Writing or refactoring Java code for CUI projects
- Implementing core Java classes and services
- Setting up logging infrastructure
- Organizing constants and configuration
- Modernizing legacy Java code to use current best practices

This skill provides the **foundation** for all Java development in CUI projects. It should be used alongside other specialized skills:

- `cui-java-unit-testing` - For comprehensive testing standards
- `cui-java-cdi` - For CDI/dependency injection patterns
- `cui-javadoc` - For API documentation standards

## Prerequisites

**Required**:
- Java 17 or later
- Maven build system
- Lombok library
- JSpecify annotations library
- cui-java-tools (for CuiLogger)

**Recommended IDE Setup**:
- Lombok plugin installed
- Null-safety analysis enabled
- Code formatter configured for CUI standards

## Standards Included

### 1. Core Patterns (`java-core-patterns.md`)
- Package structure (feature-based organization)
- Class design (Single Responsibility Principle)
- Method design (< 50 lines, Command-Query Separation)
- Parameter objects (for 3+ parameters)
- Naming conventions
- Exception handling
- Immutability and collection usage
- Design preferences (delegation over inheritance)

### 2. Null Safety (`java-null-safety.md`)
- JSpecify @NullMarked at package level
- API return type patterns (non-null by default)
- Never use @Nullable for returns (use Optional)
- Defensive null checks with Objects.requireNonNull()
- Collection nullability annotations
- Testing null-safety contracts

### 3. Lombok Patterns (`java-lombok-patterns.md`)
- @Delegate for composition
- @Builder for complex objects (3+ parameters, optional fields)
- @Value for immutable objects
- @UtilityClass for utility classes
- Records vs @Value guidance
- **DO NOT use @Slf4j** (use CuiLogger instead)

### 4. Modern Features (`java-modern-features.md`)
- Records for simple data carriers
- Switch expressions (not statements)
- Stream processing patterns
- Text blocks for multi-line strings
- Pattern matching for instanceof
- Sealed classes for restricted hierarchies
- Optional API enhancements
- Modern collection factories (List.of, Set.of, Map.of)
- var for local variables

### 5. DSL Constants (`dsl-constants.md`)
- Hierarchical organization with nested static classes
- @UtilityClass at all levels
- Static imports at category level
- Logical grouping by dimensions
- Maximum 4 levels of nesting
- Self-documenting structure

### 6. Logging Standards (`logging-standards.md`)
- CuiLogger (not SLF4J or Log4j)
- Logger: `private static final CuiLogger LOGGER = new CuiLogger(Class.class)`
- LogRecord for structured logging
- LogMessages class with DSL pattern
- Exception parameter always first
- Use %s for all substitutions
- Message identifier ranges by log level
- Testing with cui-test-juli-logger
- **NO System.out/System.err**

## Quick Start

### 1. Set Up Package-Level Null Safety

```java
// package-info.java
/**
 * Authentication services.
 *
 * <p>All types are non-null by default due to {@code @NullMarked}.
 */
@NullMarked
package de.cuioss.portal.authentication;

import org.jspecify.annotations.NullMarked;
```

### 2. Create Service with Logging

```java
import de.cuioss.tools.logging.CuiLogger;
import static de.cuioss.portal.authentication.AuthLogMessages.INFO;
import static de.cuioss.portal.authentication.AuthLogMessages.ERROR;

public class AuthenticationService {
    private static final CuiLogger LOGGER = new CuiLogger(AuthenticationService.class);

    public AuthResult authenticate(String username, String password) {
        Objects.requireNonNull(username, "username must not be null");
        Objects.requireNonNull(password, "password must not be null");

        try {
            // Authentication logic
            LOGGER.info(INFO.USER_LOGIN, username);
            return AuthResult.success(username);
        } catch (DatabaseException e) {
            LOGGER.error(e, ERROR.DATABASE_ERROR, e.getMessage());
            return AuthResult.failure("Authentication failed");
        }
    }
}
```

### 3. Create LogMessages Class

```java
@UtilityClass
public final class AuthLogMessages {
    public static final String PREFIX = "AUTH";

    @UtilityClass
    public static final class INFO {
        public static final LogRecord USER_LOGIN = LogRecordModel.builder()
            .template("User %s logged in successfully")
            .prefix(PREFIX)
            .identifier(1)
            .build();
    }

    @UtilityClass
    public static final class ERROR {
        public static final LogRecord DATABASE_ERROR = LogRecordModel.builder()
            .template("Database connection failed: %s")
            .prefix(PREFIX)
            .identifier(200)
            .build();
    }
}
```

### 4. Use Records and Modern Features

```java
// Simple immutable data carrier
public record AuthResult(boolean success, String username, List<String> errors) {
    // Compact constructor for validation
    public AuthResult {
        errors = List.copyOf(errors);  // Defensive copy
    }

    public static AuthResult success(String username) {
        return new AuthResult(true, username, List.of());
    }

    public static AuthResult failure(String... errors) {
        return new AuthResult(false, "", List.of(errors));
    }
}

// Use switch expressions
String processResult(AuthResult result) {
    return switch (result.success()) {
        case true -> "Welcome, " + result.username();
        case false -> "Authentication failed: " + String.join(", ", result.errors());
    };
}
```

## Common Development Tasks

### Create a New Service Class

1. Add @NullMarked to package-info.java
2. Define class with appropriate structure
3. Declare CuiLogger
4. Create LogMessages class with DSL pattern
5. Implement methods with null-safety
6. Use modern Java features (records, switch expressions)
7. Write unit tests
8. Run: `./mvnw clean verify`

### Refactor Legacy Code

1. Add @NullMarked to package
2. Replace System.out/SLF4J with CuiLogger
3. Convert flat constants to DSL-style nested structure
4. Apply Lombok (@Builder, @Value, @Delegate)
5. Replace classic patterns with modern features
6. Add defensive null checks
7. Update tests
8. Verify: `./mvnw clean verify`

### Add Comprehensive Logging

1. Create LogMessages class with DSL structure
2. Define LogRecord for each important message
3. Organize by log level (INFO 1-99, WARN 100-199, ERROR 200-299, FATAL 300-399)
4. Use static imports in service classes
5. Apply LogRecord with proper exception handling
6. Add test verification
7. Eliminate all System.out/System.err

## Integration with Other Skills

**Recommended skill combinations**:

```yaml
# For complete Java development
skills:
  - cui-java-core          # Foundation (this skill)
  - cui-java-unit-testing  # Testing standards
  - cui-javadoc            # API documentation

# For CDI/Quarkus projects
skills:
  - cui-java-core
  - cui-java-cdi           # Dependency injection patterns
  - cui-java-unit-testing

# For frontend integration
skills:
  - cui-java-core
  - cui-frontend-development  # JavaScript/Web Components
```

## Verification Checklist

After applying this skill, verify:

- [ ] @NullMarked present in package-info.java
- [ ] CuiLogger declared (not SLF4J)
- [ ] LogMessages class follows DSL pattern
- [ ] No @Nullable used for return types (use Optional)
- [ ] Records used for simple data carriers
- [ ] Switch expressions used (not statements)
- [ ] @Builder used for classes with 3+ parameters
- [ ] @Delegate used instead of inheritance
- [ ] Constants organized hierarchically
- [ ] No System.out or System.err usage
- [ ] Exception parameter comes first in logging
- [ ] %s used for all log substitutions
- [ ] Build passes: `./mvnw clean verify`

## Quality Standards

This skill enforces:

- **Code readability**: Self-documenting code with clear names
- **Maintainability**: Small, focused classes and methods (< 50 lines)
- **Consistency**: Uniform patterns across codebase
- **Testability**: Designs that facilitate testing
- **Type safety**: Compile-time verification of null contracts
- **Modern Java**: Use latest language features for clarity

## Examples

See `SKILL.md` for comprehensive examples including:

- Complete class examples integrating all patterns
- LogMessages examples with DSL structure
- Record validation patterns
- Delegation with @Delegate
- Switch expressions for validation
- Stream processing patterns
- Parameter objects
- Null-safety implementation

## Support

For issues or questions:

1. Review the detailed standards in the `standards/` directory
2. Check code examples in `SKILL.md`
3. Verify quality checklist at end of each standard
4. Ensure prerequisites are met (Java 17+, Lombok, JSpecify)

## License

Part of the CUI LLM Rules documentation system for CUI OSS projects.