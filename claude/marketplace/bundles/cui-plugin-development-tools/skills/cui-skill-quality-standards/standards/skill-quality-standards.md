# Skill Quality Standards

Standards for well-formed, high-quality skills in the Claude Code marketplace.

## Structural Requirements

A well-formed skill must have:

1. **Valid YAML Frontmatter** - Proper syntax with required fields (`name`, `description`)
2. **Clear Description** - Describes when and why to use this skill (50-200 characters recommended)
3. **Appropriate Tool Access** - Minimal necessary tools via `allowed-tools` field
4. **Primary SKILL.md File** - Properly named and structured (case-sensitive)
5. **Valid Standards References** - All referenced files exist within skill directory
6. **Relative Paths Only** - No absolute paths (no `~/`, `/Users/`, `/home/`)
7. **Clear Workflow** - Step-by-step usage instructions
8. **Supporting Documentation** - README.md for users (recommended)
9. **Self-Contained Standards** - No broken cross-references to external files
10. **Proper Integration** - Referenced by agents, references valid skills only
11. **Consistent Structure** - Follows skill directory conventions
12. **No Documentation-Only Noise** - Remove sections with only broken/external links that provide zero information

## Content Quality Requirements

High-quality skill content must have:

13. **No Harmful Duplication** - Avoid repeating content across standards files; use cross-references
14. **No Conflicts** - Ensure consistent requirements across all standards
15. **Precise Requirements** - Use specific, measurable criteria instead of vague terms
16. **Complete Coverage** - Cover all important aspects of the domain
17. **High Coherence** - Standards should work together logically
18. **Excellent Usability** - Clear, actionable guidance with comprehensive examples
19. **Integrated Content Score >= 75** - Minimum acceptable quality threshold
20. **Target Score >= 90** - Excellent quality for production use

## Quality Scoring Criteria

### Architecture Compliance Score (0-100)

**Formula:** `100 - total_deductions`

**Deductions:**
- External file ref in workflow: **-20 points** each (CRITICAL)
- External file ref in documentation: **-10 points** each (WARNING)
- Absolute path: **-20 points** each (CRITICAL)
- Missing internal file: **-10 points** each (WARNING)
- Documentation-only noise: **-5 points** each (minor quality issue)

**Thresholds:**
- **90-100**: Excellent - Fully self-contained, marketplace ready
- **75-89**: Good - Minor cleanup needed
- **60-74**: Fair - Moderate improvements required
- **Below 60**: Poor - Major fixes needed

### Integrated Content Score (0-100)

**Components:**
- **Duplication Analysis** (0-100): Lower is better
  - 0-2 instances: 95-100 points
  - 3-5 instances: 85-94 points
  - 6-10 instances: 70-84 points
  - 11+ instances: Below 70 points

- **Conflict Detection** (0-100): Binary
  - 0 conflicts: 100 points
  - 1 contextual conflict: 90 points
  - 1 critical conflict: 50 points
  - Multiple conflicts: Below 50 points

- **Ambiguity Analysis** (0-100): Based on vague statements
  - 0-2 instances: 95-100 points
  - 3-5 instances: 85-94 points
  - 6-10 instances: 70-84 points
  - 11+ instances: Below 70 points

- **Coherence Assessment** (0-100): Qualitative
  - Logical loading order: +25 points
  - Progressive disclosure: +25 points
  - Complete coverage: +25 points
  - No gaps detected: +25 points

- **Usability Evaluation** (0-100): Qualitative
  - Clear, actionable guidance: +25 points
  - Comprehensive code examples: +25 points
  - Specific requirements with criteria: +25 points
  - Well-structured workflow: +25 points

**Overall Score:** Weighted average of all components

**Thresholds:**
- **90-100**: Excellent - Ready for production use
- **75-89**: Good - Minor improvements needed
- **60-74**: Fair - Moderate improvements required
- **Below 60**: Poor - Major rework needed

## Principle: Minimize Content Without Information Loss

When evaluating skills, apply this principle:

### Remove Safely:
- External links that don't exist
- Format-incompatible references that won't render
- Empty documentation sections
- Broken cross-references
- Documentation-only sections with ONLY external/broken links

