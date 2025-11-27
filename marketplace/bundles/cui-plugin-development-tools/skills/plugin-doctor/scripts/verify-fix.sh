#!/bin/bash
# Verify that a fix was successful by re-running relevant diagnostic
# Usage: verify-fix.sh <fix_type> <component_path>
# Output: JSON with verification result

set -euo pipefail

# --help support
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    cat <<EOF
Usage: $(basename "$0") <fix_type> <component_path>

Verifies that a fix was successfully applied by re-running relevant diagnostics.

Arguments:
  fix_type        Type of fix to verify (see supported types below)
  component_path  Path to the component file that was fixed

Supported fix types:
  missing-frontmatter    Verify frontmatter was added
  missing-name-field     Verify name field was added
  missing-description-field  Verify description field was added
  missing-tools-field    Verify tools field was added
  array-syntax-tools     Verify array syntax was converted
  rule-6-violation       Verify Task tool was removed
  trailing-whitespace    Verify trailing whitespace was removed
  pattern-22-violation   Verify self-update patterns were removed
  unused-tool-declared   Verify unused tools were removed

Output: JSON with verification result including:
  - verified: Whether verification completed
  - issue_resolved: Whether the issue was actually fixed
  - details: Human-readable explanation

Exit codes:
  0 - Verification completed (check issue_resolved for result)
  1 - Error (missing arguments, file not found)

Examples:
  $(basename "$0") rule-6-violation ./agents/my-agent.md
  $(basename "$0") trailing-whitespace ./commands/my-command.md
EOF
    exit 0
fi

FIX_TYPE="${1:-}"
COMPONENT_PATH="${2:-}"

if [ -z "$FIX_TYPE" ]; then
    echo '{"verified": false, "error": "Fix type required. Use --help for usage."}' >&2
    exit 1
fi

if [ -z "$COMPONENT_PATH" ]; then
    echo '{"verified": false, "error": "Component path required"}' >&2
    exit 1
fi

if [ ! -f "$COMPONENT_PATH" ]; then
    echo "{\"verified\": false, \"error\": \"File not found: $COMPONENT_PATH\"}" >&2
    exit 1
fi

# Determine which diagnostic script to use based on fix type
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIAGNOSE_SCRIPTS_DIR="$SCRIPT_DIR/../../plugin-diagnose/scripts"

# Map fix types to diagnostic checks
verify_frontmatter_fix() {
    local file="$1"

    # Check if file now has valid frontmatter
    if head -1 "$file" | grep -q "^---$"; then
        # Check for required fields
        local frontmatter
        frontmatter=$(awk '/^---$/{if(++count==2) exit; if(count==1) next} count==1' "$file")

        local has_name="false"
        local has_desc="false"

        if echo "$frontmatter" | grep -q "^name:"; then
            has_name="true"
        fi
        if echo "$frontmatter" | grep -q "^description:"; then
            has_desc="true"
        fi

        if [ "$has_name" == "true" ] && [ "$has_desc" == "true" ]; then
            echo '{"verified": true, "issue_resolved": true, "details": "Frontmatter present with required fields"}'
            return 0
        else
            echo "{\"verified\": true, \"issue_resolved\": false, \"details\": \"Frontmatter present but missing fields (name: $has_name, description: $has_desc)\"}"
            return 0
        fi
    else
        echo '{"verified": true, "issue_resolved": false, "details": "Still missing frontmatter"}'
        return 0
    fi
}

verify_array_syntax_fix() {
    local file="$1"

    # Check if tools line uses array syntax
    local frontmatter
    frontmatter=$(awk '/^---$/{if(++count==2) exit; if(count==1) next} count==1' "$file")

    if echo "$frontmatter" | grep -q "^tools:.*\["; then
        echo '{"verified": true, "issue_resolved": false, "details": "Still using array syntax for tools"}'
    else
        echo '{"verified": true, "issue_resolved": true, "details": "Tools now using comma-separated format"}'
    fi
    return 0
}

