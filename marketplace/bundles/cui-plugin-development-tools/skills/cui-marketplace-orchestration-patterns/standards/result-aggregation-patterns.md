# Result Aggregation Patterns

Patterns for collecting, merging, and reporting results from multiple agents.

## Structured Result Format

### Agent Return Schema

**Diagnosis Agents Return**:
```json
{
  "status": "CLEAN" | "ISSUES",
  "component_name": "string",
  "component_type": "command" | "agent" | "skill",
  "line_count": number,
  "classification": "ACCEPTABLE" | "LARGE" | "BLOATED",
  "issues": [
    {
      "type": "bloat" | "structure" | "reference" | "format",
      "severity": "critical" | "warning" | "suggestion",
      "description": "string",
      "location": "line X-Y",
      "fix_command": "string (optional)"
    }
  ]
}
```

**Fix Agents Return**:
```json
{
  "status": "SUCCESS" | "PARTIAL" | "FAILURE",
  "component_name": "string",
  "fixes_applied": number,
  "files_modified": ["file1.md", "file2.md"],
  "line_reduction": number,
  "remaining_issues": number,
  "errors": ["error messages if any"]
}
```

## Batch Result Collection

### Collecting Parallel Agent Results

**Pattern**: Store results by component name

```javascript
batch_results = {}

For each agent result in batch:
  component_name = result.component_name
  batch_results[component_name] = {
    diagnosis: result_from_diagnose_agent,
    validation: result_from_validate_agent
  }
```

### Merging Diagnosis and Validation

**Pattern**: Combine results for same component

```json
{
  "command_name": "foo",
  "diagnosis": {
    "status": "ISSUES",
    "classification": "BLOATED",
    "line_count": 621,
    "issues": [
      {"type": "bloat", "severity": "critical", ...}
    ]
  },
  "validation": {
    "status": "ISSUES",
    "broken_references": [
      {"type": "SlashCommand", "target": "/missing-cmd", ...}
    ]
  }
}
```

## Cross-Batch Aggregation

### Running Totals Pattern

**Initialize counters**:
```javascript
total_analyzed = 0
clean_count = 0
issues_count = 0
bloated_count = 0
issues_by_type = {
  bloat: [],
  structure: [],
  reference: [],
  format: []
}
```

**Update after each batch**:
```javascript
For each result in batch:
  total_analyzed += 1

  If result.status == "CLEAN":
    clean_count += 1
  Else:
    issues_count += 1

    For each issue in result.issues:
      issues_by_type[issue.type].append({
        component: result.component_name,
        issue: issue
      })

    If result.classification == "BLOATED":
      bloated_count += 1
```

**Report after each batch**:
```
Batch X/9 complete
  Clean: 3/5
  Issues: 2/5

Overall progress: 15/45 analyzed
  Total clean: 12
  Total with issues: 3
  Bloated: 1
```

## Issue Deduplication

### Pattern: Detect Duplicate Issues Across Components

**Problem**: Multiple components may have same issue type

**Solution**: Group by issue pattern
```javascript
grouped_issues = {}

For each component_issues:
  For each issue:
    pattern_key = issue.type + "|" + issue.description_template

    If pattern_key not in grouped_issues:
      grouped_issues[pattern_key] = {
        pattern: issue.description,
        affected_components: [],
        fix_command: issue.fix_command
      }

    grouped_issues[pattern_key].affected_components.append(
      component.name
    )
```

**Report**:
```
Issue: CONTINUOUS IMPROVEMENT RULE format incorrect
Affected: 5 commands
  - java-generate-coverage
  - js-generate-coverage
  - plugin-create-bundle
  - js-fix-jsdoc
  - maven-build-and-fix
Fix: [Same command for all 5]
```

## Summary Report Generation

### Multi-Level Summary Pattern

**Level 1: Executive Summary**
```
DIAGNOSIS COMPLETE

Total Analyzed: 45 commands
Status Breakdown:
  ✅ Clean: 21 (47%)
  ⚠️  Issues: 24 (53%)

Critical Issues:
  🔴 Bloated: 8 commands
  🔴 Broken references: 3 commands
  🟡 Format issues: 5 commands
```

