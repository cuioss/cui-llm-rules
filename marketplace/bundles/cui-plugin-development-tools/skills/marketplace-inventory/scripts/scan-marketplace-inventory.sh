#!/bin/bash
# scan-marketplace-inventory.sh
#
# Purpose: Scan marketplace directories and return structured inventory
# Usage: ./scan-marketplace-inventory.sh [options]
#
# Returns JSON with bundles, agents, commands, skills, and statistics

set -euo pipefail

# ============================================================================
# DEFAULT PARAMETERS
# ============================================================================

SCOPE="marketplace"
RESOURCE_TYPES="all"
INCLUDE_DESCRIPTIONS=false

# ============================================================================
# USAGE AND HELP
# ============================================================================

usage() {
    cat <<EOF
Usage: $(basename "$0") [options]

Scans marketplace directories and returns structured inventory of bundles,
agents, commands, and skills.

Options:
  --scope <value>              Directory scope to scan (default: marketplace)
                               Values: marketplace, global, project

  --resource-types <types>     Resource types to include (default: all)
                               Values: agents, commands, skills, scripts, or comma-separated

  --include-descriptions       Extract descriptions from YAML frontmatter
                               (default: false, faster without descriptions)

  -h, --help                   Show this help message

Examples:
  $(basename "$0")
  $(basename "$0") --scope marketplace
  $(basename "$0") --resource-types agents,commands
  $(basename "$0") --resource-types scripts
  $(basename "$0") --include-descriptions

Exit codes:
  0 - Success (JSON output)
  1 - Error (invalid parameters, missing directory)
EOF
    exit 0
}

# ============================================================================
# PARAMETER PARSING
# ============================================================================

while [[ $# -gt 0 ]]; do
    case "$1" in
        --scope)
            SCOPE="$2"
            shift 2
            ;;
        --resource-types)
            RESOURCE_TYPES="$2"
            shift 2
            ;;
        --include-descriptions)
            INCLUDE_DESCRIPTIONS=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "ERROR: Unknown parameter: $1" >&2
            echo "Use --help for usage information" >&2
            exit 1
            ;;
    esac
done

# ============================================================================
# VALIDATE PARAMETERS
# ============================================================================

# Validate scope
case "$SCOPE" in
    marketplace|global|project)
        # Valid
        ;;
    *)
        echo "ERROR: Invalid scope: $SCOPE" >&2
        echo "Valid values: marketplace, global, project" >&2
        exit 1
        ;;
esac

# ============================================================================
# DETERMINE BASE PATH
# ============================================================================

BASE_PATH=""

case "$SCOPE" in
    marketplace)
        if [ -d "marketplace/bundles" ]; then
            BASE_PATH="$(pwd)/marketplace/bundles"
        elif [ -d "../marketplace/bundles" ]; then
            BASE_PATH="$(cd ../marketplace/bundles && pwd)"
        else
            echo "ERROR: marketplace/bundles directory not found" >&2
            exit 1
        fi
        ;;
    global)
        BASE_PATH="$HOME/.claude"
        ;;
    project)
        BASE_PATH="$(pwd)/.claude"
        ;;
esac

# Validate base path exists
if [ ! -d "$BASE_PATH" ]; then
    echo "ERROR: Base path not found: $BASE_PATH" >&2
    exit 1
fi

# ============================================================================
# RESOURCE TYPE FILTERING
# ============================================================================

INCLUDE_AGENTS=false
INCLUDE_COMMANDS=false
INCLUDE_SKILLS=false
INCLUDE_SCRIPTS=false

if [ "$RESOURCE_TYPES" = "all" ]; then
    INCLUDE_AGENTS=true
    INCLUDE_COMMANDS=true
    INCLUDE_SKILLS=true
    INCLUDE_SCRIPTS=true
else
    # Parse comma-separated list
    IFS=',' read -ra TYPES <<< "$RESOURCE_TYPES"
    for type in "${TYPES[@]}"; do
        type=$(echo "$type" | xargs)  # Trim whitespace
        case "$type" in
            agents)
                INCLUDE_AGENTS=true
                ;;
            commands)
                INCLUDE_COMMANDS=true
                ;;
            skills)
                INCLUDE_SKILLS=true
                ;;
            scripts)
                INCLUDE_SCRIPTS=true
                ;;
            *)
                echo "ERROR: Invalid resource type: $type" >&2
                echo "Valid values: agents, commands, skills, scripts" >&2
                exit 1
                ;;
        esac
    done
fi

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

json_escape() {
    local string="$1"
    string="${string//\\/\\\\}"
    string="${string//\"/\\\"}"
    string="${string//$'\n'/\\n}"
    string="${string//$'\r'/\\r}"
    string="${string//$'\t'/\\t}"
    echo "$string"
}

