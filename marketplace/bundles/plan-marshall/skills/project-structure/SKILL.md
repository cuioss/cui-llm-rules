---
name: project-structure
description: Project structure knowledge base for module metadata, placement rules, and architectural conventions
allowed-tools: Read, Write, Edit, Bash
---

# Project Structure Skill

Manages project structure knowledge in `.plan/project-structure.json` for solution outline support.

**Storage**: JSON (reliable, standard tooling)
**Output**: TOON (LLM-friendly format)

## What This Skill Provides

- **Module Metadata**: Responsibility, key packages, dependencies per module
- **Placement Rules**: Where to place new components by type
- **Conventions**: Naming, packaging, testing, documentation patterns
- **Dependencies**: Module dependencies
- **Tips & Insights**: Implementation guidance accumulated over time

## When to Activate This Skill

Activate this skill when:
- Creating solution outlines (load structure in Step 0)
- Determining where new components should be placed
- Understanding module responsibilities and relationships
- Recording insights during verification phase
- Initializing project structure during wizard

---

## Workflow: Read Structure

**Pattern**: Script Automation

Read project structure knowledge. Generates from codebase if missing.

### Read Full Structure

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure read
```

**Output** (TOON):
```toon
status: success
file: .plan/project-structure.json

modules:
  my-module:
    responsibility: Core business logic for token validation
    readme: my-module/README.adoc
    dependencies:
      - io.quarkus:quarkus-core:compile
      - jakarta.inject:jakarta.inject-api:compile
    key_packages:
      de.cuioss.mymodule.service:
        path: my-module/src/main/java/de/cuioss/mymodule/service
        package_info: my-module/src/main/java/de/cuioss/mymodule/service/package-info.java
        description: Business services for token processing
      de.cuioss.mymodule.pipeline:
        path: my-module/src/main/java/de/cuioss/mymodule/pipeline
        package_info:
        description: Token validation pipeline with pluggable validators
    tips:
      - Use @ApplicationScoped for services
    insights:
      - Heavy validation in boundary layer
```

### Read Specific Module

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  module get --module my-module
```

---

## Workflow: Generate Structure

**Pattern**: Script Automation

Generate initial project-structure.toon from codebase analysis.

### Generate from Codebase

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure generate
```

Generation process:
1. Read raw-project-data.json for module list
2. Infer domains from build_systems (maven/gradle -> java, npm -> javascript)
3. Detect key packages from source directories
4. Extract project description from README
5. Create minimal structure for LLM enrichment

### Force Regenerate

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  generate --force
```

---

## Workflow: Enrich Structure

**Pattern**: LLM Analysis + Script Updates

After generating the initial structure, enrich it with semantic information by analyzing the codebase.

### Enrichment Steps

1. **Project Description**: Analyze README and documentation to write a one-sentence project description
   ```bash
   python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
     project update --description "Validates JWT tokens from multiple identity providers using a pipeline approach"
   ```

2. **Module Responsibilities**: For each module, analyze and write a 1-3 sentence description:

   **What to analyze** (in priority order):
   - `{module}/README.md` or `{module}/README.adoc` - module-specific documentation
   - `{module}/src/main/java/**/package-info.java` - package-level JavaDoc
   - `doc/` module content referencing the module
   - Key source files in `key_packages` to understand purpose

   **How to write**:
   - 1-3 sentences describing what the module does
   - Focus on the "what" and "why", not implementation details
   - Use active voice: "Validates...", "Provides...", "Manages..."

   **Example analysis flow**:
   ```
   1. Read oauth-sheriff-core/README.adoc (if exists)
   2. Read oauth-sheriff-core/src/main/java/de/cuioss/sheriff/oauth/core/package-info.java
   3. Scan doc/Specification.adoc for references to oauth-sheriff-core
   4. Write: "Validates JWT tokens from multiple identity providers using a pipeline approach with signature verification, claim validation, and caching"
   ```

   **Update command**:
   ```bash
   python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
     module update --module my-module --responsibility "Description here"
   ```

