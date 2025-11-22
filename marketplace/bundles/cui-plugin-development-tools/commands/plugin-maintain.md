---
name: plugin-maintain
description: Maintain marketplace health through updates and refactoring
---

# Maintain Marketplace

Update components, add knowledge, maintain READMEs, and refactor structure.

## Usage

```
# Update components
/plugin-maintain update agent=my-agent
/plugin-maintain update command=my-command

# Add knowledge to skill
/plugin-maintain add-knowledge skill=my-skill source=url

# Maintain READMEs
/plugin-maintain readme                    # All bundles
/plugin-maintain readme bundle=my-bundle   # Single bundle

# Refactor structure
/plugin-maintain refactor

# Apply orchestration compliance
/plugin-maintain orchestration command=my-command

# Show usage
/plugin-maintain
```

## WORKFLOW

When you invoke this command, I will:

1. **Parse task type** from parameters:
   - Detect maintenance task (update/add-knowledge/readme/refactor/orchestration)
   - Extract component target and parameters
   - Validate parameter syntax

2. **Load plugin-maintain skill**:
   ```
   Skill: cui-plugin-development-tools:plugin-maintain
   ```

3. **Invoke appropriate workflow**:
   - `update agent=X` or `update command=X` → update-component workflow
   - `add-knowledge skill=X source=Y` → add-knowledge workflow
   - `readme` or `readme bundle=X` → update-readme workflow
   - `refactor` → refactor-structure workflow
   - `orchestration command=X` → apply-orchestration workflow

4. **Display results** to user

## PARAMETERS

**Required**: `task_type` (update|add-knowledge|readme|refactor|orchestration)

**Task-Specific Required**:
- `update`: component type and name (agent=X or command=X)
- `add-knowledge`: skill name and source (skill=X source=Y)
- `readme`: None (optional bundle=X)
- `refactor`: None
- `orchestration`: command name (command=X)

**Error Handling**:
- No task type → Display usage
- Invalid task type → Display valid task types
- Missing required params → Display task-specific usage
- Component not found → Error with available components

## Examples

```
User: /plugin-maintain update agent=my-agent
Result: Invokes plugin-maintain:update-component

User: /plugin-maintain add-knowledge skill=my-skill source=https://example.com/doc
Result: Invokes plugin-maintain:add-knowledge

User: /plugin-maintain readme
Result: Invokes plugin-maintain:update-readme (all bundles)

User: /plugin-maintain readme bundle=my-bundle
Result: Invokes plugin-maintain:update-readme (single bundle)

User: /plugin-maintain refactor
Result: Invokes plugin-maintain:refactor-structure

User: /plugin-maintain
Result: Shows usage with all task types
```

## CONTINUOUS IMPROVEMENT RULE

After executing this command, if you discover any opportunities to improve it, invoke:

`/plugin-maintain command-name=plugin-maintain update="[improvement description]"`

Common improvements:
- More efficient maintenance workflows
- Better knowledge integration patterns
- Improved README generation

## Related

- `/plugin-doctor` - Diagnose and fix issues in components
- `/plugin-create` - Create new components
- `/plugin-verify` - Verify marketplace health
