---
name: cui-create-skill
description: Guide users through creating a new well-structured skill with standards organization and proper configuration
---

# Skill Creation Wizard

Guide users through creating a new, well-structured skill following architectural best practices and standards organization principles.

## PARAMETERS

- **scope=marketplace** (default): Create skill in marketplace bundle (~/git/cui-llm-rules/claude/marketplace/bundles/)
- **scope=global**: Create skill in global location (~/.claude/skills/)
- **scope=project**: Create skill in project location (.claude/skills/)

## PARAMETER VALIDATION

**If `scope=marketplace` (default):**
- Work in: `~/git/cui-llm-rules/claude/marketplace/bundles/`
- Prompt for bundle name (or create new bundle)
- Skill directory location: `~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/skills/{skill_name}/`

**If `scope=global`:**
- Work in: `~/.claude/skills/`
- No bundle structure (flat directory)
- Skill directory location: `~/.claude/skills/{skill_name}/`

**If `scope=project`:**
- Work in: `.claude/skills/`
- No bundle structure (flat directory)
- Skill directory location: `.claude/skills/{skill_name}/`

## WORKFLOW INSTRUCTIONS

### Step 1: Display Welcome and Overview

Display:
```
╔════════════════════════════════════════════════════════════╗
║              Skill Creation Wizard                         ║
╔════════════════════════════════════════════════════════════╝
║
║ This wizard will guide you through creating a new skill
║ with proper structure, standards organization, and
║ appropriate tool restrictions.
║
║ You'll answer questions about:
║ - Skill location and basic info
║ - Skill purpose and domain
║ - Tool access requirements (CRITICAL: skills use allowed-tools)
║ - Standards file organization
║ - Content structure
║ - Integration with agents
║
║ Let's begin!
║
╚════════════════════════════════════════════════════════════

Ready to start? Enter 'y' to continue:
```

Wait for user acknowledgment (any input will proceed).

### Step 2: Collect Basic Information

#### Step 2.1: Determine Scope and Location

Parse the `scope` parameter (defaults to "marketplace"):

**If scope=marketplace:**
- Set `location` = "marketplace"
- Set `base_path` = "~/git/cui-llm-rules/claude/marketplace/bundles/"
- Prompt for bundle name:
  ```
  Which bundle should contain this skill?

  Existing bundles:
  - cui-utility-commands (project utilities)
  - cui-plugin-development-tools (plugin/command/agent creation)
  - cui-pull-request-workflow (PR management)
  - cui-issue-implementation (issue planning and implementation)
  - cui-documentation-standards (documentation review)
  - cui-project-quality-gates (build and quality checks)

  Enter bundle name or "new" to create a new bundle:
  ```
  Store response as `bundle_name`.

**If scope=global:**
- Set `location` = "global"
- Set `base_path` = "~/.claude/skills/"
- No bundle (flat structure)
- Set `bundle_name` = "" (empty)

**If scope=project:**
- Set `location` = "project"
- Set `base_path` = ".claude/skills/"
- No bundle (flat structure)
- Set `bundle_name` = "" (empty)

#### Step 2.2: Skill Name

```
[Question 1/8] What is the skill name?

- Use lowercase with hyphens (e.g., cui-java-core, cui-documentation)
- Should be descriptive and domain-specific
- Must be unique (not conflict with existing skills)
- Will be used as directory name: {skill_name}/
- Recommended prefix: "cui-" for CUI marketplace skills

Skill name:
```

Store response as `skill_name`.
Validate: No spaces, lowercase, hyphens only, doesn't already exist.

#### Step 2.3: Skill Description

```
[Question 2/8] Provide a clear description of the skill.

CRITICAL: This description is used for context matching by Claude Code.
It should describe BOTH:
1. WHAT the skill does
2. WHEN to use it

Good example:
"Core Java development standards for CUI projects including coding patterns,
null safety, Lombok, modern features, DSL constants, and logging"

Bad example:
"Java standards" (too vague, no context)

Your description (50-200 characters recommended):
```

Store response as `description`.
Validate: Length 50-200 characters (warn if outside range).

#### Step 2.4: Skill Type and Tool Access

```
[Question 3/8] What type of skill is this?

1. Knowledge Skill (read-only)
   - Provides standards, patterns, and guidelines
   - AI reads and applies the knowledge
   - Recommended tools: [Read, Grep, Glob]
   - Examples: cui-java-core, cui-documentation

2. Active Skill (may need write access)
   - Generates code, creates files, runs commands
   - AI actively modifies the codebase
   - May need tools: [Read, Write, Edit, Bash, Grep, Glob]
   - Examples: code generation, automated refactoring

Enter 1 or 2:
```

