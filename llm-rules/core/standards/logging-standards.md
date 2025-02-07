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

## Documentation Requirements

### LogMessage.adoc Format
The documentation must be maintained in `doc/LogMessage.adoc` for each module and must follow this format:

```asciidoc
# Log Messages for [Module Name]

All messages follow the format: [Module-Prefix]-[identifier]: [message]

[cols="1,2,2,3,2"]
|===
|Identifier |Module |Package |Message |Description

|ModulePrefix-001
|ModuleName
|PACKAGE_NAME
|Message template with %s placeholders
|Clear description of when and why this message occurs
|===
```

### Documentation Rules
1. Every LogMessages class must have a corresponding documentation file at `doc/LogMessage.adoc`
2. Documentation must be updated whenever log messages are modified
3. Documentation must exactly match the implementation - this is a success criterion
4. Messages must be organized by:
   - Package (e.g., BUNDLE, RESOURCE)
   - Then by level (DEBUG, INFO, WARN, ERROR, FATAL)
   - Then by identifier (ascending)
5. Include all metadata:
   - Full identifier with module prefix
   - Module/component name
   - Package name in uppercase
   - Exact message template
   - Clear description

### Success Criteria
1. Documentation exists at `doc/LogMessage.adoc`
2. All implemented messages are documented
3. No documented messages that don't exist in code
4. Identifiers match between code and documentation
5. Message templates match exactly
6. All columns are properly filled out
7. Messages are properly organized by package and level

## Identifier Management

### Distinct Identifier Rules
1. Identifiers must be unique across ALL packages within a module
2. Each package should use a different range within the level ranges:
   ```
   Example for DEBUG (500-599):
   BUNDLE.DEBUG:   500-509
   RESOURCE.DEBUG: 510-519
   STAGE.DEBUG:    520-529
   ```

### Identifier Verification Process
1. Before adding new messages:
   - Check existing identifiers in ALL packages
   - Choose next available number in appropriate range
   - Verify no conflicts with other packages
2. After modifying messages:
   - Run full verification of all identifiers
   - Check for any duplicates
   - Update documentation to match

### Example Package Ranges
```java
// Module: PortalCommonCDI
// Package: BUNDLE
DEBUG: 500-509  // BUNDLE.DEBUG messages
WARN:  100-109  // BUNDLE.WARN messages

// Package: RESOURCE
DEBUG: 510-519  // RESOURCE.DEBUG messages
WARN:  110-119  // RESOURCE.WARN messages

// Package: STAGE
ERROR: 200-209  // STAGE.ERROR messages
```

## Implementation Example with Documentation

### Java Implementation
```java
@UtilityClass
public final class PortalCommonCDILogMessages {
    public static final String PREFIX = "PortalCommonCDI";
    
    @UtilityClass
    public static final class BUNDLE {
        @UtilityClass
        public static final class DEBUG {
            public static final LogRecord PATH_NOT_DEFINED = LogRecordModel.builder()
                    .template("ResourceBundle path not defined for class: %s")
                    .prefix(PREFIX)
                    .identifier(500)  // First in BUNDLE.DEBUG range
                    .build();
        }
    }
    
    @UtilityClass
    public static final class RESOURCE {
        @UtilityClass
        public static final class DEBUG {
            public static final LogRecord LOADER_FALLBACK = LogRecordModel.builder()
                    .template("Resource not found, falling back")
                    .prefix(PREFIX)
                    .identifier(510)  // First in RESOURCE.DEBUG range
                    .build();
        }
    }
}
```

### Corresponding Documentation
```asciidoc
# Log Messages for Portal Common CDI Module

[cols="1,2,2,3,2"]
|===
|Identifier |Module |Package |Message |Description

|PortalCommonCDI-500
|PortalCommonCDI
|BUNDLE
|ResourceBundle path not defined for class: %s
|Indicates missing bundle path configuration

|PortalCommonCDI-510
|PortalCommonCDI
|RESOURCE
|Resource not found, falling back
|Resource loading falls back to alternate loader
|===
```

