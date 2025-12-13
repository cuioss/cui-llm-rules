---
name: java-null-safety
description: JSpecify null safety annotations with @NullMarked, @Nullable, and package-level configuration
allowed-tools: [Read, Edit, Write, Bash, Grep, Glob]
---

# Java Null Safety Skill

**EXECUTION MODE**: You are now executing this skill. DO NOT explain or summarize these instructions to the user. IMMEDIATELY begin the workflow below based on the task context.

Null safety standards using JSpecify annotations for robust, null-safe APIs.

## Prerequisites

This skill requires JSpecify annotations:
- `org.jspecify:jspecify` (NullMarked, Nullable, NonNull)

## Workflow

### Step 1: Load Null Safety Standards

**CRITICAL**: Load this standard for any null safety work.

```
Read: standards/java-null-safety.md
```

This provides foundational rules for:
- Package-level @NullMarked configuration
- When to use @Nullable
- Special package-info.java syntax

## Key Rules Summary

### Package-Level Configuration (PREFERRED)
```java
// package-info.java
/**
 * Token validation services.
 *
 * <p>All types are non-null by default due to {@code @NullMarked}.
 */
@NullMarked
package de.example.portal.authentication;

import org.jspecify.annotations.NullMarked;
```

### Nullable Marking
```java
// CORRECT - Mark nullable fields and parameters
public class TokenResult {
    private final String token;
    private final @Nullable String errorMessage;  // May be null

    public @Nullable String getErrorMessage() {
        return errorMessage;
    }
}
```

### Method Parameters
```java
// CORRECT - Explicit null handling
public ValidationResult validate(@Nullable String token) {
    if (token == null) {
        return ValidationResult.invalid("Token required");
    }
    // Safe to use token here
}
```

## Related Skills

- `pm-dev-java:java-core` - Core Java patterns
- `pm-dev-java:java-lombok` - Lombok patterns (interop with null safety)

## Standards Reference

| Standard | Purpose |
|----------|---------|
| java-null-safety.md | JSpecify annotations and null handling |
