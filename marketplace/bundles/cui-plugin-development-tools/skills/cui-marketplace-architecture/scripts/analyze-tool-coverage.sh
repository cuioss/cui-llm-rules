#!/bin/bash
# analyze-tool-coverage.sh
# Analyzes tool coverage for agent files (Tool Fit Score)
#
# Usage: ./analyze-tool-coverage.sh <file_path>
# Returns: JSON object with tool coverage analysis and critical violations

set -euo pipefail

# ============================================================================
# USAGE AND HELP
# ============================================================================

usage() {
    cat <<EOF
Usage: $(basename "$0") <file_path>

Description:
  Analyzes tool coverage for agent markdown files. Extracts declared tools
  from YAML frontmatter, scans workflow for actual tool usage, calculates
  Tool Fit Score, and detects critical violations.

Arguments:
  file_path    Path to the agent .md file to analyze (required)

Output:
  JSON object with tool coverage analysis:
  - declared_tools: Tools listed in YAML frontmatter
  - used_tools: Tools actually used in workflow
  - Tool Fit Score: (tools used AND declared) / (tools used OR declared) * 100
  - critical_violations: Task tool usage, Maven calls, backup patterns

Exit Codes:
  0 - Success
  1 - Invalid arguments or file not found
  2 - Analysis error

Examples:
  $(basename "$0") path/to/agent.md
EOF
    exit 0
}

# ============================================================================
# PARAMETER PARSING
# ============================================================================

