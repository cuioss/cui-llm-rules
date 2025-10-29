---
name: cui-diagnose-skills
description: Analyze, verify, and fix skills for structure, YAML frontmatter, standards references, and integration quality
---

# Skill Doctor - Verify and Fix Skills

Analyze, verify, and fix skills for structure, YAML frontmatter, standards references, and integration quality.

## PARAMETERS

- **project** (optional): Review all project-specific skills in `.claude/skills/`
- **global** (optional): Review all global skills in `claude/marketplace/skills/` (plugin skills)
- **skill-name** (optional): Review a specific skill by name (e.g., `cui-java-core`)
- **No parameters**: Interactive mode - display menu of all skills and let user select

## PARAMETER VALIDATION

**If `project` parameter is provided:**
- Process all skill directories in `.claude/skills/`
- Skip if directory doesn't exist (display message)

**If `global` parameter is provided:**
- Process all skill directories in `claude/marketplace/skills/`
- Exclude `diagnose-skills` itself from analysis

**If specific skill name is provided:**
- Look for skill in both `.claude/skills/` and `claude/marketplace/skills/`
- Process the first match found
- Report error if skill not found

**If no parameters provided:**
- Display interactive menu with numbered list of all skills
- Let user select which skill(s) to review

## WORKFLOW INSTRUCTIONS

### Step 1: Determine Scope and Discover Skills

**A. Parse Parameters**

Determine what to process based on parameters:

1. If `project` → Set scope to `.claude/skills/`
2. If `global` → Set scope to `claude/marketplace/skills/`
3. If skill name provided → Search both directories
4. If no parameters → Interactive mode

**B. Discover Skills**

Based on scope, find all skill directories:

```bash
# For project scope
find .claude/skills -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort

# For global scope
find claude/marketplace/skills -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort

# For specific skill (search both)
find .claude/skills claude/marketplace/skills -mindepth 1 -maxdepth 1 -type d -name "*<skill-name>*" 2>/dev/null | head -1
```

**C. Interactive Mode (if no parameters)**

Display menu:

```
Available Skills:

PROJECT SKILLS (.claude/skills/):
(none found)

GLOBAL SKILLS (claude/marketplace/skills/):
1. cui-java-core
2. cui-java-unit-testing
3. cui-javadoc
4. cui-java-cdi
5. cui-frontend-development
6. cui-documentation
7. cui-project-setup
8. cui-requirements

Options:
- Enter number to select single skill
- Enter "project" to review all project skills
- Enter "global" to review all global skills
- Enter "all" to review everything
- Enter "quit" to exit

Your choice:
```

Wait for user input and set scope accordingly.

### Step 2: Initialize Analysis Statistics

Create tracking variables:
- `total_skills`: Total number of skills to analyze
- `skills_with_issues`: Number of skills with problems
- `skills_fixed`: Number of skills fixed
- `total_issues`: Total issues found across all skills
- `issues_fixed`: Total issues fixed
- `critical_issues`: Number of critical issues found
- `warnings`: Number of warnings found
- `yaml_errors`: Count of YAML frontmatter issues
- `broken_references`: Count of broken standards references
- `structure_issues`: Count of file structure problems
- `tool_warnings`: Count of tool restriction concerns
- `content_duplication_issues`: Count of content duplication problems
- `content_conflicts`: Count of conflicting requirements
- `content_ambiguities`: Count of ambiguous statements
- `avg_integrated_content_score`: Average integrated content score across all skills
- `skills_excellent_score`: Count of skills with score >= 90
- `skills_poor_score`: Count of skills with score < 60

### Step 3: Analyze Each Skill

For EACH skill directory, execute the following analysis:

#### Step 3.1: Display Skill Header

```
==================================================
Analyzing: <skill-name>
Location: <skill-path>
==================================================
```

#### Step 3.2: Verify SKILL.md Exists

Check for primary skill file:

1. Look for `SKILL.md` (case-sensitive) in skill directory
2. If not found, check for common variations: `skill.md`, `Skill.md`, `README.md`
3. Report critical error if no primary file found

Display:
```
Primary File Check:
✅ SKILL.md found
❌ SKILL.md not found (critical error)
⚠️  Found skill.md instead of SKILL.md (naming issue)
```

#### Step 3.3: Validate YAML Frontmatter

**CRITICAL**: Parse and validate YAML frontmatter in SKILL.md.

**A. Extract Frontmatter**

Read SKILL.md and extract YAML block between `---` delimiters:

```bash
# Extract frontmatter (first --- to second ---)
sed -n '/^---$/,/^---$/p' <skill-path>/SKILL.md | sed '1d;$d'
```

**B. Validate YAML Syntax**

Check for valid YAML structure:
- Proper `---` delimiters at start and end
- Valid YAML syntax (proper indentation, no syntax errors)
- No tabs (YAML requires spaces only)

