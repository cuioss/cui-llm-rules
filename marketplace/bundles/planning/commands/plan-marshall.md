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

Display this banner on command start (output as single code block):

```
╔═══════════════════════════════════════════════════════════════════════╗
║                                 :                                     ║
║                               .;:;.                                   ║
║                              :;:::;:                                  ║
║          ...             .;:::::::::;.              ...               ║
║          .::;:::::::::::::;:::::::::;:::::::::::::;::.                ║
║               :;:::::::::::::::::::::::::::::::;:                     ║
║                .;:::::::::::::::::::::::::::::;.                      ║
║                                                                       ║
║                        █▀█ █   █▀█ █▄ █                               ║
║                        █▀▀ █▄▄ █▀█ █ ▀█                               ║
║                  █▀▄▀█ █▀█ █▀█ █▀ █ █ █▀█ █   █                       ║
║                  █ ▀ █ █▀█ █▀▄ ▄█ █▀█ █▀█ █▄▄ █▄▄                     ║
║                                                                       ║
║                .;:::::::::::::::::::::::::::::;.                      ║
║               :;:::::::::::::::::::::::::::::::;:                     ║
║          .::;:::::::::::::;:::::::::;:::::::::::::;::.                ║
║         ...              .;:::::::::;.              ...               ║
║                              :;:::;:                                  ║
║                               .;:;.                                   ║
║                                 :                                     ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### Step 1: Load Required Skill

```
Skill: general-tools:script-executor
```

### Step 2: Discover Scripts with Notation

Use marketplace-inventory to find all scripts (includes `notation` field in `{bundle}:{skill}` format):

```bash
python3 marketplace/bundles/cui-plugin-development-tools/skills/marketplace-inventory/scripts/scan-marketplace-inventory.py --scope marketplace --resource-types scripts
```

Output contains:
```json
{
  "bundles": [{
    "name": "planning",
    "scripts": [{
      "name": "manage-files",
      "skill": "manage-files",
      "notation": "planning:manage-files",
      "path_formats": { "absolute": "/abs/path/manage-files.py" }
    }]
  }]
}
```

### Step 3: Generate Executor

Read template from:
```
marketplace/bundles/general-tools/skills/script-executor/templates/execute-script.py.template
```

Replace placeholders:
- `{{SCRIPT_MAPPINGS}}` with notation→path mappings from Step 2:
  ```python
      "planning:manage-files": "/abs/path/manage-files.py",
      "planning:manage-config": "/abs/path/manage-config.py",
  ```
- `{{EXECUTION_LOG_DIR}}` with absolute path to:
  ```
  marketplace/bundles/general-tools/skills/script-executor/scripts
  ```

Write to: `.plan/execute-script.py`

### Step 4: Clean Up Old Logs

Delete global logs older than 7 days from `.plan/logs/`:

```python
# Import from marketplace location
sys.path.insert(0, '{marketplace}/general-tools/skills/script-executor/scripts')
from execution_log import cleanup_old_global_logs
cleaned = cleanup_old_global_logs(max_age_days=7)
```

### Step 5: Update State

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
