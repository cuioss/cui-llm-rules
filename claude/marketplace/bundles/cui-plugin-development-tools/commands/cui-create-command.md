---
name: cui-create-command
description: Guide users through creating a well-structured slash command with comprehensive questionnaire
---

# Create Command Command

Interactive wizard for creating well-structured slash commands following command quality standards.

## PARAMETERS

**scope** - Where to create command (marketplace/global/project, default: marketplace)

## WORKFLOW

### Step 1: Interactive Questionnaire

**A. Command name** - kebab-case with verb (e.g., `review-code`, `run-tests`)

**B. Bundle selection** - List available bundles

**C. Description** - One sentence (<100 chars)

**D. Command type**:
1. Orchestration (coordinates agents/commands)
2. Diagnostic (analyzes and reports)
3. Interactive (user questionnaire)
4. Automation (executes workflow)

**E. Parameters** - What parameters does command accept?

**F. Workflow steps** - Main steps command performs

**G. Tool requirements** - Which tools needed?

### Step 2: Validate Against Standards

Load command quality standards and verify:
- Clear title and description
- Workflow is structured
- Tool usage appropriate
- No obvious bloat

### Step 3: Generate Command File

Create `{bundle}/commands/{command-name}.md` with:

**A. YAML frontmatter**: name, description

**B. Overview** section

**C. PARAMETERS** section (if applicable)

**D. WORKFLOW** section (numbered steps)

**E. CRITICAL RULES** section

**F. USAGE EXAMPLES** section

**G. RELATED** section

Trust AI to generate professional structure from questionnaire answers.

### Step 4: Display Summary

Show created file and next steps.

### Step 5: Run Command Diagnosis

```
SlashCommand: /cui-diagnose-commands command-name={command-name}
```

## CRITICAL RULES

**Structure:**
- Valid YAML frontmatter
- Clear parameter documentation
- Numbered workflow steps
- Usage examples included

**Quality:**
- Target <400 lines
- No embedded templates
- Trust AI inference
- Extract to skills if needed

**Anti-Bloat:**
- No "just-in-case" content
- No duplication
- Minimal specification
- Reference skills for details

## USAGE EXAMPLES

**Create command:**
```
/cui-create-command
```

**Specific scope:**
```
/cui-create-command scope=project
```

## RELATED

- `/cui-diagnose-commands` - Validates command
- Command quality standards
