#!/bin/bash

# Documentation Statistics Generator
# Analyzes AsciiDoc documentation and generates metrics reports
# Compatible with bash 3.2+

# Exit codes
EXIT_SUCCESS=0
EXIT_ERROR=1

# Default values
target_dir="."
output_format="console"
include_details=false

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Statistics storage
total_files=0
total_lines=0
total_words=0
total_sections=0
total_xrefs=0
total_images=0
total_code_blocks=0
total_tables=0
total_lists=0

# Temporary files
temp_file_stats=$(mktemp /tmp/doc-stats-files.XXXXXX)
temp_dir_stats=$(mktemp /tmp/doc-stats-dirs.XXXXXX)
trap "rm -f $temp_file_stats $temp_dir_stats" EXIT

# Display usage
usage() {
  echo "Usage: $0 [OPTIONS] [directory]"
  echo ""
  echo "Generate statistics and metrics for AsciiDoc documentation."
  echo ""
  echo "Arguments:"
  echo "  directory              Directory to analyze (default: current directory)"
  echo ""
  echo "Options:"
  echo "  -f, --format FORMAT    Output format: console, json, csv, markdown (default: console)"
  echo "  -d, --details          Include detailed per-file statistics"
  echo "  -h, --help             Show this help message"
  echo ""
  echo "Metrics Collected:"
  echo "  - File count and sizes"
  echo "  - Line and word counts"
  echo "  - Section structure depth"
  echo "  - Cross-references (xref)"
  echo "  - Images and media"
  echo "  - Code blocks"
  echo "  - Tables"
  echo "  - Lists"
  echo ""
  echo "Examples:"
  echo "  $0                                    # Basic stats for current directory"
  echo "  $0 -f json -d docs/                  # Detailed JSON report for docs"
  echo "  $0 -f markdown standards/            # Markdown report for standards"
  exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -f|--format)
      output_format="$2"
      if [[ ! "$output_format" =~ ^(console|json|csv|markdown)$ ]]; then
        echo "Error: Invalid format '$output_format'"
        exit $EXIT_ERROR
      fi
      shift 2
      ;;
    -d|--details)
      include_details=true
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
      target_dir="$1"
      shift
      ;;
  esac
done

# Validate directory
if [ ! -d "$target_dir" ]; then
  echo "Error: Directory '$target_dir' does not exist"
  exit $EXIT_ERROR
fi

# Function to format file size
format_size() {
  local size=$1
  if [ $size -gt 1048576 ]; then
    echo "$((size / 1048576)) MB"
  elif [ $size -gt 1024 ]; then
    echo "$((size / 1024)) KB"
  else
    echo "$size B"
  fi
}

# Function to analyze a single file
analyze_file() {
  local file="$1"
  local lines=$(wc -l < "$file")
  local words=$(wc -w < "$file")
  local size
  
  # Get file size
  if [[ "$OSTYPE" == "darwin"* ]]; then
    size=$(stat -f%z "$file" 2>/dev/null || echo 0)
  else
    size=$(stat -c%s "$file" 2>/dev/null || echo 0)
  fi
  
  # Count sections
  local sections=$(grep -c "^=\+ " "$file" || echo 0)
  local max_depth=$(grep "^=\+ " "$file" | awk '{print length($1)}' | sort -nr | head -1)
  [ -z "$max_depth" ] && max_depth=0
  
  # Count elements
  local xrefs=$(grep -c "xref:" "$file" || echo 0)
  local images=$(grep -c "image::" "$file" || echo 0)
  local code_blocks=$(grep -c "^\[source" "$file" || echo 0)
  local tables=$(grep -c "^|===" "$file" || echo 0)
  local lists=$(grep -cE "^[[:space:]]*(\*|[0-9]+\.|.*::)" "$file" || echo 0)
  
  # Store file stats
  echo "$file|$lines|$words|$size|$sections|$max_depth|$xrefs|$images|$code_blocks|$tables|$lists" >> "$temp_file_stats"
  
  # Update totals
  ((total_lines += lines))
  ((total_words += words))
  ((total_sections += sections))
  ((total_xrefs += xrefs))
  ((total_images += images))
  ((total_code_blocks += code_blocks))
  ((total_tables += tables))
  ((total_lists += lists))
  
  # Update directory stats
  local dir=$(dirname "$file")
  local existing=$(grep "^$dir|" "$temp_dir_stats" 2>/dev/null)
  if [ -z "$existing" ]; then
    echo "$dir|1|$lines|$words|$size" >> "$temp_dir_stats"
  else
    # Update existing entry
    local old_files old_lines old_words old_size
    IFS='|' read -r _ old_files old_lines old_words old_size <<< "$existing"
    grep -v "^$dir|" "$temp_dir_stats" > "$temp_dir_stats.tmp"
    echo "$dir|$((old_files + 1))|$((old_lines + lines))|$((old_words + words))|$((old_size + size))" >> "$temp_dir_stats.tmp"
    mv "$temp_dir_stats.tmp" "$temp_dir_stats"
  fi
}

