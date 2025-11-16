# Java Lombok Patterns

## Required Imports

```java
// Lombok Core
import lombok.Builder;
import lombok.Value;
import lombok.Data;
import lombok.Getter;
import lombok.Setter;

// Lombok Advanced
import lombok.Delegate;
import lombok.Singular;
import lombok.experimental.UtilityClass;
import lombok.Builder.Default;

// Guava (for delegation caching pattern)
import com.google.common.cache.Cache;
import com.google.common.cache.CacheBuilder;
```

## Overview

Use Lombok annotations to reduce boilerplate code in CUI projects. This document defines when and how to use Lombok effectively.

## Core Lombok Annotations

### @Delegate - Delegation Over Inheritance

Use `@Delegate` for delegation patterns instead of inheritance:

```java
// ✅ Good - delegation with Lombok
public class CachedTokenValidator implements TokenValidator {
    @Delegate
    private final TokenValidator delegate;
    private final Cache<String, ValidationResult> cache;

    public CachedTokenValidator(TokenValidator delegate) {
        this.delegate = delegate;
        this.cache = CacheBuilder.newBuilder().build();
    }

    // Override only methods that need caching
    @Override
    public ValidationResult validate(String token) {
        return cache.get(token, () -> delegate.validate(token));
    }
}

// ❌ Avoid - inheritance
public class CachedTokenValidator extends BaseTokenValidator {
    // Tight coupling, harder to test
}
```

**When to use @Delegate**:
* Implementing interfaces through composition
* Wrapping existing implementations
* Adding cross-cutting concerns (caching, logging, metrics)
* Avoiding inheritance hierarchies

### @Builder - Building Complex Objects

Use `@Builder` for classes with multiple optional parameters:

```java
@Builder
public class TokenConfig {
    private final String issuer;
    private final String audience;
    private final Duration validity;
    private final int clockSkewSeconds;
    private final Set<String> requiredClaims;

    // Lombok generates builder class
}

// Usage
TokenConfig config = TokenConfig.builder()
    .issuer("https://auth.example.com")
    .audience("my-api")
    .validity(Duration.ofHours(1))
    .clockSkewSeconds(30)
    .requiredClaims(Set.of("sub", "exp"))
    .build();
```

**@Builder features**:
```java
@Builder(toBuilder = true)  // Enables toBuilder() method for copies
public class TokenConfig {
    @Builder.Default  // Provides default value
    private final int clockSkewSeconds = 30;

    @Singular  // Generates add methods for collections
    private final Set<String> requiredClaims;
}

// Usage with @Singular
TokenConfig config = TokenConfig.builder()
    .issuer("https://auth.example.com")
    .requiredClaim("sub")  // Singular method
    .requiredClaim("exp")  // Can call multiple times
    .build();

// Usage with toBuilder()
TokenConfig modified = config.toBuilder()
    .validity(Duration.ofHours(2))
    .build();
```

**When to use @Builder**:
* Classes with 3+ constructor parameters
* Classes with optional parameters
* Immutable configuration objects
* DTOs and value objects with many fields

### @Value - Immutable Objects

Use `@Value` for immutable value objects and DTOs:

```java
@Value
public class ValidationResult {
    boolean valid;
    List<String> errors;
    Instant validatedAt;

    // Lombok generates:
    // - All-args constructor
    // - Getters (no setters)
    // - equals() and hashCode()
    // - toString()
    // - All fields are private final
}

// Usage
ValidationResult result = new ValidationResult(
    true,
    List.of(),
    Instant.now()
);

// All getters available
boolean isValid = result.isValid();
List<String> errors = result.getErrors();
```

**@Value is equivalent to**:
```java
@Getter
@FieldDefaults(makeFinal = true, level = AccessLevel.PRIVATE)
@AllArgsConstructor
@ToString
@EqualsAndHashCode
public class ValidationResult {
    // fields
}
```

**When to use @Value**:
* Immutable data transfer objects (DTOs)
* Value objects in domain model
* API response/request objects
* Configuration data classes

**When to use records instead**: For detailed comparison of records vs Lombok @Value, see [java-modern-features.md](java-modern-features.md) section "When to Use Records vs Lombok @Value".

## Additional Lombok Annotations

### @Data - Mutable Objects

Use `@Data` for mutable Java beans (use sparingly, prefer immutability):

```java
@Data
public class UserPreferences {
    private String theme;
    private Locale locale;
    private int pageSize;

    // Lombok generates:
    // - Getters and setters
    // - equals() and hashCode()
    // - toString()
    // - Required args constructor
}
```

**Note**: Prefer `@Value` or records for immutable objects. Use `@Data` only when mutability is genuinely required.

### @UtilityClass - Utility Classes

Use `@UtilityClass` for utility classes with only static methods:

```java
@UtilityClass
public class TokenUtils {
    public static String extractTokenId(String token) {
        // Implementation
    }

    public static boolean isExpired(String token) {
        // Implementation
    }

    // Lombok:
    // - Makes class final
    // - Makes constructor private
    // - Makes all methods static (if not already)
}
```

