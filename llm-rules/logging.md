# Logging Rules

## Purpose
Defines the standards and requirements for logging across the codebase.

## Core Rules

### Logger Configuration
1. Use de.cuioss.tools.logging.CuiLogger with constant name 'LOGGER'
2. Never use log4j or slf4j
3. Never use System.out or System.err - always use appropriate logger level
4. Logger should be private static final
5. The module / artifact where the CuiLogger can be found is cui-java-tools

### Logging Standards
1. Exception parameter always comes first in log methods
2. Use '%s' for string substitutions (not '{}')
3. Use de.cuioss.tools.logging.LogRecord for template logging
4. Use cui-test-juli-logger for testing
5. Use de.cuioss.test.juli.TestLogLevel for log levels in tests

## Implementation Guidelines

### LogRecord Usage
- LogRecord API: https://github.com/cuioss/cui-java-tools/tree/master/src/main/java/de/cuioss/tools/logging
- Use LogRecord#format for parameterized log messages
- Use LogRecord for all INFO/WARN/ERROR/FATAL logs in production code
- For LogAsserts testing, use LogRecord#resolveIdentifierString()
- Aggregate all LogRecords in a module specific type, 'LogMessages'
- Create a unique prefix for each module (e.g., "Portal", "Authentication"): Prompt the user if there is none set
- Persist the prefix as constant within LogMessages
- Numeric identifiers follow level ranges:
  - 001-99: INFO level messages
  - 100-199: WARN level messages
  - 200-299: ERROR level messages
  - 300-399: FATAL level messages
  - 500-599: DEBUG level messages
  - 600-699: TRACE level messages

### LogMessages Implementation
1. Create a final utility class following the naming pattern `[Module][Component]LogMessages` in the module's root package
   ```java
   @UtilityClass
   public final class PortalCommonCDILogMessages {
   ```

2. Define module-specific prefix as constant, using fully qualified module name:
   ```java
   public static final String PREFIX = "PortalCommonCDI";
   ```
   - Prefix should be specific to the module (e.g., "PortalCommonCDI", "PortalAuthentication") rather than generic

3. Place the class in the module's root package (e.g., `de.cuioss.portal.common` for portal-common-cdi module)

4. Create LogRecord instances using LogRecordModel.builder():
   ```java
   public static final LogRecord BUNDLE_LOADED = LogRecordModel.builder()
           .template("Successfully loaded %s '%s' for locale '%s'")
           .prefix(PREFIX)
           .identifier(2)
           .build();
   ```

5. Document each LogRecord with:
   - Purpose
   - Complete message format including prefix (e.g., "PortalCommonCDI-002: Successfully loaded...")
   - Parameter descriptions
   - Log level

### Example Implementation

```java
package de.cuioss.portal.common;

import de.cuioss.tools.logging.LogRecord;
import de.cuioss.tools.logging.LogRecordModel;
import lombok.experimental.UtilityClass;

/**
 * Centralized log messages for the portal-common-cdi module.
 * All messages follow the format: PortalCommonCDI-[identifier]: [message]
 * Debug level messages use 1-500 range
 * Warn level messages use 501-999 range
 */
@UtilityClass
public final class PortalCommonCDILogMessages {

    /** Module prefix for all log messages */
    public static final String PREFIX = "PortalCommonCDI";

    /**
     * Debug level message when a ResourceBundle is successfully loaded
     * Message: PortalCommonCDI-002: Successfully loaded %s '%s' for locale '%s'
     * Parameters:
     * 1. Class name
     * 2. Bundle path
     * 3. Locale
     */
    public static final LogRecord BUNDLE_LOADED = LogRecordModel.builder()
            .template("Successfully loaded %s '%s' for locale '%s'")
            .prefix(PREFIX)
            .identifier(2)
            .build();
}
```

Usage in code:
```java
import de.cuioss.portal.common.PortalCommonCDILogMessages;
// ...

LOGGER.debug(PortalCommonCDILogMessages.BUNDLE_LOADED.format(
    getClass().getName(), bundlePath, locale));
```

Usage in tests:
```java
import de.cuioss.portal.common.PortalCommonCDILogMessages;
// ...

LogAsserts.assertLogMessagePresentContaining(TestLogLevel.DEBUG,
    PortalCommonCDILogMessages.BUNDLE_LOADED.resolveIdentifierString());
```

### LogRecord Documentation
- Document all Log-Message within a file /doc/LogMessage.adoc
- Use asciidoc for formatting
- Order Log-Message using the 'identifier'
- Create a section for each log-level. The header is the level
- Omit sections without content
- Rows are: 
  - Identifier: Hint the outcome of logRecord#resolveIdentifierString()
  - Message
  - Description
- Always double-check whether the documentation refers to an existing message
- Only document existing LogMessages - no speculative or planned features

## Testing Requirements

### Coverage Requirements
1. Test coverage required for INFO/WARN/ERROR/FATAL logs in production code
2. No need to verify logs from within unit tests themselves
3. Test parameter substitution
4. Test exception logging
5. Test template-based logging with LogRecord

### LogAsserts Guidelines
1. First argument must be de.cuioss.test.juli.TestLogLevel
2. Only assertNoLogMessagePresent needs Logger parameter
3. Use appropriate assertion methods:
   - assertLogMessagePresent: Exact match of complete message
   - assertLogMessagePresentContaining: Partial match (good for identifier-based checks)
   - assertNoLogMessagePresent: Verify absence of specific messages
   - assertSingleLogMessagePresent: Verify exactly one occurrence

### Testing Strategy
1. Happy Path Testing:
   - Verify expected logs are present
   - Verify absence of warnings/errors
   - Use assertLogMessagePresentContaining with resolveIdentifierString()

2. Error Path Testing:
   - Verify error/warning logs are present
   - Verify success logs are absent
   - Test with actual exceptions where applicable

3. Best Practices:
   - One test method per logging scenario
   - Use EnableTestLogger annotation to configure logging
   - Match on message identifiers for stability
   - Test both message presence and absence where relevant
   - Keep tests maintainable using central message definitions

### Example Test Implementation
```java
@EnableTestLogger(debug = ResourceBundleLocator.class)
class ResourceBundleLocatorTest {
    @Test
    void shouldHandleHappyCase() {
        // Test code...
        LogAsserts.assertLogMessagePresentContaining(TestLogLevel.DEBUG,
                LogMessages.BUNDLE_LOADED.resolveIdentifierString());
        LogAsserts.assertNoLogMessagePresent(TestLogLevel.WARN);
    }

    @Test
    void shouldHandleError() {
        // Test error case...
        LogAsserts.assertLogMessagePresentContaining(TestLogLevel.ERROR,
                LogMessages.BUNDLE_LOAD_FAILED.resolveIdentifierString());
    }
}
```
