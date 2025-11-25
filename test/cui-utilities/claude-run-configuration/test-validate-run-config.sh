#!/bin/bash
# Test suite for validate-run-config.py
# Tests run-configuration.json format validation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT="$PROJECT_ROOT/marketplace/bundles/cui-utilities/skills/claude-run-configuration/scripts/validate-run-config.py"
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
    cat > "$TEMP_DIR/missing-version.json" << 'EOF'
{
  "commands": {
    "test-cmd": {}
  }
}
EOF

    # Invalid run-configuration.json (missing commands)
    cat > "$TEMP_DIR/missing-commands.json" << 'EOF'
{
  "version": 1
}
EOF

    # Invalid run-configuration.json (wrong version type)
    cat > "$TEMP_DIR/wrong-version-type.json" << 'EOF'
{
  "version": "1",
  "commands": {}
}
EOF

    # Valid with maven section
    cat > "$TEMP_DIR/with-maven.json" << 'EOF'
{
  "version": 1,
  "commands": {},
  "maven": {
    "build": {
      "last_execution": {
        "duration_ms": 45000
      }
    }
  }
}
EOF

    # Valid with agent_decisions section
    cat > "$TEMP_DIR/with-agent-decisions.json" << 'EOF'
{
  "version": 1,
  "commands": {},
  "agent_decisions": {
    "test-agent": {
      "status": "keep-monolithic",
      "decision_date": "2025-11-25"
    }
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
    result=$(python3 "$SCRIPT" "$TEMP_DIR/run-configuration.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['valid'] else 1)" 2>/dev/null; then
        pass "validate valid run-configuration.json"
    else
        fail "validate valid run-configuration.json" "valid=true" "$result"
    fi
}

# Test: validate invalid run-configuration.json (missing version)
test_missing_version() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/missing-version.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and not d['valid'] else 1)" 2>/dev/null; then
        pass "detect missing version"
    else
        fail "detect missing version" "valid=false" "$result"
    fi
}

# Test: validate invalid run-configuration.json (missing commands)
test_missing_commands() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/missing-commands.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and not d['valid'] else 1)" 2>/dev/null; then
        pass "detect missing commands"
    else
        fail "detect missing commands" "valid=false" "$result"
    fi
}

# Test: validate wrong version type
test_wrong_version_type() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/wrong-version-type.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and not d['valid'] else 1)" 2>/dev/null; then
        pass "detect wrong version type"
    else
        fail "detect wrong version type" "valid=false" "$result"
    fi
}

# Test: validate with maven section
test_with_maven() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/with-maven.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['valid'] else 1)" 2>/dev/null; then
        pass "validate with maven section"
    else
        fail "validate with maven section" "valid=true" "$result"
    fi
}

# Test: validate with agent_decisions section
test_with_agent_decisions() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/with-agent-decisions.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and d['valid'] else 1)" 2>/dev/null; then
        pass "validate with agent_decisions section"
    else
        fail "validate with agent_decisions section" "valid=true" "$result"
    fi
}

# Test: detect invalid JSON syntax
test_invalid_json_syntax() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/invalid-json.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and not d['valid'] else 1)" 2>/dev/null; then
        pass "detect invalid JSON syntax"
    else
        fail "detect invalid JSON syntax" "valid=false" "$result"
    fi
}

# Test: checks array in output
test_checks_array() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/run-configuration.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['success'] and len(d['checks'])>0 else 1)" 2>/dev/null; then
        pass "output includes checks array"
    else
        fail "output includes checks array" "checks array with items" "$result"
    fi
}

# Test: file not found error
test_file_not_found() {
    result=$(python3 "$SCRIPT" "$TEMP_DIR/nonexistent.json" 2>&1 || true)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if not d['success'] else 1)" 2>/dev/null; then
        pass "file not found returns error"
    else
        fail "file not found returns error" "success=false" "$result"
    fi
}

# Test: format is run-config
test_format_is_run_config() {
    setup_fixtures
    result=$(python3 "$SCRIPT" "$TEMP_DIR/run-configuration.json" 2>&1)

    if echo "$result" | python3 -c "import sys,json; d=json.load(sys.stdin); exit(0 if d['format']=='run-config' else 1)" 2>/dev/null; then
        pass "format is run-config"
    else
        fail "format is run-config" "format=run-config" "$result"
    fi
}

# Run all tests
echo "========================================"
echo "Testing validate-run-config.py"
echo "========================================"
echo ""

run_test test_valid_run_config
run_test test_missing_version
run_test test_missing_commands
run_test test_wrong_version_type
run_test test_with_maven
run_test test_with_agent_decisions
run_test test_invalid_json_syntax
run_test test_checks_array
run_test test_file_not_found
run_test test_format_is_run_config

echo ""
echo "========================================"
echo "Results: $TESTS_PASSED/$TESTS_RUN tests passed"
echo "========================================"

if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    exit 0
else
    exit 1
fi
