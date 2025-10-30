---
name: cui-diagnose-commands
description: Analyze, verify, and fix slash commands for clarity, structure, and bloat
---

# Commands Doctor - Verify and Fix Commands

Analyze, verify, and fix slash commands for clarity, structure, and anti-bloat compliance.

## PARAMETERS

- **scope=marketplace** (default): Analyze all marketplace commands
- **scope=global**: Analyze commands in ~/.claude/commands/
- **scope=project**: Analyze commands in .claude/commands/
- **command-name** (optional): Review specific command
- **No parameters**: Interactive mode

## TOOL USAGE REQUIREMENTS

**CRITICAL**: Use non-prompting tools.

```
Skill: cui-utility-commands:cui-diagnostic-patterns
```

✅ File Discovery: Use `Glob` (never `find`)
✅ Content Search: Use `Grep` (never `grep`/`awk`)
✅ File Reading: Use `Read` (never `cat`)

## WORKFLOW INSTRUCTIONS

### Load Analysis Standards

```
Skill: cui-plugin-development-tools:cui-skill-quality-standards
```

This skill provides:
- Command quality standards (15 best practices)
- 20 common issue patterns
- Anti-bloat rules (8 rules)
- Quality scoring criteria
- Bloat detection algorithm

### Workflow Overview

1. **Discover** - Find commands in specified scope
2. **Analyze** - Run validation checks (bloat, patterns, quality)
3. **Fix** - Apply anti-bloat rules and fixes
4. **Report** - Generate summary with metrics

### Analysis Steps

For each command:

1. **Read and Parse**
   - Extract YAML frontmatter (Pattern 16, 17)
   - Count lines and sections
   - Calculate complexity score

2. **Bloat Detection** (Pattern 11)
   - Lines > 500: BLOATED
   - Lines > 400: LARGE
   - Identify extractable content
   - Calculate bloat score

3. **Structure Validation**
   - Check YAML (Patterns 16-19)
   - Validate parameters section (Pattern 10)
   - Check workflow structure
   - Verify decision points (Pattern 3)

4. **Content Quality**
   - Detect duplication (Pattern 12)
   - Find over-specification (Pattern 13)
   - Check for obsolete content (Pattern 15)
   - Detect documentation noise (Pattern 20)

5. **Workflow Analysis**
   - Check overlapping steps (Pattern 2)
   - Verify cleanup logic (Pattern 5)
   - Check error handling (Pattern 6)
   - Validate statistics tracking (Pattern 7)

6. **Anti-Bloat Compliance**
   - Apply Rule 1: Never Add, Only Fix
   - Apply Rule 2: Consolidate, Don't Duplicate
   - Apply Rule 3: Clarify, Don't Expand
   - Apply Rule 4: Remove, Don't Accumulate
   - Calculate before/after metrics

### Issue Report

**CRITICAL:**
- Missing/invalid YAML (Patterns 16, 17, 18)
- Missing error handling for critical tools (Pattern 6)
- Parameter validation gap (Pattern 10)

**WARNINGS:**
- Command bloat >500 lines (Pattern 11)
- Duplicate content (Pattern 12)
- Overlapping steps (Pattern 2)
- Over-specification (Pattern 13)
- Obsolete content (Pattern 15)

**SUGGESTIONS:**
- Inconsistent prompts (Pattern 1)
- Unclear step purpose (Pattern 9)
- Missing config persistence (Pattern 8)

### Auto-Fix Strategy

- **Bloat (>500 lines)**: Recommend extracting to skill
- **Duplication**: Consolidate to single source
- **Over-specification**: Simplify, trust AI
- **Obsolete content**: Remove entirely
- **YAML issues**: Repair structure

**Anti-Bloat Metrics:**
```
Total lines: <before> → <after> (<+/- count>)
Sections removed: <count>
Duplicate text eliminated: <lines>

Target: 0 to -10% change
Warning: >5% increase
Error: >10% increase (revert)
```

### Final Report

```
Commands Analyzed: <total>
- Bloated (>500 lines): <count> - NEEDS RESTRUCTURING
- Large (>400 lines): <count> - MONITOR
- Well-sized (<400 lines): <count>

Issue Statistics:
- Critical: <count>
- Warnings: <count>
- Bloat detected: <count>

Anti-Bloat Metrics:
- Total reduction: <lines> lines removed
- Duplicate content eliminated: <lines>

By Command:
- <command>: <lines> lines | <issues>C/<warnings>W | Bloat: <YES/NO>
```

## CRITICAL RULES

- **LOAD STANDARDS FIRST** - Reference skill for patterns and anti-bloat rules
- **ANTI-BLOAT MANDATORY** - Never increase command length
- **MEASURE IMPACT** - Track before/after metrics
- **RESTRUCTURE IF BLOATED** - Commands >500 lines need skill extraction
- **TRUST AI INFERENCE** - Remove over-specification
- **REMOVE OBSOLETE** - Delete deprecated content entirely
- **ONE SOURCE OF TRUTH** - Consolidate duplicates

## STANDARDS REFERENCED

**Skill: cui-plugin-development-tools:cui-skill-quality-standards**

Provides:
- Command quality standards
- 20 analysis patterns
- 8 anti-bloat rules
- Bloat detection algorithm
- Restructuring strategies
