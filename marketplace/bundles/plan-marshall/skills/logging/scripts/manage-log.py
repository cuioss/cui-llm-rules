#!/usr/bin/env python3
"""
CLI script for unified logging operations.

Usage:
    python3 manage-log.py {type} {plan_id} {level} "{message}"

Arguments:
    type      - Log type: 'script' or 'work'
    plan_id   - Plan identifier
    level     - Log level: SUCCESS, ERROR, INFO, WARN
    message   - Log message

Examples:
    python3 manage-log.py script my-plan SUCCESS "pm-workflow:manage-task:manage-task add (0.15s)"
    python3 manage-log.py work my-plan INFO "Created deliverable: auth module"
    python3 manage-log.py work my-plan WARN "Skipped validation"
"""

import sys
from pathlib import Path

# Add scripts directory to path for imports
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from plan_logging import log_entry

VALID_TYPES = ('script', 'work')
VALID_LEVELS = ('SUCCESS', 'ERROR', 'INFO', 'WARN')


def main():
    if len(sys.argv) != 5:
        print(f"Usage: {sys.argv[0]} {{type}} {{plan_id}} {{level}} \"{{message}}\"", file=sys.stderr)
        sys.exit(1)

    log_type, plan_id, level, message = sys.argv[1:5]

    # Validate type
    if log_type not in VALID_TYPES:
        print(f"Error: type must be one of {VALID_TYPES}", file=sys.stderr)
        sys.exit(1)

    # Validate level
    if level not in VALID_LEVELS:
        print(f"Error: level must be one of {VALID_LEVELS}", file=sys.stderr)
        sys.exit(1)

    # Log entry
    try:
        log_entry(log_type, plan_id, level, message)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
