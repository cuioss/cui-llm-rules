---
name: file-operations-base
description: Base module providing reusable file operations patterns for .claude directory scripts
allowed-tools: Bash
---

# File Operations Base Skill

**Role**: Shared Python module providing atomic file operations, metadata parsing, and JSON output helpers for `.claude/` directory scripts.

## What This Skill Provides

- Atomic file write (temp file + rename pattern)
- Directory creation (mkdir -p equivalent)
- JSON success/error output helpers
- Markdown key=value metadata parsing
- Markdown metadata generation

## When to Use

Import `file_ops` module in Python scripts that write to `.claude/` directories:
- Lessons learned scripts
- Plan file scripts
- Memory management scripts
- Any script requiring atomic writes

## Module: file_ops.py

**Location**: `scripts/file_ops.py`

### Functions

**1. atomic_write_file(path, content)**
- **Purpose**: Write file atomically using temp file + rename
- **Input**: `path` (str/Path), `content` (str)
- **Output**: None (raises on error)
- **Pattern**: Creates temp file, writes, renames to target

**2. ensure_directory(path)**
- **Purpose**: Create directory and parents if needed
- **Input**: `path` (str/Path) - file or directory path
- **Output**: None
- **Note**: If path looks like file, creates parent directory

**3. output_success(operation, **kwargs)**
- **Purpose**: Print JSON success output to stdout
- **Input**: `operation` (str), additional kwargs
- **Output**: Prints JSON to stdout

**4. output_error(operation, error)**
- **Purpose**: Print JSON error output to stderr
- **Input**: `operation` (str), `error` (str)
- **Output**: Prints JSON to stderr

**5. parse_markdown_metadata(content)**
- **Purpose**: Parse key=value metadata from markdown
- **Input**: `content` (str) - full file content
- **Output**: `dict` - metadata key-value pairs
- **Format**: Supports `key=value` and `key.subkey=value` (dot notation)

**6. generate_markdown_metadata(data)**
- **Purpose**: Generate key=value metadata block
- **Input**: `data` (dict) - metadata to serialize
- **Output**: `str` - formatted metadata block

---

## Usage Example

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/path/to/file-operations-base/scripts')
from file_ops import (
    atomic_write_file,
    ensure_directory,
    output_success,
    output_error,
    parse_markdown_metadata,
    generate_markdown_metadata
)

def main():
    try:
        # Ensure directory exists
        ensure_directory('.claude/lessons-learned/')

        # Generate metadata
        metadata = generate_markdown_metadata({
            'id': '2025-11-28-001',
            'component.type': 'command',
            'applied': 'false'
        })

        # Write atomically
        content = f"{metadata}\n# Lesson Title\n\nContent here..."
        atomic_write_file('.claude/lessons-learned/2025-11-28-001.md', content)

        output_success('write-lesson', file='.claude/lessons-learned/2025-11-28-001.md')
    except Exception as e:
        output_error('write-lesson', str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()
```

---

## Scripts

| Script | Purpose |
|--------|---------|
| `file_ops.py` | Core file operations module (importable) |
| `test-file-ops.py` | Test suite for file operations |

---

## Integration

### With claude-lessons-learned

```python
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'file-operations-base' / 'scripts'))
from file_ops import atomic_write_file, output_success, output_error
```

### With plan-files

```python
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / 'cui-utilities' / 'skills' / 'file-operations-base' / 'scripts'))
from file_ops import atomic_write_file, output_success, output_error
```

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] Stdlib-only (no external dependencies)
- [x] JSON output format
- [x] Comprehensive test coverage
- [x] Error handling for all scenarios
