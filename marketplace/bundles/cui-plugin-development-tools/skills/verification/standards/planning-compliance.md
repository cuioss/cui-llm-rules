# Planning Compliance Standard

Enforces proper access patterns and audit trail verification for planning-related commands and skills.

## Overview

Planning operations MUST use the official manage-* APIs for all .plan directory access. Direct file manipulation bypasses validation, audit trails, and can corrupt plan state. This standard detects violations and ensures proper audit trail population.

## Core Principles

1. **Abstraction Enforcement** - All .plan access goes through manage-* scripts
2. **Audit Trail Integrity** - Every operation records to work-log
3. **State Consistency** - Status reflects actual phase and progress
4. **No Silent Mutations** - All changes are tracked and verifiable

## Compliance Rules

### Rule 0: Allowed .plan Access

Some `.plan` files are designed for direct access:

| File | Access | Purpose |
|------|--------|---------|
| `.plan/execute-script.py` | Execute | Universal script executor with embedded mappings |
| `.plan/execution_log.py` | Import | Execution logging module |
| `.plan/marshall-state.toon` | Read/Write | Executor generation metadata |
| `.plan/logs/script-execution-*.log` | Append | Global execution logs |
| `.plan/lessons-learned/*.md` | Read/Write | Lessons learned via manage-lessons skill |

These are NOT violations and should not trigger compliance alerts.

**Approved Script Execution Pattern**:

All marketplace scripts should be executed via the executor:

```bash
python3 .plan/execute-script.py {notation} {subcommand} {args...}
```

Examples:
- `python3 .plan/execute-script.py planning:manage-files add --plan-id my-plan`
- `python3 .plan/execute-script.py builder:builder-maven-rules execute --goals verify`

**Violation** (after executor migration complete):
- Direct script execution: `python3 /path/to/script.py {args}` (bypasses logging and standardization)

### Rule 1: No Direct .plan/plans/** Access

**Prohibited Operations** (plan data must use manage-* API):

| Tool | Prohibited Pattern | Correct Alternative |
|------|-------------------|---------------------|
| Read | `.plan/plans/{id}/status.toon` | `manage-lifecycle.py read --plan-id {id}` |
| Read | `.plan/plans/{id}/config.toon` | `manage-config.py read --plan-id {id}` |
| Read | `.plan/plans/{id}/work-log.toon` | `manage-work-log.py list --plan-id {id}` |
| Read | `.plan/plans/{id}/requirements/REQ-*.toon` | `manage-requirement.py read --plan-id {id} --id REQ-001` |
| Read | `.plan/plans/{id}/specifications/SPEC-*.toon` | `manage-specification.py read --plan-id {id} --id SPEC-001` |
| Read | `.plan/plans/{id}/tasks/TASK-*.toon` | `manage-task.py read --plan-id {id} --id TASK-001` |
| Write | `.plan/plans/{id}/*` | Use appropriate manage-* create/update |
| Edit | `.plan/plans/{id}/*` | Use appropriate manage-* update |
| Glob | `.plan/plans/**/*.toon` | Use manage-* list operations |
| Glob | `.plan/plans/{id}/requirements/*` | `manage-requirement.py list --plan-id {id}` |
| Glob | `.plan/plans/{id}/specifications/*` | `manage-specification.py list --plan-id {id}` |
| Glob | `.plan/plans/{id}/tasks/*` | `manage-task.py list --plan-id {id}` |
| Bash find | `find .plan/plans -name "*.toon"` | Use manage-* list operations |
| Bash ls | `ls .plan/plans/{id}/tasks/` | `manage-task.py list --plan-id {id}` |

**No Exceptions**: All .plan file access must go through manage-* scripts. The following scripts provide complete coverage:

| File | Read Script | Write Script |
|------|-------------|--------------|
| `task.md` | `manage-files.py read --plan-id {id} --file task.md` | `manage-files.py write --plan-id {id} --file task.md` |
| `lessons-learned/*.md` | `manage-lesson.py get --id {lesson_id}` | `manage-lesson.py add` |
| Any plan file | `manage-files.py read --plan-id {id} --file {path}` | `manage-files.py write --plan-id {id} --file {path}` |

