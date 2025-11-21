#!/usr/bin/env bash
# Generate README from bundle inventory
#
# Usage: generate-readme.sh <bundle_path>
#
# Outputs JSON with generated README content.

set -euo pipefail

BUNDLE_PATH="${1:-}"

if [ -z "$BUNDLE_PATH" ]; then
    echo '{"error": "Usage: generate-readme.sh <bundle_path>"}'
    exit 1
fi

if [ ! -d "$BUNDLE_PATH" ]; then
    echo "{\"error\": \"Bundle directory not found: $BUNDLE_PATH\"}"
    exit 1
fi

# Check for plugin.json
if [ ! -f "$BUNDLE_PATH/plugin.json" ]; then
    echo "{\"error\": \"Missing plugin.json in bundle: $BUNDLE_PATH\"}"
    exit 1
fi

# Extract bundle name from plugin.json
BUNDLE_NAME=""
if command -v python3 &> /dev/null; then
    BUNDLE_NAME=$(python3 -c "import json; print(json.load(open('$BUNDLE_PATH/plugin.json')).get('name', 'Unknown'))" 2>/dev/null || echo "Unknown")
else
    # Fallback: grep for name
    BUNDLE_NAME=$(grep -o '"name"[[:space:]]*:[[:space:]]*"[^"]*"' "$BUNDLE_PATH/plugin.json" | head -1 | sed 's/.*"\([^"]*\)"$/\1/' || echo "Unknown")
fi

# Extract frontmatter description from component file
extract_description() {
    local file="$1"
    if [ ! -f "$file" ]; then
        echo "No description"
        return
    fi

    # Look for description in frontmatter
    if head -1 "$file" | grep -q '^---'; then
        awk '/^---$/{if(++count==2) exit} count==1 && /^description:/{sub(/^description:[[:space:]]*/, ""); print; found=1} END{if(!found) print "No description"}' "$file"
    else
        echo "No description"
    fi
}

# Build commands list
COMMANDS_JSON="[]"
COMMANDS_COUNT=0
if [ -d "$BUNDLE_PATH/commands" ]; then
    COMMANDS_LIST=""
    for cmd_file in "$BUNDLE_PATH/commands"/*.md; do
        if [ -f "$cmd_file" ]; then
            CMD_NAME=$(basename "$cmd_file" .md)
            CMD_DESC=$(extract_description "$cmd_file")
            if [ -n "$COMMANDS_LIST" ]; then
                COMMANDS_LIST="${COMMANDS_LIST},"
            fi
            # Escape for JSON
            CMD_DESC_ESC=$(printf '%s' "$CMD_DESC" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')
            COMMANDS_LIST="${COMMANDS_LIST}{\"name\":\"$CMD_NAME\",\"description\":$CMD_DESC_ESC}"
            COMMANDS_COUNT=$((COMMANDS_COUNT + 1))
        fi
    done
    if [ -n "$COMMANDS_LIST" ]; then
        COMMANDS_JSON="[$COMMANDS_LIST]"
    fi
fi

# Build agents list
AGENTS_JSON="[]"
AGENTS_COUNT=0
if [ -d "$BUNDLE_PATH/agents" ]; then
    AGENTS_LIST=""
    for agent_file in "$BUNDLE_PATH/agents"/*.md; do
        if [ -f "$agent_file" ]; then
            AGENT_NAME=$(basename "$agent_file" .md)
            AGENT_DESC=$(extract_description "$agent_file")
            if [ -n "$AGENTS_LIST" ]; then
                AGENTS_LIST="${AGENTS_LIST},"
            fi
            AGENT_DESC_ESC=$(printf '%s' "$AGENT_DESC" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')
            AGENTS_LIST="${AGENTS_LIST}{\"name\":\"$AGENT_NAME\",\"description\":$AGENT_DESC_ESC}"
            AGENTS_COUNT=$((AGENTS_COUNT + 1))
        fi
    done
    if [ -n "$AGENTS_LIST" ]; then
        AGENTS_JSON="[$AGENTS_LIST]"
    fi
fi

# Build skills list
SKILLS_JSON="[]"
SKILLS_COUNT=0
if [ -d "$BUNDLE_PATH/skills" ]; then
    SKILLS_LIST=""
    for skill_dir in "$BUNDLE_PATH/skills"/*/; do
        if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
            SKILL_NAME=$(basename "$skill_dir")
            SKILL_DESC=$(extract_description "$skill_dir/SKILL.md")
            if [ -n "$SKILLS_LIST" ]; then
                SKILLS_LIST="${SKILLS_LIST},"
            fi
            SKILL_DESC_ESC=$(printf '%s' "$SKILL_DESC" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read().strip()))')
            SKILLS_LIST="${SKILLS_LIST}{\"name\":\"$SKILL_NAME\",\"description\":$SKILL_DESC_ESC}"
            SKILLS_COUNT=$((SKILLS_COUNT + 1))
        fi
    done
    if [ -n "$SKILLS_LIST" ]; then
        SKILLS_JSON="[$SKILLS_LIST]"
    fi