### Keep Always:
- Working internal references
- Actual documentation content
- Working external URLs (https://)
- Content that provides information

### Information Loss Risk:
- **ZERO**: Safe to remove without any loss
- **LOW**: Minimal context lost, acceptable
- **MEDIUM**: Some information lost, requires judgment
- **HIGH**: Significant information lost, DO NOT remove

## Directory Structure Standards

```
skill-name/
├── SKILL.md                    # Primary skill file (required)
├── README.md                   # User documentation (recommended)
├── VALIDATION.md               # Quality report (optional)
├── standards/                  # Self-contained standards files
│   ├── core-standard.md
│   ├── advanced-standard.md
│   └── examples.md
├── templates/                  # Template files (optional)
└── examples/                   # Example code (optional)
```

## YAML Frontmatter Standards

### Required Fields

```yaml
---
name: skill-name                # Unique identifier (lowercase, hyphens, max 64 chars)
description: Clear description  # What skill does and when to use it (50-200 chars recommended, max 1024)
---
```

### Optional Fields

```yaml
allowed-tools: [Read, Grep, Glob]  # Tool access list (minimal necessary tools)
```

### Common Mistakes

- ❌ Using `tools` instead of `allowed-tools` (wrong field name for skills)
- ❌ Missing `---` delimiters
- ❌ Using tabs instead of spaces in YAML
- ❌ Empty or very short descriptions (< 10 chars)
- ❌ Descriptions exceeding 1024 characters (Claude Code limit)
- ❌ Names with spaces or uppercase letters

## Tool Access Standards

### Knowledge Skills (Read-Only Recommended)
- **Appropriate**: `[Read]`, `[Read, Grep, Glob]`
- **Warning**: Includes `Write`, `Edit`, `Bash` - verify intentional

### Active Skills (May Need Write Access)
- **Code generators**: `Write`, `Edit` access reasonable
- **Build runners**: `Bash` access reasonable
- **File creators**: `Write` access reasonable

### Default Behavior
- If `allowed-tools` not specified, inherits all tools from parent
- Recommendation: Explicitly specify tools for clarity

## Content Quality Checks

### Duplication Detection

**Harmful (Must Fix):**
- Exact same content in multiple files
- Identical code examples repeated
- Same requirements stated identically

**Redundant (Should Fix):**
- Similar content stated differently
- Overlapping explanations of same concept
- Inconsistent terminology for same thing

**Acceptable:**
- One file references another for details
- Cross-references with `Read: standards/other-file.md`
- Brief mentions with link to authoritative source

### Conflict Detection

**Critical (Must Fix):**
- Direct contradictions (cannot both be true)
- File A requires X, File B forbids X
- Mutually exclusive requirements

**Contextual (Should Fix):**
- Requirements true in different contexts but unclear when
- Appears contradictory but lacks context
- Needs clarification about applicability

**False (Clarify):**
- Appears contradictory but actually compatible
- Different aspects of same topic
- Complementary rather than conflicting

### Ambiguity Detection

**Vague Terms to Avoid:**
- Quantities: "some", "many", "few", "several"
- Conditions: "when appropriate", "if needed", "sometimes", "often", "usually"
- Undefined technical terms
- Missing criteria: "should be good", "must be sufficient"

**Replace With:**
- Specific numbers: "< 50 lines", ">= 80% coverage"
- Clear conditions: "for all test data (mandatory)", "when X occurs"
- Defined terms with glossary
- Measurable criteria: "must pass all tests", "zero warnings"

## Integration Standards

### Agent References
- Skills should be referenced by at least one agent
- Unused skills indicate maintenance burden
- Circular skill references should be avoided

### Skill-to-Skill References
- Use `Skill: skill-name` syntax for skill dependencies
- Keep dependency chains short (max 2-3 deep)
- Avoid circular dependencies

### Marketplace Distribution
- Skills must be fully self-contained
- No references to files outside skill directory
- All `Read: standards/` paths must exist within skill
- Format compatibility (use `.md`, not `.adoc` in marketplace)