**Level 2: Category Breakdown**
```
BLOATED COMMANDS (8):
  Critical (>550 lines):
    - plugin-diagnose-agents: 621 lines → target 350
    - plugin-diagnose-commands: 578 lines → target 318
    - plugin-diagnose-bundle: 570 lines → target 293
    - plugin-diagnose-skills: 564 lines → target 384

  Moderate (500-550 lines):
    - js-maintain-tests: 534 lines → target 444
    - java-implement-tests: 530 lines
    - plugin-diagnose-marketplace: 523 lines → target 350
    - java-maintain-tests: 512 lines → target 380
```

**Level 3: Detailed Issue List**
```
COMMAND: plugin-diagnose-agents (621 lines)
Issues:
  1. [CRITICAL] Bloat - Embedded orchestration patterns
     Location: Lines 556-590 (Architecture section)
     Fix: Extract to cui-marketplace-orchestration-patterns skill
     Reduction: ~271 lines

  2. [WARNING] Duplicate content - Fix workflow patterns
     Location: Lines 420-485
     Fix: Reference cui-fix-workflow skill instead
     Reduction: ~65 lines
```

## Remediation Plan Format

### Structured Plan Pattern

```markdown
# Remediation Plan

## Phase 1: Quick Wins (Low Risk, High Value)

### Fix 1/5: CONTINUOUS IMPROVEMENT RULE Format
**Affected**: 5 commands
**Risk**: Low (format-only change)
**Effort**: 5 minutes
**Command**:
  /plugin-update-command command-name=java-generate-coverage update="Update CONTINUOUS IMPROVEMENT RULE to imperative format with explicit command-name parameter"

[Repeat for each fix]

## Phase 2: Investigations (Verify Before Acting)

### Investigation 1/3: Broken References
**Affected**: 3 commands
**Action**: Use Grep to verify references actually broken
**Next Steps**: If confirmed broken, update references

## Phase 3: Major Refactoring (High Value, Higher Risk)

### Refactor 1/8: plugin-diagnose-agents Bloat
**Current**: 621 lines (BLOATED)
**Target**: ~350 lines (ACCEPTABLE)
**Actions**:
  1. Create cui-marketplace-orchestration-patterns skill
  2. Extract 271 lines of orchestration patterns
  3. Update plugin-diagnose-agents to reference skill
  4. Verify with /plugin-diagnose-commands

**Success Metrics**:
  - Line count ≤ 400
  - No functionality lost
  - Diagnosis still passes
```

## Progress Tracking Pattern

### Real-Time Progress Updates

```
PHASE 1: QUICK WINS (5 fixes)
[████████████████████] 5/5 complete (100%)

✅ Fix 1/5: java-generate-coverage - CONTINUOUS IMPROVEMENT RULE updated
✅ Fix 2/5: js-generate-coverage - CONTINUOUS IMPROVEMENT RULE updated
✅ Fix 3/5: plugin-create-bundle - CONTINUOUS IMPROVEMENT RULE updated
✅ Fix 4/5: js-fix-jsdoc - CONTINUOUS IMPROVEMENT RULE updated
✅ Fix 5/5: maven-build-and-fix - CONTINUOUS IMPROVEMENT RULE updated

PHASE 2: INVESTIGATIONS (3 investigations)
[████████████████████] 3/3 complete (100%)

✅ Investigation 1/3: plugin-create-bundle - False positive (no actual reference)
✅ Investigation 2/3: java-maintain-tests - False positive (no actual reference)
✅ Investigation 3/3: java-implement-tests - False positive (no actual reference)

PHASE 3: BLOAT REDUCTION (8 commands)
[████░░░░░░░░░░░░░░░░] 1/8 in progress (12%)

⏳ Refactor 1/8: plugin-diagnose-agents - Creating skill...
⏸  Refactor 2/8: plugin-diagnose-commands - Pending
⏸  Refactor 3/8: plugin-diagnose-bundle - Pending
...
```

## References

* Related standards:
  - orchestration-patterns.md - Batch processing patterns
  - token-optimization-strategies.md - Token usage optimization
  - agent-coordination-patterns.md - Multi-agent coordination
