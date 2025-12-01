#!/usr/bin/env python3
"""
Collect modified files from git diff and add to references.toon.

Runs git diff between base branch and HEAD to find changed files,
categorizes them by type (implementation, test, config), and adds
them to the plan's references.toon file.

Output: JSON with collected files and updates made.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Import file operations from base module
SCRIPT_DIR = Path(__file__).resolve().parent
MARKETPLACE_DIR = SCRIPT_DIR.parents[4]
FILE_OPS_DIR = MARKETPLACE_DIR / 'bundles' / 'general-tools' / 'skills' / 'file-operations-base' / 'scripts'
sys.path.insert(0, str(FILE_OPS_DIR))

from file_ops import output_success, output_error


def get_modified_files(base_branch: str) -> list[str]:
    """Get list of modified files compared to base branch.

    Args:
        base_branch: The branch to compare against (e.g., 'main')

    Returns:
        List of file paths that were added, modified, or renamed
    """
    try:
        # Get the merge-base to find common ancestor
        merge_base_result = subprocess.run(
            ['git', 'merge-base', base_branch, 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        merge_base = merge_base_result.stdout.strip()

        # Get diff against merge-base
        diff_result = subprocess.run(
            ['git', 'diff', '--name-only', '--diff-filter=ACMR', merge_base, 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )

        files = [f.strip() for f in diff_result.stdout.strip().split('\n') if f.strip()]
        return files

    except subprocess.CalledProcessError as e:
        # If merge-base fails, try direct diff
        try:
            diff_result = subprocess.run(
                ['git', 'diff', '--name-only', '--diff-filter=ACMR', base_branch, 'HEAD'],
                capture_output=True,
                text=True,
                check=True
            )
            files = [f.strip() for f in diff_result.stdout.strip().split('\n') if f.strip()]
            return files
        except subprocess.CalledProcessError:
            return []


def categorize_file(file_path: str) -> str:
    """Categorize a file based on its path and name.

    Args:
        file_path: Path to the file

    Returns:
        Category: 'test_files', 'config_files', or 'implementation_files'
    """
    path_lower = file_path.lower()
    name = Path(file_path).name.lower()

    # Test files
    test_indicators = [
        '/test/', '/tests/', '/spec/', '/specs/',
        '/__tests__/', '/__test__/',
        '/src/test/', '/src/tests/'
    ]
    test_suffixes = [
        'test.py', 'test.js', 'test.ts', 'test.java',
        'test.go', 'test.rs', 'test.rb',
        '_test.py', '_test.js', '_test.ts', '_test.java',
        '_test.go', '_test.rs', '_test.rb',
        '.spec.js', '.spec.ts', '.spec.py',
        'tests.py', 'tests.js', 'tests.ts'
    ]

    if any(indicator in path_lower for indicator in test_indicators):
        return 'test_files'
    if any(name.endswith(suffix) for suffix in test_suffixes):
        return 'test_files'

    # Config files
    config_names = [
        'pom.xml', 'build.gradle', 'build.gradle.kts',
        'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
        'tsconfig.json', 'jsconfig.json', 'babel.config.js', 'webpack.config.js',
        '.eslintrc', '.eslintrc.js', '.eslintrc.json', '.eslintrc.yaml',
        '.prettierrc', '.prettierrc.js', '.prettierrc.json',
        'pyproject.toml', 'setup.py', 'setup.cfg', 'requirements.txt',
        'cargo.toml', 'go.mod', 'go.sum',
        'dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
        '.gitignore', '.gitattributes', '.editorconfig',
        'makefile', 'cmakelists.txt',
        'application.properties', 'application.yml', 'application.yaml',
        'settings.json', 'settings.local.json',
        '.env', '.env.example', '.env.local'
    ]
    config_extensions = [
        '.xml', '.yml', '.yaml', '.toml', '.ini', '.cfg',
        '.properties', '.conf', '.config'
    ]
    config_dirs = [
        '/config/', '/configs/', '/configuration/',
        '/.github/', '/.vscode/', '/.idea/'
    ]

    if name in config_names:
        return 'config_files'
    if any(name.endswith(ext) for ext in config_extensions):
        # But not if it's in a source directory
        if not any(src in path_lower for src in ['/src/main/', '/lib/', '/app/']):
            return 'config_files'
    if any(d in path_lower for d in config_dirs):
        return 'config_files'

    # Everything else is implementation
    return 'implementation_files'


def read_references_toon(plan_dir: Path) -> dict:
    """Read and parse existing references.toon."""
    ref_file = plan_dir / 'references.toon'
    if not ref_file.exists():
        return {
            'implementation_files': [],
            'test_files': [],
            'config_files': []
        }

    content = ref_file.read_text()
    result = {
        'implementation_files': [],
        'test_files': [],
        'config_files': []
    }

    current_section = None
    for line in content.splitlines():
        stripped = line.strip()

        # Check for section headers
        for section in ['implementation_files', 'test_files', 'config_files']:
            if stripped.lower().startswith(section) and '[' in stripped:
                current_section = section
                break
        else:
            if stripped.startswith('-') and current_section:
                item = stripped[1:].strip()
                if item and not item.startswith('('):
                    result[current_section].append(item)
            elif stripped and ':' in stripped and not stripped.startswith('#'):
                # New section or scalar, reset
                if not stripped.startswith('-'):
                    current_section = None

    return result


def update_references_toon(plan_dir: Path, updates: dict) -> dict:
    """Update references.toon with new files.

    Args:
        plan_dir: Plan directory path
        updates: Dict with 'implementation_files', 'test_files', 'config_files' lists

    Returns:
        Dict with counts of added files per category
    """
    ref_file = plan_dir / 'references.toon'

    if not ref_file.exists():
        # Should not happen in normal flow, but handle gracefully
        output_error('collect-modified-files', f'references.toon not found in {plan_dir}')
        return {'error': 'references.toon not found'}

    content = ref_file.read_text()
    lines = content.splitlines()
    new_lines = []
    added = {'implementation_files': 0, 'test_files': 0, 'config_files': 0}

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check for file list sections
        section_found = None
        for section in ['implementation_files', 'test_files', 'config_files']:
            if stripped.lower().startswith(section) and '[' in stripped:
                section_found = section
                break

        if section_found:
            # Collect existing items in this section
            existing = set()
            section_lines = [line]
            i += 1

            while i < len(lines):
                next_line = lines[i]
                next_stripped = next_line.strip()

                # Check if we've hit another section
                if next_stripped and ':' in next_stripped and not next_stripped.startswith('-') and not next_stripped.startswith('#'):
                    break

                if next_stripped.startswith('-'):
                    item = next_stripped[1:].strip()
                    if item and not item.startswith('('):
                        existing.add(item)
                    section_lines.append(next_line)
                elif not next_stripped:
                    section_lines.append(next_line)
                else:
                    section_lines.append(next_line)
                i += 1

            # Add new files that aren't already present
            new_files = [f for f in updates.get(section_found, []) if f not in existing]
            added[section_found] = len(new_files)

            # Update count in header
            total_count = len(existing) + len(new_files)
            header_line = f"{section_found}[{total_count}]:"
            new_lines.append(header_line)

            # Add existing items (skip old header)
            for sl in section_lines[1:]:
                if sl.strip().startswith('-'):
                    new_lines.append(sl)

            # Add new items
            for f in new_files:
                new_lines.append(f"- {f}")

            # Add trailing blank line if there was one
            if section_lines and not section_lines[-1].strip():
                if new_lines[-1].strip():
                    new_lines.append('')
        else:
            new_lines.append(line)
            i += 1

    # Write updated content
    new_content = '\n'.join(new_lines)
    if not new_content.endswith('\n'):
        new_content += '\n'

    ref_file.write_text(new_content)

    return added


def main():
    parser = argparse.ArgumentParser(
        description='Collect modified files from git diff and add to references.toon',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Collect files changed since main branch
  %(prog)s --plan-dir .plan/plans/my-task --base-branch main

  # Dry run to see what would be collected
  %(prog)s --plan-dir .plan/plans/my-task --base-branch main --dry-run
"""
    )

    parser.add_argument('--plan-dir', required=True,
                        help='Directory containing the plan files')
    parser.add_argument('--base-branch', default='main',
                        help='Base branch to compare against (default: main)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be collected without updating')

    args = parser.parse_args()

    try:
        plan_dir = Path(args.plan_dir)

        if not plan_dir.exists():
            output_error('collect-modified-files', f'Plan directory not found: {plan_dir}')
            return 1

        # Get modified files from git
        modified_files = get_modified_files(args.base_branch)

        if not modified_files:
            output_success(
                'collect-modified-files',
                message='No modified files found',
                files_found=0,
                base_branch=args.base_branch
            )
            return 0

        # Categorize files
        categorized = {
            'implementation_files': [],
            'test_files': [],
            'config_files': []
        }

        for f in modified_files:
            category = categorize_file(f)
            categorized[category].append(f)

        if args.dry_run:
            output_success(
                'collect-modified-files',
                dry_run=True,
                base_branch=args.base_branch,
                files_found=len(modified_files),
                implementation_files=categorized['implementation_files'],
                test_files=categorized['test_files'],
                config_files=categorized['config_files']
            )
            return 0

        # Read existing references
        existing = read_references_toon(plan_dir)

        # Filter out files that are already tracked
        new_files = {
            'implementation_files': [f for f in categorized['implementation_files']
                                    if f not in existing['implementation_files']],
            'test_files': [f for f in categorized['test_files']
                          if f not in existing['test_files']],
            'config_files': [f for f in categorized['config_files']
                            if f not in existing['config_files']]
        }

        # Update references.toon
        added = update_references_toon(plan_dir, new_files)

        total_added = sum(added.values())

        output_success(
            'collect-modified-files',
            base_branch=args.base_branch,
            files_found=len(modified_files),
            files_added=total_added,
            added_by_category=added,
            implementation_files=new_files['implementation_files'],
            test_files=new_files['test_files'],
            config_files=new_files['config_files']
        )
        return 0

    except Exception as e:
        output_error('collect-modified-files', str(e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
