---
name: verification
description: Proactive verification mode for detecting workarounds and issues before they happen
allowed-tools: Read, Skill
---

# Verification Skill

**EXECUTION MODE**: When this skill is loaded, you are in VERIFICATION MODE. This modifies your behavior for ALL subsequent operations to proactively detect issues.

## What This Skill Provides

- **Workaround Detection** - Catch when you're about to use alternative approaches instead of documented methods
- **Proactive Analysis** - Stop before issues occur, not after
- **Manual QA Mode** - Explicit verification for testing workflows

## Unique Capability: Workaround Detection

The error-handling skill (hook-based) can only detect errors **after** they occur. This verification skill detects when you're **about to** use a workaround - something hooks cannot do.

### Workaround Indicators

Before any of these actions, STOP and analyze:

| Trigger | Indicates |
|---------|-----------|
| "Let me try a different approach" | Method workaround |
| Using path different from documented | Path workaround |
| "This step is optional" (when not marked so) | Skip workaround |
| Using different tool than specified | Substitution workaround |
| Implementing inline what script should do | Method workaround |
| Hardcoding value that should be resolved | Path workaround |

## When to Activate This Skill

Load this skill when:
- **Testing new workflows** - Verifying skills, commands, or agents work correctly
- **Debugging issues** - Finding root causes proactively
- **Quality assurance** - Ensuring strict adherence to documented methods
- **Manual verification** - When you want explicit stops, not just hook-triggered ones

## Workflow

### Step 1: Acknowledge Verification Mode

When this skill is loaded, immediately acknowledge:

```
Verification Mode Active - Will stop on workarounds, failures, or resolution issues for analysis.
```

### Step 2: Execute with Vigilance

For each operation:
1. Check if you're about to use a workaround
2. Monitor for potential issues
3. Apply verification protocol if triggered

### Step 3: On Issue Detection

When verification protocol triggers:

1. **STOP** - Do not proceed
2. **Load Standard** - Read appropriate analysis standard from error-handling skill
3. **Analyze** - Apply structured analysis
4. **Present** - Show findings to user
5. **Wait** - Do not continue until user decides

### Step 4: Load Analysis Standards

Standards are maintained by the error-handling skill:

```
Read marketplace/bundles/cui-plugin-development-tools/skills/error-handling/standards/workaround-detection.md
Read marketplace/bundles/cui-plugin-development-tools/skills/error-handling/standards/failure-analysis.md
Read marketplace/bundles/cui-plugin-development-tools/skills/error-handling/standards/resolution-analysis.md
```

## Analysis Output Format

Use this structured format for all analyses:

```markdown
## [TYPE] Analysis Required

### Issue Detected
[Clear description of what triggered the stop]

### Context
- **Operation**: [What was being attempted]
- **Component**: [Which script/skill/command]
- **Expected**: [What should have happened]
- **Actual**: [What would happen if we proceeded]

### Root Cause Analysis
[Analysis of why this is happening]

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

## Relationship with Error-Handling Skill

| Aspect | Verification | Error-Handling |
|--------|-------------|----------------|
| **Trigger** | Proactive (LLM self-monitors) | Reactive (hook triggers) |
| **Activation** | Manual load | Automatic on error |
| **Workarounds** | ✓ Can detect | ✗ Cannot detect |
| **Nested agents** | ✗ Cannot see | ✓ Can see |
| **Standards** | References error-handling | Owns standards |

**Complementary Use**: Load both for maximum coverage:
- Error-handling catches errors in nested agents via hooks
- Verification catches workarounds before they happen

## Integration Pattern

Load alongside other skills for verified execution:

```
Skill: cui-plugin-development-tools:verification
Skill: planning:plan-refine
```

## Delegation to Error-Handling

When this skill detects an issue that would benefit from the error-handling skill's analysis:

```
Skill: cui-plugin-development-tools:error-handling
```

## Tool Access

- **Read**: Load analysis standards from error-handling skill
- **Skill**: Delegate to error-handling for structured analysis

## Quality Indicators

Verification mode is working correctly when:
- [ ] Workarounds are flagged before execution
- [ ] User is always asked before proceeding
- [ ] No silent alternative paths taken
- [ ] Analysis standards are loaded from error-handling
- [ ] Structured analysis is presented

## Deactivation

Verification mode remains active for the entire session once loaded.

To run without verification:
- Start a new session without loading this skill
- Or explicitly acknowledge: "Disable verification mode for this operation"
