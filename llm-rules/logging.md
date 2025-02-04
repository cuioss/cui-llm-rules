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
- Aggregate all LogRecords in a module specific type, 'LogMessages', see https://github.com/cuioss/cui-portal-core/blob/main/modules/authentication/portal-authentication-token/src/main/java/de/cuioss/portal/authentication/token/LogMessages.java as an example
- Create a short prefix for each module, prompt the user if there is none set
- Persist the prefix as constant within LogMessages
- Introduce a sensible numbering: 
  - 001 - 99 -> INFO
  - 100 - 199 -> WARN
  - 200 - 299 -> ERROR
  - 300 - 399 -> FATAL

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
   - assertLogMessagePresent
   - assertNoLogMessagePresent
   - assertSingleLogMessagePresent

### Test Data Requirements
1. Use LogRecord#resolveIdentifierString for message verification
2. Test both successful and error scenarios
3. Verify correct log level usage
