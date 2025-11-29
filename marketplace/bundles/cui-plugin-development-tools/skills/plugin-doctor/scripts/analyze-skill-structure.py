#!/usr/bin/env python3
"""
analyze-skill-structure.py

Analyzes skill directory structure and validates file references.

Usage:
    python3 analyze-skill-structure.py <skill_dir>

Arguments:
    skill_dir    Path to the skill directory containing SKILL.md

Output: JSON with structure analysis including:
    - skill_md.exists: Whether SKILL.md exists
    - skill_md.yaml_valid: Whether frontmatter is valid YAML
    - standards_files.missing_files: Files referenced but not found
    - standards_files.unreferenced_files: Files existing but not referenced
    - structure_score: Quality score 0-100

Exit codes:
    0 - Success
    1 - Error (missing argument, directory not found)
"""

import argparse
import json
import re
import sys
from pathlib import Path


def extract_frontmatter(content: str) -> tuple[bool, str]:
    """Extract YAML frontmatter from content."""
    if not content.startswith('---'):
        return False, ''

    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if match:
        return True, match.group(1)
    return False, ''


def check_yaml_validity(frontmatter: str) -> bool:
    """Basic YAML validity check."""
    return bool(re.search(r'^[a-z_]*:', frontmatter, re.MULTILINE))


def remove_code_blocks(content: str) -> str:
    """Remove code blocks from content."""
    result = []
    in_codeblock = False

    for line in content.split('\n'):
        if line.startswith('```'):
            in_codeblock = not in_codeblock
            continue
        if not in_codeblock:
            result.append(line)

    return '\n'.join(result)


def extract_references(content: str, skill_dir: Path) -> set[str]:
    """Extract file references from SKILL.md content."""
    references = set()

    # Pattern for direct relative paths like scripts/*.sh, references/*.md, assets/*.*
    # Support nested paths like references/examples/file.md
    pattern = r'([a-zA-Z0-9_-]+:)?(scripts|references|assets)(/[a-zA-Z0-9_.-]+)+\.[a-z]+'
    all_refs = re.findall(pattern, content)

    # Filter out cross-skill references (those with prefix like bundle-name:references/)
    # Keep only local references (no colon prefix)
    for match in all_refs:
        if isinstance(match, tuple):
            # match is (prefix, dir, rest) - check if prefix is empty
            prefix = match[0]
            if not prefix:
                # Reconstruct the full path
                full_match = ''.join(match[1:]) if len(match) > 1 else match[0]
                # Re-extract the full path from content
                pass

    # Simpler approach: find all local references
    local_pattern = r'(scripts|references|assets)(/[a-zA-Z0-9_.-]+)+\.[a-z]+'
    for match in re.finditer(local_pattern, content):
        ref = match.group(0)
        # Skip if it's preceded by a colon (cross-skill reference)
        start = match.start()
        if start > 0 and content[start-1] == ':':
            continue
        references.add(ref)

    # Also detect table-format references like | `script.py` |
    content_no_codeblocks = remove_code_blocks(content)
    table_pattern = r'`(scripts|references|assets)(/[a-zA-Z0-9_.-]+)+\.[a-z]+`'
    for match in re.finditer(table_pattern, content_no_codeblocks):
        ref = match.group(0).strip('`')
        references.add(ref)

    # Also detect backtick references like `analyze-data.sh` in tables (filename only)
    for subdir in ['scripts', 'references', 'assets']:
        subdir_path = skill_dir / subdir
        if subdir_path.is_dir():
            for file_path in subdir_path.iterdir():
                if file_path.is_file():
                    filename = file_path.name
                    # Check if this filename appears in backticks in the content
                    if f'`{filename}`' in content_no_codeblocks:
                        relative_path = f"{subdir}/{filename}"
                        references.add(relative_path)

    return references


def find_existing_files(skill_dir: Path) -> set[str]:
    """Find all files in scripts/, references/, and assets/ directories."""
    existing = set()

    for subdir in ['scripts', 'references', 'assets']:
        subdir_path = skill_dir / subdir
        if subdir_path.is_dir():
            for file_path in subdir_path.rglob('*'):
                if file_path.is_file():
                    relative_path = str(file_path.relative_to(skill_dir))
                    existing.add(relative_path)

    return existing


def calculate_structure_score(skill_exists: bool, yaml_valid: bool,
                              missing_count: int, unreferenced_count: int) -> int:
    """Calculate structure score based on issues."""
    if not skill_exists:
        return 0
    if not yaml_valid:
        return 30

    if missing_count == 0 and unreferenced_count == 0:
        return 100

    # Start at 100 and deduct points
    score = 100

    # Deduct 20 points per missing file (referenced but doesn't exist)
    score -= missing_count * 20

    # Deduct 10 points per unreferenced file (exists but not referenced)
    score -= unreferenced_count * 10

    return max(0, score)


def analyze_skill(skill_dir: Path) -> dict:
    """Analyze skill directory structure."""
    skill_md = skill_dir / 'SKILL.md'

    # Check SKILL.md existence
    skill_exists = skill_md.is_file()
    yaml_valid = False
    missing_files = []
    unreferenced_files = []

    if skill_exists:
        try:
            content = skill_md.read_text(encoding='utf-8', errors='replace')
        except (OSError, IOError):
            content = ''

        # Check YAML frontmatter validity
        frontmatter_present, frontmatter = extract_frontmatter(content)
        if frontmatter_present:
            yaml_valid = check_yaml_validity(frontmatter)

        # Extract references and find existing files
        references = extract_references(content, skill_dir)
        existing = find_existing_files(skill_dir)

        # Content without code blocks for missing file detection
        content_no_codeblocks = remove_code_blocks(content)
        refs_outside_codeblocks = set()
        local_pattern = r'(scripts|references|assets)(/[a-zA-Z0-9_.-]+)+\.[a-z]+'
        for match in re.finditer(local_pattern, content_no_codeblocks):
            ref = match.group(0)
            start = match.start()
            if start > 0 and content_no_codeblocks[start-1] == ':':
                continue
            refs_outside_codeblocks.add(ref)

        # Find missing files (referenced outside code blocks but don't exist)
        for ref in references:
            file_path = skill_dir / ref
            if not file_path.is_file():
                # Only flag if referenced outside code blocks
                if ref in refs_outside_codeblocks:
                    missing_files.append(ref)

        # Find unreferenced files (exist but not referenced)
        for existing_file in existing:
            if existing_file not in references:
                unreferenced_files.append(existing_file)

    # Calculate structure score
    structure_score = calculate_structure_score(
        skill_exists, yaml_valid,
        len(missing_files), len(unreferenced_files)
    )

    return {
        'skill_dir': str(skill_dir),
        'skill_md': {
            'exists': skill_exists,
            'yaml_valid': yaml_valid
        },
        'standards_files': {
            'missing_files': sorted(missing_files),
            'unreferenced_files': sorted(unreferenced_files)
        },
        'structure_score': structure_score
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze skill directory structure and validate file references"
    )
    parser.add_argument(
        'skill_dir',
        help="Path to the skill directory containing SKILL.md"
    )

    args = parser.parse_args()

    skill_dir = Path(args.skill_dir)

    # Validate path
    if not skill_dir.exists():
        print(json.dumps({'error': f'Directory not found: {args.skill_dir}'}), file=sys.stderr)
        return 1

    if not skill_dir.is_dir():
        print(json.dumps({'error': f'Not a directory: {args.skill_dir}'}), file=sys.stderr)
        return 1

    # Analyze skill
    result = analyze_skill(skill_dir)

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