## DSL-Style Nesting Pattern for LogMessages

The logging system uses a strict DSL-Style Nesting Pattern to organize log messages in a hierarchical, type-safe manner.

### Nesting Structure
1. First level: Module-specific class (e.g., `PortalCommonCDILogMessages`)
2. Second level: Package name in uppercase (e.g., `BUNDLE` for bundle package, `RESOURCE` for resource package)
3. Third level: Log Level (e.g., `INFO`, `WARN`, `ERROR`, `DEBUG`)
4. Fourth level: Message Constants (e.g., `PATH_NOT_DEFINED`, `LOADER_FALLBACK`)

### Example Package to Log Message Mapping
```
de.cuioss.portal.common.bundle.* -> BUNDLE.*
de.cuioss.portal.common.resource.* -> RESOURCE.*
de.cuioss.portal.common.stage.* -> STAGE.*
```

### Import Rules
```java
// CORRECT:
import static de.cuioss.portal.common.PortalCommonCDILogMessages.BUNDLE;

// Then use:
BUNDLE.DEBUG.PATH_NOT_DEFINED
BUNDLE.WARN.LOAD_FAILED

// INCORRECT - DO NOT:
import static de.cuioss.portal.common.PortalCommonCDILogMessages.BUNDLE.DEBUG;
import static de.cuioss.portal.common.PortalCommonCDILogMessages.*;
```

### Implementation Requirements
1. Always import the component/category level constant (second level)
2. Never import the log level or message constants
3. Keep nesting depth at exactly 4 levels
4. Each level must be a static final class with @UtilityClass

### Example Structure
```java
@UtilityClass
public final class PortalCommonCDILogMessages {
    public static final String PREFIX = "PORTAL_CDI";
    
    @UtilityClass
    public static final class BUNDLE {  // Package level
        @UtilityClass
        public static final class DEBUG {  // Log level
            public static final LogRecord PATH_NOT_DEFINED = ...;  // Message
        }
        
        @UtilityClass
        public static final class WARN {
            public static final LogRecord LOAD_FAILED = ...;
        }
    }
}
```

### Common Mistakes to Avoid
1. Importing log levels directly
2. Skipping the component/category level
3. Using wildcard imports
4. Breaking the 4-level hierarchy
5. Mixing different components in the same import

### Benefits
1. Improved code organization through logical grouping
2. Better IDE support with auto-completion
3. Clear visual hierarchy in code
4. Type-safe access to log messages
5. Self-documenting structure

## Message Identifier Numbering

### Range Allocation
- 001-099: INFO messages
- 100-199: WARN messages
- 200-299: ERROR messages
- 300-399: FATAL messages
- 500-599: DEBUG messages
- 600-699: TRACE messages

### Numbering Rules
1. Each package category (BUNDLE, RESOURCE, etc.) must maintain its own consistent sequence of numbers
2. Numbers must be assigned sequentially within each range
3. No gaps in numbering within a range
4. No duplicate numbers within a package category

### Example for Package Category BUNDLE:
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
        public static final LogRecord SECOND_WARNING = builder()
            .identifier(101)  // Next sequential number
            .build();
    }
}
```

### Example for Package Category RESOURCE:
```java
@UtilityClass
public static final class RESOURCE {
    @UtilityClass
    public static final class INFO {
        public static final LogRecord FIRST_MESSAGE = builder()
            .identifier(1)  // Start with 1 again (separate sequence per category)
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

### Best Practices
1. Keep track of used identifiers in the LogMessage.adoc documentation
2. When adding new messages, always use the next available number in the sequence
3. When removing messages, consider leaving a comment about the gap to prevent reuse
4. Document the complete message catalog with identifiers in ascending order
5. Review identifier sequence during code reviews

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