**C. Validate Required Fields**

Check required fields are present and non-empty:

✅ **name** (required): Unique identifier for skill
- Must be present
- Must be non-empty string
- Must use lowercase letters, numbers, and hyphens only
- Maximum 64 characters
- Should match directory name (convention)
- Example: `cui-java-core`, `cui-documentation`

✅ **description** (required): Clear, specific description of what the skill does and when to use it
- Must be present
- Must be non-empty string
- Recommended: 50-200 characters
- Maximum: 1024 characters (Claude Code limit)
- Should describe both WHAT the skill does AND WHEN to use it
- Critical for Claude to discover when to activate the skill
- Example: "Core Java development standards for CUI projects including coding patterns, null safety, Lombok, modern features, DSL constants, and logging"

**D. Validate Optional Fields**

Check optional fields if present:

⚠️ **allowed-tools** (optional): Tool access list
- If present, must be valid array format: `[Read, Write]` or `[Read, Write, Edit]`
- Valid tool names: Read, Write, Edit, Bash, Grep, Glob, Task, WebFetch, WebSearch
- Check for common mistakes:
  - Using `tools` instead of `allowed-tools` (WRONG - skills use `allowed-tools`)
  - Invalid tool names
  - Empty array `[]`

**E. Report Findings**

Display:
```
YAML Frontmatter Validation:
✅ Valid YAML syntax
✅ Required field 'name' present: "cui-java-core"
✅ Required field 'description' present (142 characters)
✅ Optional field 'allowed-tools' valid: [Read, Edit, Write, Bash, Grep, Glob]
❌ Missing required field: 'name'
❌ Invalid YAML syntax at line 3: unexpected indentation
⚠️  Field 'tools' should be 'allowed-tools' for skills (WRONG field name)
⚠️  Description is very short (12 characters) - recommend 50-200 characters
⚠️  Description exceeds 1024 characters - Claude Code maximum
⚠️  Name exceeds 64 characters - Claude Code maximum
⚠️  Name contains spaces or uppercase - should use lowercase and hyphens only
⚠️  Unknown field 'color' - not used for skills
```

Update statistics: Increment `yaml_errors` for each ❌ issue.

#### Step 3.4: Validate Standards References

**CRITICAL**: Find and verify all references to standards files.

**A. Extract Standards References**

Search SKILL.md for standards file references:

```bash
# Find lines with "Read: standards/" or similar patterns
grep -E "(Read:|Source:)\s*standards/" <skill-path>/SKILL.md
```

Typical patterns:
- `Read: standards/java-core-patterns.md`
- `Source: standards/logging-standards.md`
- References in workflow sections

**B. Verify Each Reference**

For each referenced standards file:

1. **Extract file path**: Parse the relative path (e.g., `standards/java-core-patterns.md`)
2. **Check file exists**: Verify file exists at `<skill-path>/<file-path>`
3. **Validate relative path**: Ensure path starts with `standards/` (not `./standards/` or absolute)
4. **Check section anchors**: If reference includes `#section-id`, verify section exists in file

**C. Detect Absolute Path Issues**

Scan for prohibited absolute paths:
- `~/` paths
- `/Users/` or `/home/` paths
- Full filesystem paths

These are critical errors - skills must be portable.

**D. Report Findings**

Display:
```
Standards References Verification:
✅ All 6 standards references valid
  - standards/java-core-patterns.md ✅
  - standards/java-null-safety.md ✅
  - standards/java-lombok-patterns.md ✅
  - standards/java-modern-features.md ✅
  - standards/dsl-constants.md ✅
  - standards/logging-standards.md ✅
❌ Referenced file not found: standards/missing-file.md
❌ Section anchor not found: standards/logging.md#nonexistent-section
❌ Using absolute path: ~/git/cui-llm-rules/standards/file.md (must be relative)
⚠️  No standards references found (is this intentional?)
```

Update statistics: Increment `broken_references` for each ❌ issue.

#### Step 3.5: Validate Directory Structure

Check skill directory structure follows conventions.

**A. Check Primary Files**

Verify expected files:
- ✅ `SKILL.md` (required) - already checked in Step 3.2
- ℹ️ `README.md` (optional but recommended) - usage documentation
- ℹ️ `VALIDATION.md` (optional) - validation report for Phase 2 skills

**B. Check Supporting Directories**

Check for optional directories and their contents:

