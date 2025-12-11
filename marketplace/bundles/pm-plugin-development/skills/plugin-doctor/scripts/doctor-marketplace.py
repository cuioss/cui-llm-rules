#!/usr/bin/env python3
"""
doctor-marketplace.py - Batch marketplace analysis and fixing.

Provides automated batch operations across the entire marketplace:
- scan: Discover all components (agents, commands, skills, scripts)
- analyze: Batch analyze all components for issues
- fix: Apply safe fixes automatically across marketplace
- report: Generate comprehensive report for LLM review

This is Phase 1 of the hybrid doctor workflow. It handles deterministic
operations that can be fully automated. Phase 2 (LLM) handles semantic
analysis and complex fixes.

Output: JSON to stdout.

Usage:
    python3 doctor-marketplace.py scan [--bundles NAMES]
    python3 doctor-marketplace.py analyze [--bundles NAMES] [--type TYPE]
    python3 doctor-marketplace.py fix [--bundles NAMES] [--dry-run]
    python3 doctor-marketplace.py report [--bundles NAMES] [--output FILE]
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Import from sibling scripts (same directory)
SCRIPT_DIR = Path(__file__).parent

# Add parent paths to allow imports from analyze.py and fix.py
sys.path.insert(0, str(SCRIPT_DIR))

# Import functions from analyze.py
from analyze import (
    analyze_markdown_file,
    analyze_skill_structure,
    analyze_tool_coverage,
    detect_component_type,
)

# Import functions from fix.py
from fix import (
    SAFE_FIX_TYPES,
    RISKY_FIX_TYPES,
    categorize_fix,
    apply_single_fix,
    load_templates,
)


# =============================================================================
# Constants
# =============================================================================

MARKETPLACE_BUNDLES_PATH = "marketplace/bundles"
TEMP_DIR = ".plan/temp"
REPORT_PREFIX = "doctor-marketplace-report"


def get_default_report_path() -> Path:
    """Generate timestamped report path in .plan/temp/ directory."""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path(TEMP_DIR) / f"{REPORT_PREFIX}-{timestamp}.json"


def ensure_temp_dir() -> Path:
    """Ensure .plan/temp/ directory exists and return path."""
    temp_path = Path(TEMP_DIR)
    temp_path.mkdir(parents=True, exist_ok=True)
    return temp_path


# =============================================================================
# Discovery Functions (adapted from scan-marketplace-inventory.py)
# =============================================================================

def find_marketplace_root() -> Optional[Path]:
    """Find the marketplace/bundles directory."""
    # Try current directory first
    cwd = Path.cwd()
    if (cwd / MARKETPLACE_BUNDLES_PATH).is_dir():
        return cwd / MARKETPLACE_BUNDLES_PATH
    # Try parent
    if (cwd.parent / MARKETPLACE_BUNDLES_PATH).is_dir():
        return cwd.parent / MARKETPLACE_BUNDLES_PATH
    return None


def find_bundles(base_path: Path, bundle_filter: Optional[Set[str]] = None) -> List[Path]:
    """Find all bundle directories by locating plugin.json files."""
    bundles = []
    for plugin_json in base_path.rglob(".claude-plugin/plugin.json"):
        bundle_dir = plugin_json.parent.parent
        if bundle_filter and bundle_dir.name not in bundle_filter:
            continue
        if bundle_dir not in bundles:
            bundles.append(bundle_dir)
    return sorted(bundles, key=lambda p: p.name)


def discover_components(bundle_dir: Path) -> Dict[str, List[Dict]]:
    """Discover all components in a bundle."""
    components = {
        "agents": [],
        "commands": [],
        "skills": [],
        "scripts": []
    }

    # Agents
    agents_dir = bundle_dir / "agents"
    if agents_dir.is_dir():
        for f in sorted(agents_dir.glob("*.md")):
            if f.is_file():
                components["agents"].append({
                    "name": f.stem,
                    "path": str(f),
                    "type": "agent"
                })

    # Commands
    commands_dir = bundle_dir / "commands"
    if commands_dir.is_dir():
        for f in sorted(commands_dir.glob("*.md")):
            if f.is_file():
                components["commands"].append({
                    "name": f.stem,
                    "path": str(f),
                    "type": "command"
                })

    # Skills
    skills_dir = bundle_dir / "skills"
    if skills_dir.is_dir():
        for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
            skill_dir = skill_md.parent
            components["skills"].append({
                "name": skill_dir.name,
                "path": str(skill_dir),
                "skill_md_path": str(skill_md),
                "type": "skill"
            })

    # Scripts
    if skills_dir.is_dir():
        for script_file in sorted(skills_dir.rglob("scripts/*.py")):
            if script_file.is_file():
                skill_dir = script_file.parent.parent
                components["scripts"].append({
                    "name": script_file.stem,
                    "path": str(script_file),
                    "skill": skill_dir.name,
                    "type": "script"
                })
        for script_file in sorted(skills_dir.rglob("scripts/*.sh")):
            if script_file.is_file():
                skill_dir = script_file.parent.parent
                components["scripts"].append({
                    "name": script_file.stem,
                    "path": str(script_file),
                    "skill": skill_dir.name,
                    "type": "script"
                })

    return components


# =============================================================================
# Analysis Functions
# =============================================================================

def analyze_component(component: Dict) -> Dict:
    """Analyze a single component and return issues."""
    component_type = component.get("type")
    path = component.get("path")

    issues = []
    analysis = {}

    if component_type in ("agent", "command"):
        # Markdown analysis
        file_path = Path(path)
        if file_path.exists():
            md_analysis = analyze_markdown_file(file_path, component_type)
            analysis["markdown"] = md_analysis

            # Extract issues from analysis
            issues.extend(extract_issues_from_markdown_analysis(md_analysis, path, component_type))

            # Tool coverage analysis
            coverage = analyze_tool_coverage(file_path)
            if "error" not in coverage:
                analysis["coverage"] = coverage
                issues.extend(extract_issues_from_coverage_analysis(coverage, path))

    elif component_type == "skill":
        skill_dir = Path(path)
        skill_md_path = component.get("skill_md_path")

        # Structure analysis
        structure = analyze_skill_structure(skill_dir)
        analysis["structure"] = structure

        # Markdown analysis of SKILL.md
        if skill_md_path:
            md_path = Path(skill_md_path)
            if md_path.exists():
                md_analysis = analyze_markdown_file(md_path, "skill")
                analysis["markdown"] = md_analysis
                issues.extend(extract_issues_from_markdown_analysis(md_analysis, skill_md_path, "skill"))

    return {
        "component": component,
        "analysis": analysis,
        "issues": issues,
        "issue_count": len(issues)
    }


def extract_issues_from_markdown_analysis(analysis: Dict, file_path: str, component_type: str) -> List[Dict]:
    """Extract fixable issues from markdown analysis."""
    issues = []

    # Check frontmatter
    fm = analysis.get("frontmatter", {})
    if not fm.get("present"):
        issues.append({
            "type": "missing-frontmatter",
            "file": file_path,
            "severity": "error",
            "fixable": True
        })
    elif not fm.get("yaml_valid"):
        issues.append({
            "type": "invalid-yaml",
            "file": file_path,
            "severity": "error",
            "fixable": True
        })
    else:
        required = fm.get("required_fields", {})
        if not required.get("name", {}).get("present"):
            issues.append({
                "type": "missing-name-field",
                "file": file_path,
                "severity": "error",
                "fixable": True
            })
        if not required.get("description", {}).get("present"):
            issues.append({
                "type": "missing-description-field",
                "file": file_path,
                "severity": "warning",
                "fixable": True
            })
        if component_type in ("agent", "command") and not required.get("tools", {}).get("present"):
            issues.append({
                "type": "missing-tools-field",
                "file": file_path,
                "severity": "warning",
                "fixable": True
            })

    # Check rule violations
    rules = analysis.get("rules", {})
    if rules.get("rule_6_violation"):
        issues.append({
            "type": "rule-6-violation",
            "file": file_path,
            "severity": "warning",
            "fixable": True,
            "description": "Agent declares Task tool (Rule 6)"
        })
    if rules.get("rule_7_violation"):
        issues.append({
            "type": "rule-7-violation",
            "file": file_path,
            "severity": "warning",
            "fixable": False,
            "description": "Direct Maven usage outside builder (Rule 7)"
        })
    if rules.get("rule_8_violation"):
        issues.append({
            "type": "rule-8-violation",
            "file": file_path,
            "severity": "warning",
            "fixable": False,
            "description": "Direct script path (Rule 8)"
        })

    # Check CI rule
    ci = analysis.get("continuous_improvement_rule", {})
    if ci.get("format", {}).get("pattern_22_violation"):
        issues.append({
            "type": "pattern-22-violation",
            "file": file_path,
            "severity": "warning",
            "fixable": True,
            "description": "Agent uses self-update pattern (Pattern 22)"
        })

    # Check bloat
    bloat = analysis.get("bloat", {}).get("classification", "NORMAL")
    if bloat in ("CRITICAL", "BLOATED"):
        issues.append({
            "type": "file-bloat",
            "file": file_path,
            "severity": "warning" if bloat == "BLOATED" else "error",
            "fixable": False,
            "classification": bloat,
            "line_count": analysis.get("metrics", {}).get("line_count", 0)
        })

    return issues


def extract_issues_from_coverage_analysis(coverage: Dict, file_path: str) -> List[Dict]:
    """Extract issues from tool coverage analysis."""
    issues = []

    tc = coverage.get("tool_coverage", {})

    # Unused tools
    unused = tc.get("unused_tools", [])
    if unused:
        issues.append({
            "type": "unused-tool-declared",
            "file": file_path,
            "severity": "info",
            "fixable": True,
            "details": {"unused_tools": unused}
        })

    # Missing tools
    missing = tc.get("missing_tools", [])
    if missing:
        issues.append({
            "type": "tool-not-declared",
            "file": file_path,
            "severity": "warning",
            "fixable": True,
            "details": {"missing_tools": missing}
        })

    return issues


# =============================================================================
# Fix Functions
# =============================================================================

def categorize_all_issues(issues: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize issues into safe and risky."""
    safe = []
    risky = []
    unfixable = []

    for issue in issues:
        if not issue.get("fixable", False):
            unfixable.append(issue)
            continue

        category = categorize_fix(issue)
        if category == "safe":
            safe.append(issue)
        else:
            risky.append(issue)

    return {
        "safe": safe,
        "risky": risky,
        "unfixable": unfixable
    }


