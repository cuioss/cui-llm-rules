# CUI Java Expert

Comprehensive Java development expertise bundle aggregating core Java patterns, CDI/Quarkus best practices, and unit testing standards for CUI projects.

## Purpose

This bundle provides a complete Java development knowledge base by aggregating four foundational Java skills into a single, cohesive package. It serves as the primary resource for AI assistants working with Java code in CUI projects, ensuring consistent application of standards, patterns, and best practices across all Java development tasks.

## Components Included

### Skills (4 skills)

1. **cui-java-core** - Core Java development standards
   - Coding patterns and best practices
   - Null safety with @NullMarked
   - Lombok patterns and usage
   - Modern Java features (records, sealed types, pattern matching)
   - DSL-style constants pattern
   - CUI logging framework integration

2. **cui-java-cdi** - CDI and Quarkus development standards
   - CDI aspects and lifecycle management
   - Container configuration and initialization
   - Integration testing patterns
   - Quarkus native compilation optimization
   - Security integration

3. **cui-java-unit-testing** - Java unit testing standards
   - JUnit 5 best practices
   - Test generators and utilities
   - Value object testing patterns
   - Assertion strategies
   - Test organization and naming

4. **cui-javadoc** - JavaDoc documentation standards
   - JavaDoc best practices and validation
   - Documentation requirements
   - Code example standards
   - JavaDoc maintenance patterns

### Agents (3 focused agents)

1. **java-coverage-analyzer** - Analyzes existing JaCoCo coverage reports (focused analyzer - no build execution)
2. **logging-violation-analyzer** - Analyzes LOGGER statement violations (focused analyzer - no fixes)
3. **cui-log-record-documenter** - Documents LogRecord classes in AsciiDoc format (focused documenter)

### Commands (5 commands)

1. **cui-java-task-manager** - End-to-end Java task implementation orchestrator (delegates to self-contained commands)
2. **cui-log-record-enforcer** - Enforces CUI logging standards (orchestrates violation analysis and fixes)
3. **cui-java-implement-code** - Self-contained command: implements code + verifies + iterates
4. **cui-java-implement-tests** - Self-contained command: writes tests + runs tests + iterates
5. **cui-java-coverage-report** - Self-contained command: generates coverage + analyzes reports

## Installation

```bash
/plugin install cui-java-expert
```

This installs all three Java skills in a single operation, providing comprehensive Java development guidance.

## When to Use

This bundle is ideal for:

- **Java Development Tasks**: Any Java coding work in CUI projects
- **Code Reviews**: Ensuring Java code follows CUI standards
- **Refactoring**: Modernizing Java code with current patterns
- **New Features**: Implementing new Java functionality
- **Testing**: Writing comprehensive unit tests
- **CDI Integration**: Working with CDI containers and dependency injection
- **Quarkus Projects**: Developing Quarkus-based applications

## Key Features

### Comprehensive Coverage

The bundle covers all essential aspects of Java development in CUI projects:

- **Core Patterns**: Industry-standard Java coding practices
- **Type Safety**: Null safety with JSpecify annotations
- **Modern Features**: Latest Java language features and patterns
- **Dependency Injection**: CDI best practices and container management
- **Testing Excellence**: Comprehensive unit testing strategies
- **Framework Integration**: Quarkus-specific patterns and optimization

### Integrated Standards

All three skills work together seamlessly:

- **Consistent Patterns**: Unified approach across all Java development
- **No Conflicts**: Skills are designed to complement each other
- **Complete Domain Coverage**: From core patterns to testing to CDI
- **Production Ready**: All standards tested in real CUI projects

### AI-Optimized

Designed specifically for AI assistants:

- **Clear Workflows**: Step-by-step guidance for common tasks
- **Contextual Activation**: Skills activate based on task context
- **Example-Driven**: Working code examples from real unit tests
- **Standards-Based**: Links to authoritative sources and best practices

## Skill Details

### cui-java-core

**Focus**: Foundation of all Java development in CUI projects

**Key Topics**:
- Package and class organization
- Naming conventions and code style
- Exception handling patterns
- Immutability and collections
- Null safety configuration
- Optional vs non-null return types
- Lombok annotations (@Delegate, @Builder, @Value)
- Records, sealed types, pattern matching
- DSL-style constants for type-safe configuration
- CUI logging framework usage

