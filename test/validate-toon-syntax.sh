#!/bin/bash
# Validate TOON syntax for all .toon files in test directories

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FAILED=0
PASSED=0

echo "🔍 Validating TOON syntax for all .toon files..."
echo ""

# Find all .toon files
TOON_FILES=$(find "$SCRIPT_DIR" -name "*.toon" -type f)

if [ -z "$TOON_FILES" ]; then
    echo "❌ No .toon files found"
    exit 1
fi

for file in $TOON_FILES; do
    echo "Checking: $(basename "$file")"

    # Basic syntax validation
    ERRORS=""

    # Check 1: File not empty
    if [ ! -s "$file" ]; then
        ERRORS="${ERRORS}  - File is empty\n"
    fi

    # Check 2: Array declarations have matching row counts
    # Extract array declarations like: issues[5]{...}:
    ARRAY_DECLS=$(grep -E '^[a-z_]+\[[0-9]+\]\{' "$file" || true)

    if [ -n "$ARRAY_DECLS" ]; then
        while IFS= read -r decl; do
            # Extract array name and declared count
            ARRAY_NAME=$(echo "$decl" | sed -E 's/^([a-z_]+)\[([0-9]+)\].*/\1/')
            DECLARED_COUNT=$(echo "$decl" | sed -E 's/^[a-z_]+\[([0-9]+)\].*/\1/')

            # Count actual rows (lines between array declaration and next empty line or EOF)
            # This is a simplified check - actual rows start after the declaration line
            ACTUAL_COUNT=$(awk "/$ARRAY_NAME\[/,/^$|^[a-z_]+:/" "$file" | grep -v "$ARRAY_NAME\[" | grep -v "^$" | grep -v "^[a-z_]*:" | wc -l | tr -d ' ')

            if [ "$DECLARED_COUNT" != "$ACTUAL_COUNT" ]; then
                ERRORS="${ERRORS}  - Array '$ARRAY_NAME': declared $DECLARED_COUNT rows, found $ACTUAL_COUNT rows\n"
            fi
        done <<< "$ARRAY_DECLS"
    fi

    # Check 3: No tabs (TOON should use spaces)
    TABS=$(grep $'\t' "$file" || true)
    if [ -n "$TABS" ]; then
        ERRORS="${ERRORS}  - Tabs detected (TOON should use spaces only)\n"
    fi

    if [ -n "$ERRORS" ]; then
        echo "  ❌ FAILED"
        echo -e "$ERRORS"
        FAILED=$((FAILED + 1))
    else
        echo "  ✅ PASSED"
        PASSED=$((PASSED + 1))
    fi
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Results:"
echo "  ✅ Passed: $PASSED"
echo "  ❌ Failed: $FAILED"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $FAILED -gt 0 ]; then
    exit 1
fi

echo "✨ All TOON files have valid syntax"
exit 0