fi

# Generate README content
README_CONTENT="# $BUNDLE_NAME"$'\n\n'

# Commands section
if [ "$COMMANDS_COUNT" -gt 0 ]; then
    README_CONTENT="${README_CONTENT}## Commands"$'\n\n'
    for cmd_file in "$BUNDLE_PATH/commands"/*.md; do
        if [ -f "$cmd_file" ]; then
            CMD_NAME=$(basename "$cmd_file" .md)
            CMD_DESC=$(extract_description "$cmd_file")
            README_CONTENT="${README_CONTENT}- **$CMD_NAME** - $CMD_DESC"$'\n'
        fi
    done
    README_CONTENT="${README_CONTENT}"$'\n'
fi

# Agents section
if [ "$AGENTS_COUNT" -gt 0 ]; then
    README_CONTENT="${README_CONTENT}## Agents"$'\n\n'
    for agent_file in "$BUNDLE_PATH/agents"/*.md; do
        if [ -f "$agent_file" ]; then
            AGENT_NAME=$(basename "$agent_file" .md)
            AGENT_DESC=$(extract_description "$agent_file")
            README_CONTENT="${README_CONTENT}- **$AGENT_NAME** - $AGENT_DESC"$'\n'
        fi
    done
    README_CONTENT="${README_CONTENT}"$'\n'
fi

# Skills section
if [ "$SKILLS_COUNT" -gt 0 ]; then
    README_CONTENT="${README_CONTENT}## Skills"$'\n\n'
    for skill_dir in "$BUNDLE_PATH/skills"/*/; do
        if [ -d "$skill_dir" ] && [ -f "$skill_dir/SKILL.md" ]; then
            SKILL_NAME=$(basename "$skill_dir")
            SKILL_DESC=$(extract_description "$skill_dir/SKILL.md")
            README_CONTENT="${README_CONTENT}- **$SKILL_NAME** - $SKILL_DESC"$'\n'
        fi
    done
    README_CONTENT="${README_CONTENT}"$'\n'
fi

# Installation section
README_CONTENT="${README_CONTENT}## Installation"$'\n\n'
README_CONTENT="${README_CONTENT}Add to your Claude Code settings or install via marketplace."$'\n'

# Escape README content for JSON
README_ESCAPED=$(printf '%s' "$README_CONTENT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')

# Output JSON result
cat <<EOF
{
  "bundle_path": "$BUNDLE_PATH",
  "bundle_name": "$BUNDLE_NAME",
  "readme_generated": true,
  "components": {
    "commands": $COMMANDS_COUNT,
    "agents": $AGENTS_COUNT,
    "skills": $SKILLS_COUNT
  },
  "readme_content": $README_ESCAPED,
  "commands": $COMMANDS_JSON,
  "agents": $AGENTS_JSON,
  "skills": $SKILLS_JSON
}
EOF
