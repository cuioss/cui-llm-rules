#!/usr/bin/env python3
"""
fix.py - Plugin component fix tools.

Consolidated from:
- extract-fixable-issues.py → extract subcommand
- categorize-fixes.py → categorize subcommand
- apply-fix.py → apply subcommand
- verify-fix.py → verify subcommand

Manages extraction, categorization, application, and verification of fixes.

Output: JSON to stdout.
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path


# =============================================================================
# Constants
# =============================================================================

# Issue types that can be fixed automatically or with user confirmation
FIXABLE_ISSUE_TYPES = {
    # Safe fixes (auto-applicable)
    "missing-frontmatter",
    "invalid-yaml",
    "missing-name-field",
    "missing-description-field",
    "missing-tools-field",
    "array-syntax-tools",
    "trailing-whitespace",
    "improper-indentation",
    "missing-blank-line-before-list",
    # Risky fixes (require confirmation)
    "unused-tool-declared",
    "tool-not-declared",
    "rule-6-violation",
    "rule-7-violation",
    "pattern-22-violation",
    "backup-file-pattern",
    "ci-rule-self-update",
}

# Safe fix types - can be auto-applied without user confirmation
SAFE_FIX_TYPES = {
    "missing-frontmatter",
    "invalid-yaml",
    "missing-name-field",
    "missing-description-field",
    "missing-tools-field",
    "array-syntax-tools",
    "trailing-whitespace",
    "improper-indentation",
    "missing-blank-line-before-list",
}

# Risky fix types - require user confirmation
RISKY_FIX_TYPES = {
    "unused-tool-declared",
    "tool-not-declared",
    "rule-6-violation",
    "rule-7-violation",
    "pattern-22-violation",
    "backup-file-pattern",
    "ci-rule-self-update",
}


# =============================================================================
# Shared Functions
# =============================================================================

def extract_frontmatter(content: str) -> tuple[bool, str]:
    """Extract YAML frontmatter from content."""
    if not content.startswith('---'):
        return False, ''

    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if match:
        return True, match.group(1)
    return False, ''


def read_json_input(input_file: str) -> tuple[dict | None, str | None]:
    """Read and parse JSON from file or stdin."""
    try:
        if input_file == "-":
            content = sys.stdin.read()
        else:
            with open(input_file, "r", encoding="utf-8") as f:
                content = f.read()

        if not content.strip():
            return {}, None

        return json.loads(content), None
    except FileNotFoundError:
        return None, f"File not found: {input_file}"
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"


# =============================================================================
# Extract Subcommand (from extract-fixable-issues.py)
# =============================================================================

def is_fixable(issue_type: str) -> bool:
    """Check if an issue type is fixable."""
    return issue_type in FIXABLE_ISSUE_TYPES


def extract_fixable_issues(diagnosis: dict) -> dict:
    """Extract only fixable issues from diagnosis results."""
    issues = diagnosis.get("issues", [])

    fixable_issues = []
    for issue in issues:
        issue_type = issue.get("type", "")
        if is_fixable(issue_type) or issue.get("fixable", False):
            fixable_issues.append(issue)

    return {
        "fixable_issues": fixable_issues,
        "total_count": len(fixable_issues),
        "source_bundle": diagnosis.get("bundle", "unknown"),
        "original_total": len(issues),
        "filtered_count": len(issues) - len(fixable_issues)
    }


def cmd_extract(args) -> int:
    """Extract fixable issues from diagnosis JSON."""
    data, error = read_json_input(args.input)

    if error:
        result = {"error": error, "fixable_issues": [], "total_count": 0}
        print(json.dumps(result, indent=2))
        return 1

    if not data:
        result = {
            "fixable_issues": [],
            "total_count": 0,
            "source_bundle": "unknown",
            "original_total": 0,
            "filtered_count": 0,
            "error": None
        }
        print(json.dumps(result, indent=2))
        return 0

    result = extract_fixable_issues(data)
    result["error"] = None
    print(json.dumps(result, indent=2))
    return 0


# =============================================================================
# Categorize Subcommand (from categorize-fixes.py)
# =============================================================================

def categorize_fix(issue: dict) -> str:
    """Categorize a single issue as 'safe' or 'risky'."""
    issue_type = issue.get("type", "")

    if issue_type in SAFE_FIX_TYPES:
        return "safe"
    elif issue_type in RISKY_FIX_TYPES:
        return "risky"
    else:
        return "risky"


def categorize_issues(extracted: dict) -> dict:
    """Categorize all fixable issues into safe and risky categories."""
    issues = extracted.get("fixable_issues", [])

    safe_fixes = []
    risky_fixes = []

    for issue in issues:
        category = categorize_fix(issue)
        if category == "safe":
            safe_fixes.append(issue)
        else:
            risky_fixes.append(issue)

    return {
        "safe": safe_fixes,
        "risky": risky_fixes,
        "summary": {
            "safe_count": len(safe_fixes),
            "risky_count": len(risky_fixes),
            "total_count": len(issues)
        },
        "source_bundle": extracted.get("source_bundle", "unknown")
    }


def cmd_categorize(args) -> int:
    """Categorize fixable issues as safe or risky."""
    data, error = read_json_input(args.input)

    if error:
        result = {
            "error": error,
            "safe": [],
            "risky": [],
            "summary": {"safe_count": 0, "risky_count": 0, "total_count": 0}
        }
        print(json.dumps(result, indent=2))
        return 1

    if not data:
        result = {
            "safe": [],
            "risky": [],
            "summary": {"safe_count": 0, "risky_count": 0, "total_count": 0},
            "error": None
        }
        print(json.dumps(result, indent=2))
        return 0

    result = categorize_issues(data)
    result["error"] = None
    print(json.dumps(result, indent=2))
    return 0


# =============================================================================
# Apply Subcommand (from apply-fix.py)
# =============================================================================

def load_templates(script_dir: Path) -> dict:
    """Load fix templates from assets/fix-templates.json."""
    templates_path = script_dir.parent / "assets" / "fix-templates.json"
    if templates_path.exists():
        with open(templates_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def apply_missing_frontmatter(file_path: Path, fix: dict, templates: dict) -> dict:
    """Add frontmatter to a file that has none."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if content.strip().startswith("---"):
        return {"success": False, "error": "File already has frontmatter"}

    component_type = "unknown"
    str_path = str(file_path)
    if "/agents/" in str_path:
        component_type = "agent"
    elif "/commands/" in str_path:
        component_type = "command"
    elif "/skills/" in str_path:
        component_type = "skill"

    name = file_path.stem

    frontmatter = f"""---
name: {name}
description: [Description needed]
"""
    if component_type == "agent":
        frontmatter += "tools: Read, Write, Edit\nmodel: sonnet\n"
    frontmatter += "---\n\n"

    new_content = frontmatter + content

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return {
        "success": True,
        "changes": ["Added YAML frontmatter"],
        "component_type": component_type
    }


