#!/usr/bin/env python3
"""
Create config.toon from structured input.

Creates a configuration file in TOON format with build and workflow settings.
Uses atomic file operations to write to .cui/plans/ directory.

Output: JSON with created file path.
"""

import argparse
import json
import sys
from pathlib import Path

# Import file operations from base module
SCRIPT_DIR = Path(__file__).resolve().parent
MARKETPLACE_DIR = SCRIPT_DIR.parents[4]
FILE_OPS_DIR = MARKETPLACE_DIR / 'bundles' / 'cui-utilities' / 'skills' / 'file-operations-base' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))

from file_ops import atomic_write_file, ensure_directory, output_success, output_error


# Valid enum values
VALID_PLAN_TYPES = ['implementation', 'simple', 'plugin-development']
VALID_TECHNOLOGIES = ['java', 'javascript', 'mixed', 'none']
VALID_BUILD_SYSTEMS = ['maven', 'gradle', 'npm', 'npx', 'none']
VALID_COMPATIBILITY = ['breaking', 'deprecations']
VALID_COMMIT_STRATEGIES = ['fine-granular', 'phase-specific', 'complete']
VALID_FINALIZING = ['commit-only', 'pr-workflow']


def validate_enum(value: str, valid_values: list[str], field_name: str) -> str:
    """Validate enum value.

    Args:
        value: Value to validate
        valid_values: List of valid values
        field_name: Name of field for error message

    Returns:
        Validated value

    Raises:
        ValueError: If value is invalid
    """
    if value not in valid_values:
        raise ValueError(f"Invalid {field_name}: '{value}'. Valid values: {', '.join(valid_values)}")
    return value


def generate_config_toon(
    plan_type: str,
    technology: str,
    build_system: str,
    compatibility: str,
    commit_strategy: str,
    finalizing: str,
    branch: str = "",
    issue: str = ""
) -> str:
    """Generate config.toon content in TOON format.

    Args:
        plan_type: implementation, simple, or plugin-development
        technology: java, javascript, mixed, none
        build_system: maven, gradle, npm, npx, none
        compatibility: breaking or deprecations
        commit_strategy: fine-granular, phase-specific, complete
        finalizing: commit-only or pr-workflow
        branch: Branch name (optional)
        issue: Issue reference (optional)

    Returns:
        Complete config in TOON format
    """
    lines = [
        "# Plan Configuration",
        "",
        f"plan_type: {plan_type}",
        f"branch: {branch or 'none'}",
        f"issue: {issue or 'none'}",
        "",
        f"technology: {technology}",
        f"build_system: {build_system}",
        "",
        f"compatibility: {compatibility}",
        f"commit_strategy: {commit_strategy}",
        f"finalizing: {finalizing}",
    ]

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Create config.toon from structured input',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create Java/Maven config
  %(prog)s --plan-dir .cui/plans/my-task \\
           --plan-type implementation \\
           --technology java \\
           --build-system maven \\
           --compatibility deprecations \\
           --commit-strategy phase-specific \\
           --finalizing pr-workflow

  # Create JavaScript/npm config with context
  %(prog)s --plan-dir .cui/plans/my-task \\
           --plan-type simple \\
           --technology javascript \\
           --build-system npm \\
           --compatibility breaking \\
           --commit-strategy complete \\
           --finalizing commit-only \\
           --branch feature/my-feature \\
           --issue "#123"

Output TOON format:
  # Plan Configuration

  plan_type: implementation
  branch: feature/my-feature
  issue: #123

  technology: java
  build_system: maven

  compatibility: deprecations
  commit_strategy: fine-granular
  finalizing: pr-workflow
"""
    )

    parser.add_argument('--plan-dir', required=True,
                        help='Directory for plan files')
    parser.add_argument('--plan-type', required=True,
                        choices=VALID_PLAN_TYPES,
                        help='Plan type: implementation, simple, or plugin-development')
    parser.add_argument('--technology', required=True,
                        choices=VALID_TECHNOLOGIES,
                        help='Technology stack: java, javascript, mixed, none')
    parser.add_argument('--build-system', required=True,
                        choices=VALID_BUILD_SYSTEMS,
                        help='Build system: maven, gradle, npm, npx, none')
    parser.add_argument('--compatibility', required=True,
                        choices=VALID_COMPATIBILITY,
                        help='Compatibility mode: breaking or deprecations')
    parser.add_argument('--commit-strategy', required=True,
                        choices=VALID_COMMIT_STRATEGIES,
                        help='Commit strategy: fine-granular, phase-specific, complete')
    parser.add_argument('--finalizing', required=True,
                        choices=VALID_FINALIZING,
                        help='Finalizing mode: commit-only or pr-workflow')
    parser.add_argument('--branch', default='',
                        help='Branch name (optional)')
    parser.add_argument('--issue', default='',
                        help='Issue reference (optional)')

    args = parser.parse_args()

    try:
        plan_dir = Path(args.plan_dir)

        # Ensure directory exists
        ensure_directory(plan_dir)

        # Generate content
        content = generate_config_toon(
            plan_type=args.plan_type,
            technology=args.technology,
            build_system=args.build_system,
            compatibility=args.compatibility,
            commit_strategy=args.commit_strategy,
            finalizing=args.finalizing,
            branch=args.branch,
            issue=args.issue
        )

        # Write file with .toon extension
        file_path = plan_dir / "config.toon"
        atomic_write_file(file_path, content)

        output_success(
            'write-config',
            file=str(file_path),
            plan_type=args.plan_type,
            technology=args.technology,
            build_system=args.build_system,
            format='toon'
        )
        return 0

    except Exception as e:
        output_error('write-config', str(e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
