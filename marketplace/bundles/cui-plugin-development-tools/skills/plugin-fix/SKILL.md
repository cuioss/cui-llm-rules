---
name: plugin-fix
description: Fix identified quality issues in marketplace components with automated categorization, application, and verification
allowed-tools: Read, Edit, Write, Bash, AskUserQuestion, Glob, Grep, Skill
---

# Plugin Fix Skill

Comprehensive fix application skill for marketplace components. Provides automated fix workflows with safe/risky categorization, user prompting for risky fixes, and verification.

## Purpose

This skill provides automated fix workflows for issues identified by the plugin-diagnose skill. It categorizes fixes as safe (auto-apply) or risky (require confirmation), applies fixes using specialized scripts, and verifies that fixes resolved the issues.

**Use this skill when:**
- Applying fixes after running plugin-diagnose workflows
- Automating safe fixes without user intervention
- Presenting risky fixes to users for approval
- Verifying fixes resolved the identified issues

## Progressive Disclosure Strategy

**Load ONE reference guide per workflow:**

| Workflow | Reference to Load |
|----------|-------------------|
| analyze-and-categorize | `{baseDir}/references/fix-catalog.md` |
| apply-safe-fixes | `{baseDir}/references/safe-fixes-guide.md` |
| apply-risky-fixes | `{baseDir}/references/risky-fixes-guide.md` |
| verify-fixes | `{baseDir}/references/verification-guide.md` |

**Context Efficiency**: ~600 lines per workflow vs ~2,400 lines if loading all guides

## External Resources

### Scripts (Stdlib-Only, JSON Output)

All scripts located at `{baseDir}/scripts/`:

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `extract-fixable-issues.py` | Filter fixable issues from diagnosis | Diagnosis JSON | Fixable issues JSON |
| `categorize-fixes.py` | Categorize as safe/risky | Extracted issues | `{safe: [], risky: []}` |
| `apply-fix.py` | Apply single fix with backup | Fix JSON, bundle dir | Success/failure JSON |
| `verify-fix.sh` | Verify fix resolved issue | Fix type, component path | Verification JSON |

### Assets

| Asset | Purpose |
|-------|---------|
| `{baseDir}/assets/fix-templates.json` | Fix templates and categorization rules |

## Workflow 1: analyze-and-categorize

**Purpose**: Extract fixable issues from diagnosis results and categorize them as safe or risky.

**Parameters**:
- `diagnosis_json`: Path to diagnosis JSON from plugin-diagnose (required)
- `bundle_dir`: Bundle directory path (required)

**Steps**:

1. **Load Reference Guide**
   ```
   Read: {baseDir}/references/fix-catalog.md
   ```

2. **Extract Fixable Issues**
   ```bash
   Bash: {baseDir}/scripts/extract-fixable-issues.py {diagnosis_json}
   ```
   This filters diagnosis results to only include issues that can be fixed.

3. **Categorize Issues**
   ```bash
   Bash: {baseDir}/scripts/categorize-fixes.py {extracted_issues_path}
   ```
   Outputs JSON with `{safe: [...], risky: [...]}`.

4. **Report Categorization**
   - Report: "Found X safe fixes (auto-applicable) and Y risky fixes (require confirmation)"
   - List safe fix types briefly
   - List risky fix types with why they need confirmation

5. **Return Categorized Fixes**
   Return the categorization JSON for use in subsequent workflows.

**Output**: JSON with `{safe: [...], risky: [...], summary: {...}}`

## Workflow 2: apply-safe-fixes

**Purpose**: Automatically apply all safe fixes without user confirmation.

**Parameters**:
- `categorized_fixes`: JSON from analyze-and-categorize (required)
- `bundle_dir`: Bundle directory path (required)
- `dry_run`: Preview changes without applying (optional, default: false)

**Steps**:

1. **Load Reference Guide**
   ```
   Read: {baseDir}/references/safe-fixes-guide.md
   ```

2. **Check for Safe Fixes**
   If no safe fixes in categorized_fixes:
   - Report: "No safe fixes to apply"
   - Return early

3. **Apply Each Safe Fix**
   For each fix in `categorized_fixes.safe`:
   ```bash
   Bash: echo '{fix_json}' | {baseDir}/scripts/apply-fix.py - {bundle_dir}
   ```
   Track:
   - Successful fixes (with changes made)
   - Failed fixes (with error details)

4. **Report Results**
   - Report: "Applied X/Y safe fixes successfully"
   - List changes made by each fix
   - If any failures, show error details

5. **Recommend Verification**
   - Suggest: "Run verify-fixes workflow to confirm fixes resolved issues"

**Output**: Applied fixes report with success/failure details

## Workflow 3: apply-risky-fixes

**Purpose**: Present risky fixes to user for approval, then apply approved fixes.

**Parameters**:
- `categorized_fixes`: JSON from analyze-and-categorize (required)
- `bundle_dir`: Bundle directory path (required)

**Steps**:

1. **Load Reference Guide**
   ```
   Read: {baseDir}/references/risky-fixes-guide.md
   ```

2. **Check for Risky Fixes**
   If no risky fixes:
   - Report: "No risky fixes to apply"
   - Return early

