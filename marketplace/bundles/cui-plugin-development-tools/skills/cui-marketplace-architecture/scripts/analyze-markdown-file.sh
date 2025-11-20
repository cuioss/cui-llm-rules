#!/bin/bash
# analyze-markdown-file.sh
# Analyzes a markdown file and returns structured JSON with metrics and content blocks
#
# Usage: ./analyze-markdown-file.sh <file_path>
# Returns: JSON object with file analysis

set -euo pipefail

# Help function
show_help() {
    cat << EOF
Usage: analyze-markdown-file.sh <file_path>

Description:
  Analyzes agent/command markdown files for structure, bloat classification,
  YAML frontmatter validity, and continuous improvement patterns.

Arguments:
  file_path    Path to the agent/command .md file to analyze (required)

Output:
  JSON object with comprehensive file analysis:
  - Basic metrics (lines, words, characters)
  - Bloat classification (ACCEPTABLE/LARGE/BLOATED)
  - File type detection (agent/command)
  - YAML frontmatter validation
  - Section structure analysis
  - Continuous improvement rule detection
  - Parameter documentation detection

Exit Codes:
  0 - Success
  1 - Invalid arguments or file not found
  2 - Analysis error

Examples:
  analyze-markdown-file.sh marketplace/bundles/cui-java-expert/agents/log-record-documenter.md
  analyze-markdown-file.sh marketplace/bundles/cui-task-workflow/commands/orchestrate-language.md
EOF
    exit 0
}