def apply_safe_fixes(issues: List[Dict], marketplace_root: Path, dry_run: bool = False) -> Dict:
    """Apply all safe fixes to files."""
    results = {
        "applied": [],
        "failed": [],
        "skipped": [],
        "dry_run": dry_run
    }

    templates = load_templates(SCRIPT_DIR)

    # Group issues by file to avoid conflicts
    by_file: Dict[str, List[Dict]] = {}
    for issue in issues:
        file_path = issue.get("file", "")
        if file_path:
            by_file.setdefault(file_path, []).append(issue)

    for file_path, file_issues in by_file.items():
        path = Path(file_path)
        if not path.exists():
            for issue in file_issues:
                results["failed"].append({
                    "issue": issue,
                    "error": f"File not found: {file_path}"
                })
            continue

        # Find bundle directory for this file
        bundle_dir = find_bundle_for_file(path, marketplace_root)
        if not bundle_dir:
            for issue in file_issues:
                results["failed"].append({
                    "issue": issue,
                    "error": "Could not determine bundle directory"
                })
            continue

        for issue in file_issues:
            if dry_run:
                results["skipped"].append({
                    "issue": issue,
                    "reason": "dry_run"
                })
                continue

            # Convert absolute path to relative for apply_single_fix
            try:
                rel_path = str(path.relative_to(bundle_dir))
            except ValueError:
                rel_path = str(path)

            fix_data = {
                "type": issue.get("type"),
                "file": rel_path,
                "details": issue.get("details", {})
            }

            result = apply_single_fix(fix_data, bundle_dir, templates)

            if result.get("success"):
                results["applied"].append({
                    "issue": issue,
                    "result": result
                })
            else:
                results["failed"].append({
                    "issue": issue,
                    "error": result.get("error", "Unknown error")
                })

    return results


