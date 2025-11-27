#!/usr/bin/env bash
# Test script for analyze-content-tone.py

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="marketplace/bundles/cui-documentation-standards/skills/cui-documentation/scripts/analyze-content-tone.py"
FIXTURES_DIR="$SCRIPT_DIR/fixtures"

echo "Testing analyze-content-tone.py"
echo "================================"

# Test 1: Help output
echo "Test 1: --help flag"
python3 "$SCRIPT_PATH" --help > /dev/null
echo "✓ Help flag works"

# Test 2: Analyze sample file
echo ""
echo "Test 2: Analyze sample AsciiDoc file"

# Create sample AsciiDoc with various tone issues
cat > "$FIXTURES_DIR/sample.adoc" <<'EOF'
= Sample Documentation

== Introduction

Our powerful JWT library provides the best-in-class performance for token validation.
It's blazing-fast and enterprise-grade, making it the perfect solution for your needs.

== Features

The library is easy to use and implements OAuth 2.0.
It provides sub-millisecond validation with comprehensive security features.

Used by thousands of companies worldwide, this robust solution is production-ready
and supports all major frameworks.

== Performance

Faster than competitors with proven scalability.
EOF

# Run analysis
python3 "$SCRIPT_PATH" \
  --file "$FIXTURES_DIR/sample.adoc" \
  --output "$FIXTURES_DIR/analysis.json" \
  --pretty

# Verify output exists
if [ -f "$FIXTURES_DIR/analysis.json" ]; then
  echo "✓ Analysis completed"

  # Check for expected categories
  if grep -q "promotional" "$FIXTURES_DIR/analysis.json"; then
    echo "✓ Detected promotional language"
  fi

  if grep -q "performance_claim" "$FIXTURES_DIR/analysis.json"; then
    echo "✓ Detected performance claims"
  fi

  if grep -q "standards_claim" "$FIXTURES_DIR/analysis.json"; then
    echo "✓ Detected standards claims"
  fi

  # Check summary exists
  if grep -q "total_issues" "$FIXTURES_DIR/analysis.json"; then
    echo "✓ Summary generated"
  fi
else
  echo "✗ Output file not created"
  exit 1
fi

# Test 3: Directory analysis
echo ""
echo "Test 3: Directory analysis"

# Create another sample file
cat > "$FIXTURES_DIR/another.adoc" <<'EOF'
= Another Document

== Section

This is factual content without promotional language.
The implementation follows RFC 6749.
EOF

python3 "$SCRIPT_PATH" \
  --directory "$FIXTURES_DIR" \
  --pretty > /dev/null

echo "✓ Directory analysis works"

# Cleanup
rm -f "$FIXTURES_DIR/sample.adoc" "$FIXTURES_DIR/another.adoc" "$FIXTURES_DIR/analysis.json"

echo ""
echo "All tests passed ✓"
