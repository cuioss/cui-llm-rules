# Java Null Safety Standards

## Overview

All CUI projects MUST use JSpecify annotations for null safety. This document defines how to apply null safety annotations to ensure robust, null-safe APIs.

## JSpecify Annotations

### Required Library

```xml
<dependency>
    <groupId>org.jspecify</groupId>
    <artifactId>jspecify</artifactId>
</dependency>
```

### Core Annotations

* `@NullMarked` - Marks a package or class where all types are non-null by default
* `@Nullable` - Marks a type as nullable (exception to @NullMarked default)
* `@NonNull` - Explicitly marks a type as non-null (only needed without @NullMarked)

## Package-Level Configuration (PREFERRED)

Always prefer `@NullMarked` in `package-info.java` for consistent null-safety across the entire package.

```java
// package-info.java
/**
 * Token validation and authentication services.
 *
 * <p>All types in this package are non-null by default due to {@code @NullMarked}.
 * Use {@code @Nullable} to explicitly mark nullable types.
 */
@NullMarked
package de.cuioss.portal.authentication;

import org.jspecify.annotations.NullMarked;
```

**Benefits**:
* Consistent null-safety across entire package
* Less annotation noise (default is non-null)
* Clear contract for package APIs
* Easier to maintain

## API Return Type Guidelines

For public API methods with `@NullMarked` at package level, choose one of these patterns:

### Pattern 1: Guaranteed Non-Null Return (Default)

Methods return non-null by default with package-level `@NullMarked`:

```java
/**
 * Validates the JWT token and returns the result.
 *
 * @param token the token to validate, must not be null
 * @return validation result, never null
 */
public ValidationResult validate(String token) {
    // Implementation must ensure non-null return
    return new ValidationResult(token, checkSignature(token));
}
```

### Pattern 2: Optional Result

Use `Optional<T>` when the method may not have a result to return:

```java
/**
 * Finds a user by their unique identifier.
 *
 * @param userId the user identifier, must not be null
 * @return the user if found, or Optional.empty() if not found
 */
public Optional<User> findById(String userId) {
    User user = repository.get(userId);
    return Optional.ofNullable(user);
}
```

### CRITICAL RULE: Never Use @Nullable for Return Types

**NEVER** use `@Nullable` for return types. Either guarantee a non-null return or use Optional.

```java
// ❌ BAD - Never do this
public @Nullable ValidationResult validate(String token) {
    // Nullable returns are forbidden
}

// ✅ GOOD - Guaranteed non-null
public ValidationResult validate(String token) {
    // Must return non-null
}

// ✅ GOOD - Use Optional for "no result" scenarios
public Optional<ValidationResult> tryValidate(String token) {
    // Returns Optional.empty() when no result
}
```

## Null-Safe Implementation Patterns

### With @NullMarked (Package Level)

```java
// With @NullMarked at package level, everything is non-null by default
public class TokenValidator {

    // Field is non-null by default
    private final TokenConfig config;

    // Parameter is non-null by default
    public TokenValidator(TokenConfig config) {
        // No null check needed if caller respects contract
        // But defensive programming is still acceptable:
        this.config = Objects.requireNonNull(config, "config must not be null");
    }

    // Parameter and return are non-null by default
    public ValidationResult validate(String token) {
        Objects.requireNonNull(token, "token must not be null");
        // Implementation must return non-null
        return new ValidationResult(/*...*/);
    }

    // Mark nullable parameters explicitly
    public String processWithDefault(@Nullable String input) {
        return input != null ? input.toUpperCase() : "DEFAULT";
    }

    // Use Optional instead of @Nullable returns
    public Optional<UserInfo> extractUserInfo(String token) {
        return parseToken(token)
            .map(this::extractUser);
    }
}
```

### Without @NullMarked (Explicit Annotations)

If not using package-level `@NullMarked`, you must explicitly annotate:

```java
import org.jspecify.annotations.NonNull;
import org.jspecify.annotations.Nullable;

public class TokenValidator {

    @NonNull
    private final TokenConfig config;

    public TokenValidator(@NonNull TokenConfig config) {
        this.config = config;
    }

    @NonNull
    public ValidationResult validate(@NonNull String token) {
        return new ValidationResult(/*...*/);
    }

    @NonNull
    public String processWithDefault(@Nullable String input) {
        return input != null ? input.toUpperCase() : "DEFAULT";
    }
}
```

## Implementation Requirements

### 1. Package-Level Configuration

* Always prefer `@NullMarked` in `package-info.java`
* Document the null-safety contract in package documentation
* Use `@Nullable` only for exceptions to the non-null default

### 2. Default Non-Null

