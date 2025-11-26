#!/bin/bash
# Scans a skill directory and returns structured inventory of all content files
# Usage: scan-skill-inventory.sh --skill-path <path> [--include-hidden]
# Output: JSON with complete file inventory

set -euo pipefail

# --help support
if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
    cat <<EOF
Usage: $(basename "$0") --skill-path <path> [--include-hidden]

Scans a skill directory and returns structured inventory of all content files.

Arguments:
  --skill-path <path>    Path to the skill directory (required)
  --include-hidden       Include hidden files (default: false)

Output: JSON with inventory including:
  - skill_name: Name of the skill (from directory name)
  - skill_path: Absolute path to skill directory
  - directories: Array of subdirectories with their files
  - root_files: Files in the root of the skill directory
  - statistics: Aggregate counts and metrics

Exit codes:
  0 - Success
  1 - Error (missing argument, directory not found)

Examples:
  $(basename "$0") --skill-path marketplace/bundles/cui-documentation-standards/skills/cui-documentation
  $(basename "$0") --skill-path ./skills/my-skill --include-hidden
EOF
    exit 0
fi

# Parse arguments
SKILL_PATH=""
INCLUDE_HIDDEN="false"

while [[ $# -gt 0 ]]; do
    case $1 in
        --skill-path)
            SKILL_PATH="$2"
            shift 2
            ;;
        --include-hidden)
            INCLUDE_HIDDEN="true"
            shift
            ;;
        *)
            echo "{\"error\": \"Unknown argument: $1. Use --help for usage.\"}" >&2
            exit 1
            ;;
    esac
done

if [ -z "$SKILL_PATH" ]; then
    echo '{"error": "Skill path required. Use --skill-path <path>."}' >&2
    exit 1
fi

if [ ! -d "$SKILL_PATH" ]; then
    echo "{\"error\": \"Directory not found: $SKILL_PATH\"}" >&2
    exit 1
fi

# Get absolute path
SKILL_PATH=$(cd "$SKILL_PATH" && pwd)

# Extract skill name from path
SKILL_NAME=$(basename "$SKILL_PATH")

# Function to count lines in a file
count_lines() {
    wc -l < "$1" | tr -d ' '
}

# Function to get file size (macOS and Linux compatible)
get_size() {
    if stat -f%z "$1" 2>/dev/null; then
        return
    fi
    stat -c%s "$1" 2>/dev/null || echo "0"
}

# Temporary file for extension counting
EXT_TEMP=$(mktemp)
trap "rm -f $EXT_TEMP" EXIT

# Build JSON output
echo "{"
echo "  \"skill_name\": \"$SKILL_NAME\","
echo "  \"skill_path\": \"$SKILL_PATH\","

# Initialize counters
TOTAL_DIRS=0
TOTAL_FILES=0
TOTAL_LINES=0

# Collect directories
echo "  \"directories\": ["

FIRST_DIR="true"
for dir in "$SKILL_PATH"/*/; do
    [ -d "$dir" ] || continue

    DIR_NAME=$(basename "$dir")

    # Skip hidden directories unless requested
    if [ "$INCLUDE_HIDDEN" = "false" ] && [[ "$DIR_NAME" == .* ]]; then
        continue
    fi

    # Skip common non-content directories
    if [[ "$DIR_NAME" == "__pycache__" ]] || [[ "$DIR_NAME" == "node_modules" ]] || [[ "$DIR_NAME" == ".git" ]]; then
        continue
    fi

    TOTAL_DIRS=$((TOTAL_DIRS + 1))

    if [ "$FIRST_DIR" = "false" ]; then
        echo ","
    fi
    FIRST_DIR="false"

    echo "    {"
    echo "      \"name\": \"$DIR_NAME\","
    echo "      \"path\": \"$DIR_NAME/\","
    echo "      \"files\": ["

    FIRST_FILE="true"

    # Find files in directory (non-recursive for first level)
    for file in "$dir"*; do
        [ -f "$file" ] || continue

        FILE_NAME=$(basename "$file")

        # Skip hidden files unless requested
        if [ "$INCLUDE_HIDDEN" = "false" ] && [[ "$FILE_NAME" == .* ]]; then
            continue
        fi

        TOTAL_FILES=$((TOTAL_FILES + 1))

        # Count lines
        LINES=$(count_lines "$file")
        TOTAL_LINES=$((TOTAL_LINES + LINES))

        # Get size
        SIZE=$(get_size "$file")

        # Track extension
        EXT="${FILE_NAME##*.}"
        if [ "$EXT" != "$FILE_NAME" ]; then
            echo ".$EXT" >> "$EXT_TEMP"
        fi

        # Get relative path from skill root
        REL_PATH="${file#$SKILL_PATH/}"

        if [ "$FIRST_FILE" = "false" ]; then
            echo ","
        fi
        FIRST_FILE="false"

        printf '        {"name": "%s", "path": "%s", "lines": %d, "size_bytes": %d}' \
            "$FILE_NAME" "$REL_PATH" "$LINES" "$SIZE"
    done

    echo ""
    echo "      ]"
    printf "    }"
done

echo ""
echo "  ],"

# Collect root files
echo "  \"root_files\": ["

FIRST_ROOT="true"
for file in "$SKILL_PATH"/*; do
    [ -f "$file" ] || continue

    FILE_NAME=$(basename "$file")

    # Skip hidden files unless requested
    if [ "$INCLUDE_HIDDEN" = "false" ] && [[ "$FILE_NAME" == .* ]]; then
        continue
    fi

    TOTAL_FILES=$((TOTAL_FILES + 1))

    # Count lines
    LINES=$(count_lines "$file")
    TOTAL_LINES=$((TOTAL_LINES + LINES))

    # Get size
    SIZE=$(get_size "$file")

    # Track extension
    EXT="${FILE_NAME##*.}"
    if [ "$EXT" != "$FILE_NAME" ]; then
        echo ".$EXT" >> "$EXT_TEMP"
    fi

    if [ "$FIRST_ROOT" = "false" ]; then
        echo ","
    fi
    FIRST_ROOT="false"

    printf '    {"name": "%s", "path": "%s", "lines": %d, "size_bytes": %d}' \
        "$FILE_NAME" "$FILE_NAME" "$LINES" "$SIZE"
done

echo ""
echo "  ],"

# Statistics
echo "  \"statistics\": {"
echo "    \"total_directories\": $TOTAL_DIRS,"
echo "    \"total_files\": $TOTAL_FILES,"
echo "    \"total_lines\": $TOTAL_LINES,"
echo "    \"by_extension\": {"

# Count extensions from temp file
FIRST_EXT="true"
if [ -s "$EXT_TEMP" ]; then
    sort "$EXT_TEMP" | uniq -c | while read count ext; do
        if [ "$FIRST_EXT" = "false" ]; then
            printf ",\n"
        fi
        FIRST_EXT="false"
        printf '      "%s": %d' "$ext" "$count"
    done
fi

echo ""
echo "    }"
echo "  }"
echo "}"
