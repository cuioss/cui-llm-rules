---
name: cui-create-skill
description: Guide users through creating a well-structured skill with standards organization and proper configuration
---

# Create Skill Command

Interactive wizard that guides users through creating a new well-structured Claude Code skill following marketplace architecture best practices.

## PARAMETERS

**scope** - Where to create skill (marketplace/global/project, default: marketplace)

## WORKFLOW

### Step 1: Welcome and Context

Display welcome message explaining skill creation process.

### Step 2: Collect Basic Information

**A. Skill name** - kebab-case, descriptive (e.g., `java-unit-testing-patterns`)

**B. Bundle selection** - List available bundles or create new

**C. Short description** (1 sentence, <100 chars)

**D. Detailed description** (2-3 sentences explaining what standards/knowledge skill provides)

### Step 3: Determine Skill Type

Ask user to select:
1. **Standards skill** - Provides coding/process standards (most common)
2. **Reference skill** - Provides reference material (API docs, examples)
3. **Diagnostic skill** - Provides diagnostic patterns/tools

### Step 4: Collect Standards Information (if standards skill)

**A. Standards categories** - What domains does this cover? (e.g., Java, Testing, Documentation)

**B. Target audience** - Who uses these standards? (developers, documentation writers, etc.)

**C. Standards files** - What standards files will be included?
- Prompt user to list main standards documents
- Suggest organization structure based on categories

### Step 5: Enforce Architecture Compliance

Load and apply marketplace architecture standards:

```
Skill: cui-marketplace-architecture
```

Verify:
- Self-contained standards (no cross-skill duplication)
- Proper skill usage patterns (Skill tool for standards, not Read)
- Clean reference patterns (xref within skill, Skill across skills)

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

### Step 7: Display Success Summary

Show:
- Files created
- Next steps (populate standards files, test skill activation)
- Integration commands to reference skill

### Step 8: Run Skill Diagnosis

Execute:
```
SlashCommand: /cui-diagnose-skills skill-name={created-skill-name}
```

Review results and offer to fix any issues found.

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

## USAGE EXAMPLES

**Create marketplace skill:**
```
/cui-create-skill
```

**Create global skill:**
```
/cui-create-skill scope=global
```

**Create project skill:**
```
/cui-create-skill scope=project
```

## ARCHITECTURE

This command:
- Uses interactive questionnaire pattern
- References cui-marketplace-architecture skill for validation
- Delegates diagnosis to /cui-diagnose-skills
- Generates minimal structure (no bloated templates)
- Trusts AI to format content appropriately

## STANDARDS

Follows:
- Claude Code marketplace architecture standards
- Skill quality standards
- YAML frontmatter conventions

## RELATED

- `/cui-diagnose-skills` - Validates created skill
- `/cui-create-bundle` - Creates bundle for skills
- `cui-marketplace-architecture` skill - Architecture rules
