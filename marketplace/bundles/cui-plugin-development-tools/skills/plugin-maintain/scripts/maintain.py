#!/usr/bin/env python3
"""
Plugin component maintenance tools.

Consolidates:
- update-component.py → update subcommand
- check-duplication.py → check-duplication subcommand
- analyze-component.py → analyze subcommand
- generate-readme.py → readme subcommand

Usage:
    maintain.py update --component <path> --updates <json>
    maintain.py check-duplication --skill-path <path> --content-file <path>
    maintain.py analyze --component <path>
    maintain.py readme --bundle-path <path>
"""

import argparse
import json
import re
import shutil
import sys
from difflib import SequenceMatcher
from pathlib import Path

EXIT_SUCCESS = 0
EXIT_ERROR = 1


# =============================================================================
# Shared Utilities
# =============================================================================

def parse_frontmatter(content: str) -> tuple[dict | None, str]:
    """Parse YAML frontmatter from content. Returns (frontmatter_dict, body)."""
    if not content.startswith('---'):
        return None, content

    # Find closing ---
    lines = content.split('\n')
    end_idx = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        return None, content

    # Parse YAML (simple key: value parsing)
    frontmatter = {}
    for line in lines[1:end_idx]:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip()
            value = value.strip()
            # Detect array syntax
            if value.startswith('[') and value.endswith(']'):
                frontmatter[key] = {'value': value, 'is_array': True}
            else:
                frontmatter[key] = value

    body = '\n'.join(lines[end_idx + 1:])
    return frontmatter, body


def output_json(data: dict) -> None:
    """Output JSON result to stdout."""
    print(json.dumps(data, indent=2))


# =============================================================================
# Update Subcommand
# =============================================================================

def create_backup(path: Path) -> str:
    """Create backup of file."""
    backup_path = path.with_suffix(path.suffix + '.maintain-backup')
    shutil.copy2(path, backup_path)
    return str(backup_path)


def restore_backup(path: Path, backup_path: str):
    """Restore file from backup."""
    shutil.copy2(backup_path, path)


def apply_frontmatter_update(content: str, field: str, value: str) -> str:
    """Update or add a frontmatter field."""
    lines = content.split('\n')

    if not content.startswith('---'):
        # No frontmatter, create it
        new_fm = f'---\n{field}: {value}\n---\n\n'
        return new_fm + content

    # Find frontmatter end
    end_idx = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break

    if end_idx == -1:
        return content  # Malformed, don't modify

    # Check if field exists
    field_found = False
    for i in range(1, end_idx):
        if lines[i].startswith(f'{field}:'):
            lines[i] = f'{field}: {value}'
            field_found = True
            break

    if not field_found:
        # Insert before closing ---
        lines.insert(end_idx, f'{field}: {value}')

    return '\n'.join(lines)


def apply_section_update(content: str, section: str, new_content: str) -> str:
    """Update or add a section."""
    # Find section header
    pattern = rf'^(#{1,4})\s+{re.escape(section)}\s*$'
    match = re.search(pattern, content, re.MULTILINE | re.IGNORECASE)

    if match:
        # Find end of section (next header of same or higher level)
        header_level = len(match.group(1))
        start = match.end()

        # Find next section of same or higher level
        next_pattern = rf'^#{{{1},{header_level}}}\s+'
        next_match = re.search(next_pattern, content[start:], re.MULTILINE)

        if next_match:
            end = start + next_match.start()
            content = content[:start] + '\n\n' + new_content + '\n\n' + content[end:]
        else:
            # Section goes to end
            content = content[:start] + '\n\n' + new_content + '\n'
    else:
        # Add new section at end
        content = content.rstrip() + f'\n\n## {section}\n\n{new_content}\n'

    return content