Store response as `skill_type`.

**Based on skill_type, set default tools:**
- If knowledge (1): `allowed_tools` = [Read, Grep, Glob]
- If active (2): Prompt for specific tools needed

**If active (2), ask follow-up:**
```
Which tools will this skill need?

Available tools:
- Read (read files)
- Write (create new files)
- Edit (modify existing files)
- Bash (run shell commands)
- Grep (search content in files)
- Glob (find files by pattern)
- WebFetch (fetch web content - rare for skills)

Enter as comma-separated list (e.g., "Read, Write, Edit, Bash"):
```

Store response as `allowed_tools`.

**CRITICAL REMINDER:**
Display:
```
⚠️  IMPORTANT: Skills use 'allowed-tools' NOT 'tools' in YAML frontmatter!
   This is different from agents which use 'tools'.
```

### Step 3: Standards Organization

#### Step 3.1: Standards Files

```
[Question 4/8] Will this skill include standards files?

Skills typically include one or more standards files in a standards/ subdirectory.

1. Yes - I'll provide standards files
2. No - This skill won't have standards files (rare)

Enter 1 or 2:
```

Store response as `include_standards`.

**If yes (1), collect standards file information:**

```
How many standards files will this skill have?

Recommendation: 3-6 files covering different aspects of the domain.
- Too few (1-2): Consider if this needs to be a skill
- Too many (>10): Consider splitting into multiple skills

Enter number:
```

Store response as `standards_count`.

**For EACH standards file (1 to standards_count):**

```
Standards File #{n}:

File name (without .md extension):
Examples: "java-core-patterns", "testing-junit-core", "logging-standards"
```

Store as `standards_files[n].name`.

```
File description (what does this file cover?):
Example: "Core Java coding patterns including naming, structure, and best practices"
```

Store as `standards_files[n].description`.

```
Estimated content size:
1. Small (50-150 lines)
2. Medium (150-350 lines)
3. Large (350+ lines)

Enter 1, 2, or 3:
```

Store as `standards_files[n].size`.

```
Add another standards file?
1. Yes
2. No

Enter 1 or 2:
```

### Step 4: Skill Workflow Design

#### Step 4.1: Loading Strategy

```
[Question 5/8] How should standards be loaded?

1. Load All (simple)
   - All standards loaded when skill is activated
   - Best for: Small skills with always-needed content
   - Example: "Read all 3 standards files"

2. Conditional Loading (advanced)
   - Load different standards based on context
   - Best for: Complex skills with optional content
   - Example: "Read core patterns always, load testing patterns only if test context detected"

Enter 1 or 2:
```

Store response as `loading_strategy`.

**If conditional (2), ask follow-up:**

For each standards file:
```
Standards File: {file_name}

Loading condition:
1. Always load (core/essential)
2. Conditional (specify condition)

Enter 1 or 2:
```

If conditional:
```
What condition triggers loading this file?
Examples:
- "If processing test files"
- "If @Deprecated annotation detected"
- "If build.gradle present"

Your condition:
```

Store as `standards_files[n].loading_condition`.

#### Step 4.2: Workflow Steps

```
[Question 6/8] Describe the skill workflow

When this skill is activated, what should happen?
Provide step-by-step instructions for Claude.

Example:
1. Read core Java patterns from standards/java-core-patterns.md
2. Read null safety rules from standards/java-null-safety.md
3. If Lombok is detected, read standards/java-lombok-patterns.md
4. Apply patterns during code review or generation

Your workflow:
```

Store response as `workflow_description`.

### Step 5: Integration and Documentation

#### Step 5.1: Agent Integration

```
[Question 7/8] Which agents should use this skill?

List agents that should reference this skill (or "none" if unsure):
Examples:
- maven-project-builder
- code-reviewer
- test-generator

Agents (comma-separated):
```

Store response as `target_agents`.

#### Step 5.2: Additional Documentation

```
[Question 8/8] Additional documentation to include?

1. README.md (recommended) - User-facing usage guide
2. VALIDATION.md (optional) - Quality assessment report
3. Both
4. Neither

Enter 1, 2, 3, or 4:
```

Store response as `additional_docs`.

### Step 5A: Enforce Architecture Compliance

**CRITICAL**: Ensure skill will follow marketplace architecture rules from the start.

**Invoke Architecture Skill**:
```
Skill: cui-marketplace-architecture
```

