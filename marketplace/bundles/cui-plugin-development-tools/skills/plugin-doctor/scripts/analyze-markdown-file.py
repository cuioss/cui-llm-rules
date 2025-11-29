#!/usr/bin/env python3
"""
analyze-markdown-file.py

Analyzes markdown file structure, frontmatter, and compliance with standards.

Usage:
    python3 analyze-markdown-file.py <file_path> [component_type]

Arguments:
    file_path       Path to the markdown file to analyze
    component_type  Optional: agent, command, skill, or auto (default: auto)

Output: JSON with structural analysis including:
    - file_type: Detected component type
    - metrics.line_count: Total lines in file
    - frontmatter: Presence and validity of YAML frontmatter
    - continuous_improvement_rule: CI rule presence and pattern
    - bloat.classification: NORMAL, LARGE, BLOATED, or CRITICAL
    - execution_patterns: EXECUTION MODE, workflow tree, MANDATORY markers
    - rules: Rule 6, Rule 7, and Rule 8 violation detection
    - quality.has_forbidden_metadata: Forbidden metadata sections

Exit codes:
    0 - Success
    1 - Error (missing argument, file not found)
"""

import argparse
import json
import re
import sys
from pathlib import Path


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


def extract_frontmatter(content: str) -> tuple[bool, str]:
    """Extract YAML frontmatter from content."""
    if not content.startswith('---'):
        return False, ''

    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if match:
        return True, match.group(1)
    return False, ''


def check_frontmatter_fields(frontmatter: str) -> dict:
    """Check required fields in frontmatter."""
    has_name = bool(re.search(r'^name:', frontmatter, re.MULTILINE))
    has_desc = bool(re.search(r'^description:', frontmatter, re.MULTILINE))

    # Check tools field - agents use "tools:", skills use "allowed-tools:"
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


def check_yaml_validity(frontmatter: str) -> bool:
    """Basic YAML validity check."""
    return bool(re.search(r'^[a-z_]*:', frontmatter, re.MULTILINE))


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

        # Check Pattern 22 violation (self-invocation in agents)
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
        # Commands should be thin wrappers - stricter thresholds
        if line_count > 200:
            return 'CRITICAL'
        elif line_count > 150:
            return 'BLOATED'
        elif line_count > 100:
            return 'LARGE'
    elif component_type == 'skill':
        # Skills may have multiple workflows - more permissive
        if line_count > 1200:
            return 'CRITICAL'
        elif line_count > 800:
            return 'BLOATED'
        elif line_count > 400:
            return 'LARGE'
    else:
        # Agents and unknown types - standard thresholds
        if line_count > 800:
            return 'CRITICAL'
        elif line_count > 500:
            return 'BLOATED'
        elif line_count > 300:
            return 'LARGE'

    return 'NORMAL'


def check_execution_patterns(content: str) -> dict:
    """Check for execution patterns in content."""
    has_execution_mode = bool(re.search(r'EXECUTION MODE', content, re.IGNORECASE))
    has_workflow_tree = bool(re.search(r'Workflow Decision Tree', content, re.IGNORECASE))
    mandatory_count = len(re.findall(r'\*\*MANDATORY\*\*', content))
    has_handoff_rules = bool(re.search(r'CRITICAL HANDOFF', content, re.IGNORECASE))

    return {
        'has_execution_mode': has_execution_mode,
        'has_workflow_tree': has_workflow_tree,
        'mandatory_marker_count': mandatory_count,
        'has_handoff_rules': has_handoff_rules
    }


