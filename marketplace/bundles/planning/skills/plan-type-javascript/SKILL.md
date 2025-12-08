---
name: plan-type-javascript
description: JavaScript plan type providing domain-specific configuration and refinement for JavaScript/npm projects
allowed-tools: Read, Bash
---

# Plan Type: JavaScript (`planning:plan-type-javascript`)

**Use Cases**:
- JavaScript implementation tasks
- npm projects
- Web components
- CUI frontend libraries

**API**: Implements `planning:plan-type-api` contract.

**FQN Convention**: All skill/command references use fully qualified names: `{bundle}:{component}`

---

## Scripts

| Script | Purpose |
|--------|---------|
| `planning:manage-log/scripts/manage-work-log.py` | Work log entries |
| `planning:manage-config/scripts/manage-config.py` | Config field access |
| `planning:manage-references/scripts/manage-references.py` | Reference file CRUD |

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Technology | javascript |
| Verification | `/builder:builder-build-and-fix system=npm` |
| PR Workflow | true |
| Specify Agent | `cui-frontend-expert:js-specify-agent` |
| Plan Agent | `cui-frontend-expert:js-plan-agent` |

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

## Operation: specify

**Input**: `plan_id`, `requirement_id?` (optional for single-item mode)

**Before delegation**, log:
```bash
python3 {manage_work_log_path} add \
  --plan-id {plan_id} \
  --phase refine \
  --type progress \
  --summary "Delegating to js-specify-agent" \
  --detail "requirement_id={requirement_id|batch}"
```

**Delegation**:
```
Task(cui-frontend-expert:js-specify-agent,
     plan_id={plan_id},
     requirement_id={requirement_id})  # omit for batch
```

**After delegation**, log outcome:
```bash
python3 {manage_work_log_path} add \
  --plan-id {plan_id} \
  --phase refine \
  --type outcome \
  --summary "js-specify-agent completed: {spec_count} specs created" \
  --detail "lessons_recorded={count}"
```

**Returns**: `{status, spec_ids[], lessons_recorded}`

The agent analyzes JavaScript codebase, creates specifications with:
- Module design and exports
- Web component structure (for UI components)
- Event handling patterns
- State management approach
- Integration with existing modules

---

## Operation: plan

**Input**: `plan_id`, `specification_id?` (optional for single-item mode)

**Before delegation**, log:
```bash
python3 {manage_work_log_path} add \
  --plan-id {plan_id} \
  --phase refine \
  --type progress \
  --summary "Delegating to js-plan-agent" \
  --detail "specification_id={specification_id|batch}"
```

**Delegation**:
```
Task(cui-frontend-expert:js-plan-agent,
     plan_id={plan_id},
     specification_id={specification_id})  # omit for batch
```

**After delegation**, log outcome:
```bash
python3 {manage_work_log_path} add \
  --plan-id {plan_id} \
  --phase refine \
  --type outcome \
  --summary "js-plan-agent completed: {task_count} tasks created" \
  --detail "lessons_recorded={count}"
```

**Returns**: `{status, task_ids[], lessons_recorded}`

The agent creates tasks with JavaScript-specific steps:

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