**Detection Pattern**:

When you observe tool calls that directly access .plan structure files:

```
## PLANNING COMPLIANCE Violation Detected

### Issue Detected
Direct .plan file access bypassing manage-* API

### Context
- **Operation**: [Read/Write/Edit/Glob]
- **Target**: [.plan/plans/{id}/status.toon]
- **Expected**: Use manage-lifecycle.py read
- **Actual**: Direct file read attempted

### Root Cause Analysis
Calling code is accessing .plan files directly instead of using the
manage-* abstraction layer. This bypasses:
- Input validation
- Audit trail logging
- Format consistency checks
- Atomic write guarantees

### Impact Assessment
| Aspect | Impact |
|--------|--------|
| Blocking | No - but should not proceed |
| Data Loss Risk | Yes - no atomic writes |
| Audit Trail | Broken - no work-log entry |
| State Corruption | Possible - no validation |

### Options
1. **Use manage-* API**: Replace direct access with appropriate script
2. **Investigate why**: Determine if manage-* is missing functionality
3. **Document exception**: If truly needed, document why direct access required

### Recommendation
Use manage-* API - this is a design violation, not a missing feature case
```

### Rule 2: Work-Log Population Verification

After any planning operation completes, verify work-log contains appropriate entry.

**Required Work-Log Entries**:

| Operation | Required Entry Type | Required Fields |
|-----------|-------------------|-----------------|
| Phase transition | `progress` | phase, summary |
| Decision made | `decision` | phase, summary, detail (rationale) |
| Artifact created | `artifact` | phase, summary (artifact type and id) |
| Task completed | `outcome` | phase, summary |
| Error occurred | `error` | phase, summary, detail (error info) |

**Verification Steps**:

1. After operation completes, query work-log:
   ```bash
   python3 .plan/execute-script.py planning:manage-log:list --plan-id {plan_id} --limit 5
   ```

2. Verify most recent entry matches operation:
   - Timestamp is within last few seconds
   - Type matches operation category
   - Phase matches current phase
   - Summary describes what happened

**Verification Template**:

```
## POST-OPERATION Audit Verification

### Operation Completed
[Description of what was just executed]

### Work-Log Check
```toon
[Output from manage-work-log.py list]
```

### Verification Result
| Check | Status | Notes |
|-------|--------|-------|
| Entry exists | Pass/Fail | [Details] |
| Correct type | Pass/Fail | Expected: {type}, Found: {type} |
| Correct phase | Pass/Fail | Expected: {phase}, Found: {phase} |
| Meaningful summary | Pass/Fail | [Assessment] |

### Assessment
[PASS/FAIL with explanation]
```

### Rule 3: Status Consistency Verification

After phase transitions or progress updates, verify status reflects correct state.

**Status Verification Points**:

| Trigger | What to Verify |
|---------|---------------|
| Phase transition | `current_phase` updated, previous phase marked `done` |
| Task completion | Phase progress reflects completed tasks |
| Error state | Status shows `error` or `blocked` if applicable |
| Plan completion | All phases marked `done` |

**Verification Steps**:

1. After phase-affecting operation, query status:
   ```bash
   python3 .plan/execute-script.py planning:manage-lifecycle:read --plan-id {plan_id}
   ```

2. Verify status consistency:
   - `current_phase` matches expected phase
   - Phases array shows correct `status` for each phase
   - `updated` timestamp is recent

**Verification Template**:

```
## STATUS Consistency Check

### Expected State
- Current phase: {phase}
- Previous phases: {list of done phases}
- Phase status: {expected statuses}

### Actual State
```toon
[Output from manage-lifecycle.py read]
```

### Consistency Check
| Field | Expected | Actual | Status |
|-------|----------|--------|--------|
| current_phase | {phase} | {actual} | Pass/Fail |
| phases[init] | done | {actual} | Pass/Fail |
| phases[refine] | done | {actual} | Pass/Fail |
| phases[execute] | in_progress | {actual} | Pass/Fail |
| updated | recent | {timestamp} | Pass/Fail |

### Assessment
[PASS/FAIL with explanation]
```

