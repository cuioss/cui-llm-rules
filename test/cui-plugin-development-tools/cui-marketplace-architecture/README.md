# Test Suite: cui-marketplace-architecture

Tests for scripts and utilities in the `cui-marketplace-architecture` skill.

## Structure

```
test/cui-plugin-development-tools/cui-marketplace-architecture/
├── README.md                         # This file
├── test-analyze-markdown-file.sh     # Test suite for analyze-markdown-file.sh
└── fixtures/                         # Test fixtures (if needed)
```

## Running Tests

### Test analyze-markdown-file.sh

```bash
./test/cui-plugin-development-tools/cui-marketplace-architecture/test-analyze-markdown-file.sh
```

**What it tests:**
- Line count accuracy (must match `wc -l` exactly)
- CONTINUOUS IMPROVEMENT RULE detection
- YAML frontmatter extraction
- JSON output structure
- Bloat classification logic (ACCEPTABLE/LARGE/BLOATED)

**Test files:**
Uses real marketplace command files as test subjects:
- plugin-diagnose-skills.md (LARGE, 443 lines)
- orchestrate-language.md (ACCEPTABLE)
- js-implement-code.md (BLOATED, 521 lines)
- java-implement-code.md (BLOATED, 503 lines)

## Test Philosophy

- **Deterministic**: Tests use real files with known properties
- **Self-verifying**: Compares script output against `wc -l`
- **Comprehensive**: Tests all major features of the script
- **Independent**: Can run without full marketplace installation

## Adding New Tests

To add tests for a new script:

1. Create test file: `test-{script-name}.sh`
2. Make it executable: `chmod +x test-{script-name}.sh`
3. Follow the pattern in `test-analyze-markdown-file.sh`
4. Update this README

## Requirements

- `bash` 4.0+
- `jq` (for JSON parsing)
- Access to marketplace command files
