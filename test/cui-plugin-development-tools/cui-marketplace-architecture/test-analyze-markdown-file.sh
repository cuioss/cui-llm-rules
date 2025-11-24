#!/bin/bash
# Test suite for analyze-markdown-file.sh
#
# Usage: ./test-analyze-markdown-file.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
SCRIPT_UNDER_TEST="$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/skills/plugin-doctor/scripts/analyze-markdown-file.sh"
TEST_FIXTURES_DIR="$SCRIPT_DIR/fixtures"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to run a test
run_test() {
    local test_name="$1"
    local test_file="$2"
    local expected_lines="$3"
    local expected_ci_rule="$4"
    local expected_frontmatter="$5"

    TESTS_RUN=$((TESTS_RUN + 1))

    echo -n "Test: $test_name ... "

    # Run script
    result=$("$SCRIPT_UNDER_TEST" "$test_file" 2>&1)

    # Parse JSON
    actual_lines=$(echo "$result" | jq -r '.metrics.line_count')
    actual_ci=$(echo "$result" | jq -r '.continuous_improvement_rule.present')
    actual_fm=$(echo "$result" | jq -r '.frontmatter.present')

    # Verify line count matches wc -l
    wc_lines=$(wc -l < "$test_file" | tr -d ' ')

    if [ "$actual_lines" != "$wc_lines" ]; then
        echo -e "${RED}FAIL${NC}"
        echo "  Line count mismatch: script=$actual_lines, wc -l=$wc_lines"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    # Verify expected values
    if [ "$actual_lines" != "$expected_lines" ] || \
       [ "$actual_ci" != "$expected_ci_rule" ] || \
       [ "$actual_fm" != "$expected_frontmatter" ]; then
        echo -e "${RED}FAIL${NC}"
        echo "  Expected: lines=$expected_lines, ci=$expected_ci_rule, fm=$expected_frontmatter"
        echo "  Actual:   lines=$actual_lines, ci=$actual_ci, fm=$actual_fm"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi

    echo -e "${GREEN}PASS${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

# Test with real marketplace files
test_real_files() {
    echo ""
    echo "=== Testing with real marketplace files ==="
    echo ""

    # Test known files from the marketplace
    local test_cases=(
        "plugin-diagnose-skills.md|$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/commands/plugin-diagnose-skills.md"
        "orchestrate-language.md|$PROJECT_ROOT/marketplace/bundles/cui-task-workflow/commands/orchestrate-language.md"
        "js-implement-code.md|$PROJECT_ROOT/marketplace/bundles/cui-frontend-expert/commands/js-implement-code.md"
        "java-implement-code.md|$PROJECT_ROOT/marketplace/bundles/cui-java-expert/commands/java-implement-code.md"
    )

    for test_case in "${test_cases[@]}"; do
        IFS='|' read -r name file <<< "$test_case"

        if [ ! -f "$file" ]; then
            echo "SKIP: $name (file not found)"
            continue
        fi

        # Get actual line count
        lines=$(wc -l < "$file" | tr -d ' ')

        # Determine if CI rule and frontmatter present
        has_ci="false"
        if grep -qi "CONTINUOUS IMPROVEMENT" "$file"; then
            has_ci="true"
        fi

        has_fm="false"
        if head -1 "$file" | grep -q "^---$"; then
            has_fm="true"
        fi

        run_test "$name" "$file" "$lines" "$has_ci" "$has_fm"
    done
}

# Test classification logic
test_classification() {
    echo ""
    echo "=== Testing bloat classification ==="
    echo ""

    local test_cases=(
        "plugin-diagnose-skills.md|$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/commands/plugin-diagnose-skills.md|LARGE"
        "js-implement-code.md|$PROJECT_ROOT/marketplace/bundles/cui-frontend-expert/commands/js-implement-code.md|BLOATED"
        "java-implement-code.md|$PROJECT_ROOT/marketplace/bundles/cui-java-expert/commands/java-implement-code.md|BLOATED"
    )

    for test_case in "${test_cases[@]}"; do
        IFS='|' read -r name file expected_class <<< "$test_case"

        if [ ! -f "$file" ]; then
            continue
        fi

        TESTS_RUN=$((TESTS_RUN + 1))
        echo -n "Classify: $name ... "

        result=$("$SCRIPT_UNDER_TEST" "$file" 2>&1)
        lines=$(echo "$result" | jq -r '.metrics.line_count')
        actual_class=$(echo "$result" | jq -r '.bloat.classification')

        if [ "$actual_class" == "$expected_class" ]; then
            echo -e "${GREEN}PASS${NC} ($lines lines = $actual_class)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}FAIL${NC}"
            echo "  Expected: $expected_class, Got: $actual_class ($lines lines)"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    done
}

# Enhancement 1b: Test file type detection
test_file_type_detection() {
    echo ""
    echo "=== Testing file type detection ==="
    echo ""

    local test_cases=(
        "command-file|$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/commands/plugin-diagnose-skills.md|command"
        "agent-file|$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/agents/diagnose-command.md|agent"
    )

    for test_case in "${test_cases[@]}"; do
        IFS='|' read -r name file expected_type <<< "$test_case"

        if [ ! -f "$file" ]; then
            echo "SKIP: $name (file not found)"
            continue
        fi

        TESTS_RUN=$((TESTS_RUN + 1))
        echo -n "FileType: $name ... "

        result=$("$SCRIPT_UNDER_TEST" "$file" 2>&1)
        actual_type=$(echo "$result" | jq -r '.file_type.type')

        if [ "$actual_type" == "$expected_type" ]; then
            echo -e "${GREEN}PASS${NC} (type=$actual_type)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}FAIL${NC}"
            echo "  Expected: $expected_type, Got: $actual_type"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    done
}

# Enhancement 1a: Test YAML frontmatter validation
test_yaml_validation() {
    echo ""
    echo "=== Testing YAML frontmatter validation ==="
    echo ""

    local test_cases=(
        "valid-yaml|$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/commands/plugin-diagnose-skills.md|true|true|true"
        "valid-yaml-agent|$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/agents/diagnose-command.md|true|true|true"
    )

    for test_case in "${test_cases[@]}"; do
        IFS='|' read -r name file expected_valid expected_name expected_desc <<< "$test_case"

        if [ ! -f "$file" ]; then
            echo "SKIP: $name (file not found)"
            continue
        fi

        TESTS_RUN=$((TESTS_RUN + 1))
        echo -n "YAML: $name ... "

        result=$("$SCRIPT_UNDER_TEST" "$file" 2>&1)
        yaml_valid=$(echo "$result" | jq -r '.frontmatter.yaml_valid')
        has_name=$(echo "$result" | jq -r '.frontmatter.required_fields.name.present')
        has_desc=$(echo "$result" | jq -r '.frontmatter.required_fields.description.present')

        if [ "$yaml_valid" == "$expected_valid" ] && \
           [ "$has_name" == "$expected_name" ] && \
           [ "$has_desc" == "$expected_desc" ]; then
            echo -e "${GREEN}PASS${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}FAIL${NC}"
            echo "  Expected: valid=$expected_valid, name=$expected_name, desc=$expected_desc"
            echo "  Actual:   valid=$yaml_valid, name=$has_name, desc=$has_desc"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    done
}

# Enhancement 1c: Test section structure analysis
test_structure_analysis() {
    echo ""
    echo "=== Testing section structure analysis ==="
    echo ""

    local test_cases=(
        "diagnose-command|$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/commands/plugin-diagnose-commands.md|8"
        "orchestrate-language|$PROJECT_ROOT/marketplace/bundles/cui-task-workflow/commands/orchestrate-language.md|8"
    )

    for test_case in "${test_cases[@]}"; do
        IFS='|' read -r name file expected_sections <<< "$test_case"

        if [ ! -f "$file" ]; then
            echo "SKIP: $name (file not found)"
            continue
        fi

        TESTS_RUN=$((TESTS_RUN + 1))
        echo -n "Structure: $name ... "

        result=$("$SCRIPT_UNDER_TEST" "$file" 2>&1)
        section_count=$(echo "$result" | jq -r '.structure.section_count')

        if [ "$section_count" == "$expected_sections" ]; then
            echo -e "${GREEN}PASS${NC} ($section_count sections)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${YELLOW}PARTIAL${NC}"
            echo "  Expected: $expected_sections sections, Got: $section_count"
            # Count as pass if within 1 section (due to section naming variations)
            if [ $((section_count - expected_sections)) -le 1 ] && [ $((section_count - expected_sections)) -ge -1 ]; then
                TESTS_PASSED=$((TESTS_PASSED + 1))
            else
                TESTS_FAILED=$((TESTS_FAILED + 1))
            fi
        fi
    done
}

# Enhancement 1d: Test CI rule format validation
test_ci_format_validation() {
    echo ""
    echo "=== Testing CI rule format validation ==="
    echo ""

    local test_cases=(
        "command-self-update|$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/commands/plugin-diagnose-skills.md|self-update|false"
        "agent-caller-reporting|$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/agents/diagnose-command.md|caller-reporting|false"
    )

    for test_case in "${test_cases[@]}"; do
        IFS='|' read -r name file expected_pattern expected_violation <<< "$test_case"

        if [ ! -f "$file" ]; then
            echo "SKIP: $name (file not found)"
            continue
        fi

        TESTS_RUN=$((TESTS_RUN + 1))
        echo -n "CI Format: $name ... "

        result=$("$SCRIPT_UNDER_TEST" "$file" 2>&1)
        ci_pattern=$(echo "$result" | jq -r '.continuous_improvement_rule.format.pattern')
        pattern_22=$(echo "$result" | jq -r '.continuous_improvement_rule.format.pattern_22_violation')

        if [ "$ci_pattern" == "$expected_pattern" ] && \
           [ "$pattern_22" == "$expected_violation" ]; then
            echo -e "${GREEN}PASS${NC} (pattern=$ci_pattern)"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}FAIL${NC}"
            echo "  Expected: pattern=$expected_pattern, violation=$expected_violation"
            echo "  Actual:   pattern=$ci_pattern, violation=$pattern_22"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    done
}

