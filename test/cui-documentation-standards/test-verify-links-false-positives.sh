#!/usr/bin/env bash
# Test script for verify-links-false-positives.py

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="marketplace/bundles/cui-documentation-standards/skills/cui-documentation/scripts/verify-links-false-positives.py"
FIXTURES_DIR="$SCRIPT_DIR/fixtures"

echo "Testing verify-links-false-positives.py"
echo "========================================"

# Test 1: Help output
echo "Test 1: --help flag"
python3 "$SCRIPT_PATH" --help > /dev/null
echo "✓ Help flag works"

# Test 2: Process sample input
echo ""
echo "Test 2: Classify broken links"

# Create sample input
cat > "$FIXTURES_DIR/broken-links.json" <<'EOF'
{
  "issues": [
    {
      "file": "standards/security.adoc",
      "line": 42,
      "link": "<<owasp-top-10>>",
      "type": "broken_anchor"
    },
    {
      "file": "standards/security.adoc",
      "line": 89,
      "link": "http://localhost:8080/api",
      "type": "broken_link"
    },
    {
      "file": "requirements/spec.adoc",
      "line": 120,
      "link": "xref:missing-file.adoc[Missing]",
      "type": "broken_file_link"
    },
    {
      "file": "guide.adoc",
      "line": 56,
      "link": "file:///local/path/doc.pdf",
      "type": "broken_link"
    }
  ]
}
EOF

# Run classification
python3 "$SCRIPT_PATH" \
  --input "$FIXTURES_DIR/broken-links.json" \
  --output "$FIXTURES_DIR/classified.json" \
  --pretty

# Verify output exists
if [ -f "$FIXTURES_DIR/classified.json" ]; then
  echo "✓ Classification completed"

  # Check categories exist
  if grep -q "likely-false-positive" "$FIXTURES_DIR/classified.json"; then
    echo "✓ Found likely-false-positive category"
  fi

  if grep -q "must-verify-manual" "$FIXTURES_DIR/classified.json"; then
    echo "✓ Found must-verify-manual category"
  fi
else
  echo "✗ Output file not created"
  exit 1
fi

# Test 3: Stdin/stdout
echo ""
echo "Test 3: Stdin/stdout processing"
cat "$FIXTURES_DIR/broken-links.json" | python3 "$SCRIPT_PATH" --pretty > /dev/null
echo "✓ Stdin/stdout works"

# Cleanup
rm -f "$FIXTURES_DIR/broken-links.json" "$FIXTURES_DIR/classified.json"

echo ""
echo "All tests passed ✓"
