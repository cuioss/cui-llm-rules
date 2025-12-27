---
name: project-structure
description: Project structure knowledge base for module metadata, placement rules, and architectural conventions
allowed-tools: Read, Write, Edit, Bash
---

# Project Structure Skill

Manages project structure knowledge in `.plan/project-structure.toon` for solution outline support.

## What This Skill Provides

- **Module Metadata**: Responsibility, layer, technology, key packages per module
- **Placement Rules**: Where to place new components by type
- **Conventions**: Naming, packaging, testing, documentation patterns
- **Dependencies**: Module dependencies and layer constraints
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
file: .plan/project-structure.toon

modules:
  my-module:
    responsibility: Core business logic
    layer: service
    technology:
      framework: quarkus
      di: cdi
      testing: junit5
    key_packages:
      - de.cuioss.mymodule.service
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
1. Read marshal.json for module list
2. Infer domains from build_systems (maven/gradle -> java, npm -> javascript)
3. Infer layers from module names and types
4. Detect key packages from source directories
5. Create minimal structure for user refinement

### Force Regenerate

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  generate --force
```

---

## Workflow: Update Module Metadata

**Pattern**: Read-Process-Write

Update module metadata including responsibility, layer, and technology.

### Update Module

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  module update --module my-module \
  --responsibility "Core business logic and validation" \
  --layer service
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

### Noun: module

| Verb | Parameters | Purpose |
|------|------------|---------|
| `get` | `--module` | Get specific module metadata |
| `list` | (none) | List all modules |
| `update` | `--module [--responsibility] [--layer]` | Update module metadata |
| `add-tip` | `--module --tip` | Add implementation tip |
| `add-insight` | `--module --insight` | Add learned insight |
| `set-technology` | `--module --framework [--di] [--testing]` | Set technology stack |
| `add-package` | `--module --package` | Add key package |

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

`.plan/project-structure.toon`

### Structure

```toon
# Project Structure Knowledge

modules:
  module-name:
    responsibility: Brief description of module purpose
    layer: extension|presentation|service|packaging|testing|api
    technology:
      framework: framework-name
      di: cdi|spring|none
      testing: junit5|jest|playwright
    key_packages:
      - com.example.module.package1
      - com.example.module.package2
    tips:
      - Implementation tip 1
      - Implementation tip 2
    insights:
      - Learned insight from implementation
    best_practices:
      - Established best practice

dependencies:
  module_deps:
    dependent-module:
      - dependency1
      - dependency2
  layer_rules:
    layer-name:
      allowed:
        - allowed-layer1
      forbidden:
        - forbidden-layer1

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

## Layer Definitions

| Layer | Description | Examples |
|-------|-------------|----------|
| `extension` | Plugin/extension code, core functionality | processors, services |
| `presentation` | UI components, web interfaces | ui, frontend |
| `service` | Business logic | service modules |
| `api` | Public API definitions | api modules |
| `packaging` | Build artifacts, assembly | nar, assembly |
| `testing` | Test modules (integration, e2e) | integration-testing, e2e |

See `standards/layer-definitions.md` for detailed layer rules.

---

## Integration Points

### With Solution Outline

Solution outline Step 0 loads this skill:
1. Read project-structure.toon
2. Use module metadata for placement decisions
3. Apply layer constraints to deliverables
4. Follow placement rules for new components

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
error: project-structure.toon not found. Run 'generate' command first
```

Error types:
- `project-structure.toon not found` - Run generate or wizard
- `marshal.json not found` - Run /marshall-steward first
- `Unknown module: {name}` - Module not in structure
- `Unknown component type: {name}` - Placement rule not defined

---

## Related Skills

- `plan-marshall:plan-marshall-config` - marshal.json configuration (domains, modules)
- `plan-marshall:marshall-steward` - Wizard and menu integration
- `plan-marshall:toon-usage` - TOON format specification
- `pm-workflow:manage-solution-outline` - Solution outline consumer
