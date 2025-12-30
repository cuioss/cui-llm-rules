---
name: analyze-project-architecture
description: LLM-based architectural analysis that transforms raw project data into meaningful structure
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Analyze Project Architecture Skill

LLM-driven analysis skill that transforms raw project data into rich, meaningful project structure knowledge.

## What This Skill Provides

- **Semantic Analysis**: Understand module responsibilities from code, not just names
- **Technology Detection**: Detect frameworks from imports and annotations, not just build config
- **Key Package Identification**: Select architecturally significant packages (2-4 per module)
- **Package Descriptions**: Write meaningful descriptions for each key package
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

Transform raw project data into rich project-structure.json with LLM analysis.

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
- Dependencies with scope (use these to detect frameworks)
- Source/test file counts
- Documentation paths

### Step 2: Generate Initial Structure

Generate the initial structure with detected packages:

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure generate --force
```

This creates `.plan/project-structure.json` with:
- Modules from raw data
- `key_packages` with `path` and `package_info` (if exists)
- Empty `description` fields to be enriched

### Step 3: Read Project-Level Documentation

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

### Step 4: Enrich Each Module

For each module in the generated structure:

#### 4a. Analyze Module and Write Responsibility

Read module documentation:
```
# Module README if exists
Read {module_path}/README.md

# Package-info if exists (Java)
Read {module_path}/src/main/java/{base_package}/package-info.java
```

Then update responsibility:
```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  module update --module {module-name} \
  --responsibility "{analyzed responsibility}"
```

#### 4b. Enrich Package Descriptions

**IMPORTANT**: First read the generated structure to see which packages exist:

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  module get --module {module-name}
```

Then for **each key package listed in the output**:

1. **Read package-info.java** (if `package_info` field exists in structure)
2. **Sample 1-2 key classes** in the package
3. **Write 1-2 sentence description**

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  module set-package-description --module {module-name} \
  --package {package.name} \
  --description "{analyzed description}"
```

**CRITICAL**: Only set descriptions for packages that already exist in `key_packages`. If you need to add a package that wasn't auto-detected, use `add-package` first:

```bash
# Add a missing package first
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  module add-package --module {module-name} \
  --package {package.name} \
  --path {module-path}/src/main/java/{package/as/path} \
  --description "{description}"
```

**Package Description Guidelines**:
- Focus on what the package provides, not implementation details
- Use active voice: "Provides...", "Contains...", "Handles..."
- 1-2 sentences maximum

**Example**:
```bash
# First check what packages exist
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  module get --module oauth-sheriff-core

# Then set description for an EXISTING package
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  module set-package-description --module oauth-sheriff-core \
  --package de.cuioss.sheriff.oauth.core.pipeline \
  --description "Provides the token validation pipeline with configurable validators for signature, claims, and expiration"
```

### Step 5: Set Technology (Optional)

If framework detection from dependencies is insufficient:

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  module set-technology --module {module-name} \
  --framework quarkus --di cdi --testing junit5
```

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

## Writing Package Descriptions

Each key package should have a 1-2 sentence description.

### Good Package Descriptions

| Package | Description |
|---------|-------------|
| `de.cuioss.sheriff.oauth.core.pipeline` | Provides the token validation pipeline with pluggable validators for signature, claims, and expiration checks |
| `de.cuioss.sheriff.oauth.core.domain` | Contains domain models for tokens, claims, and validation results |
| `de.cuioss.sheriff.oauth.core.cache` | Manages caching of JWKS keys and validated tokens for performance optimization |

### Bad Package Descriptions (Avoid)

| Package | Bad Description | Problem |
|---------|-----------------|---------|
| `de.cuioss.sheriff.oauth.core` | Core package | Says nothing |
| `de.cuioss.sheriff.oauth.core.pipeline` | Pipeline classes | Describes type, not function |

### Sources for Package Descriptions

In priority order:
1. **package-info.java** - JavaDoc often has good summary
2. **Key interfaces** - Public interfaces define the contract
3. **Main implementation classes** - Dominant classes show purpose
4. **Usage by other packages** - How is this package used?

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
- Set `responsibility: "Parent POM coordinating {child modules}"`
- Skip package analysis

---

## Quality Standards

Generated project-structure.json should meet:

| Criterion | Requirement |
|-----------|-------------|
| Responsibility | Non-empty for all modules with source code |
| Key packages | 2-4 significant packages per module |
| Package descriptions | Non-empty for all key packages |
| Technology | Detected from imports/annotations |
| No placeholders | No "TODO" or empty values |

---

## Integration Points

### With marshall-steward Wizard

Wizard Step 6 uses two-phase approach:
1. **Step 6a**: Run `collect-raw-data` script
2. **Step 6b**: Invoke this skill for analysis and enrichment

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
