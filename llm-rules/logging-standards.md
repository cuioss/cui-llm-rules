# Logging Standards and Rules

## 1. Logger Configuration
- Use `de.cuioss.tools.logging.CuiLogger` with constant name 'LOGGER'
- Logger must be private static final
- No log4j, slf4j, System.out, or System.err
- Module/artifact: cui-java-tools

## 2. LogRecord Usage (MANDATORY for INFO/WARN/ERROR/FATAL)
- LogRecord MUST be used for INFO/WARN/ERROR/FATAL in production code
- Direct logging (log.info, log.warn etc) is NOT allowed for these levels
- LogRecord MUST NOT be used for DEBUG/TRACE levels
- All messages must be defined in LogMessages classes

Example:
```java
// CORRECT:
LOGGER.info(INFO.USER_LOGIN.format(username));
LOGGER.error(e, ERROR.DATABASE_CONNECTION.format(url));
LOGGER.debug("Processing file %s", filename);  // Direct logging for DEBUG

// INCORRECT:
logger.info("User %s logged in", username);  // Direct logging not allowed for INFO
LOGGER.debug(DEBUG.SOME_DEBUG_MESSAGE.format()); // LogRecord not allowed for DEBUG
```

## 3. LogRecord Implementation
Pattern usage with LogRecord (for INFO/WARN/ERROR/FATAL only):
* With parameters: Use format method
  ```java
  LOGGER.info(INFO.SOME_MESSAGE.format(param1, param2));
  ```
* With exceptions (exception first):
  ```java
  LOGGER.error(e, ERROR.CANNOT_GENERATE_CODE_CHALLENGE.format());
  // or with parameters
  LOGGER.error(e, ERROR.SOME_ERROR.format(param1));
  ```

## 4. Debug/Trace Direct Logging
- DEBUG and TRACE levels MUST use direct logging
- Always use '%s' for parameter substitution
- Exception parameter always first

Example:
```java
LOGGER.debug("Processing file %s", filename);
LOGGER.trace(e, "Detailed error info: %s", e.getMessage());
```

## 5. Message Organization
- Aggregate LogRecords in module-specific 'LogMessages'
- Create unique module prefix
- Store prefix as constant
- Message Identifiers:
  * 001-99: INFO
  * 100-199: WARN
  * 200-299: ERROR
  * 300-399: FATAL

## 6. LogMessages Implementation
- Follow the DSL-Style Nested Constants Pattern
- Import category level constant, NOT its members

Example:
```java
// CORRECT:
import static de.cuioss.portal.core.PortalCoreLogMessages.SERVLET;

// Then use:
SERVLET.INFO.SOME_MESSAGE
SERVLET.WARN.OTHER_MESSAGE

// INCORRECT:
import static de.cuioss.portal.core.PortalCoreLogMessages.SERVLET.*;

// Don't use:
INFO.SOME_MESSAGE
WARN.OTHER_MESSAGE
```

## 7. Testing Requirements
- Coverage required for INFO/WARN/ERROR/FATAL logs
- Test parameter substitution
- Test exception logging
- Debug level logs optional

## 8. LogAsserts Guidelines
- First argument must be TestLogLevel
- Only assertNoLogMessagePresent needs Logger parameter
- Use appropriate assertion methods:
  * assertLogMessagePresent: Exact match
  * assertLogMessagePresentContaining: Partial match
  * assertNoLogMessagePresent: Absence check
  * assertSingleLogMessagePresent: Single occurrence
