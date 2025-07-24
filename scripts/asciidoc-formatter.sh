#!/bin/bash

# AsciiDoc Formatter - Auto-fix common AsciiDoc formatting issues
# Companion tool to asciidoc-validator.sh

# Exit codes
EXIT_SUCCESS=0
EXIT_ERROR=1

# Default values
target_path="."
dry_run=false
backup=true
interactive=false
fix_types=("all")
verbose=false

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Statistics
files_processed=0
files_modified=0
issues_fixed=0

# Display usage
usage() {
  echo "Usage: $0 [OPTIONS] [file_or_directory]"
  echo ""
  echo "Auto-format AsciiDoc files to fix common formatting issues."
  echo ""
  echo "Arguments:"
  echo "  file_or_directory    File or directory to format (default: current directory)"
  echo ""
  echo "Options:"
  echo "  -t, --type TYPE      Fix types: all, lists, xref, headers, whitespace"
  echo "                       Can be specified multiple times"
  echo "  -n, --dry-run        Show what would be fixed without modifying files"
  echo "  -i, --interactive    Ask before applying each fix"
  echo "  -b, --no-backup      Don't create backup files"
  echo "  -v, --verbose        Show detailed progress"
  echo "  -h, --help           Show this help message"
  echo ""
  echo "Fix Types:"
  echo "  lists      - Add blank lines before lists"
  echo "  xref       - Convert <<>> syntax to xref:"
  echo "  headers    - Add missing header attributes"
  echo "  whitespace - Fix trailing whitespace and ensure final newline"
  echo "  all        - Apply all fixes (default)"
  echo ""
  echo "Examples:"
  echo "  $0                                    # Format all .adoc files in current directory"
  echo "  $0 -n docs/                          # Dry run on docs directory"
  echo "  $0 -t lists -t xref file.adoc       # Fix only lists and xrefs in specific file"
  echo "  $0 -i --no-backup                   # Interactive mode without backups"
  exit 0
}

# Parse arguments
fix_types=()
while [[ $# -gt 0 ]]; do
  case $1 in
    -t|--type)
      if [[ ! "$2" =~ ^(all|lists|xref|headers|whitespace)$ ]]; then
        echo "Error: Invalid fix type '$2'"
        exit $EXIT_ERROR
      fi
      fix_types+=("$2")
      shift 2
      ;;
    -n|--dry-run)
      dry_run=true
      shift
      ;;
    -i|--interactive)
      interactive=true
      shift
      ;;
    -b|--no-backup)
      backup=false
      shift
      ;;
    -v|--verbose)
      verbose=true
      shift
      ;;
    -h|--help)
      usage
      ;;
    -*)
      echo "Error: Unknown option $1"
      usage
      ;;
    *)
      target_path="$1"
      shift
      ;;
  esac
done

