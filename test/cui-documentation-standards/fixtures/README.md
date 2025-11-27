# Test Fixtures

This directory contains test fixtures for cui-documentation-standards scripts.

## Purpose

Test files are created dynamically by test scripts and cleaned up after execution.

## Test Scripts

- `test-verify-links-false-positives.sh` - Tests link classification script
- `test-analyze-content-tone.sh` - Tests content tone analysis script

## Usage

```bash
# Run individual test
bash test/cui-documentation-standards/test-verify-links-false-positives.sh

# Run all tests
bash test/cui-documentation-standards/test-*.sh
```