def check_rule_violations(content: str, frontmatter: str, component_type: str,
                          has_tools: bool, file_path: str) -> dict:
    """Check for rule violations."""
    # Rule 6: Task tool prohibition in agents
    rule_6_violation = False
    if component_type == 'agent' and has_tools:
        # Check if Task appears in the tools array
        if re.search(r'^  - Task$|Task,|Task$', frontmatter, re.MULTILINE):
            rule_6_violation = True

    # Rule 7: Maven execution restriction
    rule_7_violation = False
    if re.search(r'mvn |maven |./mvnw ', content):
        # Exclude maven-specific bundles/skills
        if 'builder-maven' not in file_path:
            # Check for actual command invocations
            pattern = r'^Bash:.*mvn|^Bash:.*maven|^Bash:.*\./mvnw|`.*mvn |`.*\./mvnw |^\s+mvn |^\s+\./mvnw '
            matches = re.findall(pattern, content, re.MULTILINE)
            # Filter out rule descriptions
            for match in matches:
                if 'Rule 7' not in match and 'should use' not in match and 'instead of' not in match:
                    rule_7_violation = True
                    break

    # Rule 8: Script-runner usage (no hardcoded paths)
    rule_8_violation = False
    if re.search(r'python3 .*/scripts/|bash .*/scripts/|\{[^}]+\}/scripts/', content):
        # Check if it's using script-runner skill (acceptable)
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


def analyze_file(file_path: Path, component_type: str) -> dict:
    """Analyze markdown file and return results."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='replace')
    except (OSError, IOError) as e:
        return {'error': f'Failed to read file: {e}'}

    # Basic metrics
    line_count = content.count('\n') + (1 if content and not content.endswith('\n') else 0)

    # Auto-detect component type if needed
    if component_type == 'auto':
        component_type = detect_component_type(str(file_path))

    # Extract and analyze frontmatter
    frontmatter_present, frontmatter = extract_frontmatter(content)
    yaml_valid = check_yaml_validity(frontmatter) if frontmatter_present else False
    required_fields = check_frontmatter_fields(frontmatter) if frontmatter_present else {
        'name': {'present': False},
        'description': {'present': False},
        'tools': {'present': False, 'field_type': 'none'}
    }

    # Count sections
    section_count = len(re.findall(r'^## ', content, re.MULTILINE))

    # Check for parameters section
    has_param_section = bool(re.search(r'^## PARAMETERS|^### Parameters', content, re.MULTILINE | re.IGNORECASE))

    # Continuous improvement
    ci_rule = check_continuous_improvement(content, component_type)

    # Bloat classification
    bloat_class = get_bloat_classification(line_count, component_type)

    # Execution patterns
    exec_patterns = check_execution_patterns(content)

    # Rule violations
    rules = check_rule_violations(
        content, frontmatter, component_type,
        required_fields['tools']['present'], str(file_path)
    )

    # Forbidden metadata
    has_forbidden, forbidden_sections = check_forbidden_metadata(content)

    return {
        'file_path': str(file_path),
        'file_type': {
            'type': component_type
        },
        'metrics': {
            'line_count': line_count
        },
        'frontmatter': {
            'present': frontmatter_present,
            'yaml_valid': yaml_valid,
            'required_fields': required_fields
        },
        'structure': {
            'section_count': section_count
        },
        'parameters': {
            'has_section': has_param_section
        },
        'continuous_improvement_rule': ci_rule,
        'bloat': {
            'classification': bloat_class
        },
        'execution_patterns': exec_patterns,
        'rules': rules,
        'quality': {
            'has_forbidden_metadata': has_forbidden,
            'forbidden_sections': forbidden_sections
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze markdown file structure, frontmatter, and compliance"
    )
    parser.add_argument(
        'file_path',
        help="Path to the markdown file to analyze"
    )
    parser.add_argument(
        'component_type',
        nargs='?',
        default='auto',
        choices=['agent', 'command', 'skill', 'auto'],
        help="Component type (default: auto)"
    )

    args = parser.parse_args()

    file_path = Path(args.file_path)

    # Validate path
    if not file_path.exists():
        print(json.dumps({'error': f'File not found: {args.file_path}'}), file=sys.stderr)
        return 1

    if not file_path.is_file():
        print(json.dumps({'error': f'Not a file: {args.file_path}'}), file=sys.stderr)
        return 1

    # Analyze file
    result = analyze_file(file_path, args.component_type)

    if 'error' in result:
        print(json.dumps(result), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
