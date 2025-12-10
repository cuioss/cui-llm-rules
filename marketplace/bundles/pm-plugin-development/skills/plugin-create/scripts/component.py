#!/usr/bin/env python3
"""
component.py - Marketplace component creation utilities.

Consolidated from:
- generate-frontmatter.py → generate subcommand
- validate-component.py → validate subcommand

Provides frontmatter generation and component validation for agents, commands, and skills.

Output: YAML for generate, JSON for validate.
"""

import argparse
import json
import re
import sys


# =============================================================================
# Generate Subcommand
# =============================================================================

def generate_agent_frontmatter(answers):
    """Generate frontmatter for agent component."""
    frontmatter = {
        'name': answers['name'],
        'description': answers['description']
    }

    # Add optional model field if present
    if 'model' in answers and answers['model']:
        frontmatter['model'] = answers['model']

    # Format tools as comma-separated string (not array)
    if 'tools' in answers:
        tools = answers['tools']
        if isinstance(tools, list):
            if len(tools) == 0:
                raise ValueError("Error: Agents must have at least one tool")
            frontmatter['tools'] = ', '.join(tools)
        else:
            frontmatter['tools'] = tools
    else:
        raise ValueError("Error: Agents must have 'tools' field")

    return frontmatter


def generate_command_frontmatter(answers):
    """Generate frontmatter for command component."""
    frontmatter = {
        'name': answers['name'],
        'description': answers['description']
    }
    return frontmatter


def generate_skill_frontmatter(answers):
    """Generate frontmatter for skill component."""
    frontmatter = {
        'name': answers['name'],
        'description': answers['description']
    }

    # Add optional allowed-tools field if present
    if 'allowed-tools' in answers and answers['allowed-tools']:
        if isinstance(answers['allowed-tools'], list):
            frontmatter['allowed-tools'] = ', '.join(answers['allowed-tools'])
        else:
            frontmatter['allowed-tools'] = answers['allowed-tools']

    # Add optional requirements field if present
    if 'requirements' in answers and answers['requirements']:
        frontmatter['requirements'] = answers['requirements']

    return frontmatter


def format_frontmatter(frontmatter_dict):
    """Format frontmatter as YAML with --- delimiters."""
    lines = []

    for key, value in frontmatter_dict.items():
        # Quote value if it contains special characters
        if isinstance(value, str) and ('"' in value or "'" in value or ':' in value):
            # Escape double quotes and wrap in quotes
            escaped_value = value.replace('"', '\\"')
            lines.append(f'{key}: "{escaped_value}"')
        else:
            lines.append(f'{key}: {value}')

    yaml_content = '\n'.join(lines)
    return f"---\n{yaml_content}\n---"


def cmd_generate(args) -> int:
    """Generate YAML frontmatter for marketplace component."""
    try:
        answers = json.loads(args.config)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {str(e)}", file=sys.stderr)
        return 1

    # Validate component type
    if args.type not in ['agent', 'command', 'skill']:
        print(f"Error: Invalid component type '{args.type}'. Must be 'agent', 'command', or 'skill'", file=sys.stderr)
        return 1

    # Generate frontmatter based on type
    try:
        if args.type == 'agent':
            frontmatter_dict = generate_agent_frontmatter(answers)
        elif args.type == 'command':
            frontmatter_dict = generate_command_frontmatter(answers)
        elif args.type == 'skill':
            frontmatter_dict = generate_skill_frontmatter(answers)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1

    # Format as YAML with delimiters
    print(format_frontmatter(frontmatter_dict))
    return 0


# =============================================================================
# Validate Subcommand
# =============================================================================

def parse_simple_yaml(yaml_text):
    """Parse simple YAML (key: value pairs only) without external dependencies."""
    result = {}
    lines = yaml_text.strip().split('\n')

    for line_num, line in enumerate(lines, 1):
        # Check for improper indentation (leading spaces before top-level keys)
        if line and line[0] == ' ' and ':' in line:
            raise ValueError(f"Line {line_num}: Improper indentation detected")

        line = line.strip()
        if not line or line.startswith('#'):
            continue

        if ':' not in line:
            raise ValueError(f"Line {line_num}: Invalid YAML syntax - expected key: value pair")

        key, _, value = line.partition(':')
        key = key.strip()
        value = value.strip()

        if not key:
            raise ValueError(f"Line {line_num}: Empty key in YAML")

        # Handle different value types
        if value.startswith('[') and value.endswith(']'):
            items = value[1:-1].split(',')
            result[key] = [item.strip() for item in items]
        elif value.startswith('"') and value.endswith('"'):
            result[key] = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            result[key] = value[1:-1]
        else:
            result[key] = value

    return result


def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
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

    for field in ['name', 'description']:
        if field not in frontmatter:
            errors.append({
                "type": "frontmatter_field_missing",
                "field": field,
                "message": f"Required frontmatter field '{field}' not found"
            })

    if 'tools' not in frontmatter:
        errors.append({
            "type": "frontmatter_field_missing",
            "field": "tools",
            "message": "Required frontmatter field 'tools' not found"
        })
    else:
        tools = frontmatter['tools']

        if isinstance(tools, list):
            warnings.append({
                "type": "tools_format",
                "field": "tools",
                "message": f"Tools field uses array syntax {tools} - should use comma-separated format '{', '.join(tools)}'"
            })
            tools_list = tools
        elif isinstance(tools, str):
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

    for field in ['name', 'description']:
        if field not in frontmatter:
            errors.append({
                "type": "frontmatter_field_missing",
                "field": field,
                "message": f"Required frontmatter field '{field}' not found"
            })

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

    for field in ['name', 'description']:
        if field not in frontmatter:
            errors.append({
                "type": "frontmatter_field_missing",
                "field": field,
                "message": f"Required frontmatter field '{field}' not found"
            })

    if 'allowed-tools' in frontmatter:
        if isinstance(frontmatter['allowed-tools'], list):
            warnings.append({
                "type": "tools_format",
                "field": "allowed-tools",
                "message": "allowed-tools field uses array syntax - should use comma-separated format"
            })

    return errors, warnings


