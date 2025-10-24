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
    BEGIN {
        in_code_block = 0
        prev_line = ""
        prev_was_blank = 1  # Start as if previous was blank
        in_list = 0
    }
    
    {
        # Track if we are inside a code block
        if ($0 == "----") {
            in_code_block = !in_code_block
        }
        
        # Check if current line is blank
        current_is_blank = (length($0) == 0)
        
        # Detect if current line starts a new list (only outside code blocks)
        starts_new_list = 0
        if (!in_code_block) {
            # Check for list starters
            if (match($0, /^[\*\-\+] /)) {              # Unordered list
                starts_new_list = 1
                list_type = "unordered"
            } else if (match($0, /^[0-9]+\. /)) {        # Ordered list  
                starts_new_list = 1
                list_type = "ordered"
            } else if (match($0, /^[^:]+::/)) {          # Definition list
                starts_new_list = 1
                list_type = "definition"
            } else if (match($0, /^\. /) && !in_list) { # Numbered list with dot
                starts_new_list = 1
                list_type = "numbered"
            }
        }
        
        # Detect if we are continuing a list
        continuing_list = 0
        if (!in_code_block && in_list) {
            # Check for list continuations
            if (match($0, /^[\*\-\+] /) ||     # Another unordered item
                match($0, /^\*\* /) ||         # Nested unordered
                match($0, /^[0-9]+\. /) ||     # Another ordered item
                match($0, /^\. /) ||           # Another numbered item (dot syntax)
                current_is_blank) {            # Blank line within list
                continuing_list = 1
            }
        }
        
        # If this starts a new list and previous line was not blank
        # and we are not at the beginning of the file and not already in list
        if (starts_new_list && !prev_was_blank && NR > 1 && !in_list) {
            print NR ":" list_type ":" substr(prev_line, 1, 50)
        }
        
        # Update list state
        if (starts_new_list) {
            in_list = 1
        } else if (!continuing_list && !current_is_blank) {
            in_list = 0
        }
        
        # Update state for next iteration
        prev_line = $0
        prev_was_blank = current_is_blank
    }
  ' "$file")
  
  if [ -n "$list_issues" ]; then
    file_has_issues=true
    local list_count=$(echo "$list_issues" | wc -l | tr -d ' ')
    ((file_warnings += list_count))
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