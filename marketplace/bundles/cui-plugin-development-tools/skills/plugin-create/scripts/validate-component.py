#!/usr/bin/env python3
"""
Validates marketplace component structure.

Usage: validate-component.py <path> <type>
Output: JSON with validation results
"""

import sys
import json
import re


def show_help():
    """Display help message."""
    help_text = """
Usage: validate-component.py <file_path> <component_type>

Validates marketplace component structure and compliance.

Arguments:
  file_path       Path to the component markdown file
  component_type  Type: agent, command, or skill

Validation checks:
  Frontmatter:
    - Presence and valid YAML syntax
    - Required fields: name, description
    - Tools field for agents (comma-separated, not array)
    - Rule 6: Agents cannot use Task tool

  Content structure:
    - Required sections per component type
    - CONTINUOUS IMPROVEMENT RULE presence
    - Pattern 22 (self-invocation) detection for agents

Output: JSON with validation results including:
  - valid: Boolean overall validity
  - errors: Array of critical issues
  - warnings: Array of non-critical issues

Exit codes:
  0 - Validation passed (valid=true)
  1 - Validation failed or error

Examples:
  validate-component.py ./agents/my-agent.md agent
  validate-component.py ./commands/my-command.md command
  validate-component.py ./skills/my-skill/SKILL.md skill
"""
    print(help_text.strip())
    sys.exit(0)


def parse_simple_yaml(yaml_text):
    """Parse simple YAML (key: value pairs only) without external dependencies."""
    result = {}
    lines = yaml_text.strip().split('\n')

    for line_num, line in enumerate(lines, 1):
        # Check for improper indentation (leading spaces before top-level keys)
        if line and line[0] == ' ' and ':' in line:
            # This looks like improperly indented YAML
            raise ValueError(f"Line {line_num}: Improper indentation detected")

        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # Handle key: value pairs
        if ':' not in line:
            # Non-empty, non-comment line without colon is invalid
            raise ValueError(f"Line {line_num}: Invalid YAML syntax - expected key: value pair")

        key, _, value = line.partition(':')
        key = key.strip()
        value = value.strip()

        if not key:
            raise ValueError(f"Line {line_num}: Empty key in YAML")

        # Handle different value types
        if value.startswith('[') and value.endswith(']'):
            # Array syntax: [item1, item2, item3]
            items = value[1:-1].split(',')
            result[key] = [item.strip() for item in items]
        elif value.startswith('"') and value.endswith('"'):
            # Quoted string
            result[key] = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            # Single quoted string
            result[key] = value[1:-1]
        else:
            # Unquoted value
            result[key] = value

    return result

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    # Match content between --- delimiters
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return None, "YAML frontmatter not found (must be between --- delimiters)"

    frontmatter_text = match.group(1)

    try:
        frontmatter = parse_simple_yaml(frontmatter_text)
        return frontmatter, None
    except Exception as e:
        return None, f"Invalid YAML syntax: {str(e)}"

def validate_frontmatter_agent(frontmatter):
    """Validate agent frontmatter fields."""
    errors = []
    warnings = []

    # Required fields
    if 'name' not in frontmatter:
        errors.append({
            "type": "frontmatter_field_missing",
            "field": "name",
            "message": "Required frontmatter field 'name' not found"
        })

    if 'description' not in frontmatter:
        errors.append({
            "type": "frontmatter_field_missing",
            "field": "description",
            "message": "Required frontmatter field 'description' not found"
        })

    if 'tools' not in frontmatter:
        errors.append({
            "type": "frontmatter_field_missing",
            "field": "tools",
            "message": "Required frontmatter field 'tools' not found"
        })
    else:
        tools = frontmatter['tools']

        # Check if tools is using array syntax (should be comma-separated string)
        if isinstance(tools, list):
            warnings.append({
                "type": "tools_format",
                "field": "tools",
                "message": f"Tools field uses array syntax {tools} - should use comma-separated format '{', '.join(tools)}'"
            })
            # Convert to list for checking
            tools_list = tools
        elif isinstance(tools, str):
            # Parse comma-separated string
            tools_list = [t.strip() for t in tools.split(',')]
        else:
            errors.append({
                "type": "tools_format",
                "field": "tools",
                "message": "Tools field must be comma-separated string"
            })
            tools_list = []

        # Check for prohibited Task tool (Rule 6)
        if 'Task' in tools_list:
            errors.append({
                "type": "prohibited_tool",
                "field": "tools",
                "message": "Agents cannot use Task tool (Rule 6) - unavailable at runtime"
            })

    return errors, warnings

