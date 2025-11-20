#!/bin/bash
# analyze-skill-structure.sh
#
# Purpose: Validate skill directory structure and standards files
# Usage: ./analyze-skill-structure.sh <skill_directory>
#
# Returns JSON with:
# - SKILL.md validation status
# - Standards files inventory
# - Missing/unreferenced file detection
# - Structure quality score

set -euo pipefail

# ============================================================================
# USAGE AND HELP
# ============================================================================

usage() {
    cat <<EOF
Usage: $(basename "$0") <skill_directory>

Analyzes skill directory structure and validates standards files.

Arguments:
  skill_directory    Path to skill directory (e.g., marketplace/bundles/cui-java-expert/skills/cui-java-core)

Output:
  JSON object with skill structure analysis

Examples:
  $(basename "$0") marketplace/bundles/cui-java-expert/skills/cui-java-core
  $(basename "$0") ~/.claude/skills/my-skill

Exit codes:
  0 - Success (JSON output)
  1 - Error (invalid parameters, missing directory)
EOF
    exit 0
}

# Show usage if no arguments or help requested
if [ $# -eq 0 ] || [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    usage
fi

# ============================================================================
# INPUT VALIDATION
# ============================================================================

SKILL_DIR="${1:-}"

if [ -z "$SKILL_DIR" ]; then
    echo "ERROR: skill_directory parameter required" >&2
    exit 1
fi

if [ ! -d "$SKILL_DIR" ]; then
    echo "ERROR: Directory not found: $SKILL_DIR" >&2
    exit 1
fi

# Normalize path (remove trailing slash)
SKILL_DIR="${SKILL_DIR%/}"

# ============================================================================
# SKILL.md VALIDATION
# ============================================================================

SKILL_MD_PATH="$SKILL_DIR/SKILL.md"
SKILL_MD_EXISTS=false
YAML_VALID=false
SKILL_NAME=""
HAS_NAME_FIELD=false
HAS_DESCRIPTION_FIELD=false
HAS_ALLOWED_TOOLS_FIELD=false
YAML_ERRORS=()

if [ -f "$SKILL_MD_PATH" ]; then
    SKILL_MD_EXISTS=true

    # Extract frontmatter
    if grep -q "^---$" "$SKILL_MD_PATH"; then
        FRONTMATTER=$(sed -n '/^---$/,/^---$/p' "$SKILL_MD_PATH" | sed '1d;$d')

        if [ -n "$FRONTMATTER" ]; then
            YAML_VALID=true

            # Parse name field
            if echo "$FRONTMATTER" | grep -q "^name:"; then
                SKILL_NAME=$(echo "$FRONTMATTER" | grep "^name:" | sed 's/^name:[[:space:]]*//')
                HAS_NAME_FIELD=true
            else
                YAML_ERRORS+=("Missing required field: name")
            fi

            # Parse description field
            if echo "$FRONTMATTER" | grep -q "^description:"; then
                HAS_DESCRIPTION_FIELD=true
            else
                YAML_ERRORS+=("Missing required field: description")
            fi

            # Check for allowed-tools field
            if echo "$FRONTMATTER" | grep -q "^allowed-tools:"; then
                HAS_ALLOWED_TOOLS_FIELD=true
            fi

            # Check for wrong field name
            if echo "$FRONTMATTER" | grep -q "^tools:"; then
                YAML_ERRORS+=("Wrong field name: 'tools' should be 'allowed-tools'")
            fi
        else
            YAML_VALID=false
            YAML_ERRORS+=("Empty YAML frontmatter")
        fi
    else
        YAML_VALID=false
        YAML_ERRORS+=("No YAML frontmatter found")
    fi
fi

# ============================================================================
# STANDARDS FILES DISCOVERY
# ============================================================================

STANDARDS_DIR="$SKILL_DIR/standards"
STANDARDS_FILES=()
STANDARDS_COUNT=0

if [ -d "$STANDARDS_DIR" ]; then
    # Find all .md files in standards directory
    while IFS= read -r -d '' file; do
        # Get basename (file name without path)
        basename=$(basename "$file")
        STANDARDS_FILES+=("$basename")
        STANDARDS_COUNT=$((STANDARDS_COUNT + 1))
    done < <(find "$STANDARDS_DIR" -maxdepth 1 -name "*.md" -type f -print0 2>/dev/null)

    # Sort array
    if [ "$STANDARDS_COUNT" -gt 0 ]; then
        IFS=$'\n' STANDARDS_FILES=($(sort <<<"${STANDARDS_FILES[*]}"))
        unset IFS
    fi
fi

# ============================================================================
# EXTRACT STANDARDS REFERENCES FROM SKILL.MD
# ============================================================================

REFERENCED_FILES=()
REFERENCED_COUNT=0

if [ "$SKILL_MD_EXISTS" = true ]; then
    # Extract lines with "Read: standards/" pattern
    while IFS= read -r line; do
        # Extract file name from patterns like "Read: standards/file.md"
        if [[ "$line" =~ standards/([^[:space:]]+\.md) ]]; then
            filename="${BASH_REMATCH[1]}"
            REFERENCED_FILES+=("$filename")
            REFERENCED_COUNT=$((REFERENCED_COUNT + 1))
        fi
    done < <(grep -i "standards/" "$SKILL_MD_PATH" 2>/dev/null || true)

    # Sort and deduplicate
    if [ "$REFERENCED_COUNT" -gt 0 ]; then
        IFS=$'\n' REFERENCED_FILES=($(printf '%s\n' "${REFERENCED_FILES[@]}" | sort -u))
        unset IFS
        REFERENCED_COUNT=${#REFERENCED_FILES[@]}
    fi
fi

# ============================================================================
# COMPARE REFERENCED VS ACTUAL FILES
# ============================================================================

# Missing files (referenced but don't exist)
MISSING_FILES=()
if [ "$REFERENCED_COUNT" -gt 0 ]; then
    for ref_file in "${REFERENCED_FILES[@]}"; do
        found=false
        if [ "$STANDARDS_COUNT" -gt 0 ]; then
            for actual_file in "${STANDARDS_FILES[@]}"; do
                if [ "$ref_file" = "$actual_file" ]; then
                    found=true
                    break
                fi
            done
        fi
        if [ "$found" = false ]; then
            MISSING_FILES+=("$ref_file")
        fi
    done
fi

# Unreferenced files (exist but not referenced in SKILL.md)
UNREFERENCED_FILES=()
if [ "$STANDARDS_COUNT" -gt 0 ]; then
    for actual_file in "${STANDARDS_FILES[@]}"; do
        found=false
        if [ "$REFERENCED_COUNT" -gt 0 ]; then
            for ref_file in "${REFERENCED_FILES[@]}"; do
                if [ "$actual_file" = "$ref_file" ]; then
                    found=true
                    break
                fi
            done
        fi
        if [ "$found" = false ]; then
            UNREFERENCED_FILES+=("$actual_file")
        fi
    done
fi

# ============================================================================
# CALCULATE STRUCTURE SCORE
# ============================================================================

# Score calculation:
# - SKILL.md exists: +30 points
# - Valid YAML: +20 points
# - All required fields present: +10 points
# - No missing files: +20 points
# - No unreferenced files: +20 points

STRUCTURE_SCORE=0

if [ "$SKILL_MD_EXISTS" = true ]; then
    STRUCTURE_SCORE=$((STRUCTURE_SCORE + 30))
fi

if [ "$YAML_VALID" = true ]; then
    STRUCTURE_SCORE=$((STRUCTURE_SCORE + 20))
fi

if [ "$HAS_NAME_FIELD" = true ] && [ "$HAS_DESCRIPTION_FIELD" = true ]; then
    STRUCTURE_SCORE=$((STRUCTURE_SCORE + 10))
fi

if [ "${#MISSING_FILES[@]}" -eq 0 ] && [ "$REFERENCED_COUNT" -gt 0 ]; then
    STRUCTURE_SCORE=$((STRUCTURE_SCORE + 20))
fi

if [ "${#UNREFERENCED_FILES[@]}" -eq 0 ] && [ "$STANDARDS_COUNT" -gt 0 ]; then
    STRUCTURE_SCORE=$((STRUCTURE_SCORE + 20))
fi

# ============================================================================
# JSON ESCAPING HELPER
# ============================================================================

json_escape() {
    local string="$1"
    # Escape backslashes, double quotes, and control characters
    string="${string//\\/\\\\}"
    string="${string//\"/\\\"}"
    string="${string//$'\n'/\\n}"
    string="${string//$'\r'/\\r}"
    string="${string//$'\t'/\\t}"
    echo "$string"
}

# ============================================================================
# BUILD JSON ARRAYS
# ============================================================================

build_json_array() {
    local array_name="$1"
    local count
    eval "count=\${#${array_name}[@]}"

    if [ "$count" -eq 0 ]; then
        echo "[]"
        return
    fi

    # Copy array to temporary array for safe iteration
    local -a temp_array
    eval "temp_array=(\"\${${array_name}[@]}\")"

    local json="["
    local first=true
    local item
    local escaped_item

    for item in "${temp_array[@]}"; do
        escaped_item=$(json_escape "$item")
        if [ "$first" = true ]; then
            json="${json}\"${escaped_item}\""
            first=false
        else
            json="${json}, \"${escaped_item}\""
        fi
    done

    json="${json}]"
    echo "$json"
}

# ============================================================================
# OUTPUT JSON
# ============================================================================

# Build arrays
STANDARDS_FILES_JSON=$(build_json_array "STANDARDS_FILES")
REFERENCED_FILES_JSON=$(build_json_array "REFERENCED_FILES")
MISSING_FILES_JSON=$(build_json_array "MISSING_FILES")
UNREFERENCED_FILES_JSON=$(build_json_array "UNREFERENCED_FILES")
YAML_ERRORS_JSON=$(build_json_array "YAML_ERRORS")

# Escape string fields
SKILL_NAME_ESC=$(json_escape "$SKILL_NAME")

# Build JSON output
cat <<EOF
{
  "skill_md": {
    "exists": $SKILL_MD_EXISTS,
    "yaml_valid": $YAML_VALID,
    "name": "$SKILL_NAME_ESC",
    "has_name_field": $HAS_NAME_FIELD,
    "has_description_field": $HAS_DESCRIPTION_FIELD,
    "has_allowed_tools_field": $HAS_ALLOWED_TOOLS_FIELD,
    "yaml_errors": $YAML_ERRORS_JSON
  },
  "standards_files": {
    "total_files": $STANDARDS_COUNT,
    "files": $STANDARDS_FILES_JSON,
    "referenced_count": $REFERENCED_COUNT,
    "referenced_in_skill": $REFERENCED_FILES_JSON,
    "missing_files": $MISSING_FILES_JSON,
    "unreferenced_files": $UNREFERENCED_FILES_JSON
  },
  "structure_score": $STRUCTURE_SCORE
}
EOF
