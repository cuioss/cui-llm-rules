---
name: plugin-diagnose
description: Find and understand quality issues in marketplace components
---

# Diagnose Marketplace Issues

Analyze marketplace components for quality issues, bloat, and standards violations.

## Usage

```
# Diagnose all components of a type
/plugin-diagnose agents
/plugin-diagnose commands
/plugin-diagnose skills
/plugin-diagnose metadata
/plugin-diagnose scripts

# Diagnose single component
/plugin-diagnose agent=my-agent
/plugin-diagnose command=my-command
/plugin-diagnose skill=my-skill

# Diagnose entire marketplace
/plugin-diagnose marketplace

# Show usage
/plugin-diagnose
```

## Workflow

When you invoke this command, I will:

1. **Parse scope** from parameters:
   - Detect component type (agents/commands/skills/metadata/scripts/marketplace)
   - Detect single vs all components
   - Validate parameter syntax

2. **Load plugin-diagnose skill**:
   ```
   Skill: cui-plugin-development-tools:plugin-diagnose
   ```

3. **Invoke appropriate workflow**:
   - `agents` or `agent=X` → diagnose-agents workflow
   - `commands` or `command=X` → diagnose-commands workflow
   - `skills` or `skill=X` → diagnose-skills workflow
   - `metadata` → diagnose-metadata workflow
   - `scripts` → diagnose-scripts workflow
   - `marketplace` → validate-marketplace workflow

4. **Display results** with issue categorization

5. **Offer fix option**: "Run /plugin-fix to apply fixes"

## Parameter Validation

**Required**: One of:
- `scope`: agents|commands|skills|metadata|scripts|marketplace
- `component=name`: agent=X, command=X, or skill=X

**Error Handling**:
- No scope → Display usage with examples
- Invalid scope → Display valid scopes
- Component not found → Error with available components

## Examples

```
User: /plugin-diagnose agents
Result: Invokes plugin-diagnose:diagnose-agents (all agents)

User: /plugin-diagnose agent=my-agent
Result: Invokes plugin-diagnose:diagnose-agents (single agent)

User: /plugin-diagnose marketplace
Result: Invokes plugin-diagnose:validate-marketplace

User: /plugin-diagnose
Result: Shows usage with all scope options

User: /plugin-diagnose invalid
Result: Error: Invalid scope. Use: agents, commands, skills, metadata, scripts, or marketplace
```

## Related

- `/plugin-fix` - Apply fixes to diagnosed issues
- `/plugin-create` - Create new components
- `/plugin-verify` - Run full marketplace verification