3. **Package Descriptions**: For each key package, analyze and write a 1-2 sentence description:

   **What to analyze** (in priority order):
   - `{package}/package-info.java` - package-level JavaDoc
   - Key classes in the package (interfaces, main implementations)
   - How the package is used by other packages

   **How to write**:
   - 1-2 sentences describing the package's core purpose
   - Focus on what the package provides, not implementation details
   - Use active voice: "Provides...", "Contains...", "Handles..."

   **Example analysis flow**:
   ```
   1. Read de/cuioss/sheriff/oauth/core/package-info.java
   2. Scan main interfaces/classes: TokenValidator, TokenPipeline
   3. Write: "Provides the core token validation pipeline with pluggable validators for signature, claims, and expiration checks"
   ```

   **Update command**:
   ```bash
   python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
     module set-package-description --module my-module \
     --package com.example.core.service \
     --description "Provides business services for token processing and validation"
   ```

4. **Add Missing Packages**: Add important packages not auto-detected:
   ```bash
   python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
     module add-package --module my-module --package com.example.core.service \
     --description "Provides business services for token processing"
   ```

### Required Enrichment Fields

| Field | Sources to Analyze | Action |
|-------|-------------------|--------|
| `project.description` | Project README | Auto-extracted during generate |
| `module.responsibility` | Module README, package-info.java, doc/ references, key source files | LLM writes 1-3 sentences per module |
| `key_packages[*].description` | package-info.java, key classes, usage patterns | LLM writes 1-2 sentences per package |

---

## Workflow: Update Module Metadata

**Pattern**: Read-Process-Write

Update module metadata including responsibility.

### Update Module

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  module update --module my-module \
  --responsibility "Core business logic and validation"
```

### Add Tip

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  module add-tip --module my-module \
  --tip "Use @ApplicationScoped for singleton services"
```

### Add Insight

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  module add-insight --module my-module \
  --insight "Heavy validation happens in onTrigger method"
```

---

## Workflow: Query Placement

**Pattern**: Read-Process-Write

Query where to place new components based on placement rules.

### Query Placement Rule

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  placement query --component-type processor
```

**Output**:
```toon
status: success
component_type: processor
module: nifi-cuioss-processors
package: de.cuioss.nifi.processors.{feature}
pattern: {Name}Processor.java
test_pattern: {Name}ProcessorTest.java
example: OAuthTokenProcessor.java
```

### List All Placement Rules

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  placement list
```

---

## Workflow: Validate Structure

**Pattern**: Validation Pipeline

Validate project-structure.toon format and consistency.

### Validate

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure validate
```

**Output**:
```toon
status: success
file: .plan/project-structure.toon
modules_count: 5
has_placement: true
has_conventions: true
warnings[0]:
```

---

## API Reference

### read

| Parameters | Purpose |
|------------|---------|
| (none) | Read full structure (generates if missing) |

### generate

| Parameters | Purpose |
|------------|---------|
| (none) | Generate structure from codebase |
| `--force` | Overwrite existing structure |

### validate

| Parameters | Purpose |
|------------|---------|
| (none) | Validate structure format |

### Noun: project

| Verb | Parameters | Purpose |
|------|------------|---------|
| `update` | `[--description] [--name]` | Update project-level metadata |

### raw-data-as-toon

| Parameters | Purpose |
|------------|---------|
| (none) | Output raw project data as TOON for LLM consumption |

Reads `.plan/raw-project-data.json` and outputs in TOON format. Returns error if file doesn't exist (run `collect-raw-data` first).

### modules-for-commands

| Parameters | Purpose |
|------------|---------|
| (none) | Output module data for command generation |
| `--module` | Filter to specific module |

**Output format** (TOON uniform array):
```toon
modules[3]{name,path,build_systems,packaging}:
my-core,my-core,maven,jar
my-ui,my-ui,maven+npm,war
e2e-tests,e2e-tests,npm,pom
```

Build systems are joined with `+` to avoid comma conflicts. This command is the API for `build_env persist` and other scripts that need module information from `raw-project-data.json`.

### Noun: module

