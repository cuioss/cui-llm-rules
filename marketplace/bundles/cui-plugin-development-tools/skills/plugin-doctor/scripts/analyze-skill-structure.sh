#!/bin/bash
# Analyzes skill directory structure and file references
# Usage: analyze-skill-structure.sh <skill_dir>
# Output: JSON with structure analysis

set -euo pipefail

# --help support
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    cat <<EOF
Usage: $(basename "$0") <skill_dir>

Analyzes skill directory structure and validates file references.

Arguments:
  skill_dir    Path to the skill directory containing SKILL.md

Output: JSON with structure analysis including:
  - skill_md.exists: Whether SKILL.md exists
  - skill_md.yaml_valid: Whether frontmatter is valid YAML
  - standards_files.missing_files: Files referenced but not found
  - standards_files.unreferenced_files: Files existing but not referenced
  - structure_score: Quality score 0-100

Exit codes:
  0 - Success
  1 - Error (missing argument, directory not found)

Examples:
  $(basename "$0") marketplace/bundles/cui-java-expert/skills/cui-java-core
  $(basename "$0") ./skills/my-skill
EOF
    exit 0
fi

SKILL_DIR="${1:-}"

if [ -z "$SKILL_DIR" ]; then
    echo '{"error": "Skill directory required. Use --help for usage."}' >&2
    exit 1
fi

if [ ! -d "$SKILL_DIR" ]; then
    echo "{\"error\": \"Directory not found: $SKILL_DIR\"}" >&2
    exit 1
fi

SKILL_MD="$SKILL_DIR/SKILL.md"

# Check SKILL.md existence
SKILL_EXISTS="false"
YAML_VALID="false"

if [ -f "$SKILL_MD" ]; then
    SKILL_EXISTS="true"

    # Check YAML frontmatter validity
    if head -1 "$SKILL_MD" | grep -q "^---$"; then
        FRONTMATTER=$(awk '/^---$/{if(++count==2) exit; if(count==1) next} count==1' "$SKILL_MD")

        # Basic YAML validity check
        if echo "$FRONTMATTER" | grep -q "^[a-z_]*:"; then
            YAML_VALID="true"
        fi
    fi
fi

# Extract file references from SKILL.md
REFERENCED_FILES=""
MISSING_FILES=""
UNREFERENCED_FILES=""

if [ "$SKILL_EXISTS" = "true" ]; then
    # Find file references in SKILL.md
    # Pattern: Direct relative paths like scripts/*.sh, references/*.md, assets/*.*
    # Note: Skills use relative paths from their directory (the old placeholder pattern is deprecated)

    CONTENT=$(cat "$SKILL_MD")

    # Step 1: Extract ALL potential file references from the FULL content
    # We'll filter later based on whether files actually exist
    # Support nested paths like references/examples/file.md
    # First extract all potential references, including those in code blocks
    ALL_REFS=$(echo "$CONTENT" | \
        grep -oE '([a-zA-Z0-9_-]+:)?(scripts|references|assets)(/[a-zA-Z0-9_.-]+)+\.[a-z]+' || echo "")

    # Filter out cross-skill references (those with prefix like bundle-name:references/)
    # Keep only local references (no colon prefix)
    LOCAL_REFS=$(echo "$ALL_REFS" | \
        grep -v '^[a-zA-Z0-9_-]*:' | \
        sort -u || echo "")

    # Step 2: For "missing files" detection, also extract refs from content WITHOUT code blocks
    # This helps identify example paths in code blocks that shouldn't be flagged as missing
    CONTENT_NO_CODEBLOCKS=$(echo "$CONTENT" | awk '
        /^```/ { in_codeblock = !in_codeblock; next }
        !in_codeblock { print }
    ')

    REFS_OUTSIDE_CODEBLOCKS=$(echo "$CONTENT_NO_CODEBLOCKS" | \
        grep -oE '(scripts|references|assets)(/[a-zA-Z0-9_.-]+)+\.[a-z]+' | \
        sort -u || echo "")

    # REFERENCED_FILES = all local refs (both inside and outside code blocks)
    # This is used for "unreferenced files" detection (files that exist but aren't mentioned)
    REFERENCED_FILES="$LOCAL_REFS"

    # Step 3: Also detect table-format references like | `script.py` |
    # These are common in External Resources tables
    # Support nested paths like `references/examples/file.md`
    TABLE_REFS=$(echo "$CONTENT_NO_CODEBLOCKS" | \
        grep -oE '\`(scripts|references|assets)(/[a-zA-Z0-9_.-]+)+\.[a-z]+\`' | \
        sed 's/`//g' | \
        sort -u || echo "")

    # Also detect backtick references like `analyze-data.sh` in tables (filename only)
    # Match against scripts/references/assets directories
    FILENAME_REFS=""
    for subdir in "scripts" "references" "assets"; do
        SUBDIR_PATH="$SKILL_DIR/$subdir"
        if [ -d "$SUBDIR_PATH" ]; then
            while IFS= read -r filepath; do
                if [ -z "$filepath" ] || [ ! -f "$filepath" ]; then
                    continue
                fi
                FILENAME=$(basename "$filepath")
                # Check if this filename appears in backticks in the content
                if echo "$CONTENT_NO_CODEBLOCKS" | grep -q "\`$FILENAME\`"; then
                    RELATIVE_PATH="${filepath#$SKILL_DIR/}"
                    FILENAME_REFS="${FILENAME_REFS}${RELATIVE_PATH}"$'\n'
                fi
            done <<< "$(find "$SUBDIR_PATH" -type f 2>/dev/null || echo "")"
        fi
    done

    # Combine all reference types
    REFERENCED_FILES=$(printf "%s\n%s\n%s" "$REFERENCED_FILES" "$TABLE_REFS" "$FILENAME_REFS" | grep -v '^$' | sort -u || echo "")

    # Check for missing files - only flag as missing if:
    # 1. Referenced OUTSIDE code blocks (real references, not examples)
    # 2. File doesn't exist
    # Files referenced only inside code blocks are examples and shouldn't be flagged
    while IFS= read -r ref; do
        if [ -z "$ref" ]; then
            continue
        fi

        FILE_PATH="$SKILL_DIR/$ref"
        if [ ! -f "$FILE_PATH" ]; then
            # Only flag as missing if referenced outside code blocks
            if echo "$REFS_OUTSIDE_CODEBLOCKS" | grep -qF "$ref"; then
                MISSING_FILES="${MISSING_FILES}${ref}"$'\n'
            fi
        fi
    done <<< "$REFERENCED_FILES"

    # Find unreferenced files (files that exist but aren't referenced)
    # Check scripts/, references/, and assets/ directories
    for subdir in "scripts" "references" "assets"; do
        SUBDIR_PATH="$SKILL_DIR/$subdir"
        if [ -d "$SUBDIR_PATH" ]; then
            # Find all files in subdirectory
            while IFS= read -r filepath; do
                if [ -z "$filepath" ] || [ ! -f "$filepath" ]; then
                    continue
                fi

                # Get relative path from skill directory
                RELATIVE_PATH="${filepath#$SKILL_DIR/}"

                # Check if this file is referenced
                if ! echo "$REFERENCED_FILES" | grep -qF "$RELATIVE_PATH"; then
                    UNREFERENCED_FILES="${UNREFERENCED_FILES}${RELATIVE_PATH}"$'\n'
                fi
            done <<< "$(find "$SUBDIR_PATH" -type f 2>/dev/null || echo "")"
        fi
    done
