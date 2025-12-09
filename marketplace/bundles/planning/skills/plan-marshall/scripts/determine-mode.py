#!/usr/bin/env python3
"""
Determine the operational mode for plan-marshall.

Returns either 'wizard' or 'menu' based on the existence of:
- .plan/execute-script.py (executor)
- .plan/marshal.json (configuration)

Usage:
    python3 determine-mode.py [--plan-dir PATH]

Options:
    --plan-dir PATH    Directory to check (default: .plan)

Output (TOON format):
    mode	wizard
    reason	executor_missing

    mode	menu
    reason	both_exist
"""

import argparse
import sys
from pathlib import Path


def determine_mode(plan_dir: Path) -> tuple[str, str]:
    """
    Determine operational mode based on existing files.

    Args:
        plan_dir: Path to the .plan directory

    Returns:
        Tuple of (mode, reason) where mode is 'wizard' or 'menu'
    """
    executor_path = plan_dir / "execute-script.py"
    marshal_path = plan_dir / "marshal.json"

    executor_exists = executor_path.exists()
    marshal_exists = marshal_path.exists()

    if not executor_exists:
        return "wizard", "executor_missing"
    elif not marshal_exists:
        return "wizard", "marshal_missing"
    else:
        return "menu", "both_exist"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Determine plan-marshall operational mode"
    )
    parser.add_argument(
        "--plan-dir",
        type=str,
        default=".plan",
        help="Directory to check (default: .plan)"
    )

    args = parser.parse_args()
    plan_dir = Path(args.plan_dir)

    mode, reason = determine_mode(plan_dir)

    # Output in TOON format
    print(f"mode\t{mode}")
    print(f"reason\t{reason}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
