#!/usr/bin/env python3
"""
analyze.py - Plugin component analysis tools.

Consolidated from:
- analyze-markdown-file.py → markdown subcommand
- analyze-skill-structure.py → structure subcommand
- analyze-tool-coverage.py → coverage subcommand
- analyze-cross-file-content.py → cross-file subcommand

Provides comprehensive analysis for plugin components.

Output: JSON to stdout.
"""

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Set, Tuple


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


def check_yaml_validity(frontmatter: str) -> bool:
    """Basic YAML validity check."""
    return bool(re.search(r'^[a-z_]*:', frontmatter, re.MULTILINE))


def count_lines(file_path: Path) -> int:
    """Count lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return sum(1 for _ in f)
    except (OSError, IOError):
        return 0


def detect_component_type(file_path: str) -> str:
    """Detect component type from file path."""
    if '/commands/' in file_path:
        return 'command'
    elif '/agents/' in file_path:
        return 'agent'
    elif '/skills/' in file_path:
        return 'skill'
    return 'unknown'


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


# =============================================================================
# Markdown Analysis (from analyze-markdown-file.py)
# =============================================================================

def check_frontmatter_fields(frontmatter: str) -> dict:
    """Check required fields in frontmatter."""
    has_name = bool(re.search(r'^name:', frontmatter, re.MULTILINE))
    has_desc = bool(re.search(r'^description:', frontmatter, re.MULTILINE))

    has_tools = False
    tools_field_type = 'none'

    if re.search(r'^tools:', frontmatter, re.MULTILINE):
        has_tools = True
        tools_field_type = 'tools'
    elif re.search(r'^allowed-tools:', frontmatter, re.MULTILINE):
        has_tools = True
        tools_field_type = 'allowed-tools'

    return {
        'name': {'present': has_name},
        'description': {'present': has_desc},
        'tools': {'present': has_tools, 'field_type': tools_field_type}
    }


def check_continuous_improvement(content: str, component_type: str) -> dict:
    """Check CONTINUOUS IMPROVEMENT RULE presence and pattern."""
    ci_present = bool(re.search(r'CONTINUOUS IMPROVEMENT', content, re.IGNORECASE))
    ci_pattern = 'none'
    pattern_22_violation = False

    if ci_present:
        if re.search(r'/plugin-update-command|/plugin-update-agent', content):
            ci_pattern = 'self-update'
        elif re.search(r'REPORT.*improvement|report.*to.*caller', content, re.IGNORECASE):
            ci_pattern = 'caller-reporting'

        if component_type == 'agent' and ci_pattern == 'self-update':
            pattern_22_violation = True

    return {
        'present': ci_present,
        'format': {
            'pattern': ci_pattern,
            'pattern_22_violation': pattern_22_violation
        }
    }


def get_bloat_classification(line_count: int, component_type: str) -> str:
    """Get bloat classification based on line count and component type."""
    if component_type == 'command':
        if line_count > 200:
            return 'CRITICAL'
        elif line_count > 150:
            return 'BLOATED'
        elif line_count > 100:
            return 'LARGE'
    elif component_type == 'skill':
        if line_count > 1200:
            return 'CRITICAL'
        elif line_count > 800:
            return 'BLOATED'
        elif line_count > 400:
            return 'LARGE'
    else:
        if line_count > 800:
            return 'CRITICAL'
        elif line_count > 500:
            return 'BLOATED'
        elif line_count > 300:
            return 'LARGE'

    return 'NORMAL'


def check_execution_patterns(content: str) -> dict:
    """Check for execution patterns in content."""
    return {
        'has_execution_mode': bool(re.search(r'EXECUTION MODE', content, re.IGNORECASE)),
        'has_workflow_tree': bool(re.search(r'Workflow Decision Tree', content, re.IGNORECASE)),
        'mandatory_marker_count': len(re.findall(r'\*\*MANDATORY\*\*', content)),
        'has_handoff_rules': bool(re.search(r'CRITICAL HANDOFF', content, re.IGNORECASE))
    }


def check_rule_violations(content: str, frontmatter: str, component_type: str,
                          has_tools: bool, file_path: str) -> dict:
    """Check for rule violations."""
    rule_6_violation = False
    if component_type == 'agent' and has_tools:
        if re.search(r'^  - Task$|Task,|Task$', frontmatter, re.MULTILINE):
            rule_6_violation = True

    rule_7_violation = False
    if re.search(r'mvn |maven |./mvnw ', content):
        if 'builder-maven' not in file_path:
            pattern = r'^Bash:.*mvn|^Bash:.*maven|^Bash:.*\./mvnw|`.*mvn |`.*\./mvnw |^\s+mvn |^\s+\./mvnw '
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                if 'Rule 7' not in match and 'should use' not in match and 'instead of' not in match:
                    rule_7_violation = True
                    break

    rule_8_violation = False
    if re.search(r'python3 .*/scripts/|bash .*/scripts/|\{[^}]+\}/scripts/', content):
        if not re.search(r'Skill:.*script-runner', content):
            rule_8_violation = True

    return {
        'rule_6_violation': rule_6_violation,
        'rule_7_violation': rule_7_violation,
        'rule_8_violation': rule_8_violation
    }


def check_forbidden_metadata(content: str) -> tuple[bool, str]:
    """Check for forbidden metadata sections."""
    forbidden_pattern = r'^## (Version|Version History|License|Changelog|Change Log|Author|Revision History)$'
    matches = re.findall(forbidden_pattern, content, re.MULTILINE)

    if matches:
        return True, ','.join(matches)
    return False, ''


def analyze_markdown_file(file_path: Path, component_type: str) -> dict:
    """Analyze markdown file and return results."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError) as e:
        return {'error': f'Failed to read file: {e}'}

    line_count = content.count('\n') + (1 if content and not content.endswith('\n') else 0)

    if component_type == 'auto':
        component_type = detect_component_type(str(file_path))

    frontmatter_present, frontmatter = extract_frontmatter(content)
    yaml_valid = check_yaml_validity(frontmatter) if frontmatter_present else False
    required_fields = check_frontmatter_fields(frontmatter) if frontmatter_present else {
        'name': {'present': False},
        'description': {'present': False},
        'tools': {'present': False, 'field_type': 'none'}
    }

    section_count = len(re.findall(r'^## ', content, re.MULTILINE))
    has_param_section = bool(re.search(r'^## PARAMETERS|^### Parameters', content, re.MULTILINE | re.IGNORECASE))
    ci_rule = check_continuous_improvement(content, component_type)
    bloat_class = get_bloat_classification(line_count, component_type)
    exec_patterns = check_execution_patterns(content)
    rules = check_rule_violations(
        content, frontmatter, component_type,
        required_fields['tools']['present'], str(file_path)
    )
    has_forbidden, forbidden_sections = check_forbidden_metadata(content)

    return {
        'file_path': str(file_path),
        'file_type': {'type': component_type},
        'metrics': {'line_count': line_count},
        'frontmatter': {
            'present': frontmatter_present,
            'yaml_valid': yaml_valid,
            'required_fields': required_fields
        },
        'structure': {'section_count': section_count},
        'parameters': {'has_section': has_param_section},
        'continuous_improvement_rule': ci_rule,
        'bloat': {'classification': bloat_class},
        'execution_patterns': exec_patterns,
        'rules': rules,
        'quality': {
            'has_forbidden_metadata': has_forbidden,
            'forbidden_sections': forbidden_sections
        }
    }


