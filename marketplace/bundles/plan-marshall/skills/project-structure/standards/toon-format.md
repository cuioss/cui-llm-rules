# Project Structure TOON Format

Schema definition for `.plan/project-structure.toon`.

## File Location

**Path**: `.plan/project-structure.toon`

**Version Control**: Tracked in git (not gitignored)

## Top-Level Structure

```toon
# Project Structure Knowledge

modules:
  {module-definitions}

dependencies:
  module_deps:
    {module-dependency-map}
  layer_rules:
    {layer-constraint-definitions}

placement:
  {component-type-rules}

conventions:
  naming:
    {naming-conventions}
  packages:
    {package-conventions}
  testing:
    {testing-conventions}
  documentation:
    {documentation-conventions}
```

## Section: modules

Each module entry contains metadata about a project module.

### Module Schema

```toon
modules:
  module-name:
    responsibility: Brief description of module purpose
    layer: extension|presentation|service|api|packaging|testing
    technology:
      framework: framework-name (e.g., quarkus, spring, nifi-api)
      di: cdi|spring|none
      testing: junit5|jest|playwright|none
    key_packages:
      - com.example.module.package1
      - com.example.module.package2
    tips:
      - Implementation tip for developers
    insights:
      - Learned insight from past implementations
    best_practices:
      - Established best practice for this module
```

### Field Descriptions

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `responsibility` | Yes | string | One-sentence description of module purpose |
| `layer` | Yes | enum | Architectural layer (see layer-definitions.md) |
| `technology` | No | object | Technology stack details |
| `technology.framework` | No | string | Primary framework (quarkus, spring, nifi-api, angular) |
| `technology.di` | No | enum | Dependency injection (cdi, spring, none) |
| `technology.testing` | No | string | Testing framework (junit5, jest, playwright) |
| `key_packages` | No | list | Primary packages in this module |
| `tips` | No | list | Implementation tips for developers |
| `insights` | No | list | Learned insights from implementations |
| `best_practices` | No | list | Established best practices |

## Section: dependencies

Defines module relationships and layer constraints.

### Module Dependencies

```toon
dependencies:
  module_deps:
    dependent-module:
      - dependency1
      - dependency2
    another-module:
      - dependency3
```

Lists which modules depend on which other modules.

### Layer Rules

```toon
dependencies:
  layer_rules:
    layer-name:
      allowed:
        - layer-that-can-be-depended-on
      forbidden:
        - layer-that-must-not-be-depended-on
```

Defines architectural constraints between layers.

## Section: placement

Defines where new components should be placed.

### Placement Rule Schema

```toon
placement:
  component-type:
    module: target-module-name
    package: com.example.{feature}
    pattern: {Name}Component.java
    test_pattern: {Name}ComponentTest.java
    example: ExampleComponent.java
```

### Field Descriptions

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `module` | Yes | string | Target module for this component type |
| `package` | Yes | string | Package pattern with `{feature}` placeholder |
| `pattern` | Yes | string | File naming pattern with `{Name}` placeholder |
| `test_pattern` | No | string | Test file pattern |
| `example` | No | string | Example file name for reference |

### Placeholder Substitution

- `{feature}` - Lowercase feature name (e.g., `oauth`, `validation`)
- `{Name}` - PascalCase component name (e.g., `OAuthToken`, `UserValidator`)
- `{name}` - camelCase or kebab-case name

## Section: conventions

Project-wide conventions organized by category.

### Categories

```toon
conventions:
  naming:
    - "Processors: {Name}Processor"
    - "Controller Services: {Name}Service"
  packages:
    - "com.example.{domain}.{layer} for domain code"
  testing:
    - "Unit tests in same module as source"
    - "Integration tests in integration-testing module"
  documentation:
    - "JavaDoc on all public classes"
    - "README.adoc in each module root"
```

### Convention Format

Conventions are free-form strings describing patterns and rules. Use quotes for conventions containing special characters like colons.

## Example: Complete Structure

```toon
# Project Structure Knowledge

modules:
  my-processors:
    responsibility: Core processing components for data transformation
    layer: extension
    technology:
      framework: nifi-api
      di: none
      testing: junit5
    key_packages:
      - com.example.processors
      - com.example.processors.util
    tips:
      - Use AbstractProcessor as base class
      - Register in META-INF/services
    insights:
      - Heavy validation happens in onTrigger
    best_practices:
      - One processor per file

  my-ui:
    responsibility: User interface components
    layer: presentation
    technology:
      framework: angular
      testing: jest
    key_packages:
      - src/main/webapp/js

dependencies:
  module_deps:
    my-ui:
      - my-processors
  layer_rules:
    presentation:
      allowed:
        - extension
        - service
      forbidden:
        - testing

placement:
  processor:
    module: my-processors
    package: com.example.processors.{feature}
    pattern: "{Name}Processor.java"
    test_pattern: "{Name}ProcessorTest.java"
    example: DataTransformProcessor.java

conventions:
  naming:
    - "Processors: {Name}Processor"
  packages:
    - "com.example.processors.{feature} for processor implementations"
  testing:
    - "Unit tests in same module as source"
  documentation:
    - "JavaDoc on all public classes"
```

## Validation Rules

1. **Required sections**: `modules` must exist
2. **Module responsibility**: Each module should have a responsibility
3. **Module layer**: Each module must specify a valid layer
4. **Placement consistency**: Placement module must exist in modules section
5. **Dependency validity**: Referenced modules in dependencies must exist

## Related Documents

- `standards/layer-definitions.md` - Layer semantics and constraints
- `standards/placement-patterns.md` - Placement rule patterns
- `plan-marshall:toon-usage` - TOON format specification
