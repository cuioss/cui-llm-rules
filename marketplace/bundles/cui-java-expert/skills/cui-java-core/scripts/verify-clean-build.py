#!/usr/bin/env python3
"""
Verify Maven build output for clean compilation.

Parses Maven build logs to extract compilation errors and warnings,
categorizing them by type and severity.

Output: JSON with build status for Claude to process.
"""

import argparse
import json
import re
import sys
from typing import List, Dict, Any, Optional


# Maven error patterns
ERROR_PATTERNS = [
    # Compilation errors
    (r'\[ERROR\]\s+(.+?\.java):\[(\d+),(\d+)\]\s+(.+)', 'compilation_error'),
    (r'\[ERROR\]\s+(.+?\.java):\[(\d+)\]\s+(.+)', 'compilation_error'),

    # Symbol errors
    (r'cannot find symbol', 'symbol_error'),
    (r'symbol:\s+(.+)', 'symbol_detail'),

    # Type errors
    (r'incompatible types', 'type_error'),

    # Method errors
    (r'method\s+(\w+).+cannot be applied', 'method_error'),
]

# Maven warning patterns
WARNING_PATTERNS = [
    # Compiler warnings
    (r'\[WARNING\]\s+(.+?\.java):\[(\d+),(\d+)\]\s+(.+)', 'compiler_warning'),
    (r'\[WARNING\]\s+(.+?\.java):\[(\d+)\]\s+(.+)', 'compiler_warning'),

    # Specific warning types
    (r'unchecked conversion', 'unchecked_conversion'),
    (r'unchecked call', 'unchecked_call'),
    (r'Deprecated', 'deprecated_api'),
    (r'unused', 'unused_code'),
    (r'raw type', 'raw_type'),
]

# Build system warnings (low severity)
BUILD_SYSTEM_WARNING_PATTERNS = [
    (r"'version' for .+ is missing", 'missing_version'),
    (r"Using platform encoding", 'platform_encoding'),
    (r"deprecated", 'deprecated_config'),
]


def parse_error_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse Maven error line to extract details."""
    # Pattern: [ERROR] /path/to/File.java:[line,col] message
    match = re.search(r'\[ERROR\]\s+(.+?\.java):\[(\d+)(?:,(\d+))?\]\s+(.+)', line)
    if match:
        file_path = match.group(1)
        line_num = int(match.group(2))
        col_num = int(match.group(3)) if match.group(3) else None
        message = match.group(4).strip()

        # Determine error type
        error_type = 'compilation_error'
        if 'cannot find symbol' in message:
            error_type = 'symbol_error'
        elif 'incompatible types' in message:
            error_type = 'type_error'
        elif 'method' in message and 'cannot be applied' in message:
            error_type = 'method_error'

        return {
            'file': file_path,
            'line': line_num,
            'column': col_num,
            'message': message,
            'type': error_type
        }

    return None


def parse_warning_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse Maven warning line to extract details."""
    # Pattern: [WARNING] /path/to/File.java:[line,col] message
    match = re.search(r'\[WARNING\]\s+(.+?\.java):\[(\d+)(?:,(\d+))?\]\s+(.+)', line)
    if match:
        file_path = match.group(1)
        line_num = int(match.group(2))
        col_num = int(match.group(3)) if match.group(3) else None
        message = match.group(4).strip()

        # Determine warning type
        warning_type = 'compiler_warning'
        if 'unchecked conversion' in message:
            warning_type = 'unchecked_conversion'
        elif 'unchecked call' in message:
            warning_type = 'unchecked_call'
        elif 'Deprecated' in message:
            warning_type = 'deprecated_api'
        elif 'unused' in message.lower():
            warning_type = 'unused_code'
        elif 'raw type' in message:
            warning_type = 'raw_type'

        return {
            'file': file_path,
            'line': line_num,
            'column': col_num,
            'message': message,
            'type': warning_type
        }

    # Check for build system warnings
    for pattern, warning_type in BUILD_SYSTEM_WARNING_PATTERNS:
        if re.search(pattern, line, re.IGNORECASE):
            return {
                'file': None,
                'line': None,
                'column': None,
                'message': line.strip(),
                'type': warning_type
            }

    return None


def extract_context_lines(lines: List[str], error_idx: int, context_size: int = 3) -> List[str]:
    """Extract context lines around error."""
    start = max(0, error_idx - context_size)
    end = min(len(lines), error_idx + context_size + 1)
    return lines[start:end]


def parse_build_log(log_path: str) -> Dict[str, Any]:
    """Parse Maven build log to extract errors and warnings."""
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except IOError as e:
        return {
            'status': 'error',
            'data': {
                'message': f'Failed to read log file: {e}',
                'errors': [],
                'warnings': []
            }
        }

    errors = []
    warnings = []
    current_error = None

    for i, line in enumerate(lines):
        # Parse errors
        if '[ERROR]' in line:
            error = parse_error_line(line)
            if error:
                # Add context
                context = extract_context_lines(lines, i, 2)
                error['context'] = ''.join(context).strip()
                errors.append(error)
                current_error = error
            # Handle symbol details on next line
            elif current_error and 'symbol:' in line:
                symbol_match = re.search(r'symbol:\s+(.+)', line)
                if symbol_match:
                    current_error['symbol'] = symbol_match.group(1).strip()

        # Parse warnings
        elif '[WARNING]' in line:
            warning = parse_warning_line(line)
            if warning:
                # Add context for code warnings
                if warning['file']:
                    context = extract_context_lines(lines, i, 2)
                    warning['context'] = ''.join(context).strip()
                warnings.append(warning)

    # Determine status
    if errors:
        build_status = 'has-errors'
    elif warnings:
        build_status = 'has-warnings'
    else:
        build_status = 'clean'

    # Return in wrapper format expected by tests
    return {
        'status': build_status,
        'data': {
            'errors': errors,
            'warnings': warnings,
            'summary': {
                'error_count': len(errors),
                'warning_count': len(warnings)
            }
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description='Verify Maven build output for clean compilation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse build log
  %(prog)s --log-file target/build-output.log

  # Output to file
  %(prog)s --log-file target/build-output.log --output verification.json

Output:
  {
    "status": "clean|has-errors|has-warnings",
    "data": {
      "errors": [...],
      "warnings": [...],
      "summary": {
        "error_count": 0,
        "warning_count": 0
      }
    }
  }

Status Values:
  clean: No errors or warnings
  has-errors: Compilation errors found
  has-warnings: Compiler warnings found (no errors)
        """
    )

    parser.add_argument(
        '--log-file',
        type=str,
        required=True,
        help='Path to Maven build log file'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output JSON file (default: stdout)'
    )

    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON output'
    )

    args = parser.parse_args()

    # Parse log
    result = parse_build_log(args.log_file)

    # Output
    indent = 2 if args.pretty else None
    output_json = json.dumps(result, indent=indent)

    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_json)
        except IOError as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_json)

    # Exit with status based on verification
    # 0: Clean build
    # 1: Errors or warnings found
    sys.exit(0 if result['status'] == 'clean' else 1)


if __name__ == '__main__':
    main()
