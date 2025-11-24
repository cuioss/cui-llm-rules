#!/bin/bash
# Analyzes tool coverage and fit for agents/commands
# Usage: analyze-tool-coverage.sh <file_path>
# Output: JSON with tool analysis

set -euo pipefail

# --help support
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    cat <<EOF
Usage: $(basename "$0") <file_path>

Analyzes tool declarations vs actual usage in agents and commands.

Arguments:
  file_path    Path to the agent or command markdown file

Output: JSON with tool coverage analysis including:
  - tool_coverage.declared_count: Number of tools declared in frontmatter
  - tool_coverage.used_count: Number of declared tools actually used
  - tool_coverage.missing_tools: Tools used but not declared
  - tool_coverage.unused_tools: Tools declared but not used
  - tool_coverage.tool_fit_score: Score 0-100
  - tool_coverage.rating: Excellent, Good, Needs improvement, or Poor
  - critical_violations: Rule 6 (Task tool), Rule 7 (Maven), backup patterns

Exit codes:
  0 - Success
  1 - Error (missing argument, file not found, no frontmatter)

Examples:
  $(basename "$0") marketplace/bundles/cui-java-expert/agents/java-analyzer.md
  $(basename "$0") ./agents/my-agent.md
EOF
    exit 0
fi

FILE_PATH="${1:-}"

if [ -z "$FILE_PATH" ]; then
    echo '{"error": "File path required. Use --help for usage."}' >&2
    exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
    echo "{\"error\": \"File not found: $FILE_PATH\"}" >&2
    exit 1
fi

# Extract frontmatter
if ! head -1 "$FILE_PATH" | grep -q "^---$"; then
    echo '{"error": "No frontmatter found"}' >&2
    exit 1
fi

FRONTMATTER=$(awk '/^---$/{if(++count==2) exit; if(count==1) next} count==1' "$FILE_PATH")

# Extract tools from frontmatter
TOOLS_LINE=$(echo "$FRONTMATTER" | grep "^tools:" || echo "")
DECLARED_TOOLS=""

if [ -n "$TOOLS_LINE" ]; then
    # Parse comma-separated tools
    DECLARED_TOOLS=$(echo "$TOOLS_LINE" | sed 's/^tools: *//' | sed 's/, /,/g' | tr ',' '\n' | sed 's/^ *//;s/ *$//' | grep -v "^$")
fi

# Count declared tools
DECLARED_COUNT=$(echo "$DECLARED_TOOLS" | grep -c "." || echo "0")

# Detect tool usage in file content (exclude frontmatter to avoid false matches)
CONTENT=$(awk '/^---$/{if(++count==2) {getline; body=1}} body' "$FILE_PATH")
USED_TOOLS=""
MISSING_TOOLS=""
UNUSED_TOOLS=""

# Check each declared tool for usage
while IFS= read -r tool; do
    if [ -z "$tool" ]; then
        continue
    fi

    # Check if tool is referenced in content (case-insensitive)
    if echo "$CONTENT" | grep -qi "$tool"; then
        USED_TOOLS="${USED_TOOLS}${tool}"$'\n'
    else
        UNUSED_TOOLS="${UNUSED_TOOLS}${tool}"$'\n'
    fi
done <<< "$DECLARED_TOOLS"

# Count used tools (count actual newlines, not including the echo-added one)
if [ -z "$USED_TOOLS" ]; then
    USED_COUNT=0
else
    USED_COUNT=$(printf "%s" "$USED_TOOLS" | wc -l | tr -d ' ')
fi

if [ -z "$UNUSED_TOOLS" ]; then
    UNUSED_COUNT=0
else
    UNUSED_COUNT=$(printf "%s" "$UNUSED_TOOLS" | wc -l | tr -d ' ')
fi

# Detect common tools used but not declared
COMMON_TOOLS="Read Write Edit Glob Grep Bash WebFetch WebSearch AskUserQuestion TodoWrite Skill Task SlashCommand"
for tool in $COMMON_TOOLS; do
    # Check if tool is used but not declared
    if echo "$CONTENT" | grep -qi "$tool" && ! echo "$DECLARED_TOOLS" | grep -qi "$tool"; then
        MISSING_TOOLS="${MISSING_TOOLS}${tool}"$'\n'
    fi
done

if [ -z "$MISSING_TOOLS" ]; then
    MISSING_COUNT=0
else
    MISSING_COUNT=$(printf "%s" "$MISSING_TOOLS" | wc -l | tr -d ' ')
fi

