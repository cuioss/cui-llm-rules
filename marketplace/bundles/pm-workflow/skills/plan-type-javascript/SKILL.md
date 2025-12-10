---
name: plan-type-javascript
description: JavaScript plan type for npm/frontend projects
allowed-tools: Read, Bash
domain:
  solution_outline_agent: pm-frontend:js-solution-outline-agent
  task_plan_agent: pm-frontend:js-task-plan-agent
  verification_command: /pm-builder:builder-build-and-fix system=npm
  pr_workflow: true
  standards:
    - pm-frontend:cui-javascript
    - pm-frontend:cui-jsdoc
    - pm-frontend:cui-javascript-unit-testing
    - pm-frontend:cui-javascript-linting
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
| `solution_outline_agent` | `pm-frontend:js-solution-outline-agent` | Creates solution outline with deliverables |
| `task_plan_agent` | `pm-frontend:js-task-plan-agent` | Creates tasks from deliverables |
| `verification_command` | `/pm-builder:builder-build-and-fix system=npm` | Build verification |
| `pr_workflow` | `true` | Create PR after execution |
| `standards` | JavaScript, JSDoc, Unit testing, Linting | Skills to load |

---

## Operation: configure

**Input**: `plan_id`

**References fields added** (via `pm-workflow:manage-references:manage-references set`):

| Field | Value |
|-------|-------|
| `standards` | `["pm-frontend:cui-javascript", "pm-frontend:cui-jsdoc", "pm-frontend:cui-javascript-unit-testing", "pm-frontend:cui-javascript-linting"]` |
| `adrs` | `[]` |
| `interfaces` | `[]` |
| `dependencies` | `[]` |

**Config fields added** (via `pm-workflow:manage-config:manage-config set`):

| Field | Value |
|-------|-------|
| `create_pr` | `true` |
| `verification_required` | `true` |
| `verification_command` | `/pm-builder:builder-build-and-fix system=npm` |
| `branch_strategy` | `feature` |

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
2. Add unit tests (load `pm-frontend:cui-javascript-unit-testing`)
3. Add JSDoc (load `pm-frontend:cui-jsdoc`)
4. Follow CUI patterns (load `pm-frontend:cui-javascript`)
5. Verify `npm test` passes

**Web Component Task Steps**:
1. Create/modify web component at `{path}`
2. Follow web component patterns (load `pm-frontend:cui-javascript`)
3. Add unit tests (load `pm-frontend:cui-javascript-unit-testing`)
4. Add Cypress tests (load `pm-frontend:cui-cypress`)
5. Add JSDoc (load `pm-frontend:cui-jsdoc`)
6. Verify `npm test` passes

**Returns**: `{status, task_ids[], lessons_recorded}`
