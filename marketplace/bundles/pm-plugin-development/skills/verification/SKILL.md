---
name: verification
description: Verification mode that stops and analyzes on failures, workarounds, or resolution issues
allowed-tools: Read
---

# Verification Skill

**EXECUTION MODE**: When this skill is loaded, you are in VERIFICATION MODE. This modifies your behavior for ALL subsequent operations. You MUST follow the verification protocols below.

Verification mode ensures quality by stopping execution on any failure, workaround, or resolution issue to perform root cause analysis before proceeding.

## What This Skill Provides

- **Failure Detection** - Stop on script failures, tool errors, or unexpected outputs
- **Resolution Analysis** - Stop when resolving paths, references, or dependencies fails
- **Workaround Detection** - Stop when using alternative approaches instead of intended methods
- **Root Cause Analysis** - Structured analysis of what failed and why
- **User Presentation** - Clear presentation of findings before proceeding

## When to Activate This Skill

Activate this skill when:
- **Testing new workflows** - Verifying skills, commands, or agents work correctly
- **Debugging issues** - Finding root causes of failures
- **Quality assurance** - Ensuring scripts and tools function as documented
- **Integration testing** - Verifying component interactions

## Activation Scopes

The skill supports different verification scopes via the `scope` parameter:

### Base Verification (default)

```
Skill: pm-plugin-development:verification
```

Applies: Script failures, resolution failures, workaround detection

### Planning Verification

```
Skill: pm-plugin-development:verification
scope: planning
```

Applies: All base checks PLUS:
- No direct .plan file access (must use manage-* scripts)
- Work-log population after each operation
- Status consistency after phase transitions

Use this scope when testing `/plan-manage`, `/plan-execute`, or any planning-related skills.

## Verification Mode Behavior

**CRITICAL**: When this skill is loaded, you MUST modify your behavior as follows:

### On Script Failure

When any script returns non-zero exit code or produces error output:

1. **STOP** - Do not continue with the workflow
2. **ANALYZE** - Perform failure analysis (see standards/failure-analysis.md)
3. **PRESENT** - Show analysis to user with structured format
4. **WAIT** - Ask user how to proceed before continuing

### On Resolution Failure

When resolving paths, skill references, or dependencies fails:

1. **STOP** - Do not use fallback or alternative paths
2. **ANALYZE** - Perform resolution analysis (see standards/resolution-analysis.md)
3. **PRESENT** - Show what failed to resolve and why
4. **WAIT** - Ask user for guidance before proceeding

### On Workaround Usage

When you would use an alternative approach instead of the documented method:

1. **STOP** - Do not silently use the workaround
2. **DETECT** - Recognize you are about to use a workaround
3. **ANALYZE** - Explain why the intended method failed
4. **PRESENT** - Show both intended method and workaround
5. **WAIT** - Ask user to approve workaround or fix the issue

## Analysis Output Format

All analyses MUST use this structured format:

```
## [TYPE] Analysis Required

### Issue Detected
[Clear description of what triggered the stop]

### Context
- **Operation**: [What was being attempted]
- **Component**: [Which script/skill/command]
- **Expected**: [What should have happened]
- **Actual**: [What actually happened]

### Root Cause Analysis
[Analysis of why this occurred]

### Impact Assessment
| Aspect | Impact |
|--------|--------|
| Blocking | Yes/No |
| Data Loss Risk | Yes/No |
| Workaround Available | Yes/No |

### Options
1. [Option 1 with consequences]
2. [Option 2 with consequences]
3. [Option 3 with consequences]

### Recommendation
[Your recommended next step]

---
**Verification Mode Active** - Awaiting user decision before proceeding.
```

## Workflow

### Step 1: Acknowledge Verification Mode

When this skill is loaded, immediately acknowledge:

```
Verification Mode Active - All operations will stop on failures, resolution issues, or workarounds for analysis.
```

If `scope: planning` was specified, add:

```
Planning Scope Active - Additional checks: .plan access patterns, work-log population, status consistency.
```

### Step 2: Execute with Vigilance

For each operation:
1. Check if it's a script execution, resolution, or potential workaround
2. Monitor for failure conditions
3. Apply appropriate verification protocol if triggered

### Step 3: Analyze Failures

When verification protocol triggers:
1. Load appropriate analysis standard
2. Perform structured analysis
3. Format output per template
4. Present to user and wait

### Step 4: Resume After User Decision

Only after user provides direction:
1. Execute user's chosen option
2. Continue verification mode for subsequent operations
3. Track all verification stops in session

## Standards Organization

```
standards/
├── failure-analysis.md      (Script and tool failure analysis)
├── resolution-analysis.md   (Path and reference resolution issues)
├── workaround-detection.md  (Detecting and analyzing workarounds)
└── planning-compliance.md   (Planning command/skill access patterns)
```

## Verification Triggers

### Script Failures
- Non-zero exit code
- Error output (stderr)
- Unexpected output format
- Missing expected output
- Timeout conditions

### Resolution Failures
- Path not found
- Skill not found
- Reference not resolved
- Dependency missing
- Configuration missing

### Workaround Indicators
- Using alternative path
- Falling back to different method
- Skipping documented step
- Substituting different tool
- Manual intervention where automation expected

### Planning Compliance Violations (scope: planning only)

These checks apply ONLY when `scope: planning` is specified:

