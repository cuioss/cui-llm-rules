#!/bin/bash
# Tests for detect-build-systems.py script
# Tests build system detection logic

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT_PATH="$PROJECT_ROOT/marketplace/bundles/builder/skills/environment-detection/scripts/detect-build-systems.py"
FIXTURES_DIR="$SCRIPT_DIR/fixtures"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASSED=0
FAILED=0

# Setup test fixtures
setup_fixtures() {
    rm -rf "$FIXTURES_DIR"
    mkdir -p "$FIXTURES_DIR"

    # Maven project
    mkdir -p "$FIXTURES_DIR/maven-project"
    echo '<project></project>' > "$FIXTURES_DIR/maven-project/pom.xml"

    # Gradle project (Kotlin DSL)
    mkdir -p "$FIXTURES_DIR/gradle-project"
    echo 'plugins { java }' > "$FIXTURES_DIR/gradle-project/build.gradle.kts"

    # Gradle project (Groovy DSL)
    mkdir -p "$FIXTURES_DIR/gradle-groovy-project"
    echo 'plugins { id "java" }' > "$FIXTURES_DIR/gradle-groovy-project/build.gradle"

    # npm project
    mkdir -p "$FIXTURES_DIR/npm-project"
    echo '{"name": "test", "version": "1.0.0"}' > "$FIXTURES_DIR/npm-project/package.json"

    # Mixed Maven + npm project
    mkdir -p "$FIXTURES_DIR/mixed-maven-npm"
    echo '<project></project>' > "$FIXTURES_DIR/mixed-maven-npm/pom.xml"
    echo '{"name": "frontend"}' > "$FIXTURES_DIR/mixed-maven-npm/package.json"

    # Mixed Gradle + npm project
    mkdir -p "$FIXTURES_DIR/mixed-gradle-npm"
    echo 'plugins { java }' > "$FIXTURES_DIR/mixed-gradle-npm/build.gradle.kts"
    echo '{"name": "frontend"}' > "$FIXTURES_DIR/mixed-gradle-npm/package.json"

    # Empty project (no build files)
    mkdir -p "$FIXTURES_DIR/empty-project"

    # Settings-only Gradle project
    mkdir -p "$FIXTURES_DIR/gradle-settings-only"
    echo 'rootProject.name = "test"' > "$FIXTURES_DIR/gradle-settings-only/settings.gradle.kts"
}

# Cleanup test fixtures
cleanup_fixtures() {
    rm -rf "$FIXTURES_DIR"
}

# Assert function
assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="$3"

    if [[ "$expected" == "$actual" ]]; then
        echo -e "${GREEN}✓ PASSED${NC} - $message"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} - $message"
        echo "  Expected: $expected"
        echo "  Actual:   $actual"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

assert_contains() {
    local haystack="$1"
    local needle="$2"
    local message="$3"

    if [[ "$haystack" == *"$needle"* ]]; then
        echo -e "${GREEN}✓ PASSED${NC} - $message"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} - $message"
        echo "  Expected to contain: $needle"
        echo "  Actual: $haystack"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Extract JSON field using Python
json_field() {
    local json="$1"
    local field="$2"
    echo "$json" | python3 -c "import sys, json; print(json.load(sys.stdin).get('$field', ''))" 2>/dev/null
}

# Run tests
echo "=========================================="
echo "Testing detect-build-systems.py"
echo "=========================================="
echo

# Setup
setup_fixtures

echo "Test: Maven project detection"
output=$(python3 "$SCRIPT_PATH" --project-dir "$FIXTURES_DIR/maven-project")
assert_equals "maven" "$(json_field "$output" "available_systems")" "Maven detected as available"
assert_equals "maven" "$(json_field "$output" "default_system")" "Maven is default"

echo
echo "Test: Gradle project detection (Kotlin DSL)"
output=$(python3 "$SCRIPT_PATH" --project-dir "$FIXTURES_DIR/gradle-project")
assert_equals "gradle" "$(json_field "$output" "available_systems")" "Gradle detected as available"
assert_equals "gradle" "$(json_field "$output" "default_system")" "Gradle is default"

echo
echo "Test: Gradle project detection (Groovy DSL)"
output=$(python3 "$SCRIPT_PATH" --project-dir "$FIXTURES_DIR/gradle-groovy-project")
assert_equals "gradle" "$(json_field "$output" "available_systems")" "Gradle (Groovy) detected"
assert_equals "gradle" "$(json_field "$output" "default_system")" "Gradle (Groovy) is default"

echo
echo "Test: npm project detection"
output=$(python3 "$SCRIPT_PATH" --project-dir "$FIXTURES_DIR/npm-project")
assert_equals "npm" "$(json_field "$output" "available_systems")" "npm detected as available"
assert_equals "npm" "$(json_field "$output" "default_system")" "npm is default"

echo
echo "Test: Mixed Maven + npm project"
output=$(python3 "$SCRIPT_PATH" --project-dir "$FIXTURES_DIR/mixed-maven-npm")
assert_equals "maven,npm" "$(json_field "$output" "available_systems")" "Both Maven and npm detected"
assert_equals "maven" "$(json_field "$output" "default_system")" "Maven has priority over npm"

echo
echo "Test: Mixed Gradle + npm project"
output=$(python3 "$SCRIPT_PATH" --project-dir "$FIXTURES_DIR/mixed-gradle-npm")
assert_equals "gradle,npm" "$(json_field "$output" "available_systems")" "Both Gradle and npm detected"
assert_equals "gradle" "$(json_field "$output" "default_system")" "Gradle has priority over npm"

echo
echo "Test: Empty project (no build files)"
output=$(python3 "$SCRIPT_PATH" --project-dir "$FIXTURES_DIR/empty-project")
assert_equals "" "$(json_field "$output" "available_systems")" "No systems detected"
assert_equals "" "$(json_field "$output" "default_system")" "No default system"
assert_contains "$output" "No build systems detected" "Correct message for empty project"

echo
echo "Test: Gradle settings-only project"
output=$(python3 "$SCRIPT_PATH" --project-dir "$FIXTURES_DIR/gradle-settings-only")
assert_equals "gradle" "$(json_field "$output" "available_systems")" "Gradle detected from settings file"

echo
echo "Test: Simple output format"
output=$(python3 "$SCRIPT_PATH" --project-dir "$FIXTURES_DIR/maven-project" --format simple)
assert_contains "$output" "available_systems=maven" "Simple format shows available_systems"
assert_contains "$output" "default_system=maven" "Simple format shows default_system"

echo
echo "Test: Help flag"
output=$(python3 "$SCRIPT_PATH" --help 2>&1)
assert_contains "$output" "project-dir" "Help shows project-dir option"
assert_contains "$output" "format" "Help shows format option"

# Cleanup
cleanup_fixtures

# Summary
echo
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "Passed: ${GREEN}$PASSED${NC}"
echo "Failed: ${RED}$FAILED${NC}"

if [[ $FAILED -gt 0 ]]; then
    exit 1
else
    echo -e "\n${GREEN}All tests passed!${NC}"
    exit 0
fi