3. **Present Each Risky Fix**
   For each fix in `categorized_fixes.risky`:

   a. **Explain the Issue**
      - File affected
      - Issue type and severity
      - What the fix will change
      - Why this requires confirmation

   b. **Ask for Approval**
      ```
      AskUserQuestion:
        question: "Apply this fix?"
        options:
          - label: "Yes"
            description: "Apply this fix"
          - label: "No"
            description: "Skip this fix"
          - label: "Skip All"
            description: "Skip all remaining risky fixes"
      ```

   c. **Apply if Approved**
      If user selects "Yes":
      ```bash
      Bash: echo '{fix_json}' | {baseDir}/scripts/apply-fix.py - {bundle_dir}
      ```

   d. **Handle Skip All**
      If user selects "Skip All", break out of loop

4. **Report Results**
   - Report: "X fixes approved, Y applied successfully, Z skipped"
   - List what was changed
   - List what was skipped

5. **Recommend Verification**
   - Suggest: "Run verify-fixes workflow to confirm fixes resolved issues"

**Output**: Applied risky fixes report with approval/rejection details

## Workflow 4: verify-fixes

**Purpose**: Verify that applied fixes actually resolved the issues.

**Parameters**:
- `applied_fixes`: JSON from apply-safe-fixes or apply-risky-fixes (required)
- `bundle_dir`: Bundle directory path (required)

**Steps**:

1. **Load Reference Guide**
   ```
   Read: {baseDir}/references/verification-guide.md
   ```

2. **Check for Applied Fixes**
   If no applied fixes:
   - Report: "No fixes to verify"
   - Return early

3. **Verify Each Applied Fix**
   For each fix that was successfully applied:
   ```bash
   Bash: {baseDir}/scripts/verify-fix.sh {fix_type} {component_path}
   ```
   Parse verification result:
   - `verified: true` - Verification completed
   - `issue_resolved: true` - Issue is no longer present
   - `issue_resolved: false` - Issue still present (fix may have failed)

4. **Collect Verification Results**
   Track:
   - Verified and resolved
   - Verified but not resolved (needs investigation)
   - Verification failed (script error)

5. **Report Verification Summary**
   - Report: "X/Y fixes verified successful"
   - List resolved issues
   - If any unresolved, list with details and recommendations
   - If verification failures, suggest re-running diagnostics

**Output**: Verification report with issue resolution status

## Complete Fix Workflow

For a complete fix cycle, execute workflows in order:

```
1. Run plugin-diagnose to identify issues
   → Get diagnosis_json

2. Run analyze-and-categorize
   → Get categorized_fixes (safe + risky)

3. Run apply-safe-fixes (automatic)
   → Applied safe fixes

4. Run apply-risky-fixes (with prompts)
   → Applied approved risky fixes

5. Run verify-fixes
   → Verification report

6. If issues remain, re-run plugin-diagnose
```

## Fix Type Reference

### Safe Fix Types (Auto-Apply)

| Type | What It Fixes |
|------|---------------|
| `missing-frontmatter` | Adds YAML frontmatter with defaults |
| `invalid-yaml` | Fixes YAML syntax errors |
| `missing-name-field` | Adds name field from filename |
| `missing-description-field` | Adds placeholder description |
| `missing-tools-field` | Adds minimal tools declaration |
| `array-syntax-tools` | Converts `[A, B]` to `A, B` |
| `trailing-whitespace` | Removes trailing whitespace |
| `improper-indentation` | Normalizes indentation |

### Risky Fix Types (Require Confirmation)

| Type | What It Fixes | Why Risky |
|------|---------------|-----------|
| `unused-tool-declared` | Removes unused tools | May be intentional |
| `tool-not-declared` | Adds missing tool | Changes capabilities |
| `rule-6-violation` | Removes Task tool | Affects agent design |
| `rule-7-violation` | Removes Maven patterns | Affects build logic |
| `pattern-22-violation` | Changes self-update to caller reporting | Structural change |

## Integration with Plugin-Diagnose

This skill is designed to work with output from the plugin-diagnose skill:

```
plugin-diagnose:diagnose-agents → plugin-fix:analyze-and-categorize
plugin-diagnose:diagnose-commands → plugin-fix:analyze-and-categorize
plugin-diagnose:diagnose-skills → plugin-fix:analyze-and-categorize
```

The diagnosis JSON format is compatible with extract-fixable-issues.py.

## Error Handling

**Script Failures**:
- apply-fix.py creates backups before modifying files
- If fix fails, backup is restored automatically
- Verification workflow detects unresolved issues

**User Cancellation**:
- "Skip All" in risky fixes exits gracefully
- Partial application is tracked and reported

**File Not Found**:
- Scripts handle missing files gracefully
- Error reported in JSON output
- Workflow continues with remaining fixes

## Quality Standards

- **Backup before modify**: All fixes create `.fix-backup` files
- **JSON output**: All scripts output parseable JSON
- **Stdlib-only**: No external dependencies
- **Verification**: Always recommend verification after fixes
- **User control**: Risky fixes require explicit approval

## See Also

- `plugin-diagnose` - Identify issues to fix
- `plugin-create` - Create new components correctly
- `plugin-architecture` - Architecture standards that fixes enforce