**Allowed `.plan` Access** (NOT violations):
- `.plan/scripts-library.toon` - Read for script path resolution (legacy)
- `.plan/execute-script.py` - Script executor with embedded mappings
- `.plan/execution_log.py` - Execution logging module
- `.plan/marshall-state.toon` - Executor generation metadata
- `.plan/logs/script-execution-*.log` - Global execution logs
- `.plan/lessons-learned/*.md` - Read/write via manage-lessons skill

**Approved Script Execution Pattern**:
```bash
python3 .plan/execute-script.py {notation} {subcommand} {args...}
```

This is the preferred pattern for all marketplace script execution.

**Prohibited `.plan/plans/**` Access** (violations):
- Direct Read/Write/Edit of `.plan/plans/*/status.toon`
- Direct Read/Write/Edit of `.plan/plans/*/config.toon`
- Direct Read/Write/Edit of `.plan/plans/*/work-log.toon`
- Direct access to goals/tasks directories
- Glob patterns targeting `.plan/plans/**/*.toon` or subdirectories
- Bash find/ls commands scanning `.plan/plans/` structure
- Missing work-log entry after significant operation
- Status not updated after phase transition
- Artifacts created without manage-* scripts

## Tool Access

**Read**: Load analysis standards on-demand

No other tools required - this skill modifies behavioral patterns.

## Integration Pattern

This skill is designed to be loaded alongside other skills:

```
Skill: pm-plugin-development:verification
Skill: pm-workflow:plan-refine
```

When both are loaded, verification mode applies to all plan-refine operations.

## Quality Indicators

Verification mode is working correctly when:
- [ ] All script failures produce structured analysis
- [ ] Resolution issues are caught before fallbacks
- [ ] Workarounds are flagged before execution
- [ ] User is always asked before proceeding
- [ ] No silent failures or alternative paths taken

## Example Session

```
User: Run the init phase for my-plan

Claude: Verification Mode Active - All operations will stop on failures, resolution issues, or workarounds for analysis.

Executing plan-init for my-plan...

## SCRIPT FAILURE Analysis Required

### Issue Detected
Script pm-workflow:manage-lifecycle:manage-lifecycle returned non-zero exit code (1)

### Context
- **Operation**: Create plan status
- **Component**: pm-workflow:manage-lifecycle
- **Expected**: status: success with plan created
- **Actual**: status: error with invalid_plan_type

### Root Cause Analysis
The plan_type "java" does not conform to bundle:skill notation.
Script expects format like "pm-workflow:plan-type-java" but received "java".

### Impact Assessment
| Aspect | Impact |
|--------|--------|
| Blocking | Yes |
| Data Loss Risk | No |
| Workaround Available | Yes |

### Options
1. Fix the calling code to use qualified plan_type
2. Manually run with correct plan_type
3. Update script to accept short names (not recommended)

### Recommendation
Fix option 1 - Update calling code to use "pm-workflow:plan-type-java"

---
**Verification Mode Active** - Awaiting user decision before proceeding.
```

## Planning-Specific Verification (scope: planning)

When `scope: planning` is specified, apply these additional checks for planning commands:

### Before Each Operation
1. Check if operation will access .plan files directly
2. Verify manage-* script is being used instead

### After Each Operation
1. Query work-log for recent entry matching operation
2. Query status for consistency with expected phase
3. Report any discrepancies

### Example Planning Violation

```
User: Continue executing the current plan

Claude: Verification Mode Active

Checking plan status...

## PLANNING COMPLIANCE Violation Detected

### Issue Detected
Direct .plan file access bypassing manage-* API

### Context
- **Operation**: Read
- **Target**: .plan/plans/jwt-auth/status.toon
- **Expected**: Use `python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle read --plan-id jwt-auth`
- **Actual**: Direct file read attempted

### Root Cause Analysis
Command is reading status.toon directly instead of using
`python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle read`.
This bypasses audit trail and validation.

### Impact Assessment
| Aspect | Impact |
|--------|--------|
| Blocking | No - but should not proceed |
| Data Loss Risk | No (read-only) |
| Audit Trail | Not broken but inconsistent pattern |
| Maintainability | Poor - mixed access patterns |

### Options
1. **Use pm-workflow:manage-lifecycle:manage-lifecycle**: Consistent abstraction layer
2. **Proceed with warning**: Log deviation but continue

### Recommendation
Use `python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle read` for all status access

---
**Verification Mode Active** - Awaiting user decision before proceeding.
```

### Example Post-Operation Audit

```
User: (approved using pm-workflow:manage-lifecycle:manage-lifecycle)

Claude: Task TASK-001 completed successfully.

## POST-OPERATION Audit Verification

### Operation Completed
Marked TASK-001 as complete, transitioned to TASK-002

### Work-Log Check
```toon
entries[1]{timestamp,type,phase,summary}:
2025-12-07T14:30:00Z,outcome,execute,Completed TASK-001: Implement JWT generator
```

### Status Check
```toon
current_phase: execute
phases[4]{name,status}:
init,done
refine,done
execute,in_progress
finalize,pending
```

### Verification Result
| Check | Status | Notes |
|-------|--------|-------|
| Work-log entry exists | Pass | Entry within last 5 seconds |
| Correct type | Pass | outcome matches task completion |
| Correct phase | Pass | execute phase |
| Meaningful summary | Pass | Describes completed task |
| Status consistent | Pass | execute phase in_progress |

### Assessment
PASS - All audit trail and status checks verified
```

## Deactivation

Verification mode remains active for the entire session once loaded.

To run without verification:
- Start a new session without loading this skill
- Or explicitly acknowledge: "Disable verification mode for this operation"