def find_bundle_for_file(file_path: Path, marketplace_root: Path) -> Optional[Path]:
    """Find the bundle directory containing a file."""
    # Walk up from file to find bundle (contains .claude-plugin/plugin.json)
    current = file_path.parent
    while current != current.parent and marketplace_root in current.parents or current == marketplace_root:
        plugin_json = current / ".claude-plugin" / "plugin.json"
        if plugin_json.exists():
            return current
        current = current.parent
    return None


# =============================================================================
# Report Functions
# =============================================================================

def generate_report(scan_results: Dict, analysis_results: List[Dict], fix_results: Optional[Dict] = None) -> Dict:
    """Generate comprehensive report for LLM review."""

    # Aggregate all issues
    all_issues = []
    for result in analysis_results:
        all_issues.extend(result.get("issues", []))

    categorized = categorize_all_issues(all_issues)

    # Count by type
    issue_counts: Dict[str, int] = {}
    for issue in all_issues:
        itype = issue.get("type", "unknown")
        issue_counts[itype] = issue_counts.get(itype, 0) + 1

    # Count by bundle
    bundle_counts: Dict[str, Dict[str, int]] = {}
    for result in analysis_results:
        comp = result.get("component", {})
        path = comp.get("path", "")

        # Extract bundle name from path
        bundle_name = extract_bundle_name(path)
        if bundle_name not in bundle_counts:
            bundle_counts[bundle_name] = {"total": 0, "safe": 0, "risky": 0}

        for issue in result.get("issues", []):
            bundle_counts[bundle_name]["total"] += 1
            cat = categorize_fix(issue)
            if issue.get("fixable", False):
                if cat == "safe":
                    bundle_counts[bundle_name]["safe"] += 1
                else:
                    bundle_counts[bundle_name]["risky"] += 1

    report = {
        "summary": {
            "total_bundles": scan_results.get("total_bundles", 0),
            "total_components": scan_results.get("total_components", 0),
            "total_issues": len(all_issues),
            "safe_fixes": len(categorized["safe"]),
            "risky_fixes": len(categorized["risky"]),
            "unfixable": len(categorized["unfixable"])
        },
        "issues_by_type": issue_counts,
        "issues_by_bundle": bundle_counts,
        "safe_fixes": categorized["safe"],
        "risky_fixes": categorized["risky"],
        "unfixable_issues": categorized["unfixable"],
        "llm_review_items": []
    }

    # Items requiring LLM review
    for issue in categorized["risky"]:
        report["llm_review_items"].append({
            "type": issue.get("type"),
            "file": issue.get("file"),
            "description": issue.get("description", ""),
            "action_required": "Review and confirm fix"
        })

    for issue in categorized["unfixable"]:
        report["llm_review_items"].append({
            "type": issue.get("type"),
            "file": issue.get("file"),
            "description": issue.get("description", ""),
            "action_required": "Manual investigation required"
        })

    if fix_results:
        report["fix_results"] = {
            "applied": len(fix_results.get("applied", [])),
            "failed": len(fix_results.get("failed", [])),
            "skipped": len(fix_results.get("skipped", []))
        }

    return report