# Calculate tool fit score
TOOL_FIT_SCORE="0.0"
if [ "$DECLARED_COUNT" -gt 0 ]; then
    if [ "$MISSING_COUNT" -eq 0 ] && [ "$UNUSED_COUNT" -eq 0 ]; then
        TOOL_FIT_SCORE="100.0"
    elif [ "$MISSING_COUNT" -eq 0 ]; then
        # Only unused tools
        TOOL_FIT_SCORE=$(awk "BEGIN {printf \"%.1f\", ($USED_COUNT / $DECLARED_COUNT) * 100}")
    elif [ "$UNUSED_COUNT" -eq 0 ]; then
        # Only missing tools
        TOTAL_NEEDED=$((USED_COUNT + MISSING_COUNT))
        TOOL_FIT_SCORE=$(awk "BEGIN {printf \"%.1f\", ($USED_COUNT / $TOTAL_NEEDED) * 100}")
    else
        # Both issues
        TOTAL_NEEDED=$((USED_COUNT + MISSING_COUNT))
        TOOL_FIT_SCORE=$(awk "BEGIN {printf \"%.1f\", ($USED_COUNT / $TOTAL_NEEDED) * 100}")
    fi
fi

# Determine rating
RATING="Poor"
if awk "BEGIN {exit !($TOOL_FIT_SCORE >= 90)}"; then
    RATING="Excellent"
elif awk "BEGIN {exit !($TOOL_FIT_SCORE >= 70)}"; then
    RATING="Good"
elif awk "BEGIN {exit !($TOOL_FIT_SCORE >= 50)}"; then
    RATING="Needs improvement"
fi

# Check critical violations
HAS_TASK_TOOL="false"
HAS_TASK_CALLS="false"
MAVEN_CALLS=""
BACKUP_PATTERNS=""

# Rule 6: Task tool in agents
if echo "$DECLARED_TOOLS" | grep -qi "Task"; then
    HAS_TASK_TOOL="true"
fi

# Task invocations in content
if echo "$CONTENT" | grep -qi "Task tool\|invoke.*Task\|subagent_type"; then
    HAS_TASK_CALLS="true"
fi

# Rule 7: Maven anti-pattern
MAVEN_LINES=$(echo "$CONTENT" | grep -n "Bash.*mvn\|Bash.*./mvnw\|Bash.*maven" || echo "")
if [ -n "$MAVEN_LINES" ]; then
    while IFS= read -r line; do
        LINE_NUM=$(echo "$line" | cut -d: -f1)
        LINE_TEXT=$(echo "$line" | cut -d: -f2-)
        MAVEN_CALLS="${MAVEN_CALLS}    {\"line\": $LINE_NUM, \"text\": $(echo "$LINE_TEXT" | jq -Rs .)},"
    done <<< "$MAVEN_LINES"
    # Remove trailing comma
    MAVEN_CALLS="${MAVEN_CALLS%,}"
fi

# Backup file patterns
BACKUP_LINES=$(echo "$CONTENT" | grep -n "\.backup\|\.bak\|\.old\|\.orig" || echo "")
if [ -n "$BACKUP_LINES" ]; then
    while IFS= read -r line; do
        LINE_NUM=$(echo "$line" | cut -d: -f1)
        LINE_TEXT=$(echo "$line" | cut -d: -f2-)
        BACKUP_PATTERNS="${BACKUP_PATTERNS}    {\"line\": $LINE_NUM, \"pattern\": $(echo "$LINE_TEXT" | jq -Rs .)},"
    done <<< "$BACKUP_LINES"
    # Remove trailing comma
    BACKUP_PATTERNS="${BACKUP_PATTERNS%,}"
fi

# Build JSON arrays (use printf to avoid echo's trailing newline)
MISSING_TOOLS_JSON=""
if [ -n "$MISSING_TOOLS" ]; then
    while IFS= read -r tool; do
        if [ -n "$tool" ]; then
            MISSING_TOOLS_JSON="${MISSING_TOOLS_JSON}    $(printf "%s" "$tool" | jq -Rs .),"
        fi
    done <<< "$MISSING_TOOLS"
    # Remove trailing comma
    MISSING_TOOLS_JSON="${MISSING_TOOLS_JSON%,}"
fi

UNUSED_TOOLS_JSON=""
if [ -n "$UNUSED_TOOLS" ]; then
    while IFS= read -r tool; do
        if [ -n "$tool" ]; then
            UNUSED_TOOLS_JSON="${UNUSED_TOOLS_JSON}    $(printf "%s" "$tool" | jq -Rs .),"
        fi
    done <<< "$UNUSED_TOOLS"
    # Remove trailing comma
    UNUSED_TOOLS_JSON="${UNUSED_TOOLS_JSON%,}"
fi

# Output JSON
cat <<EOF
{
  "file_path": "$FILE_PATH",
  "tool_coverage": {
    "declared_count": $DECLARED_COUNT,
    "used_count": $USED_COUNT,
    "missing_count": $MISSING_COUNT,
    "unused_count": $UNUSED_COUNT,
    "tool_fit_score": $TOOL_FIT_SCORE,
    "rating": "$RATING",
    "missing_tools": [
${MISSING_TOOLS_JSON}
    ],
    "unused_tools": [
${UNUSED_TOOLS_JSON}
    ]
  },
  "critical_violations": {
    "has_task_tool": $HAS_TASK_TOOL,
    "has_task_calls": $HAS_TASK_CALLS,
    "maven_calls": [
${MAVEN_CALLS}
    ],
    "backup_file_patterns": [
${BACKUP_PATTERNS}
    ]
  }
}
EOF
