---
name: analyze-project-architecture
description: LLM-based architectural analysis that transforms raw project data into meaningful structure
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Analyze Project Architecture Skill

LLM-driven analysis skill that transforms raw project data into rich, meaningful project structure knowledge.

## What This Skill Provides

- **Semantic Analysis**: Understand module responsibilities from code, not just names
- **Layer Confirmation**: Verify or override script-inferred architectural layers
- **Technology Detection**: Detect frameworks from imports and annotations, not just build config
- **Key Package Identification**: Select architecturally significant packages (2-4 per module)
- **Insight Generation**: Create actionable tips based on observed patterns

## When to Activate This Skill

Activate this skill when:
- **marshall-steward wizard Step 6b**: After collect-raw-data, generate meaningful structure
- **Regenerating project structure**: When structure needs semantic enrichment
- **Initial project setup**: To bootstrap knowledge base with meaningful content

**Prerequisites**:
- `marshal.json` exists (run `/marshall-steward` first)
- Raw data collected via `collect-raw-data` command (or skill generates it)

---

## Workflow: Analyze and Generate Structure

**Pattern**: Context Aggregation

Transform raw project data into rich project-structure.toon with LLM analysis.

### Step 0: Verify Prerequisites

Check that raw data exists or collect it:

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure collect-raw-data
```

This generates `.plan/raw-project-data.json` from filesystem discovery.

### Step 1: Load Raw Data

Read raw project data in TOON format for LLM analysis:

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure raw-data-as-toon
```

This outputs the raw data in TOON format (token-efficient for LLM processing).

This provides:
- Module list with paths
- Packages per module
- Dependencies with scope
- Framework detection from build config
- Source/test file counts
- Documentation paths

### Step 2: Read Project-Level Documentation

Read documentation sources in priority order:

1. **Project README** - High-level project description
2. **Documentation directory** - Architectural docs, module guides

```
# Read project README
Read README.md (or README.adoc)

# Scan doc/ directory if exists
Glob doc/**/*.md
Glob doc/**/*.adoc
```

**Goal**: Understand project purpose, architecture decisions, module organization.

See `standards/documentation-sources.md` for complete priority table.

### Step 3: Analyze Each Module

For each module in raw data:

#### 3a. Read Module Documentation

```
# Module README if exists
Read {module_path}/README.md

# Package-info if exists (Java)
Read {module_path}/src/main/java/{base_package}/package-info.java
```

#### 3b. Sample Key Source Files

Identify 2-3 representative source files:

```
# Find main classes (Java)
Glob {module_path}/src/main/java/**/*.java

# Find main files (JavaScript)
Glob {module_path}/src/**/*.js
```

**Selection criteria**:
- Entry points (Main classes, primary exports)
- Core interfaces/types
- Classes with most imports/dependencies

Read selected files to understand:
- Imports and annotations used
- Framework integration patterns
- Business logic structure

#### 3c. Infer Module Metadata

Using collected context, determine:

| Field | How to Infer |
|-------|--------------|
| `responsibility` | From README, package-info, or dominant class purpose |
| `layer` | Verify/override script inference (see Layer Confirmation) |
| `technology.framework` | From imports: `io.quarkus.*`, `org.springframework.*` |
| `technology.di` | From annotations: `@Inject`, `@Autowired`, `@ApplicationScoped` |
| `technology.testing` | From test imports: JUnit, Mockito, Jest |
| `key_packages` | 2-4 architecturally significant packages |
| `tips` | Implementation guidance from observed patterns |

### Step 4: Analyze Module Relationships

Review dependencies from raw data:

- Identify inter-module dependencies
- Verify layer constraint compliance
- Note any architectural concerns

### Step 5: Generate project-structure.toon

Write enriched structure:

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure generate --force
```

Then update each module with analyzed metadata:

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  module update --module {module-name} \
  --responsibility "{inferred responsibility}" \
  --layer {confirmed layer}
```

**Output**: `.plan/project-structure.toon` with meaningful content

---

## Inferring Module Responsibility

Write responsibility as a single sentence describing what the module does, not what it is.

### Good Responsibilities

| Module | Responsibility |
|--------|----------------|
| oauth-sheriff-core | Validates OAuth access tokens against configurable security policies |
| benchmark-core | Provides performance testing infrastructure for token validation benchmarks |
| oauth-sheriff-quarkus | Integrates core validation into Quarkus applications via CDI |

### Bad Responsibilities (Avoid)

| Module | Bad Responsibility | Problem |
|--------|-------------------|---------|
| oauth-sheriff-core | Core module | Says nothing about purpose |
| benchmark-core | Benchmarking | Too vague |
| oauth-sheriff-quarkus | Quarkus extension | Describes type, not function |

### Derivation Strategy