fi

# Count issues (count actual newlines)
if [ -z "$MISSING_FILES" ]; then
    MISSING_COUNT=0
else
    MISSING_COUNT=$(printf "%s" "$MISSING_FILES" | wc -l | tr -d ' ')
fi

if [ -z "$UNREFERENCED_FILES" ]; then
    UNREFERENCED_COUNT=0
else
    UNREFERENCED_COUNT=$(printf "%s" "$UNREFERENCED_FILES" | wc -l | tr -d ' ')
fi

# Calculate structure score
STRUCTURE_SCORE=0

if [ "$SKILL_EXISTS" = "false" ]; then
    # No SKILL.md = score 0
    STRUCTURE_SCORE=0
elif [ "$YAML_VALID" = "false" ]; then
    # Invalid YAML = score 30
    STRUCTURE_SCORE=30
elif [ "$MISSING_COUNT" -eq 0 ] && [ "$UNREFERENCED_COUNT" -eq 0 ]; then
    # Perfect structure = score 100
    STRUCTURE_SCORE=100
else
    # Start at 100 and deduct points
    SCORE=100

    # Deduct 20 points per missing file (referenced but doesn't exist)
    SCORE=$((SCORE - (MISSING_COUNT * 20)))

    # Deduct 10 points per unreferenced file (exists but not referenced)
    SCORE=$((SCORE - (UNREFERENCED_COUNT * 10)))

    # Minimum score is 0
    if [ $SCORE -lt 0 ]; then
        SCORE=0
    fi

    STRUCTURE_SCORE=$SCORE
fi

# Build JSON arrays (use printf to avoid echo's trailing newline)
MISSING_FILES_JSON=""
if [ -n "$MISSING_FILES" ]; then
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            MISSING_FILES_JSON="${MISSING_FILES_JSON}    $(printf "%s" "$file" | jq -Rs .),"
        fi
    done <<< "$MISSING_FILES"
    # Remove trailing comma
    MISSING_FILES_JSON="${MISSING_FILES_JSON%,}"
fi

UNREFERENCED_FILES_JSON=""
if [ -n "$UNREFERENCED_FILES" ]; then
    while IFS= read -r file; do
        if [ -n "$file" ]; then
            UNREFERENCED_FILES_JSON="${UNREFERENCED_FILES_JSON}    $(printf "%s" "$file" | jq -Rs .),"
        fi
    done <<< "$UNREFERENCED_FILES"
    # Remove trailing comma
    UNREFERENCED_FILES_JSON="${UNREFERENCED_FILES_JSON%,}"
fi

# Output JSON
cat <<EOF
{
  "skill_dir": "$SKILL_DIR",
  "skill_md": {
    "exists": $SKILL_EXISTS,
    "yaml_valid": $YAML_VALID
  },
  "standards_files": {
    "missing_files": [
${MISSING_FILES_JSON}
    ],
    "unreferenced_files": [
${UNREFERENCED_FILES_JSON}
    ]
  },
  "structure_score": $STRUCTURE_SCORE
}
EOF
