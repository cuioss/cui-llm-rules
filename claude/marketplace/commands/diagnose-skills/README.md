# diagnose-skills

Analyzes and verifies skills for YAML frontmatter correctness, standards reference validity, content integration quality (duplication, conflicts, ambiguities), and structural compliance.

## Purpose

Automates skill quality assurance by validating YAML frontmatter fields, verifying standards file references, detecting content duplication/conflicts/ambiguities, calculating integrated content scores, and ensuring skills meet Claude Code requirements.

## Usage

```bash
# Interactive mode - select from menu
/diagnose-skills

# Verify all project skills
/diagnose-skills project

# Verify all marketplace skills
/diagnose-skills global

# Verify specific skill
/diagnose-skills cui-java-core
/diagnose-skills cui-documentation
```

## What It Does

The command performs comprehensive skill analysis across 8 steps:

1. **Discover Skills** - Find all skill directories in `.claude/skills/` or `claude/marketplace/skills/`
2. **Verify SKILL.md** - Check primary skill file exists (case-sensitive)
3. **Validate YAML Frontmatter** - Parse and verify required/optional fields
4. **Check Standards References** - Verify all referenced files exist
5. **Validate Tool Restrictions** - Check allowed-tools field if present
6. **Analyze Content Integration** - Detect duplication, conflicts, ambiguities across referenced standards
7. **Calculate Score** - Generate integrated content quality score (0-100)
8. **Generate Report** - Comprehensive summary with recommendations

## Key Features

- **YAML Frontmatter Validation**: Required fields (name, description), optional fields (allowed-tools)
- **Standards Reference Verification**: Checks all file paths exist, detects broken links
- **Content Duplication Detection**: Finds redundant requirements across standards files
- **Conflict Detection**: Identifies contradictory requirements (critical vs contextual)
- **Ambiguity Detection**: Flags vague language ("some", "many", "when appropriate")
- **Integrated Content Score**: 0-100% quality rating based on duplication/conflicts/ambiguities
- **Tool Restriction Analysis**: Validates allowed-tools array syntax and values
- **Coherence Validation**: Assesses logical flow and completeness
- **Structural Compliance**: Verifies file naming, directory structure

## Parameters

### project (Optional)
- **Format**: `project` (flag)
- **Description**: Review all skills in `.claude/skills/`
- **Use Case**: Verify project-specific skills

### global (Optional)
- **Format**: `global` (flag)
- **Description**: Review all skills in `claude/marketplace/skills/`
- **Use Case**: Verify marketplace/plugin skills

### skill-name (Optional)
- **Format**: `<skill-name>`
- **Description**: Review specific skill by name
- **Search**: Looks in both `.claude/skills/` and `claude/marketplace/skills/`
- **Examples**:
  - `cui-java-core`
  - `cui-documentation`
  - `cui-frontend-development`

### No Parameters (Default)
- **Behavior**: Interactive mode with numbered menu
- **Options**: Select single skill, project, global, all, or quit

## YAML Frontmatter Validation

### Required Fields

**name** (required):
- Unique identifier for skill
- Lowercase letters, numbers, hyphens only
- Maximum 64 characters
- Should match directory name
- Example: `cui-java-core`, `cui-documentation`

**description** (required):
- Clear description of WHAT skill does AND WHEN to use it
- 50-200 characters recommended
- Maximum 1024 characters (Claude Code limit)
- Critical for Claude's skill discovery
- Example: "Core Java development standards for CUI projects including coding patterns, null safety, Lombok, modern features, DSL constants, and logging"

### Optional Fields

**allowed-tools** (optional):
- Tool access restrictions
- Format: `[Read, Write, Edit]` or `[Read, Write, Edit, Bash, Grep, Glob, Task, WebFetch, WebSearch]`
- Common mistakes:
  - Using `tools` instead of `allowed-tools` (WRONG)
  - Invalid tool names
  - Empty array `[]`
- Note: Skills use `allowed-tools`, agents use `tools`

## Standards Reference Verification

### What It Checks

1. **File Existence**: Every referenced standards file must exist
2. **Path Correctness**: Paths relative to skill directory
3. **Conditional Loading**: Validates if-conditions on standards
4. **Cross-References**: Checks xref links within standards

### Common Issues

**Broken References:**
- File moved/deleted but skill not updated
- Typo in filename or path
- Case sensitivity mismatch (standards/Java-Core.md vs standards/java-core.md)

**Outdated Paths:**
- Standards restructured but skill references old locations
- File renamed but skill not updated

## Content Integration Analysis

### Duplication Detection