This loads architecture rules and validation patterns for marketplace components.

Display architecture requirements:
```
╔════════════════════════════════════════════════════════════╗
║     CRITICAL: Skill Architecture Requirements              ║
╔════════════════════════════════════════════════════════════╝

Your skill MUST be self-contained to be marketplace-ready.

Apply rules from loaded standards (architecture-rules.md):

## Rule 1: Self-Containment

ALL standards content must be in your skill's standards/ directory.

✅ CORRECT file references in SKILL.md:
   Read: standards/java-core-patterns.md
   Read: standards/testing/junit-patterns.md
   Skill: cui-other-skill

❌ PROHIBITED file references:
   Read: ../../../../standards/java/java-core.adoc
   Read: ~/git/cui-llm-rules/standards/logging.adoc
   Read: ../../doc/architecture.adoc

## Why Self-Containment Matters

When your skill is distributed:
- Global install: ~/.claude/skills/{skill_name}/
- Marketplace: Downloaded independently
- Project: .claude/skills/{skill_name}/

External file paths BREAK in all these scenarios!

## Reference Patterns Allowed

From loaded standards (reference-patterns.md):

1. Internal Files (within skill directory):
   Format: Read: standards/filename.md
   Example: Read: standards/java-core-patterns.md

2. External URLs (public documentation):
   Format: https://example.com/docs
   Example: * Java Spec: https://docs.oracle.com/javase/specs/

3. Skill Dependencies (other skills):
   Format: Skill: cui-skill-name
   Example: Skill: cui-java-unit-testing

## What This Means for You

As you create standards files:
1. ALL content goes in {skill_name}/standards/
2. Use ONLY relative paths: standards/filename.md
3. NO paths escaping skill directory (no ../..)
4. NO absolute paths (no ~/ or /full/path)
5. External docs via URLs only

## Compliance Checklist

Before creating skill, confirm:
- [ ] All standards content will be in standards/ directory
- [ ] You understand: no external file paths allowed
- [ ] You will use: Read: standards/filename.md format
- [ ] You will NOT use: ../../../../ or ~/ paths

╚════════════════════════════════════════════════════════════

Ready to proceed with these architecture rules in mind? [Y/n]:
```

Wait for user acknowledgment.

**If user enters 'n':**
```
Architecture rules are MANDATORY for marketplace skills.

Options:
1. Review architecture documentation
2. Continue anyway (skill will fail validation)
3. Cancel skill creation

Enter 1, 2, or 3:
```

**If option 1 (Review):**
Display key sections from loaded architecture-rules.md and reference-patterns.md.
Then ask if ready to proceed.

**If option 2 (Continue anyway):**
```
⚠️ WARNING: Proceeding without architecture compliance

Your skill WILL FAIL validation if it uses external file references.
You will need to fix architecture violations before marketplace release.

Create non-compliant skill anyway? [y/N]:
```

**If option 3 (Cancel):**
Exit skill creation wizard.

### Step 6: Generate Skill Structure

Based on collected information, create skill directory and files:

#### Step 6.1: Create Directory Structure

**Determine full path:**
- If scope=marketplace: `~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/skills/{skill_name}/`
- If scope=global: `~/.claude/skills/{skill_name}/`
- If scope=project: `.claude/skills/{skill_name}/`

**Create directories:**
```bash
mkdir -p {skill_path}
mkdir -p {skill_path}/standards
```

#### Step 6.2: Generate SKILL.md

**CRITICAL: Use 'allowed-tools' not 'tools'**

Generate SKILL.md with proper structure:

```markdown
---
name: {skill_name}
description: {description}
allowed-tools: {allowed_tools}
---

# {Skill Name Title Case}

{description}

## Purpose

This skill provides {domain-specific purpose based on description}.

## Target Audience

- Agents that {target use case}
- Use cases: {specific scenarios}

## Workflow

### Step 1: Activation

This skill is activated when {activation context}.

### Step 2: Load Standards

{Based on loading_strategy, generate appropriate instructions}

**If loading_strategy = "Load All":**
```
Read all standards files:
1. Read: standards/{file1}.md
2. Read: standards/{file2}.md
3. Read: standards/{file3}.md
```

**If loading_strategy = "Conditional":**
```
Core standards (always load):
- Read: standards/{core_file}.md