# Check for help flag
if [ $# -eq 1 ] && { [ "$1" == "--help" ] || [ "$1" == "-h" ]; }; then
    show_help
fi

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

# ============================================================================
# BASIC METRICS
# ============================================================================

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

BLOAT_SCORE=$(awk "BEGIN {printf \"%.1f\", ($LINE_COUNT / 400.0) * 100}")

# ============================================================================
# ENHANCEMENT 1B: FILE TYPE DETECTION
# ============================================================================

FILE_TYPE="unknown"
PATH_PATTERN=""

if [[ "$FILE_PATH" =~ /commands/[^/]+\.md$ ]]; then
    FILE_TYPE="command"
    PATH_PATTERN="*/commands/*.md"
elif [[ "$FILE_PATH" =~ /agents/[^/]+\.md$ ]]; then
    FILE_TYPE="agent"
    PATH_PATTERN="*/agents/*.md"
elif [[ "$FILE_PATH" =~ /SKILL\.md$ ]]; then
    FILE_TYPE="skill"
    PATH_PATTERN="*/SKILL.md"
fi

# ============================================================================
# ENHANCEMENT 1A: YAML FRONTMATTER VALIDATION
# ============================================================================

FRONTMATTER=""
HAS_FRONTMATTER=false
YAML_VALID=true
YAML_PARSE_ERRORS=()
FIELD_ERRORS=()

# Extract frontmatter
if head -1 "$FILE_PATH" | grep -q "^---$"; then
    FRONTMATTER=$(sed -n '2,/^---$/p' "$FILE_PATH" | sed '$d')
    if [ -n "$FRONTMATTER" ]; then
        HAS_FRONTMATTER=true
    fi
fi

# Parse YAML fields
YAML_NAME=""
YAML_DESCRIPTION=""
YAML_DESCRIPTION_LENGTH=0
YAML_TOOLS=""
YAML_MODEL=""
YAML_COLOR=""

NAME_PRESENT=false
DESC_PRESENT=false

if [ "$HAS_FRONTMATTER" = true ]; then
    # Extract name
    if echo "$FRONTMATTER" | grep -q "^name:"; then
        YAML_NAME=$(echo "$FRONTMATTER" | grep "^name:" | sed 's/^name:[[:space:]]*//' | sed 's/^["'"'"']//' | sed 's/["'"'"']$//')
        NAME_PRESENT=true
    fi

    # Extract description
    if echo "$FRONTMATTER" | grep -q "^description:"; then
        YAML_DESCRIPTION=$(echo "$FRONTMATTER" | grep "^description:" | sed 's/^description:[[:space:]]*//' | sed 's/^["'"'"']//' | sed 's/["'"'"']$//')
        DESC_PRESENT=true
        YAML_DESCRIPTION_LENGTH=${#YAML_DESCRIPTION}
    fi

    # Extract tools or allowed-tools
    if echo "$FRONTMATTER" | grep -q "^tools:"; then
        YAML_TOOLS="tools"
    elif echo "$FRONTMATTER" | grep -q "^allowed-tools:"; then
        YAML_TOOLS="allowed-tools"
    fi

    # Extract model
    if echo "$FRONTMATTER" | grep -q "^model:"; then
        YAML_MODEL=$(echo "$FRONTMATTER" | grep "^model:" | sed 's/^model:[[:space:]]*//')
    fi

    # Extract color
    if echo "$FRONTMATTER" | grep -q "^color:"; then
        YAML_COLOR=$(echo "$FRONTMATTER" | grep "^color:" | sed 's/^color:[[:space:]]*//')
    fi

    # Validation checks
    if [ "$NAME_PRESENT" = false ]; then
        YAML_PARSE_ERRORS+=("Missing required field: name")
        YAML_VALID=false
    fi

    if [ "$DESC_PRESENT" = false ]; then
        YAML_PARSE_ERRORS+=("Missing required field: description")
        YAML_VALID=false
    fi

    # Check description length for agents/commands (max 200 chars)
    if [ "$FILE_TYPE" = "agent" ] || [ "$FILE_TYPE" = "command" ]; then
        if [ "$YAML_DESCRIPTION_LENGTH" -gt 200 ]; then
            FIELD_ERRORS+=("description: Length $YAML_DESCRIPTION_LENGTH exceeds 200 chars")
        fi
    fi

    # Check wrong field names
    if [ "$FILE_TYPE" = "skill" ] && [ "$YAML_TOOLS" = "tools" ]; then
        FIELD_ERRORS+=("tools: Should be 'allowed-tools' for skills")
    elif [ "$FILE_TYPE" != "skill" ] && [ "$FILE_TYPE" != "unknown" ] && [ "$YAML_TOOLS" = "allowed-tools" ]; then
        FIELD_ERRORS+=("allowed-tools: Should be 'tools' for agents/commands")
    fi

    # Basic YAML syntax check - look for unclosed quotes
    if echo "$FRONTMATTER" | grep -q -E '(^|[^\\])"[^"]*$'; then
        YAML_PARSE_ERRORS+=("Possible unclosed quote in YAML")
        YAML_VALID=false
    fi
fi

# ============================================================================
# ENHANCEMENT 1C: SECTION STRUCTURE ANALYSIS
# ============================================================================

# Count sections (## headings)
SECTION_COUNT=$(grep -c "^##[[:space:]]" "$FILE_PATH" 2>/dev/null || true)
if ! [[ "$SECTION_COUNT" =~ ^[0-9]+$ ]]; then
    SECTION_COUNT=0
fi

# Extract section names (limit to first 50 to avoid huge output)
SECTIONS_RAW=$(grep "^##[[:space:]]" "$FILE_PATH" | sed 's/^##[[:space:]]*//' | head -50)
SECTIONS_JSON="[]"
if [ -n "$SECTIONS_RAW" ]; then
    # Build JSON array of sections
    SECTIONS_JSON="["
    first=true
    while IFS= read -r section; do
        if [ "$first" = true ]; then
            first=false
        else
            SECTIONS_JSON+=","
        fi
        # Escape quotes in section name
        section_escaped=$(echo "$section" | sed 's/"/\\"/g')
        SECTIONS_JSON+="\"$section_escaped\""
    done <<< "$SECTIONS_RAW"
    SECTIONS_JSON+="]"
fi

# Check for required sections
HAS_YOUR_TASK=$(echo "$SECTIONS_RAW" | grep -qi "YOUR TASK" && echo "true" || echo "false")
HAS_INPUT_PARAMETERS=$(echo "$SECTIONS_RAW" | grep -qi "INPUT PARAMETERS\|^PARAMETERS$" && echo "true" || echo "false")
HAS_WORKFLOW=$(echo "$SECTIONS_RAW" | grep -qi "WORKFLOW" && echo "true" || echo "false")
HAS_CRITICAL_RULES=$(echo "$SECTIONS_RAW" | grep -qi "CRITICAL RULES" && echo "true" || echo "false")

# Count workflow steps (### Step N:)
WORKFLOW_STEPS=$(grep -c "^###[[:space:]]*Step[[:space:]]*[0-9]" "$FILE_PATH" 2>/dev/null || true)
if ! [[ "$WORKFLOW_STEPS" =~ ^[0-9]+$ ]]; then
    WORKFLOW_STEPS=0
fi

# Count code blocks (```)
CODE_BLOCKS=$(grep -c '^```' "$FILE_PATH" 2>/dev/null || true)
if ! [[ "$CODE_BLOCKS" =~ ^[0-9]+$ ]]; then
    CODE_BLOCKS=0
fi
# Code blocks come in pairs, so divide by 2
CODE_BLOCKS=$((CODE_BLOCKS / 2))

# ============================================================================
# CONTINUOUS IMPROVEMENT RULE - BASE DETECTION
# ============================================================================

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

# ============================================================================
# ENHANCEMENT 1D: CI RULE FORMAT VALIDATION
# ============================================================================

CI_FORMAT="unknown"
CI_HAS_UPDATE_INSTRUCTION=false
CI_UPDATE_COMMAND=""
CI_HAS_IMPROVEMENT_AREAS=false
CI_IMPROVEMENT_AREA_COUNT=0
CI_PATTERN_22_VIOLATION=false

if [ "$HAS_CI_RULE" = true ] && [ -n "$CI_RULE_CONTENT" ]; then
    # Detect pattern type
    if echo "$CI_RULE_CONTENT" | grep -qi "YOU MUST.*update this file"; then
        # Self-update pattern
        if echo "$CI_RULE_CONTENT" | grep -qi "/plugin-update-command"; then
            CI_FORMAT="self-update"
            CI_UPDATE_COMMAND="/plugin-update-command"
            CI_HAS_UPDATE_INSTRUCTION=true
        elif echo "$CI_RULE_CONTENT" | grep -qi "/plugin-update-agent"; then
            CI_FORMAT="self-update"
            CI_UPDATE_COMMAND="/plugin-update-agent"
            CI_HAS_UPDATE_INSTRUCTION=true

            # Check for Pattern 22 violation (agent with self-update)
            if [ "$FILE_TYPE" = "agent" ]; then
                CI_PATTERN_22_VIOLATION=true
            fi
        fi
    elif echo "$CI_RULE_CONTENT" | grep -qi "REPORT.*improvement.*to.*caller"; then
        # Caller-reporting pattern
        CI_FORMAT="caller-reporting"
        CI_HAS_UPDATE_INSTRUCTION=true

        # Extract update command mentioned
        if echo "$CI_RULE_CONTENT" | grep -qi "/plugin-update-agent"; then
            CI_UPDATE_COMMAND="/plugin-update-agent"
        elif echo "$CI_RULE_CONTENT" | grep -qi "/plugin-update-command"; then
            CI_UPDATE_COMMAND="/plugin-update-command"
        fi
    fi

    # Count improvement areas (bullet points or numbered items)
    # Look for lines starting with - or 1. 2. etc
    CI_IMPROVEMENT_AREA_COUNT=$(echo "$CI_RULE_CONTENT" | grep -c "^[[:space:]]*[-*]" 2>/dev/null || true)
    if ! [[ "$CI_IMPROVEMENT_AREA_COUNT" =~ ^[0-9]+$ ]]; then
        CI_IMPROVEMENT_AREA_COUNT=0
    fi

    if [ "$CI_IMPROVEMENT_AREA_COUNT" -gt 0 ]; then
        CI_HAS_IMPROVEMENT_AREAS=true
    else
        # Try numbered list
        CI_IMPROVEMENT_AREA_COUNT=$(echo "$CI_RULE_CONTENT" | grep -c "^[[:space:]]*[0-9]\\." 2>/dev/null || true)
        if ! [[ "$CI_IMPROVEMENT_AREA_COUNT" =~ ^[0-9]+$ ]]; then
            CI_IMPROVEMENT_AREA_COUNT=0
        fi
        if [ "$CI_IMPROVEMENT_AREA_COUNT" -gt 0 ]; then
            CI_HAS_IMPROVEMENT_AREAS=true
        fi
    fi
fi

# ============================================================================
# ENHANCEMENT 1E: PARAMETER DOCUMENTATION CHECK
# ============================================================================

PARAMS_HAS_SECTION=false
PARAMS_SECTION_NAME=""
PARAMS_COUNT=0
PARAMS_DOCUMENTED=()

# Look for INPUT PARAMETERS or PARAMETERS section
if grep -qi "^##.*INPUT PARAMETERS" "$FILE_PATH"; then
    PARAMS_HAS_SECTION=true
    PARAMS_SECTION_NAME="INPUT PARAMETERS"
elif grep -qi "^##.*PARAMETERS" "$FILE_PATH"; then
    PARAMS_HAS_SECTION=true
    PARAMS_SECTION_NAME="PARAMETERS"
fi

if [ "$PARAMS_HAS_SECTION" = true ]; then
    # Extract parameters section
    PARAMS_SECTION=$(awk '/^##.*PARAMETERS/,/^##[^#]/' "$FILE_PATH")

    # Count parameter items (lines with `param_name`)
    PARAMS_COUNT=$(echo "$PARAMS_SECTION" | grep -c "\`[a-zA-Z_][a-zA-Z0-9_]*\`" 2>/dev/null || true)
    # If grep returned empty or non-numeric, default to 0
    if ! [[ "$PARAMS_COUNT" =~ ^[0-9]+$ ]]; then
        PARAMS_COUNT=0
    fi
fi

# ============================================================================
# JSON ESCAPING HELPER
# ============================================================================

escape_json() {
    local input="$1"
    # Replace backslash, then quotes, then newlines, then tabs
    echo "$input" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | awk '{printf "%s\\n", $0}' | sed 's/\\n$//'
}

FRONTMATTER_ESCAPED=$(escape_json "$FRONTMATTER")
CI_RULE_ESCAPED=$(escape_json "$CI_RULE_CONTENT")
YAML_NAME_ESCAPED=$(escape_json "$YAML_NAME")
YAML_DESCRIPTION_ESCAPED=$(escape_json "$YAML_DESCRIPTION")

# ============================================================================
# BUILD JSON ARRAYS FOR ERRORS
# ============================================================================

# Build parse_errors JSON array
PARSE_ERRORS_JSON="[]"
if [ ${#YAML_PARSE_ERRORS[@]} -gt 0 ]; then
    PARSE_ERRORS_JSON="["
    first=true
    for error in "${YAML_PARSE_ERRORS[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            PARSE_ERRORS_JSON+=","
        fi
        error_escaped=$(escape_json "$error")
        PARSE_ERRORS_JSON+="\"$error_escaped\""
    done
    PARSE_ERRORS_JSON+="]"
fi

# Build field_errors JSON array
FIELD_ERRORS_JSON="[]"
if [ ${#FIELD_ERRORS[@]} -gt 0 ]; then
    FIELD_ERRORS_JSON="["
    first=true
    for error in "${FIELD_ERRORS[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            FIELD_ERRORS_JSON+=","
        fi
        error_escaped=$(escape_json "$error")
        FIELD_ERRORS_JSON+="\"$error_escaped\""
    done
    FIELD_ERRORS_JSON+="]"
fi

# ============================================================================
# BUILD AND OUTPUT JSON
# ============================================================================

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
  "file_type": {
    "type": "$FILE_TYPE",
    "path_pattern": "$PATH_PATTERN"
  },
  "frontmatter": {
    "present": $HAS_FRONTMATTER,
    "content": "$FRONTMATTER_ESCAPED",
    "yaml_valid": $YAML_VALID,
    "parse_errors": $PARSE_ERRORS_JSON,
    "required_fields": {
      "name": {
        "present": $NAME_PRESENT,
        "value": "$YAML_NAME_ESCAPED"
      },
      "description": {
        "present": $DESC_PRESENT,
        "value": "$YAML_DESCRIPTION_ESCAPED",
        "length": $YAML_DESCRIPTION_LENGTH
      }
    },
    "field_errors": $FIELD_ERRORS_JSON
  },
  "structure": {
    "section_count": $SECTION_COUNT,
    "sections": $SECTIONS_JSON,
    "required_sections": {
      "YOUR TASK": $HAS_YOUR_TASK,
      "INPUT PARAMETERS": $HAS_INPUT_PARAMETERS,
      "WORKFLOW": $HAS_WORKFLOW,
      "CRITICAL RULES": $HAS_CRITICAL_RULES
    },
    "workflow_steps": $WORKFLOW_STEPS,
    "code_blocks": $CODE_BLOCKS
  },
  "continuous_improvement_rule": {
    "present": $HAS_CI_RULE,
    "line_number": $CI_RULE_LINE,
    "content": "$CI_RULE_ESCAPED",
    "format": {
      "pattern": "$CI_FORMAT",
      "has_update_instruction": $CI_HAS_UPDATE_INSTRUCTION,
      "update_command": "$CI_UPDATE_COMMAND",
      "has_improvement_areas": $CI_HAS_IMPROVEMENT_AREAS,
      "improvement_area_count": $CI_IMPROVEMENT_AREA_COUNT,
      "pattern_22_violation": $CI_PATTERN_22_VIOLATION
    }
  },
  "parameters": {
    "has_section": $PARAMS_HAS_SECTION,
    "section_name": "$PARAMS_SECTION_NAME",
    "count": $PARAMS_COUNT
  }
}
EOF
