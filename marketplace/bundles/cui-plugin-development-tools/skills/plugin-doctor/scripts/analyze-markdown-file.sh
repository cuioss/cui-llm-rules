#!/bin/bash
# Analyzes markdown file structure, frontmatter, and compliance
# Usage: analyze-markdown-file.sh <file_path> [component_type]
# Output: JSON with structural analysis

set -euo pipefail

# --help support
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    cat <<EOF
Usage: $(basename "$0") <file_path> [component_type]

Analyzes markdown file structure, frontmatter, and compliance with standards.

Arguments:
  file_path       Path to the markdown file to analyze
  component_type  Optional: agent, command, skill, or auto (default: auto)

Output: JSON with structural analysis including:
  - file_type: Detected component type
  - metrics.line_count: Total lines in file
  - frontmatter: Presence and validity of YAML frontmatter
  - continuous_improvement_rule: CI rule presence and pattern
  - bloat.classification: NORMAL, LARGE, BLOATED, or CRITICAL
  - execution_patterns: EXECUTION MODE, workflow tree, MANDATORY markers
  - rules: Rule 6, Rule 7, and Rule 8 violation detection
    * Rule 6: Task tool in agents
    * Rule 7: Direct Maven usage (should use cui-maven skill)
    * Rule 8: Hardcoded script paths (should use script-runner)
  - quality.has_forbidden_metadata: Forbidden metadata sections (Version, License, etc.)
  - quality.forbidden_sections: List of detected forbidden section names

Exit codes:
  0 - Success
  1 - Error (missing argument, file not found)

Examples:
  $(basename "$0") marketplace/bundles/cui-java-expert/agents/java-analyzer.md agent
  $(basename "$0") ./commands/my-command.md command
  $(basename "$0") ./skills/my-skill/SKILL.md
EOF
    exit 0
fi

FILE_PATH="${1:-}"
COMPONENT_TYPE="${2:-auto}"

if [ -z "$FILE_PATH" ]; then
    echo '{"error": "File path required. Use --help for usage."}' >&2
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
TOOLS_FIELD_TYPE="none"

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
    # Check tools field - agents use "tools:", skills use "allowed-tools:"
    if echo "$FRONTMATTER" | grep -q "^tools:"; then
        HAS_TOOLS="true"
        TOOLS_FIELD_TYPE="tools"
    fi
    if echo "$FRONTMATTER" | grep -q "^allowed-tools:"; then
        HAS_TOOLS="true"
        TOOLS_FIELD_TYPE="allowed-tools"
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

# Check for EXECUTION MODE directive (required for executable skills)
HAS_EXECUTION_MODE="false"
if grep -qi "EXECUTION MODE" "$FILE_PATH"; then
    HAS_EXECUTION_MODE="true"
fi

# Check for Workflow Decision Tree (for skills)
HAS_WORKFLOW_TREE="false"
if grep -qi "Workflow Decision Tree" "$FILE_PATH"; then
    HAS_WORKFLOW_TREE="true"
fi

# Check for MANDATORY markers
MANDATORY_COUNT=$(grep -c "\\*\\*MANDATORY\\*\\*" "$FILE_PATH" 2>/dev/null | tr -d '\n' || echo "0")

# Check for CRITICAL HANDOFF RULES (required for commands loading skills)
HAS_HANDOFF_RULES="false"
if grep -qi "CRITICAL HANDOFF" "$FILE_PATH"; then
    HAS_HANDOFF_RULES="true"
fi

# Check Rule 6: Task tool prohibition in agents
RULE_6_VIOLATION="false"
if [ "$COMPONENT_TYPE" == "agent" ] && [ "$HAS_TOOLS" == "true" ]; then
    # Check if Task appears in the tools array (either "- Task" or "Task," in comma-separated format)
    if echo "$FRONTMATTER" | grep -qE "^  - Task$|Task,|Task$"; then
        RULE_6_VIOLATION="true"
    fi
fi

# Check Rule 7: Maven execution restriction (expanded to all components)
RULE_7_VIOLATION="false"
# Check for direct mvn usage (should use cui-maven skill instead)
if grep -qE "mvn |maven |./mvnw " "$FILE_PATH"; then
    # Exclude maven-specific bundles/skills
    if ! echo "$FILE_PATH" | grep -q "cui-maven"; then
        # Check if it's just documentation/comments
        if ! grep -E "mvn |maven |./mvnw " "$FILE_PATH" | grep -q "^[[:space:]]*#\|^[[:space:]]*//"; then
            RULE_7_VIOLATION="true"
        fi
    fi
fi

# Check Rule 8: Script-runner usage (no hardcoded paths)
RULE_8_VIOLATION="false"
# Check for hardcoded script paths (should use script-runner with portable notation)
if grep -qE "python3 .*/scripts/|bash .*/scripts/|{[^}]+}/scripts/" "$FILE_PATH"; then
    # Check if it's using script-runner skill (acceptable)
    if ! grep -q "Skill:.*script-runner" "$FILE_PATH"; then
        RULE_8_VIOLATION="true"
    fi
fi

# Check for forbidden metadata sections (version, license, changelog, author)
# These are artifacts that should not appear in marketplace components
# License is repo-wide (Apache-2.0), version/changelog violate no-history rule
HAS_FORBIDDEN_METADATA="false"
FORBIDDEN_SECTIONS=""
if grep -qE "^## (Version|Version History|License|Changelog|Change Log|Author|Revision History)$" "$FILE_PATH"; then
    HAS_FORBIDDEN_METADATA="true"
    FORBIDDEN_SECTIONS=$(grep -oE "^## (Version|Version History|License|Changelog|Change Log|Author|Revision History)$" "$FILE_PATH" | sed 's/^## //' | tr '\n' ',' | sed 's/,$//')
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
        "present": $HAS_TOOLS,
        "field_type": "$TOOLS_FIELD_TYPE"
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
  "execution_patterns": {
    "has_execution_mode": $HAS_EXECUTION_MODE,
    "has_workflow_tree": $HAS_WORKFLOW_TREE,
    "mandatory_marker_count": $MANDATORY_COUNT,
    "has_handoff_rules": $HAS_HANDOFF_RULES
  },
  "rules": {
    "rule_6_violation": $RULE_6_VIOLATION,
    "rule_7_violation": $RULE_7_VIOLATION,
    "rule_8_violation": $RULE_8_VIOLATION
  },
  "quality": {
    "has_forbidden_metadata": $HAS_FORBIDDEN_METADATA,
    "forbidden_sections": "$FORBIDDEN_SECTIONS"
  }
}
EOF