Conditional standards:
- If {condition}: Read: standards/{conditional_file}.md
```

### Step 3: Apply Standards

Apply loaded standards to {task description based on workflow_description}.

## Standards Organization

This skill includes {standards_count} standards files:

{For each standards_file:}
### {file_name}.md
{file_description}
- Size: ~{estimated_lines} lines
{If conditional: - Load when: {loading_condition}}

## Tool Access

**Allowed Tools**: {allowed_tools}

{If knowledge skill:}
This is a knowledge skill (read-only access). It provides guidance but does not modify code directly.

{If active skill:}
This is an active skill with write access. It can generate and modify code based on standards.

## Integration

### Target Agents

This skill should be referenced by:
{For each target_agent:}
- {agent_name}

### Usage in Agents

Agents should invoke this skill using:
```markdown
Skill: {skill_name}
```

## Maintenance

### Updating Standards

When standards are updated:
1. Update the relevant standards/*.md file
2. Test with target agents
3. Run /cui-diagnose-skills {skill_name} to verify quality

### Quality Checks

Regularly verify:
- ✅ No content duplication across standards files
- ✅ No conflicting requirements
- ✅ Clear, unambiguous language
- ✅ Comprehensive domain coverage

## Notes

{Any additional notes or special considerations}
```

#### Step 6.3: Create Standards Files

For each standards file in `standards_files`:

Create placeholder file: `{skill_path}/standards/{file_name}.md`

**Template content:**
```markdown
# {File Name Title Case}

{file_description}

## Overview

This file defines standards for {domain aspect}.

## Requirements

### Core Requirements

**MUST** requirements:
- {Placeholder: Add mandatory requirements}
- {Placeholder: Each requirement should be specific and measurable}

**SHOULD** requirements:
- {Placeholder: Add recommended practices}

**MAY** optional:
- {Placeholder: Add optional enhancements}

## Patterns and Examples

### Pattern 1: {Pattern Name}

**Description**: {What this pattern does}

**When to use**: {Context and conditions}

**Example**:
```{language}
// Placeholder code example
```

**Anti-pattern** (avoid):
```{language}
// Placeholder anti-pattern example
```

### Pattern 2: {Pattern Name}

{Repeat structure}

## Common Issues

### Issue 1: {Issue Description}

**Problem**: {What goes wrong}

**Solution**: {How to fix}

**Example**:
```{language}
// Solution example
```

## Checklist

Use this checklist to verify compliance:

- [ ] {Requirement 1}
- [ ] {Requirement 2}
- [ ] {Requirement 3}

## References

- {Link to authoritative source}
- {Link to related documentation}
```

#### Step 6.4: Create README.md (if requested)

If `additional_docs` includes README:

Create: `{skill_path}/README.md`

```markdown
# {Skill Name Title Case}

{description}

## Purpose

This skill provides {expanded purpose}.

## Contents

This skill includes:

{For each standards_file:}
- `standards/{file_name}.md` - {file_description}

## Usage

### For Users

This skill is automatically activated by Claude Code when {context}.

### For Agents

Reference this skill in your agent definition:

```markdown
Skill: {skill_name}
```

### Loading Strategy

{Describe loading_strategy - all at once or conditional}

## Tool Access

**Allowed Tools**: {allowed_tools}

{Explanation of why these tools are needed}

## Maintenance

### Updating Content

To update this skill:
1. Edit the relevant standards/*.md file
2. Maintain clear, specific requirements
3. Include comprehensive examples
4. Run quality checks with /cui-diagnose-skills

### Quality Standards

All content must meet:
- ✅ No duplication across files
- ✅ No conflicting requirements
- ✅ Specific, measurable criteria
- ✅ Comprehensive examples

## Contributing

When adding new standards:
1. Follow existing file structure
2. Use relative paths only (no absolute paths)
3. Include examples for all patterns
4. Test with target agents before committing

## License

{License information if applicable}
```

#### Step 6.5: Create VALIDATION.md (if requested)

If `additional_docs` includes VALIDATION:

Create: `{skill_path}/VALIDATION.md`

