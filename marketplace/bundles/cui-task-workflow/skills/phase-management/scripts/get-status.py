#!/usr/bin/env python3
"""
Get comprehensive plan status.

Usage:
    python3 get-status.py <plan_directory>
    python3 get-status.py --help

Output: JSON with plan status, phase progress, and configuration.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Phase order
PHASE_ORDER = ['init', 'refine', 'implement', 'verify', 'finalize']
SIMPLE_PHASE_ORDER = ['init', 'execute', 'finalize']


def parse_plan_md(plan_file: Path) -> dict:
    """Parse plan.md for status information."""
    if not plan_file.exists():
        return {'error': f'File not found: {plan_file}'}

    content = plan_file.read_text()

    # Extract title
    title_match = re.search(r'^#\s+(?:Task Plan:\s*)?(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else ''

    # Extract current phase and task
    phase_match = re.search(r'\*\*Current Phase\*\*:\s*(\w+)', content)
    current_phase = phase_match.group(1) if phase_match else ''

    task_match = re.search(r'\*\*Current Task\*\*:\s*([^\n]+)', content)
    current_task = task_match.group(1).strip() if task_match else ''

    # Parse phase progress table
    phases = []
    table_pattern = r'\|\s*Phase\s*\|\s*Status\s*\|\s*Tasks\s*\|\s*Completed\s*\|.*?\n\|[-\s|]+\n((?:\|[^\n]+\n)+)'
    table_match = re.search(table_pattern, content, re.IGNORECASE)

    if table_match:
        table_rows = table_match.group(1).strip().split('\n')
        for row in table_rows:
            cols = [c.strip() for c in row.split('|')[1:-1]]
            if len(cols) >= 4:
                phase_name = cols[0].strip()
                status = cols[1].strip()
                task_count = cols[2].strip()
                completed = cols[3].strip()

                completed_match = re.match(r'(\d+)/(\d+)', completed)
                if completed_match:
                    completed_count = int(completed_match.group(1))
                    total_count = int(completed_match.group(2))
                else:
                    completed_count = 0
                    total_count = int(task_count) if task_count.isdigit() else 0

                phases.append({
                    'phase': phase_name,
                    'status': status,
                    'tasks': total_count,
                    'completed': f'{completed_count}/{total_count}',
                    'completed_count': completed_count,
                    'total_count': total_count
                })

    # Find current task name
    current_task_name = ''
    if current_task:
        task_num_match = re.search(r'task-?(\d+)', current_task, re.IGNORECASE)
        if task_num_match:
            task_num = task_num_match.group(1)
            task_header = re.search(rf'### Task {task_num}:\s*([^\n]+)', content)
            if task_header:
                current_task_name = task_header.group(1).strip()

    return {
        'title': title,
        'current_phase': current_phase,
        'current_task': current_task,
        'current_task_name': current_task_name,
        'phases': phases
    }


def parse_config_md(config_file: Path) -> dict:
    """Parse config.md for configuration information."""
    if not config_file.exists():
        return {}

    content = config_file.read_text()

    config = {}

    # Extract plan type
    type_match = re.search(r'\*\*Plan Type\*\*:\s*(\w+)', content)
    if type_match:
        config['plan_type'] = type_match.group(1)

    # Extract from Build Configuration table
    build_table = re.search(r'\|\s*Property\s*\|\s*Value\s*\|.*?\n\|[-\s|]+\n((?:\|[^\n]+\n)+)', content)
    if build_table:
        for row in build_table.group(1).strip().split('\n'):
            cols = [c.strip() for c in row.split('|')[1:-1]]
            if len(cols) >= 2:
                key = cols[0].lower().replace(' ', '_')
                value = cols[1]
                config[key] = value

    return config


def parse_references_md(references_file: Path) -> dict:
    """Parse references.md for reference information."""
    if not references_file.exists():
        return {}

    content = references_file.read_text()

    refs = {}

    # Extract issue
    issue_match = re.search(r'\*\*Issue\*\*:\s*\[([^\]]+)\]\(([^)]+)\)', content)
    if issue_match:
        refs['issue'] = {
            'title': issue_match.group(1),
            'url': issue_match.group(2)
        }

    # Extract branch
    branch_match = re.search(r'\*\*Branch\*\*:\s*`([^`]+)`', content)
    if branch_match:
        refs['branch'] = branch_match.group(1)

    # Count ADRs
    adrs = re.findall(r'ADR-\d+', content)
    if adrs:
        refs['adrs'] = list(set(adrs))

    # Count interfaces
    interfaces = re.findall(r'IF-\d+', content)
    if interfaces:
        refs['interfaces'] = list(set(interfaces))

    return refs


def calculate_overall_progress(phases: list) -> float:
    """Calculate overall progress percentage."""
    total_tasks = sum(p.get('total_count', 0) for p in phases)
    completed_tasks = sum(p.get('completed_count', 0) for p in phases)

    if total_tasks == 0:
        return 0.0

    return round(completed_tasks / total_tasks * 100, 1)


def determine_overall_status(phases: list, current_phase: str) -> str:
    """Determine overall plan status."""
    if not phases:
        return 'pending'

    all_completed = all(p.get('status') == 'completed' for p in phases)
    if all_completed:
        return 'completed'

    if current_phase:
        return 'in_progress'

    return 'pending'


def get_status(plan_directory: str) -> dict:
    """Get comprehensive plan status."""
    plan_dir = Path(plan_directory)

    if not plan_dir.exists():
        return {
            'error': {
                'type': 'directory_not_found',
                'message': f'Plan directory not found: {plan_directory}'
            }
        }

    plan_file = plan_dir / 'plan.md'
    config_file = plan_dir / 'config.md'
    references_file = plan_dir / 'references.md'

    # Parse plan.md
    plan_data = parse_plan_md(plan_file)
    if 'error' in plan_data:
        return {
            'error': {
                'type': 'plan_parse_error',
                'message': plan_data['error']
            }
        }

    # Parse config.md
    config_data = parse_config_md(config_file)

    # Parse references.md
    refs_data = parse_references_md(references_file)

    # Calculate progress
    overall_progress = calculate_overall_progress(plan_data.get('phases', []))
    overall_status = determine_overall_status(
        plan_data.get('phases', []),
        plan_data.get('current_phase', '')
    )

    # Get plan name from directory
    plan_name = plan_dir.name

    # Build result
    result = {
        'plan_status': {
            'name': plan_name,
            'title': plan_data.get('title', ''),
            'plan_type': config_data.get('plan_type', 'implementation'),
            'overall_status': overall_status,
            'overall_progress': overall_progress
        },
        'phase_progress': plan_data.get('phases', []),
        'current_focus': {
            'phase': plan_data.get('current_phase', ''),
            'task': plan_data.get('current_task', ''),
            'task_name': plan_data.get('current_task_name', '')
        },
        'configuration': {
            'technology': config_data.get('technology', ''),
            'build_system': config_data.get('build_system', ''),
            'branch': refs_data.get('branch', config_data.get('branch', '')),
            'compatibility': config_data.get('compatibility', ''),
            'commit_strategy': config_data.get('commit_strategy', ''),
            'finalizing': config_data.get('finalizing', '')
        },
        'references': {
            'issue': refs_data.get('issue'),
            'adrs': refs_data.get('adrs', []),
            'interfaces': refs_data.get('interfaces', [])
        },
        'plan_directory': plan_directory
    }

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Get comprehensive plan status.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output JSON structure:
{
  "plan_status": {
    "name": "jwt-auth",
    "title": "Implement JWT Authentication",
    "plan_type": "implementation",
    "overall_status": "in_progress",
    "overall_progress": 65.0
  },
  "phase_progress": [
    {"phase": "init", "status": "completed", "tasks": 5, "completed": "5/5"},
    {"phase": "refine", "status": "completed", "tasks": 3, "completed": "3/3"},
    {"phase": "implement", "status": "in_progress", "tasks": 7, "completed": "5/7"},
    {"phase": "verify", "status": "pending", "tasks": 4, "completed": "0/4"},
    {"phase": "finalize", "status": "pending", "tasks": 3, "completed": "0/3"}
  ],
  "current_focus": {
    "phase": "implement",
    "task": "task-12",
    "task_name": "Implement RefreshTokenService"
  },
  "configuration": {...},
  "references": {...}
}
"""
    )
    parser.add_argument('plan_directory', help='Path to plan directory')

    args = parser.parse_args()

    result = get_status(args.plan_directory)
    print(json.dumps(result, indent=2))

    # Exit with error code if there was an error
    if 'error' in result:
        sys.exit(1)


if __name__ == '__main__':
    main()