### @Slf4j - Logging (DO NOT USE in CUI Projects)

**IMPORTANT**: Do NOT use `@Slf4j` or similar logging annotations in CUI projects.

```java
// ❌ WRONG - Do not use Lombok logging annotations
@Slf4j
public class TokenValidator {
    // log field is generated, but wrong logger
}

// ✅ CORRECT - Use CuiLogger explicitly
public class TokenValidator {
    private static final CuiLogger LOGGER = new CuiLogger(TokenValidator.class);
}
```

**Reason**: CUI projects use `CuiLogger`, not SLF4J. See `logging-standards.md` in this skill for details.

## Combining Annotations

Lombok annotations can be combined effectively:

```java
@Value
@Builder
public class TokenConfig {
    String issuer;
    String audience;

    @Builder.Default
    Duration validity = Duration.ofHours(1);

    @Singular
    Set<String> requiredClaims;
}

// Usage
TokenConfig config = TokenConfig.builder()
    .issuer("https://auth.example.com")
    .audience("my-api")
    .requiredClaim("sub")
    .requiredClaim("exp")
    .build();
```

## Best Practices

### 1. Prefer Immutability

```java
// ✅ Good - immutable with @Value
@Value
@Builder
public class User {
    String id;
    String name;
    String email;
}

// ❌ Avoid - mutable with @Data
@Data
public class User {
    String id;
    String name;
    String email;
    // Setters allow mutation
}
```

### 2. Use @Builder for Complex Objects

```java
// ✅ Good - builder for multiple parameters
@Value
@Builder
public class SearchCriteria {
    String query;
    int maxResults;
    Set<String> categories;
    LocalDate startDate;
    LocalDate endDate;
}

// ❌ Avoid - constructor with many parameters
@Value
public class SearchCriteria {
    String query;
    int maxResults;
    Set<String> categories;
    LocalDate startDate;
    LocalDate endDate;

    // Long constructor is hard to use
    public SearchCriteria(String query, int maxResults,
                         Set<String> categories, LocalDate startDate,
                         LocalDate endDate) {
        // ...
    }
}
```

### 3. Use @Delegate for Composition

```java
// ✅ Good - composition with @Delegate
public class RateLimitedValidator implements TokenValidator {
    @Delegate
    private final TokenValidator delegate;
    private final RateLimiter rateLimiter;

    @Override
    public ValidationResult validate(String token) {
        rateLimiter.checkLimit();
        return delegate.validate(token);
    }
}
```

### 4. Provide Defaults with @Builder

```java
@Value
@Builder
public class HttpConfig {
    @Builder.Default
    int connectTimeout = 5000;

    @Builder.Default
    int readTimeout = 30000;

    @Builder.Default
    boolean followRedirects = true;
}

// Usage - only override what's needed
HttpConfig config = HttpConfig.builder()
    .connectTimeout(10000)  // Override
    .build();  // Others use defaults
```

## Lombok vs Records

For simple immutable data carriers, prefer records (Java 17+):

```java
// ✅ Prefer records for simple cases
public record User(String id, String name, String email) {}

// Use Lombok when you need:
// - @Builder for complex construction
// - @Delegate for composition
// - Additional annotations like @JsonProperty
@Value
@Builder
@JsonIgnoreProperties(ignoreUnknown = true)
public class ApiResponse {
    @JsonProperty("user_id")
    String userId;

    String status;

    @Singular
    List<String> messages;
}
```

## Common Pitfalls

### 1. Overusing @Data

```java
// ❌ Bad - unnecessary mutability
@Data
public class ValidationResult {
    boolean valid;
    List<String> errors;
    // Should be immutable!
}

// ✅ Good - immutable
@Value
public class ValidationResult {
    boolean valid;
    List<String> errors;
}
```

### 2. Missing @Builder.Default

```java
// ❌ Bad - no default, must always specify
@Value
@Builder
public class Config {
    int timeout;  // No default
}

// ✅ Good - sensible default
@Value
@Builder
public class Config {
    @Builder.Default
    int timeout = 30000;
}
```

### 3. Using Wrong Logging Annotation

```java
// ❌ WRONG
@Slf4j
public class MyClass {
    // Wrong logger for CUI projects
}

// ✅ CORRECT
public class MyClass {
    private static final CuiLogger LOGGER = new CuiLogger(MyClass.class);
}
```

## Quality Checklist

- [ ] @Value used for immutable objects
- [ ] @Builder used for classes with 3+ parameters
- [ ] @Delegate used instead of inheritance
- [ ] @Builder.Default provided for optional fields
- [ ] @Singular used for collection builders
- [ ] Records considered as alternative to @Value
- [ ] No Lombok logging annotations (use CuiLogger)
- [ ] @Data used sparingly (prefer immutability)
- [ ] @UtilityClass used for utility classes
- [ ] Lombok dependency included in pom.xml
