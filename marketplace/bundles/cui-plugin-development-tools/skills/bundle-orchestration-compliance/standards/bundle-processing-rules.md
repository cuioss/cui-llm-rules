# Bundle Processing Rules

Core rules for sequential bundle-by-bundle processing in diagnose commands.

## Core Principle

**Bundle-by-bundle processing requires:**
- Complete ALL steps (analysis → reference validation → fixes → verification) for one bundle
- THEN proceed to the next bundle
- NEVER skip steps or jump to summary prematurely

## Rule 1: Sequential Processing

**Requirement:** Process bundles one at a time in sorted order.

**Sort order:**
1. `cui-plugin-development-tools` (always first)
2. All other bundles alphabetically by name

**Display:** `Processing {total_bundles} bundles in order: {bundle_list}`

**Violation:** Processing bundles in parallel or random order causes:
- Token overload (all analysis loaded at once)
- Lost context for later bundles
- Inability to apply fixes incrementally
- Invalid cross-bundle aggregation

## Rule 2: Complete Steps 5a-5j for Each Bundle

**Requirement:** ALL steps must be completed for current bundle before proceeding to next.

**Step sequence per bundle:**
- Step 5a: Analyze bundle components
- Step 5b: Validate references for bundle
- Step 5c: Aggregate results
- Step 5d: Display bundle summary
- Step 5e: Categorize issues (if any found)
- Step 5f: Handle reference issues (if any found)
- Step 5g: Apply safe fixes (if auto-fix enabled)
- Step 5h: Prompt for risky fixes (if any found)
- Step 5i: Verify fixes (if any applied)
- Step 5i-verification: Check git status (if any applied)
- Step 5j: Verify mandatory completion checklist

**Violation:** Skipping steps 5c-5j and jumping to Step 6 (summary) produces:
- Incomplete analysis (no aggregation)
- Unverified fixes (agents claim but don't apply)
- Missing user prompts (risky fixes not addressed)
- Invalid results

## Rule 3: All Components in Bundle

**Requirement:** Process ALL components in bundle, not partial subsets.

**Examples:**
- If bundle has 13 commands: Analyze ALL 13, validate references for ALL 13
- If bundle has 8 agents: Analyze ALL 8, not just 4

**Violation:** Processing only subset (e.g., 4 of 13 commands) means:
- Incomplete bundle analysis
- Missing issues in unprocessed components
- Invalid bundle quality scores
- Misleading statistics

## Rule 4: No Summary Until All Bundles Complete

**Requirement:** Only execute Step 6 (overall summary) after ALL bundles processed.

**Check before Step 6:**
- Have all bundles been processed? (not just first bundle)
- Has each bundle completed Steps 5a-5j? (not just 5a-5d)
- Are fix workflows complete? (not skipped)

**Violation:** Generating summary after only 1 of 8 bundles produces:
- Incomplete marketplace analysis
- Misleading aggregate statistics
- False impression of completion

## Explicit Stop Points

**STOP and complete current step if:**

1. **Before Step 5:** Analysis and reference validation not complete for ALL components in bundle
2. **Before Steps 5e-5i:** Analysis complete but fix workflow not started
3. **Before Step 5j:** Fixes applied but not verified with git status
4. **Before Step 6:** Not all bundles have completed Steps 5a-5j

**CONTINUE to next step only when:**
- Current step is 100% complete for entire bundle
- All verification checks pass
- Mandatory completion checklist verified (Step 5j)

## Bundle Completion Verification

**Before proceeding to next bundle, verify:**

```
Bundle: {bundle-name}
✓ Step 5a: {N} components analyzed (ALL, not subset)
✓ Step 5b: {N} components reference-validated (ALL, not subset)
✓ Step 5c: Results aggregated
✓ Step 5d: Bundle summary displayed
✓ Steps 5e-5i: Fix workflow complete (or skipped if no issues)
✓ Step 5i-verification: Git status verified (or skipped if no fixes)
✓ Step 5j: Mandatory completion checklist checked
```

**If ANY item above is incomplete: STOP and complete it.**

## Error Recovery

**If bundle processing fails mid-workflow:**

1. **Identify failure point:** Which step failed?
2. **Attempt recovery:** Can the step be retried?
3. **If unrecoverable:** Mark bundle as incomplete, note in statistics
4. **Decision:** Continue to next bundle or abort entire workflow?

**Never:** Silently skip failed bundle and proceed without noting failure.

## Efficiency Considerations

**Within-bundle parallelization (ALLOWED):**
- Analyze all components in parallel (single message, multiple Task calls)
- Validate all references in parallel (single message, multiple Task calls)

**Across-bundle parallelization (PROHIBITED):**
- Do NOT start bundle 2 before bundle 1 completes Steps 5a-5j
- Do NOT analyze multiple bundles simultaneously

## Quality Standards

- Bundle processing must be deterministic (same order every time)
- Stop points must be explicit and unambiguous
- Verification must use observable evidence
- Statistics must track per-bundle and cross-bundle metrics
- Summary must only execute after all bundles complete

## Integration Pattern

```markdown
### Step 5: Process Each Bundle Sequentially

**CRITICAL**: Complete ALL steps (5a-5j) for one bundle before moving to the next.

**⚠️ MANDATORY COMPLETION CHECK**: You MUST NOT skip Steps 5c-5j. Jumping directly to Step 6 (summary) without completing the fix workflow produces incomplete, invalid results.

[Reference bundle-processing-rules from bundle-orchestration-compliance skill]

**For EACH bundle in sorted order:**
  [Steps 5a-5j here]

**Only after ALL steps complete: Proceed to next bundle**
```

## Related Standards

- `mandatory-completion-checklist.md` - Checklist to verify before next bundle
- `anti-skip-protections.md` - Warnings against skipping steps
- `post-fix-verification.md` - Git status verification after fixes