def apply_array_syntax_fix(file_path: Path, fix: dict, templates: dict) -> dict:
    """Convert array syntax tools: [A, B] to comma-separated tools: A, B."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r'^(tools:\s*)\[([^\]]+)\]'
    replacement = r'\1\2'

    new_content, count = re.subn(pattern, replacement, content, flags=re.MULTILINE)

    if count == 0:
        return {"success": False, "error": "No array syntax found"}

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return {
        "success": True,
        "changes": [f"Converted {count} array syntax to comma-separated"],
        "replacements": count
    }


def apply_missing_field_fix(file_path: Path, fix: dict, templates: dict) -> dict:
    """Add a missing required field to frontmatter."""
    field_name = fix.get("type", "").replace("missing-", "").replace("-field", "")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.strip().startswith("---"):
        return {"success": False, "error": "No frontmatter found"}

    lines = content.split("\n")
    frontmatter_end = -1
    in_frontmatter = False

    for i, line in enumerate(lines):
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
            else:
                frontmatter_end = i
                break

    if frontmatter_end == -1:
        return {"success": False, "error": "Invalid frontmatter structure"}

    defaults = {
        "name": file_path.stem,
        "description": "[Description needed]",
        "tools": "Read"
    }
    default_value = defaults.get(field_name, "[Value needed]")

    new_line = f"{field_name}: {default_value}"
    lines.insert(frontmatter_end, new_line)

    new_content = "\n".join(lines)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return {
        "success": True,
        "changes": [f"Added {field_name}: {default_value}"],
        "field_added": field_name
    }


def apply_trailing_whitespace_fix(file_path: Path, fix: dict, templates: dict) -> dict:
    """Remove trailing whitespace from all lines."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    fixed_count = 0
    new_lines = []
    for line in lines:
        stripped = line.rstrip() + ("\n" if line.endswith("\n") else "")
        if stripped != line:
            fixed_count += 1
        new_lines.append(stripped)

    if new_lines and not new_lines[-1].endswith("\n"):
        new_lines[-1] = new_lines[-1].rstrip()

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    return {
        "success": True,
        "changes": [f"Removed trailing whitespace from {fixed_count} lines"],
        "lines_fixed": fixed_count
    }


