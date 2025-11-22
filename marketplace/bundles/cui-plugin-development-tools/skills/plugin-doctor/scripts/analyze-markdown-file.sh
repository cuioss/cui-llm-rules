#!/bin/bash
# Analyzes markdown file structure, frontmatter, and compliance
# Usage: analyze-markdown-file.sh <file_path> [component_type]
# Output: JSON with structural analysis

set -euo pipefail

FILE_PATH="${1:-}"
COMPONENT_TYPE="${2:-auto}"

if [ -z "$FILE_PATH" ]; then
    echo '{"error": "File path required"}' >&2
    exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
    echo "{\"error\": \"File not found: $FILE_PATH\"}" >&2
    exit 1
fi

# Count lines
LINE_COUNT=$(wc -l < "$FILE_PATH" | tr -d ' ')

# Detect file type if auto
if [ "$COMPONENT_TYPE" == "auto" ]; then
    if echo "$FILE_PATH" | grep -q "/commands/"; then
        COMPONENT_TYPE="command"
    elif echo "$FILE_PATH" | grep -q "/agents/"; then
        COMPONENT_TYPE="agent"
    elif echo "$FILE_PATH" | grep -q "/skills/"; then
        COMPONENT_TYPE="skill"
    else
        COMPONENT_TYPE="unknown"
    fi
fi

# Check frontmatter presence
FRONTMATTER_PRESENT="false"
YAML_VALID="false"
HAS_NAME="false"
HAS_DESC="false"
HAS_TOOLS="false"

if head -1 "$FILE_PATH" | grep -q "^---$"; then
    FRONTMATTER_PRESENT="true"

    # Extract frontmatter
    FRONTMATTER=$(awk '/^---$/{if(++count==2) exit; if(count==1) next} count==1' "$FILE_PATH")

    # Check YAML validity (basic check)
    if echo "$FRONTMATTER" | grep -q "^[a-z_]*:"; then
        YAML_VALID="true"
    fi

    # Check required fields
    if echo "$FRONTMATTER" | grep -q "^name:"; then
        HAS_NAME="true"
    fi
    if echo "$FRONTMATTER" | grep -q "^description:"; then
        HAS_DESC="true"
    fi
    if echo "$FRONTMATTER" | grep -q "^tools:"; then
        HAS_TOOLS="true"
    fi
fi

# Check CONTINUOUS IMPROVEMENT RULE
CI_RULE_PRESENT="false"
CI_PATTERN="none"
PATTERN_22_VIOLATION="false"

if grep -qi "CONTINUOUS IMPROVEMENT" "$FILE_PATH"; then
    CI_RULE_PRESENT="true"

    # Detect pattern
    if grep -q "/plugin-update-command\|/plugin-update-agent" "$FILE_PATH"; then
        CI_PATTERN="self-update"
    elif grep -qi "REPORT.*improvement\|report.*to.*caller" "$FILE_PATH"; then
        CI_PATTERN="caller-reporting"
    fi

    # Check Pattern 22 violation (self-invocation in agents)
    if [ "$COMPONENT_TYPE" == "agent" ] && [ "$CI_PATTERN" == "self-update" ]; then
        PATTERN_22_VIOLATION="true"
    fi
fi

# Count sections (## headings)
SECTION_COUNT=$(grep -c "^## " "$FILE_PATH" || echo "0")

# Check for parameters section
HAS_PARAM_SECTION="false"
if grep -qi "^## PARAMETERS\|^### Parameters" "$FILE_PATH"; then
    HAS_PARAM_SECTION="true"
fi

# Bloat classification based on line count
BLOAT_CLASS="NORMAL"
if [ "$LINE_COUNT" -gt 800 ]; then
    BLOAT_CLASS="CRITICAL"
elif [ "$LINE_COUNT" -gt 500 ]; then
    BLOAT_CLASS="BLOATED"
elif [ "$LINE_COUNT" -gt 300 ]; then
    BLOAT_CLASS="LARGE"
fi

# Check Rule 6: Task tool prohibition in agents
RULE_6_VIOLATION="false"
if [ "$COMPONENT_TYPE" == "agent" ] && [ "$HAS_TOOLS" == "true" ]; then
    # Check if Task appears in the tools array (either "- Task" or "Task," in comma-separated format)
    if echo "$FRONTMATTER" | grep -qE "^  - Task$|Task,|Task$"; then
        RULE_6_VIOLATION="true"
    fi
fi

# Check Rule 7: Maven execution restriction
RULE_7_VIOLATION="false"
if [ "$COMPONENT_TYPE" == "agent" ] && [ "$HAS_TOOLS" == "true" ]; then
    AGENT_NAME=$(basename "$FILE_PATH" .md)
    if [ "$AGENT_NAME" != "maven-builder" ]; then
        # Check if agent uses Maven via Bash
        if grep -q "Bash.*maven\|Bash.*mvn\|Bash.*./mvnw" "$FILE_PATH"; then
            RULE_7_VIOLATION="true"
        fi
    fi
fi

# Output JSON
cat <<EOF
{
  "file_path": "$FILE_PATH",
  "file_type": {
    "type": "$COMPONENT_TYPE"
  },
  "metrics": {
    "line_count": $LINE_COUNT
  },
  "frontmatter": {
    "present": $FRONTMATTER_PRESENT,
    "yaml_valid": $YAML_VALID,
    "required_fields": {
      "name": {
        "present": $HAS_NAME
      },
      "description": {
        "present": $HAS_DESC
      },
      "tools": {
        "present": $HAS_TOOLS
      }
    }
  },
  "structure": {
    "section_count": $SECTION_COUNT
  },
  "parameters": {
    "has_section": $HAS_PARAM_SECTION
  },
  "continuous_improvement_rule": {
    "present": $CI_RULE_PRESENT,
    "format": {
      "pattern": "$CI_PATTERN",
      "pattern_22_violation": $PATTERN_22_VIOLATION
    }
  },
  "bloat": {
    "classification": "$BLOAT_CLASS"
  },
  "rules": {
    "rule_6_violation": $RULE_6_VIOLATION,
    "rule_7_violation": $RULE_7_VIOLATION
  }
}
EOF