def extract_bundle_name(path: str) -> str:
    """Extract bundle name from a file path."""
    parts = path.split("/")
    try:
        bundles_idx = parts.index("bundles")
        if bundles_idx + 1 < len(parts):
            return parts[bundles_idx + 1]
    except ValueError:
        pass
    return "unknown"


# =============================================================================
# Subcommands
# =============================================================================

def cmd_scan(args) -> int:
    """Scan marketplace and list all components."""
    marketplace_root = find_marketplace_root()
    if not marketplace_root:
        print(json.dumps({"error": "Marketplace directory not found"}), file=sys.stderr)
        return 1

    bundle_filter = None
    if args.bundles:
        bundle_filter = {b.strip() for b in args.bundles.split(",") if b.strip()}

    bundles = find_bundles(marketplace_root, bundle_filter)

    results = {
        "marketplace_root": str(marketplace_root),
        "bundles": [],
        "total_bundles": 0,
        "total_components": 0
    }

    total_components = 0
    for bundle_dir in bundles:
        components = discover_components(bundle_dir)
        bundle_total = sum(len(v) for v in components.values())
        total_components += bundle_total

        results["bundles"].append({
            "name": bundle_dir.name,
            "path": str(bundle_dir),
            "components": components,
            "counts": {
                "agents": len(components["agents"]),
                "commands": len(components["commands"]),
                "skills": len(components["skills"]),
                "scripts": len(components["scripts"]),
                "total": bundle_total
            }
        })

    results["total_bundles"] = len(bundles)
    results["total_components"] = total_components

    print(json.dumps(results, indent=2))
    return 0


