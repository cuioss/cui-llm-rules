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
python3 .plan/execute-script.py {notation} [subcommand] {args...}
```

Examples:
- `python3 .plan/execute-script.py planning:manage-files:manage-files add --plan-id my-plan`
- `python3 .plan/execute-script.py builder:builder-maven-rules:maven execute --goals verify`

**Violation** (after executor migration complete):
- Direct script execution: `python3 /path/to/script.py {args}` (bypasses logging and standardization)

### Rule 1: No Direct .plan/plans/** Access

**Prohibited Operations** (plan data must use manage-* API):

| Tool | Prohibited Pattern | Correct Alternative |
|------|-------------------|---------------------|
| Read | `.plan/plans/{id}/status.toon` | `python3 .plan/execute-script.py planning:manage-lifecycle:manage-lifecycle read --plan-id {id}` |
| Read | `.plan/plans/{id}/config.toon` | `python3 .plan/execute-script.py planning:manage-config:manage-config read --plan-id {id}` |
| Read | `.plan/plans/{id}/work-log.toon` | `python3 .plan/execute-script.py planning:manage-log:manage-work-log read --plan-id {id}` |
| Read | `.plan/plans/{id}/solution_outline.md` | `python3 .plan/execute-script.py planning:manage-solution-outline:manage-solution-outline read --plan-id {id}` |
| Read | `.plan/plans/{id}/tasks/TASK-*.toon` | `python3 .plan/execute-script.py planning:manage-tasks:manage-task get --plan-id {id} --number 1` |
| Write | `.plan/plans/{id}/*` | Use appropriate manage-* create/update via execute-script.py |
| Edit | `.plan/plans/{id}/*` | Use appropriate manage-* update via execute-script.py |
| Glob | `.plan/plans/**/*.toon` | Use manage-* list operations via execute-script.py |
| Glob | `.plan/plans/{id}/solution_outline.md` | `python3 .plan/execute-script.py planning:manage-solution-outline:manage-solution-outline read --plan-id {id}` |
| Glob | `.plan/plans/{id}/tasks/*` | `python3 .plan/execute-script.py planning:manage-tasks:manage-task list --plan-id {id}` |
| Bash find | `find .plan/plans -name "*.toon"` | Use manage-* list operations via execute-script.py |
| Bash ls | `ls .plan/plans/{id}/tasks/` | `python3 .plan/execute-script.py planning:manage-tasks:manage-task list --plan-id {id}` |

**No Exceptions**: All .plan file access must go through manage-* scripts. The following scripts provide complete coverage:

| File | Read Script | Write Script |
|------|-------------|--------------|
| `request.md` | `planning:manage-plan-documents:manage-plan-document request read --plan-id {id}` | `planning:manage-plan-documents:manage-plan-document request create --plan-id {id} --title ... --source ... --body ...` |
| `solution_outline.md` | `planning:manage-solution-outline:manage-solution-outline read --plan-id {id}` | `planning:manage-solution-outline:manage-solution-outline write --plan-id {id} <<'EOF'` then validate |
| `lessons-learned/*.md` | `planning:manage-lessons:manage-lesson get --id {lesson_id}` | `planning:manage-lessons:manage-lesson add` |
| Any plan file | `planning:manage-files:manage-files read --plan-id {id} --file {path}` | `planning:manage-files:manage-files write --plan-id {id} --file {path}` |

**Detection Pattern**:

When you observe tool calls that directly access .plan structure files:

```
## PLANNING COMPLIANCE Violation Detected

### Issue Detected
Direct .plan file access bypassing manage-* API

### Context
- **Operation**: [Read/Write/Edit/Glob]
- **Target**: [.plan/plans/{id}/status.toon]
- **Expected**: Use `python3 .plan/execute-script.py planning:manage-lifecycle:manage-lifecycle read`
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
   python3 .plan/execute-script.py planning:manage-log:manage-work-log read --plan-id {plan_id}
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

### Rule 4: Script Execution via Executor (Mandatory)

All marketplace script execution MUST use the universal executor pattern.

**Required Pattern**:
```bash
python3 .plan/execute-script.py {notation} {subcommand} {args...}
```

**Notation Format**: `{bundle}:{skill}:{script}` (e.g., `planning:manage-files:manage-files`)

**CRITICAL - Singular vs Plural Script Names**:

| Skill Name (plural) | Script Name (SINGULAR) | Full Notation |
|---------------------|------------------------|---------------|
| `manage-plan-documents` | `manage-plan-document` | `planning:manage-plan-documents:manage-plan-document` |
| `manage-tasks` | `manage-task` | `planning:manage-tasks:manage-task` |
| `manage-lessons` | `manage-lesson` | `planning:manage-lessons:manage-lesson` |
| `manage-lifecycle` | `manage-lifecycle` | `planning:manage-lifecycle:manage-lifecycle` |
| `manage-config` | `manage-config` | `planning:manage-config:manage-config` |
| `manage-files` | `manage-files` | `planning:manage-files:manage-files` |
| `manage-log` | `manage-work-log` | `planning:manage-log:manage-work-log` |

**Prohibited Operations** (direct script paths must use executor):

| Tool | Prohibited Pattern | Correct Alternative |
|------|-------------------|---------------------|
| Bash | `python3 {script_path} {verb}` | `python3 .plan/execute-script.py {notation} {verb}` |
| Bash | `python3 marketplace/.../script.py` | `python3 .plan/execute-script.py {notation}` |
| Bash | `python3 {bundle}/scripts/foo.py` | `python3 .plan/execute-script.py {bundle}:{skill}` |

**Why This Matters**:
- **Execution logging**: All invocations are logged with timestamps and duration
- **Notation consistency**: Single canonical way to reference scripts
- **Error standardization**: Consistent error output format
- **Cross-cutting features**: Enables future metrics, caching, etc.

**Detection Pattern**:

When you observe tool calls that directly execute scripts:

```
## PLANNING COMPLIANCE Violation Detected

### Issue Detected
Direct script execution bypassing execute-script.py

### Context
- **Operation**: Bash
- **Target**: `python3 {path}/manage-files.py add --plan-id my-plan`
- **Expected**: `python3 .plan/execute-script.py planning:manage-files:manage-files add --plan-id my-plan`
- **Actual**: Direct script path used

### Root Cause Analysis
Calling code is executing scripts directly instead of using the
execute-script.py proxy. This bypasses:
- Execution logging
- Notation consistency
- Error standardization
- Cross-cutting features

### Options
1. **Use executor**: Replace direct path with executor notation
2. **Update caller**: Fix the SKILL.md/agent/command documentation

### Recommendation
Use executor pattern - this is a design violation
```

### Rule 5: Log File Verification and Issue Detection

Plan-related log files must exist, be properly formatted, remain consistent, and be actively scanned to detect script execution issues.

**Log File Types**:

| File | Location | Purpose |
|------|----------|---------|
| `work-log.toon` | `.plan/plans/{id}/work-log.toon` | Semantic work entries (decisions, artifacts, progress) |
| `execution.log` | `.plan/plans/{id}/execution.log` | Script execution records for plan-scoped operations |
| `script-execution-*.log` | `.plan/logs/script-execution-{date}.log` | Global execution records (non-plan operations) |

**Log Entry Format** (execution.log):

Success entry (single line):
```
{timestamp}\t{notation}\t{subcommand}\t{exit_code}\t{duration}s
```

Error entry (multi-line):
```
{timestamp}\t{notation}\t{subcommand}\t{exit_code}\t{duration}s\tERROR
  args: {full argument list}
  stdout: {truncated stdout}
  stderr: {truncated stderr}
```

**Verification Checks**:

| Check | What to Verify | When |
|-------|---------------|------|
| Existence | `work-log.toon` exists for every active plan | After plan creation |
| Existence | `execution.log` exists after first plan-scoped script call | After executor runs with `--plan-id` |
| Format | `work-log.toon` follows TOON format with entries table | After any log operation |
| Format | `execution.log` uses TSV format with required columns | After executor runs |
| Consistency | Work-log entries match expected operations | After phase transitions |
| Consistency | Execution.log records match script calls | After any executor call |

**Issue Detection via Log Scanning**:

Actively scan execution logs to detect script issues:

| Issue Type | Detection Pattern | Severity | Action |
|------------|-------------------|----------|--------|
| Script failure | Lines containing `\tERROR` | High | Investigate stderr, fix root cause |
| Repeated failures | Same notation with exit_code != 0 multiple times | Critical | Script is broken, needs immediate fix |
| Slow execution | Duration > 30s for simple operations | Medium | Optimize script or investigate hang |
| Missing executions | Expected script calls not in log | High | Executor not used (compliance violation) |
| Argument errors | stderr contains "usage:" or "argument" | Medium | Caller using wrong arguments |
| Import/module errors | stderr contains "ModuleNotFoundError" or "ImportError" | Critical | Missing dependency or path issue |
| Permission errors | stderr contains "Permission denied" | High | File/directory access issue |

**Log Scanning Commands**:

1. Find all errors in plan execution log:
   ```bash
   grep -E '\tERROR$' .plan/plans/{plan_id}/execution.log
   ```

2. Find repeated failures (same script failing):
   ```bash
   grep -E '\tERROR$' .plan/plans/{plan_id}/execution.log | cut -f2 | sort | uniq -c | sort -rn
   ```

3. Find slow executions (>10s):
   ```bash
   awk -F'\t' '$5+0 > 10 {print}' .plan/plans/{plan_id}/execution.log
   ```

4. Get full error context (multi-line entries):
   ```bash
   grep -A3 '\tERROR$' .plan/plans/{plan_id}/execution.log
   ```

5. Scan global logs for today's issues:
   ```bash
   grep -E '\tERROR$' .plan/logs/script-execution-$(date +%Y-%m-%d).log
   ```

**Verification Steps**:

1. Check work-log exists and has entries:
   ```bash
   python3 .plan/execute-script.py planning:manage-log:manage-work-log read --plan-id {plan_id}
   ```

2. Check execution.log exists and scan for issues:
   ```bash
   # Check recent entries
   tail -10 .plan/plans/{plan_id}/execution.log

   # Scan for errors
   grep -c '\tERROR$' .plan/plans/{plan_id}/execution.log || echo "0 errors"
   ```

3. Verify format compliance:
   - Work-log: Has header comments, entries table with 5 columns
   - Execution.log: TSV with timestamp, notation, subcommand, exit_code, duration

**Detection Pattern for Log Issues**:

```
## PLANNING COMPLIANCE Violation Detected

### Issue Detected
[Log file integrity issue / Script execution failure detected]

### Context
- **Check Type**: [existence/format/consistency/script-failure]
- **File**: [path to log file]
- **Expected**: [what should exist or match]
- **Actual**: [what was found]

### Log Scan Results (if script failure)
| Metric | Value |
|--------|-------|
| Total executions | {count} |
| Failed executions | {error_count} |
| Unique failing scripts | {list} |
| Most recent error | {timestamp} |

### Error Details
```
{stderr content from log}
```

### Root Cause Analysis
[Explanation of why this matters for audit trail integrity or script health]

### Impact Assessment
| Aspect | Impact |
|--------|--------|
| Audit Trail | Incomplete or corrupted |
| Debugging | Missing operation history |
| Compliance | Cannot verify operations occurred |
| Script Health | [Broken/Degraded/Healthy] |

### Options
1. **Fix script**: Address the error shown in stderr
2. **Regenerate entries**: Use manage-log to add missing entries
3. **Investigate cause**: Determine why log was not updated
4. **Manual recovery**: Reconstruct from other sources if possible

### Recommendation
[Specific action based on violation type]
```

**Common Log Violations and Script Issues**:

| Violation | Symptom | Cause |
|-----------|---------|-------|
| Missing work-log | `manage-log:list` returns error | Plan created without init entry |
| Empty work-log | No entries after operations | Operations bypassed logging |
| Stale execution.log | Old timestamps only | Executor not used for recent calls |
| Format corruption | Parse errors | Direct file edit instead of API |
| Script failure | ERROR entries in log | Bug in script or invalid arguments |
| Repeated failures | Same script failing multiple times | Systemic issue needs investigation |
| Import errors | ModuleNotFoundError in stderr | Missing dependency or wrong Python path |
| Timeout patterns | Very long durations (>60s) | Script hanging or performance issue |

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
   python3 .plan/execute-script.py planning:manage-lifecycle:manage-lifecycle read --plan-id {plan_id}
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
[Output from planning:manage-lifecycle:manage-lifecycle read]
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

- [ ] No direct .plan file access (except request.md read)
- [ ] Work-log entry added for significant operations
- [ ] Status reflects current phase correctly
- [ ] All artifacts created via manage-* scripts
- [ ] No orphaned files in .plan structure
- [ ] Log files exist and are properly formatted (work-log.toon, execution.log)
- [ ] Execution.log contains recent entries for script calls
- [ ] Execution.log scanned for ERROR entries - none found or issues addressed
- [ ] No repeated script failures detected in logs

## Integration with Commands

### plan-manage Command

When `/plan-manage` executes, verify after each action:

| Action | Expected Work-Log Entry | Expected Status Change |
|--------|------------------------|----------------------|
| `init` | type=artifact, summary=plan created | phases[init]=in_progress |
| configure complete | type=progress, summary=configuration complete | phases[init]=done, current_phase=refine |
| `refine` | type=artifact per GOAL/TASK created | phases[refine] progress updates |
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
Should use: python3 .plan/execute-script.py planning:manage-lifecycle:manage-lifecycle read --plan-id my-plan
```

**Note**: Script notation is `planning:manage-lifecycle:manage-lifecycle` (skill name matches script name).

**Why It Matters**: Direct reads bypass the managed parser, may read stale data during atomic writes, and don't leverage script validation.

### Violation 2: Missing Work-Log Entry

```
Operation: Created solution_outline.md with 3 goals
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
Should use: python3 .plan/execute-script.py planning:manage-tasks:manage-task add --plan-id my-plan --title "..." --goal 1 --description "..." --steps "A" "B"
```

**Note**: Script notation uses SINGULAR `manage-task` (not `manage-tasks`). Full notation: `planning:manage-tasks:manage-task`.

**Why It Matters**: Bypasses numbering logic, validation, and work-log entry creation.

## Exception Handling

Some operations legitimately need direct access:

### Legitimate Exceptions

1. **Lessons learned** - standalone markdown files accessed via manage-lessons skill
2. **Diagnostics/debugging** - when investigating issues with user approval

**Note**: `request.md` and `solution_outline.md` are now managed via `planning:manage-plan-documents` skill.

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
python3 .plan/execute-script.py planning:manage-log:manage-work-log read --plan-id {plan_id}

# Verify status is consistent
python3 .plan/execute-script.py planning:manage-lifecycle:manage-lifecycle read --plan-id {plan_id}

# Verify no orphaned files (optional)
python3 .plan/execute-script.py planning:manage-files:manage-files list --plan-id {plan_id}
```

Expected output should show:
- Work-log entry within last few seconds
- Status current_phase matches expected
- All files properly registered

## Post-Run Verification: Executor Pattern

After script operations complete, verify proper executor usage:

**For plan-scoped operations** (when `--plan-id` was provided):
```bash
# Verify execution logged to plan
tail -5 .plan/plans/{plan-id}/execution.log
```

**For global operations** (no plan context):
```bash
# Verify execution logged to daily global log
tail -5 .plan/logs/script-execution-$(date +%Y-%m-%d).log
```

**Success entry format** (compact):
```
{timestamp}	{notation}	{subcommand}	0	{duration}
```

**Error entry format** (detailed):
```
{timestamp}	{notation}	{subcommand}	{exit_code}	{duration}	ERROR
  args: {full argument list}
  stderr: {error message}
```

Expected verification:
- Timestamp is recent (within last few seconds)
- Notation matches expected script
- Exit code is 0 for success
- For errors: args and stderr provide debugging context
