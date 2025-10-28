# AsciiDoc Review Agent

Comprehensive quality analysis agent for AsciiDoc documentation files.

## Purpose

This agent performs thorough review of AsciiDoc files covering:
- **Format compliance** - Validates section headers, list syntax, blank line requirements
- **Link validity** - Checks cross-references, anchors, external links
- **Content quality** - Analyzes correctness, clarity, consistency, completeness
- **Tone and style** - Ensures professional, neutral, technical writing (no marketing language)

## Usage

```bash
# Review a single AsciiDoc file
User: "Review the Requirements.adoc file for quality issues"

# Review all AsciiDoc files in a directory (non-recursive)
User: "Check all AsciiDoc files in the doc/ directory"

# Verify AsciiDoc documentation in a specific location
User: "Verify the AsciiDoc documentation in oauth-sheriff-core/"
```

## Skills Used

This agent leverages:
- **cui-documentation**: Provides comprehensive AsciiDoc formatting rules, tone/style standards, and general documentation quality requirements

## How It Works

1. **Activates cui-documentation skill** to load all relevant documentation standards
2. **Validates input** and discovers target AsciiDoc files
3. **Runs format validation** using `asciidoc-validator.sh` script
4. **Verifies links** using `verify-adoc-links.py` script
5. **Analyzes content quality** using ULTRATHINK reasoning:
   - Factual correctness and RFC citation accuracy
   - Language clarity and conciseness
   - Tone/style compliance (detects marketing language, promotional wording)
   - Terminology consistency
   - Content completeness
6. **Prioritizes issues** (Critical → High → Medium → Low)
7. **Applies fixes** for critical and high-priority issues
8. **Re-validates** to confirm issues resolved
9. **Generates comprehensive report** with metrics and findings

## Features

### Validation Tools
- Uses `asciidoc-validator.sh` from cui-documentation skill (not asciidoctor compiler)
- Uses `verify-adoc-links.py` for comprehensive link checking
- Both scripts are fast, lightweight, have no dependencies
- Scripts accessed via: `./.claude/skills/cui-documentation/scripts/`
- **Portable** - Works in any project with cui-documentation skill installed
- No hardcoded repository paths - ready for remote distribution

### Smart Link Handling
- **Never removes links without verification**
- Manually checks file existence before suggesting removal
- Resolves paths from current file's directory (not project root)
- Asks user before any destructive changes
- Searches for relocated files before removal

### Tone/Style Analysis
- Detects marketing language and promotional wording
- Identifies qualification patterns ("production-proven", "battle-tested")
- Flags transitional markers (TODO, Status indicators)
- Context-aware scrutiny (stricter for specifications/standards)
- Uses ULTRATHINK reasoning for nuanced analysis

### Internal Anchor Fixing
- Automatically adds missing anchor IDs to section headers
- Converts anchor IDs to expected section titles
- Handles multiple aliases for same section
- Re-validates after adding anchors

## Examples

### Example 1: Single File Review

```
User: "Review standards/java-core.adoc for quality"

Agent:
1. Loads cui-documentation skill
2. Validates format (finds 3 blank line issues)
3. Verifies links (all valid)
4. Analyzes tone (finds 2 marketing language instances)
5. Applies fixes for all issues
6. Re-validates (all clean)
7. Reports: ✅ SUCCESS - 5 issues found and fixed
```

### Example 2: Directory Review

```
User: "Check all AsciiDoc files in doc/"

Agent:
1. Loads cui-documentation skill
2. Finds 8 .adoc files in doc/ (non-recursive)
3. Validates format across all files (finds 12 issues)
4. Verifies links (finds 2 broken anchors)
5. Analyzes tone (finds 5 promotional phrases)
6. Fixes high-priority issues (19 total)
7. Re-validates
8. Reports: ⚠️ PARTIAL - 19 fixed, 3 minor issues remain
```

## Notes

- **Non-recursive**: Only processes files directly in target directory (not subdirectories)
- **Script-based validation**: Uses custom scripts, not heavyweight rendering tools
- **Conservative link handling**: Always asks before removing links
- **ULTRATHINK reasoning**: Deep analysis for tone/style issues
- **Comprehensive tracking**: Reports all tool usage and metrics

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
