# CUI Logging Standards

## Overview

CUI projects use the CUI logging framework from cui-java-tools. This document defines standards for logger configuration, log message organization, and logging best practices.

## Logger Configuration

### Required Setup

All CUI projects MUST use `de.cuioss.tools.logging.CuiLogger`:

```java
import de.cuioss.tools.logging.CuiLogger;

public class TokenValidator {
    private static final CuiLogger LOGGER = new CuiLogger(TokenValidator.class);

    // Use logger throughout the class
}
```

**Requirements**:
* Use `CuiLogger` - not SLF4J, Log4j, or java.util.logging
* Logger must be `private static final`
* Logger constant name must be `LOGGER`
* Pass the class to logger constructor: `new CuiLogger(YourClass.class)`
* Module/artifact: `cui-java-tools`

### Prohibited Practices

**DO NOT**:
* Use log4j or slf4j directly
* Use `System.out.println()` or `System.err.println()` - use appropriate logger level instead
* Use `@Slf4j` or other logging annotations - CUI uses explicit logger declaration
* Use prefixes like `[DEBUG_LOG]` - always use log levels (DEBUG, INFO, WARN, ERROR, FATAL)
* Directly instantiate loggers in multiple places - use single static final logger per class

```java
// ❌ WRONG - prohibited practices
@Slf4j  // Don't use Lombok logging
public class MyClass {
    System.out.println("Debug: " + message);  // Don't use System.out
    System.err.println("Error: " + error);    // Don't use System.err
    log.info("[DEBUG_LOG] Processing...");    // Don't use custom prefixes
}

// ✅ CORRECT - use CuiLogger
public class MyClass {
    private static final CuiLogger LOGGER = new CuiLogger(MyClass.class);

    public void process() {
        LOGGER.debug("Processing started");
        LOGGER.info("Processing completed");
    }
}
```

## Logging Methods

### Method Signature Rules

* **Exception parameter always comes first** when logging with exceptions
* **Use '%s' for string substitutions** (not '{}', '%d', '%f', etc.)
* Use `LogRecord` for structured logging

### Basic Logging

```java
// Simple messages
LOGGER.debug("Starting token validation");
LOGGER.info("Token validated successfully");
LOGGER.warn("Clock skew detected");
LOGGER.error("Validation failed");
LOGGER.fatal("Critical system failure");

// With parameters (%s for all substitutions)
LOGGER.info("User %s logged in from %s", username, ipAddress);
LOGGER.warn("Request took %s ms (threshold: %s)", duration, threshold);

// With exception (exception comes FIRST)
LOGGER.error(exception, "Failed to connect to database: %s", url);
LOGGER.fatal(exception, "System shutdown due to: %s", reason);
```

## LogRecord Usage

### Core Requirements

**CRITICAL RULES**:
* **REQUIRED**: LogRecord MUST be used for INFO, WARN, ERROR, and FATAL levels
* **PROHIBITED**: LogRecord MUST NOT be used for DEBUG or TRACE levels
* Use `LogRecord#format()` for parameterized messages
* Use `LogRecord#resolveIdentifierString()` for testing

**Rationale**:
- INFO/WARN/ERROR/FATAL are production-critical messages that require structured identifiers for monitoring, alerting, and documentation
- DEBUG/TRACE are development-only messages that don't need the overhead of LogRecord structure

### Module Organization

Aggregate LogRecords in module-specific 'LogMessages' class:

```java
@UtilityClass
public final class AuthenticationLogMessages {
    // Module prefix for all messages
    public static final String PREFIX = "AUTH";

    @UtilityClass
    public static final class INFO {
        public static final LogRecord USER_LOGIN = LogRecordModel.builder()
            .template("User %s logged in successfully")
            .prefix(PREFIX)
            .identifier(1)
            .build();

        public static final LogRecord SESSION_CREATED = LogRecordModel.builder()
            .template("Session created for user %s with validity %s")
            .prefix(PREFIX)
            .identifier(2)
            .build();
    }

    @UtilityClass
    public static final class WARN {
        public static final LogRecord RATE_LIMIT = LogRecordModel.builder()
            .template("Rate limit exceeded for user %s")
            .prefix(PREFIX)
            .identifier(100)
            .build();
    }

    @UtilityClass
    public static final class ERROR {
        public static final LogRecord VALIDATION_FAILED = LogRecordModel.builder()
            .template("Token validation failed: %s")
            .prefix(PREFIX)
            .identifier(200)
            .build();

        public static final LogRecord DATABASE_ERROR = LogRecordModel.builder()
            .template("Database connection failed: %s")
            .prefix(PREFIX)
            .identifier(201)
            .build();
    }

    @UtilityClass
    public static final class FATAL {
        public static final LogRecord SYSTEM_FAILURE = LogRecordModel.builder()
            .template("Critical system failure: %s")
            .prefix(PREFIX)
            .identifier(300)
            .build();
    }
}
```