## Automated Verification Checklist

After each planning command/skill execution, verify:

- [ ] No direct .plan file access (except task.md read)
- [ ] Work-log entry added for significant operations
- [ ] Status reflects current phase correctly
- [ ] All artifacts created via manage-* scripts
- [ ] No orphaned files in .plan structure

## Integration with Commands

### plan-manage Command

When `/plan-manage` executes, verify after each action:

| Action | Expected Work-Log Entry | Expected Status Change |
|--------|------------------------|----------------------|
| `init` | type=artifact, summary=plan created | phases[init]=in_progress |
| configure complete | type=progress, summary=configuration complete | phases[init]=done, current_phase=refine |
| `refine` | type=artifact per REQ/SPEC/TASK created | phases[refine] progress updates |
| refine complete | type=outcome, summary=refine complete | phases[refine]=done, current_phase=execute |

### plan-execute Command

When `/plan-execute` executes, verify after each task:

| Event | Expected Work-Log Entry | Expected Status Change |
|-------|------------------------|----------------------|
| Task started | type=progress, summary=task title | task status=in_progress |
| Step completed | type=progress, summary=step description | step marked complete |
| Task completed | type=outcome, summary=task completion | task status=done |
| Build verified | type=outcome, summary=verification passed | - |
| Error occurred | type=error, detail=error info | may set blocked state |
| All tasks done | type=progress, summary=execute phase complete | current_phase=finalize |

## Common Violations

### Violation 1: Direct Status Read

```
Claude uses: Read .plan/plans/my-plan/status.toon
Should use: python3 .plan/execute-script.py planning:manage-lifecycle:read --plan-id my-plan
```

**Why It Matters**: Direct reads bypass the managed parser, may read stale data during atomic writes, and don't leverage script validation.

### Violation 2: Missing Work-Log Entry

```
Operation: Created SPEC-001 specification
Work-log: No entry found for artifact creation
```

**Why It Matters**: Audit trail is incomplete, making debugging and progress tracking impossible.

### Violation 3: Stale Status After Transition

```
Operation: Completed all execute phase tasks
Expected: current_phase=finalize
Actual: current_phase=execute (not updated)
```

**Why It Matters**: Phase routing will execute wrong phase, plan lifecycle is broken.

### Violation 4: Direct File Creation

```
Claude uses: Write .plan/plans/my-plan/tasks/TASK-003.toon
Should use: python3 .plan/execute-script.py planning:manage-tasks:create --plan-id my-plan --title "..."
```

**Why It Matters**: Bypasses numbering logic, validation, and work-log entry creation.

## Exception Handling

Some operations legitimately need direct access:

### Legitimate Exceptions

1. **Initial task.md creation** - plan-init creates this file directly
2. **Reading task.md** - reference document, read-only
3. **Lessons learned** - standalone markdown files
4. **Diagnostics/debugging** - when investigating issues with user approval

### Documenting Exceptions

When direct access is truly required, document it:

```
## EXCEPTION: Direct .plan Access

### Justification
[Why manage-* cannot be used]

### Risk Mitigation
[How data integrity is preserved]

### Scope
[Exactly which files and operations]

User approval obtained: [Yes/No]
```

## Post-Run Verification Script

Use this verification pattern after major operations:

```bash
# Verify work-log has recent entry
python3 .plan/execute-script.py planning:manage-log:list --plan-id {plan_id} --limit 1

# Verify status is consistent
python3 .plan/execute-script.py planning:manage-lifecycle:read --plan-id {plan_id}

# Verify no orphaned files (optional)
python3 .plan/execute-script.py planning:manage-files:list --plan-id {plan_id}
```

Expected output should show:
- Work-log entry within last few seconds
- Status current_phase matches expected
- All files properly registered