extract_description() {
    local file="$1"

    if [ ! -f "$file" ]; then
        echo "null"
        return
    fi

    # Check for YAML frontmatter
    if ! grep -q "^---$" "$file"; then
        echo "null"
        return
    fi

    # Extract frontmatter
    local frontmatter
    frontmatter=$(sed -n '/^---$/,/^---$/p' "$file" | sed '1d;$d')

    if [ -z "$frontmatter" ]; then
        echo "null"
        return
    fi

    # Extract description field
    if echo "$frontmatter" | grep -q "^description:"; then
        local desc
        desc=$(echo "$frontmatter" | grep "^description:" | sed 's/^description:[[:space:]]*//')
        if [ -n "$desc" ]; then
            echo "\"$(json_escape "$desc")\""
            return
        fi
    fi

    echo "null"
}

# ============================================================================
# BUNDLE DISCOVERY
# ============================================================================

# Find all bundles by locating plugin.json files
BUNDLE_DIRS=()
while IFS= read -r -d '' plugin_json; do
    bundle_dir=$(dirname "$(dirname "$plugin_json")")
    BUNDLE_DIRS+=("$bundle_dir")
done < <(find "$BASE_PATH" -name "plugin.json" -path "*/.claude-plugin/plugin.json" -print0 2>/dev/null)

# ============================================================================
# BUILD BUNDLE INVENTORY
# ============================================================================

BUNDLES_JSON="["
BUNDLE_COUNT=0
TOTAL_AGENTS=0
TOTAL_COMMANDS=0
TOTAL_SKILLS=0
TOTAL_SCRIPTS=0
TOTAL_RESOURCES=0