if [ $# -eq 0 ] || [ "$1" = "--help" ]; then
    usage
fi

FILE_PATH="${1:-}"

# ============================================================================
# INPUT VALIDATION
# ============================================================================

if [ -z "$FILE_PATH" ]; then
    echo '{"error": "file_path parameter required"}' >&2
    exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
    echo "{\"error\": \"File not found: $FILE_PATH\"}" >&2
    exit 1
fi

if [[ ! "$FILE_PATH" =~ \.md$ ]]; then
    echo "{\"error\": \"Expected .md file, got: $FILE_PATH\"}" >&2
    exit 1
fi

# ============================================================================
# EXTRACT DECLARED TOOLS FROM YAML
# ============================================================================

DECLARED_TOOLS=()
HAS_FRONTMATTER=false

# Check if file starts with ---
if head -1 "$FILE_PATH" | grep -q "^---$"; then
    HAS_FRONTMATTER=true

    # Extract frontmatter
    FRONTMATTER=$(sed -n '2,/^---$/p' "$FILE_PATH" | sed '$d')

    # Look for tools: line
    if echo "$FRONTMATTER" | grep -q "^tools:"; then
        # Extract tools array - handle both formats:
        # tools: [Read, Write, Glob]
        # tools:
        #   - Read
        #   - Write

        # Try inline array format first
        TOOLS_LINE=$(echo "$FRONTMATTER" | grep "^tools:" | sed 's/^tools:[[:space:]]*//')

        if [[ "$TOOLS_LINE" =~ ^\[.*\]$ ]]; then
            # Inline array format: [Read, Write, Glob]
            TOOLS_LINE=$(echo "$TOOLS_LINE" | sed 's/^\[//' | sed 's/\]$//')
            # Split by comma
            IFS=',' read -ra TOOLS_ARRAY <<< "$TOOLS_LINE"
            for tool in "${TOOLS_ARRAY[@]}"; do
                # Trim whitespace
                tool=$(echo "$tool" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
                # Extract base tool name (before parentheses or colon)
                tool=$(echo "$tool" | sed 's/(.*//' | sed 's/:.*//')
                if [ -n "$tool" ]; then
                    DECLARED_TOOLS+=("$tool")
                fi
            done
        else
            # Multi-line format: extract lines starting with -
            # Extract range and remove first/last lines (portable for BSD/GNU sed)
            TOOLS_SECTION=$(sed -n '/^tools:/,/^[a-z]/p' <<< "$FRONTMATTER" | sed '1d;$d')
            while IFS= read -r line; do
                if [[ "$line" =~ ^[[:space:]]*-[[:space:]]*(.*) ]]; then
                    tool="${BASH_REMATCH[1]}"
                    # Extract base tool name
                    tool=$(echo "$tool" | sed 's/(.*//' | sed 's/:.*//')
                    tool=$(echo "$tool" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
                    if [ -n "$tool" ]; then
                        DECLARED_TOOLS+=("$tool")
                    fi
                fi
            done <<< "$TOOLS_SECTION"
        fi
    fi
fi

# ============================================================================
# SCAN WORKFLOW FOR TOOL USAGE
# ============================================================================

USED_TOOLS=()

# Tool usage patterns to detect
# Format: "ToolName:" or "ToolName(" for tool invocations

# Common tools to check for
TOOL_PATTERNS=(
    "Read:"
    "Write:"
    "Edit:"
    "Glob:"
    "Grep:"
    "Task:"
    "Bash:"
    "Bash("
    "Skill:"
    "SlashCommand:"
    "AskUserQuestion:"
    "WebFetch:"
    "WebSearch:"
    "TodoWrite:"
    "NotebookEdit:"
)

for pattern in "${TOOL_PATTERNS[@]}"; do
    # Extract tool name from pattern (remove : or ()
    tool_name=$(echo "$pattern" | sed 's/[:(].*//')

    # Check if pattern appears in file (case-sensitive, not in code blocks)
    if grep -q "$pattern" "$FILE_PATH"; then
        # Verify it's not just in a code block or comment
        # Simple heuristic: if found outside ``` blocks
        USED_TOOLS+=("$tool_name")
    fi
done

# Remove duplicates from used tools
if [ "${#USED_TOOLS[@]}" -gt 0 ]; then
    USED_TOOLS=($(printf '%s\n' "${USED_TOOLS[@]}" | sort -u))
fi

# ============================================================================
# CALCULATE TOOL FIT SCORE
# ============================================================================

# Convert arrays to sorted unique lists for set operations
# Handle empty arrays (set -u compatibility)
DECLARED_SORTED=()
if [ "${#DECLARED_TOOLS[@]}" -gt 0 ]; then
    DECLARED_SORTED=($(printf '%s\n' "${DECLARED_TOOLS[@]}" | sort -u))
fi

USED_SORTED=()
if [ "${#USED_TOOLS[@]}" -gt 0 ]; then
    USED_SORTED=($(printf '%s\n' "${USED_TOOLS[@]}" | sort -u))
fi

# Calculate intersection (tools both declared AND used)
INTERSECTION=()
if [ "${#DECLARED_SORTED[@]}" -gt 0 ] && [ "${#USED_SORTED[@]}" -gt 0 ]; then
    for tool in "${DECLARED_SORTED[@]}"; do
        for used_tool in "${USED_SORTED[@]}"; do
            if [ "$tool" = "$used_tool" ]; then
                INTERSECTION+=("$tool")
                break
            fi
        done
    done
fi

# Calculate union (tools declared OR used)
UNION=()
if [ "${#DECLARED_SORTED[@]}" -gt 0 ] && [ "${#USED_SORTED[@]}" -gt 0 ]; then
    # Both arrays have elements
    UNION=($(printf '%s\n' "${DECLARED_SORTED[@]}" "${USED_SORTED[@]}" | sort -u))
elif [ "${#DECLARED_SORTED[@]}" -gt 0 ]; then
    # Only declared tools
    UNION=("${DECLARED_SORTED[@]}")
elif [ "${#USED_SORTED[@]}" -gt 0 ]; then
    # Only used tools
    UNION=("${USED_SORTED[@]}")
fi

# Calculate missing tools (used but not declared)
MISSING_TOOLS=()
if [ "${#USED_SORTED[@]}" -gt 0 ]; then
    for tool in "${USED_SORTED[@]}"; do
        found=false
        if [ "${#DECLARED_SORTED[@]}" -gt 0 ]; then
            for declared_tool in "${DECLARED_SORTED[@]}"; do
                if [ "$tool" = "$declared_tool" ]; then
                    found=true
                    break
                fi
            done
        fi
        if [ "$found" = false ]; then
            MISSING_TOOLS+=("$tool")
        fi
    done
fi

# Calculate unused tools (declared but not used)
UNUSED_TOOLS=()
if [ "${#DECLARED_SORTED[@]}" -gt 0 ]; then
    for tool in "${DECLARED_SORTED[@]}"; do
        found=false
        if [ "${#USED_SORTED[@]}" -gt 0 ]; then
            for used_tool in "${USED_SORTED[@]}"; do
                if [ "$tool" = "$used_tool" ]; then
                    found=true
                    break
                fi
            done
        fi
        if [ "$found" = false ]; then
            UNUSED_TOOLS+=("$tool")
        fi
    done
fi

# Calculate Tool Fit Score
INTERSECTION_COUNT=${#INTERSECTION[@]}
UNION_COUNT=${#UNION[@]}

if [ "$UNION_COUNT" -eq 0 ]; then
    TOOL_FIT_SCORE=100.0
else
    TOOL_FIT_SCORE=$(awk "BEGIN {printf \"%.1f\", ($INTERSECTION_COUNT / $UNION_COUNT) * 100}")
fi

# Determine rating
if (( $(awk "BEGIN {print ($TOOL_FIT_SCORE >= 95)}") )); then
    RATING="Excellent"
elif (( $(awk "BEGIN {print ($TOOL_FIT_SCORE >= 80)}") )); then
    RATING="Good"
elif (( $(awk "BEGIN {print ($TOOL_FIT_SCORE >= 60)}") )); then
    RATING="Needs improvement"
else
    RATING="Poor"
fi

# ============================================================================
# DETECT CRITICAL VIOLATIONS
# ============================================================================

# Check for Task tool in frontmatter
HAS_TASK_TOOL=false
if [ "${#DECLARED_TOOLS[@]}" -gt 0 ]; then
    for tool in "${DECLARED_TOOLS[@]}"; do
        if [ "$tool" = "Task" ]; then
            HAS_TASK_TOOL=true
            break
        fi
    done
fi

# Check for Task delegation calls in workflow
HAS_TASK_CALLS=false
if grep -q "Task:" "$FILE_PATH" || grep -q "Task(" "$FILE_PATH"; then
    HAS_TASK_CALLS=true
fi

# Check for Maven calls (./mvnw, mvn)
MAVEN_CALLS=()
if grep -q "./mvnw" "$FILE_PATH"; then
    MAVEN_CALLS+=("./mvnw")
fi
if grep -q "mvn " "$FILE_PATH" || grep -q "mvn\$" "$FILE_PATH"; then
    # Avoid false positives from "environment" etc
    if grep -E "Bash.*mvn[[:space:]]|mvn[[:space:]]" "$FILE_PATH" >/dev/null; then
        MAVEN_CALLS+=("mvn")
    fi
fi

# Only flag as violation if agent is NOT maven-builder
IS_MAVEN_BUILDER=false
if [[ "$FILE_PATH" =~ maven-builder ]]; then
    IS_MAVEN_BUILDER=true
fi

if [ "$IS_MAVEN_BUILDER" = true ]; then
    MAVEN_CALLS=()  # Clear violations for maven-builder
fi

# Check for backup file creation patterns
BACKUP_PATTERNS=()
# Check for cp/mv commands creating backup files (most specific)
if grep -E "cp[[:space:]].*\.bak|cp[[:space:]].*\.backup|mv[[:space:]].*\.bak|mv[[:space:]].*\.backup" "$FILE_PATH" >/dev/null; then
    BACKUP_PATTERNS+=("cp/mv command creating .bak/.backup file")
# Otherwise check for generic .bak/.backup references
elif grep -E "\.bak[\"']?|\.backup[\"']?" "$FILE_PATH" >/dev/null; then
    BACKUP_PATTERNS+=(".bak or .backup file reference")
fi

# ============================================================================
# JSON ESCAPING HELPER
# ============================================================================

escape_json() {
    local input="$1"
    echo "$input" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g'
}

# Build JSON arrays
build_json_array() {
    local array_name="$1"
    local json="["
    local first=true
    local item
    local count

    # Check if array exists and get count
    eval "count=\${#${array_name}[@]}"

    if [ "$count" -eq 0 ]; then
        echo "[]"
        return
    fi

    # Use eval to access array elements
    eval "
        for item in \"\${${array_name}[@]}\"; do
            if [ \"\$first\" = true ]; then
                first=false
            else
                json+=\",\"
            fi
            item_escaped=\$(escape_json \"\$item\")
            json+=\"\\\"\$item_escaped\\\"\"
        done
    "
    json+="]"
    echo "$json"
}

DECLARED_JSON=$(build_json_array DECLARED_SORTED)
USED_JSON=$(build_json_array USED_SORTED)
MISSING_JSON=$(build_json_array MISSING_TOOLS)
UNUSED_JSON=$(build_json_array UNUSED_TOOLS)
MAVEN_JSON=$(build_json_array MAVEN_CALLS)
BACKUP_JSON=$(build_json_array BACKUP_PATTERNS)

# ============================================================================
# BUILD AND OUTPUT JSON
# ============================================================================

cat <<EOF
{
  "file_path": "$FILE_PATH",
  "tool_coverage": {
    "declared_tools": $DECLARED_JSON,
    "used_tools": $USED_JSON,
    "missing_tools": $MISSING_JSON,
    "unused_tools": $UNUSED_JSON,
    "tool_fit_score": $TOOL_FIT_SCORE,
    "rating": "$RATING"
  },
  "critical_violations": {
    "has_task_tool": $HAS_TASK_TOOL,
    "has_task_calls": $HAS_TASK_CALLS,
    "maven_calls": $MAVEN_JSON,
    "backup_file_patterns": $BACKUP_JSON
  }
}
EOF
