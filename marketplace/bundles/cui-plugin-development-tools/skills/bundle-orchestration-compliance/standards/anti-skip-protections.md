# Anti-Skip Protections

Warnings and consequences displayed to prevent skipping critical workflow steps.

## Purpose

Prevents diagnose commands from skipping Steps 5c-5j (aggregation, summary, fix workflow, verification) and jumping directly to Step 6 (overall summary).

## The Problem

**Common failure mode:**
1. Complete Step 5a (analyze components) ✓
2. Complete Step 5b (validate references) ✓
3. Skip Steps 5c-5j (aggregate, fix, verify) ✗
4. Jump to Step 6 (summary) ✗

**Result:** Incomplete diagnosis with unverified fixes and invalid statistics.

## Protection 1: Mandatory Completion Check (Step 5 Header)

**Display at the start of Step 5:**

```markdown
### Step 5: Process Each Bundle Sequentially

**CRITICAL**: Complete ALL steps (5a-5j) for one bundle before moving to the next.

**⚠️ MANDATORY COMPLETION CHECK**: You MUST NOT skip Steps 5c-5j. Jumping directly to Step 6 (summary) without completing the fix workflow produces incomplete, invalid results.
```

**Purpose:** Sets expectation that ALL substeps are required.

## Protection 2: Reference Validation Completeness (Step 5b)

**Display during reference validation:**

```markdown
**Launch reference validation agents in parallel** (single message, multiple Task calls) for **ALL commands in current bundle**.

**⚠️ CRITICAL**: You MUST validate references for ALL commands in the bundle, not a partial subset. Validating only 4 of 13 commands violates the workflow.
```

**Purpose:** Prevents processing only partial subset of components.

**Example violation:** Bundle has 13 commands but only 4 are reference-validated.

## Protection 3: Fix Workflow Anti-Skip (Steps 5e-5i)

**Display before fix workflow:**

```markdown
**Steps 5e-5i: Apply Fix Workflow for Bundle ⚠️ FIX PHASE STARTS**

**⚠️ ANTI-SKIP PROTECTION**: Steps 5e-5i are MANDATORY if any issues were found. Skipping these steps means:
- Reference fixes claimed by agents are not verified
- Safe fixes are not applied
- Risky fixes are not prompted
- No verification that fixes actually worked
- Invalid/incomplete diagnosis results

**EXPLICIT STOP POINT**: If you have NOT completed Steps 5a-5d above, STOP and complete them first. Do not proceed to fix workflow until analysis and reference validation are complete for the entire bundle.
```

**Purpose:** Explains consequences of skipping and provides explicit stop point.

## Protection 4: Conditional Requirements

**For conditional steps, clarify when skipping is allowed:**

```markdown
**If any issues found in this bundle:**

Load and apply fix workflow from skill:
[...]

**If NO issues found:**
- Skip Steps 5e-5i (no fixes needed)
- Mark as N/A in completion checklist
- Proceed to Step 5j
```

**Purpose:** Distinguishes legitimate skipping (no issues) from violation (skipping despite issues).

## Consequences of Skipping

**Display these consequences in warnings:**

| Step Skipped | Consequence |
|--------------|-------------|
| 5c (Aggregate) | Bundle statistics missing, can't calculate quality scores |
| 5d (Summary) | No bundle report, can't track progress |
| 5e (Categorize) | Don't know which fixes are safe vs risky |
| 5f (Handle refs) | Reference fixes claimed but not verified |
| 5g (Safe fixes) | Safe fixes not applied despite auto-fix enabled |
| 5h (Risky fixes) | User not prompted, risky issues unaddressed |
| 5i (Verify) | Don't know if fixes worked or broke something |
| 5i-verification | Don't know if agents actually edited files |
| 5j (Checklist) | Proceed to next bundle with incomplete current bundle |

## Explicit Stop Points

**Use these phrases to indicate when to stop vs continue:**

**STOP indicators:**
```
"If you have NOT completed Steps 5a-5d above, STOP and complete them first."
"STOP. Complete that step before proceeding."
"Do NOT proceed to next bundle."
```

**CONTINUE indicators:**
```
"Only after ALL steps complete: Proceed to next bundle"
"If all items verified: Continue to next bundle"
"Once checklist complete: Return to Step 5 for next bundle"
```

## Integration Pattern

**In diagnose commands, add anti-skip protections at:**

1. **Step 5 header:** Mandatory completion check
2. **Step 5b:** Reference validation completeness
3. **Steps 5e-5i:** Fix workflow anti-skip + explicit stop point
4. **Step 5j:** Mandatory completion checklist

**Example integration:**

```markdown
### Step 5: Process Each Bundle Sequentially

[Mandatory completion check warning]

**For EACH bundle in sorted order:**

**Step 5a:** [Analysis]

**Step 5b:** [Reference validation]
[Reference validation completeness warning]

[...Steps 5c-5d...]

**Steps 5e-5i:** [Fix workflow]
[Anti-skip protection + explicit stop point]

**Step 5j:** [Completion checklist]
```

## Enforcement

**Commands MUST:**
1. Display warnings at designated points
2. Explain consequences of skipping
3. Provide explicit stop points
4. Distinguish legitimate skips from violations

**Commands MUST NOT:**
1. Allow skipping without warnings
2. Proceed past stop points
3. Skip verification steps silently
4. Assume steps are optional

## Quality Standards

- Warnings must be visible and clear
- Consequences must be specific and accurate
- Stop points must be unambiguous
- Conditional logic must be explicit
- Integration pattern must be consistent

## Related Standards

- `bundle-processing-rules.md` - Sequential processing requirements
- `mandatory-completion-checklist.md` - Checklist before next bundle
- `post-fix-verification.md` - Verification after fixes