**Standards Files**: 9 comprehensive documents covering core patterns, null safety, Lombok, modern features, constants, logging, LogMessages documentation, and HTTP client patterns

### cui-java-cdi

**Focus**: CDI and Quarkus best practices for enterprise Java applications

**Key Topics**:
- CDI scopes and lifecycle (@ApplicationScoped, @RequestScoped, etc.)
- Producer methods and qualifiers
- CDI events and observers
- Container initialization and startup
- Integration testing with CDI
- Quarkus Arc specifics
- Native compilation optimization
- Build-time vs runtime initialization
- Security integration patterns

**Standards Files**: 4 documents covering CDI aspects, container configuration, testing, and native optimization

### cui-java-unit-testing

**Focus**: Comprehensive unit testing for Java code

**Key Topics**:
- JUnit 5 test structure and organization
- Test naming conventions
- Assertion patterns and best practices
- Test generators for common patterns
- Value object testing utilities
- Mock usage and best practices
- Test coverage strategies
- Integration with build systems

**Standards Files**: 6 documents covering JUnit core, generators, value objects, MockWebServer, integration testing, and JUL logger testing

### cui-javadoc

**Focus**: JavaDoc documentation standards and validation for Java code

**Key Topics**:
- JavaDoc best practices and formatting
- Documentation requirements for classes, methods, and fields
- Code examples in JavaDoc
- JavaDoc validation and quality checks
- Documentation maintenance patterns
- Integration with build systems

**Standards Files**: 4 documents covering JavaDoc standards, code examples, validation, and maintenance

## Usage Examples

### Core Java Development

```java
// Using DSL-style constants (cui-java-core)
public interface ConfigKeys {
    String API_URL = "api.url";
    String TIMEOUT = "api.timeout";
}

// Null safety with @NullMarked (cui-java-core)
@NullMarked
package de.cuioss.example;

// Using Lombok @Delegate (cui-java-core)
@Getter
public class UserWrapper {
    @Delegate
    private final User user;
}
```

### CDI Integration

```java
// CDI producer with lifecycle (cui-java-cdi)
@ApplicationScoped
public class ConfigProducer {

    @Produces
    @Startup
    public Configuration produceConfig() {
        return Configuration.load();
    }
}

// Integration test setup (cui-java-cdi)
@QuarkusTest
class ServiceTest {
    @Inject
    MyService service;

    @Test
    void shouldProcessData() {
        // test implementation
    }
}
```

### Unit Testing

```java
// Using test generators (cui-java-unit-testing)
@Test
void shouldTestValueObject() {
    var generator = new ValueObjectGenerator<>(User.class);
    generator.assertBasicValueObjectContract();
}

// JUnit 5 best practices (cui-java-unit-testing)
@Nested
@DisplayName("User Authentication")
class AuthenticationTests {

    @Test
    @DisplayName("Should authenticate valid user")
    void shouldAuthenticateValidUser() {
        // test implementation
    }
}
```

## Dependencies

None - this bundle is standalone and aggregates existing marketplace skills.

## Related Bundles

This Java expertise bundle complements other CUI bundles:

- **cui-utility-commands** - For research and utility commands
- **cui-maven** - For Maven build and POM maintenance
- **cui-workflow** - For complete development workflow from issue implementation to PR review
- **cui-documentation-standards** - For JavaDoc and technical documentation

## Bundle Statistics

- **Total Skills**: 4
- **Total Agents**: 5 (focused Layer 3 agents)
- **Total Commands**: 5 (orchestrators + self-contained)
- **Total Standards Files**: 23
- **Total Lines of Documentation**: ~6,800
- **Quality Score**: 92.5/100 average
- **Status**: Refactored for Rule 6 Compliance ✅

## Maintenance

This bundle is maintained as part of the CUI Development Standards marketplace. Skills are regularly updated to reflect:

- New Java language features
- Quarkus framework updates
- Testing best practices evolution
- Community feedback and improvements

## Support

For issues or questions:

1. Check individual skill README files in `claude/marketplace/skills/`
2. Review standards documentation in each skill's `standards/` directory
3. Consult the [CUI LLM Rules repository](https://github.com/cuioss/cui-llm-rules)
4. Report issues in the repository

## License

Apache-2.0 - Part of the CUI LLM Rules documentation system for CUI OSS projects.

---

**Version**: 1.0.0
**Last Updated**: 2025-11-01
**Status**: Production Ready ✅
**Average Quality Score**: 94.0/100 ⭐