def validate_frontmatter_command(frontmatter):
    """Validate command frontmatter fields."""
    errors = []
    warnings = []

    # Required fields
    if 'name' not in frontmatter:
        errors.append({
            "type": "frontmatter_field_missing",
            "field": "name",
            "message": "Required frontmatter field 'name' not found"
        })

    if 'description' not in frontmatter:
        errors.append({
            "type": "frontmatter_field_missing",
            "field": "description",
            "message": "Required frontmatter field 'description' not found"
        })

    # Commands should NOT have tools field in frontmatter
    if 'tools' in frontmatter:
        warnings.append({
            "type": "unexpected_field",
            "field": "tools",
            "message": "Commands typically don't have 'tools' in frontmatter"
        })

    return errors, warnings

def validate_frontmatter_skill(frontmatter):
    """Validate skill frontmatter fields."""
    errors = []
    warnings = []

    # Required fields
    if 'name' not in frontmatter:
        errors.append({
            "type": "frontmatter_field_missing",
            "field": "name",
            "message": "Required frontmatter field 'name' not found"
        })

    if 'description' not in frontmatter:
        errors.append({
            "type": "frontmatter_field_missing",
            "field": "description",
            "message": "Required frontmatter field 'description' not found"
        })

    # Check allowed-tools format if present
    if 'allowed-tools' in frontmatter:
        allowed_tools = frontmatter['allowed-tools']

        if isinstance(allowed_tools, list):
            warnings.append({
                "type": "tools_format",
                "field": "allowed-tools",
                "message": f"allowed-tools field uses array syntax - should use comma-separated format"
            })

    return errors, warnings

def validate_agent_content(content):
    """Validate agent-specific content rules."""
    errors = []
    warnings = []

    # Check for CONTINUOUS IMPROVEMENT RULE section
    if '## CONTINUOUS IMPROVEMENT RULE' not in content:
        warnings.append({
            "type": "missing_section",
            "section": "CONTINUOUS IMPROVEMENT RULE",
            "message": "Agent should have CONTINUOUS IMPROVEMENT RULE section"
        })
    else:
        # Check for self-invocation pattern (Pattern 22)
        # Agents must REPORT improvements, not invoke commands
        problematic_patterns = [
            r'YOU MUST.*using\s+/plugin-',
            r'invoke\s+/plugin-',
            r'call\s+/plugin-',
            r'SlashCommand:\s*/plugin-'
        ]

        for pattern in problematic_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                errors.append({
                    "type": "self_invocation",
                    "section": "CONTINUOUS IMPROVEMENT RULE",
                    "message": "Agent uses self-invocation pattern (Pattern 22) - agents must REPORT improvements, not invoke commands"
                })
                break

    # Check for required sections
    required_sections = ['# ', '## Workflow', '## Tool Usage']
    for section in required_sections:
        if section not in content:
            warnings.append({
                "type": "missing_section",
                "section": section.replace('## ', '').replace('# ', 'Title'),
                "message": f"Expected section '{section}' not found"
            })

    return errors, warnings

def validate_command_content(content):
    """Validate command-specific content rules."""
    errors = []
    warnings = []

    # Check for required sections
    required_sections = [
        '# ',  # Title
        '## WORKFLOW',
        '## USAGE EXAMPLES'
    ]

    for section in required_sections:
        if section not in content:
            section_name = section.replace('## ', '').replace('# ', 'Title')
            errors.append({
                "type": "missing_section",
                "section": section_name,
                "message": f"Required section '{section_name}' not found"
            })

    # Check for CONTINUOUS IMPROVEMENT RULE (should be present for commands)
    if '## CONTINUOUS IMPROVEMENT RULE' not in content:
        warnings.append({
            "type": "missing_section",
            "section": "CONTINUOUS IMPROVEMENT RULE",
            "message": "Command should have CONTINUOUS IMPROVEMENT RULE section"
        })

    return errors, warnings

