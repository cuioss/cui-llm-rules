---
name: plan-marshall
description: Generate execute-script.py with embedded script mappings
allowed-tools: Read, Write, Bash, Glob
---

# plan-marshall Command

Generate or update `.plan/execute-script.py` with current script mappings.

## Usage

```
/plan-marshall              # Generate/update executor
/plan-marshall --force      # Regenerate even if up-to-date
/plan-marshall --verify     # Check without modifying
/plan-marshall --dry-run    # Show what would be generated
/plan-marshall --cleanup    # Also clean up old global logs (default: enabled)
```

## Workflow

### Step 1: Load Required Skill

```
Skill: general-tools:script-executor
```

### Step 2: Discover Scripts

Use marketplace-inventory to find all scripts:

```bash
python3 marketplace/bundles/cui-plugin-development-tools/skills/marketplace-inventory/scripts/scan-marketplace-inventory.py --scope marketplace --resource-types scripts
```

### Step 3: Build Mappings

For each discovered script:
1. Extract bundle and skill from path
2. Generate simplified notation: `{bundle}:{skill}`
3. Verify script exists at absolute path

### Step 4: Generate Executor

Read template from:
```
marketplace/bundles/general-tools/skills/script-executor/templates/execute-script.py.template
```

Replace placeholders:
- `{{SCRIPT_MAPPINGS}}` with discovered mappings in format:
  ```python
      "planning:manage-files": "/abs/path/manage-files.py",
      "planning:manage-config": "/abs/path/manage-config.py",
  ```
- `{{EXECUTION_LOG_DIR}}` with absolute path to:
  ```
  marketplace/bundles/general-tools/skills/script-executor/scripts
  ```

Write to: `.plan/execute-script.py`

### Step 5: Clean Up Old Logs

Delete global logs older than 7 days from `.plan/logs/`:

```python
# Import from marketplace location
sys.path.insert(0, '{marketplace}/general-tools/skills/script-executor/scripts')
from execution_log import cleanup_old_global_logs
cleaned = cleanup_old_global_logs(max_age_days=7)
```

### Step 6: Update State

Write to: `.plan/marshall-state.toon`

```toon
status	generated	script_count	checksum	logs_cleaned
success	{timestamp}	{count}	{hash}	{cleaned_count}
```

## Verification

After generation, verify:
1. `execute-script.py` exists and is valid Python
2. All mapped scripts exist
3. State file is current

Run verification:
```bash
python3 -m py_compile .plan/execute-script.py && echo "Executor syntax OK"
python3 .plan/execute-script.py --list | wc -l  # Should match script count
```

## Output

```toon
status	scripts_discovered	executor_generated	logs_cleaned
success	42	.plan/execute-script.py	3
```
