---
name: plugin-doctor
description: Diagnose and fix quality issues in marketplace components
---

# Doctor Marketplace Components

Analyze marketplace components for quality issues and apply fixes in a single workflow.

## Usage

```
# Doctor all components of a type
/plugin-doctor agents
/plugin-doctor commands
/plugin-doctor skills
/plugin-doctor metadata
/plugin-doctor scripts

# Doctor single component
/plugin-doctor agent=my-agent
/plugin-doctor command=my-command
/plugin-doctor skill=my-skill

# Doctor entire marketplace
/plugin-doctor marketplace

# Diagnosis only (no fixes)
/plugin-doctor agents --no-fix

# Show usage
/plugin-doctor
```

## WORKFLOW

When you invoke this command, I will:

1. **Parse scope** from parameters:
   - Detect component type (agents/commands/skills/metadata/scripts/marketplace)
   - Detect single vs all components
   - Check for --no-fix flag

2. **Load plugin-doctor skill**:
   ```
   Skill: cui-plugin-development-tools:plugin-doctor
   ```

3. **Execute doctor workflow**:
   - **Diagnose**: Analyze components using scripts
   - **Categorize**: Separate safe vs risky issues
   - **Auto-Fix**: Apply safe fixes automatically
   - **Prompt**: Ask for confirmation on risky fixes
   - **Verify**: Confirm fixes resolved issues

4. **Display results** with fixes applied and verification status

## PARAMETERS

**Required**: One of:
- `scope`: agents|commands|skills|metadata|scripts|marketplace
- `component=name`: agent=X, command=X, or skill=X

**Optional**:
- `--no-fix`: Diagnosis only, skip fix phase

**Error Handling**:
- No scope → Display usage with examples
- Invalid scope → Display valid scopes
- Component not found → Error with available components

## Fix Categorization

**Safe Fixes** (applied automatically, NO prompts):
- Missing frontmatter fields
- Invalid YAML syntax
- Unused tools in frontmatter
- Trailing whitespace

**Risky Fixes** (require confirmation via prompt):
- Rule 6 violations (Task tool in agents)
- Rule 7 violations (Maven usage)
- Pattern 22 violations (self-invocation)
- Structural changes
- Content removal

## Non-Prompting Behavior

This command delegates to `cui-plugin-development-tools:plugin-doctor` skill which is designed to run without user prompts for safe operations:

- **Safe fixes**: Applied automatically WITHOUT any user prompts
- **Risky fixes**: ONLY these require confirmation
- **All analysis**: Non-prompting (uses pre-approved tools and paths)

## Examples

```
User: /plugin-doctor agents
Result: Diagnoses all agents, auto-fixes safe issues, prompts for risky fixes

User: /plugin-doctor skill=my-skill
Result: Diagnoses single skill, applies fixes, verifies

User: /plugin-doctor marketplace
Result: Comprehensive health check across all component types

User: /plugin-doctor commands --no-fix
Result: Diagnosis only, shows issues without applying fixes

User: /plugin-doctor
Result: Shows usage with all scope options
```

## CONTINUOUS IMPROVEMENT RULE

After executing this command, if you discover any opportunities to improve it, invoke:

`/plugin-maintain command-name=plugin-doctor update="[improvement description]"`

Common improvements:
- More efficient workflow patterns
- Better error handling or user prompts
- Clearer parameter documentation
- Additional fix categorizations

## Related

- `/plugin-create` - Create new components
- `/plugin-maintain` - Update existing components
- `/plugin-verify` - Run full marketplace verification
