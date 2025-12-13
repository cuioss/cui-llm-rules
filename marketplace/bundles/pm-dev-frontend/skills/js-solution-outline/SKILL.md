---
name: js-solution-outline
description: Analyze JavaScript codebase and create solution outline with deliverables
allowed-tools: Read, Glob, Grep, Bash
---

# JavaScript Solution Outline Skill

**Role**: Domain analysis skill for JavaScript implementation tasks. Transforms the request into a solution document by analyzing the codebase.

**Key Pattern**: Single solution document - deliverables are consolidated into `solution_outline.md` via `manage-solution-outline` skill.

## Operation: decompose

**Input**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |

**Process**:

### Step 0: Load Solution Outline Skill

Load the solution outline skill for structure and examples:

```
Skill: pm-workflow:manage-solution-outline
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
python3 .plan/execute-script.py pm-workflow:manage-plan-documents:manage-plan-documents \
  request read \
  --plan-id {plan_id}

# Read plan configuration
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config read \
  --plan-id {plan_id}

# Read references (issue context if available)
python3 .plan/execute-script.py pm-workflow:manage-references:manage-references read \
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

Create a single solution document containing all deliverables. Each deliverable should be:
- **Independent**: Can be implemented without other deliverables completing first (when possible)
- **Testable**: Has clear completion criteria
- **Sized**: Reasonable scope (not too large, not too small)

Build a deliverables markdown section with numbered deliverables and required metadata:

```markdown
### 1. {Deliverable Title}

**Metadata:**
- change_type: {create|modify|refactor}
- execution_mode: automated
- domain: {javascript|javascript-testing}
- suggested_skill: pm-dev-frontend:{js-implement|js-refactor|js-implement-tests}
- suggested_workflow: {implement|refactor|implement-tests}
- context_skills: []
- depends: none

{JavaScript-specific technical deliverable description}

**Component**: {module|class|web-component|utility|config}
**Path**: `src/components/...`
**Package**: {package name for workspaces}
**Dependencies**: {npm packages, internal modules}
**Test Path**: `src/__tests__/...`
**Standards**: {ESLint, JSDoc, etc.}

**Verification:**
- Command: `npm test`
- Criteria: All tests pass, no lint errors

**Success Criteria:**
- {criterion 1}
- {criterion 2}

### 2. {Next Deliverable Title}
...
```

Write and validate the solution document using heredoc:

```bash
python3 .plan/execute-script.py pm-workflow:manage-solution-outline:manage-solution-outline \
  write \
  --plan-id {plan_id} \
  --validate <<'EOF'
# Solution Outline

## Summary
{one-line summary}

## Overview
{ASCII diagram showing component relationships}

## Deliverables

### 1. {Deliverable Title}
{content}
EOF
```

**Why heredoc?** Solution outlines contain ASCII diagrams and rich content that don't fit CLI parameter passing. The `--validate` flag is REQUIRED - it ensures structure validation on every write.

### Step 4: Record Issues as Lessons

On unexpected codebase state or ambiguity:

```bash
python3 .plan/execute-script.py plan-marshall:lessons-learned:manage-lesson add \
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

deliverables_count: {number of deliverables in solution document}
lessons_recorded: {count}
```

---

## Skill and Workflow Mapping

When creating deliverables, use this mapping for `suggested_skill` and `suggested_workflow`:

| Change Type | Component Type | Skill | Workflow |
|-------------|----------------|-------|----------|
| create | module | pm-dev-frontend:js-implement | implement |
| create | test | pm-dev-frontend:js-implement-tests | implement-tests |
| modify | any | pm-dev-frontend:js-implement | implement |
| refactor | any | pm-dev-frontend:js-refactor | refactor |
| fix | lint | pm-dev-frontend:js-enforce-eslint | fix-lint |
| fix | docs | pm-dev-frontend:js-fix-jsdoc | fix-docs |

### Domain Selection

| Content Type | Domain |
|--------------|--------|
| Production code (`src/`) | `javascript` |
| Test code (`src/__tests__/`, `test/`, `cypress/`) | `javascript-testing` |
| Mixed (prod + tests in same deliverable) | Split into separate deliverables |

### Context Skills Guidance

| Situation | Add to context_skills |
|-----------|----------------------|
| E2E testing with Cypress | `pm-dev-frontend:cui-cypress` |
| Complex CSS work | `pm-dev-frontend:cui-css` |

---

## Deliverable Decomposition Patterns

| Request Pattern | Typical Deliverables |
|-----------------|----------------------|
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
- Reference `pm-dev-frontend:cui-javascript-linting` standards

### Web Components
When task involves custom elements:
- Check for LitElement usage
- Identify component registration patterns
- Reference `pm-dev-frontend:cui-javascript` standards

### Testing
When task involves testing:
- Check for Jest configuration
- Identify Cypress E2E tests
- Reference `pm-dev-frontend:cui-javascript-unit-testing` standards

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

**Caller**: `pm-dev-frontend:js-solution-outline-agent`

**Script Notations** (use EXACTLY as shown):
- `pm-workflow:manage-solution-outline:manage-solution-outline` - Write and validate solution document (write --validate, read, list-deliverables)
- `pm-workflow:manage-plan-documents:manage-plan-documents` - Request operations (request read)
- `pm-workflow:manage-config:manage-config` - Plan config (read)
- `pm-workflow:manage-references:manage-references` - Plan references (read)
- `plan-marshall:lessons-learned:manage-lesson` - Record lessons on issues (add)

**Standards Referenced**:
- `pm-dev-frontend:cui-javascript` - Core JavaScript patterns
- `pm-dev-frontend:cui-javascript-linting` - ESLint/Prettier standards
- `pm-dev-frontend:cui-javascript-unit-testing` - Jest testing standards
- `pm-dev-frontend:cui-jsdoc` - Documentation standards
