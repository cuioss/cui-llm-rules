---
name: js-analysis
description: Analyzes JavaScript implementation tasks to identify components, test requirements, and dependencies. Implements planning:analysis-api contract.
allowed-tools: Read, Glob, Grep, Bash
---

# JavaScript Analysis Skill

**Role**: Domain analysis skill for JavaScript implementation tasks. Analyzes task requirements and codebase to identify JavaScript components (modules, classes, web components) and their dependencies.

**Integration**: Called by `planning:plan-refine` during the refine phase for `implementation` plan types with JavaScript projects.

**API Contract**: Load `planning:analysis-api` for full input/output specification.

```
Skill: planning:analysis-api
```

## Operation: analyze

**Contract**: See `planning:analysis-api` for full input/output specification.

### Domain-Specific Input

| Parameter | Description |
|-----------|-------------|
| `build_system` | Required: `npm` |

### Domain-Specific Output

**Component Types**: `module`, `class`, `web-component`, `utility`, `config`

**Domain-Specific Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `test_required` | boolean | Whether unit tests are needed |
| `test_path` | string | Path to test file |

**Example Output**:
```yaml
analysis_result:
  status: "success"
  components:
    - name: "cui-data-table"
      type: "web-component"
      scope: "create"
      path: "src/components/cui-data-table/cui-data-table.js"
      test_required: true
      test_path: "test/components/cui-data-table/cui-data-table.spec.js"
      dependencies:
        - "cui-base-component"
      complexity: "high"
      notes: "Main table component with DOM manipulation"
```

## Analysis Process

### Step 1: Parse Task Intent

Extract from task description:
- Action verbs: implement, add, create, fix, refactor, update
- Component types: component, module, class, function, utility
- Target paths: Look for `src/`, `lib/`, component names
- Features: UI, logic, integration keywords

### Step 2: Detect Project Structure

**Package Configuration**:
```bash
Read package.json
```

**Source Structure**:
```bash
Glob src/**/*.js
Glob src/**/*.mjs
```

**Test Structure**:
```bash
Glob test/**/*.spec.js
Glob src/**/*.test.js
```

**Web Components**:
```bash
Grep "customElements.define" --type js
Grep "class.*extends.*HTMLElement" --type js
```

### Step 3: Explore Affected Components

For each identified component:

**Modules/Classes**:
```bash
Grep "export class {ClassName}" --type js
Grep "export function {FunctionName}" --type js
Read {js-file-path}
```

**Web Components**:
```bash
Grep "customElements.define.*{component-tag}" --type js
Read {component-path}
```

**Configuration**:
```bash
Glob **/*.config.js
Glob **/jest.config.*
Glob **/eslint.config.*
```

### Step 4: Identify Dependencies

For each component, analyze:
- **Import statements**: `import { X } from './module'`
- **Dynamic imports**: `import('./module')`
- **Package dependencies**: From `package.json`
- **Web component dependencies**: Nested component usage
- **CSS dependencies**: Imported stylesheets

### Step 5: Determine Test Requirements

| Component Type | Test Required | Test Type |
|---------------|---------------|-----------|
| Web component | Yes | Unit + Cypress |
| Utility module | Yes | Unit |
| Class | Yes | Unit |
| Configuration | Conditional | Integration |
| Pure function | Yes | Unit |

### Step 6: Assess Complexity

| Factor | Low | Medium | High |
|--------|-----|--------|------|
| Files affected | 1-3 | 4-8 | 9+ |
| Dependencies | 0-2 | 3-5 | 6+ |
| Breaking changes | None | Internal | Public API |
| Test coverage needed | Unit only | Unit + E2E | Full suite |
| CSS changes | None | Component | Global |

### Step 7: Return Components

Return structured component list with all metadata for plan-type skill to generate tasks.

## Component Type Detection

| Indicator | Type |
|-----------|------|
| `extends HTMLElement` | web-component |
| `customElements.define` | web-component |
| `export class` | class |
| `export function` | module |
| `export default` | module |
| Ends with `.config.js` | config |
| In `utils/` directory | utility |

## Scope Detection

| Indicator | Scope |
|-----------|-------|
| "implement", "add", "create", "new" | create |
| "fix", "update", "modify", "change" | modify |
| "refactor", "reorganize", "migrate" | refactor |

## Example Analysis

**Task**: "Create a data-table web component with sorting and pagination"

**Analysis Output**:
```yaml
components:
  - name: "cui-data-table"
    type: "web-component"
    scope: "create"
    path: "src/components/cui-data-table/cui-data-table.js"
    test_required: true
    test_path: "test/components/cui-data-table/cui-data-table.spec.js"
    dependencies:
      - "cui-base-component"
    complexity: "high"
    notes: "Main table component with DOM manipulation"

  - name: "cui-data-table-header"
    type: "web-component"
    scope: "create"
    path: "src/components/cui-data-table/cui-data-table-header.js"
    test_required: true
    test_path: "test/components/cui-data-table/cui-data-table-header.spec.js"
    dependencies:
      - "cui-data-table"
    complexity: "medium"
    notes: "Header with sorting controls"

  - name: "cui-pagination"
    type: "web-component"
    scope: "create"
    path: "src/components/cui-pagination/cui-pagination.js"
    test_required: true
    test_path: "test/components/cui-pagination/cui-pagination.spec.js"
    dependencies: []
    complexity: "medium"
    notes: "Reusable pagination component"

  - name: "table-utils"
    type: "utility"
    scope: "create"
    path: "src/utils/table-utils.js"
    test_required: true
    test_path: "test/utils/table-utils.spec.js"
    dependencies: []
    complexity: "low"
    notes: "Sorting and filtering utilities"
```

## Integration with Plan-Type Skills

After analysis completes, return components to `plan-refine`, which passes them to:

```
Skill: planning:plan-type-implementation
operation: generate-tasks
plan_id: {plan_id}
components: {components from analysis}
```

The plan-type skill then generates appropriate tasks (implement, test, verify) and writes them directly to plan.md.

## CUI-Specific Patterns

### Web Component Analysis
When task involves web components:
- Check for `cui-` prefix convention
- Identify base component inheritance
- Flag for `cui-frontend-expert:cui-javascript` standards

### Testing Analysis
When task involves testing:
- Check for Jest configuration
- Identify Cypress E2E requirements
- Flag for `cui-frontend-expert:cui-javascript-unit-testing` standards

### Linting Analysis
When task involves linting:
- Check ESLint configuration
- Identify rule violations
- Flag for `cui-frontend-expert:cui-javascript-linting` standards

### JSDoc Analysis
When task involves documentation:
- Check for JSDoc coverage
- Identify documentation gaps
- Flag for `cui-frontend-expert:cui-jsdoc` standards

## Error Handling

### Module Not Found
If task references a module that doesn't exist:
- For "create" scope: Continue (expected)
- For "modify" scope: Warn and ask for clarification
- For "refactor" scope: Error and request correct path

### Package Not Found
If npm package isn't installed:
- Check if task is to add the dependency
- Otherwise warn about missing dependency

### Ambiguous Component
If multiple files match the name:
- List all matches with paths
- Ask user to select correct one

## Quality Checklist

- [x] Self-contained with relative paths
- [x] Returns structured components[] for plan generation
- [x] Identifies test requirements for each component
- [x] Assesses complexity for task planning
- [x] Handles web components and ES modules
- [x] Respects CUI-specific patterns
