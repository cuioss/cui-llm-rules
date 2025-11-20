---
name: plugin-create-skill
description: Guide users through creating a well-structured skill with standards organization and proper configuration
---

# Create Skill Command

Interactive wizard that guides users through creating a new well-structured Claude Code skill following marketplace architecture best practices.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=plugin-create-skill update="[your improvement]"` with:
1. Improved questionnaire patterns for gathering skill requirements
2. Better validation strategies for architecture compliance
3. More effective skill file generation templates
4. Enhanced duplication detection across existing skills
5. Any lessons learned about skill creation workflows

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

**scope** - Where to create skill (marketplace/global/project, default: marketplace)

## WORKFLOW

### Step 1: Welcome and Context

Display welcome message explaining skill creation process.

### Step 2: Collect Basic Information

**A. Skill name** - kebab-case, descriptive (e.g., `java-unit-testing-patterns`)
   - **Validation**: Must not be empty, must match kebab-case pattern
   - **Error**: If invalid: "Skill name must be kebab-case (lowercase-with-hyphens)" and retry

**B. Bundle selection** - List available bundles or create new
   - **Validation**: Must select valid bundle from list
   - **Error**: If invalid selection: "Please select a bundle from the list" and retry

**C. Short description** (1 sentence, <100 chars)
   - **Validation**: Must not be empty, must be ≤100 chars
   - **Error**: If invalid: "Description required (max 100 chars): {current_length}/100" and retry

**D. Detailed description** (2-3 sentences explaining what standards/knowledge skill provides)
   - **Validation**: Must not be empty, must be at least 100 chars
   - **Error**: If too short: "Detailed description must be at least 100 characters: {current_length}/100" and retry

### Step 3: Determine Skill Type

Ask user to select:
1. **Standards skill** - Provides coding/process standards (most common)
2. **Reference skill** - Provides reference material (API docs, examples)
3. **Diagnostic skill** - Provides diagnostic patterns/tools

   - **Validation**: Must select 1-3
   - **Error**: If invalid: "Please select skill type (1-3)" and retry

### Step 4: Collect Standards Information (if standards skill)

**A. Standards categories** - What domains does this cover? (e.g., Java, Testing, Documentation)

**B. Target audience** - Who uses these standards? (developers, documentation writers, etc.)

**C. Standards files** - What standards files will be included?
- Prompt user to list main standards documents
- Suggest organization structure based on categories

### Step 5: Enforce Architecture Compliance and Check Duplication

Load and apply marketplace architecture standards:

```
Skill: cui-plugin-development-tools:cui-marketplace-architecture
```

Verify:
- Self-contained standards (no cross-skill duplication)
- Proper skill usage patterns (Skill tool for standards, not Read)
- Clean reference patterns (xref within skill, Skill across skills)

**Duplication detection:**
1. Use Glob to find all skills in target bundle
2. Use Grep to search for similar skill names or descriptions
3. **If duplicates found**:
   - Display: "⚠️ Similar skills found: {list skill names with descriptions}"
   - Prompt: "[C]ontinue anyway/[R]ename skill/[A]bort creation?"
   - Track in duplication_checks counter

**Error handling:**
- If Glob/Grep fails: Log warning, continue (increment validations_performed with note)

### Step 6: Create Skill Structure

**A. Create directories**:
```
{bundle}/skills/{skill-name}/
{bundle}/skills/{skill-name}/standards/
```

**B. Generate SKILL.md** with:
- YAML frontmatter (name, description, requirements, standards list)
- Overview section
- What This Skill Provides
- When to Activate
- Workflow (how to use standards)
- Standards Organization
- Tool Access requirements

**C. Generate README.md** with:
- Skill overview
- Standards list
- Usage examples
- Integration notes

**D. Create placeholder standards files** based on user input

**Error handling:**
- **If Write fails**: Display "Failed to create skill file: {error}" and prompt "[R]etry/[A]bort"
- **If directory doesn't exist**: Create directories first, then retry Write
- Track successful creation in files_created and standards_files_created counters

### Step 7: Cleanup and Display Success Summary

**Cleanup:**
- No temporary files created (all state in memory)
- No cleanup required

**Display summary:**
```
╔════════════════════════════════════════════════════════════╗
║          Skill Created Successfully                        ║
╚════════════════════════════════════════════════════════════╝

Skill: {skill-name}
Location: {file-path}
Bundle: {bundle-name}
Type: {skill-type}

Statistics:
- Questions answered: {questions_answered}
- Validations performed: {validations_performed}
- Duplication checks: {duplication_checks}
- Files created: {files_created}
- Standards files created: {standards_files_created}

Next steps:
1. Review skill file: {file-path}
2. Populate standards files in standards/ directory
3. Run diagnosis: /plugin-diagnose-skills skill-name={skill-name}
4. Test skill activation
```

### Step 8: Run Skill Diagnosis

Execute:
```
SlashCommand: /cui-plugin-development-tools:plugin-diagnose-skills skill-name={created-skill-name}
```

**Error handling:**
- **If diagnosis fails**: Display warning but don't abort (skill was already created)
- Report: "⚠️ Diagnosis failed: {error}. Skill created but not validated. Run /plugin-diagnose-skills {skill-name} manually."

## STATISTICS TRACKING

Track throughout workflow:
- `questions_answered`: Count of questionnaire responses collected
- `validations_performed`: Count of validation checks executed
- `files_created`: Count of skill files successfully created (SKILL.md, README.md)
- `standards_files_created`: Count of standards/*.md files created
- `duplication_checks`: Count of duplication detection runs

Display all statistics in Step 7 summary.

## CRITICAL RULES

**Architecture Compliance:**
- Skills must be self-contained (no cross-skill duplication)
- Use Skill tool for cross-skill references
- Standards files in standards/ directory only
- No executable logic in SKILL.md (descriptive only)

**YAML Frontmatter:**
- Required: name, description
- Optional: requirements, standards (list of standards files)
- Use list format for standards array

**Standards Organization:**
- Group related standards in subdirectories
- Use descriptive file names (kebab-case.md)
- One concern per standards file
- Cross-reference using relative paths

**File Generation:**
- Trust AI to generate appropriate structure
- Provide outline, not full templates
- Let AI format professionally

**Validation:**
- ALL questionnaire responses must be validated
- Clear error messages for invalid inputs
- Retry on validation failures
- Check for duplicate skills before creation

**Error Handling:**
- Prompt user on file operation failures
- Allow retry/abort decisions
- Track all validations and checks
- Non-blocking diagnosis failures

## USAGE EXAMPLES

**Create marketplace skill:**
```
/plugin-create-skill
```

**Create global skill:**
```
/plugin-create-skill scope=global
```

**Create project skill:**
```
/plugin-create-skill scope=project
```

## ARCHITECTURE

This command:
- Uses interactive questionnaire pattern
- References cui-marketplace-architecture skill for validation
- Delegates diagnosis to /plugin-diagnose-skills
- Generates minimal structure (no bloated templates)
- Trusts AI to format content appropriately

## STANDARDS

Follows:
- Claude Code marketplace architecture standards
- Skill quality standards
- YAML frontmatter conventions

## RELATED

- `/plugin-diagnose-skills` - Validates created skill
- `/cui-update-skill` - Update existing skills
- `/plugin-create-bundle` - Creates bundle for skills
- `cui-marketplace-architecture` skill - Architecture rules