| Verb | Parameters | Purpose |
|------|------------|---------|
| `get` | `--module` | Get specific module metadata |
| `list` | (none) | List all modules |
| `update` | `--module [--responsibility]` | Update module metadata |
| `add-tip` | `--module --tip` | Add implementation tip |
| `add-insight` | `--module --insight` | Add learned insight |
| `add-package` | `--module --package [--path] [--package-info] [--description]` | Add key package with structured info |
| `set-package-description` | `--module --package --description` | Set description for existing package |

### Noun: placement

| Verb | Parameters | Purpose |
|------|------------|---------|
| `query` | `--component-type` | Query placement rule for type |
| `list` | (none) | List all placement rules |
| `set` | `--component-type --module --package --pattern` | Set placement rule |

### Noun: convention

| Verb | Parameters | Purpose |
|------|------------|---------|
| `list` | (none) | List all conventions |
| `add` | `--category --convention` | Add convention |

### Noun: dependency

| Verb | Parameters | Purpose |
|------|------------|---------|
| `list` | (none) | List module dependencies |
| `add` | `--from-module --to-module` | Add module dependency |

---

## Data Model

### File Location

`.plan/project-structure.json`

### Structure

```toon
# Project Structure Knowledge

project:
  name: Project name (from raw-project-data.json)
  description: One-sentence project purpose (LLM-enriched)
  documentation:
    readme: path/to/README.md
    doc_files:
      - doc/file1.adoc
      - doc/file2.adoc

modules:
  module-name:
    responsibility: Brief description of module purpose (1-3 sentences)
    readme: module-name/README.adoc
    dependencies:
      - groupId:artifactId:scope
    key_packages:
      com.example.module.core:
        path: module-name/src/main/java/com/example/module/core
        package_info: module-name/src/main/java/com/example/module/core/package-info.java
        description: Core domain models and validation logic
      com.example.module.service:
        path: module-name/src/main/java/com/example/module/service
        package_info:
        description: Business services for processing requests
    tips:
      - Implementation tip 1
      - Implementation tip 2
    insights:
      - Learned insight from implementation
    best_practices:
      - Established best practice

dependencies:
  module-name:
    - dependency1
    - dependency2

placement:
  component-type:
    module: target-module
    package: com.example.{feature}
    pattern: {Name}Component.java
    test_pattern: {Name}ComponentTest.java
    example: ExampleComponent.java

conventions:
  naming:
    - Naming convention 1
  packages:
    - Package convention 1
  testing:
    - Testing convention 1
  documentation:
    - Documentation convention 1
```

---

## Integration Points

### With Solution Outline

Solution outline Step 0 loads this skill:
1. Read project-structure.json
2. Use module metadata for placement decisions
3. Follow placement rules for new components

### With Marshall Steward

Wizard Step 6 calls:
- `generate` to create initial structure
- Prompts for module responsibilities

Menu 3.4 provides:
- View structure
- Edit module metadata
- Update placement rules

### With Verification Phase

After implementation:
- `module add-insight` captures learnings
- Detected patterns update placement rules
- New modules added to structure

---

## Scripts

| Script | Notation |
|--------|----------|
| manage_project_structure | `plan-marshall:project-structure:manage_project_structure` |

Script characteristics:
- Uses Python stdlib only (json, argparse, pathlib)
- Outputs TOON to stdout
- Exit code 0 for success, 1 for errors
- Supports `--help` flag

---

## Error Handling

Standard error conditions:

```toon
status: error
error: project-structure.json not found. Run 'generate' command first
```

Error types:
- `project-structure.json not found` - Run generate or wizard
- `marshal.json not found` - Run /marshall-steward first
- `Unknown module: {name}` - Module not in structure
- `Unknown component type: {name}` - Placement rule not defined

---

## Related Skills

- `plan-marshall:plan-marshall-config` - marshal.json configuration (domains, modules)
- `plan-marshall:marshall-steward` - Wizard and menu integration
- `plan-marshall:toon-usage` - TOON format specification
- `pm-workflow:manage-solution-outline` - Solution outline consumer
