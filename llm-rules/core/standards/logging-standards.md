# Logging Standards

## Purpose
Defines comprehensive standards for logging across the codebase, including configuration, implementation, and testing requirements.

## Important Note on Code Changes
When adapting code to these logging standards:
- Only modify logging-related code (imports, log statements, assertions)
- DO NOT change any unrelated production or test code
- DO NOT refactor or "improve" other aspects while implementing logging changes
- Keep changes focused solely on logging standard compliance

This rule applies to both production and test code changes. For example:
```java
// When updating to DSL-style logging:

// ALLOWED - Only logging-related changes:
- Updating logging imports
- Converting log statements to new format
- Updating log assertions in tests

// NOT ALLOWED (unless explicitly part of task):
- Refactoring methods
- Changing other imports
- Modifying business logic
- Adding new features
- Updating unrelated documentation
```

## Related Documentation
- core/standards/project-standards.md: Project standards and technology stack
- core/standards/documentation-standards.md: Documentation standards
- core/standards/quality-standards.md: Quality standards
- maintenance/java/process.md: Java maintenance process
- java/dsl-style-constants.md: DSL-Style Constants Pattern

## Core Standards

### 1. Logger Configuration
1. Required Setup:
   - Use de.cuioss.tools.logging.CuiLogger with constant name 'LOGGER'
   - Logger must be private static final
   - Module/artifact: cui-java-tools

2. Prohibited Practices:
   - No log4j or slf4j usage
   - No System.out or System.err - use appropriate logger level
   - No direct logger instantiation

### 2. Logging Standards
1. Method Requirements:
   - Exception parameter always comes first
   - Use '%s' for string substitutions (not '{}')
   - Use de.cuioss.tools.logging.LogRecord for template logging

2. Testing Configuration:
   - Use cui-test-juli-logger for testing
   - Use de.cuioss.test.juli.TestLogLevel for log levels

## Implementation Guidelines

### 1. LogRecord Usage
1. Core Requirements:
   - Use LogRecord API for structured logging
   - Use LogRecord#format for parameterized messages
   - Required for INFO/WARN/ERROR/FATAL in production
   - Use LogRecord#resolveIdentifierString() for testing

2. Module Organization:
   - Aggregate LogRecords in module-specific 'LogMessages'
   - Create unique module prefix (e.g., "Portal", "Authentication")
   - Store prefix as constant in LogMessages

3. Message Identifiers:
   - 001-99: INFO level
   - 100-199: WARN level
   - 200-299: ERROR level
   - 300-399: FATAL level
   - 500-599: DEBUG level
   - 600-699: TRACE level

### 2. LogMessages Implementation
1. Class Structure and Organization:
   - Follow the DSL-Style Nested Constants Pattern (see java/dsl-style-constants.md)
   - Import category level constant, NOT its members
   - Example:
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

2. Complete Implementation Example:
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

3. Implementation Rules:
   - Create final utility class
   - Name pattern: [Module][Component]LogMessages
   - Place in module's root package
   - Define module-specific prefix constant

4. Documentation Requirements:
   - Purpose description
   - Complete message format
   - Parameter descriptions
   - Log level specification

### 3. Documentation Standards
1. Location and Format:
   - Document in /doc/LogMessage.adoc
   - Use asciidoc formatting
   - Order by identifier
   - Organize by log level

2. Content Requirements:
   - Identifier (from resolveIdentifierString())
   - Message template
   - Description
   - Only document existing messages

## Testing Standards

### 1. Coverage Requirements
1. Required Coverage:
   - All INFO/WARN/ERROR/FATAL logs
   - Parameter substitution
   - Exception logging
   - Template-based logging

2. Exclusions:
   - Debug level logs optional
   - Test logs themselves

### 2. LogAsserts Guidelines
1. Core Rules:
   - First arg: de.cuioss.test.juli.TestLogLevel
   - Logger parameter only for assertNoLogMessagePresent
   - Use appropriate assertion method

2. Assertion Methods:
   - assertLogMessagePresent: Exact match
   - assertLogMessagePresentContaining: Partial match
   - assertNoLogMessagePresent: Absence check
   - assertSingleLogMessagePresent: Single occurrence

### 3. Testing Strategy
1. Happy Path:
   ```java
   @EnableTestLogger(debug = ResourceBundleLocator.class)
   class ResourceBundleLocatorTest {
       @Test
       void shouldHandleHappyCase() {
           LogAsserts.assertLogMessagePresentContaining(
               TestLogLevel.DEBUG,
               LogMessages.BUNDLE_LOADED.resolveIdentifierString());
           LogAsserts.assertNoLogMessagePresent(TestLogLevel.WARN);
       }
   }
   ```

2. Error Path:
   ```java
   @Test
   void shouldHandleError() {
       LogAsserts.assertLogMessagePresentContaining(
           TestLogLevel.ERROR,
           LogMessages.BUNDLE_LOAD_FAILED.resolveIdentifierString());
   }
   ```

3. Best Practices:
   - One test per logging scenario
   - Use EnableTestLogger annotation
   - Match on message identifiers
   - Test presence and absence
   - Maintain central message definitions

## Success Criteria

### 1. Configuration
- Correct logger setup
- No prohibited logging frameworks
- Proper constant naming
- Correct visibility modifiers

### 2. Implementation
- LogRecord usage for required levels
- Proper message organization
- Valid identifier ranges
- Complete documentation

### 3. Testing
- Required coverage achieved
- Proper assertion usage
- Comprehensive scenarios
- Maintainable structure

## See Also
- core/standards/project-standards.md: Project standards
- core/standards/documentation-standards.md: Documentation standards
- core/standards/quality-standards.md: Quality standards
- maintenance/java/process.md: Java maintenance process
- java/dsl-style-constants.md: DSL-Style Constants Pattern
