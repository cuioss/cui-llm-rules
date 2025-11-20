---
name: plugin-create-command
description: Guide users through creating a well-structured slash command with comprehensive questionnaire
---

# Create Command Command

Interactive wizard for creating well-structured slash commands following command quality standards.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=plugin-create-command update="[your improvement]"` with:
1. Improved questionnaire patterns for gathering command requirements
2. Better validation strategies for command quality standards
3. More effective command file generation templates
4. Enhanced duplication detection across existing commands
5. Any lessons learned about command creation workflows

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

**scope** - Where to create command (marketplace/global/project, default: marketplace)

## WORKFLOW

### Step 1: Interactive Questionnaire

**A. Command name** - kebab-case with verb (e.g., `review-code`, `run-tests`)
   - **Validation**: Must not be empty, must match kebab-case pattern, should start with verb
   - **Error**: If invalid: "Command name must be kebab-case starting with verb (e.g., create-agent)" and retry

**B. Bundle selection** - List available bundles
   - **Validation**: Must select valid bundle from list
   - **Error**: If invalid selection: "Please select a bundle from the list" and retry

**C. Description** - One sentence (<100 chars)
   - **Validation**: Must not be empty, must be ≤100 chars
   - **Error**: If invalid: "Description required (max 100 chars): {current_length}/100" and retry

**D. Command type**:
1. Orchestration (coordinates agents/commands)
2. Diagnostic (analyzes and reports)
3. Interactive (user questionnaire)
4. Automation (executes workflow)
   - **Validation**: Must select 1-4
   - **Error**: If invalid: "Please select command type (1-4)" and retry

**E. Parameters** - What parameters does command accept?
   - **Validation**: Can be empty (for commands with no parameters)
   - **Prompt**: "List parameters (comma-separated) or press Enter if none"

**F. Workflow steps** - Main steps command performs
   - **Validation**: Must provide at least 2 steps
   - **Error**: If empty or <2: "Command requires at least 2 workflow steps" and retry

**G. Tool requirements** - Which tools needed?
   - **Validation**: Must list at least one tool (or "none" for pure orchestrators)
   - **Error**: If empty: "Specify tools needed or 'none' for orchestration-only" and retry

### Step 2: Validate Against Standards and Check Duplication

**A. Load and validate** command quality standards:
```
Read: ~/git/cui-llm-rules/marketplace/bundles/cui-plugin-development-tools/standards/command-quality-standards.md
```

Verify:
- Clear title and description
- Workflow is structured
- Tool usage appropriate
- No obvious bloat

**B. Duplication detection:**
1. Use Glob to find all commands in target bundle
2. Use Grep to search for similar command names or descriptions
3. **If duplicates found**:
   - Display: "⚠️ Similar commands found: {list command names with descriptions}"
   - Prompt: "[C]ontinue anyway/[R]ename command/[A]bort creation?"
   - Track in duplication_checks counter

**Error handling:**
- **If Read fails**: Display "Failed to load standards: {error}" and prompt "[C]ontinue without validation/[A]bort"
- **If Glob/Grep fails**: Log warning, continue (increment validations_performed with note)

### Step 3: Generate Command File

Create `{bundle}/commands/{command-name}.md` with:

**A. YAML frontmatter**: name, description

**B. Overview** section

**C. CONTINUOUS IMPROVEMENT RULE** section (REQUIRED):
```markdown
## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name={command-name} update="[your improvement]"` with:
1. [Improvement area 1 specific to command purpose]
2. [Improvement area 2 specific to command purpose]
3. [Improvement area 3 specific to command purpose]
4. [Improvement area 4 specific to command purpose]
5. Any lessons learned about [command domain] workflows

This ensures the command evolves and becomes more effective with each execution.
```

**D. PARAMETERS** section (if applicable)

**E. WORKFLOW** section (numbered steps)

**F. CRITICAL RULES** section

**G. USAGE EXAMPLES** section

**H. RELATED** section

Trust AI to generate professional structure from questionnaire answers and populate CONTINUOUS IMPROVEMENT RULE with 3-5 improvement areas relevant to the command's specific purpose.

**Error handling:**
- **If Write fails**: Display "Failed to create command file: {error}" and prompt "[R]etry/[A]bort"
- **If directory doesn't exist**: Create directories first, then retry Write
- Track successful creation in files_created counter

### Step 4: Cleanup and Display Summary

**Cleanup:**
- No temporary files created (all state in memory)
- No cleanup required

**Display summary:**
```
╔════════════════════════════════════════════════════════════╗
║          Command Created Successfully                      ║
╚════════════════════════════════════════════════════════════╝

Command: {command-name}
Location: {file-path}
Bundle: {bundle-name}
Type: {command-type}

Statistics:
- Questions answered: {questions_answered}
- Validations performed: {validations_performed}
- Duplication checks: {duplication_checks}
- Files created: {files_created}

Next steps:
1. Review command file: {file-path}
2. Run diagnosis: /plugin-diagnose-commands command-name={command-name}
3. Test command functionality
```

### Step 5: Run Command Diagnosis

```
SlashCommand: /cui-plugin-development-tools:plugin-diagnose-commands command-name={command-name}
```

**Error handling:**
- **If diagnosis fails**: Display warning but don't abort (command was already created)
- Report: "⚠️ Diagnosis failed: {error}. Command created but not validated. Run /plugin-diagnose-commands {command-name} manually."

## STATISTICS TRACKING

Track throughout workflow:
- `questions_answered`: Count of questionnaire responses collected
- `validations_performed`: Count of validation checks executed
- `files_created`: Count of command files successfully created
- `duplication_checks`: Count of duplication detection runs

Display all statistics in final summary.

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

**Validation:**
- ALL questionnaire responses must be validated
- Clear error messages for invalid inputs
- Retry on validation failures
- Check for duplicate commands before creation

**Error Handling:**
- Prompt user on file operation failures
- Allow retry/abort decisions
- Track all validations and checks
- Non-blocking diagnosis failures

## USAGE EXAMPLES

**Create command:**
```
/plugin-create-command
```

**Specific scope:**
```
/plugin-create-command scope=project
```

## RELATED

- `/plugin-diagnose-commands` - Validates command
- `/plugin-update-command` - Update existing commands
- Command quality standards - bundles/cui-plugin-development-tools/standards/command-quality-standards.md
