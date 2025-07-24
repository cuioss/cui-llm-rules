#!/bin/bash

# AsciiDoc Validator - Comprehensive validation tool for AsciiDoc documents
# Compatible with bash 3.2+ (macOS default)

# Exit codes
EXIT_SUCCESS=0
EXIT_NON_COMPLIANT=1
EXIT_ERROR=2

# Default values
check_dir="standards"
output_format="console"
verbose=false
quiet=false
severity_level="all"
ignore_patterns=("asciidoc-standards.adoc")

# Color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Statistics
total_files=0
total_errors=0
total_warnings=0
total_info=0
non_compliant_files=0

# Temporary file for storing results
results_file=$(mktemp /tmp/asciidoc-validator.XXXXXX)
trap "rm -f $results_file" EXIT

# Display usage information
usage() {
  echo "Usage: $0 [OPTIONS] [directory]"
  echo ""
  echo "Validate AsciiDoc files for compliance with project standards."
  echo ""
  echo "Arguments:"
  echo "  directory              Directory to check (default: standards)"
  echo ""
  echo "Options:"
  echo "  -f, --format FORMAT    Output format: console, json (default: console)"
  echo "  -v, --verbose          Show detailed output for all files"
  echo "  -q, --quiet            Show only errors (no success messages)"
  echo "  -i, --ignore PATTERN   Add ignore pattern (can be used multiple times)"
  echo "  -s, --severity LEVEL   Minimum severity: error, warning, all (default: all)"
  echo "  -h, --help             Show this help message"
  echo ""
  echo "Checks performed:"
  echo "  - Required header attributes"
  echo "  - List formatting (blank lines)"
  echo "  - Cross-reference syntax"
  echo ""
  echo "Exit codes:"
  echo "  0 - All files compliant"
  echo "  1 - Non-compliant files found"
  echo "  2 - Error occurred"
  echo ""
  echo "Examples:"
  echo "  $0                                    # Check standards directory"
  echo "  $0 -f json docs                       # JSON output for docs directory"
  echo "  $0 -q -i 'temp*.adoc' standards       # Quiet mode, ignore temp files"
  exit $EXIT_ERROR
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -f|--format)
      output_format="$2"
      if [[ ! "$output_format" =~ ^(console|json)$ ]]; then
        echo "Error: Invalid format '$output_format'. Use 'console' or 'json'."
        exit $EXIT_ERROR
      fi
      shift 2
      ;;
    -v|--verbose)
      verbose=true
      shift
      ;;
    -q|--quiet)
      quiet=true
      shift
      ;;
    -i|--ignore)
      ignore_patterns+=("$2")
      shift 2
      ;;
    -s|--severity)
      severity_level="$2"
      if [[ ! "$severity_level" =~ ^(error|warning|all)$ ]]; then
        echo "Error: Invalid severity '$severity_level'. Use 'error', 'warning', or 'all'."
        exit $EXIT_ERROR
      fi
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    -*)
      echo "Error: Unknown option $1"
      usage
      ;;
    *)
      check_dir="$1"
      shift
      ;;
  esac
done

# Validate that the directory exists
if [ ! -d "$check_dir" ]; then
  if [ "$output_format" = "json" ]; then
    echo '{"error": "Directory not found", "directory": "'"$check_dir"'"}'
  else
    echo "Error: Directory '$check_dir' does not exist."
  fi
  exit $EXIT_ERROR
fi

# Required header attributes
required_attrs=(
  "= "
  ":toc: left"
  ":toclevels: 3"
  ":toc-title: Table of Contents"
  ":sectnums:"
  ":source-highlighter: highlight.js"
)

