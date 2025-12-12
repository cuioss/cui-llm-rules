---
name: plan-type-javascript
description: JavaScript plan type for npm/frontend projects
allowed-tools: Read, Bash

# Detection patterns and keywords
patterns:
  - "*.js"
  - "*.ts"
  - "*.jsx"
  - "*.tsx"
  - "package.json"
keywords:
  - javascript
  - typescript
  - npm
  - frontend
  - web component
  - react
  - node

# Agent routing
domain:
  solution_outline_agent: pm-dev-frontend:js-solution-outline-agent
  task_plan_agent: pm-dev-frontend:js-task-plan-agent

# Plan defaults for this type
plan_defaults:
  verification_command: /pm-dev-builder:builder-build-and-fix system=npm
  pr_workflow: true
  standards:
    - pm-dev-frontend:cui-javascript
    - pm-dev-frontend:cui-jsdoc
    - pm-dev-frontend:cui-javascript-unit-testing
    - pm-dev-frontend:cui-javascript-linting
---

# Plan Type: JavaScript (`pm-workflow:plan-type-javascript`)

**Use Cases**:
- JavaScript implementation tasks
- npm projects
- Web components
- CUI frontend libraries

**API**: Implements `pm-workflow:plan-type-api` contract.

## Domain Configuration

The `domain:` frontmatter provides structured routing information for commands:

| Field | Value | Purpose |
|-------|-------|---------|
| `solution_outline_agent` | `pm-dev-frontend:js-solution-outline-agent` | Creates solution outline with deliverables |
| `task_plan_agent` | `pm-dev-frontend:js-task-plan-agent` | Creates tasks from deliverables |

The `plan_defaults:` frontmatter is automatically read by `manage-config create` during plan initialization:

| Field | Value | Config Field |
|-------|-------|--------------|
| `verification_command` | `/pm-dev-builder:builder-build-and-fix system=npm` | `verification_command`, `verification_required` |
| `pr_workflow` | `true` | `create_pr`, `branch_strategy` |
| `standards` | JavaScript, JSDoc, Unit testing, Linting | (informational) |

---

## Agent Behavior

### js-solution-outline-agent

Analyzes JavaScript codebase and creates deliverables with:
- Module design and exports
- Web component structure (for UI components)
- Event handling patterns
- State management approach
- Integration with existing modules

**Returns**: `{status, deliverable_count, solution_document, lessons_recorded}`

### js-task-plan-agent

Creates tasks with JavaScript-specific steps:

**Module Task Steps**:
1. Create/modify implementation file at `{path}`
2. Add unit tests (load `pm-dev-frontend:cui-javascript-unit-testing`)
3. Add JSDoc (load `pm-dev-frontend:cui-jsdoc`)
4. Follow CUI patterns (load `pm-dev-frontend:cui-javascript`)
5. Verify `npm test` passes

**Web Component Task Steps**:
1. Create/modify web component at `{path}`
2. Follow web component patterns (load `pm-dev-frontend:cui-javascript`)
3. Add unit tests (load `pm-dev-frontend:cui-javascript-unit-testing`)
4. Add Cypress tests (load `pm-dev-frontend:cui-cypress`)
5. Add JSDoc (load `pm-dev-frontend:cui-jsdoc`)
6. Verify `npm test` passes

**Returns**: `{status, task_ids[], lessons_recorded}`