def apply_updates(component_path: str, updates: list) -> dict:
    """Apply a list of updates to component."""
    path = Path(component_path)

    if not path.exists():
        return {
            'error': f'File not found: {component_path}',
            'component_path': component_path,
            'success': False
        }

    # Create backup
    backup_path = create_backup(path)

    try:
        content = path.read_text()
        updates_applied = 0
        changes = []

        for update in updates:
            update_type = update.get('type', '')

            if update_type == 'frontmatter':
                field = update.get('field', '')
                value = update.get('value', '')
                if field:
                    content = apply_frontmatter_update(content, field, value)
                    changes.append(f'Updated frontmatter field: {field}')
                    updates_applied += 1

            elif update_type == 'section':
                section = update.get('section', '')
                new_content = update.get('content', '')
                if section:
                    content = apply_section_update(content, section, new_content)
                    changes.append(f'Updated section: {section}')
                    updates_applied += 1

            elif update_type == 'replace':
                old_text = update.get('old', '')
                new_text = update.get('new', '')
                if old_text and old_text in content:
                    content = content.replace(old_text, new_text, 1)
                    changes.append(f'Replaced text: {old_text[:30]}...')
                    updates_applied += 1

            elif update_type == 'append':
                text = update.get('text', '')
                if text:
                    content = content.rstrip() + '\n\n' + text + '\n'
                    changes.append('Appended content')
                    updates_applied += 1

        # Write updated content
        path.write_text(content)

        return {
            'component_path': component_path,
            'updates_applied': updates_applied,
            'success': True,
            'changes': changes,
            'backup_created': backup_path,
            'validation_errors': []
        }

    except Exception as e:
        # Restore backup on error
        restore_backup(path, backup_path)
        return {
            'component_path': component_path,
            'success': False,
            'error': str(e),
            'backup_restored': True
        }


def cmd_update(args) -> int:
    """Handle update subcommand."""
    # Read updates from stdin or --updates argument
    if args.updates:
        try:
            input_data = json.loads(args.updates)
        except json.JSONDecodeError as e:
            output_json({'error': f'Invalid JSON in --updates: {e}'})
            return EXIT_ERROR
    else:
        try:
            input_data = json.loads(sys.stdin.read())
        except json.JSONDecodeError as e:
            output_json({'error': f'Invalid JSON input: {e}'})
            return EXIT_ERROR

    updates = input_data.get('updates', [])
    result = apply_updates(args.component, updates)
    output_json(result)
    return EXIT_SUCCESS if result.get('success') else EXIT_ERROR


# =============================================================================
# Check-Duplication Subcommand
# =============================================================================

def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    # Remove markdown formatting
    text = re.sub(r'[#*`_\[\]]', '', text)
    # Normalize whitespace
    text = ' '.join(text.lower().split())
    return text