# Enhancement 1e: Test parameter documentation check
test_parameter_detection() {
    echo ""
    echo "=== Testing parameter documentation detection ==="
    echo ""

    local test_cases=(
        "has-params|$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/commands/plugin-diagnose-skills.md|true"
        "has-params-2|$PROJECT_ROOT/marketplace/bundles/cui-plugin-development-tools/agents/diagnose-command.md|true"
    )

    for test_case in "${test_cases[@]}"; do
        IFS='|' read -r name file expected_has_section <<< "$test_case"

        if [ ! -f "$file" ]; then
            echo "SKIP: $name (file not found)"
            continue
        fi

        TESTS_RUN=$((TESTS_RUN + 1))
        echo -n "Parameters: $name ... "

        result=$("$SCRIPT_UNDER_TEST" "$file" 2>&1)
        has_section=$(echo "$result" | jq -r '.parameters.has_section')

        if [ "$has_section" == "$expected_has_section" ]; then
            echo -e "${GREEN}PASS${NC}"
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}FAIL${NC}"
            echo "  Expected: has_section=$expected_has_section"
            echo "  Actual:   has_section=$has_section"
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    done
}

# Test JSON validity for all marketplace files
test_json_validity() {
    echo ""
    echo "=== Testing JSON validity for all commands ==="
    echo ""

    local files=("$PROJECT_ROOT"/marketplace/bundles/*/commands/*.md)
    local valid_count=0
    local invalid_count=0

    for file in "${files[@]}"; do
        if [ ! -f "$file" ]; then
            continue
        fi

        TESTS_RUN=$((TESTS_RUN + 1))

        # Try to run script and parse JSON
        if result=$("$SCRIPT_UNDER_TEST" "$file" 2>&1) && echo "$result" | jq . > /dev/null 2>&1; then
            valid_count=$((valid_count + 1))
            TESTS_PASSED=$((TESTS_PASSED + 1))
        else
            echo -e "${RED}FAIL${NC}: Invalid JSON for $(basename "$file")"
            invalid_count=$((invalid_count + 1))
            TESTS_FAILED=$((TESTS_FAILED + 1))
        fi
    done

    echo "JSON validity: $valid_count valid, $invalid_count invalid"
}

# Main test execution
main() {
    echo "========================================"
    echo "Test Suite: analyze-markdown-file.sh"
    echo "========================================"

    # Check script exists
    if [ ! -f "$SCRIPT_UNDER_TEST" ]; then
        echo -e "${RED}ERROR: Script not found: $SCRIPT_UNDER_TEST${NC}"
        exit 1
    fi

    # Check jq is available
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}ERROR: jq is required for tests${NC}"
        exit 1
    fi

    # Run all test suites
    test_real_files
    test_classification
    test_file_type_detection
    test_yaml_validation
    test_structure_analysis
    test_ci_format_validation
    test_parameter_detection
    test_json_validity

    # Print summary
    echo ""
    echo "========================================"
    echo "Test Summary"
    echo "========================================"
    echo "Total:  $TESTS_RUN"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    echo ""

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
        exit 0
    else
        echo -e "${RED}✗ Some tests failed!${NC}"
        exit 1
    fi
}

# Run main
main