```markdown
# Skill Quality Validation Report

**Skill**: {skill_name}
**Validation Date**: {current_date}
**Validator**: Automated (cui-create-skill)

## Validation Methodology

This skill was created using the cui-create-skill wizard, which ensures:
- Proper YAML frontmatter structure
- Correct use of 'allowed-tools' (not 'tools')
- Relative path standards references
- Appropriate tool access restrictions
- Comprehensive documentation

## Structure Validation

✅ SKILL.md present with valid YAML frontmatter
✅ Standards directory created: standards/
✅ {standards_count} standards files created
✅ README.md documentation included
✅ Proper directory structure

## YAML Frontmatter

```yaml
name: {skill_name}
description: {description}
allowed-tools: {allowed_tools}
```

✅ Uses 'allowed-tools' (correct for skills)
✅ Description is clear and specific
✅ Tool restrictions appropriate for skill type

## Standards Organization

Total standards files: {standards_count}

{For each standards_file:}
- `standards/{file_name}.md`
  - Status: ✅ Created
  - Size: Placeholder (needs content)
  - Purpose: {file_description}

## Content Quality Assessment

⚠️ **Placeholder Content**: Standards files contain template placeholders.
Next steps:
1. Fill in actual standards content
2. Add comprehensive examples
3. Test with target agents
4. Run /cui-diagnose-skills for full validation

## Tool Access Validation

**Skill Type**: {skill_type}
**Allowed Tools**: {allowed_tools}

{If knowledge_skill:}
✅ Read-only tools appropriate for knowledge skill
✅ No unnecessary write permissions

{If active_skill:}
✅ Write permissions justified by skill purpose
⚠️ Ensure write operations are safe and controlled

## Integration Validation

**Target Agents**: {target_agents}

Next steps:
1. Update target agents to reference this skill
2. Test skill activation in agent workflows
3. Verify standards are loaded correctly

## Zero Information Loss

This skill was created with:
- ✅ All user inputs captured
- ✅ Workflow logic preserved
- ✅ Integration requirements documented
- ✅ Maintenance guidance included

## Recommendations

### Immediate Actions
1. ✅ Skill structure created
2. ⚠️ Add content to standards files
3. ⚠️ Test with at least one agent
4. ⚠️ Run /cui-diagnose-skills {skill_name}

### Quality Improvements
- Add more comprehensive examples to standards files
- Include common pitfalls and anti-patterns
- Add checklists for compliance verification
- Document integration patterns with specific agents

## Compliance Score

**Structure**: 100% (all required files created)
**Content**: 0% (placeholder content only)
**Integration**: 0% (not yet integrated with agents)

**Overall**: 33% - Requires content development

After filling in standards content and integrating with agents, re-run:
```
/cui-diagnose-skills {skill_name}
```

This will provide full content quality analysis including:
- Duplication detection
- Conflict detection
- Ambiguity analysis
- Coherence assessment
- Integration verification
```

### Step 7: Display Creation Summary

```
╔════════════════════════════════════════════════════════════╗
║          Skill Created Successfully!                       ║
╔════════════════════════════════════════════════════════════╝

Skill: {skill_name}
Location: {full_path}

Structure Created:
✅ SKILL.md ({line_count} lines)
✅ standards/ directory ({standards_count} files)
{If README: ✅ README.md (documentation)}
{If VALIDATION: ✅ VALIDATION.md (quality report)}

Configuration:
- Allowed Tools: {allowed_tools}
- Skill Type: {skill_type}
- Loading Strategy: {loading_strategy}
- Standards Files: {standards_count}

CRITICAL REMINDER:
⚠️  Used 'allowed-tools' (correct for skills, NOT 'tools')

Next Steps:
1. Fill in content for standards/*.md files (currently placeholders)
2. Add comprehensive examples and patterns
3. Test with target agents: {target_agents}
4. Run /cui-diagnose-skills {skill_name} for quality validation

╚════════════════════════════════════════════════════════════
```

### Step 8: Auto-Verify with Skill Doctor

Display:
```
Would you like to run /cui-diagnose-skills now for initial verification?

This will validate:
- YAML frontmatter structure
- Standards file references
- Tool access configuration
- Directory structure

Note: Content quality will be low (placeholder content) until you fill in standards.

Run diagnosis? [Y/n]:
```

If yes:
1. Automatically invoke `/cui-diagnose-skills {skill_name}`
2. Wait for diagnose-skills to complete analysis
3. Display results

**Expected output:**
```
Skill Doctor Analysis Results:

Structure: ✅ Excellent
- YAML frontmatter valid
- Directory structure correct
- All files present

YAML Configuration: ✅ Excellent
- ✅ Uses 'allowed-tools' (correct)
- ✅ Description is clear
- ✅ Tool restrictions appropriate

Standards References: ✅ All valid
- {standards_count} files referenced
- All paths relative (no absolute paths)

Content Quality: ⚠️ Placeholder (0%)
- Standards files contain template placeholders
- Need to add actual content

Recommendations:
1. Fill in standards/*.md content
2. Add comprehensive examples
3. Test with agents
4. Re-run diagnosis after content added
```

