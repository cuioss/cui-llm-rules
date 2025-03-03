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
```

### 2. Import and Usage Pattern
```java
// CORRECT:
import static de.cuioss.portal.core.PortalCoreLogMessages.INFO;

// Then use:
INFO.USER_LOGIN
WARN.USER_NOT_LOGGED_IN

// INCORRECT - DO NOT:
import static de.cuioss.portal.core.PortalCoreLogMessages.INFO.*;
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
public static final class PortalCoreLogMessages {
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

#### Mandatory LogRecord Usage (INFO/WARN/ERROR/FATAL)
LogRecord MUST be used for INFO/WARN/ERROR/FATAL levels in production code. Direct logging is NOT allowed for these levels:

```java
// CORRECT:
LOGGER.info(INFO.USER_LOGIN.format(username));
LOGGER.error(e, ERROR.DATABASE_CONNECTION.format(url));

// INCORRECT - Never use direct logging for INFO/WARN/ERROR/FATAL:
logger.info("User %s logged in", username);
logger.error(e, "Database connection failed: %s", url);
```

#### Forbidden LogRecord Usage (DEBUG/TRACE)
LogRecord MUST NOT be used for DEBUG/TRACE levels. These levels MUST use direct logging:

```java
// CORRECT:
LOGGER.debug("Processing file %s", filename);
LOGGER.trace(e, "Detailed error info: %s", e.getMessage());

// INCORRECT - Never use LogRecord for DEBUG/TRACE:
LOGGER.debug(DEBUG.SOME_DEBUG_MESSAGE.format());
LOGGER.trace(TRACE.SOME_TRACE_MESSAGE.format());
```

#### Parameter Handling
- For LogRecords (INFO/WARN/ERROR/FATAL): Use format method
  ```java
  LOGGER.info(INFO.SOME_MESSAGE.format(param1, param2));
  ```

- For Direct Logging (DEBUG/TRACE): Use '%s' for parameter substitution
  ```java
  LOGGER.debug("Processing file %s with size %s", filename, size);
  ```

#### Exception Handling
- For LogRecords (INFO/WARN/ERROR/FATAL):
  ```java
  LOGGER.error(e, ERROR.CANNOT_GENERATE_CODE_CHALLENGE.format());
  LOGGER.error(e, ERROR.SOME_ERROR.format(param1));
  ```

- For Direct Logging (DEBUG/TRACE):
  ```java
  LOGGER.debug(e, "Detailed error info: %s", e.getMessage());
  ```

#### Parameter-Free Calls
For LogRecords without parameters, use method reference syntax:
```java
// CORRECT:
LOGGER.info(INFO.STARTUP_COMPLETE::format);

// INCORRECT:
LOGGER.info(INFO.STARTUP_COMPLETE.format());
```

### 6. Common Implementation Patterns

### 1. Exception Logging
```java
try {
    // Some code that might throw
} catch (Exception e) {
    LOGGER.error(e, ERROR.REQUEST_PROCESSING_ERROR.format(e.getMessage()));
}
```

### 2. Parameter Substitution
```java
// Single parameter
LOGGER.info(INFO.USER_LOGIN.format(username));

// Multiple parameters
LOGGER.warn(WARN.USER_INFO_ENRICHED.format(userId, attributeName));
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