# Function to check a single file
check_file() {
  local file="$1"
  local file_has_issues=false
  local file_errors=0
  local file_warnings=0
  
  # Check for required header attributes
  local missing_attrs=""
  for attr in "${required_attrs[@]}"; do
    if ! grep -q "$attr" "$file"; then
      missing_attrs="${missing_attrs}${attr}|"
      file_has_issues=true
      ((file_errors++))
    fi
  done
  
  # Check for list formatting issues
  local list_issues=$(awk '
    function count_spaces(line) {
      match(line, /^[[:space:]]*/)
      return RLENGTH
    }
    
    /^[[:space:]]*\* / && !/^[[:space:]]*\*\*/ && prev !~ /^[[:space:]]*$/ && prev !~ /^[[:space:]]*\* / && prev !~ /^[[:space:]]*[0-9]+\. / {
      current_spaces = count_spaces($0)
      prev_spaces = count_spaces(prev)
      if (current_spaces <= prev_spaces) {
        print NR ":unordered:" substr(prev, 1, 50)
      }
    }
    /^[[:space:]]*[0-9]+\. / && prev !~ /^[[:space:]]*$/ && prev !~ /^[[:space:]]*[0-9]+\. / {
      print NR ":ordered:" substr(prev, 1, 50)
    }
    /^[[:space:]]*[^:]+::/ && prev !~ /^[[:space:]]*$/ && prev !~ /^[[:space:]]*[^:]+::/ {
      print NR ":definition:" substr(prev, 1, 50)
    }
    {prev=$0}
  ' "$file")
  
  if [ -n "$list_issues" ]; then
    file_has_issues=true
    file_warnings=$(echo "$list_issues" | wc -l | tr -d ' ')
  fi
  
  # Check for cross-reference syntax issues
  local xref_count=$(grep -c "<<.*\.adoc.*>>" "$file" 2>/dev/null || echo 0)
  if [ "$xref_count" -gt 0 ]; then
    file_has_issues=true
    ((file_warnings += xref_count))
  fi
  
  # Store results
  if [ "$file_has_issues" = true ]; then
    echo "$file|$file_errors|$file_warnings|$missing_attrs|$list_issues|$xref_count" >> "$results_file"
    ((non_compliant_files++))
    ((total_errors += file_errors))
    ((total_warnings += file_warnings))
  elif [ "$verbose" = true ]; then
    echo "$file|0|0|||" >> "$results_file"
  fi
}

# Main processing
if [ "$output_format" = "console" ] && [ "$quiet" = false ]; then
  echo "Checking .adoc files in '$check_dir' for compliance with AsciiDoc standards..."
  echo ""
fi

# Build find command with ignore patterns
find_cmd="find \"$check_dir\" -name \"*.adoc\""
for pattern in "${ignore_patterns[@]}"; do
  find_cmd="$find_cmd | grep -v \"$pattern\""
done

# Process files
eval $find_cmd | sort | while read -r file; do
  ((total_files++))
  check_file "$file"
done

# Read back total counts (since we're in a subshell)
if [ -f "$results_file" ]; then
  total_files=$(eval $find_cmd | wc -l | tr -d ' ')
  non_compliant_files=$(wc -l < "$results_file" | tr -d ' ')
  
  # Count errors and warnings
  total_errors=0
  total_warnings=0
  while IFS='|' read -r file errors warnings rest; do
    ((total_errors += errors))
    ((total_warnings += warnings))
  done < "$results_file"
fi

# Output results
if [ "$output_format" = "json" ]; then
  # JSON output
  echo "{"
  echo "  \"directory\": \"$check_dir\","
  echo "  \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\","
  echo "  \"summary\": {"
  echo "    \"total_files\": $total_files,"
  echo "    \"non_compliant_files\": $non_compliant_files,"
  echo "    \"compliant_files\": $((total_files - non_compliant_files)),"
  echo "    \"total_errors\": $total_errors,"
  echo "    \"total_warnings\": $total_warnings"
  echo "  },"
  echo "  \"files\": ["
  
  first_file=true
  while IFS='|' read -r file errors warnings missing_attrs list_issues xref_count; do
    [ "$first_file" = false ] && echo ","
    first_file=false
    
    echo -n "    {"
    echo -n "\"file\": \"$file\", "
    echo -n "\"compliant\": false, "
    echo -n "\"errors\": $errors, "
    echo -n "\"warnings\": $warnings"
    
    # Add issues details
    echo -n ", \"issues\": ["
    
    first_issue=true
    
    # Missing attributes
    if [ -n "$missing_attrs" ]; then
      IFS='|' read -ra attrs <<< "$missing_attrs"
      for attr in "${attrs[@]}"; do
        [ -z "$attr" ] && continue
        [ "$first_issue" = false ] && echo -n ", "
        first_issue=false
        echo -n "{\"type\": \"missing_header\", \"severity\": \"error\", \"attribute\": \"$attr\"}"
      done
    fi
    
    # List issues
    if [ -n "$list_issues" ]; then
      echo "$list_issues" | while IFS=: read -r line_num list_type context; do
        [ "$first_issue" = false ] && echo -n ", "
        first_issue=false
        echo -n "{\"type\": \"list_formatting\", \"severity\": \"warning\", \"line\": $line_num}"
      done
    fi
    
    # Xref issues
    if [ "$xref_count" -gt 0 ]; then
      [ "$first_issue" = false ] && echo -n ", "
      echo -n "{\"type\": \"deprecated_xref\", \"severity\": \"warning\", \"count\": $xref_count}"
    fi
    
    echo -n "]}"
  done < "$results_file"
  
  echo ""
  echo "  ]"
  echo "}"
else
  # Console output
  while IFS='|' read -r file errors warnings missing_attrs list_issues xref_count; do
    if [ "$errors" -gt 0 ] || [ "$warnings" -gt 0 ] || [ "$verbose" = true ]; then
      echo "Checking $file..."
      
      if [ "$errors" -eq 0 ] && [ "$warnings" -eq 0 ]; then
        echo "  ✅ Compliant with all standards"
      else
        # Show missing attributes
        if [ -n "$missing_attrs" ]; then
          echo "  ❌ Missing required header attributes:"
          IFS='|' read -ra attrs <<< "$missing_attrs"
          for attr in "${attrs[@]}"; do
            [ -z "$attr" ] && continue
            echo "     - $attr"
          done
        fi
        
        # Show list issues
        if [ -n "$list_issues" ]; then
          echo "  ⚠️  List formatting issues: missing blank line before lists"
          echo "$list_issues" | while IFS=: read -r line_num list_type context; do
            echo "      Line $line_num: $list_type list after: $context"
          done
        fi
        
        # Show xref issues
        if [ "$xref_count" -gt 0 ]; then
          echo "  ⚠️  Deprecated cross-reference syntax: found $xref_count instance(s) using <<>> instead of xref:"
        fi
      fi
      echo ""
    fi
  done < "$results_file"
  
  # Summary
  if [ "$quiet" = false ]; then
    echo "Summary:"
    echo "-------"
    echo "Total files checked: $total_files"
    echo "Non-compliant files: $non_compliant_files"
    echo "Total errors: $total_errors"
    echo "Total warnings: $total_warnings"
    echo ""
    
    if [ "$non_compliant_files" -eq 0 ]; then
      echo "All files comply with the AsciiDoc standards! 🎉"
    else
      echo "Some files need to be updated to comply with the AsciiDoc standards."
    fi
  fi
fi

# Exit with appropriate code
if [ "$total_errors" -gt 0 ]; then
  exit $EXIT_NON_COMPLIANT
elif [ "$total_warnings" -gt 0 ] && [ "$severity_level" != "error" ]; then
  exit $EXIT_NON_COMPLIANT
else
  exit $EXIT_SUCCESS
fi