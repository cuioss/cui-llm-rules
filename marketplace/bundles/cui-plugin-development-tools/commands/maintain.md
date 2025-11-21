---
name: maintain
description: Maintain marketplace health through updates and refactoring
---

# Maintain Marketplace

Update components, add knowledge, maintain READMEs, and refactor structure.

## Usage

```
# Update components
/maintain update agent=my-agent
/maintain update command=my-command

# Add knowledge to skill
/maintain add-knowledge skill=my-skill source=url

# Maintain READMEs
/maintain readme                    # All bundles
/maintain readme bundle=my-bundle   # Single bundle

# Refactor structure
/maintain refactor

# Apply orchestration compliance
/maintain orchestration command=my-command

# Show usage
/maintain
```

## Workflow

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

## Parameter Validation

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
User: /maintain update agent=my-agent
Result: Invokes plugin-maintain:update-component

User: /maintain add-knowledge skill=my-skill source=https://example.com/doc
Result: Invokes plugin-maintain:add-knowledge

User: /maintain readme
Result: Invokes plugin-maintain:update-readme (all bundles)

User: /maintain readme bundle=my-bundle
Result: Invokes plugin-maintain:update-readme (single bundle)

User: /maintain refactor
Result: Invokes plugin-maintain:refactor-structure

User: /maintain
Result: Shows usage with all task types
```

## Related

- `/diagnose` - Find issues in components
- `/create` - Create new components
- `/verify` - Verify marketplace health
