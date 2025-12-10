# Python Implementation Standards

Standards for implementing Python scripts in the marketplace.

## Shebang and Encoding

All Python scripts MUST start with:

```python
#!/usr/bin/env python3
"""Brief description of what the script does."""
```

## Stdlib-Only Requirement

**CRITICAL**: Scripts MUST use only Python standard library (no pip dependencies).

See `references/stdlib-modules.md` for the complete list of allowed modules.

**Rationale**: Scripts must work on any system with Python 3 installed, without requiring package installation.

## Subcommand Pattern

Scripts MUST follow the `{noun}.py {verb}` pattern using argparse subparsers.

**Required Pattern**:
```python
#!/usr/bin/env python3
"""Manage configuration files for plans."""

import argparse
import json
import sys

def cmd_get(args):
    """Handle 'get' subcommand."""
    # Implementation
    pass

def cmd_set(args):
    """Handle 'set' subcommand."""
    # Implementation
    pass

def cmd_list(args):
    """Handle 'list' subcommand."""
    # Implementation
    pass

def main():
    parser = argparse.ArgumentParser(
        description="Manage configuration files for plans"
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # get subcommand
    get_parser = subparsers.add_parser('get', help='Get a config value')
    get_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    get_parser.add_argument('--key', required=True, help='Configuration key')
    get_parser.set_defaults(func=cmd_get)

    # set subcommand
    set_parser = subparsers.add_parser('set', help='Set a config value')
    set_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    set_parser.add_argument('--key', required=True, help='Configuration key')
    set_parser.add_argument('--value', required=True, help='Value to set')
    set_parser.set_defaults(func=cmd_set)

    # list subcommand
    list_parser = subparsers.add_parser('list', help='List all config values')
    list_parser.add_argument('--plan-id', required=True, help='Plan identifier')
    list_parser.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
```

**Naming Convention**:
- Script name is a noun: `manage-config.py`, `manage-files.py`, `analyze.py`
- Subcommands are verbs: `get`, `set`, `list`, `add`, `remove`, `validate`

**Anti-patterns** (DO NOT use):
- `get-config.py` - verb-noun pattern
- `add-file.py` - verb-noun pattern
- Scripts without subcommand support

## Help Output Requirements

**CRITICAL**: All scripts MUST support `--help` flag via argparse.

Argparse provides automatic help generation. Ensure:
- Parser has a description
- All arguments have help text
- Subparsers have individual help

**Test**:
```bash
python3 .plan/execute-script.py {bundle}:{skill} --help
python3 .plan/execute-script.py {bundle}:{skill} {subcommand} --help
```

## Error Handling

### Input Validation

```python
def cmd_get(args):
    """Handle 'get' subcommand."""
    plan_path = Path(f".plan/plans/{args.plan_id}")

    # Validate plan exists
    if not plan_path.exists():
        print(json.dumps({"error": f"Plan not found: {args.plan_id}"}), file=sys.stderr)
        sys.exit(1)

    # Validate key format
    if not re.match(r'^[a-z][a-z0-9_]*$', args.key):
        print(json.dumps({"error": f"Invalid key format: {args.key}"}), file=sys.stderr)
        sys.exit(1)

    # ... implementation
```

### Error Messages

**Format**: Clear, actionable error messages

**Good Examples**:
```python
{"error": "Plan not found: my-plan"}
{"error": "Invalid key format. Expected: lowercase with underscores, got: MyKey"}
{"error": "Config file parsing failed at line 42: unexpected character"}
```

**Bad Examples**:
```python
{"error": "Error"}  # Too vague
{"error": "Failed"}  # No context
{"error": "1"}  # Not descriptive
```

## Simple YAML Parsing

**DO NOT** use PyYAML. Use custom parsing for simple frontmatter:

```python
def parse_simple_yaml(content: str) -> dict:
    """Parse simple YAML frontmatter (key:value pairs only).

    Handles:
    - key: value pairs
    - Quoted values
    - Simple arrays (single line)
    """
    result = {}
    for line in content.strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            result[key] = value
    return result
```

**Key Insight**: Simple YAML parsing is sufficient for frontmatter - full YAML library is not needed.

## Handler Dictionary Pattern

For scripts with multiple operations:

```python
FIX_HANDLERS = {
    "missing_frontmatter": handle_missing_frontmatter,
    "invalid_yaml": handle_invalid_yaml,
    "unused_tools": handle_unused_tools,
}

def apply_fix(fix_type: str, file_path: str, **kwargs) -> dict:
    handler = FIX_HANDLERS.get(fix_type)
    if not handler:
        return {"error": f"Unknown fix type: {fix_type}"}
    return handler(file_path, **kwargs)
```

## Backup Before Modify Pattern

Always backup files before modification:

```python
import shutil
from pathlib import Path

def apply_fix_with_backup(file_path: str, fix_func) -> dict:
    backup_path = Path(file_path).with_suffix('.bak')
    shutil.copy2(file_path, backup_path)
    try:
        result = fix_func(file_path)
        backup_path.unlink()  # Remove backup on success
        return result
    except Exception as e:
        shutil.copy2(backup_path, file_path)  # Restore on failure
        backup_path.unlink()
        return {"error": str(e)}
```

## Executable Permissions

Scripts MUST have executable permissions:

```bash
chmod +x scripts/script-name.py
```

**Verify**:
```bash
ls -l scripts/
# Should show: -rwxr-xr-x (executable flag set)
```

## Script Quality Checklist

Before marking script as "quality approved":

- [ ] Shebang: `#!/usr/bin/env python3`
- [ ] Stdlib-only (no pip dependencies)
- [ ] Subcommand pattern: `{noun}.py {verb}`
- [ ] Argparse with subparsers
- [ ] All arguments have help text
- [ ] Error handling with clear messages
- [ ] Exit codes (0 for success, 1 for error)
- [ ] Executable permissions set
- [ ] Test file exists and passes