def validate_skill_content(content):
    """Validate skill-specific content rules."""
    errors = []
    warnings = []

    # Check for required SKILL.md sections
    required_sections = [
        '# ',  # Title
        '## What This Skill Provides',
        '## When to',  # "When to Use This Skill" or "When to Activate"
        '## Workflow'
    ]

    for section in required_sections:
        if section not in content:
            section_name = section.replace('## ', '').replace('# ', 'Title')
            warnings.append({
                "type": "missing_section",
                "section": section_name,
                "message": f"Expected section '{section_name}' not found in SKILL.md"
            })

    # Skills should NOT have CONTINUOUS IMPROVEMENT RULE
    if '## CONTINUOUS IMPROVEMENT RULE' in content:
        warnings.append({
            "type": "unexpected_section",
            "section": "CONTINUOUS IMPROVEMENT RULE",
            "message": "Skills should not have CONTINUOUS IMPROVEMENT RULE section"
        })

    return errors, warnings

def validate_component(file_path, component_type):
    """Main validation function."""
    errors = []
    warnings = []

    # Read file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return {
            "valid": False,
            "errors": [{
                "type": "file_not_found",
                "message": f"File not found: {file_path}"
            }],
            "warnings": []
        }
    except Exception as e:
        return {
            "valid": False,
            "errors": [{
                "type": "read_error",
                "message": f"Error reading file: {str(e)}"
            }],
            "warnings": []
        }

    # Extract and validate frontmatter
    frontmatter, error = extract_frontmatter(content)

    if error:
        errors.append({
            "type": "frontmatter_missing",
            "message": error
        })
    else:
        # Validate frontmatter based on component type
        if component_type == 'agent':
            fm_errors, fm_warnings = validate_frontmatter_agent(frontmatter)
            errors.extend(fm_errors)
            warnings.extend(fm_warnings)
        elif component_type == 'command':
            fm_errors, fm_warnings = validate_frontmatter_command(frontmatter)
            errors.extend(fm_errors)
            warnings.extend(fm_warnings)
        elif component_type == 'skill':
            fm_errors, fm_warnings = validate_frontmatter_skill(frontmatter)
            errors.extend(fm_errors)
            warnings.extend(fm_warnings)
        else:
            errors.append({
                "type": "invalid_type",
                "message": f"Invalid component type: {component_type}. Must be 'agent', 'command', or 'skill'"
            })
            return {
                "valid": False,
                "errors": errors,
                "warnings": warnings
            }

    # Validate content structure based on component type
    if component_type == 'agent':
        content_errors, content_warnings = validate_agent_content(content)
        errors.extend(content_errors)
        warnings.extend(content_warnings)
    elif component_type == 'command':
        content_errors, content_warnings = validate_command_content(content)
        errors.extend(content_errors)
        warnings.extend(content_warnings)
    elif component_type == 'skill':
        content_errors, content_warnings = validate_skill_content(content)
        errors.extend(content_errors)
        warnings.extend(content_warnings)

    # Determine validity
    valid = len(errors) == 0

    return {
        "valid": valid,
        "errors": errors,
        "warnings": warnings
    }

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        show_help()

    if len(sys.argv) != 3:
        print(json.dumps({
            "valid": False,
            "errors": [{
                "type": "usage_error",
                "message": "Usage: validate-component.py <file_path> <component_type>. Use --help for details."
            }],
            "warnings": []
        }))
        sys.exit(1)

    file_path = sys.argv[1]
    component_type = sys.argv[2]

    result = validate_component(file_path, component_type)
    print(json.dumps(result, indent=2))

    # Exit with non-zero code if validation failed
    sys.exit(0 if result["valid"] else 1)

if __name__ == "__main__":
    main()