def extract_sections(content: str) -> dict[str, str]:
    """Extract sections from markdown content."""
    sections = {}
    current_section = 'intro'
    current_content = []

    for line in content.split('\n'):
        if line.startswith('#'):
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            # Extract section name
            current_section = re.sub(r'^#+\s*', '', line).strip().lower()
            current_content = []
        else:
            current_content.append(line)

    if current_content:
        sections[current_section] = '\n'.join(current_content)

    return sections


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity ratio between two texts."""
    normalized1 = normalize_text(text1)
    normalized2 = normalize_text(text2)

    if not normalized1 or not normalized2:
        return 0.0

    return SequenceMatcher(None, normalized1, normalized2).ratio()


def find_duplicate_sections(new_sections: dict, existing_sections: dict) -> list:
    """Find sections that have high overlap."""
    duplicates = []

    for new_name, new_content in new_sections.items():
        for existing_name, existing_content in existing_sections.items():
            similarity = calculate_similarity(new_content, existing_content)
            if similarity > 0.6:  # 60% similarity threshold
                duplicates.append({
                    'new_section': new_name,
                    'existing_section': existing_name,
                    'similarity': round(similarity * 100, 1)
                })

    return duplicates


def check_duplication(skill_path: str, content_file: str) -> dict:
    """Main duplication checking function."""
    skill_dir = Path(skill_path)
    content_path = Path(content_file)

    # Validate inputs
    if not skill_dir.exists():
        return {
            'error': f'Skill directory not found: {skill_path}',
            'skill_path': skill_path
        }

    if not content_path.exists():
        return {
            'error': f'Content file not found: {content_file}',
            'new_content_file': content_file
        }

    # Read new content
    new_content = content_path.read_text()
    new_sections = extract_sections(new_content)
    new_normalized = normalize_text(new_content)

    # Check for empty content
    if not new_normalized.strip():
        return {
            'skill_path': skill_path,
            'new_content_file': content_file,
            'duplication_detected': False,
            'duplication_percentage': 0,
            'duplicate_files': [],
            'recommendation': 'proceed',
            'note': 'Content file is empty or minimal'
        }

    # Find references directory
    refs_dir = skill_dir / 'references'
    if not refs_dir.exists():
        refs_dir = skill_dir / 'standards'  # Try standards directory

    if not refs_dir.exists():
        return {
            'skill_path': skill_path,
            'new_content_file': content_file,
            'duplication_detected': False,
            'duplication_percentage': 0,
            'duplicate_files': [],
            'recommendation': 'proceed',
            'note': 'No existing references directory found'
        }

    # Scan existing references
    duplicate_files = []
    max_overlap = 0

    for ref_file in refs_dir.glob('*.md'):
        existing_content = ref_file.read_text()

        # Overall similarity
        overall_similarity = calculate_similarity(new_content, existing_content)

        if overall_similarity > 0.3:  # 30% overall threshold
            existing_sections = extract_sections(existing_content)
            duplicate_sections = find_duplicate_sections(new_sections, existing_sections)

            if duplicate_sections:
                overlap_pct = round(overall_similarity * 100, 1)
                duplicate_files.append({
                    'existing_file': str(ref_file.relative_to(skill_dir)),
                    'overlap_percentage': overlap_pct,
                    'duplicate_sections': [d['existing_section'] for d in duplicate_sections[:5]]
                })
                max_overlap = max(max_overlap, overlap_pct)

    # Determine recommendation
    duplication_detected = max_overlap > 30
    if max_overlap >= 70:
        recommendation = 'skip'
    elif max_overlap >= 40:
        recommendation = 'consolidate'
    else:
        recommendation = 'proceed'

    return {
        'skill_path': skill_path,
        'new_content_file': content_file,
        'duplication_detected': duplication_detected,
        'duplication_percentage': max_overlap,
        'duplicate_files': sorted(duplicate_files, key=lambda x: x['overlap_percentage'], reverse=True),
        'recommendation': recommendation
    }


def cmd_check_duplication(args) -> int:
    """Handle check-duplication subcommand."""
    result = check_duplication(args.skill_path, args.content_file)
    output_json(result)
    return EXIT_SUCCESS if 'error' not in result else EXIT_ERROR


# =============================================================================
# Analyze Subcommand
# =============================================================================

def detect_component_type(path: Path) -> str:
    """Detect component type from path."""
    path_str = str(path)
    if '/agents/' in path_str:
        return 'agent'
    elif '/commands/' in path_str:
        return 'command'
    elif '/skills/' in path_str or path.name == 'SKILL.md':
        return 'skill'
    return 'unknown'


def check_sections(body: str) -> dict:
    """Check for required and recommended sections."""
    missing_sections = []

    # Count markdown headers
    headers = re.findall(r'^#{1,4}\s+(.+)$', body, re.MULTILINE)
    sections_found = [h.lower() for h in headers]

    # Recommended sections for agents/commands
    recommended = ['purpose', 'workflow', 'examples', 'error handling', 'critical rules']
    for section in recommended:
        if not any(section in s for s in sections_found):
            missing_sections.append(section)

    return {
        'sections_found': len(headers),
        'missing_sections': missing_sections
    }


def check_bloat(body: str, total_lines: int) -> list:
    """Check for bloat indicators."""
    issues = []

    if total_lines > 800:
        issues.append({
            'type': 'bloat',
            'severity': 'high',
            'message': f'Component has {total_lines} lines (>800 threshold)',
            'location': 'entire file'
        })
    elif total_lines > 500:
        issues.append({
            'type': 'bloat',
            'severity': 'medium',
            'message': f'Component has {total_lines} lines (approaching 800 threshold)',
            'location': 'entire file'
        })

    # Check for duplicate content patterns
    paragraphs = re.split(r'\n\n+', body)
    seen_content = set()
    for i, para in enumerate(paragraphs):
        para_clean = ' '.join(para.split()).lower()
        if len(para_clean) > 100:  # Only check substantial paragraphs
            if para_clean in seen_content:
                issues.append({
                    'type': 'duplicate-content',
                    'severity': 'medium',
                    'message': 'Duplicate paragraph detected',
                    'location': f'paragraph {i+1}'
                })
            seen_content.add(para_clean)

    return issues


def check_tool_compliance(frontmatter: dict | None, body: str) -> list:
    """Check for tool compliance issues."""
    issues = []

    if frontmatter is None:
        return issues

    tools_raw = frontmatter.get('tools', '')

    # Check for array syntax
    if isinstance(tools_raw, dict) and tools_raw.get('is_array'):
        issues.append({
            'type': 'tool-compliance',
            'severity': 'medium',
            'message': 'Tools use array syntax instead of comma-separated',
            'location': 'frontmatter'
        })
        tools_str = tools_raw.get('value', '')[1:-1]  # Remove []
    else:
        tools_str = str(tools_raw)

    tools = [t.strip() for t in tools_str.split(',') if t.strip()]

    # Rule 6: Agents should not use Task tool
    if 'Task' in tools:
        issues.append({
            'type': 'rule-6-violation',
            'severity': 'high',
            'message': 'Agent declares Task tool (Rule 6 violation)',
            'location': 'frontmatter tools'
        })

    return issues


def calculate_quality_score(frontmatter: dict | None, body: str, issues: list) -> int:
    """Calculate quality score 0-100."""
    score = 100

    # No frontmatter is critical
    if frontmatter is None:
        score -= 30
    else:
        # Missing required fields
        if 'name' not in frontmatter:
            score -= 10
        if 'description' not in frontmatter:
            score -= 10

    # Deduct for issues
    for issue in issues:
        if issue['severity'] == 'high':
            score -= 15
        elif issue['severity'] == 'medium':
            score -= 8
        elif issue['severity'] == 'low':
            score -= 3

    return max(0, min(100, score))


def generate_suggestions(frontmatter: dict | None, body: str, issues: list, section_info: dict) -> list:
    """Generate improvement suggestions."""
    suggestions = []

    if frontmatter is None:
        suggestions.append('Add YAML frontmatter with name, description, and tools fields')

    for section in section_info.get('missing_sections', []):
        suggestions.append(f'Add missing {section} section')

    for issue in issues:
        if issue['type'] == 'bloat':
            suggestions.append('Consider splitting into smaller components or extracting to skill')
        elif issue['type'] == 'rule-6-violation':
            suggestions.append('Remove Task tool from agent - agents should be self-contained')
        elif issue['type'] == 'duplicate-content':
            suggestions.append('Remove duplicate content to reduce bloat')

    return list(set(suggestions))  # Deduplicate


def analyze_component(component_path: str) -> dict:
    """Main analysis function."""
    path = Path(component_path)

    if not path.exists():
        return {
            'error': f'File not found: {component_path}',
            'component_path': component_path
        }

    content = path.read_text()
    lines = content.split('\n')
    total_lines = len(lines)

    frontmatter, body = parse_frontmatter(content)
    component_type = detect_component_type(path)

    # Calculate frontmatter lines
    fm_lines = 0
    if frontmatter is not None:
        for i, line in enumerate(lines):
            if i > 0 and line.strip() == '---':
                fm_lines = i + 1
                break

    # Perform checks
    issues = []

    if frontmatter is None:
        issues.append({
            'type': 'missing-frontmatter',
            'severity': 'high',
            'message': 'Component is missing YAML frontmatter',
            'location': 'file start'
        })

    section_info = check_sections(body)
    issues.extend(check_bloat(body, total_lines))
    issues.extend(check_tool_compliance(frontmatter, body))

    quality_score = calculate_quality_score(frontmatter, body, issues)
    suggestions = generate_suggestions(frontmatter, body, issues, section_info)

    return {
        'component_path': component_path,
        'component_type': component_type,
        'quality_score': quality_score,
        'issues': issues,
        'suggestions': suggestions,
        'stats': {
            'total_lines': total_lines,
            'frontmatter_lines': fm_lines,
            'body_lines': total_lines - fm_lines,
            'sections': section_info['sections_found']
        }
    }


def cmd_analyze(args) -> int:
    """Handle analyze subcommand."""
    result = analyze_component(args.component)
    output_json(result)
    return EXIT_SUCCESS if 'error' not in result else EXIT_ERROR


# =============================================================================
# Readme Subcommand
# =============================================================================

def extract_description(file_path: Path) -> str:
    """Extract description from YAML frontmatter."""
    if not file_path.exists():
        return 'No description'

    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError):
        return 'No description'

    # Check for YAML frontmatter
    if not content.startswith('---'):
        return 'No description'

    # Extract frontmatter
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return 'No description'

    frontmatter = match.group(1)

    # Extract description field
    for line in frontmatter.split('\n'):
        if line.startswith('description:'):
            desc = line[len('description:'):].strip()
            return desc if desc else 'No description'

    return 'No description'


def get_bundle_name(bundle_path: Path) -> str:
    """Extract bundle name from plugin.json."""
    # Check both locations: .claude-plugin/plugin.json (standard) and plugin.json (legacy)
    plugin_json = bundle_path / '.claude-plugin' / 'plugin.json'
    if not plugin_json.exists():
        plugin_json = bundle_path / 'plugin.json'

    if not plugin_json.exists():
        return 'Unknown'

    try:
        with open(plugin_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('name', 'Unknown')
    except (OSError, IOError, json.JSONDecodeError):
        return 'Unknown'


def discover_commands(bundle_path: Path) -> list[dict]:
    """Discover command .md files in bundle/commands/."""
    commands_dir = bundle_path / 'commands'
    if not commands_dir.is_dir():
        return []

    commands = []
    for cmd_file in sorted(commands_dir.glob('*.md')):
        if cmd_file.is_file():
            commands.append({
                'name': cmd_file.stem,
                'description': extract_description(cmd_file)
            })
    return commands


def discover_agents(bundle_path: Path) -> list[dict]:
    """Discover agent .md files in bundle/agents/."""
    agents_dir = bundle_path / 'agents'
    if not agents_dir.is_dir():
        return []

    agents = []
    for agent_file in sorted(agents_dir.glob('*.md')):
        if agent_file.is_file():
            agents.append({
                'name': agent_file.stem,
                'description': extract_description(agent_file)
            })
    return agents


def discover_skills(bundle_path: Path) -> list[dict]:
    """Discover skill directories containing SKILL.md."""
    skills_dir = bundle_path / 'skills'
    if not skills_dir.is_dir():
        return []

    skills = []
    for skill_md in sorted(skills_dir.glob('*/SKILL.md')):
        skill_dir = skill_md.parent
        skills.append({
            'name': skill_dir.name,
            'description': extract_description(skill_md)
        })
    return skills


def generate_readme_content(bundle_name: str, commands: list[dict],
                           agents: list[dict], skills: list[dict]) -> str:
    """Generate README markdown content."""
    lines = [f'# {bundle_name}', '']

    # Commands section
    if commands:
        lines.extend(['## Commands', ''])
        for cmd in commands:
            lines.append(f"- **{cmd['name']}** - {cmd['description']}")
        lines.append('')

    # Agents section
    if agents:
        lines.extend(['## Agents', ''])
        for agent in agents:
            lines.append(f"- **{agent['name']}** - {agent['description']}")
        lines.append('')

    # Skills section
    if skills:
        lines.extend(['## Skills', ''])
        for skill in skills:
            lines.append(f"- **{skill['name']}** - {skill['description']}")
        lines.append('')

    # Installation section
    lines.extend([
        '## Installation',
        '',
        'Add to your Claude Code settings or install via marketplace.'
    ])

    return '\n'.join(lines)


def cmd_readme(args) -> int:
    """Handle readme subcommand."""
    bundle_path = Path(args.bundle_path)

    # Validate path
    if not bundle_path.exists():
        output_json({'error': f'Bundle directory not found: {args.bundle_path}'})
        return EXIT_ERROR

    if not bundle_path.is_dir():
        output_json({'error': f'Not a directory: {args.bundle_path}'})
        return EXIT_ERROR

    # Check for plugin.json (both standard and legacy locations)
    plugin_json = bundle_path / '.claude-plugin' / 'plugin.json'
    if not plugin_json.exists():
        plugin_json = bundle_path / 'plugin.json'
    if not plugin_json.exists():
        output_json({'error': f'Missing plugin.json in bundle: {args.bundle_path}'})
        return EXIT_ERROR

    # Get bundle name
    bundle_name = get_bundle_name(bundle_path)

    # Discover components
    commands = discover_commands(bundle_path)
    agents = discover_agents(bundle_path)
    skills = discover_skills(bundle_path)

    # Generate README content
    readme_content = generate_readme_content(bundle_name, commands, agents, skills)

    # Build result
    result = {
        'bundle_path': str(bundle_path),
        'bundle_name': bundle_name,
        'readme_generated': True,
        'components': {
            'commands': len(commands),
            'agents': len(agents),
            'skills': len(skills)
        },
        'readme_content': readme_content,
        'commands': commands,
        'agents': agents,
        'skills': skills
    }

    output_json(result)
    return EXIT_SUCCESS


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Plugin component maintenance tools',
        epilog='''
Examples:
  # Apply updates to a component
  maintain.py update --component agent.md --updates '{"updates": [...]}'

  # Check for duplicate knowledge
  maintain.py check-duplication --skill-path ./skills/my-skill --content-file ./new.md

  # Analyze a component for quality
  maintain.py analyze --component ./agents/my-agent.md

  # Generate README for a bundle
  maintain.py readme --bundle-path ./marketplace/bundles/my-bundle
''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Operation to perform')

    # Update subcommand
    p_update = subparsers.add_parser('update', help='Apply updates to a component')
    p_update.add_argument('--component', required=True, help='Path to component file')
    p_update.add_argument('--updates', help='JSON updates (or read from stdin)')

    # Check-duplication subcommand
    p_dup = subparsers.add_parser('check-duplication', help='Check for duplicate knowledge')
    p_dup.add_argument('--skill-path', required=True, help='Path to skill directory')
    p_dup.add_argument('--content-file', required=True, help='Path to new content file')

    # Analyze subcommand
    p_analyze = subparsers.add_parser('analyze', help='Analyze component for quality')
    p_analyze.add_argument('--component', required=True, help='Path to component file')

    # Readme subcommand
    p_readme = subparsers.add_parser('readme', help='Generate README for a bundle')
    p_readme.add_argument('--bundle-path', required=True, help='Path to bundle directory')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return EXIT_ERROR

    if args.command == 'update':
        return cmd_update(args)
    elif args.command == 'check-duplication':
        return cmd_check_duplication(args)
    elif args.command == 'analyze':
        return cmd_analyze(args)
    elif args.command == 'readme':
        return cmd_readme(args)
    else:
        parser.print_help()
        return EXIT_ERROR


if __name__ == '__main__':
    sys.exit(main())
