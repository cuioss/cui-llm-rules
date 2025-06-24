# AI Development Guidelines

This file provides guidance to AI tools (IntelliJ Junie, Claude Code, GitHub Copilot, etc.) when working with code in CUI projects.

## Build Commands Template
Common Maven commands for CUI projects:
- Build project: `./mvnw clean install`
- Build Single Module: `./mvnw clean install -pl <module-name>`
- Run tests: `./mvnw test`
- Run single test: `./mvnw test -Dtest=ClassName#methodName`
- Clean-Up Code: `./mvnw -Ppre-commit clean install -DskipTests` -> Check the console after running the command and fix all errors and warnings, verify until they are all corrected

## CUI Standards Documentation
- Standards Overview: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards`

### Java Standards
- Java Code Standards: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards/java`
- DSL-Style Constants: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards/java/dsl-style-constants.adoc`

### Documentation Standards
- General Documentation: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards/documentation`
- Javadoc Standards: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards/documentation/javadoc-standards.adoc`
- AsciiDoc Standards: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards/documentation/asciidoc-standards.adoc`
- README Structure: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards/documentation/readme-structure.adoc`

### Logging Standards
- Logging Core Standards: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards/logging`
- Logging Implementation Guide: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards/logging/implementation-guide.adoc`
- Logging Testing Guide: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards/logging/testing-guide.adoc`

### Testing Standards
- Testing Core Standards: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards/testing`
- Quality Standards: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards/testing/quality-standards.adoc`
- CUI Test Generator Guide: `https://gitingest.com/github.com/cuioss/cui-test-generator`

### Requirements Standards
- Requirements Documents: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards/requirements`
- Specification Documents: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards/requirements/specification-documents.adoc`
- New Project Guide: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards/requirements/new-project-guide.adoc`

### CDI and Quarkus Standards
- CDI Development Patterns: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards/cdi-quarkus`
- Quarkus Testing Standards: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards/cdi-quarkus/testing-standards.adoc`
- Container Standards: `https://gitingest.com/github.com/cuioss/cui-llm-rules/tree/main/standards/cdi-quarkus/container-standards.adoc`

## Code Style Guidelines
- Follow package structure: reverse domain name notation (de.cuioss.*)
- Use DSL-style nested constants for logging messages
- Organize imports: Java standard first, then 3rd party, then project imports
- Use `@NonNull` annotations from Lombok for required parameters
- Keep classes small and focused - follow Single Responsibility Principle
- Follow builder pattern for complex object creation
- Use meaningful, descriptive method and variable names
- Use Optional for nullable return values instead of null
- Use immutable objects when possible
- Always validate input parameters
- Prefer delegation over inheritance

## Lombok Usage
- Use `@Builder` for complex object creation
- Use `@Value` for immutable objects
- Use `@NonNull` for required parameters
- Use `@ToString` and `@EqualsAndHashCode` for value objects
- Use `@UtilityClass` for utility classes
- Make proper use of `lombok.config` settings

## Logging Standards
- Use `de.cuioss.tools.logging.CuiLogger` (private static final LOGGER)
- Use LogRecord API for structured logging with dedicated message constants
- Follow logging level ranges: INFO (001-99), WARN (100-199), ERROR (200-299), FATAL (300-399)
- Use CuiLogger.error(exception, ERROR.CONSTANT.format(param)) pattern
- All log messages must be documented in doc/LogMessages.adoc
- Exception parameter always comes first in logging methods
- Use '%s' for string substitutions (not '{}')

## Testing Standards
- Use JUnit 5 (`@Test`, `@DisplayName`, `@Nested`)
- Use cui-test-juli-logger for logger testing with `@EnableTestLogger`
- Test all code paths, edge cases, and error conditions
- Use assertLogMessagePresentContaining for testing log messages
- Follow Arrange-Act-Assert pattern in test methods
- Tests must be independent and not rely on execution order
- Unit tests should use descriptive method names
- Use nested test classes to organize related tests
- Mock or stub dependencies in unit tests
- Use test data builders when appropriate
- All public methods must have unit tests
- Test coverage should aim for at least 80% line coverage

## CUI Test Generator Usage
- Mandatory for all test data generation
- Use annotation hierarchy: @GeneratorsSource > @CompositeTypeGeneratorSource > @CsvSource > @ValueSource > @MethodSource (last resort)
- Parameterized tests mandatory for 3+ similar test variants
- See CUI Test Generator Guide for comprehensive examples

## Javadoc Standards
- Every public class/interface must be documented
- Include clear purpose statement in class documentation
- Document all public methods with parameters, returns, and exceptions
- Include `@since` tag with version information
- Document thread-safety considerations
- Include usage examples for complex classes and methods
- Every package should have package-info.java
- Use `{@link}` for references to classes, methods, and fields
- Document Builder classes with complete usage examples

## AI Tool Specific Instructions

### For IntelliJ Junie
- Always check for pre-commit profile availability
- Use proper Maven module selection for focused builds
- Leverage IDE integration for testing and debugging

### For Claude Code
- Use todo lists for complex multi-step tasks
- Batch tool calls for parallel operations
- Always run lint and typecheck commands after code changes

### For GitHub Copilot
- Context-aware suggestions based on CUI standards
- Follow established patterns in the codebase
- Respect existing code style and architecture

### For All AI Tools
- Always refer to CUI standards documentation before making changes
- Validate against existing patterns in the codebase
- Run tests after any code modifications
- Follow the pre-commit process for code quality
- Document any new public APIs according to Javadoc standards
- Use gitingest.com links for accessing CUI standards repository content