# Output formatters
output_console() {
  echo -e "${BLUE}Documentation Statistics Report${NC}"
  echo "=============================="
  echo "Directory: $target_dir"
  echo "Generated: $(date)"
  echo ""
  
  # Overall statistics
  echo -e "${CYAN}Overall Statistics:${NC}"
  echo "  Total files: $total_files"
  echo "  Total lines: $(printf "%'d" $total_lines)"
  echo "  Total words: $(printf "%'d" $total_words)"
  
  if [ $total_files -gt 0 ]; then
    echo "  Average lines/file: $((total_lines / total_files))"
    echo "  Average words/file: $((total_words / total_files))"
  fi
  echo ""
  
  echo -e "${CYAN}Content Elements:${NC}"
  echo "  Sections: $total_sections"
  echo "  Cross-references: $total_xrefs"
  echo "  Images: $total_images"
  echo "  Code blocks: $total_code_blocks"
  echo "  Tables: $total_tables"
  echo "  Lists: $total_lists"
  echo ""
  
  # Directory breakdown
  echo -e "${CYAN}By Directory:${NC}"
  echo "Directory                          Files    Lines     Words      Size"
  echo "------------------------------------------------------------------------"
  
  sort "$temp_dir_stats" | while IFS='|' read -r dir files lines words size; do
    printf "%-35s %5d %8d %9d %10s\n" "$dir" "$files" "$lines" "$words" "$(format_size $size)"
  done
  
  # Detailed file statistics
  if [ "$include_details" = true ]; then
    echo ""
    echo -e "${CYAN}File Details:${NC}"
    echo "File                               Lines  Words  Sections  XRefs  Images  Code"
    echo "--------------------------------------------------------------------------------"
    
    while IFS='|' read -r file lines words size sections depth xrefs images code tables lists; do
      printf "%-35s %5d %6d %8d %6d %7d %5d\n" "$(basename "$file")" "$lines" "$words" "$sections" "$xrefs" "$images" "$code"
    done < "$temp_file_stats" | sort
  fi
}

