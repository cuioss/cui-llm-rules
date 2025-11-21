---
name: diagnose
description: Find and understand quality issues in marketplace components
---

# Diagnose Marketplace Issues

Analyze marketplace components for quality issues, bloat, and standards violations.

## Usage

```
# Diagnose all components of a type
/diagnose agents
/diagnose commands
/diagnose skills
/diagnose metadata
/diagnose scripts

# Diagnose single component
/diagnose agent=my-agent
/diagnose command=my-command
/diagnose skill=my-skill

# Diagnose entire marketplace
/diagnose marketplace

# Show usage
/diagnose
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

5. **Offer fix option**: "Run /fix to apply fixes"

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
User: /diagnose agents
Result: Invokes plugin-diagnose:diagnose-agents (all agents)

User: /diagnose agent=my-agent
Result: Invokes plugin-diagnose:diagnose-agents (single agent)

User: /diagnose marketplace
Result: Invokes plugin-diagnose:validate-marketplace

User: /diagnose
Result: Shows usage with all scope options

User: /diagnose invalid
Result: Error: Invalid scope. Use: agents, commands, skills, metadata, scripts, or marketplace
```

## Related

- `/fix` - Apply fixes to diagnosed issues
- `/create` - Create new components
- `/verify` - Run full marketplace verification