# If no fix types specified, use "all"
if [ ${#fix_types[@]} -eq 0 ]; then
  fix_types=("all")
fi

# Check if target exists
if [ ! -e "$target_path" ]; then
  echo "Error: Path '$target_path' does not exist"
  exit $EXIT_ERROR
fi

# Function to check if a fix type is enabled
is_fix_enabled() {
  local fix_type="$1"
  for type in "${fix_types[@]}"; do
    [ "$type" = "all" ] || [ "$type" = "$fix_type" ] && return 0
  done
  return 1
}

# Function to create backup
create_backup() {
  local file="$1"
  if [ "$backup" = true ] && [ "$dry_run" = false ]; then
    cp "$file" "${file}.bak"
    [ "$verbose" = true ] && echo "Created backup: ${file}.bak"
  fi
}

# Function to show diff
show_diff() {
  local file="$1"
  local temp_file="$2"
  
  if command -v colordiff &> /dev/null; then
    colordiff -u "$file" "$temp_file" | head -20
  else
    diff -u "$file" "$temp_file" | head -20
  fi
}

# Function to fix list formatting
fix_lists() {
  local file="$1"
  local temp_file="${file}.tmp"
  local fixed_count=0
  
  awk '
    function count_spaces(line) {
      match(line, /^[[:space:]]*/)
      return RLENGTH
    }
    
    # Fix unordered lists
    /^[[:space:]]*\* / && !/^[[:space:]]*\*\*/ && prev !~ /^[[:space:]]*$/ && prev !~ /^[[:space:]]*\* / && prev !~ /^[[:space:]]*[0-9]+\. / {
      current_spaces = count_spaces($0)
      prev_spaces = count_spaces(prev)
      if (current_spaces <= prev_spaces) {
        print ""
        fixed_count++
      }
    }
    
    # Fix ordered lists
    /^[[:space:]]*[0-9]+\. / && prev !~ /^[[:space:]]*$/ && prev !~ /^[[:space:]]*[0-9]+\. / {
      print ""
      fixed_count++
    }
    
    # Fix definition lists
    /^[[:space:]]*[^:]+::/ && prev !~ /^[[:space:]]*$/ && prev !~ /^[[:space:]]*[^:]+::/ {
      print ""
      fixed_count++
    }
    
    {print; prev=$0}
    
    END {print fixed_count > "/tmp/fix_count"}
  ' "$file" > "$temp_file"
  
  if [ -f /tmp/fix_count ]; then
    fixed_count=$(cat /tmp/fix_count)
    rm -f /tmp/fix_count
  fi
  
  if [ $fixed_count -gt 0 ]; then
    echo -e "${YELLOW}  Fixed $fixed_count list formatting issues${NC}"
    ((issues_fixed += fixed_count))
    echo "$temp_file"
    return 0
  else
    rm -f "$temp_file"
    return 1
  fi
}

# Function to fix cross-references
fix_xrefs() {
  local file="$1"
  local temp_file="${file}.tmp"
  
  if grep -q "<<.*\.adoc.*>>" "$file"; then
    # Convert <<file.adoc#anchor,text>> to xref:file.adoc#anchor[text]
    sed 's/<<\([^,>]*\),\([^>]*\)>>/xref:\1[\2]/g' "$file" > "$temp_file"
    
    local count=$(grep -o "xref:" "$temp_file" | wc -l)
    echo -e "${YELLOW}  Fixed $count cross-reference(s)${NC}"
    ((issues_fixed += count))
    echo "$temp_file"
    return 0
  fi
  
  return 1
}

# Function to fix headers
fix_headers() {
  local file="$1"
  local temp_file="${file}.tmp"
  local added_headers=false
  
  # Check if file has a title
  if ! grep -q "^= " "$file"; then
    return 1
  fi
  
  # Required headers
  local required_headers=(
    ":toc: left"
    ":toclevels: 3"
    ":toc-title: Table of Contents"
    ":sectnums:"
    ":source-highlighter: highlight.js"
  )
  
  # Find where to insert headers (after title)
  local title_line=$(grep -n "^= " "$file" | head -1 | cut -d: -f1)
  
  if [ -n "$title_line" ]; then
    # Create temp file with headers
    head -n "$title_line" "$file" > "$temp_file"
    
    # Add missing headers
    for header in "${required_headers[@]}"; do
      if ! grep -q "$header" "$file"; then
        echo "$header" >> "$temp_file"
        added_headers=true
      fi
    done
    
    # Add the rest of the file
    tail -n +$((title_line + 1)) "$file" >> "$temp_file"
    
    if [ "$added_headers" = true ]; then
      echo -e "${YELLOW}  Added missing header attributes${NC}"
      ((issues_fixed++))
      echo "$temp_file"
      return 0
    else
      rm -f "$temp_file"
    fi
  fi
  
  return 1
}

# Function to fix whitespace
fix_whitespace() {
  local file="$1"
  local temp_file="${file}.tmp"
  local fixed=false
  
  # Remove trailing whitespace and ensure final newline
  sed 's/[[:space:]]*$//' "$file" | awk 'NR > 1 { print prev } { prev = $0 } END { print prev; if (prev != "") print "" }' > "$temp_file"
  
  # Check if anything changed
  if ! cmp -s "$file" "$temp_file"; then
    echo -e "${YELLOW}  Fixed whitespace issues${NC}"
    ((issues_fixed++))
    echo "$temp_file"
    return 0
  else
    rm -f "$temp_file"
    return 1
  fi
}

# Function to process a single file
process_file() {
  local file="$1"
  local file_modified=false
  local current_file="$file"
  
  ((files_processed++))
  
  [ "$verbose" = true ] && echo -e "${BLUE}Processing: $file${NC}"
  
  # Apply fixes in sequence
  if is_fix_enabled "lists"; then
    if temp_file=$(fix_lists "$current_file"); then
      file_modified=true
      current_file="$temp_file"
    fi
  fi
  
  if is_fix_enabled "xref"; then
    if temp_file=$(fix_xrefs "$current_file"); then
      file_modified=true
      current_file="$temp_file"
    fi
  fi
  
  if is_fix_enabled "headers"; then
    if temp_file=$(fix_headers "$current_file"); then
      file_modified=true
      current_file="$temp_file"
    fi
  fi
  
  if is_fix_enabled "whitespace"; then
    if temp_file=$(fix_whitespace "$current_file"); then
      file_modified=true
      current_file="$temp_file"
    fi
  fi
  
  # Handle modifications
  if [ "$file_modified" = true ]; then
    ((files_modified++))
    
    if [ "$interactive" = true ]; then
      echo -e "\n${YELLOW}Proposed changes for $file:${NC}"
      show_diff "$file" "$current_file"
      echo -n "Apply these changes? [y/N] "
      read -r response
      
      if [[ "$response" =~ ^[Yy]$ ]]; then
        if [ "$dry_run" = false ]; then
          create_backup "$file"
          mv "$current_file" "$file"
          echo -e "${GREEN}✓ Applied fixes to $file${NC}"
        else
          echo -e "${BLUE}Would apply fixes to $file${NC}"
        fi
      else
        echo "Skipped"
        rm -f "$current_file"
      fi
    else
      if [ "$dry_run" = true ]; then
        echo -e "${BLUE}Would fix: $file${NC}"
        show_diff "$file" "$current_file"
        rm -f "$current_file"
      else
        create_backup "$file"
        mv "$current_file" "$file"
        echo -e "${GREEN}✓ Fixed: $file${NC}"
      fi
    fi
  else
    [ "$verbose" = true ] && echo "  No issues found"
  fi
  
  # Clean up any remaining temp files
  rm -f "${file}.tmp"*
}

# Main execution
echo -e "${BLUE}AsciiDoc Formatter${NC}"
echo "=================="
[ "$dry_run" = true ] && echo "(DRY RUN - no files will be modified)"
echo ""

# Find and process files
if [ -f "$target_path" ]; then
  # Single file
  if [[ "$target_path" == *.adoc ]]; then
    process_file "$target_path"
  else
    echo "Error: File must have .adoc extension"
    exit $EXIT_ERROR
  fi
else
  # Directory
  while IFS= read -r -d '' file; do
    process_file "$file"
  done < <(find "$target_path" -name "*.adoc" -type f -print0 | sort -z)
fi

# Summary
echo ""
echo "Summary:"
echo "--------"
echo "Files processed: $files_processed"
echo "Files modified: $files_modified"
echo "Issues fixed: $issues_fixed"

if [ "$dry_run" = true ] && [ $files_modified -gt 0 ]; then
  echo ""
  echo "Run without --dry-run to apply these fixes"
fi

exit $EXIT_SUCCESS