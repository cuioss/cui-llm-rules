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

## Script Path Resolution

**MANDATORY**: Before executing any script, resolve paths via script-runner.

```
Skill: general-tools:script-runner
Resolve: planning:manage-log/scripts/manage-work-log.py
Resolve: planning:manage-config/scripts/manage-config.py
Resolve: planning:manage-references/scripts/manage-references.py
```

Use the resolved absolute paths in all Bash commands.

---

## Characteristics

| Aspect | Value |
|--------|-------|
| Technology | java |
| Verification | `/builder:builder-build-and-fix` |
| PR Workflow | true |
| Specify Agent | `cui-java-expert:java-specify-agent` |
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

## Operation: specify

**Input**: `plan_id`, `requirement_id?` (optional for single-item mode)

**Before delegation**, log:
```bash
python3 {resolved_manage_work_log} add \
  --plan-id {plan_id} \
  --phase refine \
  --type progress \
  --summary "Delegating to java-specify-agent" \
  --detail "requirement_id={requirement_id|batch}"
```

**Delegation**:
```
Task(cui-java-expert:java-specify-agent,
     plan_id={plan_id},
     requirement_id={requirement_id})  # omit for batch
```

**After delegation**, log outcome:
```bash
python3 {resolved_manage_work_log} add \
  --plan-id {plan_id} \
  --phase refine \
  --type outcome \
  --summary "java-specify-agent completed: {spec_count} specs created" \
  --detail "lessons_recorded={count}"
```

**Returns**: `{status, spec_ids[], lessons_recorded}`

The agent analyzes Java codebase, creates specifications with:
- Class/interface design decisions
- Package placement rationale
- Dependencies (CDI, Spring, external libs)
- Module assignment (for multi-module projects)
- Integration points with existing code

---

## Operation: plan

**Input**: `plan_id`, `specification_id?` (optional for single-item mode)

**Before delegation**, log:
```bash
python3 {resolved_manage_work_log} add \
  --plan-id {plan_id} \
  --phase refine \
  --type progress \
  --summary "Delegating to java-plan-agent" \
  --detail "specification_id={specification_id|batch}"
```

**Delegation**:
```
Task(cui-java-expert:java-plan-agent,
     plan_id={plan_id},
     specification_id={specification_id})  # omit for batch
```

**After delegation**, log outcome:
```bash
python3 {resolved_manage_work_log} add \
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