**What It Finds:**
- Redundant requirements stated in multiple standards files
- Near-duplicates with slightly different wording
- Overlapping guidance that should be consolidated

**Severity Levels:**
- ❌ **Critical**: Exact duplicates (copy-paste)
- ⚠️ **Redundant**: Same requirement, different wording
- ℹ️ **Overlap**: Related but distinct (acceptable)

**Example:**
```
⚠️ Redundant: Null-safety requirements stated differently
  - standards/java-null-safety.md: "Never return @Nullable"
  - standards/java-core-patterns.md: "Avoid null returns, use Optional"
  Recommendation: Align language to avoid confusion
```

### Conflict Detection

**What It Finds:**
- Contradictory "must" statements across files
- Incompatible patterns or practices
- Conflicting best practices

**Conflict Types:**
- ❌ **Critical**: Direct contradiction (cannot both be true)
- ⚠️ **Contextual**: True in different contexts but unclear when
- ℹ️ **False**: Appears contradictory but actually compatible

**Example:**
```
❌ Critical: Lombok @Value usage contradicts immutability pattern
  - standards/java-lombok-patterns.md:67: "Use @Value for immutable objects"
  - standards/java-core-patterns.md:134: "Prefer records over Lombok annotations"
  Resolution: Clarify when to use each (records for simple, @Value for complex)
```

### Ambiguity Detection

**What It Finds:**
- Vague quantities: "some", "many", "few", "several"
- Unclear conditions: "when appropriate", "if needed", "sometimes"
- Undefined terms without definitions
- Missing criteria: "should be good", "must be sufficient"

**Severity Levels:**
- ❌ **Too vague**: Cannot determine what to do (unusable)
- ⚠️ **Needs clarification**: Understandable but could be clearer
- ✅ **Precise**: Clear, specific, actionable

**Example:**
```
❌ Too vague: "Methods should be reasonably short"
  - standards/java-core-patterns.md:78
  Fix: "Methods should be < 50 lines (recommended), < 100 lines (maximum)"
```

## Integrated Content Score

### Calculation (0-100%)

**Formula:**
```
Base Score = 100

Deductions:
- Critical duplication: -5 per instance
- Redundant duplication: -3 per instance
- Critical conflict: -10 per instance
- Contextual conflict: -5 per instance
- Critical ambiguity: -5 per instance
- Needs clarification: -3 per instance

Final Score = Base Score - Total Deductions (minimum 0)
```

### Rating Scale

- **90-100%**: Excellent - Minimal issues, high quality
- **80-89%**: Good - Minor issues, generally solid
- **70-79%**: Fair - Some issues needing attention
- **60-69%**: Poor - Significant issues affecting usability
- **0-59%**: Critical - Major problems requiring immediate fixes

### Score Interpretation

**95-100% (Excellent):**
- No critical issues
- At most 1-2 minor clarifications needed
- Standards are well-integrated and coherent

**80-94% (Good):**
- No critical issues
- Some redundancies or minor conflicts
- Generally usable but could be cleaner

**60-79% (Fair):**
- 1-2 critical issues OR
- Multiple minor issues (5-10 redundancies/conflicts/ambiguities)
- Needs cleanup for optimal quality

**0-59% (Poor/Critical):**
- Multiple critical issues
- Extensive duplication or conflicts
- Standards may be confusing or contradictory
- Requires significant rework

## Tool Restriction Validation

### Allowed Values

Valid tools for `allowed-tools` field:
- `Read` - Read files
- `Write` - Create new files
- `Edit` - Modify existing files
- `Bash` - Execute shell commands
- `Grep` - Search file contents
- `Glob` - Find files by pattern
- `Task` - Launch sub-agents
- `WebFetch` - Fetch web content
- `WebSearch` - Search the web

### Common Mistakes

**Wrong Field Name:**
```yaml
# WRONG (agents use 'tools', skills use 'allowed-tools')
tools: [Read, Write]

# CORRECT
allowed-tools: [Read, Write]
```

**Invalid Tool Names:**
```yaml
# WRONG
allowed-tools: [read, write, bash]  # Lowercase
allowed-tools: [File, Execute]      # Non-existent tools

# CORRECT
allowed-tools: [Read, Write, Bash]
```

**Empty Array:**
```yaml
# WRONG
allowed-tools: []  # No tools allowed (skill can't do anything)

# CORRECT
allowed-tools: [Read]  # At minimum, Read for loading standards
```

## Expected Duration

- **Single Skill** (small, 1-3 standards files): 10-30 seconds
  - YAML validation: instant
  - Reference check: 1-5 sec
  - Content analysis: 5-15 sec
  - Scoring: instant

