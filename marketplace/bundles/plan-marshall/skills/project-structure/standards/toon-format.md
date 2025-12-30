# Project Structure Format

Schema definition for `.plan/project-structure.json`.

## File Location

**Path**: `.plan/project-structure.json`

**Storage**: JSON (standard tooling, reliable parsing)
**Output**: TOON (LLM-friendly format for display)

## Top-Level Structure

```json
{
  "project": {
    "name": "project-name",
    "description": "One-sentence project purpose"
  },
  "modules": {
    "module-name": { ... }
  },
  "dependencies": {
    "module-name": ["dep1", "dep2"]
  },
  "placement": {
    "component-type": { ... }
  },
  "conventions": {
    "naming": [...],
    "packages": [...],
    "testing": [...],
    "documentation": [...]
  }
}
```

## Section: modules

Each module entry contains metadata about a project module.

### Module Schema

```json
{
  "module-name": {
    "responsibility": "Brief description of module purpose (1-3 sentences)",
    "readme": "module-name/README.adoc",
    "dependencies": [
      "io.quarkus:quarkus-core:compile",
      "jakarta.inject:jakarta.inject-api:compile"
    ],
    "key_packages": {
      "com.example.module.core": {
        "path": "module-name/src/main/java/com/example/module/core",
        "package_info": "module-name/src/main/java/com/example/module/core/package-info.java",
        "description": "Core domain models and validation logic"
      }
    },
    "tips": ["Implementation tip"],
    "insights": ["Learned insight"],
    "best_practices": ["Best practice"]
  }
}
```

### Field Descriptions

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `responsibility` | Yes | string | 1-3 sentence description of module purpose |
| `readme` | No | string | Project-relative path to module README if exists |
| `dependencies` | No | list | External dependencies as `groupId:artifactId:scope` |
| `key_packages` | No | object | Key packages with structured info |
| `key_packages[pkg].path` | Yes | string | Project-relative path to package directory |
| `key_packages[pkg].package_info` | No | string | Path to package-info.java if exists |
| `key_packages[pkg].description` | Yes | string | 1-2 sentence package description |
| `tips` | No | list | Implementation tips for developers |
| `insights` | No | list | Learned insights from implementations |
| `best_practices` | No | list | Established best practices |

## Section: dependencies

Defines inter-module dependencies.

```json
{
  "dependencies": {
    "my-ui": ["my-core"],
    "my-api": ["my-core", "my-service"]
  }
}
```

Lists which modules depend on which other modules within the project.

## Section: placement

Defines where new components should be placed.

### Placement Rule Schema

```json
{
  "placement": {
    "service": {
      "module": "my-core",
      "package": "com.example.core.{feature}",
      "pattern": "{Name}Service.java",
      "test_pattern": "{Name}ServiceTest.java",
      "example": "UserService.java"
    }
  }
}
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

## Section: conventions

Project-wide conventions organized by category.

```json
{
  "conventions": {
    "naming": ["Services: {Name}Service"],
    "packages": ["com.example.{domain} for domain code"],
    "testing": ["Unit tests in same module as source"],
    "documentation": ["JavaDoc on all public classes"]
  }
}
```

## TOON Output Format

When read via the script, output is in TOON format:

```toon
status: success
file: .plan/project-structure.json

modules:
  my-core:
    responsibility: Core business logic for token validation
    readme: my-core/README.adoc
    dependencies:
      - io.quarkus:quarkus-core:compile
      - jakarta.inject:jakarta.inject-api:compile
    key_packages:
      com.example.core:
        path: my-core/src/main/java/com/example/core
        package_info: my-core/src/main/java/com/example/core/package-info.java
        description: Core domain models
      com.example.core.service:
        path: my-core/src/main/java/com/example/core/service
        package_info:
        description: Business services
    tips:
      - Use @ApplicationScoped for services
```

## Validation Rules

1. **Required sections**: `modules` must exist
2. **Module responsibility**: Each module should have a responsibility
3. **Placement consistency**: Placement module must exist in modules section
4. **Dependency validity**: Referenced modules in dependencies must exist

## Related Documents

- `standards/placement-patterns.md` - Placement rule patterns
- `plan-marshall:toon-usage` - TOON format specification