def apply_rule_6_fix(file_path: Path, fix: dict, templates: dict) -> dict:
    """Remove Task tool from agent's tools declaration."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    patterns = [
        (r'^(tools:.*),\s*Task\b', r'\1'),
        (r'^(tools:.*)\bTask,\s*', r'\1'),
        (r'^(tools:\s*)Task$', r'\1Read'),
    ]

    new_content = content
    changed = False
    for pattern, replacement in patterns:
        new_content, count = re.subn(pattern, replacement, new_content, flags=re.MULTILINE)
        if count > 0:
            changed = True

    if not changed:
        return {"success": False, "error": "Task tool not found in tools declaration"}

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return {
        "success": True,
        "changes": ["Removed Task tool from tools declaration (Rule 6)"],
        "rule": "Rule 6"
    }


def apply_unused_tool_fix(file_path: Path, fix: dict, templates: dict) -> dict:
    """Remove unused tools from declaration."""
    unused_tools = fix.get("details", {}).get("unused_tools", [])
    if not unused_tools:
        return {"success": False, "error": "No unused tools specified"}

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = content
    removed = []
    for tool in unused_tools:
        patterns = [
            (rf',\s*{tool}\b', ''),
            (rf'\b{tool},\s*', ''),
        ]
        for pattern, replacement in patterns:
            new_content, count = re.subn(pattern, replacement, new_content, flags=re.MULTILINE)
            if count > 0:
                removed.append(tool)
                break

    if not removed:
        return {"success": False, "error": "Could not remove any unused tools"}

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return {
        "success": True,
        "changes": [f"Removed unused tools: {', '.join(removed)}"],
        "tools_removed": removed
    }


def apply_pattern_22_fix(file_path: Path, fix: dict, templates: dict) -> dict:
    """Fix Pattern 22 violation by changing self-update to caller reporting."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    replacements = [
        (r'/plugin-update-agent', 'report improvements to the caller'),
        (r'/plugin-update-command', 'report improvements to the caller'),
        (r'update this agent directly', 'report suggested improvements to the caller'),
        (r'Make the changes yourself', 'Let the caller decide whether to apply changes'),
    ]

    new_content = content
    changes_made = []
    for pattern, replacement in replacements:
        if re.search(pattern, new_content, re.IGNORECASE):
            new_content = re.sub(pattern, replacement, new_content, flags=re.IGNORECASE)
            changes_made.append(f"Replaced '{pattern}' with caller reporting")

    if not changes_made:
        return {"success": False, "error": "No Pattern 22 violations found to fix"}

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    return {
        "success": True,
        "changes": changes_made,
        "pattern": "Pattern 22"
    }


FIX_HANDLERS = {
    "missing-frontmatter": apply_missing_frontmatter,
    "array-syntax-tools": apply_array_syntax_fix,
    "missing-name-field": apply_missing_field_fix,
    "missing-description-field": apply_missing_field_fix,
    "missing-tools-field": apply_missing_field_fix,
    "trailing-whitespace": apply_trailing_whitespace_fix,
    "rule-6-violation": apply_rule_6_fix,
    "unused-tool-declared": apply_unused_tool_fix,
    "pattern-22-violation": apply_pattern_22_fix,
}


