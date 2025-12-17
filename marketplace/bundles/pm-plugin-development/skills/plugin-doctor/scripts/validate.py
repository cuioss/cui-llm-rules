#!/usr/bin/env python3
"""
validate.py - Plugin validation and inventory tools.

Consolidated from:
- validate-references.py → references subcommand
- verify-cross-file-findings.py → cross-file subcommand
- scan-skill-inventory.py → inventory subcommand

Validates plugin components and manages skill inventory.

Output: JSON to stdout.

Usage:
    validate.py references --file <markdown-file>
    validate.py cross-file --analysis <json-file> [--llm-findings <json-file>]
    validate.py inventory --skill-path <directory>
"""

import argparse
import sys

from cmd_references import cmd_references
from cmd_cross_file import cmd_cross_file
from cmd_inventory import cmd_inventory


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Plugin validation and inventory tools',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate plugin references
  %(prog)s references --file agent.md

  # Verify cross-file findings
  %(prog)s cross-file --analysis analysis.json --llm-findings findings.json

  # Scan skill inventory
  %(prog)s inventory --skill-path skills/plugin-doctor
"""
    )

    subparsers = parser.add_subparsers(dest='command', help='Operation to perform')

    # references subcommand
    p_refs = subparsers.add_parser('references', help='Validate plugin references')
    p_refs.add_argument('--file', '-f', required=True, help='Path to markdown file')
    p_refs.set_defaults(func=cmd_references)

    # cross-file subcommand
    p_cross = subparsers.add_parser('cross-file', help='Verify cross-file findings')
    p_cross.add_argument('--analysis', '-a', required=True, help='Path to script analysis JSON')
    p_cross.add_argument('--llm-findings', '-l', help='Path to LLM findings JSON (stdin if omitted)')
    p_cross.set_defaults(func=cmd_cross_file)

    # inventory subcommand
    p_inv = subparsers.add_parser('inventory', help='Scan skill inventory')
    p_inv.add_argument('--skill-path', '-s', required=True, help='Path to skill directory')
    p_inv.add_argument('--include-hidden', action='store_true', help='Include hidden files')
    p_inv.set_defaults(func=cmd_inventory)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
