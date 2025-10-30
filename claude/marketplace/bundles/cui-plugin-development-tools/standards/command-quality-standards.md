# Command Quality Standards

Quality standards and anti-bloat rules for Claude Code slash commands.

## Command Best Practices

These practices are synthesized from Claude Code marketplace requirements and common command quality patterns observed in production skills.

A well-formed slash command must have:

1. **Clear Title and Description** - User knows exactly what command does
2. **Documented Parameters** - All parameters explained with examples
3. **Parameter Validation** - Check all inputs before processing
4. **Structured Workflow** - Numbered steps in logical order
5. **Decision Points** - All conditional logic clearly defined
6. **Error Handling** - What to do when tools fail
7. **User Feedback** - Progress updates and clear messages
8. **Statistics Tracking** - Counters for all important metrics
9. **Cleanup Instructions** - Artifacts removed immediately
10. **Examples** - Show how to use the command
11. **Critical Rules** - Important constraints highlighted
12. **Verification** - Check that work was successful
13. **Consistent Style** - Formatting, prompts, terminology uniform
14. **Integration Notes** - How command relates to others
15. **Performance Expectations** - How long command takes to run

## YAML Frontmatter Standards

### Required Fields

```yaml
---
name: command-name              # Unique identifier (lowercase, hyphens, max 64 chars)
description: Clear description  # What command does (50-200 chars recommended, max 1024)
---
```

### Common Mistakes

- ❌ Missing `---` delimiters
- ❌ Using tabs instead of spaces
- ❌ Empty or very short descriptions
- ❌ Descriptions exceeding 1024 characters
- ❌ Names with spaces or uppercase letters

## Anti-Bloat Rules

**CRITICAL**: Prevent command bloat - improve without increasing length.

### Rule 1: Never Add, Only Fix

- **DO**: Fix existing content for clarity, consistency, correctness
- **DO NOT**: Add new sections, examples, or explanations unless CRITICAL
- **Exception**: Only add if fundamentally missing

**Example:**
```markdown
BAD: "Run the linter" → "Run the linter. The linter checks code quality..."
GOOD: "Run the linter" → "Run AsciiDoc Linter to check code quality"
```

### Rule 2: Consolidate, Don't Duplicate

- **DO**: Merge redundant sections
- **DO NOT**: Add explanatory text that repeats existing content
- **If**: Two steps say the same thing → Merge or remove one

### Rule 3: Clarify, Don't Expand

- **DO**: Make ambiguous text precise
- **DO NOT**: Turn short instructions into paragraphs
- **Target**: Reduce ambiguity with FEWER words when possible

**Example:**
```markdown
BAD: "Clean up artifacts. This means removing all temporary..."
GOOD: "Remove .html, .bak, .tmp files immediately after each tool"
```

### Rule 4: Remove, Don't Accumulate

- **DO**: Remove redundant text, unnecessary steps, obsolete notes
- **DO NOT**: Keep old content "just in case"
- **Philosophy**: Every word should earn its place

### Rule 5: Structural Fixes Only

- **DO**: Fix step numbering, section organization, flow logic
- **DO NOT**: Add "helpful" comments, warnings everywhere
- **Limit**: One CRITICAL/IMPORTANT note per major section maximum

### Rule 6: Efficiency Over Completeness

- **DO**: Trust the AI to understand context
- **DO NOT**: Over-specify every detail
- **Remember**: Claude can infer reasonable defaults

### Rule 7: Measure Impact

After fixing, command should be:
- **Shorter** or **same length** (never longer)
- **Clearer** (reduced ambiguities)
- **More consistent** (unified style)
- **Less redundant** (no duplicate logic)

**Acceptable length changes:**
- Remove 50 lines, add 10 lines: ✅ Good (-40 net)
- Remove 10 lines, add 10 lines: ✅ Acceptable (0 net)
- Remove 0 lines, add 50 lines: ❌ Bad (+50 bloat)

### Rule 8: Track Metrics

```
Anti-Bloat Metrics:
- Total lines: <before> → <after> (<+/- count>)
- Redundant sections removed: <count>
- Duplicate text eliminated: <count>

Target: Net reduction or neutral (0 to -10% ideal)
Warning: If >5% increase, review all additions
Error: If >10% increase, revert and try again
```

## Command Complexity Scoring

**Low Complexity** (< 200 lines):
- Simple questionnaire or single-step task
- Linear workflow
- Minimal decision points

**Medium Complexity** (200-400 lines):
- Multi-step workflow
- Some conditional logic
- Moderate decision points

**High Complexity** (> 400 lines):
- Complex multi-phase workflow
- Significant conditional logic
- **BLOATED - Consider restructuring**

## Bloat Detection Criteria

Commands showing bloat symptoms:

- **> 500 lines**: Bloated - needs restructuring
- **> 400 lines**: Large - monitor for bloat
- Duplicate sections (same content repeated)
- Overlapping steps (multiple steps handle same thing)
- Over-specification (excessive detail)
- Accumulated warnings/notes everywhere
- Redundant examples

**Fix Strategy:**
1. Extract detailed knowledge to skills (standards/)
2. Remove duplicate content
3. Consolidate overlapping steps
4. Trust AI inference (remove over-specification)
5. Remove obsolete notes/warnings

## Quality Thresholds

**Excellent Command:**
- 200-400 lines (concise workflow)
- Zero duplicate sections
- Zero overlapping steps
- Clear decision points
- All parameters validated
- Consistent formatting

**Acceptable Command:**
- 400-500 lines
- Minor duplication
- Clear enough workflow
- Most parameters validated

**Bloated Command (Needs Refactoring):**
- > 500 lines
- Significant duplication
- Overlapping responsibilities
- Over-specified details
- **Action**: Apply anti-bloat rules or extract to skills

## "Minimize Without Information Loss" Principle

When refactoring commands:

✅ **Remove Safely:**
- Duplicate content (keep one, reference from others)
- Redundant examples (one good example > three mediocre ones)
- Over-specification (trust AI inference)
- Obsolete notes/warnings
- Overlapping step logic

❌ **Keep Always:**
- Core workflow steps
- Critical rules and constraints
- Parameter documentation
- Decision point logic
- Error handling instructions

## Directory Structure Standards

```
command-name.md                # Single file command (required)
```

Commands are always single files, not directories.

Exception: If command needs extensive standards/patterns (>400 lines of detailed knowledge), extract to a skill and reference it.

## Restructuring Pattern

When a command exceeds 500 lines:

**Before (Bloated):**
```
command-name.md (1,500 lines)
├── Parameters
├── Workflow (with embedded detailed logic)
├── Analysis Patterns (200 lines)
├── Best Practices (150 lines)
├── Examples
└── Error Handling
```

**After (Restructured):**
```
command-name.md (300-400 lines)
├── Parameters
├── Workflow (references skill for details)
└── Critical Rules

skill-name/SKILL.md
└── standards/
    ├── analysis-patterns.md
    └── quality-standards.md
```

Command references skill: `Skill: bundle:skill-name`