def cmd_analyze(args) -> int:
    """Analyze all components for issues."""
    marketplace_root = find_marketplace_root()
    if not marketplace_root:
        print(json.dumps({"error": "Marketplace directory not found"}), file=sys.stderr)
        return 1

    bundle_filter = None
    if args.bundles:
        bundle_filter = {b.strip() for b in args.bundles.split(",") if b.strip()}

    type_filter = None
    if args.type:
        type_filter = {t.strip() for t in args.type.split(",") if t.strip()}

    bundles = find_bundles(marketplace_root, bundle_filter)

    all_analysis = []
    total_issues = 0

    for bundle_dir in bundles:
        components = discover_components(bundle_dir)

        # Filter by type if specified
        component_list = []
        if not type_filter or "agent" in type_filter or "agents" in type_filter:
            component_list.extend(components["agents"])
        if not type_filter or "command" in type_filter or "commands" in type_filter:
            component_list.extend(components["commands"])
        if not type_filter or "skill" in type_filter or "skills" in type_filter:
            component_list.extend(components["skills"])

        for component in component_list:
            result = analyze_component(component)
            result["bundle"] = bundle_dir.name
            all_analysis.append(result)
            total_issues += result.get("issue_count", 0)

    # Categorize all issues
    all_issues = []
    for result in all_analysis:
        all_issues.extend(result.get("issues", []))

    categorized = categorize_all_issues(all_issues)

    output = {
        "analysis": all_analysis,
        "summary": {
            "total_components": len(all_analysis),
            "total_issues": total_issues,
            "safe_fixes": len(categorized["safe"]),
            "risky_fixes": len(categorized["risky"]),
            "unfixable": len(categorized["unfixable"])
        },
        "categorized": categorized
    }

    print(json.dumps(output, indent=2))
    return 0


def cmd_fix(args) -> int:
    """Apply safe fixes across marketplace."""
    marketplace_root = find_marketplace_root()
    if not marketplace_root:
        print(json.dumps({"error": "Marketplace directory not found"}), file=sys.stderr)
        return 1

    bundle_filter = None
    if args.bundles:
        bundle_filter = {b.strip() for b in args.bundles.split(",") if b.strip()}

    bundles = find_bundles(marketplace_root, bundle_filter)

    # First analyze to find issues
    all_issues = []
    for bundle_dir in bundles:
        components = discover_components(bundle_dir)
        for comp_type in ["agents", "commands", "skills"]:
            for component in components[comp_type]:
                result = analyze_component(component)
                all_issues.extend(result.get("issues", []))

    # Categorize and get safe fixes only
    categorized = categorize_all_issues(all_issues)
    safe_issues = categorized["safe"]

    if not safe_issues:
        output = {
            "status": "no_fixes_needed",
            "message": "No safe fixes to apply",
            "dry_run": args.dry_run,
            "total_issues": len(all_issues),
            "risky_issues": len(categorized["risky"]),
            "unfixable_issues": len(categorized["unfixable"])
        }
        print(json.dumps(output, indent=2))
        return 0

    # Apply safe fixes
    fix_results = apply_safe_fixes(safe_issues, marketplace_root, args.dry_run)

    output = {
        "status": "completed",
        "dry_run": args.dry_run,
        "total_safe_issues": len(safe_issues),
        "applied": len(fix_results["applied"]),
        "failed": len(fix_results["failed"]),
        "skipped": len(fix_results["skipped"]),
        "details": fix_results,
        "remaining": {
            "risky_issues": len(categorized["risky"]),
            "unfixable_issues": len(categorized["unfixable"])
        }
    }

    print(json.dumps(output, indent=2))
    return 0 if not fix_results["failed"] else 1


