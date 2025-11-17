---
name: plugin-inventory
description: Discovers and catalogs all marketplace resources with names and paths
---

# Plugin Inventory Command

Scans the marketplace directory structure and generates a complete inventory of all bundles, agents, commands, and skills with their names and paths.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=plugin-inventory update="[your improvement]"` with:
1. Better glob patterns for discovering marketplace resources efficiently
2. Improved output format for presenting inventory data
3. More effective metadata extraction from YAML frontmatter
4. Enhanced error handling for missing or malformed resources
5. Any lessons learned about marketplace structure scanning workflows

This ensures the command evolves and becomes more effective with each execution.

## PURPOSE

Provides a centralized, reusable inventory service for discovering all marketplace resources. Other commands can use this command to:
- Validate references to marketplace components
- Discover what agents/commands/skills exist
- Get complete resource lists for analysis
- Find resources by name or type

## PARAMETERS

**scope** (optional, default: "marketplace") - Where to scan for resources
- `marketplace` - Scan marketplace/bundles/ (relative to current working directory)
- `global` - Scan ~/.claude/
- `project` - Scan .claude/ (relative to current working directory)

**--type** (optional) - Filter to specific resource type(s)
- `agents` - Return only agents
- `commands` - Return only commands
- `skills` - Return only skills
- If not specified: Return all resource types (default)

**--json** (optional) - Output in JSON format instead of human-readable format
**--include-descriptions** (optional) - Extract and include descriptions from YAML frontmatter (slower)

## WORKFLOW

### Step 1: Parse Parameters

**Parse scope parameter:**
- marketplace → Base path: `marketplace/bundles`
- global → Base path: `~/.claude`
- project → Base path: `.claude`

**Default:** Use marketplace if no scope provided

**Parse --type parameter:**
- Extract requested type(s): agents, commands, or skills
- If not provided: scan_all = true
- If provided: scan_all = false, scan_agents/scan_commands/scan_skills = true/false based on type

**Token Optimization:** Skipping unneeded resource types reduces:
- Discovery operations (fewer Glob calls)
- Result payload (smaller JSON output)
- Processing time

### Step 2: Discover All Bundles

**Use Glob to find all bundles by their plugin.json files:**

```
Glob: pattern="*/.claude-plugin/plugin.json", path="{base_path}"
```

**Extract bundle information:**
- Each result has format: `{base_path}/{bundle-name}/.claude-plugin/plugin.json`
- Extract bundle name from path (second-to-last directory component)
- Extract bundle path as `{base_path}/{bundle-name}`

**Track:** Total bundles discovered

### Step 3: For Each Bundle, Discover Agents

**When to execute:** If scan_all = true OR --type=agents specified

**For each bundle discovered:**

```
Glob: pattern="*.md", path="{bundle_path}/agents"
```

**Extract agent names:** Remove .md extension from each filename

**Build agent list:** Store bundle name, agent name, and full path

**If skipped:** Set agents = [] for this bundle

### Step 4: For Each Bundle, Discover Commands

**When to execute:** If scan_all = true OR --type=commands specified

**For each bundle discovered:**

```
Glob: pattern="*.md", path="{bundle_path}/commands"
```

**Extract command names:** Remove .md extension from each filename

**Build command list:** Store bundle name, command name, and full path

**If skipped:** Set commands = [] for this bundle

### Step 5: For Each Bundle, Discover Skills

**When to execute:** If scan_all = true OR --type=skills specified

**For each bundle discovered:**

```
Glob: pattern="*/SKILL.md", path="{bundle_path}/skills"
```

**If Glob fails** (directory doesn't exist): Set skills = [], continue to next bundle

**Extract skill information:**
- Each result has format: `{bundle_path}/skills/{skill-name}/SKILL.md`
- Extract skill name: Take the second-to-last path component (directory before `SKILL.md`)
- Skill path is: `{bundle_path}/skills/{skill-name}` (directory containing SKILL.md)

**Build skill list:** Store bundle name, skill name, and skill directory path

**If skipped:** Set skills = [] for this bundle

### Step 6: Optionally Extract Descriptions

**If --include-descriptions flag provided:**

For each agent/command/skill file:
```
Read: {file_path}
Grep: pattern="description:\s*(.+)", path="{file_path}"
```

Extract description from YAML frontmatter and include in results

### Step 7: Display Results

**If --json flag provided:**

Output complete JSON structure:
```json
{
  "scope": "marketplace",
  "base_path": "{absolute_base_path}",
  "scan_timestamp": "{ISO8601_timestamp}",
  "bundles": [
    {
      "name": "{bundle-name}",
      "path": "{bundle-path}",
      "agents": [
        {"name": "{agent-name}", "path": "{agent-path}"}
      ],
      "commands": [
        {"name": "{command-name}", "path": "{command-path}"}
      ],
      "skills": [
        {"name": "{skill-name}", "path": "{skill-path}"}
      ],
      "statistics": {
        "agents": N,
        "commands": N,
        "skills": N,
        "total_resources": N
      }
    }
  ],
  "statistics": {
    "total_bundles": N,
    "total_agents": N,
    "total_commands": N,
    "total_skills": N,
    "total_resources": N
  }
}
```

**Otherwise, display human-readable format:**

```
==================================================
Marketplace Inventory
==================================================

