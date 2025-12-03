---
name: java-specify
description: Analyze Java codebase and create specifications from requirements with direct storage
allowed-tools: Read, Glob, Grep, Bash
---

# Java Specify Skill

**Role**: Domain analysis skill for Java implementation tasks. Transforms requirements into specifications by analyzing the codebase and writing SPECs directly.

**Key Pattern**: Direct storage - specifications are written immediately via `manage-specifications` script.

## Operation: specify

**Input**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `requirement_id` | string | No | Single REQ ID (omit for batch - queries all pending) |

**Process**:

### Step 1: Load Requirements

Script: `planning:manage-requirements/scripts/manage-requirement.py`

**Batch mode** (no requirement_id):
```bash
python3 {script_path} findAll \
  --plan-id {plan_id}
```

**Single mode** (requirement_id provided):
```bash
python3 {script_path} get \
  --plan-id {plan_id} \
  --number {requirement_id}
```

### Step 2: Load Context

Read plan context files:
```
Read {plan_dir}/task.md        # Original task description
Read {plan_dir}/config.toon    # build_system, plan_type
Read {plan_dir}/references.toon # issue_context if available
```

### Step 3: For Each Requirement

#### 3a. Analyze Codebase

Parse requirement intent and explore affected Java components:

**Project Structure Detection**:
```bash
Glob **/pom.xml              # Maven multi-module
Glob **/build.gradle*        # Gradle
Glob settings.gradle*        # Gradle settings
```

**Component Exploration**:
```bash
Grep "class {ClassName}" --type java
Grep "interface {InterfaceName}" --type java
Glob src/main/java/**/*.java
Read {java-file-path}
```

**Identify**:
- Classes, interfaces, modules affected
- Package structure and placement
- Dependencies (CDI, external libs)
- Test requirements
- Complexity assessment

#### 3b. Create Specification

Write specification with Java-specific technical details:

Script: `planning:manage-specifications/scripts/manage-specification.py`

```bash
python3 {script_path} add \
  --plan-id {plan_id} \
  --title "{component} implementation" \
  --requirements "REQ-{n}" \
  --body "{Java-specific technical specification}"
```

**Specification Body Content**:
- Component type (class, interface, module, config)
- Target path (e.g., `src/main/java/de/cuioss/...`)
- Module assignment (for multi-module projects)
- Dependencies and integration points
- Test requirements and test path
- Standards to follow (CDI, logging, etc.)

#### 3c. Record Issues as Lessons

On unexpected codebase state or ambiguity:

Script: `planning:manage-lessons/scripts/manage-lesson.py`

```bash
python3 {script_path} add \
  --component-type skill \
  --component-name java-specify \
  --category observation \
  --title "{issue summary}" \
  --detail "{context and resolution approach}"
```

### Step 4: Return Results

**Output**:
```toon
status: success
plan_id: {plan_id}

specs_created[N]:
- SPEC-1
- SPEC-2
- SPEC-3

lessons_recorded: {count}
```

---

## Component Types

| Type | Indicators | Example |
|------|------------|---------|
| `class` | Service, ServiceImpl, Repository, Controller | UserService.java |
| `interface` | Interface definition | AuthenticationProvider.java |
| `module` | pom.xml, build.gradle reference | core-service module |
| `config` | Config, Configuration suffix | CacheConfig.java |
| `package` | Package path mentioned | de.cuioss.service.auth |

---

## Scope Detection

| Indicator | Scope |
|-----------|-------|
| "implement", "add", "create", "new" | create |
| "fix", "update", "modify", "change" | modify |
| "refactor", "reorganize", "migrate" | refactor |

---

## Complexity Assessment

| Factor | Low | Medium | High |
|--------|-----|--------|------|
| Files affected | 1-3 | 4-8 | 9+ |
| Cross-module | No | 1 module | 2+ modules |
| Breaking changes | None | Internal | Public API |
| Dependencies | 0-2 | 3-5 | 6+ |
| Test coverage needed | Unit only | Unit + Integration | Full suite |

---

## Test Requirements

| Component Type | Test Required | Test Type |
|---------------|---------------|-----------|
| Service class | Yes | Unit + Integration |
| Repository | Yes | Integration |
| Controller | Yes | Integration |
| DTO/Model | Conditional | Unit (if logic) |
| Config class | Conditional | Integration |
| Utility class | Yes | Unit |

---

## CUI-Specific Patterns

### Logging Analysis
When task involves logging:
- Check for `CuiLogger` usage
- Identify `LogRecord` requirements
- Reference `cui-java-expert:cui-java-core` standards

### CDI Analysis
When task involves CDI:
- Check `beans.xml` configuration
- Identify scope annotations
- Reference `cui-java-expert:cui-java-cdi` standards

### Testing Analysis
When task involves testing:
- Check for `@EnabledIfReachable` patterns
- Identify generator requirements
- Reference `cui-java-expert:cui-java-unit-testing` standards

---

## Error Handling

### Component Not Found

| Scope | Action |
|-------|--------|
| `create` | Continue (expected - component doesn't exist yet) |
| `modify` | Warn and ask for clarification |
| `refactor` | Error and request correct path |

### Module Not Found

If module doesn't exist in multi-module project:
- Check if task is to create the module
- Otherwise error with suggestion

### Ambiguous Component

If multiple classes match the name:
- List all matches with paths
- Ask user to select correct one

---

## Integration

**Caller**: `cui-java-expert:java-specify-agent`

**Scripts Used**:
- `planning:manage-requirements/scripts/manage-requirement.py` - Load requirements
- `planning:manage-specifications/scripts/manage-specification.py` - Create specifications
- `planning:manage-lessons/scripts/manage-lesson.py` - Record lessons on issues

**Standards Referenced**:
- `cui-java-expert:cui-java-core` - Core Java patterns
- `cui-java-expert:cui-java-cdi` - CDI/Quarkus patterns
- `cui-java-expert:cui-java-unit-testing` - Testing standards