output_json() {
  echo "{"
  echo "  \"metadata\": {"
  echo "    \"directory\": \"$target_dir\","
  echo "    \"generated\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\","
  echo "    \"total_files\": $total_files"
  echo "  },"
  echo "  \"summary\": {"
  echo "    \"lines\": $total_lines,"
  echo "    \"words\": $total_words,"
  echo "    \"sections\": $total_sections,"
  echo "    \"cross_references\": $total_xrefs,"
  echo "    \"images\": $total_images,"
  echo "    \"code_blocks\": $total_code_blocks,"
  echo "    \"tables\": $total_tables,"
  echo "    \"lists\": $total_lists,"
  echo "    \"averages\": {"
  if [ $total_files -gt 0 ]; then
    echo "      \"lines_per_file\": $((total_lines / total_files)),"
    echo "      \"words_per_file\": $((total_words / total_files)),"
    echo "      \"sections_per_file\": $((total_sections / total_files))"
  else
    echo "      \"lines_per_file\": 0,"
    echo "      \"words_per_file\": 0,"
    echo "      \"sections_per_file\": 0"
  fi
  echo "    }"
  echo "  },"
  echo "  \"directories\": {"
  
  local first_dir=true
  while IFS='|' read -r dir files lines words size; do
    [ "$first_dir" = false ] && echo ","
    first_dir=false
    
    echo -n "    \"$dir\": {"
    echo -n "\"files\": $files, "
    echo -n "\"lines\": $lines, "
    echo -n "\"words\": $words, "
    echo -n "\"size\": $size"
    echo -n "}"
  done < "$temp_dir_stats"
  
  echo ""
  echo "  }"
  
  if [ "$include_details" = true ]; then
    echo ","
    echo "  \"files\": {"
    
    local first_file=true
    while IFS='|' read -r file lines words size sections depth xrefs images code tables lists; do
      [ "$first_file" = false ] && echo ","
      first_file=false
      
      echo -n "    \"$file\": {"
      echo -n "\"lines\": $lines, "
      echo -n "\"words\": $words, "
      echo -n "\"size\": $size, "
      echo -n "\"sections\": $sections, "
      echo -n "\"max_depth\": $depth, "
      echo -n "\"xrefs\": $xrefs, "
      echo -n "\"images\": $images, "
      echo -n "\"code_blocks\": $code, "
      echo -n "\"tables\": $tables, "
      echo -n "\"lists\": $lists"
      echo -n "}"
    done < "$temp_file_stats"
    
    echo ""
    echo "  }"
  fi
  
  echo "}"
}

output_csv() {
  if [ "$include_details" = true ]; then
    echo "File,Lines,Words,Size,Sections,MaxDepth,XRefs,Images,CodeBlocks,Tables,Lists"
    while IFS='|' read -r file lines words size sections depth xrefs images code tables lists; do
      echo "\"$file\",$lines,$words,$size,$sections,$depth,$xrefs,$images,$code,$tables,$lists"
    done < "$temp_file_stats"
  else
    echo "Directory,Files,Lines,Words,Size"
    while IFS='|' read -r dir files lines words size; do
      echo "\"$dir\",$files,$lines,$words,$size"
    done < "$temp_dir_stats"
  fi
}

output_markdown() {
  echo "# Documentation Statistics Report"
  echo ""
  echo "**Directory:** $target_dir  "
  echo "**Generated:** $(date)  "
  echo ""
  
  echo "## Summary"
  echo ""
  echo "| Metric | Value |"
  echo "|--------|-------|"
  echo "| Total Files | $total_files |"
  echo "| Total Lines | $(printf "%'d" $total_lines) |"
  echo "| Total Words | $(printf "%'d" $total_words) |"
  
  if [ $total_files -gt 0 ]; then
    echo "| Average Lines/File | $((total_lines / total_files)) |"
    echo "| Average Words/File | $((total_words / total_files)) |"
  fi
  echo ""
  
  echo "## Content Elements"
  echo ""
  echo "| Element | Count |"
  echo "|---------|-------|"
  echo "| Sections | $total_sections |"
  echo "| Cross-references | $total_xrefs |"
  echo "| Images | $total_images |"
  echo "| Code Blocks | $total_code_blocks |"
  echo "| Tables | $total_tables |"
  echo "| Lists | $total_lists |"
  echo ""
  
  echo "## By Directory"
  echo ""
  echo "| Directory | Files | Lines | Words | Size |"
  echo "|-----------|-------|-------|-------|------|"
  
  while IFS='|' read -r dir files lines words size; do
    echo "| $dir | $files | $lines | $words | $(format_size $size) |"
  done < "$temp_dir_stats" | sort
}

# Main execution
if [ "$output_format" = "console" ]; then
  echo -e "${BLUE}Analyzing documentation...${NC}" >&2
fi

# Find and analyze all .adoc files
find "$target_dir" -name "*.adoc" -type f | while read -r file; do
  ((total_files++))
  analyze_file "$file"
done

# Get final count
total_files=$(find "$target_dir" -name "*.adoc" -type f | wc -l | tr -d ' ')

# Output results
case "$output_format" in
  json)
    output_json
    ;;
  csv)
    output_csv
    ;;
  markdown)
    output_markdown
    ;;
  *)
    output_console
    ;;
esac

exit $EXIT_SUCCESS