---
name: js-specify
description: Analyze JavaScript codebase and create specifications from requirements with direct storage
allowed-tools: Read, Glob, Grep, Bash
---

# JavaScript Specify Skill

**Role**: Domain analysis skill for JavaScript implementation tasks. Transforms requirements into specifications by analyzing the codebase and writing SPECs directly.

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

Parse requirement intent and explore affected JavaScript components:

**Project Structure Detection**:
```bash
Glob package.json           # npm project
Glob **/package.json        # workspace packages
Glob pom.xml               # Maven integration (frontend-maven-plugin)
```

**Component Exploration**:
```bash
Grep "class {ClassName}" --type js
Grep "export.*{FunctionName}" --type js
Glob src/**/*.js
Glob src/**/*.mjs
Read {js-file-path}
```

**Identify**:
- Modules, classes, web components affected
- Directory structure and placement
- Dependencies (npm packages, internal modules)
- Test requirements
- Complexity assessment

#### 3b. Create Specification

Write specification with JavaScript-specific technical details:

Script: `planning:manage-specifications/scripts/manage-specification.py`

```bash
python3 {script_path} add \
  --plan-id {plan_id} \
  --title "{component} implementation" \
  --requirements "REQ-{n}" \
  --body "{JavaScript-specific technical specification}"
```

**Specification Body Content**:
- Component type (module, class, web-component, utility, config)
- Target path (e.g., `src/components/...`)
- Package assignment (for workspaces)
- Dependencies and imports
- Test requirements and test path
- Standards to follow (ESLint, JSDoc, etc.)

#### 3c. Record Issues as Lessons

On unexpected codebase state or ambiguity:

Script: `planning:manage-lessons/scripts/manage-lesson.py`

```bash
python3 {script_path} add \
  --component-type skill \
  --component-name js-specify \
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
| `module` | ES module, export statements | user-service.js |
| `class` | Class definition | AuthenticationProvider.js |
| `web-component` | Custom element, LitElement | my-button.js |
| `utility` | Helper functions, no state | string-utils.js |
| `config` | Configuration file | eslint.config.js |

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
| Cross-package | No | 1 package | 2+ packages |
| Breaking changes | None | Internal | Public API |
| Dependencies | 0-2 | 3-5 | 6+ |
| Test coverage needed | Unit only | Unit + E2E | Full suite |

---

## Test Requirements

| Component Type | Test Required | Test Type |
|---------------|---------------|-----------|
| Module | Yes | Unit (Jest) |
| Class | Yes | Unit (Jest) |
| Web Component | Yes | Unit + E2E (Cypress) |
| Utility | Yes | Unit (Jest) |
| Config | Conditional | Lint verification |

---

## CUI Frontend Patterns

### ESLint/Prettier
When task involves code quality:
- Check for existing ESLint configuration
- Identify Prettier settings
- Reference `cui-frontend-expert:cui-javascript-linting` standards

### Web Components
When task involves custom elements:
- Check for LitElement usage
- Identify component registration patterns
- Reference `cui-frontend-expert:cui-javascript` standards

### Testing
When task involves testing:
- Check for Jest configuration
- Identify Cypress E2E tests
- Reference `cui-frontend-expert:cui-javascript-unit-testing` standards

---

## Error Handling

### Component Not Found

| Scope | Action |
|-------|--------|
| `create` | Continue (expected - component doesn't exist yet) |
| `modify` | Warn and ask for clarification |
| `refactor` | Error and request correct path |

### Package Not Found

If package doesn't exist in workspace:
- Check if task is to create the package
- Otherwise error with suggestion

### Ambiguous Component

If multiple files match the name:
- List all matches with paths
- Ask user to select correct one

---

## Integration

**Caller**: `cui-frontend-expert:js-specify-agent`

**Scripts Used**:
- `planning:manage-requirements/scripts/manage-requirement.py` - Load requirements
- `planning:manage-specifications/scripts/manage-specification.py` - Create specifications
- `planning:manage-lessons/scripts/manage-lesson.py` - Record lessons on issues

**Standards Referenced**:
- `cui-frontend-expert:cui-javascript` - Core JavaScript patterns
- `cui-frontend-expert:cui-javascript-linting` - ESLint/Prettier standards
- `cui-frontend-expert:cui-javascript-unit-testing` - Jest testing standards
- `cui-frontend-expert:cui-jsdoc` - Documentation standards