* With `@NullMarked`, all types are non-null by default
* Only use `@Nullable` for exceptions
* Never annotate with `@NonNull` when using `@NullMarked` (redundant)

### 3. Implementation Responsibility

* The implementation MUST ensure that non-nullable methods never return null
* Add defensive null checks at API boundaries
* Use `Objects.requireNonNull()` for parameter validation

```java
public ValidationResult validate(String token) {
    // Defensive programming at API boundary
    Objects.requireNonNull(token, "token must not be null");

    // Implementation ensures non-null return
    if (isValid(token)) {
        return ValidationResult.valid();
    }
    return ValidationResult.invalid("Token validation failed");
}
```

### 4. Static Analysis

* JSpecify annotations enable static analysis tools to detect potential null pointer issues
* Use IDE null analysis features
* Configure build tools to enforce null safety

### 5. Unit Testing

Test that non-nullable methods never return null under any valid input conditions:

```java
@Test
void shouldNeverReturnNull() {
    // With @NullMarked, non-nullable methods must never return null
    assertNotNull(service.processToken("valid"));
    assertNotNull(service.processToken(""));

    // Non-nullable methods should handle edge cases without returning null
    assertNotNull(service.processToken("edge-case"));
}

@Test
void shouldUseOptionalForMissingValues() {
    // Use Optional.empty() instead of null returns
    assertTrue(service.findUser("unknown").isEmpty());
    assertTrue(service.findUser("existing").isPresent());
}

@Test
void shouldRejectNullParameters() {
    // Non-nullable parameters should be validated
    assertThrows(NullPointerException.class,
        () -> service.processToken(null));
}
```

## Nullable Parameters

Use `@Nullable` sparingly for parameters that genuinely accept null:

```java
// Good - null has clear meaning (use default)
public String format(@Nullable Locale locale) {
    Locale effectiveLocale = locale != null ? locale : Locale.getDefault();
    return formatter.format(effectiveLocale);
}

// Better - use Optional for optional parameters
public String format(Optional<Locale> locale) {
    return formatter.format(locale.orElse(Locale.getDefault()));
}

// Best - overload methods instead of nullable parameters
public String format() {
    return format(Locale.getDefault());
}

public String format(Locale locale) {
    return formatter.format(locale);
}
```

## Collections and Generics

Apply null-safety to collection types:

```java
// With @NullMarked, all elements are non-null
public List<User> getActiveUsers() {
    // Returns non-null list of non-null User objects
    return users.stream()
        .filter(User::isActive)
        .toList();
}

// Use @Nullable for nullable elements
public List<@Nullable String> getOptionalValues() {
    // List is non-null, but elements can be null
    return Arrays.asList("value1", null, "value3");
}

// Optional elements alternative
public List<Optional<String>> getOptionalValues() {
    // List and elements are non-null, empty Optional indicates absence
    return Arrays.asList(
        Optional.of("value1"),
        Optional.empty(),
        Optional.of("value3")
    );
}
```

## Documentation Contract

JSpecify annotations serve as executable documentation of the API contract:

```java
/**
 * Validates a token and extracts user information.
 *
 * <p>With package-level {@code @NullMarked}:
 * <ul>
 *   <li>The {@code token} parameter must not be null (enforced by annotation)</li>
 *   <li>The return value is never null (guaranteed by annotation)</li>
 *   <li>Use {@link Optional} for "no result" scenarios</li>
 * </ul>
 *
 * @param token the token to validate, must not be null
 * @return validation result, never null
 * @throws NullPointerException if token is null
 */
public ValidationResult validate(String token) {
    Objects.requireNonNull(token, "token must not be null");
    // Implementation
}
```

## Migration Strategy

### For New Code

1. Add `@NullMarked` to `package-info.java`
2. Write code assuming non-null by default
3. Use `@Nullable` only where null is explicitly allowed
4. Use `Optional<T>` for "no result" return types
5. Validate with unit tests

### For Existing Code

1. Add `@NullMarked` to package
2. Review all public APIs
3. Add `@Nullable` where null is currently accepted/returned
4. Refactor nullable returns to Optional where appropriate
5. Add null checks with `Objects.requireNonNull()` at API boundaries
6. Update tests to verify null-safety contracts

## Quality Checklist

- [ ] Package has @NullMarked in package-info.java
- [ ] No @Nullable used for return types (use Optional instead)
- [ ] Nullable parameters documented and justified
- [ ] Defensive null checks at API boundaries
- [ ] Unit tests verify non-null contracts (see cui-java-unit-testing skill for testing best practices)
- [ ] Static analysis configured and passing
- [ ] JavaDoc documents null-safety contract
- [ ] Collections specify element nullability if needed
