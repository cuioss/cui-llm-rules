#!/bin/bash
# analyze-markdown-file.sh
# Analyzes a markdown file and returns structured JSON with metrics and content blocks
#
# Usage: ./analyze-markdown-file.sh <file_path>
# Returns: JSON object with file analysis

set -euo pipefail

# Check arguments
if [ $# -ne 1 ]; then
    echo '{"error": "Usage: analyze-markdown-file.sh <file_path>"}' >&2
    exit 1
fi

FILE_PATH="$1"

# Check file exists
if [ ! -f "$FILE_PATH" ]; then
    echo "{\"error\": \"File not found: $FILE_PATH\"}" >&2
    exit 1
fi

# Get basic metrics
LINE_COUNT=$(wc -l < "$FILE_PATH" | tr -d ' ')
WORD_COUNT=$(wc -w < "$FILE_PATH" | tr -d ' ')
CHAR_COUNT=$(wc -c < "$FILE_PATH" | tr -d ' ')

# Calculate bloat classification and score
if [ "$LINE_COUNT" -gt 500 ]; then
    CLASSIFICATION="BLOATED"
elif [ "$LINE_COUNT" -gt 400 ]; then
    CLASSIFICATION="LARGE"
else
    CLASSIFICATION="ACCEPTABLE"
fi

# Bloat score: (line_count / 400) * 100
BLOAT_SCORE=$(awk "BEGIN {printf \"%.1f\", ($LINE_COUNT / 400.0) * 100}")

# Extract YAML frontmatter (between first two --- markers)
FRONTMATTER=""
if head -1 "$FILE_PATH" | grep -q "^---$"; then
    FRONTMATTER=$(sed -n '2,/^---$/p' "$FILE_PATH" | sed '$d')
fi

# Check for CONTINUOUS IMPROVEMENT RULE section
HAS_CI_RULE=false
CI_RULE_CONTENT=""
CI_RULE_LINE=0

if grep -qi "CONTINUOUS IMPROVEMENT" "$FILE_PATH"; then
    HAS_CI_RULE=true
    # Get line number of the heading line (##+ CONTINUOUS IMPROVEMENT)
    CI_RULE_LINE=$(grep -n -E "^##+ CONTINUOUS IMPROVEMENT" "$FILE_PATH" | head -1 | cut -d: -f1)

    # If not found as heading, get first mention line
    if [ -z "$CI_RULE_LINE" ] || [ "$CI_RULE_LINE" = "0" ]; then
        CI_RULE_LINE=$(grep -n -i "CONTINUOUS IMPROVEMENT" "$FILE_PATH" | head -1 | cut -d: -f1)
    fi

    # Extract section content (from heading line to next ## heading or end of file)
    # Limit to ~50 lines max to avoid huge output
    CI_RULE_CONTENT=$(awk -v start="$CI_RULE_LINE" '
        NR == start { print; in_section=1; count=1; next }
        in_section {
            if (/^##[^#]/ || count > 50) exit;
            print;
            count++;
        }
    ' "$FILE_PATH")
fi

# Escape JSON strings (handle quotes, backslashes, newlines)
escape_json() {
    local input="$1"
    # Replace backslash, then quotes, then newlines, then tabs
    echo "$input" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}' | sed 's/\\n$//'
}

FRONTMATTER_ESCAPED=$(escape_json "$FRONTMATTER")
CI_RULE_ESCAPED=$(escape_json "$CI_RULE_CONTENT")

# Build JSON output
cat <<EOF
{
  "file_path": "$FILE_PATH",
  "metrics": {
    "line_count": $LINE_COUNT,
    "word_count": $WORD_COUNT,
    "char_count": $CHAR_COUNT
  },
  "bloat": {
    "classification": "$CLASSIFICATION",
    "score": $BLOAT_SCORE
  },
  "frontmatter": {
    "present": $([ -n "$FRONTMATTER" ] && echo "true" || echo "false"),
    "content": "$FRONTMATTER_ESCAPED"
  },
  "continuous_improvement_rule": {
    "present": $HAS_CI_RULE,
    "line_number": $CI_RULE_LINE,
    "content": "$CI_RULE_ESCAPED"
  }
}
EOF