def cmd_report(args) -> int:
    """Generate comprehensive report for LLM review."""
    marketplace_root = find_marketplace_root()
    if not marketplace_root:
        print(json.dumps({"error": "Marketplace directory not found"}), file=sys.stderr)
        return 1

    bundle_filter = None
    if args.bundles:
        bundle_filter = {b.strip() for b in args.bundles.split(",") if b.strip()}

    bundles = find_bundles(marketplace_root, bundle_filter)

    # Scan
    scan_results = {
        "total_bundles": len(bundles),
        "total_components": 0
    }

    # Analyze all
    all_analysis = []
    for bundle_dir in bundles:
        components = discover_components(bundle_dir)
        total = sum(len(v) for v in components.values())
        scan_results["total_components"] += total

        for comp_type in ["agents", "commands", "skills"]:
            for component in components[comp_type]:
                result = analyze_component(component)
                result["bundle"] = bundle_dir.name
                all_analysis.append(result)

    # Generate report
    report = generate_report(scan_results, all_analysis)

    # Determine output path - always write to file
    if args.output:
        output_path = Path(args.output)
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        # Default: timestamped file in .plan/temp/
        ensure_temp_dir()
        output_path = get_default_report_path()

    # Write report to file
    output_json = json.dumps(report, indent=2)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output_json)

    # Output success message with file path
    print(json.dumps({
        "status": "success",
        "report_file": str(output_path),
        "summary": report["summary"]
    }, indent=2))

    return 0


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Batch marketplace analysis and fixing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan entire marketplace
  %(prog)s scan

  # Scan specific bundles
  %(prog)s scan --bundles pm-dev-java,pm-workflow

  # Analyze all components
  %(prog)s analyze

  # Analyze only agents and commands
  %(prog)s analyze --type agents,commands

  # Preview safe fixes (dry run)
  %(prog)s fix --dry-run

  # Apply safe fixes
  %(prog)s fix

  # Generate report for LLM review
  %(prog)s report --output analysis-report.json
"""
    )

    subparsers = parser.add_subparsers(dest='command', help='Operation to perform')

    # scan subcommand
    p_scan = subparsers.add_parser('scan', help='Scan marketplace components')
    p_scan.add_argument('--bundles', help='Comma-separated list of bundle names to scan')
    p_scan.set_defaults(func=cmd_scan)

    # analyze subcommand
    p_analyze = subparsers.add_parser('analyze', help='Analyze all components for issues')
    p_analyze.add_argument('--bundles', help='Comma-separated list of bundle names')
    p_analyze.add_argument('--type', help='Component types to analyze (agents,commands,skills)')
    p_analyze.set_defaults(func=cmd_analyze)

    # fix subcommand
    p_fix = subparsers.add_parser('fix', help='Apply safe fixes across marketplace')
    p_fix.add_argument('--bundles', help='Comma-separated list of bundle names')
    p_fix.add_argument('--dry-run', action='store_true', help='Preview fixes without applying')
    p_fix.set_defaults(func=cmd_fix)

    # report subcommand
    p_report = subparsers.add_parser('report', help='Generate comprehensive report')
    p_report.add_argument('--bundles', help='Comma-separated list of bundle names')
    p_report.add_argument('--output', '-o', help='Output file for report (default: stdout)')
    p_report.set_defaults(func=cmd_report)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