Scope: {scope}
Base Path: {base_path}

Bundles Discovered: {count}

Bundle: {bundle-1}
  Agents ({count}): {agent-1}, {agent-2}, ...
  Commands ({count}): {command-1}, {command-2}, ...
  Skills ({count}): {skill-1}, {skill-2}, ...

Bundle: {bundle-2}
  Agents ({count}): {agent-1}, {agent-2}, ...
  Commands ({count}): {command-1}, {command-2}, ...
  Skills ({count}): {skill-1}, {skill-2}, ...

...

==================================================
Summary
==================================================

Total Bundles: {count}
Total Agents: {count}
Total Commands: {count}
Total Skills: {count}
Total Resources: {count}
```

## CRITICAL RULES

**Discovery:**
- **ALWAYS use Glob** for file/directory discovery
- **NEVER use Bash** for find, ls, or test operations
- Handle missing directories gracefully (empty arrays)

**Validation:**
- Only use paths returned by Glob - never fabricate names
- Verify each extracted name matches an actual Glob result
- Skip invalid entries rather than failing

**Performance:**
- Default mode (no --include-descriptions): Fast scan using Glob only
- With --include-descriptions: Slower, uses Read/Grep per resource

**Error Handling:**
- If base path doesn't exist: Display clear error with path
- If Glob fails: Display error and continue with partial results
- If individual resource fails: Log warning, continue scanning

## TOOL USAGE

- **Glob**: Primary tool for all discovery operations
- **Read**: Optional, only with --include-descriptions flag
- **Grep**: Optional, only with --include-descriptions flag for extracting frontmatter

## EXAMPLES

### Example 1: Quick Inventory (Default)
```bash
/plugin-inventory
```
Scans marketplace/bundles/, displays human-readable summary of all resources

### Example 2: Commands Only (JSON)
```bash
/plugin-inventory --type=commands --json
```
Returns only commands in JSON format (used by plugin-diagnose-commands)

### Example 3: Agents Only (JSON)
```bash
/plugin-inventory --type=agents --json
```
Returns only agents in JSON format (used by plugin-diagnose-agents)

### Example 4: Skills Only (JSON)
```bash
/plugin-inventory --type=skills --json
```
Returns only skills in JSON format (used by plugin-diagnose-skills)

### Example 5: Global Scope
```bash
/plugin-inventory scope=global
```
Scans ~/.claude/ instead of marketplace

### Example 6: With Descriptions
```bash
/plugin-inventory --include-descriptions --json
```
Full inventory with descriptions in JSON format

## RELATED

- `/plugin-diagnose-agents` - Uses inventory to discover agents
- `/plugin-diagnose-commands` - Uses inventory to discover commands
- `/plugin-diagnose-skills` - Uses inventory to discover skills
- `/plugin-diagnose-bundle` - Uses inventory to validate bundle structure