def validate_agent_content(content):
    """Validate agent-specific content rules."""
    errors = []
    warnings = []

    if '## CONTINUOUS IMPROVEMENT RULE' not in content:
        warnings.append({
            "type": "missing_section",
            "section": "CONTINUOUS IMPROVEMENT RULE",
            "message": "Agent should have CONTINUOUS IMPROVEMENT RULE section"
        })
    else:
        # Check for self-invocation pattern (Pattern 22)
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

    required_sections = ['# ', '## WORKFLOW', '## USAGE EXAMPLES']

    for section in required_sections:
        if section not in content:
            section_name = section.replace('## ', '').replace('# ', 'Title')
            errors.append({
                "type": "missing_section",
                "section": section_name,
                "message": f"Required section '{section_name}' not found"
            })

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

    required_sections = ['# ', '## What This Skill Provides', '## When to', '## Workflow']

    for section in required_sections:
        if section not in content:
            section_name = section.replace('## ', '').replace('# ', 'Title')
            warnings.append({
                "type": "missing_section",
                "section": section_name,
                "message": f"Expected section '{section_name}' not found in SKILL.md"
            })

    if '## CONTINUOUS IMPROVEMENT RULE' in content:
        warnings.append({
            "type": "unexpected_section",
            "section": "CONTINUOUS IMPROVEMENT RULE",
            "message": "Skills should not have CONTINUOUS IMPROVEMENT RULE section"
        })

    return errors, warnings


def cmd_validate(args) -> int:
    """Validate marketplace component structure."""
    errors = []
    warnings = []

    # Read file
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        result = {
            "valid": False,
            "errors": [{"type": "file_not_found", "message": f"File not found: {args.file}"}],
            "warnings": []
        }
        print(json.dumps(result, indent=2))
        return 1
    except Exception as e:
        result = {
            "valid": False,
            "errors": [{"type": "read_error", "message": f"Error reading file: {str(e)}"}],
            "warnings": []
        }
        print(json.dumps(result, indent=2))
        return 1

    # Extract and validate frontmatter
    frontmatter, error = extract_frontmatter(content)

    if error:
        errors.append({"type": "frontmatter_missing", "message": error})
    else:
        # Validate frontmatter based on component type
        if args.type == 'agent':
            fm_errors, fm_warnings = validate_frontmatter_agent(frontmatter)
        elif args.type == 'command':
            fm_errors, fm_warnings = validate_frontmatter_command(frontmatter)
        elif args.type == 'skill':
            fm_errors, fm_warnings = validate_frontmatter_skill(frontmatter)
        else:
            errors.append({
                "type": "invalid_type",
                "message": f"Invalid component type: {args.type}. Must be 'agent', 'command', or 'skill'"
            })
            result = {"valid": False, "errors": errors, "warnings": warnings}
            print(json.dumps(result, indent=2))
            return 1

        errors.extend(fm_errors)
        warnings.extend(fm_warnings)

    # Validate content structure based on component type
    if args.type == 'agent':
        content_errors, content_warnings = validate_agent_content(content)
    elif args.type == 'command':
        content_errors, content_warnings = validate_command_content(content)
    elif args.type == 'skill':
        content_errors, content_warnings = validate_skill_content(content)
    else:
        content_errors, content_warnings = [], []

    errors.extend(content_errors)
    warnings.extend(content_warnings)

    # Determine validity
    valid = len(errors) == 0

    result = {"valid": valid, "errors": errors, "warnings": warnings}
    print(json.dumps(result, indent=2))
    return 0 if valid else 1


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Marketplace component creation utilities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate agent frontmatter
  %(prog)s generate --type agent --config '{"name": "my-agent", "description": "Does things", "tools": ["Read", "Write"]}'

  # Generate command frontmatter
  %(prog)s generate --type command --config '{"name": "my-cmd", "description": "A command"}'

  # Generate skill frontmatter
  %(prog)s generate --type skill --config '{"name": "my-skill", "description": "A skill"}'

  # Validate agent
  %(prog)s validate --file ./agents/my-agent.md --type agent

  # Validate command
  %(prog)s validate --file ./commands/my-command.md --type command

  # Validate skill
  %(prog)s validate --file ./skills/my-skill/SKILL.md --type skill
"""
    )

    subparsers = parser.add_subparsers(dest='command', help='Operation to perform')

    # generate command
    p_generate = subparsers.add_parser('generate', help='Generate YAML frontmatter')
    p_generate.add_argument('--type', required=True, choices=['agent', 'command', 'skill'],
                           help='Component type')
    p_generate.add_argument('--config', required=True,
                           help='JSON string with component configuration')
    p_generate.set_defaults(func=cmd_generate)

    # validate command
    p_validate = subparsers.add_parser('validate', help='Validate component structure')
    p_validate.add_argument('--file', required=True, help='Path to component file')
    p_validate.add_argument('--type', required=True, choices=['agent', 'command', 'skill'],
                           help='Component type')
    p_validate.set_defaults(func=cmd_validate)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