1. **Check README.md** - Often states purpose directly
2. **Check package-info.java** - JavaDoc describes package purpose
3. **Analyze main classes** - What do the dominant classes do?
4. **Check parent module context** - Nested modules serve parent's purpose

---

## Identifying Key Packages

Select 2-4 **architecturally significant** packages per module. Not all packages.

### Selection Criteria

**Include**:
- Packages with core domain logic
- Packages defining public APIs
- Packages with main entry points

**Exclude**:
- Utility packages (`*.util`, `*.helper`)
- Internal implementation details (`*.internal`)
- Test packages

### Example

For oauth-sheriff-core:
```toon
key_packages:
  - de.cuioss.sheriff.oauth.core.pipeline    # Core validation pipeline
  - de.cuioss.sheriff.oauth.core.policy      # Security policy definitions
```

NOT:
```toon
key_packages:
  - de.cuioss.sheriff.oauth.core
  - de.cuioss.sheriff.oauth.core.pipeline
  - de.cuioss.sheriff.oauth.core.policy
  - de.cuioss.sheriff.oauth.core.util       # Skip utilities
  - de.cuioss.sheriff.oauth.core.internal   # Skip internals
```

---

## Detecting Technology from Code

Build config (pom.xml, package.json) shows dependencies, but **code shows actual usage**.

### Framework Detection

| Framework | Detection Pattern |
|-----------|-------------------|
| Quarkus | `import io.quarkus.*`, `@QuarkusTest` |
| Spring | `import org.springframework.*`, `@SpringBootApplication` |
| NiFi | `extends AbstractProcessor`, `@Tags` |
| CDI | `@Inject`, `@ApplicationScoped`, `@Produces` |
| React | `import React from 'react'`, JSX syntax |

### Testing Detection

| Framework | Detection Pattern |
|-----------|-------------------|
| JUnit 5 | `import org.junit.jupiter.*`, `@Test` |
| JUnit 4 | `import org.junit.Test` |
| Mockito | `import org.mockito.*`, `@Mock` |
| Jest | `describe()`, `it()`, `expect()` |
| Cypress | `cy.visit()`, `cy.get()` |

### Example Analysis

```java
// Seeing this in code:
import io.quarkus.runtime.annotations.RegisterForReflection;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

// Infer:
technology:
  framework: quarkus
  di: cdi
```

---

## Layer Confirmation

Script inference uses naming patterns which may be wrong. Verify using code analysis.

### When to Override Script Layer

| Script Says | Code Shows | Correct Layer |
|-------------|------------|---------------|
| `service` (from `-core`) | No framework deps, pure Java | `library` |
| `extension` (default) | Has `@WebServlet`, UI code | `presentation` |
| `extension` (default) | Defines public interfaces only | `api` |
| `extension` (default) | Only test code | `testing` |

### Layer Verification Questions

1. **Is it a library?** Pure code without framework annotations, depended on by others
2. **Is it an API?** Primarily interfaces and DTOs, minimal implementation
3. **Is it presentation?** Has UI components, web endpoints, user interaction
4. **Is it packaging?** No source code, just bundles other modules

See `plan-marshall:project-structure/standards/layer-definitions.md` for complete layer rules.

---

## Error Handling

### Missing Raw Data

If `collect-raw-data` reports no data:

```bash
# Resolution: Ensure project has build files (pom.xml, package.json)
# Then regenerate:
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure collect-raw-data
```

### Missing Documentation

If module has no README or package-info:
- Rely on source code analysis
- Use parent module context
- Note in tips: "Consider adding module documentation"

### Empty Modules

Modules with no source files (packaging modules):
- Set `layer: packaging`
- Set `responsibility: "Bundles {child modules} for deployment"`
- Skip package analysis

---

## Quality Standards

Generated project-structure.toon should meet:

| Criterion | Requirement |
|-----------|-------------|
| Responsibility | Non-empty for all modules with source code |
| Layer | Verified against actual code, not just name |
| Key packages | 2-4 significant packages per module |
| Technology | Detected from imports/annotations |
| No placeholders | No "TODO" or empty values |

---

## Integration Points

### With marshall-steward Wizard

Wizard Step 6 uses two-phase approach:
1. **Step 6a**: Run `collect-raw-data` script
2. **Step 6b**: Invoke this skill for analysis

### With project-structure Skill

This skill generates content that `project-structure` skill manages:
- This skill: Creates initial rich content
- project-structure: Maintains and queries content

### With Solution Outline

Solution outline Step 0 consumes the structure this skill creates.

---

## Related Skills

- `plan-marshall:project-structure` - Structure management and queries
- `plan-marshall:plan-marshall-config` - marshal.json configuration
- `plan-marshall:toon-usage` - TOON format specification
- `plan-marshall:marshall-steward` - Wizard integration