- **Single Skill** (large, 5-10 standards files): 30-90 seconds
  - YAML validation: instant
  - Reference check: 5-10 sec
  - Content analysis: 20-60 sec (cross-file comparisons)
  - Scoring: instant

- **All Project Skills** (3-5 skills): 1-3 minutes

- **All Marketplace Skills** (8-12 skills): 3-8 minutes

## Integration

Use this command:
- After creating new skills
- After updating skill content or referenced standards
- Before committing skill changes
- As part of quality assurance workflow
- Periodically to maintain skill quality
- When restructuring standards documentation

Often used with:
- `/diagnose-commands` - Verify slash commands
- `/diagnose-agents` - Verify agents
- Manual review of standards files

## Example Output

```
==================================================
Analyzing: cui-java-core
Location: claude/marketplace/skills/cui-java-core
==================================================

Primary File Check:
✅ SKILL.md found

YAML Frontmatter Validation:
✅ Valid YAML syntax
✅ Required field 'name' present: "cui-java-core"
✅ Required field 'description' present (128 chars)
✅ Optional field 'allowed-tools' valid: [Read]

Standards Reference Verification:
✅ All 6 standards files exist
- standards/java-core-patterns.md ✅
- standards/java-null-safety.md ✅
- standards/java-lombok.md ✅
- standards/java-modern-features.md ✅
- standards/java-dsl-constants.md ✅
- standards/logging-core.md ✅

Tool Restrictions:
✅ allowed-tools properly configured
ℹ️  Restricted to: [Read]
✅ No tool restriction concerns

Content Integration Analysis:
Analyzing 6 standards files for integration quality...

Duplication Detection:
⚠️ Redundant (2 instances):
1. Null-safety guidance overlaps (java-null-safety.md:34, java-core-patterns.md:89)
   Recommendation: Consolidate to single authoritative section

Conflict Detection:
❌ Critical (1 instance):
1. Lombok @Value vs Records preference unclear
   - java-lombok.md:67: "Use @Value for immutable objects"
   - java-core-patterns.md:134: "Prefer records over Lombok"
   Resolution: Clarify contexts (records for simple, @Value for complex)

Ambiguity Detection:
⚠️ Needs clarification (3 instances):
1. "Methods should be reasonably short" (java-core-patterns.md:78)
   Fix: Specify numeric guidelines
2. "Use Optional when appropriate" (java-null-safety.md:45)
   Fix: Define "appropriate" contexts
3. "Prefer modern features" (java-modern-features.md:12)
   Fix: List specific features to prefer

Integrated Content Score: 74% (Fair)
- Base: 100
- Deductions: -26 (1 critical conflict, 2 redundancies, 3 clarifications)

Recommendations:
1. CRITICAL: Resolve Lombok vs Records conflict
2. Address 2 redundant requirement statements
3. Clarify 3 ambiguous guidelines with specific criteria
4. Consider consolidating overlapping null-safety guidance

────────────────────────────────────────────────────

Summary for cui-java-core:
- YAML: ✅ Valid
- References: ✅ All exist
- Tools: ✅ Properly configured
- Integration: ⚠️ Fair (74%) - needs improvement
- Status: ⚠️ Has warnings

==================================================
Skill Doctor - Analysis Complete
==================================================

Skills Analyzed: 1
- With issues: 1
- Fixed: 0 (no auto-fix available for content issues)
- Status: Fair

Issue Statistics:
- YAML errors: 0
- Broken references: 0
- Tool warnings: 0
- Content duplication: 2
- Content conflicts: 1
- Content ambiguities: 3

Integrated Content Scores:
- Average score: 74% (Fair)
- Excellent (90-100%): 0 skills
- Good (80-89%): 0 skills
- Fair (70-79%): 1 skill ← cui-java-core
- Poor (60-69%): 0 skills
- Critical (0-59%): 0 skills

Recommendations:
⚠️ cui-java-core: Content integration needs improvement (74%)
  - Resolve 1 critical conflict
  - Address 2 redundancies
  - Clarify 3 ambiguities
```

## Notes

- **YAML frontmatter is critical**: Without valid YAML, Claude Code cannot load the skill
- **Description field is key for discovery**: Claude uses it to determine when to activate skill
- **Skills use 'allowed-tools', agents use 'tools'**: Common confusion point
- **Content analysis requires standards files**: Must have access to referenced files
- **Integrated content score is composite**: Multiple factors affect final rating
- **No auto-fix for content issues**: Duplication/conflicts/ambiguities require manual resolution
- **Case-sensitive file names**: SKILL.md must be exactly that case
- **Tool restrictions optional**: If not specified, skill has access to all tools

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
