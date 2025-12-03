---
name: plan-type-javascript
description: JavaScript plan type providing domain-specific configuration and refinement for JavaScript/npm projects
allowed-tools: Read, Bash
---

# Plan Type: JavaScript

**Use Cases**:
- JavaScript implementation tasks
- npm projects
- Web components
- CUI frontend libraries

**API**: Implements `planning:plan-type-api` contract.

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Technology | javascript |
| Verification | `/builder-build-and-fix system=npm` |
| PR Workflow | true |

---

## Operation: configure

**Input**: `plan_id`

**References fields added**:

| Field | Value |
|-------|-------|
| `standards` | `["cui-frontend-expert:cui-javascript", "cui-frontend-expert:cui-jsdoc", "cui-frontend-expert:cui-javascript-unit-testing", "cui-frontend-expert:cui-javascript-linting"]` |
| `adrs` | `[]` |
| `interfaces` | `[]` |
| `dependencies` | `[]` |

**Config fields added**:

| Field | Value |
|-------|-------|
| `create_pr` | `true` |
| `verification_required` | `true` |
| `verification_command` | `/builder-build-and-fix system=npm` |
| `branch_strategy` | `feature` |

---

## Operation: specify

**Input**: `plan_id`

**JavaScript-Specific Content** (included in specifications):
- Module design and exports
- Web component structure (for UI components)
- Event handling patterns
- State management approach
- Integration with existing modules

---

## Operation: plan

**Input**: `plan_id`

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
