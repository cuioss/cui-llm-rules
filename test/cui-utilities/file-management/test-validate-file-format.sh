#!/bin/bash
# Test suite for validate-file-format.py
# Tests JSON file format validation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT="$PROJECT_ROOT/marketplace/bundles/cui-utilities/skills/file-management/scripts/validate-file-format.py"
FIXTURES="$SCRIPT_DIR/fixtures"
TEMP_DIR=$(mktemp -d)

# Cleanup on exit
trap "rm -rf $TEMP_DIR" EXIT

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

TESTS_RUN=0
TESTS_PASSED=0

# Test helper functions
pass() {
    echo -e "${GREEN}PASS${NC}: $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

fail() {
    echo -e "${RED}FAIL${NC}: $1"
    echo "  Expected: $2"
    echo "  Got: $3"
}

run_test() {
    TESTS_RUN=$((TESTS_RUN + 1))
    "$@"
}

# Create test fixtures
setup_fixtures() {
    mkdir -p "$TEMP_DIR/.claude/memory/context"

    # Valid run-configuration.json
    cat > "$TEMP_DIR/run-configuration.json" << 'EOF'
{
  "version": 1,
  "commands": {
    "test-cmd": {
      "last_execution": {
        "date": "2025-11-25",
        "status": "SUCCESS"
      }
    }
  }
}
EOF

    # Invalid run-configuration.json (missing version)
    cat > "$TEMP_DIR/invalid-run-config.json" << 'EOF'
{
  "commands": {
    "test-cmd": {}
  }
}
EOF

    # Valid scripts.local.json
    cat > "$TEMP_DIR/scripts.local.json" << 'EOF'
{
  "version": 1,
  "scripts": {
    "test:skill/scripts/test.py": {
      "absolute": "/path/to/script.py",
      "type": "python"
    }
  },
  "permissions": ["Bash(python3 /path/to/script.py:*)"]
}
EOF

    # Invalid scripts.local.json (missing permissions)
    cat > "$TEMP_DIR/invalid-scripts.json" << 'EOF'
{
  "version": 1,
  "scripts": {}
}
EOF

    # Valid settings.local.json
    cat > "$TEMP_DIR/settings.local.json" << 'EOF'
{
  "allow": ["Bash(./mvnw:*)"],
  "deny": []
}
EOF

    # Valid memory file
    cat > "$TEMP_DIR/.claude/memory/context/test-memory.json" << 'EOF'
{
  "meta": {
    "created": "2025-11-25T10:30:00Z",
    "category": "context",
    "summary": "test-feature"
  },
  "content": {
    "decisions": ["Use JWT"]
  }
}
EOF

    # Invalid memory file (missing meta)
    cat > "$TEMP_DIR/invalid-memory.json" << 'EOF'
{
  "content": {
    "test": true
  }
}
EOF

    # Invalid JSON syntax
    cat > "$TEMP_DIR/invalid-json.json" << 'EOF'
{
  "broken": true,
  missing-quotes: "value"
}
EOF
}

# Test: validate valid run-configuration.json
test_valid_run_config() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/run-configuration.json" --format run-config 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['valid'] else 1)" 2>/dev/null; then
        pass "validate valid run-configuration.json"
    else
        fail "validate valid run-configuration.json" "valid=true" "$result"
    fi
}

# Test: validate invalid run-configuration.json
test_invalid_run_config() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/invalid-run-config.json" --format run-config 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and not d['valid'] else 1)" 2>/dev/null; then
        pass "detect invalid run-configuration.json"
    else
        fail "detect invalid run-configuration.json" "valid=false" "$result"
    fi
}

# Test: validate valid scripts.local.json
test_valid_scripts_local() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/scripts.local.json" --format scripts-local 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['valid'] else 1)" 2>/dev/null; then
        pass "validate valid scripts.local.json"
    else
        fail "validate valid scripts.local.json" "valid=true" "$result"
    fi
}

# Test: validate invalid scripts.local.json
test_invalid_scripts_local() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/invalid-scripts.json" --format scripts-local 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and not d['valid'] else 1)" 2>/dev/null; then
        pass "detect invalid scripts.local.json"
    else
        fail "detect invalid scripts.local.json" "valid=false" "$result"
    fi
}

# Test: validate valid settings.local.json
test_valid_settings_local() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/settings.local.json" --format settings-local 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['valid'] else 1)" 2>/dev/null; then
        pass "validate valid settings.local.json"
    else
        fail "validate valid settings.local.json" "valid=true" "$result"
    fi
}

# Test: validate valid memory file
test_valid_memory() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/.claude/memory/context/test-memory.json" --format memory 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['valid'] else 1)" 2>/dev/null; then
        pass "validate valid memory file"
    else
        fail "validate valid memory file" "valid=true" "$result"
    fi
}

# Test: validate invalid memory file
test_invalid_memory() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/invalid-memory.json" --format memory 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and not d['valid'] else 1)" 2>/dev/null; then
        pass "detect invalid memory file"
    else
        fail "detect invalid memory file" "valid=false" "$result"
    fi
}

# Test: detect invalid JSON syntax
test_invalid_json_syntax() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/invalid-json.json" --format run-config 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and not d['valid'] else 1)" 2>/dev/null; then
        pass "detect invalid JSON syntax"
    else
        fail "detect invalid JSON syntax" "valid=false" "$result"
    fi
}

# Test: auto-detect format from path
test_auto_detect_format() {
    setup_fixtures
    # Copy to path that can be auto-detected
    cp "$TEMP_DIR/run-configuration.json" "$TEMP_DIR/test-run-configuration.json"

    result=$(python3 "$SCRIPT" "$TEMP_DIR/test-run-configuration.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['format']=='run-config' else 1)" 2>/dev/null; then
        pass "auto-detect format from path"
    else
        fail "auto-detect format from path" "format=run-config" "$result"
    fi
}

# Test: checks array in output
test_checks_array() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/run-configuration.json" --format run-config 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and len(d['checks'])>0 else 1)" 2>/dev/null; then
        pass "output includes checks array"
    else
        fail "output includes checks array" "checks array with items" "$result"
    fi
}

# Test: file not found error
test_file_not_found() {
    result=$(python3 "$SCRIPT" "$TEMP_DIR/nonexistent.json" --format run-config 2>&1 || true)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if not d['success'] else 1)" 2>/dev/null; then
        pass "file not found returns error"
    else
        fail "file not found returns error" "success=false" "$result"
    fi
}

# Test: empty object is valid settings
test_empty_settings_valid() {
    echo '{}' > "$TEMP_DIR/empty-settings.json"
    result=$(python3 "$SCRIPT" "$TEMP_DIR/empty-settings.json" --format settings-local 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['valid'] else 1)" 2>/dev/null; then
        pass "empty object is valid settings"
    else
        fail "empty object is valid settings" "valid=true" "$result"
    fi
}

# Run all tests
echo "========================================"
echo "Testing validate-file-format.py"
echo "========================================"
echo ""

run_test test_valid_run_config
run_test test_invalid_run_config
run_test test_valid_scripts_local
run_test test_invalid_scripts_local
run_test test_valid_settings_local
run_test test_valid_memory
run_test test_invalid_memory
run_test test_invalid_json_syntax
run_test test_auto_detect_format
run_test test_checks_array
run_test test_file_not_found
run_test test_empty_settings_valid

echo ""
echo "========================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN tests passed"
echo "========================================"

if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    exit 0
else
    exit 1
fi
