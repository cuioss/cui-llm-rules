---
name: java-lombok
description: Lombok patterns including @Delegate, @Builder, @Value, @UtilityClass for reducing boilerplate
allowed-tools: [Read, Edit, Write, Bash, Grep, Glob]
---

# Java Lombok Skill

**EXECUTION MODE**: You are now executing this skill. DO NOT explain or summarize these instructions to the user. IMMEDIATELY begin the workflow below based on the task context.

Lombok standards for reducing boilerplate code while maintaining code quality and testability.

## Prerequisites

This skill requires Lombok:
- `org.projectlombok:lombok` (compile-time annotation processor)

## Workflow

### Step 1: Load Lombok Patterns

**CRITICAL**: Load this standard for any Lombok usage.

```
Read: standards/java-lombok-patterns.md
```

This provides foundational rules for:
- @Delegate for delegation over inheritance
- @Builder for complex object construction
- @Value for immutable value objects
- @UtilityClass for utility classes

## Key Rules Summary

### @Delegate - Delegation Over Inheritance
```java
// CORRECT - Delegation with Lombok
public class CachedTokenValidator implements TokenValidator {
    @Delegate
    private final TokenValidator delegate;
    private final Cache<String, ValidationResult> cache;

    @Override
    public ValidationResult validate(String token) {
        return cache.get(token, () -> delegate.validate(token));
    }
}
```

### @Builder - Complex Objects
```java
// CORRECT - Builder for multiple optional parameters
@Builder
public class TokenConfig {
    private final String issuer;
    private final String audience;
    @Builder.Default
    private final Duration validity = Duration.ofHours(1);
    @Singular
    private final Set<String> requiredClaims;
}
```

### @Value - Immutable Objects
```java
// CORRECT - Immutable value object
@Value
public class ValidationResult {
    boolean valid;
    String message;
    Instant timestamp;
}
```

### @UtilityClass - Static Methods
```java
// CORRECT - Utility class with static methods
@UtilityClass
public class TokenUtils {
    public String extractSubject(String token) {
        // Static utility method
    }
}
```

## Related Skills

- `pm-dev-java:java-core` - Core Java patterns
- `pm-dev-java:java-null-safety` - Null safety with Lombok

## Standards Reference

| Standard | Purpose |
|----------|---------|
| java-lombok-patterns.md | Lombok annotation patterns and usage |
