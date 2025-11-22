# CUI Java Expert

Comprehensive Java development expertise bundle aggregating core Java patterns, CDI/Quarkus best practices, and unit testing standards for CUI projects.

## Purpose

This bundle provides a complete Java development knowledge base by aggregating five foundational Java skills into a single, cohesive package. It serves as the primary resource for AI assistants working with Java code in CUI projects, ensuring consistent application of standards, patterns, and best practices across all Java development tasks.

## Components Included

### Skills (5 skills with workflows)

1. **cui-java-core** - Core Java development standards
   - Coding patterns and best practices
   - Null safety with @NullMarked
   - Lombok patterns and usage
   - Modern Java features (records, sealed types, pattern matching)
   - DSL-style constants pattern
   - CUI logging framework integration
   - **Workflow: Analyze Logging Violations** - Detect LOGGER usage violations
   - **Workflow: Document LogRecord** - Generate AsciiDoc documentation

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
   - **Workflow: Analyze Coverage** - Parse JaCoCo reports and extract metrics

4. **cui-javadoc** - JavaDoc documentation standards
   - JavaDoc best practices and validation
   - Documentation requirements
   - Code example standards
   - JavaDoc maintenance patterns

5. **cui-java-maintenance** - Java code maintenance standards
   - Refactoring patterns
   - Code quality metrics
   - Maintenance workflows

### Scripts (3 automation scripts)

| Script | Location | Purpose |
|--------|----------|---------|
| `analyze-coverage.py` | cui-java-unit-testing | Parse JaCoCo XML reports |
| `analyze-logging-violations.py` | cui-java-core | Detect LOGGER violations |
| `document-logrecord.py` | cui-java-core | Generate LogMessages docs |

### Commands (9 goal-based orchestrators)

1. **java-enforce-logrecords** - Enforces CUI logging standards (uses skill workflows)
2. **java-implement-code** - Self-contained command: implements code + verifies + iterates
3. **java-implement-tests** - Self-contained command: writes tests + runs tests + iterates
4. **java-generate-coverage** - Self-contained command: generates coverage + analyzes reports
5. **java-fix-javadoc** - Fixes JavaDoc errors and warnings from Maven builds
6. **java-maintain-logger** - Systematic logging standards maintenance
7. **java-maintain-tests** - Systematic test quality improvement
8. **java-optimize-quarkus-native** - Quarkus native image optimization
9. **java-refactor-code** - Systematic Java refactoring with standards compliance

**Note**: For end-to-end Java task orchestration (implementation → testing → coverage), use `/orchestrate-language language=java` from the cui-task-workflow bundle.

## Installation

```bash
/plugin install cui-java-expert
```

This installs all Java skills in a single operation, providing comprehensive Java development guidance.

## Architecture

```
cui-java-expert/
├── commands/                # 9 goal-based orchestrators
│   ├── java-implement-code.md
│   ├── java-implement-tests.md
│   ├── java-generate-coverage.md
│   ├── java-enforce-logrecords.md
│   ├── java-fix-javadoc.md
│   ├── java-maintain-logger.md
│   ├── java-maintain-tests.md
│   ├── java-optimize-quarkus-native.md
│   └── java-refactor-code.md
└── skills/
    ├── cui-java-core/       # Core Java + logging workflows
    │   ├── SKILL.md         # Workflows: Analyze Logging Violations, Document LogRecord
    │   ├── scripts/
    │   │   ├── analyze-logging-violations.py
    │   │   └── document-logrecord.py
    │   └── standards/
    ├── cui-java-unit-testing/   # Testing + coverage workflow
    │   ├── SKILL.md             # Workflow: Analyze Coverage
    │   ├── scripts/
    │   │   └── analyze-coverage.py
    │   └── standards/
    ├── cui-java-cdi/
    ├── cui-java-maintenance/
    └── cui-javadoc/
```

## Workflow Pattern

Commands are thin orchestrators that invoke skill workflows:

```
/java-generate-coverage
  ├─> Task(maven-builder) [generates coverage]
  └─> Skill(cui-java-unit-testing) workflow: Analyze Coverage

/java-enforce-logrecords
  ├─> Skill(cui-java-core) workflow: Analyze Logging Violations
  ├─> [fixes via /java-implement-code]
  └─> Skill(cui-java-core) workflow: Document LogRecord
```

## When to Use

This bundle is ideal for:

- **Java Development Tasks**: Any Java coding work in CUI projects
- **Code Reviews**: Ensuring Java code follows CUI standards
- **Refactoring**: Modernizing Java code with current patterns
- **New Features**: Implementing new Java functionality
- **Testing**: Writing comprehensive unit tests
- **CDI Integration**: Working with CDI containers and dependency injection
- **Quarkus Projects**: Developing Quarkus-based applications
- **Coverage Analysis**: Analyzing JaCoCo reports
- **Logging Compliance**: Enforcing CUI logging standards

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

All skills work together seamlessly:

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

## Usage Examples

### Coverage Analysis

```
/java-generate-coverage threshold=80
```

### Logging Enforcement

```
/java-enforce-logrecords module=my-module
```

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
```

## Bundle Statistics

- **Commands**: 9 (thin orchestrators)
- **Skills**: 5 (with integrated workflows)
- **Scripts**: 3 (Python automation)
- **Agents**: 0 (all absorbed into skill workflows)

## Dependencies

### Inter-Bundle Dependencies

- **cui-maven** - For Maven build operations (maven-builder agent)

### External Dependencies

- Python 3 for automation scripts

## License

Apache-2.0

## Support

- Repository: https://github.com/cuioss/cui-llm-rules
- Bundle: marketplace/bundles/cui-java-expert/
