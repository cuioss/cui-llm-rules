#!/usr/bin/env python3
"""
Discover plans in the workspace.

Usage:
    python3 discover-plans.py [search_path]
    python3 discover-plans.py [search_path] --filter=init
    python3 discover-plans.py [search_path] --filter=implement,verify,finalize
    python3 discover-plans.py [search_path] --filter=completed
    python3 discover-plans.py --help

Output: JSON with plans array and recommendation.

Filter options:
    - Phases: init, refine, implement, verify, finalize
    - Statuses: completed, in_progress, pending
    - Multiple filters: comma-separated (e.g., --filter=implement,verify)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Valid filter values
# Note: 'execute' is used by Simple plan type (3-phase: init→execute→finalize)
# while 'implement' is used by Implementation plan type (5-phase: init→refine→implement→verify→finalize)
VALID_PHASES = {'init', 'refine', 'implement', 'execute', 'verify', 'finalize'}
VALID_STATUSES = {'completed', 'in_progress', 'pending'}
VALID_FILTERS = VALID_PHASES | VALID_STATUSES


def parse_plan_header(content: str) -> dict:
    """Extract current phase and status from plan.md content."""
    current_phase = ''
    current_task = ''

    phase_match = re.search(r'\*\*Current Phase\*\*:\s*(\w+)', content)
    if phase_match:
        current_phase = phase_match.group(1)

    task_match = re.search(r'\*\*Current Task\*\*:\s*([^\n]+)', content)
    if task_match:
        current_task = task_match.group(1).strip()

    # Determine status from phase progress table
    status = 'pending'
    if re.search(r'\|\s*finalize\s*\|\s*completed\s*\|', content, re.IGNORECASE):
        status = 'completed'
    elif current_phase:
        status = 'in_progress'

    return {
        'current_phase': current_phase,
        'current_task': current_task,
        'status': status
    }


def parse_plan_title(content: str) -> str:
    """Extract plan title from first H1 header."""
    match = re.search(r'^#\s+(?:Task Plan:\s*)?(.+)$', content, re.MULTILINE)
    return match.group(1).strip() if match else ''


def parse_filter(filter_str: str) -> tuple:
    """Parse filter string into phase and status filters.

    Args:
        filter_str: Comma-separated filter values (e.g., 'init,refine' or 'completed')

    Returns:
        Tuple of (phase_filters, status_filters) sets
    """
    if not filter_str:
        return set(), set()

    phase_filters = set()
    status_filters = set()

    for value in filter_str.split(','):
        value = value.strip().lower()
        if value in VALID_PHASES:
            phase_filters.add(value)
        elif value in VALID_STATUSES:
            status_filters.add(value)
        # Ignore invalid filter values silently

    return phase_filters, status_filters


def matches_filter(plan: dict, phase_filters: set, status_filters: set) -> bool:
    """Check if a plan matches the given filters.

    Args:
        plan: Plan dictionary with 'phase' and 'status' keys
        phase_filters: Set of phase values to match
        status_filters: Set of status values to match

    Returns:
        True if plan matches all provided filters
    """
    # If no filters, match everything
    if not phase_filters and not status_filters:
        return True

    # Check phase filter (if any phases specified)
    if phase_filters:
        plan_phase = plan.get('phase', '').lower()
        if plan_phase not in phase_filters:
            return False

    # Check status filter (if any statuses specified)
    if status_filters:
        plan_status = plan.get('status', '').lower()
        if plan_status not in status_filters:
            return False

    return True


def discover_plans(search_path: str, filter_str: str = None) -> dict:
    """Find all plans in the search path, optionally filtered.

    Args:
        search_path: Directory to search for plans
        filter_str: Optional filter string (e.g., 'init', 'implement,verify', 'completed')

    Returns:
        Dictionary with plans array, counts, and recommendation
    """
    search_dir = Path(search_path)

    if not search_dir.exists():
        result = {
            'plans': [],
            'count': 0,
            'recommendation': None,
            'message': f'Search directory does not exist: {search_path}'
        }
        if filter_str:
            result['filter_applied'] = filter_str
            result['filtered_count'] = 0
        return result

    all_plans = []
    plan_dirs = []

    # Find all plan.md files
    for plan_file in search_dir.glob('*/plan.md'):
        plan_dirs.append((plan_file.parent, plan_file))

    # Sort by modification time (most recent first)
    plan_dirs.sort(key=lambda x: x[1].stat().st_mtime, reverse=True)

    for plan_dir, plan_file in plan_dirs:
        try:
            content = plan_file.read_text()
            header = parse_plan_header(content)
            title = parse_plan_title(content)

            # Use directory name as plan name
            plan_name = plan_dir.name

            all_plans.append({
                'name': plan_name,
                'title': title,
                'path': str(plan_dir),
                'phase': header['current_phase'],
                'task': header['current_task'],
                'status': header['status'],
                'modified': plan_file.stat().st_mtime
            })
        except Exception as e:
            # Skip plans that can't be read
            all_plans.append({
                'name': plan_dir.name,
                'title': '',
                'path': str(plan_dir),
                'phase': '',
                'task': '',
                'status': 'error',
                'error': str(e)
            })

    # Apply filters if provided
    phase_filters, status_filters = parse_filter(filter_str)
    if phase_filters or status_filters:
        plans = [p for p in all_plans if matches_filter(p, phase_filters, status_filters)]
    else:
        plans = all_plans

    # Determine recommendation (from filtered results)
    recommendation = None
    if plans:
        # Prefer most recent in-progress plan
        in_progress = [p for p in plans if p['status'] == 'in_progress']
        if in_progress:
            recommendation = in_progress[0]['name']
        else:
            # Fall back to most recent overall
            recommendation = plans[0]['name']

    result = {
        'plans': plans,
        'count': len(all_plans),
        'recommendation': recommendation,
        'search_path': search_path
    }

    # Add filter info if filter was applied
    if filter_str:
        result['filter_applied'] = filter_str
        result['filtered_count'] = len(plans)

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Discover plans in the workspace.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output JSON structure:
{
  "plans": [
    {
      "name": "plan-name",
      "title": "Plan Title",
      "path": ".cui/plans/plan-name/",
      "phase": "implement",
      "task": "task-6",
      "status": "in_progress"
    }
  ],
  "count": 1,
  "recommendation": "plan-name",
  "search_path": ".cui/plans/",
  "filter_applied": "implement",
  "filtered_count": 1
}

Filter examples:
  --filter=init                    # Plans in init phase
  --filter=refine                  # Plans in refine phase
  --filter=implement,verify,finalize  # Executable plans
  --filter=completed               # Completed plans
  --filter=in_progress             # In-progress plans
"""
    )
    parser.add_argument(
        'search_path',
        nargs='?',
        default='.cui/plans/',
        help='Path to search for plans (default: .cui/plans/)'
    )
    parser.add_argument(
        '--filter',
        dest='filter_str',
        default=None,
        help='Filter by phase (init,refine,implement,verify,finalize) or status (completed,in_progress,pending). Comma-separated for multiple values.'
    )

    args = parser.parse_args()

    result = discover_plans(args.search_path, args.filter_str)
    print(json.dumps(result, indent=2))

    # Exit 0 even for empty results (not an error)
    sys.exit(0)


if __name__ == '__main__':
    main()
