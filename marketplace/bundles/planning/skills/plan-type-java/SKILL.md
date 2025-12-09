---
name: plan-type-java
description: Java plan type providing domain-specific configuration and refinement for Java/Maven/Gradle projects
allowed-tools: Read, Bash
---

# Plan Type: Java (`planning:plan-type-java`)

**Use Cases**:
- Java implementation tasks
- Maven/Gradle projects
- CUI Java libraries and modules
- Quarkus/CDI applications

**API**: Implements `planning:plan-type-api` contract.

**FQN Convention**: All skill/command references use fully qualified names: `{bundle}:{component}`

---

## Scripts

| Script | Purpose |
|--------|---------|
| `planning:manage-log` | Work log entries |
| `planning:manage-config` | Config field access |
| `planning:manage-references` | Reference file CRUD |

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Technology | java |
| Verification | `/builder:builder-build-and-fix` |
| PR Workflow | true |
| Goals Agent | `cui-java-expert:java-goals-agent` |
| Plan Agent | `cui-java-expert:java-plan-agent` |

---

## Operation: configure

**Input**: `plan_id`

**References fields added** (via `planning:manage-references set`):

| Field | Value |
|-------|-------|
| `standards` | `["cui-java-expert:cui-java-core", "cui-java-expert:cui-javadoc", "cui-java-expert:cui-java-unit-testing"]` |
| `adrs` | `[]` |
| `interfaces` | `[]` |
| `dependencies` | `[]` |

**Config fields added** (via `planning:manage-config set`):

| Field | Value |
|-------|-------|
| `create_pr` | `true` |
| `verification_required` | `true` |
| `verification_command` | `/builder:builder-build-and-fix` |
| `branch_strategy` | `feature` |

---

## Operation: decompose

**Input**: `plan_id`

**Before delegation**, log:
```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase refine \
  --type progress \
  --summary "Delegating to java-goals-agent" \
  --detail "decomposing request into goals"
```

**Delegation**:
```
Task(cui-java-expert:java-goals-agent,
     plan_id={plan_id})
```

**After delegation**, log outcome:
```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase refine \
  --type outcome \
  --summary "java-goals-agent completed: {goal_count} goals created" \
  --detail "lessons_recorded={count}"
```

**Returns**: `{status, goal_ids[], lessons_recorded}`

The agent analyzes Java codebase, creates goals with:
- Class/interface design decisions
- Package placement rationale
- Dependencies (CDI, Spring, external libs)
- Module assignment (for multi-module projects)
- Integration points with existing code

---

## Operation: plan

**Input**: `plan_id`, `goal_id?` (optional for single-item mode)

**Before delegation**, log:
```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase refine \
  --type progress \
  --summary "Delegating to java-plan-agent" \
  --detail "goal_id={goal_id|batch}"
```

**Delegation**:
```
Task(cui-java-expert:java-plan-agent,
     plan_id={plan_id},
     goal_id={goal_id})  # omit for batch
```

**After delegation**, log outcome:
```bash
python3 .plan/execute-script.py planning:manage-log:manage-work-log add \
  --plan-id {plan_id} \
  --phase refine \
  --type outcome \
  --summary "java-plan-agent completed: {task_count} tasks created" \
  --detail "lessons_recorded={count}"
```

**Returns**: `{status, task_ids[], lessons_recorded}`

The agent creates tasks with Java-specific steps:
1. Create/modify implementation file at `{path}`
2. Add unit tests (load `cui-java-expert:cui-java-unit-testing`)
3. Add JavaDoc (load `cui-java-expert:cui-javadoc`)
4. Follow CUI patterns (load `cui-java-expert:cui-java-core`)
5. Verify `mvn test -pl {module}` passes