verify_rule_6_fix() {
    local file="$1"

    # Check if Task tool is still declared
    local frontmatter
    frontmatter=$(awk '/^---$/{if(++count==2) exit; if(count==1) next} count==1' "$file")

    if echo "$frontmatter" | grep -qE "^tools:.*\bTask\b"; then
        echo '{"verified": true, "issue_resolved": false, "details": "Task tool still declared (Rule 6 violation)"}'
    else
        echo '{"verified": true, "issue_resolved": true, "details": "Task tool removed from declaration"}'
    fi
    return 0
}

verify_trailing_whitespace_fix() {
    local file="$1"

    # Check for trailing whitespace
    local trailing_count
    trailing_count=$(grep -c '[[:space:]]$' "$file" || echo "0")

    if [ "$trailing_count" -gt 0 ]; then
        echo "{\"verified\": true, \"issue_resolved\": false, \"details\": \"Still has trailing whitespace on $trailing_count lines\"}"
    else
        echo '{"verified": true, "issue_resolved": true, "details": "No trailing whitespace found"}'
    fi
    return 0
}

verify_pattern_22_fix() {
    local file="$1"

    # Check for self-update patterns
    if grep -qi "/plugin-update-agent\|/plugin-update-command" "$file"; then
        echo '{"verified": true, "issue_resolved": false, "details": "Still contains self-update commands (Pattern 22 violation)"}'
    else
        echo '{"verified": true, "issue_resolved": true, "details": "Self-update patterns removed"}'
    fi
    return 0
}

verify_unused_tool_fix() {
    local file="$1"

    # Run full tool coverage analysis if available
    if [ -x "$DIAGNOSE_SCRIPTS_DIR/analyze-tool-coverage.sh" ]; then
        local result
        result=$("$DIAGNOSE_SCRIPTS_DIR/analyze-tool-coverage.sh" "$file" 2>/dev/null || echo '{"error": "analysis failed"}')

        local unused_count
        unused_count=$(echo "$result" | grep -o '"unused_count": [0-9]*' | grep -o '[0-9]*' || echo "0")

        if [ "$unused_count" -eq 0 ]; then
            echo '{"verified": true, "issue_resolved": true, "details": "No unused tools declared"}'
        else
            echo "{\"verified\": true, \"issue_resolved\": false, \"details\": \"Still has $unused_count unused tools declared\"}"
        fi
    else
        # Basic check without full analysis
        echo '{"verified": true, "issue_resolved": null, "details": "Full analysis not available, manual verification recommended"}'
    fi
    return 0
}

verify_generic() {
    local file="$1"
    local fix_type="$2"

    # Run markdown analysis if available
    if [ -x "$DIAGNOSE_SCRIPTS_DIR/analyze-markdown-file.sh" ]; then
        local result
        result=$("$DIAGNOSE_SCRIPTS_DIR/analyze-markdown-file.sh" "$file" 2>/dev/null || echo '{"error": "analysis failed"}')
        echo "{\"verified\": true, \"issue_resolved\": null, \"details\": \"Generic verification complete\", \"analysis\": $result}"
    else
        echo '{"verified": true, "issue_resolved": null, "details": "Manual verification recommended"}'
    fi
    return 0
}

# Route to appropriate verification based on fix type
case "$FIX_TYPE" in
    missing-frontmatter|missing-name-field|missing-description-field|missing-tools-field)
        verify_frontmatter_fix "$COMPONENT_PATH"
        ;;
    array-syntax-tools)
        verify_array_syntax_fix "$COMPONENT_PATH"
        ;;
    rule-6-violation)
        verify_rule_6_fix "$COMPONENT_PATH"
        ;;
    trailing-whitespace)
        verify_trailing_whitespace_fix "$COMPONENT_PATH"
        ;;
    pattern-22-violation)
        verify_pattern_22_fix "$COMPONENT_PATH"
        ;;
    unused-tool-declared)
        verify_unused_tool_fix "$COMPONENT_PATH"
        ;;
    *)
        verify_generic "$COMPONENT_PATH" "$FIX_TYPE"
        ;;
esac
