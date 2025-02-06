# Logging Standards

## Purpose
Defines comprehensive standards for logging across the codebase, including configuration, implementation, and testing requirements.

## Related Documentation
- core/standards/project-standards.md: Project standards and technology stack
- core/standards/documentation-standards.md: Documentation standards
- core/standards/quality-standards.md: Quality standards
- maintenance/java/process.md: Java maintenance process

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
1. Class Structure:
   ```java
   @UtilityClass
   public final class ModuleComponentLogMessages {
       public static final String PREFIX = "ModuleComponent";
   }
   ```

2. Implementation Rules:
   - Create final utility class
   - Name pattern: [Module][Component]LogMessages
   - Place in module's root package
   - Define module-specific prefix constant

3. LogRecord Creation:
   ```java
   public static final LogRecord BUNDLE_LOADED = LogRecordModel.builder()
           .template("Successfully loaded %s '%s' for locale '%s'")
           .prefix(PREFIX)
           .identifier(2)
           .build();
   ```

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
