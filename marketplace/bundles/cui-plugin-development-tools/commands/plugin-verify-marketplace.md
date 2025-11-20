---
name: plugin-verify-marketplace
description: Execute full marketplace verification by running all diagnostic commands sequentially
---

# Verify Marketplace Command

Comprehensive marketplace verification orchestrator that executes all diagnostic commands in optimal sequence to ensure marketplace integrity, quality, and consistency.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=plugin-verify-marketplace update="[your improvement]"` with:
1. Better orchestration patterns for running multiple diagnostic commands
2. Improved error handling and failure reporting strategies
3. More efficient inventory sharing mechanisms across diagnostic steps
4. Enhanced verification coverage or diagnostic sequencing
5. Any lessons learned about marketplace validation workflows

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

**bundle** - Optional bundle name to verify (default: all bundles)
  - If provided, filters verification to specific bundle
  - Example: `bundle=cui-java-expert`

**fail-fast** - Stop on first diagnostic failure (default: true)
  - If `true`, exits immediately when any diagnostic command fails
  - If `false`, runs all diagnostics and reports summary at end
  - Example: `fail-fast=false`

## WORKFLOW

### Step 1: Run Inventory Scan

Execute scan-marketplace-inventory.sh script to collect marketplace state once and reuse across all diagnostics:

```
Bash: ./.claude/skills/cui-marketplace-architecture/scripts/scan-marketplace-inventory.sh --scope marketplace
```

**Capture inventory results** for passing to subsequent commands to avoid redundant file scanning.

**Error handling:**
- If inventory fails, abort verification (cannot proceed without marketplace state)
- Display: "❌ Inventory scan failed: {error}"

### Step 2: Diagnose Skills

Execute skill diagnostics using inventory results:

```
SlashCommand: /plugin-diagnose-skills bundle={bundle}
```

**If fail-fast=true and command fails:**
- Display: "❌ Skill diagnostics failed - aborting verification"
- Exit with failure status

**If fail-fast=false:**
- Track failure, continue to next step

### Step 3: Diagnose Agents

Execute agent diagnostics using inventory results:

```
SlashCommand: /plugin-diagnose-agents bundle={bundle}
```

**If fail-fast=true and command fails:**
- Display: "❌ Agent diagnostics failed - aborting verification"
- Exit with failure status

**If fail-fast=false:**
- Track failure, continue to next step

### Step 4: Diagnose Commands

Execute command diagnostics using inventory results:

```
SlashCommand: /plugin-diagnose-commands bundle={bundle}
```

**If fail-fast=true and command fails:**
- Display: "❌ Command diagnostics failed - aborting verification"
- Exit with failure status

**If fail-fast=false:**
- Track failure, continue to next step

### Step 5: Diagnose Metadata

Execute metadata diagnostics for all bundles or specific bundle:

```
SlashCommand: /plugin-diagnose-metadata bundle={bundle}
```

**If fail-fast=true and command fails:**
- Display: "❌ Metadata diagnostics failed - aborting verification"
- Exit with failure status

**If fail-fast=false:**
- Track failure, continue to next step

### Step 6: Maintain README Files

Execute README maintenance to ensure documentation is current:

```
SlashCommand: /plugin-maintain-readme bundle={bundle}
```

**If fail-fast=true and command fails:**
- Display: "❌ README maintenance failed - aborting verification"
- Exit with failure status

**If fail-fast=false:**
- Track failure, continue to summary

### Step 7: Display Verification Summary

**If all diagnostics passed:**
```
╔════════════════════════════════════════════════════════════╗
║          Marketplace Verification: PASSED                  ║
╚════════════════════════════════════════════════════════════╝

All diagnostic commands completed successfully:
✓ Inventory scan
✓ Skills diagnostics
✓ Agents diagnostics
✓ Commands diagnostics
✓ Metadata diagnostics
✓ README maintenance

{bundle_info}
```

**If any diagnostics failed (fail-fast=false mode):**
```
╔════════════════════════════════════════════════════════════╗
║          Marketplace Verification: FAILED                  ║
╚════════════════════════════════════════════════════════════╝

Diagnostic Results:
{list each step with ✓/❌ status}

Failed Commands:
{detailed failure information for each failed step}

{bundle_info}
```

**bundle_info format:**
- If bundle parameter provided: "Bundle: {bundle}"
- If all bundles: "Scope: All marketplace bundles"

## STATISTICS TRACKING

Track throughout workflow:
- `diagnostics_run`: Count of diagnostic commands executed
- `diagnostics_passed`: Count of successful diagnostics
- `diagnostics_failed`: Count of failed diagnostics
- `total_issues_found`: Sum of all issues across diagnostics
- `total_issues_fixed`: Sum of all fixes applied

Display all statistics in final summary.

## CRITICAL RULES

**Orchestration:**
- Run inventory ONCE at start, reuse results across all diagnostics
- Execute diagnostics in dependency order (skills → agents → commands → metadata → readme)
- Pass bundle parameter through to all diagnostic commands when provided
- Respect fail-fast setting consistently across all steps

**Error Handling:**
- Inventory failure is always fatal (cannot verify without marketplace state)
- Diagnostic failures respect fail-fast parameter
- Track all failures for final summary when fail-fast=false
- Clear error messages indicating which step failed

**Parameter Validation:**
- bundle parameter must match existing bundle if provided
- fail-fast must be boolean (true/false)
- Default to fail-fast=true for safety

**Performance:**
- Avoid redundant file scanning by sharing inventory results
- Each diagnostic command should accept pre-scanned inventory data
- Minimal overhead from orchestration layer

## USAGE EXAMPLES

**Verify entire marketplace:**
```
/plugin-verify-marketplace
```

**Verify specific bundle:**
```
/plugin-verify-marketplace bundle=cui-java-expert
```

**Run all diagnostics regardless of failures:**
```
/plugin-verify-marketplace fail-fast=false
```

**Verify specific bundle, continue on errors:**
```
/plugin-verify-marketplace bundle=cui-frontend-expert fail-fast=false
```

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=plugin-verify-marketplace update="[your improvement]"` with:
1. Better validation logic for detecting structural issues
2. More accurate error detection and reporting
3. Improved orchestration efficiency across diagnostic commands
4. Enhanced fail-fast vs comprehensive mode handling
5. Any lessons learned about marketplace verification patterns

This ensures the command evolves and becomes more effective with each execution.

## RELATED

- `scan-marketplace-inventory.sh` script - Scans marketplace structure
- `/plugin-diagnose-skills` - Validates skills
- `/plugin-diagnose-agents` - Validates agents
- `/plugin-diagnose-commands` - Validates commands
- `/plugin-diagnose-metadata` - Validates metadata files
- `/plugin-maintain-readme` - Updates README documentation
