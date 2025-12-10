---
name: js-solution-outline
description: Analyze JavaScript codebase and decompose request into goals
allowed-tools: Read, Glob, Grep, Bash
---

# JavaScript Goals Skill

**Role**: Domain analysis skill for JavaScript implementation tasks. Transforms the request into a solution document by analyzing the codebase.

**Key Pattern**: Single solution document - goals are consolidated into `solution_outline.md` via `manage-plan-documents` skill.

## Operation: decompose

**Input**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |

**Process**:

### Step 0: Load Solution Outline Skill

Load the solution outline skill for structure and examples:

```
Skill: planning:manage-solution-outline
```

This provides:
- Required document structure (Summary, Overview, Deliverables)
- ASCII diagram patterns for JavaScript/frontend features
- Deliverable reference format
- Realistic examples

### Step 1: Load Request Context

Load plan context via manage-* scripts:

```bash
# Read original request description
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  request read \
  --plan-id {plan_id}

# Read plan configuration
python3 .plan/execute-script.py planning:manage-config:manage-config read \
  --plan-id {plan_id}

# Read references (issue context if available)
python3 .plan/execute-script.py planning:manage-references:manage-references read \
  --plan-id {plan_id}
```

Parse the request to identify what needs to be accomplished.

### Step 2: Analyze Codebase

Parse request intent and explore affected JavaScript components:

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

### Step 3: Create Solution Document

Create a single solution document containing all goals. Each goal should be:
- **Independent**: Can be implemented without other goals completing first (when possible)
- **Testable**: Has clear completion criteria
- **Sized**: Reasonable scope (not too large, not too small)

Build a goals markdown section with numbered goals:

```markdown
### 1. {Goal Title}

{JavaScript-specific technical goal description}

**Component**: {module|class|web-component|utility|config}
**Path**: `src/components/...`
**Package**: {package name for workspaces}
**Dependencies**: {npm packages, internal modules}
**Test Path**: `src/__tests__/...`
**Standards**: {ESLint, JSDoc, etc.}

**Success Criteria:**
- {criterion 1}
- {criterion 2}

### 2. {Next Goal Title}
...
```

Write the solution document directly using Claude Code's Write tool to: `.plan/plans/{plan_id}/solution_outline.md`

Then validate the structure:

```bash
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  solution validate \
  --plan-id {plan_id}
```

**Why direct Write?** Solution outlines contain ASCII diagrams and rich content that don't fit CLI parameter passing. The agent generates the full markdown document and writes it directly.

### Step 4: Record Issues as Lessons

On unexpected codebase state or ambiguity:

```bash
python3 .plan/execute-script.py planning:manage-lessons:manage-lesson add \
  --component-type skill \
  --component-name js-solution-outline \
  --category observation \
  --title "{issue summary}" \
  --detail "{context and resolution approach}"
```

### Step 5: Return Results

**Output**:
```toon
status: success
plan_id: {plan_id}
solution_created: true

goals_count: {number of goals in solution document}
lessons_recorded: {count}
```

---

## Goal Decomposition Patterns

| Request Pattern | Typical Goals |
|-----------------|---------------|
| "Add form validation" | 1. Create validation utility 2. Add validation to form component 3. Add error display 4. Add tests |
| "Implement new component" | 1. Create component class 2. Add CSS styles 3. Register custom element 4. Add unit tests |
| "Refactor to ES modules" | 1. Convert CommonJS to ES modules 2. Update imports 3. Update build config 4. Update tests |

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

**Caller**: `cui-frontend-expert:js-solution-outline-agent`

**Scripts Used**:
- `planning:manage-solution-outline` - Write and validate solution document
- `planning:manage-plan-documents` - Read request document
- `planning:manage-lessons` - Record lessons on issues

**Standards Referenced**:
- `cui-frontend-expert:cui-javascript` - Core JavaScript patterns
- `cui-frontend-expert:cui-javascript-linting` - ESLint/Prettier standards
- `cui-frontend-expert:cui-javascript-unit-testing` - Jest testing standards
- `cui-frontend-expert:cui-jsdoc` - Documentation standards