1. **standards/** directory:
   - Count `.md` files
   - Verify referenced in SKILL.md workflow
   - Check files are self-contained (no broken cross-references)

2. **templates/** directory:
   - Count template files (usually `.java`, `.js`, etc.)
   - Verify referenced in SKILL.md if present

3. **examples/** directory:
   - Count example files
   - Verify referenced in SKILL.md if present

4. **checklists/** directory:
   - Count checklist files
   - Verify referenced in SKILL.md if present

**C. Report Findings**

Display:
```
Structure Validation:
✅ Primary file SKILL.md present (288 lines)
✅ README.md present (documentation)
✅ VALIDATION.md present (quality report)
✅ standards/ directory (5 files, 1,485 total lines)
  - testing-junit-core.md (295 lines)
  - testing-value-objects.md (210 lines)
  - testing-generators.md (366 lines)
  - testing-mockwebserver.md (363 lines)
  - integration-testing.md (251 lines)
ℹ️  No templates/ directory
ℹ️  No examples/ directory
ℹ️  No checklists/ directory
⚠️  standards/ directory present but not referenced in SKILL.md workflow
```

Update statistics: Increment `structure_issues` for each ⚠️ or ❌ issue.

#### Step 3.6: Review Tool Restrictions

Analyze tool access patterns and appropriateness.

**A. Extract Tool Configuration**

From YAML frontmatter, extract `tools` field value.

**B. Assess Tool Access Appropriateness**

Based on skill type and tools:

**Knowledge Skills (Read-only recommended)**:
- If tools = `[Read]` or `[Read, Grep, Glob]` → ✅ Appropriate
- If tools includes `Write`, `Edit`, `Bash` → ⚠️ Warning (verify intentional)
- If tools is empty/not specified → ℹ️ Inherits all tools

**Active Skills (May need write access)**:
- Skills that generate code → Write/Edit access reasonable
- Skills that run builds → Bash access reasonable
- Skills that create files → Write access reasonable

**C. Report Findings**

Display:
```
Tool Restrictions Review:
✅ Read-only access appropriate for knowledge skill
  Tools: [Read, Grep, Glob]
⚠️  Skill has Write/Edit access - verify this is intentional
  Tools: [Read, Write, Edit, Bash, Grep, Glob]
  Recommendation: Knowledge skills should typically be read-only
ℹ️  No tool restrictions specified (inherits all tools)
  Recommendation: Consider restricting to [Read] for knowledge skills
```

Update statistics: Increment `tool_warnings` for each ⚠️ issue.

#### Step 3.7: Analyze Cross-References

Find relationships between this skill and other components.

**A. Find Agent References**

Search all agent files for references to this skill:

```bash
# Search in project agents
grep -r "skill.*<skill-name>" .claude/agents/ 2>/dev/null

# Search in global agents
grep -r "skill.*<skill-name>" claude/agents/ 2>/dev/null
```

Count agents that reference this skill.

**B. Find Skill-to-Skill References**

Search this skill's SKILL.md for references to other skills:

```bash
grep -E "skill.*cui-[a-z-]+" <skill-path>/SKILL.md
```

Count other skills referenced by this skill.

**C. Detect Integration Issues**

Report potential issues:
- Unused skills (not referenced by any agent) → ℹ️ Information
- Circular dependencies (skill-a → skill-b → skill-a) → ⚠️ Warning
- Broken skill references (references non-existent skill) → ❌ Critical

**D. Report Findings**

Display:
```
Cross-References Analysis:
✅ Referenced by 3 agents:
  - maven-project-builder (claude/agents/maven-project-builder.md)
  - code-reviewer (claude/agents/code-reviewer.md)
  - test-generator (claude/agents/test-generator.md)
✅ References 0 other skills (no dependencies)
⚠️  Not referenced by any agents (unused skill?)
  Recommendation: Consider if this skill is still needed
❌ References non-existent skill: cui-fake-skill
  Fix: Update SKILL.md to reference valid skill
ℹ️  Part of skill chain: cui-java-core → cui-java-unit-testing
```

#### Step 3.8: Validate Content Quality

Perform content and workflow quality checks.

**A. Check Workflow Structure**

Verify SKILL.md contains clear workflow:
- Look for "## Workflow" or "## Usage" section
- Check for numbered steps
- Verify Read instructions are present and clear
- Check for conditional loading logic (if applicable)

**B. Check for Common Issues**

Scan for common quality problems:
- Broken markdown links `[text](url)` where url doesn't resolve
- Code blocks without language tags (should be ` ```language`)
- Excessive length (skills > 500 lines may be too complex)
- Missing examples or patterns section

**C. Report Findings**

Display:
```
Content Quality Review:
✅ Workflow section present with clear steps
✅ Conditional loading logic well-documented
✅ Code blocks use proper language tags (java, bash, yaml)
✅ Reasonable length (288 lines)
⚠️  No examples section found
  Recommendation: Add examples for common use cases
⚠️  Workflow section missing
  Recommendation: Add clear step-by-step usage instructions
```

#### Step 3.8A: Verify Integrated Content Coherence

**CRITICAL**: Validate the complete integrated content when all standards are loaded together.

This step ensures the skill provides a coherent, non-conflicting, unambiguous information-set suitable for AI consumption.

**A. Load All Referenced Standards**

Read all standards files referenced in SKILL.md workflow:

```bash
# Extract all Read: standards/ lines from SKILL.md
grep "Read: standards/" <skill-path>/SKILL.md | awk '{print $2}'

# Read each file
for file in <standards-files>; do
  cat "<skill-path>/$file"
done
```

Store complete integrated content in memory for analysis.

**B. Analyze for Duplication**

Search for duplicate information across standards files:

1. **Extract key requirements** from each file:
   - Look for "must", "should", "shall" statements
   - Identify patterns, rules, and guidelines
   - Extract code examples and templates

2. **Detect duplicates**:
   - Same requirement stated in multiple files
   - Identical code examples repeated
   - Overlapping explanations of same concept

3. **Categorize duplication**:
   - ❌ **Harmful duplication**: Exact same content in multiple files (maintenance burden)
   - ⚠️ **Redundant duplication**: Similar content stated differently (confusing)
   - ✅ **Acceptable reference**: One file references another for details (cross-reference)

**Example findings**:
```
Duplication Analysis:
❌ Harmful: "Logger declaration pattern" duplicated in 3 files
  - standards/logging-standards.md:45-50
  - standards/java-core-patterns.md:120-125
  - standards/testing-junit-core.md:89-94
  Recommendation: Keep in logging-standards.md only, cross-reference from others

⚠️ Redundant: Null-safety requirements stated differently
  - standards/java-null-safety.md: "Never return @Nullable"
  - standards/java-core-patterns.md: "Avoid null returns, use Optional"
  Recommendation: Align language to avoid confusion
```

**C. Detect Conflicts**

Search for contradictory requirements:

1. **Compare requirements across files**:
   - Look for conflicting "must" statements
   - Identify incompatible patterns
   - Find contradictory best practices

2. **Common conflict types**:
   - File A says "always use X", File B says "prefer Y over X"
   - File A requires pattern P, File B forbids pattern P
   - File A says "mandatory", File B says "optional"

3. **Report conflicts**:
   - ❌ **Critical conflict**: Direct contradiction (cannot both be true)
   - ⚠️ **Contextual conflict**: True in different contexts but unclear when (ambiguous)
   - ℹ️ **False conflict**: Appears contradictory but actually compatible (clarify)

**Example findings**:
```
Conflict Detection:
❌ Critical: Lombok @Value usage contradicts immutability pattern
  - standards/java-lombok-patterns.md:67: "Use @Value for immutable objects"
  - standards/java-core-patterns.md:134: "Prefer records over Lombok annotations"
  Resolution: Clarify when to use each (records for simple, @Value for complex)

⚠️ Contextual: Exception handling guidance unclear
  - standards/java-core-patterns.md: "Catch specific exceptions"
  - standards/logging-standards.md: "Catch broad exceptions at boundaries"
  Resolution: Specify contexts (internal vs API boundaries)
```

**D. Check for Ambiguities**

Identify vague or unclear requirements:

1. **Ambiguity types**:
   - Vague quantities: "some", "many", "few", "several"
   - Unclear conditions: "when appropriate", "if needed", "sometimes"
   - Undefined terms: Technical terms without definitions
   - Missing criteria: "should be good", "must be sufficient"

2. **Scan for ambiguous language**:
   ```bash
   # Search for vague terms in standards files
   grep -E "(some|many|few|several|appropriate|when needed|sometimes|often|usually)" <standards-files>
   ```

3. **Assess precision**:
   - ❌ **Too vague**: Cannot determine what to do (unusable)
   - ⚠️ **Needs clarification**: Understandable with context but could be clearer
   - ✅ **Precise**: Clear, specific, actionable guidance

**Example findings**:
```
Ambiguity Detection:
❌ Too vague: "Methods should be reasonably short"
  - standards/java-core-patterns.md:78
  Fix: "Methods should be < 50 lines (recommended), < 100 lines (maximum)"

⚠️ Needs clarification: "Use generators when appropriate"
  - standards/testing-generators.md:23
  Fix: "Use generators for all test data (mandatory), except: [list exceptions]"

✅ Precise: "Minimum 80% line coverage, 80% branch coverage"
  - standards/testing-junit-core.md:156
```

**E. Validate Coherence**

Assess how well standards work together:

1. **Check information flow**:
   - Does SKILL.md workflow make sense?
   - Are standards loaded in logical order?
   - Do later standards build on earlier ones?
   - Is conditional loading justified?

2. **Check completeness**:
   - Are all aspects of domain covered?
   - Are there gaps between standards?
   - Do standards overlap appropriately?

3. **Check usability**:
   - Can an AI understand and apply these standards?
   - Are examples comprehensive enough?
   - Is guidance actionable?
   - Are prerequisites clear?

**Example findings**:
```
Coherence Validation:
✅ Logical loading order: Core patterns → Null safety → Lombok → Modern features
✅ Progressive disclosure: Essential patterns always loaded, specialized contexts conditional
✅ Comprehensive coverage: All Java development aspects covered
⚠️ Gap detected: No guidance on dependency injection setup
  Recommendation: Add section in java-core-patterns.md or create separate standard
✅ Highly usable: Clear examples, specific rules, actionable guidance
```

**F. Calculate Integrated Content Score**

Score the integrated content quality:

```
Integrated Content Score:
- Duplication: Low (3 issues) → 85/100
- Conflicts: None detected → 100/100
- Ambiguities: Low (2 issues) → 90/100
- Coherence: High → 95/100
- Usability: High → 95/100

OVERALL SCORE: 93/100 (Excellent)
```

**Scoring criteria**:
- **90-100**: Excellent - Ready for production use
- **75-89**: Good - Minor improvements needed
- **60-74**: Fair - Moderate improvements required
- **Below 60**: Poor - Major rework needed

**G. Report Integrated Content Findings**

Display comprehensive report:

```
Integrated Content Verification:

✅ Total Standards: 6 files, 68,424 bytes
✅ Integrated View: 1,485 content lines

Duplication Analysis:
✅ Low duplication (3 instances)
  - Minor: Logger pattern mentioned in 2 files (acceptable cross-reference)
  - Recommendation: No action needed

Conflict Detection:
✅ No conflicts detected
  - All requirements consistent across standards
  - Contextual differences clearly explained

Ambiguity Check:
✅ Highly precise (2 minor ambiguities)
  ⚠️ "reasonably short" methods (line 78) - recommend: add specific line count
  ⚠️ "when appropriate" generators (line 23) - recommend: specify mandatory vs optional

Coherence Assessment:
✅ Excellent integration
  - Logical loading order
  - Progressive disclosure effective
  - Comprehensive domain coverage
  - No gaps detected

Usability Evaluation:
✅ Highly usable for AI consumption
  - Clear, actionable guidance
  - Comprehensive code examples
  - Specific requirements with criteria
  - Well-structured workflow

INTEGRATED CONTENT SCORE: 93/100 (Excellent)

This skill provides a coherent, non-conflicting, unambiguous information-set
highly suitable for AI-driven development tasks.
```

Update statistics:
- `content_duplication_issues`: Count of duplication problems
- `content_conflicts`: Count of conflicting requirements
- `content_ambiguities`: Count of ambiguous statements
- `integrated_content_score`: Overall quality score (0-100)

#### Step 3.9: Generate Issue Report

Categorize all issues found:

**CRITICAL Issues (Must Fix):**
- Missing SKILL.md file
- Invalid YAML frontmatter (syntax errors, missing required fields)
- Broken standards references (file not found)
- Absolute paths in references (not portable)
- Broken cross-references to non-existent skills
- **Harmful content duplication** across standards files (maintenance burden)
- **Critical content conflicts** (contradictory requirements)
- **Too vague requirements** (unusable, cannot determine action)

**Warnings (Should Fix):**
- SKILL.md naming issues (skill.md instead of SKILL.md)
- Tool access concerns (Write/Edit access for knowledge skills)
- Missing recommended documentation (README.md)
- Unused skill (not referenced by agents)
- Missing workflow section
- **Redundant duplication** (similar content stated differently)
- **Contextual conflicts** (unclear when each applies)
- **Ambiguous requirements** (needs clarification)
- **Content gaps** (missing domain coverage)
- **Low integrated content score** (< 75/100)

**Suggestions (Nice to Have):**
- Add templates/ or examples/ directory
- Add more comprehensive description
- Consider adding VALIDATION.md report
- Add cross-references to related skills
- **Improve content precision** (remove vague language)
- **Add more code examples** (enhance usability)
- **Enhance documentation** (better explanations)

Display categorized report:
```
Issue Report for <skill-name>:

CRITICAL (2 issues):
1. standards/missing-file.md: Referenced file not found
   Impact: Skill will fail to load standards
   Fix: Create missing file or remove reference

2. YAML frontmatter: Missing required field 'description'
   Impact: Skill cannot be activated by context matching
   Fix: Add description field with clear skill purpose

WARNINGS (3 issues):
1. Tool access: Write permission for knowledge skill
   Impact: Unnecessary privileges, security concern
   Fix: Change tools to [Read, Grep, Glob]

2. Not referenced by any agents
   Impact: Skill is unused, maintenance burden
   Fix: Reference from agents or remove skill

3. Missing README.md
   Impact: No usage documentation for users
   Fix: Add README.md with skill description and examples

SUGGESTIONS (2 items):
1. Consider adding examples/ directory with working code samples
2. Add VALIDATION.md report documenting zero information loss

Total: 7 issues found
```

#### Step 3.10: Decision Point - Fix Issues?

**If NO issues found:**
- Display: "✅ Skill is well-formed and properly integrated - No issues found"
- Continue to next skill

**If issues found:**

Display:
```
Found <count> issues in <skill-name>:
- Critical: <count>
- Warnings: <count>
- Suggestions: <count>

Options:
F - Fix all issues automatically
R - Review each issue individually before fixing
S - Skip this skill (do not fix)
Q - Quit analysis entirely

Please choose [F/r/s/q]:
```

**If user responds:**
- `F` or `f` → Fix all issues automatically (Step 3.11)
- `R` or `r` → Review each issue individually (Step 3.12)
- `S` or `s` → Skip this skill, move to next
- `Q` or `q` → Stop analysis, exit command

#### Step 3.11: Auto-Fix All Issues

For each issue, apply the fix automatically:

**For YAML frontmatter issues:**
1. If missing `---` delimiters → Add proper YAML frontmatter structure
2. If missing required field → Add field with placeholder (ask user to complete)
3. If invalid syntax → Fix indentation and format
4. Display: "✅ Fixed: Added missing YAML frontmatter"

**For standards reference issues:**
1. If broken reference → Offer to remove reference or create placeholder file
2. If absolute path → Convert to relative path (strip user home directory)
3. Display: "✅ Fixed: Converted absolute paths to relative"

**For structure issues:**
1. If SKILL.md has wrong name → Rename to proper case
2. If missing README.md → Create basic README template
3. Display: "✅ Fixed: Renamed skill.md to SKILL.md"

**For tool access issues:**
1. If knowledge skill has Write access → Change to [Read, Grep, Glob]
2. Display: "✅ Fixed: Restricted tool access to read-only"

**For WARNINGS and SUGGESTIONS:**
- Skip suggestions in auto-fix mode
- Apply warnings only if deterministic fix available
- Display: "ℹ️ Skipped <count> suggestions and manual-review warnings"

After fixing:
```
Auto-Fix Complete:
- Critical issues fixed: <count>
- Warnings fixed: <count>
- Remaining issues: <count>
```

Continue to Step 3.13 (Verification)

#### Step 3.12: Review and Fix Individually

For EACH issue (in order: Critical → Warnings → Suggestions):

Display:
```
Issue <number> of <total>:
Severity: <CRITICAL/WARNING/SUGGESTION>
Category: <YAML/Standards/Structure/Tools/Cross-refs>
Problem: <description>

Current Code/State:
<show relevant content with context>

Proposed Fix:
<describe the fix or show the replacement>

Options:
Y - Apply this fix
N - Skip this issue
E - Edit fix (provide alternative)
Q - Stop reviewing, skip remaining issues

Please choose [Y/n/e/q]:
```

**If user responds:**
- `Y` or `y` → Apply the fix, continue to next issue
- `N` or `n` → Skip this issue, continue to next issue
- `E` or `e` → Ask for user's alternative fix, apply it, continue
- `Q` or `q` → Stop reviewing, move to Step 3.13

After review:
```
Review Complete:
- Issues fixed: <count>
- Issues skipped: <count>
- Remaining: <count>
```

Continue to Step 3.13 (Verification)

#### Step 3.13: Verify Fixes

If any fixes were applied:

1. Re-read the SKILL.md file and all standards files
2. Re-run analysis (Steps 3.3 through 3.8A - including integrated content verification)
3. Compare before/after:
   ```
   Verification Results:
   - Issues before: <old_count>
   - Issues after: <new_count>
   - Issues fixed: <fixed_count>
   - New issues introduced: <new_count - (old_count - fixed_count)>
   ```

4. If new issues introduced:
   - Display: "⚠️ WARNING: Fixes introduced <count> new issues"
   - Offer to revert: "Revert changes? [y/N]:"

5. Update statistics:
   - `skills_fixed++`
   - `issues_fixed += <count>`

#### Step 3.14: Display Skill Summary

```
Summary for <skill-name>:
- Initial issues: <count>
- Issues fixed: <count>
- Remaining issues: <count>
- Status: ✅ Clean / ⚠️ Has warnings / ❌ Has critical issues
```

### Step 4: Generate Final Report

After processing all skills, display comprehensive summary:

```
==================================================
Skill Doctor - Analysis Complete
==================================================

Skills Analyzed: <total_skills>
- With issues: <skills_with_issues>
- Fixed: <skills_fixed>
- Still have issues: <remaining>

Issue Statistics:
- Total issues found: <total_issues>
- Critical: <critical_count>
- Warnings: <warning_count>
- Suggestions: <suggestion_count>
- Issues fixed: <issues_fixed>

Issue Breakdown by Category:
- YAML frontmatter errors: <yaml_errors>
- Broken standards references: <broken_references>
- Structure issues: <structure_issues>
- Tool restriction warnings: <tool_warnings>
- Content duplication issues: <content_duplication_issues>
- Content conflicts: <content_conflicts>
- Content ambiguities: <content_ambiguities>

Integrated Content Quality:
- Average content score: <avg_integrated_content_score>/100
- Skills with excellent score (>= 90): <skills_excellent_score>
- Skills with good score (75-89): <skills_good_score>
- Skills with fair score (60-74): <skills_fair_score>
- Skills with poor score (< 60): <skills_poor_score> ⚠️

Content Quality Distribution:
  Excellent (90-100): ████████████████████ <skills_excellent_score>
  Good (75-89):       ██████████           <skills_good_score>
  Fair (60-74):       ████                 <skills_fair_score>
  Poor (< 60):        ██                   <skills_poor_score> ⚠️

By Skill:
<for each skill analyzed>
- <skill-name>: <issue_count> issues (<critical>C / <warnings>W / <suggestions>S)
  Status: <Clean/Warnings/Critical>
  Content Score: <score>/100 (<Excellent/Good/Fair/Poor>)
</for each>

Recommendations:
<if critical issues remain>
⚠️  CRITICAL: <count> skills still have critical issues
- <skill-1>: <issue>
- <skill-2>: <issue>
Re-run diagnose-skills on these skills to fix.
</if>

<if content quality issues>
⚠️  CONTENT QUALITY: <count> skills have content quality concerns
- Skills with conflicts: <list> - Fix contradictory requirements
- Skills with harmful duplication: <list> - Consolidate duplicate content
- Skills with poor score (< 60): <list> - Major content rework needed
- Skills with ambiguities: <list> - Clarify vague requirements
</if>

<if all clean and high quality>
✅ All analyzed skills are well-formed, properly integrated, and have excellent content quality!
Average integrated content score: <score>/100
</if>
```

## CRITICAL RULES

- **READ ENTIRE SKILL** before analyzing - context is essential
- **CATEGORIZE ISSUES PROPERLY** - Critical vs Warning vs Suggestion
- **EXPLAIN FIXES CLEARLY** - User should understand why each change is made
- **VERIFY AFTER FIXING** - Always re-analyze to ensure fixes worked
- **PRESERVE INTENT** - Fix structure/consistency but preserve skill's purpose
- **USE EDIT TOOL** - Never rewrite entire files, use targeted edits
- **TRACK STATISTICS** - Maintain counters throughout analysis
- **HANDLE ERRORS** - If skill file is malformed/unreadable, report and skip
- **INTERACTIVE BY DEFAULT** - Ask before making changes unless told otherwise
- **LEARN FROM PATTERNS** - If multiple skills have same issue, mention it in report

## ANALYSIS PATTERNS

Common issues to look for across all skills:

### Pattern 1: YAML Frontmatter Issues

**Problem:** Invalid YAML or missing required fields
**Example:** No `---` delimiters, missing `name` or `description`
**Fix:** Add proper frontmatter structure with required fields

### Pattern 2: Wrong Tool Field Name

**Problem:** Using `tools` instead of `allowed-tools`
**Example:** `tools: [Read, Write]` (WRONG - skills use `allowed-tools`, not `tools`)
**Fix:** Change `tools` to `allowed-tools` in YAML frontmatter

**Correct format:**
```yaml
---
name: skill-name
description: Brief description of what this skill does and when to use it
allowed-tools: [Read, Edit, Write, Bash, Grep, Glob]
---
```

### Pattern 3: Broken Standards References

**Problem:** References to non-existent standards files
**Example:** `Read: standards/missing-file.md`
**Fix:** Create missing file or remove reference

### Pattern 4: Absolute Paths

**Problem:** Hardcoded absolute paths to standards
**Example:** `Read: ~/git/cui-llm-rules/standards/file.md`
**Fix:** Convert to relative path: `Read: standards/file.md`

### Pattern 5: Missing Primary File

**Problem:** SKILL.md doesn't exist or has wrong case
**Example:** `skill.md` or `Skill.md` instead of `SKILL.md`
**Fix:** Rename file to proper case

### Pattern 6: Excessive Tool Access

**Problem:** Knowledge skill has Write/Edit/Bash access
**Example:** `tools: [Read, Write, Edit, Bash]` for documentation skill
**Fix:** Restrict to `tools: [Read, Grep, Glob]`

### Pattern 7: Unused Skills

**Problem:** Skill not referenced by any agents
**Example:** Skill exists but no agent uses it
**Fix:** Either reference from agents or consider removing

### Pattern 8: Missing Workflow

**Problem:** No clear usage instructions in SKILL.md
**Example:** Only frontmatter and standards list, no workflow section
**Fix:** Add "## Workflow" section with step-by-step instructions

### Pattern 9: Circular Dependencies

**Problem:** Skills reference each other in a loop
**Example:** skill-a references skill-b, skill-b references skill-a
**Fix:** Restructure skill relationships to be acyclic

### Pattern 10: Inconsistent Naming

**Problem:** Skill directory name doesn't match frontmatter `name`
**Example:** Directory: `cui-java-core`, YAML name: `CUI Java Standards`
**Fix:** Align naming (directory = kebab-case, YAML name = Title Case)

### Pattern 11: Harmful Content Duplication

**Problem:** Same content repeated across multiple standards files
**Example:** Logger declaration pattern in logging-standards.md, java-core-patterns.md, and testing-junit-core.md
**Fix:** Keep content in one authoritative file, add cross-references from others

### Pattern 12: Content Conflicts

**Problem:** Contradictory requirements in different standards
**Example:** One file says "always use X", another says "never use X"
**Fix:** Resolve conflict by clarifying contexts or unifying guidance

### Pattern 13: Ambiguous Requirements

**Problem:** Vague language that doesn't provide clear guidance
**Example:** "Methods should be reasonably short", "Use when appropriate"
**Fix:** Replace with specific criteria: "Methods < 50 lines (recommended)", "Use for all test data (mandatory)"

### Pattern 14: Content Gaps

**Problem:** Important topics missing from standards coverage
**Example:** Skill covers Java but no guidance on dependency injection
**Fix:** Add missing section or create new standards file for gap

### Pattern 15: Poor Integrated Score

**Problem:** Overall content quality below acceptable threshold (< 75/100)
**Example:** Multiple duplications, conflicts, ambiguities, and gaps
**Fix:** Systematic content review and refinement across all standards

## BEST PRACTICES FOR WELL-FORMED SKILLS

A well-formed skill should have:

### Structural Requirements
1. **Valid YAML Frontmatter** - Proper syntax with required fields
2. **Clear Description** - Describes when and why to use this skill
3. **Appropriate Tool Access** - Minimal necessary tools
4. **Primary SKILL.md File** - Properly named and structured
5. **Valid Standards References** - All referenced files exist
6. **Relative Paths Only** - No absolute paths
7. **Clear Workflow** - Step-by-step usage instructions
8. **Supporting Documentation** - README.md for users
9. **Self-Contained Standards** - No broken cross-references
10. **Proper Integration** - Referenced by agents, references valid skills
11. **Consistent Structure** - Follows skill directory conventions

### Content Quality Requirements (NEW)
12. **No Harmful Duplication** - Avoid repeating content across standards files
13. **No Conflicts** - Ensure consistent requirements across all standards
14. **Precise Requirements** - Use specific, measurable criteria instead of vague terms
15. **Complete Coverage** - Cover all important aspects of the domain
16. **High Coherence** - Standards should work together logically
17. **Excellent Usability** - Clear, actionable guidance with comprehensive examples
18. **Integrated Content Score >= 75** - Minimum acceptable quality threshold
19. **Target Score >= 90** - Excellent quality for production use

## USAGE EXAMPLES

### Analyze All Project Skills
```
/diagnose-skills project
```

### Analyze All Global Skills
```
/diagnose-skills global
```

### Analyze Specific Skill
```
/diagnose-skills cui-java-core
/diagnose-skills cui-java-unit-testing
```

### Interactive Mode
```
/diagnose-skills
[Select from menu]
```

## ERROR HANDLING

**If skill directory not found:**
```
❌ ERROR: Skill '<name>' not found
Searched in:
- .claude/skills/
- claude/marketplace/skills/

Available skills: <list>
```

**If SKILL.md is malformed:**
```
⚠️ WARNING: Skill '<name>' could not be parsed
Error: <description>

Options:
V - View file contents
S - Skip this skill
Q - Quit analysis

Please choose [V/s/q]:
```

**If fixes introduce errors:**
```
⚠️ WARNING: Fixes to '<name>' introduced new issues:
- <issue 1>
- <issue 2>

Options:
R - Revert all changes
K - Keep changes anyway
M - Manually review and fix

Please choose [R/k/m]:
```

## INTEGRATION WITH OTHER COMMANDS

This command helps maintain quality of skills used by:
- Agents that reference skills for standards enforcement
- Other commands that rely on skill availability
- Plugin distribution and marketplace integration

Run `diagnose-skills` periodically to:
- After creating new skills
- After major updates to existing skills
- When skills seem to load incorrectly
- As part of plugin release preparation

## NOTES

- This command analyzes skill STRUCTURE and INTEGRATION
- It does NOT test skill FUNCTIONALITY (that requires agent testing)
- For functionality testing, invoke skills via agents and test behavior
- diagnose-skills focuses on: structure, references, configuration, integration
- Always backup important skills before fixing (use version control)
