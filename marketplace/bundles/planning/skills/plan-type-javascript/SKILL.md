---
name: plan-type-javascript
description: JavaScript plan type for npm/frontend projects
allowed-tools: Read, Bash
domain:
  solution_outline_agent: cui-frontend-expert:js-solution-outline-agent
  plan_agent: cui-frontend-expert:js-plan-agent
  verification_command: /builder:builder-build-and-fix system=npm
  pr_workflow: true
  standards:
    - cui-frontend-expert:cui-javascript
    - cui-frontend-expert:cui-jsdoc
    - cui-frontend-expert:cui-javascript-unit-testing
    - cui-frontend-expert:cui-javascript-linting
---

# Plan Type: JavaScript (`planning:plan-type-javascript`)

**Use Cases**:
- JavaScript implementation tasks
- npm projects
- Web components
- CUI frontend libraries

**API**: Implements `planning:plan-type-api` contract.

## Domain Configuration

The `domain:` frontmatter provides structured routing information for commands:

| Field | Value | Purpose |
|-------|-------|---------|
| `solution_outline_agent` | `cui-frontend-expert:js-solution-outline-agent` | Decomposes request into goals |
| `plan_agent` | `cui-frontend-expert:js-plan-agent` | Creates tasks from goals |
| `verification_command` | `/builder:builder-build-and-fix system=npm` | Build verification |
| `pr_workflow` | `true` | Create PR after execution |
| `standards` | JavaScript, JSDoc, Unit testing, Linting | Skills to load |

---

## Operation: configure

**Input**: `plan_id`

**References fields added** (via `planning:manage-references set`):

| Field | Value |
|-------|-------|
| `standards` | `["cui-frontend-expert:cui-javascript", "cui-frontend-expert:cui-jsdoc", "cui-frontend-expert:cui-javascript-unit-testing", "cui-frontend-expert:cui-javascript-linting"]` |
| `adrs` | `[]` |
| `interfaces` | `[]` |
| `dependencies` | `[]` |

**Config fields added** (via `planning:manage-config set`):

| Field | Value |
|-------|-------|
| `create_pr` | `true` |
| `verification_required` | `true` |
| `verification_command` | `/builder:builder-build-and-fix system=npm` |
| `branch_strategy` | `feature` |

---

## Agent Behavior

### js-solution-outline-agent

Analyzes JavaScript codebase and creates goals with:
- Module design and exports
- Web component structure (for UI components)
- Event handling patterns
- State management approach
- Integration with existing modules

**Returns**: `{status, goal_count, solution_document, lessons_recorded}`

### js-plan-agent

Creates tasks with JavaScript-specific steps:

**Module Task Steps**:
1. Create/modify implementation file at `{path}`
2. Add unit tests (load `cui-frontend-expert:cui-javascript-unit-testing`)
3. Add JSDoc (load `cui-frontend-expert:cui-jsdoc`)
4. Follow CUI patterns (load `cui-frontend-expert:cui-javascript`)
5. Verify `npm test` passes

**Web Component Task Steps**:
1. Create/modify web component at `{path}`
2. Follow web component patterns (load `cui-frontend-expert:cui-javascript`)
3. Add unit tests (load `cui-frontend-expert:cui-javascript-unit-testing`)
4. Add Cypress tests (load `cui-frontend-expert:cui-cypress`)
5. Add JSDoc (load `cui-frontend-expert:cui-jsdoc`)
6. Verify `npm test` passes

**Returns**: `{status, task_ids[], lessons_recorded}`
