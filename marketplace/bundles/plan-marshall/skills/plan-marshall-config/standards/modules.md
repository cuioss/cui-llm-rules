# Module Configuration

Project module management with domain and build system mappings.

## Purpose

Modules represent distinct parts of a project with different:
- Skill domains (Java, JavaScript, testing)
- Build systems (Maven, npm, Gradle)
- Command configurations

## Module Structure

```json
{
  "modules": {
    "nifi-cuioss-processors": {
      "path": "nifi-cuioss-processors",
      "domains": ["java"],
      "build_systems": ["maven"]
    },
    "nifi-cuioss-ui": {
      "path": "nifi-cuioss-ui",
      "domains": ["java", "javascript"],
      "build_systems": ["maven", "npm"],
      "commands": {
        "npm": {
          "test": "playwright:test"
        }
      }
    }
  }
}
```

## Fields

### path

Relative path from project root to the module.

```json
"path": "modules/my-module"
```

### domains

Skill domains applicable to this module. Links to `skill_domains` configuration.

```json
"domains": ["java", "javascript"]
```

Standard domains:
- `java` - Production Java code
- `java-testing` - Java test code
- `javascript` - Production JavaScript code
- `javascript-testing` - JavaScript test code

### build_systems

Available build systems for this module. References project-level `build_systems`.

```json
"build_systems": ["maven", "npm"]
```

### commands (optional)

Module-specific command overrides per build system.

```json
"commands": {
  "npm": {
    "test": "playwright:test",
    "verify": "playwright:test"
  }
}
```

## Command Resolution

When requesting a command for a module:

1. **Check module override first**
   ```
   modules.{module}.commands.{system}.{label}
   ```

2. **Fall back to project level**
   ```
   build_systems[system=system].commands.{label}
   ```

### Example

```bash
# For e2e-playwright module with npm test
plan-marshall-config modules get-command \
  --module e2e-playwright \
  --system npm \
  --label test
```

If `modules.e2e-playwright.commands.npm.test` exists → returns `playwright:test`
Otherwise → returns project-level `build_systems[npm].commands.test`

## Module Detection

Auto-detect modules from build files:

```bash
plan-marshall-config modules detect
```

### Detection Sources

| Build System | Source File | Detection Method |
|--------------|-------------|------------------|
| Maven | pom.xml | Parse `<modules>` section |
| Gradle | build.gradle | Parse `subprojects` |
| npm | package.json | Parse `workspaces` |

### Domain Inference

Domains are inferred from module content:

| Pattern | Inferred Domain |
|---------|----------------|
| `*.java` files (non-test) | `java` |
| `*.java` files in test dirs | `java-testing` |
| `*.js` or `*.ts` files | `javascript` |
| `e2e`, `playwright`, `cypress` in path | `javascript-testing` |

### Build System Inference

Build systems are inferred from module files:

| File | Inferred System |
|------|-----------------|
| `pom.xml` | maven |
| `build.gradle` / `build.gradle.kts` | gradle |
| `package.json` | npm |

## Usage Patterns

### Get Skills for Module

```bash
# Get domains for module
domains=$(plan-marshall-config modules get-domains --module my-ui)

# For each domain, get implementation skills
plan-marshall-config skill-domains get-defaults --domain java
plan-marshall-config skill-domains get-defaults --domain javascript
```

### Get Build Command

```bash
# Get verify command with override resolution
plan-marshall-config modules get-command \
  --module my-ui \
  --system npm \
  --label verify
```

### Add Module

```bash
plan-marshall-config modules add \
  --module new-e2e \
  --path tests/e2e \
  --domains "javascript-testing" \
  --build-systems "npm"
```

## Multi-Module Project Example

```json
{
  "modules": {
    "core-api": {
      "path": "core-api",
      "domains": ["java"],
      "build_systems": ["maven"]
    },
    "core-impl": {
      "path": "core-impl",
      "domains": ["java"],
      "build_systems": ["maven"]
    },
    "web-ui": {
      "path": "web-ui",
      "domains": ["javascript"],
      "build_systems": ["npm"]
    },
    "e2e-tests": {
      "path": "e2e-tests",
      "domains": ["javascript-testing"],
      "build_systems": ["npm"],
      "commands": {
        "npm": {
          "test": "cypress:run",
          "verify": "cypress:run"
        }
      }
    }
  }
}
```

## Agent Usage

Implementation agents use module configuration to:

1. **Determine applicable skills**
   ```
   modules get-domains → skill-domains get-defaults
   ```

2. **Run correct build commands**
   ```
   modules get-command --module X --system Y --label Z
   ```

3. **Scope verification to module**
   ```
   mvn test -pl {module-path}
   ```