def apply_single_fix(fix: dict, bundle_dir: Path, templates: dict) -> dict:
    """Apply a single fix to a component file."""
    fix_type = fix.get("type", "")
    file_path = fix.get("file", "")

    if not fix_type:
        return {"success": False, "error": "Missing fix type"}
    if not file_path:
        return {"success": False, "error": "Missing file path"}

    full_path = bundle_dir / file_path
    if not full_path.exists():
        return {"success": False, "error": f"File not found: {full_path}"}

    backup_path = full_path.with_suffix(full_path.suffix + ".fix-backup")
    shutil.copy2(full_path, backup_path)

    handler = FIX_HANDLERS.get(fix_type)
    if not handler:
        return {
            "success": False,
            "error": f"No handler for fix type: {fix_type}",
            "backup_created": str(backup_path)
        }

    try:
        result = handler(full_path, fix, templates)
        result["fix_type"] = fix_type
        result["file"] = str(file_path)
        result["backup_created"] = str(backup_path)
        return result
    except Exception as e:
        shutil.copy2(backup_path, full_path)
        return {
            "success": False,
            "error": f"Fix failed: {str(e)}",
            "fix_type": fix_type,
            "file": str(file_path),
            "backup_restored": True
        }


def cmd_apply(args) -> int:
    """Apply a single fix to a component file."""
    data, error = read_json_input(args.fix)

    if error:
        result = {"success": False, "error": error}
        print(json.dumps(result, indent=2))
        return 1

    bundle_path = Path(args.bundle_dir)
    if not bundle_path.exists():
        result = {"success": False, "error": f"Bundle directory not found: {args.bundle_dir}"}
        print(json.dumps(result, indent=2))
        return 1

    script_dir = Path(__file__).parent
    templates = load_templates(script_dir)

    result = apply_single_fix(data, bundle_path, templates)
    print(json.dumps(result, indent=2))
    return 0 if result.get("success") else 1


# =============================================================================
# Verify Subcommand (from verify-fix.py)
# =============================================================================

def verify_frontmatter_fix(file_path: Path) -> dict:
    """Verify frontmatter was added with required fields."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError) as e:
        return {'verified': False, 'error': f'Failed to read file: {e}'}

    frontmatter_present, frontmatter = extract_frontmatter(content)

    if not frontmatter_present:
        return {
            'verified': True,
            'issue_resolved': False,
            'details': 'Still missing frontmatter'
        }

    has_name = bool(re.search(r'^name:', frontmatter, re.MULTILINE))
    has_desc = bool(re.search(r'^description:', frontmatter, re.MULTILINE))

    if has_name and has_desc:
        return {
            'verified': True,
            'issue_resolved': True,
            'details': 'Frontmatter present with required fields'
        }

    return {
        'verified': True,
        'issue_resolved': False,
        'details': f'Frontmatter present but missing fields (name: {has_name}, description: {has_desc})'
    }


def verify_array_syntax_fix(file_path: Path) -> dict:
    """Verify tools no longer uses array syntax."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError) as e:
        return {'verified': False, 'error': f'Failed to read file: {e}'}

    frontmatter_present, frontmatter = extract_frontmatter(content)

    if not frontmatter_present:
        return {
            'verified': True,
            'issue_resolved': True,
            'details': 'No frontmatter to check'
        }

    if re.search(r'^tools:.*\[', frontmatter, re.MULTILINE):
        return {
            'verified': True,
            'issue_resolved': False,
            'details': 'Still using array syntax for tools'
        }

    return {
        'verified': True,
        'issue_resolved': True,
        'details': 'Tools now using comma-separated format'
    }


def verify_rule_6_fix(file_path: Path) -> dict:
    """Verify Task tool was removed from declaration."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError) as e:
        return {'verified': False, 'error': f'Failed to read file: {e}'}

    frontmatter_present, frontmatter = extract_frontmatter(content)

    if not frontmatter_present:
        return {
            'verified': True,
            'issue_resolved': True,
            'details': 'No frontmatter to check'
        }

    if re.search(r'^tools:.*\bTask\b', frontmatter, re.MULTILINE):
        return {
            'verified': True,
            'issue_resolved': False,
            'details': 'Task tool still declared (Rule 6 violation)'
        }

    return {
        'verified': True,
        'issue_resolved': True,
        'details': 'Task tool removed from declaration'
    }


def verify_trailing_whitespace_fix(file_path: Path) -> dict:
    """Verify trailing whitespace was removed."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError) as e:
        return {'verified': False, 'error': f'Failed to read file: {e}'}

    trailing_count = len(re.findall(r'[ \t]+$', content, re.MULTILINE))

    if trailing_count > 0:
        return {
            'verified': True,
            'issue_resolved': False,
            'details': f'Still has trailing whitespace on {trailing_count} lines'
        }

    return {
        'verified': True,
        'issue_resolved': True,
        'details': 'No trailing whitespace found'
    }


