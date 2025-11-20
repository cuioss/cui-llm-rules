# Verification Patterns - Re-Run Analysis and Validation

Defines the patterns for verifying that fixes were applied correctly and didn't introduce new issues.

## Core Principle

**Every fix must be verified** to ensure:
- Issues were actually resolved
- No new issues were introduced
- Quality scores improved or stayed the same
- No unintended side effects occurred

## When to Verify

**Verification is mandatory** after:
- Safe fixes applied (Step 8)
- Risky fixes applied (Step 9)
- Any modifications made to components

**Skip verification** only when:
- No fixes were applied (nothing changed)
- User explicitly skipped all fixes

## Re-Run Analysis Pattern

### For Skills

After modifying a skill, re-run the diagnose-skill analysis agent to verify:
- Pass the absolute path to the modified skill
- Request complete JSON report with all issues found
- Compare results with pre-fix analysis

### For Agents

After modifying an agent, re-run the diagnose-agent analysis agent to verify:
- Pass the absolute path to the modified agent
- Request complete JSON report with all issues found
- Compare results with pre-fix analysis

### For Commands

After modifying a command, re-run the diagnose-command analysis agent to verify:
- Pass the absolute path to the modified command
- Request complete JSON report with all issues found
- Compare results with pre-fix analysis

## Parallel Re-Analysis

When multiple components were modified:

**Launch all re-analysis agents in PARALLEL** for efficiency:
- Invoke diagnosis agents concurrently in a single message
- Each agent analyzes one modified component
- Collect all results before comparing metrics
- Example: If 3 skills were modified, launch 3 diagnose-skill agents in parallel

## Before/After Comparison

### Metrics to Compare

For each modified component, compare:

1. **Issue Counts**
   - Critical: before vs after
   - Warnings: before vs after
   - Suggestions: before vs after
   - Total: before vs after

2. **Quality Scores**
   - Architecture score: before vs after
   - Integrated content score: before vs after
   - Overall quality: before vs after

3. **Specific Issues**
   - Issues resolved (in before, not in after)
   - Issues remaining (in both before and after)
   - NEW issues (not in before, in after) ← **Critical to detect**

### Comparison Structure

```json
{
  "verification_results": {
    "components_verified": {count},
    "verification_summary": {
      "issues_resolved": {count},
      "issues_remaining": {count},
      "new_issues": {count}
    },
    "by_component": {
      "component-name-1": {
        "before": {
          "critical": {count},
          "warnings": {count},
          "suggestions": {count},
          "total": {count},
          "architecture_score": {score},
          "integrated_content_score": {score},
          "overall_quality": {score}
        },
        "after": {
          "critical": {count},
          "warnings": {count},
          "suggestions": {count},
          "total": {count},
          "architecture_score": {score},
          "integrated_content_score": {score},
          "overall_quality": {score}
        },
        "changes": {
          "issues_resolved": {count},
          "issues_remaining": {count},
          "new_issues": {count},
          "score_change": "+{points}" or "-{points}"
        },
        "specific_issues": {
          "resolved": [
            "YAML frontmatter syntax error at line 5",
            "Broken reference to non-existent file"
          ],
          "remaining": [
            "Duplicate content in two sections (user skipped)"
          ],
          "new": [
            "Invalid cross-reference after consolidation"
          ]
        }
      }
    }
  }
}
```

## Success Criteria

### Successful Verification

A fix verification is considered successful when:
- ✅ Issues resolved > 0
- ✅ New issues = 0
- ✅ Quality score improved or stayed same (tolerance: -1 point)
- ✅ No critical issues introduced

### Failed Verification

A fix verification is considered failed when:
- ❌ New issues > 0 (fixes broke something)
- ❌ Quality score decreased by >1 point
- ❌ Critical issues introduced
- ❌ Issues resolved = 0 (fixes had no effect)

### Partial Success

Some fixes worked, others didn't:
- ⚠️ Issues resolved > 0 AND new issues > 0
- ⚠️ Some components improved, others degraded
- ⚠️ Quality score improved overall but some metrics decreased

## Reporting Verification Results

### Success Report Format

```
==================================================
Verification Complete
==================================================

Components Verified: {count}

Results Summary:
✅ {issues_resolved} issues resolved
⚠️ {issues_remaining} issues remain (user skipped or manual intervention required)
{if new_issues > 0}
❌ {new_issues} NEW issues introduced (fixes need review!)
{endif}

By Component:
- {component-1}: {before_total} → {after_total} issues ({change})
  Quality: {before_quality} → {after_quality} ({score_change})

- {component-2}: {before_total} → {after_total} issues ({change})
  Quality: {before_quality} → {after_quality} ({score_change})

{if all successful}
✅ All fixes verified successfully - no new issues introduced
{endif}

{if any failures}
⚠️ Some fixes introduced new issues - review needed:
- {component-name}: {new-issue-description}
{endif}
```

### Detailed Issue Report

For new issues introduced:

```
❌ NEW ISSUES DETECTED

Component: {component-name}
Location: {file}:{line}
Issue: {description}
Likely cause: {fix-that-caused-it}
Recommended action: {how-to-resolve}

Component: {component-name-2}
...
```

## Rollback Considerations

If verification fails catastrophically:

1. **Inform user** of failure and new issues
2. **Recommend rollback** to pre-fix state
3. **Provide git diff** or change summary
4. **Suggest manual intervention** for complex issues

**Rollback command:**
```
git restore {modified-files}
```

## Iteration Pattern

If issues remain after fixes:

1. **Report remaining issues** clearly
2. **Ask user** if they want to:
   - Apply more fixes (iterate)
   - Skip remaining issues
   - Review manually
3. **Re-run fix workflow** if user chooses to iterate

## Component-Specific Verification

Different component types may verify additional aspects:

**Skills:**
- Standards file cross-references still valid
- SKILL.md still references all standards files
- No orphaned standards files created

**Agents:**
- Tool declarations match actual tool usage
- Architectural patterns not violated
- Agent can still be invoked correctly

**Commands:**
- Workflow steps still coherent
- No broken command parameter references
- Quality checklist still complete

## Quality Standards

- Verification must compare before/after metrics
- New issues must be clearly reported with locations
- Score changes must be tracked
- Rollback guidance must be provided for failures
- Success must mean "no regressions" not just "some fixes applied"

## Efficiency Considerations

- **Parallel re-analysis** when multiple components modified
- **Cache before results** to avoid re-analyzing unchanged components
- **Incremental verification** for large sets (verify as you fix)
- **Skip re-analysis** of components user explicitly skipped
