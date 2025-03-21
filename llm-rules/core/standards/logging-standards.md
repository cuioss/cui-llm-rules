# Logging Standards

> **Note:** This document has been migrated to the standards directory. Please refer to the [Logging Standards](/standards/logging/core-standards.adoc) for the current version.

## Migration Notice
The detailed logging standards have been migrated to the standards directory in AsciiDoc format. Please refer to the following documents for the current standards:

- [Logging Core Standards](/standards/logging/core-standards.adoc)
- [Logging Implementation Guide](/standards/logging/implementation-guide.adoc)
- [Logging Testing Guide](/standards/logging/testing-guide.adoc)
- [DSL-Style Constants Pattern](/standards/logging/dsl-style-constants.adoc)

## Important Note on Code Changes
When adapting code to these logging standards:
- Only modify logging-related code (imports, log statements, assertions)
- DO NOT change any unrelated production or test code
- DO NOT refactor or "improve" other aspects while implementing logging changes
- Keep changes focused solely on logging standard compliance

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
   - Follow the [DSL-Style Constants Pattern](../../java/dsl-style-constants.md)
   - Import category level constant, NOT its members
   - See [Logging Implementation Guide](../../java/logging-implementation.md) for examples

2. Implementation Rules:
   - Create final utility class
   - Name pattern: [Module][Component]LogMessages
   - Place in module's root package
   - Define module-specific prefix constant

3. Documentation Requirements:
   - Purpose description
   - Complete message format
   - Parameter descriptions
   - Log level specification

## Documentation Requirements

### LogMessage.md Format
The documentation must be maintained in `doc/LogMessages.md` for each module and must follow this format:

```md
# Log Messages for [Module Name]

All messages follow the format: [Module-Prefix]-[identifier]: [message]

## INFO Level (001-099)

| ID             | Component | Message | Description |
|----------------|-----------|---------|-------------|
| PortalAuth-001 | AUTH | User '%s' successfully logged in | Logged when a user successfully authenticates |
| PortalAuth-002 | AUTH | User '%s' logged out | Logged when a user logs out of the system |

## WARN Level (100-199)

| ID             | Component | Message | Description |
|----------------|-----------|---------|-------------|
| PortalAuth-100 | AUTH | Login failed for user '%s' | Logged when a login attempt fails |

## ERROR Level (200-299)

| ID             | Component | Message | Description |
|----------------|-----------|---------|-------------|
| PortalAuth-200 | AUTH | Authentication error occurred: %s | Logged when a system error occurs |
```

### Documentation Rules
1. Every LogMessages class must have a corresponding documentation file at `doc/LogMessages.md`
2. Documentation must be updated whenever log messages are modified
3. Documentation must exactly match the implementation - this is a success criterion
4. Messages must be organized in separate tables by log level, with level ranges in headers:
   - INFO Level (001-099)
   - WARN Level (100-199)
   - ERROR Level (200-299)
   - FATAL Level (300-399)
5. Include all metadata:
   - Full identifier with module prefix
   - Module/component name
   - Exact message template
   - Clear description of when the message is used

## Success Criteria
1. Logger Configuration:
   - Only CuiLogger is used
   - Logger is private static final
   - No prohibited logging frameworks

2. Implementation:
   - All log messages use LogRecord
   - Message identifiers follow level ranges
   - DSL-Style pattern is followed
   - Imports are correct

3. Documentation:
   - LogMessage.md exists for each module
   - All messages are documented
   - Format matches specification
   - IDs and messages match implementation

4. Testing:
   - All INFO/WARN/ERROR/FATAL messages have tests
   - Tests use cui-test-juli-logger
   - Assertions follow standard patterns

## See Also
- [Logging Implementation Guide](../../java/logging-implementation.md): Detailed examples and patterns
- [Logging Testing Guide](../../testing/logging-testing.md): Testing strategies and examples
- [DSL-Style Constants Pattern](../../java/dsl-style-constants.md): Pattern for organizing log messages

## Important Notes
- All rules are normative and must be applied unconditionally
- Focus changes only on logging-related code
- Documentation must be kept in sync with implementation
- When in doubt about log levels, prefer higher severity
- Reference these rules with '@llm-rules'