### Message Identifier Ranges

Organize identifiers by log level:

* **001-099**: INFO level
* **100-199**: WARN level
* **200-299**: ERROR level
* **300-399**: FATAL level

**Note**: DEBUG and TRACE levels do NOT have identifier ranges because they must NOT use LogRecord.
### LogMessages Best Practices

Follow the DSL-Style Constants Pattern:

* Use `@UtilityClass` for LogMessages class and all nested levels
* Import category level constant, NOT individual messages
* Organize by log level (INFO, WARN, ERROR, FATAL)
* Use meaningful module prefix (e.g., "AUTH", "TOKEN", "DB")
* Store prefix as constant in LogMessages class

### LogMessages Documentation Requirements

**REQUIRED**: Every LogMessages class MUST have corresponding documentation at `doc/LogMessages.adoc`.

**See [logmessages-documentation.md](logmessages-documentation.md) for complete documentation standards** including:
- Complete AsciiDoc template and structure
- Table format and column definitions
- Documentation rules and update requirements
- Integration with project documentation
- Complete working examples

**Quick summary**:
- Document all INFO/WARN/ERROR/FATAL messages in `doc/LogMessages.adoc`
- Use AsciiDoc tables organized by log level
- Include: identifier, component, message template, description
- Keep documentation synchronized with implementation
- DEBUG and TRACE are not documented (they don't use LogRecord)

## Usage Examples

### Using LogRecord with Static Import

```java
import static com.example.AuthenticationLogMessages.INFO;
import static com.example.AuthenticationLogMessages.ERROR;

public class AuthenticationService {
    private static final CuiLogger LOGGER = new CuiLogger(AuthenticationService.class);

    public void authenticateUser(String username) {
        try {
            // Authentication logic
            LOGGER.info(INFO.USER_LOGIN, username);

        } catch (DatabaseException e) {
            LOGGER.error(e, ERROR.DATABASE_ERROR, e.getMessage());
            throw new AuthenticationException("Authentication failed", e);
        }
    }

    public void createSession(String username, Duration validity) {
        LOGGER.info(INFO.SESSION_CREATED, username, validity);
    }
}
```

### LogRecord with Multiple Parameters

```java
@UtilityClass
public static final class INFO {
    public static final LogRecord TOKEN_VALIDATED = LogRecordModel.builder()
        .template("Token validated for user %s, issuer: %s, expiry: %s")
        .prefix(PREFIX)
        .identifier(3)
        .build();
}

// Usage
LOGGER.info(INFO.TOKEN_VALIDATED, userId, issuer, expiryTime);
```

### LogRecord with Exception

```java
// Exception parameter always comes FIRST
LOGGER.error(exception, ERROR.VALIDATION_FAILED, exception.getMessage());
LOGGER.fatal(exception, FATAL.SYSTEM_FAILURE, "Database unavailable");
```

## Testing Configuration

### Test Logger Setup

Use `cui-test-juli-logger` for testing:

```xml
<dependency>
    <groupId>de.cuioss.test</groupId>
    <artifactId>cui-test-juli-logger</artifactId>
    <scope>test</scope>
</dependency>
```

### Testing Log Output

```java
import de.cuioss.test.juli.LogAsserts;
import de.cuioss.test.juli.TestLogLevel;
import de.cuioss.test.juli.junit5.EnableTestLogger;

@EnableTestLogger
class TokenValidatorTest {

    @Test
    void shouldLogValidationSuccess() {
        validator.validate(validToken);

        // Assert log message was written
        LogAsserts.assertSingleLogMessagePresentContaining(TestLogLevel.INFO, "validated");
    }

    @Test
    void shouldLogValidationError() {
        validator.validate(invalidToken);

        // Assert error was logged
        LogAsserts.assertLogMessagePresentContaining(TestLogLevel.ERROR, "validation failed");
    }
}
```

### Testing with LogRecord Identifiers

```java
@Test
void shouldLogCorrectIdentifier() {
    validator.validate(token);

    // Verify the correct LogRecord was used
    String expectedIdentifier = INFO.TOKEN_VALIDATED.resolveIdentifierString();
    LogAsserts.assertSingleLogMessagePresentContaining(
        TestLogLevel.INFO, expectedIdentifier);
}
```

## Log Levels

### When to Use Each Level

**DEBUG**:
* Detailed information for diagnosing problems
* Technical details that help trace execution
* Not used in production (disabled by default)

**INFO**:
* Important business events
* Successful operations
* Configuration information
* Application lifecycle events

**WARN**:
* Potentially harmful situations
* Deprecated API usage
* Unexpected but recoverable conditions
* Performance degradation warnings

**ERROR**:
* Error events that might still allow the application to continue
* Failed operations that don't require immediate intervention
* Recoverable errors with fallback handling

**FATAL**:
* Severe error events that will presumably lead the application to abort
* Unrecoverable errors
* Critical system failures

### Examples by Level

```java
// DEBUG - technical details (MUST NOT use LogRecord)
LOGGER.debug("Parsing JWT token with algorithm: %s", algorithm);
LOGGER.debug("Cache hit for key: %s", cacheKey);

// TRACE - fine-grained details (MUST NOT use LogRecord)
LOGGER.trace("Entering method validateToken with parameter: %s", tokenId);
LOGGER.trace("Token signature bytes: %s", signatureHex);

// INFO - important business events (MUST use LogRecord)
LOGGER.info(INFO.USER_LOGIN, username);
LOGGER.info(INFO.SESSION_CREATED, sessionId);

// WARN - potentially harmful situations (MUST use LogRecord)
LOGGER.warn(WARN.RATE_LIMIT, userId);
LOGGER.warn(WARN.CLOCK_SKEW, skewSeconds);

// ERROR - failed operations (MUST use LogRecord)
LOGGER.error(exception, ERROR.VALIDATION_FAILED, tokenId);
LOGGER.error(exception, ERROR.DATABASE_ERROR, "connection timeout");

// FATAL - critical failures (MUST use LogRecord)
LOGGER.fatal(exception, FATAL.SYSTEM_FAILURE, "database unreachable");
LOGGER.fatal(FATAL.CONFIGURATION_INVALID, "required config missing");
```

## Best Practices

### 1. Use Appropriate Log Levels

```java
// ✅ Good - appropriate levels with correct LogRecord usage
LOGGER.debug("Token signature algorithm: %s", algorithm);  // Simple string for debug
LOGGER.info(INFO.USER_LOGIN, username);  // LogRecord for info
LOGGER.error(exception, ERROR.VALIDATION_FAILED, tokenId);  // LogRecord for error

// ❌ Bad - wrong levels
LOGGER.info("Debug info: token = %s", fullToken);  // Should be debug
LOGGER.error("User logged in");  // Should be info
LOGGER.debug(DEBUG.SOME_MESSAGE, value);  // PROHIBITED - no LogRecord for debug!
```

### 2. Use LogRecord for Production Levels Only

```java
// ✅ Good - LogRecord REQUIRED for INFO/WARN/ERROR/FATAL
LOGGER.info(INFO.USER_LOGIN, username);
LOGGER.warn(WARN.RATE_LIMIT, userId);
LOGGER.error(exception, ERROR.DATABASE_ERROR, details);
LOGGER.fatal(FATAL.SYSTEM_FAILURE, reason);

// ✅ Good - simple strings for DEBUG/TRACE (LogRecord prohibited)
LOGGER.debug("Validating token signature");
LOGGER.trace("Entering method with parameter: %s", paramValue);

// ❌ Bad - simple string for production levels
LOGGER.info("User " + username + " logged in");  // MUST use LogRecord
LOGGER.warn("Rate limit exceeded");  // MUST use LogRecord

// ❌ Bad - LogRecord for debug/trace levels
LOGGER.debug(DEBUG.TOKEN_DETAILS, token);  // PROHIBITED - no LogRecord for debug!
LOGGER.trace(TRACE.METHOD_ENTRY, methodName);  // PROHIBITED - no LogRecord for trace!
```

### 3. Exception Parameter First

```java
// ✅ Good - exception first
LOGGER.error(exception, ERROR.VALIDATION_FAILED, tokenId);

// ❌ Bad - exception not first
LOGGER.error(ERROR.VALIDATION_FAILED, tokenId, exception);  // Won't work
```

### 4. Use %s for All Substitutions

```java
// ✅ Good - %s for all types
LOGGER.info("Processing %s records in %s ms", count, duration);
LOGGER.warn("Memory usage: %s MB", memoryMb);

// ❌ Bad - wrong format specifiers
LOGGER.info("Processing %d records in %d ms", count, duration);  // Use %s
```

### 5. Avoid Expensive Operations

```java
// ✅ Good - cheap operations
LOGGER.debug("Validating token for user: %s", userId);

// ❌ Bad - expensive serialization
LOGGER.debug("Token details: %s", serializeComplexObject(token));

// ✅ Better - guard with level check
if (LOGGER.isDebugEnabled()) {
    LOGGER.debug("Token details: %s", serializeComplexObject(token));
}
```

### 6. Don't Log Sensitive Information

```java
// ❌ Bad - logs sensitive data
LOGGER.info("User password: %s", password);
LOGGER.debug("Credit card: %s", creditCard);
LOGGER.info("Full JWT token: %s", jwtToken);

// ✅ Good - masks or omits sensitive data
LOGGER.info("User authenticated: %s", username);
LOGGER.debug("Token ID: %s", tokenId);  // ID only, not full token
```

## Complete Example

```java
import de.cuioss.tools.logging.CuiLogger;
import de.cuioss.tools.logging.LogRecord;
import de.cuioss.tools.logging.LogRecordModel;
import lombok.experimental.UtilityClass;
import static com.example.TokenValidatorLogMessages.INFO;
import static com.example.TokenValidatorLogMessages.ERROR;

// LogMessages definition
@UtilityClass
public final class TokenValidatorLogMessages {
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

// Service using logging
public class TokenValidator {
    private static final CuiLogger LOGGER = new CuiLogger(TokenValidator.class);

    public ValidationResult validate(String token) {
        LOGGER.debug("Starting token validation");

        try {
            String userId = extractUserId(token);
            boolean isValid = performValidation(token);

            if (isValid) {
                LOGGER.info(INFO.VALIDATION_SUCCESS, userId);
                return ValidationResult.valid();
            } else {
                LOGGER.error(ERROR.VALIDATION_FAILED, userId, "Invalid signature");
                return ValidationResult.invalid("Invalid signature");
            }

        } catch (TokenException e) {
            LOGGER.error(e, ERROR.VALIDATION_FAILED, "unknown", e.getMessage());
            throw new ValidationException("Validation failed", e);
        }
    }
}
```

## Quality Checklist

- [ ] CuiLogger used (not SLF4J or Log4j)
- [ ] Logger is private static final
- [ ] Logger constant named LOGGER
- [ ] **LogRecord REQUIRED for INFO/WARN/ERROR/FATAL**
- [ ] **LogRecord NOT used for DEBUG/TRACE**
- [ ] LogMessages class follows DSL pattern
- [ ] Message identifiers in correct ranges (001-099 INFO, 100-199 WARN, 200-299 ERROR, 300-399 FATAL)
- [ ] No DEBUG or TRACE identifiers defined (prohibited)
- [ ] **doc/LogMessages.adoc file exists and is up-to-date**
- [ ] LogMessages.adoc includes all INFO/WARN/ERROR/FATAL messages
- [ ] LogMessages.adoc matches implementation exactly
- [ ] Exception parameter comes first
- [ ] %s used for all substitutions
- [ ] Appropriate log levels used
- [ ] No sensitive information logged
- [ ] Static imports used for LogRecord categories
- [ ] Test logging configured correctly
- [ ] No System.out or System.err usage
- [ ] No custom log prefixes in messages
