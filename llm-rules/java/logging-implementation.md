# Logging Implementation Guide

## Purpose
Provides detailed examples and patterns for implementing logging according to the [Logging Standards](../core/standards/logging-standards.md).

## Related Documentation
- [Logging Standards](../core/standards/logging-standards.md): Core logging standards
- [DSL-Style Constants Pattern](./dsl-style-constants.md): Pattern for organizing constants
- [Logging Testing Guide](../testing/logging-testing.md): Testing patterns and examples

## Implementation Examples

### 1. Basic LogMessages Structure
```java
@UtilityClass
public final class PortalCoreLogMessages {
    public static final String PREFIX = "PORTAL_CORE";
    
    @UtilityClass
    public static final class SERVLET {
        @UtilityClass
        public static final class INFO {
            public static final LogRecord USER_LOGIN = LogRecordModel.builder()
                .template("User %s logged in successfully")
                .prefix(PREFIX)
                .identifier(1)
                .build();
        }
        
        @UtilityClass
        public static final class WARN {
            public static final LogRecord USER_NOT_LOGGED_IN = LogRecordModel.builder()
                .template("User not logged in for protected resource")
                .prefix(PREFIX)
                .identifier(100)
                .build();
        }
        
        @UtilityClass
        public static final class ERROR {
            public static final LogRecord REQUEST_PROCESSING_ERROR = LogRecordModel.builder()
                .template("Error processing request: %s")
                .prefix(PREFIX)
                .identifier(200)
                .build();
        }
    }
}
```

### 2. Import and Usage Pattern
```java
// CORRECT:
import static de.cuioss.portal.core.PortalCoreLogMessages.SERVLET;

// Then use:
SERVLET.INFO.USER_LOGIN
SERVLET.WARN.USER_NOT_LOGGED_IN

// INCORRECT - DO NOT:
import static de.cuioss.portal.core.PortalCoreLogMessages.SERVLET.*;
import static de.cuioss.portal.core.PortalCoreLogMessages.*;
```

### 3. Package to Component Mapping
```java
// Common mappings:
de.cuioss.portal.common.bundle.* -> BUNDLE.*
de.cuioss.portal.common.resource.* -> RESOURCE.*
de.cuioss.portal.common.stage.* -> STAGE.*
```

### 4. Identifier Range Management
```java
@UtilityClass
public static final class BUNDLE {
    @UtilityClass
    public static final class INFO {
        public static final LogRecord FIRST_MESSAGE = builder()
            .identifier(1)  // Start with 1
            .build();
        public static final LogRecord SECOND_MESSAGE = builder()
            .identifier(2)  // Next sequential number
            .build();
    }
    
    @UtilityClass
    public static final class WARN {
        public static final LogRecord FIRST_WARNING = builder()
            .identifier(100)  // Start WARN at 100
            .build();
    }
}
```

### 5. LogRecord Usage Patterns

#### Parameter-less Logging
Use method reference syntax when no parameters are needed:
```java
// CORRECT - Use method reference for no parameters
LOGGER.debug(DEBUG.STATE_PARAMETER_MATCHES::format);
LOGGER.info(INFO.STARTUP_COMPLETE::format);

// INCORRECT - Don't use empty format() call
LOGGER.debug(DEBUG.STATE_PARAMETER_MATCHES.format());
```

#### Parameterized Logging
Use lambda for lazy evaluation when parameters are needed:
```java
// CORRECT - Use lambda for lazy evaluation
LOGGER.debug(() -> DEBUG.ERROR_PARAMETER.format(errorValue));
LOGGER.info(() -> INFO.USER_LOGIN.format(username, timestamp));

// Handle mutable variables correctly
var user = getUser();
final var finalUser = user;  // Create final copy for lambda
LOGGER.debug(() -> DEBUG.USER_INFO.format(finalUser));

// INCORRECT - Don't use immediate evaluation
LOGGER.debug(DEBUG.ERROR_PARAMETER.format(errorValue));         // Wrong - eager evaluation
LOGGER.debug(() -> DEBUG.ERROR_PARAMETER::format, errorValue);  // Wrong - incorrect syntax
```

#### Exception Logging
Exception parameter always comes first, followed by lazy-evaluated message:
```java
// CORRECT - Exception first, then lambda for message
try {
    // Some code
} catch (IllegalStateException e) {
    LOGGER.error(e, () -> ERROR.PROCESSING_FAILED.format(requestId));
    LOGGER.warn(e, () -> WARN.INVALID_STATE.format(stateId));
    LOGGER.debug(e, DEBUG.GET_ATTRIBUTE_FAILED::format);  // No params, use method reference
}

// INCORRECT - Never put exception after the message or use eager evaluation
try {
    // Some code
} catch (IllegalStateException e) {
    LOGGER.error(ERROR.PROCESSING_FAILED.format(requestId), e);     // Wrong - exception not first
    LOGGER.error(e, ERROR.PROCESSING_FAILED.format(requestId));     // Wrong - eager evaluation
}
```

### 6. Performance Considerations

#### Lazy Evaluation Benefits
- Format strings and parameter evaluation only occurs if the log level is enabled
- Especially important for DEBUG/TRACE level logging
- Prevents unnecessary string concatenation and object toString() calls
- Particularly beneficial when logging complex objects or expensive toString() implementations

#### When to Use Each Pattern
1. Method Reference (`::format`):
   - Use for parameter-less logging
   - Most efficient, no lambda overhead

2. Lambda (`() -> format()`):
   - Use whenever parameters are needed
   - Ensures lazy evaluation of parameters
   - Required for mutable variables (create final copy)

3. Direct Format (`.format()`):
   - Never use this pattern
   - Always leads to eager evaluation
   - Wastes resources when logging is disabled

## Common Implementation Patterns

### 1. Exception Logging
```java
try {
    // Some code that might throw
} catch (Exception e) {
    LOGGER.error(e, () -> SERVLET.ERROR.REQUEST_PROCESSING_ERROR.format(e.getMessage()));
}
```

### 2. Parameter Substitution
```java
// Single parameter
LOGGER.info(() -> SERVLET.INFO.USER_LOGIN.format(username));

// Multiple parameters
LOGGER.debug(() -> SERVLET.DEBUG.USER_INFO_ENRICHED.format(userId, attributeName));
```

### 3. Conditional Logging
```java
if (LOGGER.isDebugEnabled()) {
    LOGGER.debug(() -> SERVLET.DEBUG.DETAILED_INFO.format(
        createDetailedMessage()));  // Expensive operation
}
```

## Best Practices

### 1. Message Organization
- Group related messages under meaningful component names
- Use consistent naming across the module
- Keep hierarchy depth at exactly 4 levels
- Follow the DSL-Style Constants Pattern

### 2. Message Templates
- Use clear, consistent language
- Include all necessary context
- Use '%s' for all parameter placeholders
- Keep messages concise but informative

### 3. Identifier Management
- Assign IDs sequentially within ranges
- Document all IDs in LogMessage.md
- Verify no duplicate IDs within module
- Follow level-specific ranges

## Important Notes
- All rules are normative and must be applied unconditionally
- Follow DSL-Style Constants Pattern exactly
- Never import below category level
- Keep hierarchy depth at exactly 4 levels
- Reference these rules with '@llm-rules'

## See Also
- [Logging Standards](../core/standards/logging-standards.md): Core standards and requirements
- [Logging Testing Guide](../testing/logging-testing.md): Testing patterns and examples
- [DSL-Style Constants Pattern](./dsl-style-constants.md): Pattern for organizing constants
- [Project Standards](../core/standards/project-standards.md): Overall project standards
