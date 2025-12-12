# Build Systems

Build system configuration with command labels and detection.

## Purpose

Build systems configuration defines:
- Which build systems are available in the project
- Command mappings for standard operations (test, verify, etc.)
- Associated skills for build execution

## Structure

```json
{
  "build_systems": [
    {
      "system": "maven",
      "skill": "pm-dev-builder:builder-maven-rules",
      "commands": {
        "compile": "compile",
        "test": "clean test",
        "verify": "clean verify",
        "install": "clean install",
        "pre-commit": "-Ppre-commit clean install",
        "coverage": "-Pcoverage clean verify"
      }
    }
  ]
}
```

## Fields

### system

Build system identifier.

| Value | Description |
|-------|-------------|
| `maven` | Apache Maven |
| `gradle` | Gradle Build |
| `npm` | Node Package Manager |

### skill

Skill that handles build execution for this system.

| System | Skill |
|--------|-------|
| maven | `pm-dev-builder:builder-maven-rules` |
| gradle | `pm-dev-builder:builder-gradle-rules` |
| npm | `pm-dev-builder:builder-npm-rules` |

### commands

Map of command labels to actual build commands.

```json
"commands": {
  "label": "actual-command"
}
```

## Standard Command Labels

| Label | Purpose | Maven | Gradle | npm |
|-------|---------|-------|--------|-----|
| `compile` | Compile source | `compile` | `compileJava` | `run build` |
| `test-compile` | Compile tests | `test-compile` | `testClasses` | - |
| `test` | Run unit tests | `clean test` | `clean test` | `run test` |
| `verify` | Full verification | `clean verify` | `clean check` | `run test && run lint` |
| `install` | Install artifacts | `clean install` | `publishToMavenLocal` | - |
| `pre-commit` | Pre-commit checks | `-Ppre-commit clean install` | `preCommit` | - |
| `coverage` | Coverage analysis | `-Pcoverage clean verify` | `jacocoTestReport` | `run test:coverage` |
| `integration` | Integration tests | `-Pintegration-tests clean verify` | - | - |
| `lint` | Linting only | - | - | `run lint` |
| `format` | Format check | - | - | `run format:check` |
| `e2e` | E2E tests | - | - | `run test:e2e` |
| `native` | Native image | `clean package -Dnative` | - | - |

## Detection

Auto-detect build systems from project files:

```bash
plan-marshall-config build-systems detect
```

### Detection Rules

| File Present | Detected System |
|--------------|-----------------|
| `pom.xml` | maven |
| `build.gradle` or `build.gradle.kts` | gradle |
| `package.json` | npm |

### Default Commands

When detected, systems are populated with default commands:

**Maven:**
```json
{
  "system": "maven",
  "skill": "pm-dev-builder:builder-maven-rules",
  "commands": {
    "compile": "compile",
    "test-compile": "test-compile",
    "test": "clean test",
    "verify": "clean verify",
    "install": "clean install",
    "pre-commit": "-Ppre-commit clean install",
    "coverage": "-Pcoverage clean verify",
    "integration": "-Pintegration-tests clean verify",
    "native": "clean package -Dnative"
  }
}
```

**Gradle:**
```json
{
  "system": "gradle",
  "skill": "pm-dev-builder:builder-gradle-rules",
  "commands": {
    "compile": "compileJava",
    "test-compile": "testClasses",
    "test": "clean test",
    "verify": "clean check",
    "install": "clean publishToMavenLocal",
    "pre-commit": "clean preCommit",
    "coverage": "clean test jacocoTestReport"
  }
}
```

**npm:**
```json
{
  "system": "npm",
  "skill": "pm-dev-builder:builder-npm-rules",
  "commands": {
    "compile": "run build",
    "test": "run test",
    "verify": "run test && run lint",
    "lint": "run lint",
    "format": "run format:check",
    "coverage": "run test:coverage",
    "e2e": "run test:e2e"
  }
}
```

## Usage Patterns

### Get Command for Build

```bash
# Get verify command for Maven
plan-marshall-config build-systems get-command \
  --system maven \
  --label verify

# Output:
# status: success
# system: maven
# label: verify
# command: clean verify
# skill: pm-dev-builder:builder-maven-rules
```

### Module-Aware Command Resolution

For module-specific commands, use modules API:

```bash
# Resolves module overrides automatically
plan-marshall-config modules get-command \
  --module e2e-tests \
  --system npm \
  --label test
```

### Add Build System

```bash
# Add Gradle with default commands
plan-marshall-config build-systems add --system gradle
```

### Remove Build System

```bash
# Remove unused build system
plan-marshall-config build-systems remove --system gradle
```

## Build System Selection

Agents choose build systems based on context:

| Context | Preferred System |
|---------|------------------|
| Development iteration | `npm` (faster feedback) |
| Final verification | `maven`/`gradle` (authoritative) |
| Frontend-only module | `npm` |
| Java-only module | `maven`/`gradle` |
| Mixed module | Both available |

## Customizing Commands

### Project-Level

Edit marshal.json directly or use re-detection:

```json
{
  "build_systems": [
    {
      "system": "maven",
      "commands": {
        "verify": "clean verify -DskipITs"
      }
    }
  ]
}
```

### Module-Level

Use module command overrides:

```json
{
  "modules": {
    "e2e-tests": {
      "commands": {
        "npm": {
          "test": "playwright:test",
          "verify": "playwright:test"
        }
      }
    }
  }
}
```

## Integration with Builder Agents

Builder agents use build-systems configuration:

1. **Get command**: `build-systems get-command --system X --label Y`
2. **Load skill**: `Skill: {skill}`
3. **Execute**: Use skill's execution workflow

```
plan-marshall-config build-systems get-command --system maven --label verify
    ↓
skill: pm-dev-builder:builder-maven-rules
command: clean verify
    ↓
Load skill, execute command
```
