# Logging Rules

## Purpose
Defines the standards and requirements for logging across the codebase.

## Core Rules

### Logger Configuration
1. Use CuiLogger with constant name 'LOGGER'
2. Never use log4j or slf4j
3. Never use System.out or System.err - always use appropriate logger level
4. Logger should be private static final

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
- For LogAsserts testing, use LogRecord#resolveIdentifierString()

## Testing Requirements

### Coverage Requirements
1. Test coverage required for INFO/WARN/ERROR/FATAL logs in production code
2. No need to verify logs from within unit tests themselves
3. Test parameter substitution
4. Test exception logging
5. Test template-based logging with LogRecord

### LogAsserts Guidelines
1. First argument must be TestLogLevel
2. Only assertNoLogMessagePresent needs Logger parameter
3. Use appropriate assertion methods:
   - assertLogMessagePresent
   - assertNoLogMessagePresent
   - assertSingleLogMessagePresent

### Test Data Requirements
1. Use LogRecord#resolveIdentifierString for message verification
2. Test both successful and error scenarios
3. Verify correct log level usage