def verify_pattern_22_fix(file_path: Path) -> dict:
    """Verify self-update patterns were removed."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError) as e:
        return {'verified': False, 'error': f'Failed to read file: {e}'}

    if re.search(r'/plugin-update-agent|/plugin-update-command', content, re.IGNORECASE):
        return {
            'verified': True,
            'issue_resolved': False,
            'details': 'Still contains self-update commands (Pattern 22 violation)'
        }

    return {
        'verified': True,
        'issue_resolved': True,
        'details': 'Self-update patterns removed'
    }


def verify_generic(file_path: Path, fix_type: str) -> dict:
    """Generic verification for unknown fix types."""
    return {
        'verified': True,
        'issue_resolved': None,
        'details': 'Manual verification recommended'
    }


def cmd_verify(args) -> int:
    """Verify that a fix was successfully applied."""
    file_path = Path(args.file)

    if not file_path.exists():
        print(json.dumps({
            'verified': False,
            'error': f'File not found: {args.file}'
        }), file=sys.stderr)
        return 1

    if not file_path.is_file():
        print(json.dumps({
            'verified': False,
            'error': f'Not a file: {args.file}'
        }), file=sys.stderr)
        return 1

    fix_type = args.fix_type

    if fix_type in ('missing-frontmatter', 'missing-name-field',
                    'missing-description-field', 'missing-tools-field'):
        result = verify_frontmatter_fix(file_path)
    elif fix_type == 'array-syntax-tools':
        result = verify_array_syntax_fix(file_path)
    elif fix_type == 'rule-6-violation':
        result = verify_rule_6_fix(file_path)
    elif fix_type == 'trailing-whitespace':
        result = verify_trailing_whitespace_fix(file_path)
    elif fix_type == 'pattern-22-violation':
        result = verify_pattern_22_fix(file_path)
    else:
        result = verify_generic(file_path, fix_type)

    print(json.dumps(result, indent=2))
    return 0


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Plugin component fix tools',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract fixable issues from diagnosis
  %(prog)s extract --input diagnosis.json

  # Categorize fixes as safe/risky
  %(prog)s categorize --input extracted.json

  # Apply a fix
  %(prog)s apply --fix fix.json --bundle-dir /path/to/bundle

  # Verify a fix was applied
  %(prog)s verify --fix-type missing-frontmatter --file agent.md
"""
    )

    subparsers = parser.add_subparsers(dest='command', help='Operation to perform')

    # extract subcommand
    p_extract = subparsers.add_parser('extract', help='Extract fixable issues')
    p_extract.add_argument(
        '--input', '-i',
        default='-',
        help="Path to diagnosis JSON file, or '-' for stdin (default: stdin)"
    )
    p_extract.set_defaults(func=cmd_extract)

    # categorize subcommand
    p_categorize = subparsers.add_parser('categorize', help='Categorize fixes as safe/risky')
    p_categorize.add_argument(
        '--input', '-i',
        default='-',
        help="Path to extracted issues JSON, or '-' for stdin (default: stdin)"
    )
    p_categorize.set_defaults(func=cmd_categorize)

    # apply subcommand
    p_apply = subparsers.add_parser('apply', help='Apply a single fix')
    p_apply.add_argument(
        '--fix', '-f',
        required=True,
        help="Path to fix JSON file, or '-' for stdin"
    )
    p_apply.add_argument(
        '--bundle-dir', '-b',
        required=True,
        help="Path to bundle directory"
    )
    p_apply.set_defaults(func=cmd_apply)

    # verify subcommand
    p_verify = subparsers.add_parser('verify', help='Verify a fix was applied')
    p_verify.add_argument(
        '--fix-type', '-t',
        required=True,
        help="Type of fix to verify"
    )
    p_verify.add_argument(
        '--file', '-f',
        required=True,
        help="Path to the component file that was fixed"
    )
    p_verify.set_defaults(func=cmd_verify)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