for bundle_dir in "${BUNDLE_DIRS[@]}"; do
    bundle_name=$(basename "$bundle_dir")

    # Add comma if not first bundle
    if [ "$BUNDLE_COUNT" -gt 0 ]; then
        BUNDLES_JSON="${BUNDLES_JSON},"
    fi

    BUNDLES_JSON="${BUNDLES_JSON}
    {
      \"name\": \"$bundle_name\",
      \"path\": \"${bundle_dir#$PWD/}\""

    # ========================================================================
    # DISCOVER AGENTS
    # ========================================================================

    AGENTS_JSON="[]"
    AGENT_COUNT=0

    if [ "$INCLUDE_AGENTS" = true ] && [ -d "$bundle_dir/agents" ]; then
        AGENTS_JSON="["
        first_agent=true

        while IFS= read -r -d '' agent_file; do
            agent_name=$(basename "$agent_file" .md)

            if [ "$first_agent" = false ]; then
                AGENTS_JSON="${AGENTS_JSON},"
            fi
            first_agent=false

            AGENTS_JSON="${AGENTS_JSON}
        {
          \"name\": \"$agent_name\",
          \"path\": \"${agent_file#$PWD/}\""

            if [ "$INCLUDE_DESCRIPTIONS" = true ]; then
                desc=$(extract_description "$agent_file")
                AGENTS_JSON="${AGENTS_JSON},
          \"description\": $desc"
            fi

            AGENTS_JSON="${AGENTS_JSON}
        }"

            AGENT_COUNT=$((AGENT_COUNT + 1))
        done < <(find "$bundle_dir/agents" -maxdepth 1 -name "*.md" -type f -print0 2>/dev/null)

        AGENTS_JSON="${AGENTS_JSON}
      ]"
    fi

    BUNDLES_JSON="${BUNDLES_JSON},
      \"agents\": $AGENTS_JSON"

    # ========================================================================
    # DISCOVER COMMANDS
    # ========================================================================

    COMMANDS_JSON="[]"
    COMMAND_COUNT=0

    if [ "$INCLUDE_COMMANDS" = true ] && [ -d "$bundle_dir/commands" ]; then
        COMMANDS_JSON="["
        first_command=true

        while IFS= read -r -d '' command_file; do
            command_name=$(basename "$command_file" .md)

            if [ "$first_command" = false ]; then
                COMMANDS_JSON="${COMMANDS_JSON},"
            fi
            first_command=false

            COMMANDS_JSON="${COMMANDS_JSON}
        {
          \"name\": \"$command_name\",
          \"path\": \"${command_file#$PWD/}\""

            if [ "$INCLUDE_DESCRIPTIONS" = true ]; then
                desc=$(extract_description "$command_file")
                COMMANDS_JSON="${COMMANDS_JSON},
          \"description\": $desc"
            fi

            COMMANDS_JSON="${COMMANDS_JSON}
        }"

            COMMAND_COUNT=$((COMMAND_COUNT + 1))
        done < <(find "$bundle_dir/commands" -maxdepth 1 -name "*.md" -type f -print0 2>/dev/null)

        COMMANDS_JSON="${COMMANDS_JSON}
      ]"
    fi

    BUNDLES_JSON="${BUNDLES_JSON},
      \"commands\": $COMMANDS_JSON"

    # ========================================================================
    # DISCOVER SKILLS
    # ========================================================================

    SKILLS_JSON="[]"
    SKILL_COUNT=0

    if [ "$INCLUDE_SKILLS" = true ] && [ -d "$bundle_dir/skills" ]; then
        SKILLS_JSON="["
        first_skill=true

        while IFS= read -r -d '' skill_md; do
            skill_dir=$(dirname "$skill_md")
            skill_name=$(basename "$skill_dir")

            if [ "$first_skill" = false ]; then
                SKILLS_JSON="${SKILLS_JSON},"
            fi
            first_skill=false

            SKILLS_JSON="${SKILLS_JSON}
        {
          \"name\": \"$skill_name\",
          \"path\": \"${skill_dir#$PWD/}\""

            if [ "$INCLUDE_DESCRIPTIONS" = true ]; then
                desc=$(extract_description "$skill_md")
                SKILLS_JSON="${SKILLS_JSON},
          \"description\": $desc"
            fi

            SKILLS_JSON="${SKILLS_JSON}
        }"

            SKILL_COUNT=$((SKILL_COUNT + 1))
        done < <(find "$bundle_dir/skills" -mindepth 2 -maxdepth 2 -name "SKILL.md" -type f -print0 2>/dev/null)

        SKILLS_JSON="${SKILLS_JSON}
      ]"
    fi

    BUNDLES_JSON="${BUNDLES_JSON},
      \"skills\": $SKILLS_JSON"

    # ========================================================================
    # DISCOVER SCRIPTS
    # ========================================================================

    SCRIPTS_JSON="[]"
    SCRIPT_COUNT=0

    if [ "$INCLUDE_SCRIPTS" = true ] && [ -d "$bundle_dir/skills" ]; then
        SCRIPTS_JSON="["
        first_script=true

        while IFS= read -r -d '' script_file; do
            # Extract script info - handle both .sh and .py extensions
            script_basename=$(basename "$script_file")
            script_name="${script_basename%.*}"
            script_ext="${script_basename##*.}"
            script_dir=$(dirname "$script_file")
            skill_dir=$(dirname "$script_dir")
            skill_name=$(basename "$skill_dir")

            if [ "$first_script" = false ]; then
                SCRIPTS_JSON="${SCRIPTS_JSON},"
            fi
            first_script=false

            # Generate three path formats
            relative_path="${script_file#$PWD/}"
            runtime_mount="./.claude/skills/$skill_name/scripts/$script_basename"

            # Determine script type
            script_type="bash"
            if [ "$script_ext" = "py" ]; then
                script_type="python"
            fi

            SCRIPTS_JSON="${SCRIPTS_JSON}
        {
          \"name\": \"$script_name\",
          \"skill\": \"$skill_name\",
          \"type\": \"$script_type\",
          \"path_formats\": {
            \"runtime\": \"$runtime_mount\",
            \"relative\": \"$relative_path\",
            \"absolute\": \"$script_file\"
          }
        }"

            SCRIPT_COUNT=$((SCRIPT_COUNT + 1))
        done < <(find "$bundle_dir/skills" -type f \( -name "*.sh" -o -name "*.py" \) -path "*/scripts/*" -print0 2>/dev/null)

        SCRIPTS_JSON="${SCRIPTS_JSON}
      ]"
    fi

    BUNDLES_JSON="${BUNDLES_JSON},
      \"scripts\": $SCRIPTS_JSON"

    # ========================================================================
    # BUNDLE STATISTICS
    # ========================================================================

    BUNDLE_TOTAL=$((AGENT_COUNT + COMMAND_COUNT + SKILL_COUNT + SCRIPT_COUNT))

    BUNDLES_JSON="${BUNDLES_JSON},
      \"statistics\": {
        \"agents\": $AGENT_COUNT,
        \"commands\": $COMMAND_COUNT,
        \"skills\": $SKILL_COUNT,
        \"scripts\": $SCRIPT_COUNT,
        \"total_resources\": $BUNDLE_TOTAL
      }
    }"

    # Update totals
    TOTAL_AGENTS=$((TOTAL_AGENTS + AGENT_COUNT))
    TOTAL_COMMANDS=$((TOTAL_COMMANDS + COMMAND_COUNT))
    TOTAL_SKILLS=$((TOTAL_SKILLS + SKILL_COUNT))
    TOTAL_SCRIPTS=$((TOTAL_SCRIPTS + SCRIPT_COUNT))
    BUNDLE_COUNT=$((BUNDLE_COUNT + 1))
done

BUNDLES_JSON="${BUNDLES_JSON}
  ]"

TOTAL_RESOURCES=$((TOTAL_AGENTS + TOTAL_COMMANDS + TOTAL_SKILLS + TOTAL_SCRIPTS))

# ============================================================================
# OUTPUT JSON
# ============================================================================

cat <<EOF
{
  "scope": "$SCOPE",
  "base_path": "$BASE_PATH",
  "bundles": $BUNDLES_JSON,
  "statistics": {
    "total_bundles": $BUNDLE_COUNT,
    "total_agents": $TOTAL_AGENTS,
    "total_commands": $TOTAL_COMMANDS,
    "total_skills": $TOTAL_SKILLS,
    "total_scripts": $TOTAL_SCRIPTS,
    "total_resources": $TOTAL_RESOURCES
  }
}
EOF