### Step 9: Final Completion

```
╔════════════════════════════════════════════════════════════╗
║          Setup Complete!                                   ║
╔════════════════════════════════════════════════════════════╝

Your new skill is ready for content development: {skill_name}

The skill structure follows best practices:
✅ Correct YAML frontmatter with 'allowed-tools'
✅ Proper directory structure
✅ Standards files organized logically
✅ Appropriate tool restrictions
✅ Comprehensive documentation
✅ Verified by cui-diagnose-skills

Location: {full_path}

IMPORTANT - Next Steps:
1. Edit each standards/*.md file to add real content
2. Replace placeholders with actual requirements
3. Add comprehensive code examples
4. Test with target agents
5. Run /cui-diagnose-skills again for content quality analysis

The skill will be automatically discovered by Claude Code once content is added.

Happy skill development! 🚀

╚════════════════════════════════════════════════════════════
```

## CRITICAL RULES

- **ALWAYS use 'allowed-tools' in YAML frontmatter** - Skills use 'allowed-tools', NOT 'tools' (agents use 'tools')
- **ALWAYS use relative paths** - No absolute paths in standards references
- **ALWAYS validate tool restrictions** - Knowledge skills should be read-only
- **ALWAYS create placeholder content** - Don't leave files empty, provide templates
- **ALWAYS run diagnose-skills** after creation to verify structure
- **DEFAULT to marketplace scope** (scope=marketplace is default)
- **VERIFY frontmatter syntax** is valid YAML with name, description, allowed-tools fields
- **CREATE standards/ directory** even if empty (prevents broken references)
- **DOCUMENT loading strategy** clearly in SKILL.md workflow
- **PROVIDE maintenance guidance** in README.md

## LESSONS LEARNED FROM PREVIOUS SESSIONS

### Lesson 1: YAML Frontmatter Field Name
**Issue**: Skills were using 'tools' instead of 'allowed-tools'
**Impact**: Claude Code ignores tool restrictions when wrong field name used
**Solution**: Always use 'allowed-tools' for skills, warn users prominently
**Prevention**: Automated validation in wizard, multiple reminders in UI

### Lesson 2: Absolute vs Relative Paths
**Issue**: Standards references used absolute paths like ~/user/path
**Impact**: Skills break for other users, not portable
**Solution**: Always use relative paths (e.g., standards/file.md)
**Prevention**: Generate all paths relative, validate in diagnose-skills

### Lesson 3: Tool Access Granularity
**Issue**: Knowledge skills had unnecessary write permissions
**Impact**: Security risk, permission bloat
**Solution**: Guide users to minimal necessary tools
**Prevention**: Skill type question drives default tool selection

### Lesson 4: Content Organization
**Issue**: Large monolithic standards files were hard to maintain
**Impact**: Duplication, conflicts, poor modularity
**Solution**: Multiple focused standards files with clear boundaries
**Prevention**: Wizard guides 3-6 file organization pattern

### Lesson 5: Scope Parameter Consistency
**Issue**: Different commands used different parameters (project/global)
**Impact**: Inconsistent user experience
**Solution**: Unified 'scope' parameter across all plugin dev tools
**Prevention**: All create/diagnose commands use same scope pattern

## VALIDATION RULES

Before writing skill files:

1. **Name Validation:**
   - Lowercase only
   - Hyphens for spaces
   - No special characters
   - Unique (doesn't exist)
   - Descriptive and domain-specific
   - Recommended prefix: "cui-"

2. **YAML Frontmatter Validation:**
   - Uses 'allowed-tools' (NOT 'tools')
   - Description 50-200 characters
   - Valid tool names only
   - Proper YAML syntax (spaces, not tabs)

3. **Tool Access Validation:**
   - Knowledge skills: [Read, Grep, Glob] recommended
   - Active skills: Justify Write/Edit/Bash access
   - No unnecessary permissions

4. **Standards Organization Validation:**
   - 3-6 files recommended (not too few, not too many)
   - Clear separation of concerns
   - No overlapping content planned
   - Logical naming convention

5. **Path Validation:**
   - All standards paths relative
   - No ~ or absolute paths
   - Consistent path format

## USAGE

**Create skill in marketplace (default):**
```
/cui-create-skill
/cui-create-skill scope=marketplace
```

**Create global skill:**
```
/cui-create-skill scope=global
```

**Create project-local skill:**
```
/cui-create-skill scope=project
```

The wizard will guide you through all questions and generate a complete skill structure ready for content development.
