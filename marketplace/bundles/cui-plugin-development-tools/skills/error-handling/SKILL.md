---
name: error-handling
description: Error analysis and resolution skill activated by hooks when errors are detected
allowed-tools: Read, Skill
---

# Error Handling Skill

**EXECUTION MODE**: This skill is loaded when a hook detects an error. You MUST follow the workflow below to analyze the error and present options to the user.

Activated by the error-detector hook when errors are detected in tool output. Performs structured analysis and guides resolution.

## What This Skill Provides

- **Error Context Reading** - Parse error context from `.plan/error-context.toon`
- **Error Classification** - Categorize errors by type (resolution, script, validation)
- **Root Cause Analysis** - Apply appropriate analysis standard
- **User Presentation** - Present structured analysis with options
- **Resolution Logging** - Log error resolution to work-log

## When This Skill Is Activated

This skill is loaded when:
- A hook detects an error and instructs LLM to load it
- Error context is available in `.plan/error-context.toon`

Do NOT load this skill manually - it is meant to be triggered by the error-detector hook.

## Workflow

### Step 1: Acknowledge Activation

When this skill is loaded, immediately acknowledge:

```
Error Handling Mode Active - Reading error context and performing analysis.
```

### Step 2: Read Error Context

Read `.plan/error-context.toon` (TOON format) to understand:
- Which tool failed
- What patterns were matched
- What the raw output was
- When it happened

**TOON Format Reference**: See `Skill: general-tools:toon-usage` for parsing patterns.

```
Read .plan/error-context.toon
```

### Step 3: Classify Error

Based on the error context, classify the error type:

| Error Type | Pattern Indicators | Analysis Standard |
|------------|-------------------|-------------------|
| Resolution failure | "Unknown skill", "not found", "skill not found" | standards/resolution-analysis.md |
| Script failure | "exit code", "failed", "exception" | standards/failure-analysis.md |
| Validation failure | "status: error", "invalid" | standards/failure-analysis.md |

### Step 4: Load Analysis Standard

Based on classification, read appropriate standard from this skill's `standards/` directory:

For resolution failures:
```
Read marketplace/bundles/cui-plugin-development-tools/skills/error-handling/standards/resolution-analysis.md
```

For script/validation failures:
```
Read marketplace/bundles/cui-plugin-development-tools/skills/error-handling/standards/failure-analysis.md
```

### Step 5: Perform Analysis

Apply the analysis template from the loaded standard:

```markdown
## [TYPE] Analysis Required

### Issue Detected
[Clear description of what triggered the error]

### Context
- **Tool**: [Which tool produced the error]
- **Timestamp**: [When it occurred]
- **Operation**: [What was being attempted]
- **Patterns Matched**: [Error patterns detected]

### Root Cause Analysis
[Analysis of why this occurred based on raw output]

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
**Error Handling Mode Active** - Awaiting user decision before proceeding.
```

### Step 6: Present and Wait

Present the structured analysis to the user.

**CRITICAL**: Do NOT proceed with any other actions until the user provides direction.

### Step 7: Log Error After Resolution

After user makes a decision and the error is handled, log to work-log:

```
Skill: planning:manage-log
operation: add
type: error
phase: {current_phase if known, otherwise "unknown"}
summary: "{error_type}: {brief description}"
detail: "{resolution chosen by user}"
```

## Error Pattern Reference

### Resolution Failures

These indicate a component (skill, path, reference) could not be found:

- `Unknown skill` - Skill not registered or misspelled
- `skill not found` - Skill doesn't exist in bundle
- `not found` - Generic resource not found
- `Cannot find bundle` - Bundle doesn't exist

**Analysis Focus**: Trace the resolution chain to find where it fails.

### Script Failures

These indicate a script execution failed:

- `exit code [1-9]` - Non-zero exit code
- `failed` - Generic failure indicator
- `exception` - Python/runtime exception
- `error` - Generic error indicator

**Analysis Focus**: Examine script inputs, environment, and error messages.

### Validation Failures

These indicate input validation rejected the data:

- `status: error` - Structured error response
- `invalid` - Validation rule violation

**Analysis Focus**: Compare actual input against expected format.

## Standards Organization

This skill owns the analysis standards used for error investigation:

```
standards/
├── failure-analysis.md      # Script and tool failure analysis
├── resolution-analysis.md   # Path and reference resolution issues
└── workaround-detection.md  # Detecting and analyzing workarounds
```

These standards are also used by the verification skill for proactive analysis.

## Integration with Other Skills

### Verification Skill

The verification skill (`cui-plugin-development-tools:verification`) provides:
- Proactive behavioral mode for manual QA workflows
- Workaround detection (catching when LLM is about to use alternative approaches)
- Uses this skill's standards for analysis

The verification skill is complementary - it catches issues that hooks cannot detect (like workarounds before they happen).

### Manage-Log Skill

The manage-log skill (`planning:manage-log`) is used to:
- Record error occurrences
- Track resolution decisions
- Maintain audit trail

## Tool Access

- **Read**: Load error context and analysis standards
- **Skill**: Load manage-log for error logging

## Quality Indicators

Error handling is working correctly when:
- [ ] Error context is read from `.plan/error-context.toon`
- [ ] Error is classified by type
- [ ] Appropriate analysis standard is loaded
- [ ] Structured analysis is presented to user
- [ ] Execution stops until user decides
- [ ] Error is logged to work-log after resolution

## Example Session

```
Claude: Error Handling Mode Active - Reading error context and performing analysis.

Reading .plan/error-context.toon...

## RESOLUTION FAILURE Analysis Required

### Issue Detected
Skill reference failed to resolve: cui-plugin-development-tools:plan-type-plugin

### Context
- **Tool**: Task (planning:plan-refine-agent)
- **Timestamp**: 2024-12-06T15:30:00+01:00
- **Operation**: Loading plan-type skill for refine phase
- **Patterns Matched**: Unknown skill, not found

### Root Cause Analysis
The skill `plan-type-plugin` does not exist in the `cui-plugin-development-tools` bundle.
The plan configuration specifies an invalid plan_type that references a non-existent skill.

Checking bundle contents:
- marketplace/bundles/cui-plugin-development-tools/skills/ contains:
  - marketplace-inventory
  - plugin-architecture
  - plugin-create
  - plugin-doctor
  - plugin-maintain
  - plugin-specify
  - plugin-plan
  - verification
  - error-handling

No `plan-type-plugin` skill exists.

### Impact Assessment
| Aspect | Impact |
|--------|--------|
| Blocking | Yes |
| Data Loss Risk | No |
| Workaround Available | Yes |

### Options
1. **Fix plan configuration**: Update plan_type to use an existing skill
2. **Create missing skill**: Create plan-type-plugin skill (if intended)
3. **Use different workflow**: Bypass plan-type loading (may miss type-specific guidance)

### Recommendation
Option 1 - Fix the plan configuration to use a valid plan_type. The plan_type should reference an existing skill in format `bundle:skill-name`.

---
**Error Handling Mode Active** - Awaiting user decision before proceeding.
```

## Cleanup

After the error is resolved and logged:

1. The error context file `.plan/error-context.toon` may be left for debugging
2. Or cleaned up with: `rm .plan/error-context.toon`

This skill does not automatically clean up to preserve audit trail if needed.