def cmd_markdown(args) -> int:
    """Analyze markdown file structure and compliance."""
    file_path = Path(args.file)

    if not file_path.exists():
        print(json.dumps({'error': f'File not found: {args.file}'}), file=sys.stderr)
        return 1

    if not file_path.is_file():
        print(json.dumps({'error': f'Not a file: {args.file}'}), file=sys.stderr)
        return 1

    result = analyze_markdown_file(file_path, args.type)

    if 'error' in result:
        print(json.dumps(result), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


# =============================================================================
# Structure Analysis (from analyze-skill-structure.py)
# =============================================================================

def extract_skill_references(content: str, skill_dir: Path) -> set[str]:
    """Extract file references from SKILL.md content."""
    references = set()

    local_pattern = r'(scripts|references|assets)(/[a-zA-Z0-9_.-]+)+\.[a-z]+'
    for match in re.finditer(local_pattern, content):
        ref = match.group(0)
        start = match.start()
        if start > 0 and content[start-1] == ':':
            continue
        references.add(ref)

    content_no_codeblocks = remove_code_blocks(content)
    table_pattern = r'`(scripts|references|assets)(/[a-zA-Z0-9_.-]+)+\.[a-z]+`'
    for match in re.finditer(table_pattern, content_no_codeblocks):
        ref = match.group(0).strip('`')
        references.add(ref)

    for subdir in ['scripts', 'references', 'assets']:
        subdir_path = skill_dir / subdir
        if subdir_path.is_dir():
            for file_path in subdir_path.iterdir():
                if file_path.is_file():
                    filename = file_path.name
                    if f'`{filename}`' in content_no_codeblocks:
                        references.add(f"{subdir}/{filename}")

    return references


def find_existing_files(skill_dir: Path) -> set[str]:
    """Find all files in scripts/, references/, and assets/ directories."""
    existing = set()

    for subdir in ['scripts', 'references', 'assets']:
        subdir_path = skill_dir / subdir
        if subdir_path.is_dir():
            for file_path in subdir_path.rglob('*'):
                if file_path.is_file():
                    # Skip files in __pycache__ directories or with excluded extensions
                    if '__pycache__' in file_path.parts:
                        continue
                    if file_path.suffix in {'.pyc', '.pyo', '.class', '.o'}:
                        continue
                    existing.add(str(file_path.relative_to(skill_dir)))

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

    score = 100
    score -= missing_count * 20
    score -= unreferenced_count * 10

    return max(0, score)


def analyze_skill_structure(skill_dir: Path) -> dict:
    """Analyze skill directory structure."""
    skill_md = skill_dir / 'SKILL.md'

    skill_exists = skill_md.is_file()
    yaml_valid = False
    missing_files = []
    unreferenced_files = []

    if skill_exists:
        try:
            content = skill_md.read_text(encoding='utf-8', errors='replace')
        except (OSError, IOError):
            content = ''

        frontmatter_present, frontmatter = extract_frontmatter(content)
        if frontmatter_present:
            yaml_valid = check_yaml_validity(frontmatter)

        references = extract_skill_references(content, skill_dir)
        existing = find_existing_files(skill_dir)

        content_no_codeblocks = remove_code_blocks(content)
        refs_outside_codeblocks = set()
        local_pattern = r'(scripts|references|assets)(/[a-zA-Z0-9_.-]+)+\.[a-z]+'
        for match in re.finditer(local_pattern, content_no_codeblocks):
            ref = match.group(0)
            start = match.start()
            if start > 0 and content_no_codeblocks[start-1] == ':':
                continue
            refs_outside_codeblocks.add(ref)

        for ref in references:
            file_path = skill_dir / ref
            if not file_path.is_file():
                if ref in refs_outside_codeblocks:
                    missing_files.append(ref)

        for existing_file in existing:
            if existing_file not in references:
                unreferenced_files.append(existing_file)

    structure_score = calculate_structure_score(
        skill_exists, yaml_valid,
        len(missing_files), len(unreferenced_files)
    )

    return {
        'skill_dir': str(skill_dir),
        'skill_md': {'exists': skill_exists, 'yaml_valid': yaml_valid},
        'standards_files': {
            'missing_files': sorted(missing_files),
            'unreferenced_files': sorted(unreferenced_files)
        },
        'structure_score': structure_score
    }


def cmd_structure(args) -> int:
    """Analyze skill directory structure."""
    skill_dir = Path(args.directory)

    if not skill_dir.exists():
        print(json.dumps({'error': f'Directory not found: {args.directory}'}), file=sys.stderr)
        return 1

    if not skill_dir.is_dir():
        print(json.dumps({'error': f'Not a directory: {args.directory}'}), file=sys.stderr)
        return 1

    result = analyze_skill_structure(skill_dir)
    print(json.dumps(result, indent=2))
    return 0


# =============================================================================
# Tool Coverage Analysis (from analyze-tool-coverage.py)
# =============================================================================

def extract_content_after_frontmatter(content: str) -> str:
    """Extract content after frontmatter."""
    match = re.match(r'^---\s*\n.*?\n---\s*\n?(.*)', content, re.DOTALL)
    if match:
        return match.group(1)
    return content


def parse_declared_tools(frontmatter: str) -> list[str]:
    """Parse tools from frontmatter.

    Handles both 'tools:' and 'allowed-tools:' field names,
    and both inline (comma-separated) and YAML list (- item) formats.
    """
    # Try both field names
    # Use [ \t]* instead of \s* to avoid matching newlines (which would cross lines)
    tools_match = re.search(r'^(?:tools|allowed-tools):[ \t]*(.*)$', frontmatter, re.MULTILINE)
    if not tools_match:
        return []

    tools_line = tools_match.group(1).strip()

    # If inline format (tools: Read, Write, Edit)
    if tools_line:
        return [t.strip() for t in tools_line.replace(',', ' ').split() if t.strip()]

    # Otherwise check for YAML list format (- Read\n- Write)
    # Find all lines after tools: that start with -
    lines = frontmatter.split('\n')
    tools = []
    in_tools_section = False
    for line in lines:
        if re.match(r'^(?:tools|allowed-tools):', line):
            in_tools_section = True
            continue
        if in_tools_section:
            list_match = re.match(r'^\s+-\s*(.+)$', line)
            if list_match:
                tools.append(list_match.group(1).strip())
            elif line.strip() and not line.startswith(' '):
                # New field started, stop parsing
                break
    return tools


def check_tool_usage(content: str, tool: str) -> bool:
    """Check if a tool is referenced in content."""
    return bool(re.search(re.escape(tool), content, re.IGNORECASE))


def find_missing_tools(content: str, declared_tools: list[str]) -> list[str]:
    """Find common tools used but not declared."""
    common_tools = [
        'Read', 'Write', 'Edit', 'Glob', 'Grep', 'Bash',
        'WebFetch', 'WebSearch', 'AskUserQuestion', 'TodoWrite',
        'Skill', 'Task', 'SlashCommand'
    ]

    missing = []
    declared_lower = [t.lower() for t in declared_tools]

    for tool in common_tools:
        if check_tool_usage(content, tool) and tool.lower() not in declared_lower:
            missing.append(tool)

    return missing


def calculate_fit_score(used_count: int, declared_count: int,
                        missing_count: int, unused_count: int) -> float:
    """Calculate tool fit score."""
    if declared_count == 0:
        return 0.0

    if missing_count == 0 and unused_count == 0:
        return 100.0

    if missing_count == 0:
        return (used_count / declared_count) * 100

    total_needed = used_count + missing_count
    if total_needed == 0:
        return 0.0
    return (used_count / total_needed) * 100


def get_rating(score: float) -> str:
    """Get rating based on score."""
    if score >= 90:
        return 'Excellent'
    elif score >= 70:
        return 'Good'
    elif score >= 50:
        return 'Needs improvement'
    return 'Poor'


def find_maven_calls(content: str) -> list[dict]:
    """Find Maven call patterns in content."""
    maven_calls = []
    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        if re.search(r'Bash.*mvn|Bash.*./mvnw|Bash.*maven', line, re.IGNORECASE):
            maven_calls.append({'line': i, 'text': line.strip()})

    return maven_calls


def find_backup_patterns(content: str) -> list[dict]:
    """Find backup file patterns in content."""
    backup_patterns = []
    lines = content.split('\n')

    for i, line in enumerate(lines, 1):
        if re.search(r'\.backup|\.bak|\.old|\.orig', line):
            backup_patterns.append({'line': i, 'pattern': line.strip()})

    return backup_patterns


def analyze_tool_coverage(file_path: Path) -> dict:
    """Analyze tool coverage in file."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError) as e:
        return {'error': f'Failed to read file: {e}'}

    frontmatter_present, frontmatter = extract_frontmatter(content)
    if not frontmatter_present:
        return {'error': 'No frontmatter found'}

    declared_tools = parse_declared_tools(frontmatter)
    declared_count = len(declared_tools)

    body_content = extract_content_after_frontmatter(content)

    used_tools = []
    unused_tools = []

    for tool in declared_tools:
        if check_tool_usage(body_content, tool):
            used_tools.append(tool)
        else:
            unused_tools.append(tool)

    used_count = len(used_tools)
    unused_count = len(unused_tools)

    missing_tools = find_missing_tools(body_content, declared_tools)
    missing_count = len(missing_tools)

    tool_fit_score = calculate_fit_score(used_count, declared_count, missing_count, unused_count)
    rating = get_rating(tool_fit_score)

    has_task_tool = 'Task' in declared_tools or 'task' in [t.lower() for t in declared_tools]
    has_task_calls = bool(re.search(r'Task tool|invoke.*Task|subagent_type', body_content, re.IGNORECASE))
    maven_calls = find_maven_calls(body_content)
    backup_patterns = find_backup_patterns(body_content)

    return {
        'file_path': str(file_path),
        'tool_coverage': {
            'declared_count': declared_count,
            'used_count': used_count,
            'missing_count': missing_count,
            'unused_count': unused_count,
            'tool_fit_score': round(tool_fit_score, 1),
            'rating': rating,
            'missing_tools': missing_tools,
            'unused_tools': unused_tools
        },
        'critical_violations': {
            'has_task_tool': has_task_tool,
            'has_task_calls': has_task_calls,
            'maven_calls': maven_calls,
            'backup_file_patterns': backup_patterns
        }
    }


def cmd_coverage(args) -> int:
    """Analyze tool coverage in file."""
    file_path = Path(args.file)

    if not file_path.exists():
        print(json.dumps({'error': f'File not found: {args.file}'}), file=sys.stderr)
        return 1

    if not file_path.is_file():
        print(json.dumps({'error': f'Not a file: {args.file}'}), file=sys.stderr)
        return 1

    result = analyze_tool_coverage(file_path)

    if 'error' in result:
        print(json.dumps(result), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


# =============================================================================
# Cross-File Analysis (from analyze-cross-file-content.py)
# =============================================================================

CONTENT_DIRS = ['references', 'workflows', 'templates']
DEFAULT_SIMILARITY_THRESHOLD = 0.4
EXACT_THRESHOLD = 0.95
MIN_SECTION_LENGTH = 100
MIN_PARAGRAPH_LENGTH = 50

PLACEHOLDER_PATTERNS = [
    r'\{\{[A-Z_]+\}\}',
    r'\{[a-z_]+\}',
    r'\[INSERT [A-Z]+\]',
    r'<[A-Z_]+>',
]

WORKFLOW_PATTERNS = [
    r'^###?\s+Step\s+\d+',
    r'^###?\s+Phase\s+\d+',
    r'^\d+\.\s+\*\*[^*]+\*\*:',
]

TERM_PATTERNS = {
    'definition': r'\*\*([^*]+)\*\*:',
    'header': r'^#{2,4}\s+(.+)$',
    'emphasized': r'\*([^*]+)\*',
    'backtick': r'`([^`]+)`',
}

KNOWN_SYNONYM_GROUPS = [
    {'cross-reference', 'xref', 'internal link', 'cross-ref'},
    {'workflow', 'process', 'procedure', 'protocol'},
    {'must', 'shall', 'required', 'mandatory'},
    {'should', 'recommended', 'advisable'},
    {'may', 'optional', 'can'},
    {'skill', 'plugin', 'component'},
    {'agent', 'assistant', 'bot'},
    {'command', 'slash command', 'directive'},
]


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)
    text = re.sub(r'[#*_\[\]()]', '', text)
    text = re.sub(r'https?://\S+', '', text)
    return ' '.join(text.lower().split())


def compute_hash(text: str) -> str:
    """Compute SHA256 hash of normalized text."""
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]


def extract_sections(content: str, file_path: str) -> List[Dict]:
    """Extract sections from markdown content."""
    sections = []
    lines = content.split('\n')
    current_section = {
        'header': '_intro',
        'level': 0,
        'start_line': 1,
        'content_lines': []
    }

    for i, line in enumerate(lines, 1):
        header_match = re.match(r'^(#{2,4})\s+(.+)$', line)
        if header_match:
            if current_section['content_lines']:
                section_text = '\n'.join(current_section['content_lines'])
                if len(section_text.strip()) >= MIN_SECTION_LENGTH:
                    current_section['end_line'] = i - 1
                    current_section['text'] = section_text
                    current_section['content_hash'] = compute_hash(section_text)
                    current_section['normalized_length'] = len(normalize_text(section_text))
                    sections.append(current_section)

            current_section = {
                'header': header_match.group(2).strip(),
                'level': len(header_match.group(1)),
                'start_line': i,
                'content_lines': []
            }
        else:
            current_section['content_lines'].append(line)

    if current_section['content_lines']:
        section_text = '\n'.join(current_section['content_lines'])
        if len(section_text.strip()) >= MIN_SECTION_LENGTH:
            current_section['end_line'] = len(lines)
            current_section['text'] = section_text
            current_section['content_hash'] = compute_hash(section_text)
            current_section['normalized_length'] = len(normalize_text(section_text))
            sections.append(current_section)

    return sections


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity ratio between two normalized texts."""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    return SequenceMatcher(None, norm1, norm2).ratio()


def find_exact_duplicates(all_sections: List[Dict]) -> List[Dict]:
    """Find exact duplicates using content hashes."""
    hash_groups: Dict[str, List[Dict]] = defaultdict(list)

    for section in all_sections:
        content_hash = section.get('content_hash')
        if content_hash:
            hash_groups[content_hash].append(section)

    duplicates = []
    for content_hash, sections in hash_groups.items():
        if len(sections) > 1:
            duplicates.append({
                'hash': content_hash,
                'occurrences': [
                    {
                        'file': s['file'],
                        'section': s['header'],
                        'lines': f"{s['start_line']}-{s['end_line']}"
                    }
                    for s in sections
                ],
                'line_count': sections[0]['end_line'] - sections[0]['start_line'] + 1,
                'content_preview': normalize_text(sections[0]['text'])[:200] + '...',
                'recommendation': 'consolidate'
            })

    return duplicates


def find_similarity_candidates(
    all_sections: List[Dict],
    threshold: float,
    exact_hashes: Set[str]
) -> List[Dict]:
    """Find sections with similarity between threshold and EXACT_THRESHOLD."""
    candidates = []
    processed_pairs: Set[Tuple[str, str]] = set()

    for i, section1 in enumerate(all_sections):
        if section1.get('content_hash') in exact_hashes:
            continue

        for j, section2 in enumerate(all_sections[i + 1:], i + 1):
            if section1['file'] == section2['file']:
                continue

            if section2.get('content_hash') in exact_hashes:
                continue

            pair_id = tuple(sorted([
                f"{section1['file']}:{section1['header']}",
                f"{section2['file']}:{section2['header']}"
            ]))

            if pair_id in processed_pairs:
                continue
            processed_pairs.add(pair_id)

            similarity = calculate_similarity(section1['text'], section2['text'])

            if threshold <= similarity < EXACT_THRESHOLD:
                candidates.append({
                    'source': {
                        'file': section1['file'],
                        'section': section1['header'],
                        'lines': f"{section1['start_line']}-{section1['end_line']}"
                    },
                    'target': {
                        'file': section2['file'],
                        'section': section2['header'],
                        'lines': f"{section2['start_line']}-{section2['end_line']}"
                    },
                    'similarity': round(similarity, 3),
                    'llm_analysis_required': True
                })

    candidates.sort(key=lambda x: x['similarity'], reverse=True)
    return candidates


def detect_extraction_candidates(all_sections: List[Dict]) -> List[Dict]:
    """Detect content that should be extracted to templates or workflows."""
    candidates = []

    for section in all_sections:
        text = section.get('text', '')

        placeholders_found = []
        for pattern in PLACEHOLDER_PATTERNS:
            matches = re.findall(pattern, text)
            placeholders_found.extend(matches)

        if placeholders_found:
            candidates.append({
                'type': 'template',
                'pattern': 'placeholder_structure',
                'file': section['file'],
                'section': section['header'],
                'lines': f"{section['start_line']}-{section['end_line']}",
                'detected_placeholders': list(set(placeholders_found)),
                'recommendation': 'extract_to_templates'
            })
            continue

        workflow_indicators = 0
        for pattern in WORKFLOW_PATTERNS:
            workflow_indicators += len(re.findall(pattern, text, re.MULTILINE))

        if workflow_indicators >= 3:
            candidates.append({
                'type': 'workflow',
                'pattern': 'step_sequence',
                'file': section['file'],
                'section': section['header'],
                'lines': f"{section['start_line']}-{section['end_line']}",
                'step_count': workflow_indicators,
                'recommendation': 'extract_to_workflows'
            })

    return candidates


def extract_terminology(all_sections: List[Dict]) -> Dict[str, Dict[str, int]]:
    """Extract terminology from content and group by file."""
    terms_by_file: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for section in all_sections:
        file_path = section['file']
        text = section.get('text', '')

        for term_type, pattern in TERM_PATTERNS.items():
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                term = match.strip().lower()
                if 2 < len(term) < 50:
                    terms_by_file[file_path][term] += 1

    return terms_by_file


def find_terminology_variants(terms_by_file: Dict[str, Dict[str, int]]) -> List[Dict]:
    """Find terminology variants using known synonym groups."""
    variants = []

    for synonym_group in KNOWN_SYNONYM_GROUPS:
        found_variants: Dict[str, List[Tuple[str, int]]] = defaultdict(list)

        for file_path, terms in terms_by_file.items():
            for term, count in terms.items():
                term_lower = term.lower()
                for synonym in synonym_group:
                    if synonym in term_lower or term_lower in synonym:
                        found_variants[term].append((file_path, count))
                        break

        if len(found_variants) > 1:
            variant_list = []
            for term, occurrences in found_variants.items():
                files = [occ[0] for occ in occurrences]
                total_count = sum(occ[1] for occ in occurrences)
                variant_list.append({
                    'term': term,
                    'files': list(set(files)),
                    'count': total_count
                })

            if variant_list:
                most_common = max(variant_list, key=lambda x: x['count'])
                variants.append({
                    'concept': list(synonym_group)[0],
                    'variants': variant_list,
                    'recommendation': f"standardize on '{most_common['term']}'"
                })

    return variants


def analyze_cross_file(skill_path: Path, similarity_threshold: float) -> Dict:
    """Main cross-file analysis function."""
    skill_name = skill_path.name
    all_sections = []
    files_analyzed = 0
    total_lines = 0

    for content_dir in CONTENT_DIRS:
        dir_path = skill_path / content_dir
        if not dir_path.exists():
            continue

        for md_file in dir_path.glob('**/*.md'):
            try:
                content = md_file.read_text(encoding='utf-8')
                rel_path = str(md_file.relative_to(skill_path))
                files_analyzed += 1
                total_lines += len(content.split('\n'))

                sections = extract_sections(content, rel_path)
                for section in sections:
                    section['file'] = rel_path
                all_sections.extend(sections)

            except Exception:
                continue

    content_blocks = [
        {
            'id': f"{s['file']}:{s['header']}".replace('/', ':').replace(' ', '-').lower(),
            'file': s['file'],
            'section': s['header'],
            'lines': f"{s['start_line']}-{s['end_line']}",
            'content_hash': s.get('content_hash', ''),
            'normalized_length': s.get('normalized_length', 0)
        }
        for s in all_sections
    ]

    exact_duplicates = find_exact_duplicates(all_sections)
    exact_hashes = {d['hash'] for d in exact_duplicates}

    similarity_candidates = find_similarity_candidates(
        all_sections, similarity_threshold, exact_hashes
    )

    extraction_candidates = detect_extraction_candidates(all_sections)

    terms_by_file = extract_terminology(all_sections)
    terminology_variants = find_terminology_variants(terms_by_file)

    llm_review_required = (
        len(similarity_candidates) > 0 or
        len(extraction_candidates) > 0 or
        len(terminology_variants) > 0
    )

    return {
        'skill_path': str(skill_path),
        'skill_name': skill_name,
        'files_analyzed': files_analyzed,
        'total_lines': total_lines,
        'content_blocks': content_blocks,
        'exact_duplicates': exact_duplicates,
        'similarity_candidates': similarity_candidates,
        'extraction_candidates': extraction_candidates,
        'terminology_variants': terminology_variants,
        'summary': {
            'exact_duplicate_pairs': len(exact_duplicates),
            'similarity_candidates': len(similarity_candidates),
            'extraction_candidates': len(extraction_candidates),
            'terminology_issues': len(terminology_variants),
            'llm_review_required': llm_review_required
        }
    }


def cmd_cross_file(args) -> int:
    """Analyze cross-file content in skill directory."""
    skill_path = Path(args.skill_path)

    if not skill_path.exists():
        print(json.dumps({'error': f'Skill path not found: {args.skill_path}'}), file=sys.stderr)
        return 1

    if not skill_path.is_dir():
        print(json.dumps({'error': f'Skill path is not a directory: {args.skill_path}'}), file=sys.stderr)
        return 1

    try:
        result = analyze_cross_file(skill_path, args.similarity_threshold)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        print(json.dumps({'error': f'Analysis failed: {str(e)}'}), file=sys.stderr)
        return 1


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Plugin component analysis tools',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze markdown file structure
  %(prog)s markdown --file agent.md

  # Analyze skill directory structure
  %(prog)s structure --directory skills/plugin-doctor

  # Analyze tool coverage
  %(prog)s coverage --file agent.md

  # Analyze cross-file content
  %(prog)s cross-file --skill-path skills/plugin-doctor
"""
    )

    subparsers = parser.add_subparsers(dest='command', help='Operation to perform')

    # markdown subcommand
    p_markdown = subparsers.add_parser('markdown', help='Analyze markdown file structure')
    p_markdown.add_argument('--file', required=True, help='Path to markdown file')
    p_markdown.add_argument(
        '--type',
        default='auto',
        choices=['agent', 'command', 'skill', 'auto'],
        help='Component type (default: auto)'
    )
    p_markdown.set_defaults(func=cmd_markdown)

    # structure subcommand
    p_structure = subparsers.add_parser('structure', help='Analyze skill directory structure')
    p_structure.add_argument('--directory', required=True, help='Path to skill directory')
    p_structure.set_defaults(func=cmd_structure)

    # coverage subcommand
    p_coverage = subparsers.add_parser('coverage', help='Analyze tool coverage')
    p_coverage.add_argument('--file', required=True, help='Path to agent/command file')
    p_coverage.set_defaults(func=cmd_coverage)

    # cross-file subcommand
    p_crossfile = subparsers.add_parser('cross-file', help='Analyze cross-file content')
    p_crossfile.add_argument('--skill-path', required=True, help='Path to skill directory')
    p_crossfile.add_argument(
        '--similarity-threshold',
        type=float,
        default=DEFAULT_SIMILARITY_THRESHOLD,
        help=f'Minimum similarity threshold (default: {DEFAULT_SIMILARITY_THRESHOLD})'
    )
    p_crossfile.set_defaults(func=cmd_cross_file)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
