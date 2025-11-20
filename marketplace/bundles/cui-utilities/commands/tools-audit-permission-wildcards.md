---
name: tools-audit-permission-wildcards
description: Analyzes marketplace bundles to identify required permission wildcard patterns for skills and commands
---

# Audit Permission Wildcards Command

Scans all marketplace bundles to discover skills and commands, analyzes their naming patterns, and generates the minimal set of wildcard permissions needed to cover all marketplace tools.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=tools-audit-permission-wildcards update="[your improvement]"` with:
1. Improved marketplace scanning patterns and skill/command discovery techniques
2. Better naming pattern recognition and prefix extraction algorithms
3. More effective wildcard generation and minimization strategies
4. Enhanced integration patterns with tools-setup-project-permissions
5. Any lessons learned about marketplace permission architecture

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

**--dry-run** - Preview analysis without updating any files

## WORKFLOW

### Step 1: Initialize Analysis

Display:
```
╔════════════════════════════════════════════════════════════╗
║     Marketplace Permission Wildcard Audit Starting         ║
╚════════════════════════════════════════════════════════════╝

Scanning marketplace bundles...
```

Track statistics:
- `bundles_scanned`: Count of bundles examined
- `skills_found`: Total skills discovered
- `commands_found`: Total commands discovered
- `scripts_found`: Total scripts discovered
- `wildcards_generated`: Number of wildcard patterns generated

### Step 2: Discover Marketplace Inventory

**A. Execute inventory script:**

```bash
./marketplace/bundles/cui-plugin-development-tools/skills/cui-marketplace-architecture/scripts/scan-marketplace-inventory.sh --resource-types all
```

This discovers all marketplace resources: agents, commands, skills, and scripts.

**B. Parse JSON output:**

Extract from returned JSON:
- `bundles[]` - Array of bundle objects
- For each bundle:
  - `name` - Bundle name
  - `skills[]` - Array of skill objects with `name` and `path` fields
  - `commands[]` - Array of command objects with `name` and `path` fields
  - `scripts[]` - Array of script objects with `name`, `skill`, and `path_formats` fields
  - `statistics` - Counts for agents, commands, skills, scripts

**C. Build component lists:**

```
bundles = [bundle.name for bundle in bundles]
skills_by_bundle = {bundle.name: [skill.name for skill in bundle.skills] for bundle in bundles}
commands_by_bundle = {bundle.name: [cmd.name for cmd in bundle.commands] for bundle in bundles}
scripts_by_bundle = {bundle.name: bundle.scripts for bundle in bundles}
skills = flatten(skills_by_bundle.values())
commands = flatten(commands_by_bundle.values())
scripts = flatten(scripts_by_bundle.values())
```

**D. Track statistics:**
- `bundles_scanned` = length of bundles array
- `skills_found` = length of skills array
- `commands_found` = length of commands array
- `scripts_found` = length of scripts array

**Error handling:**
- If script execution fails: Display "Failed to discover marketplace inventory" and exit
- If bundles array is empty: Display "No marketplace bundles found" and exit
- If JSON parsing fails: Display error and exit

### Step 3: Analyze Naming Patterns

**A. Extract skill naming patterns:**

For each skill name, identify the prefix pattern:
- Pattern: `{prefix}-{rest}` or `{name}` (no prefix)
- Examples:
  - `cui-java-core` → prefix: `cui`
  - `permission-management` → prefix: `none` (bundle-qualified reference)

Note: Skills without standard prefixes are referenced as `bundle:skill-name`, so the bundle prefix matters.

**B. Extract command naming patterns:**

For each command name, identify the prefix pattern:
- Pattern: `/{prefix}-{rest}`
- Examples:
  - `/cui-java-expert:cui-java-implement-code` → prefix: `cui`
  - `/plugin-create-bundle` → prefix: `plugin`
  - `/tools-audit-permission-wildcards` → prefix: `tools`

**C. Generate prefix sets:**
```
skill_prefixes = unique set of skill prefixes
command_prefixes = unique set of command prefixes
```

### Step 4: Generate Individual Bundle Wildcards

**CRITICAL:** Bundle name wildcards (e.g., `cui-*:*`) are NOT supported by Claude Code's permission system. The permission validation regex `^(plugin|bundle):[a-zA-Z0-9_-]+(:[a-zA-Z0-9_-]+)?(\*)?$` requires exact bundle names - wildcards cannot appear in the bundle name portion.

**A. Generate Skill wildcards (one per bundle):**

For each bundle that contains skills:
```
Skill({bundle-name}:*)
```

Examples:
- `Skill(cui-java-expert:*)` - All skills in cui-java-expert bundle
- `Skill(cui-utilities:*)` - All skills in cui-utilities bundle
- `Skill(cui-task-workflow:*)` - All skills in cui-task-workflow bundle

Do NOT generate: `Skill(cui-*:*)` - Invalid pattern!

**B. Generate SlashCommand bundle wildcards (one per bundle with commands):**

For each bundle that contains commands:
```
SlashCommand(/{bundle-name}:*)
```

Examples:
- `SlashCommand(/cui-java-expert:*)` - All cui-java-expert commands (bundle-qualified form)
- `SlashCommand(/cui-utilities:*)` - All cui-utilities commands (bundle-qualified form)
- `SlashCommand(/plugin-*:*)` - Invalid! Cannot wildcard bundle names

Note: These patterns match bundle-qualified invocations like `/cui-java-expert:java-implement-code`.

**C. Generate short-form SlashCommand permissions (one per command):**

**CRITICAL:** Commands can be invoked in two ways:
- Short form: `/plugin-create-bundle` (requires individual permission)
- Bundle-qualified: `/cui-plugin-development-tools:plugin-create-bundle` (covered by bundle wildcard)

Bundle wildcards (Step 4B) only match bundle-qualified invocations. Short-form invocations require individual permissions.

For each command discovered across all bundles:
```
SlashCommand(/{command-name}:*)
```

Examples:
- `SlashCommand(/plugin-create-bundle:*)` - Matches `/plugin-create-bundle name=example`
- `SlashCommand(/java-implement-code:*)` - Matches `/java-implement-code "task"`
- `SlashCommand(/doc-review-single-asciidoc:*)` - Matches `/doc-review-single-asciidoc file.adoc`

**Why both are needed:**
- Bundle wildcard `SlashCommand(/cui-plugin-development-tools:*)` matches `/cui-plugin-development-tools:plugin-create-bundle`
- Short-form permission `SlashCommand(/plugin-create-bundle:*)` matches `/plugin-create-bundle name=example`
- Without the short-form permission, users get prompted when using convenient short-form invocations

**D. Generate script permissions (three formats per script):**

**CRITICAL:** Skill scripts require permissions at runtime mount point `./.claude/skills/{skill-name}/scripts/`.

For each discovered script:
```
Bash({script.path_formats.runtime}:*)
Bash({script.path_formats.relative}:*)
Bash({script.path_formats.absolute}:*)
```

Examples (analyze-skill-structure.sh):
- `Bash(./.claude/skills/cui-marketplace-architecture/scripts/analyze-skill-structure.sh:*)`
- `Bash(./marketplace/bundles/cui-plugin-development-tools/skills/cui-marketplace-architecture/scripts/analyze-skill-structure.sh:*)`
- `Bash(/Users/oliver/git/cui-llm-rules/marketplace/bundles/cui-plugin-development-tools/skills/cui-marketplace-architecture/scripts/analyze-skill-structure.sh:*)`

**Why three formats?** Scripts are accessed different ways:
- Runtime mount (agents at runtime): `./.claude/skills/...`
- Relative physical (main conversation): `./marketplace/bundles/...`
- Absolute physical (testing/validation): `/full/path/...`

**E. Sort wildcards alphabetically:**
- Skill wildcards first (alphabetical by bundle name)
- SlashCommand bundle wildcards second (alphabetical by bundle name)
- SlashCommand short-form permissions third (alphabetical by command name)
- Script permissions fourth (alphabetical by script name, runtime format first)

Increment `wildcards_generated` for each pattern created (bundle wildcards, short-form permissions, AND script permissions - count all three formats per script).

### Step 5: Display Coverage Analysis

**Generate comprehensive report:**

```
╔════════════════════════════════════════════════════════════╗
║     Marketplace Permission Wildcard Audit Complete         ║
╚════════════════════════════════════════════════════════════╝

Statistics:
- Bundles scanned: {bundles_scanned}
- Skills found: {skills_found}
- Commands found: {commands_found}
- Scripts found: {scripts_found}
- Wildcards generated: {wildcards_generated}

Bundle Summary:
{For each bundle}
  • {bundle-name}
    - Skills: {skill_count} ({list skill names})
    - Commands: {command_count} ({list command names})
    - Scripts: {script_count} ({list script names})

Naming Pattern Analysis:
  Skill Patterns:
    - Bundle prefixes: {list unique bundle prefixes}
    - All skills referenced as: bundle:skill-name

  Command Patterns:
    - Command prefixes: {list unique command prefixes}

Required Wildcard Permissions:
  Skills (Bundle Wildcards):
    {list Skill wildcard patterns}

  SlashCommands (Bundle Wildcards):
    {list SlashCommand bundle wildcard patterns}

  SlashCommands (Short-Form Permissions):
    {list SlashCommand short-form patterns}

  Script Permissions (Three Formats Per Script):
    {For each script, list runtime, relative, and absolute formats}

Coverage Verification:
  ✓ {skills_found} skills covered by {skill_wildcard_count} Skill wildcards
  ✓ {commands_found} commands covered by {command_bundle_wildcard_count} SlashCommand bundle wildcards
  ✓ {commands_found} commands require {commands_found} SlashCommand short-form permissions
  ✓ {scripts_found} scripts require {scripts_found * 3} Bash permissions (3 formats each)
  ✓ Total permissions: {total_permission_count}
```

### Step 6: Update tools-setup-project-permissions

**Execute unless --dry-run mode is active.**

**A. Read current tools-setup-project-permissions.md:**
```
Read: marketplace/bundles/cui-utilities/commands/tools-setup-project-permissions.md
```

**B. Locate Step 3D section:**

Find the section starting with:
```
**D. Ensure global marketplace wildcard permissions:**
```

**C. Generate updated content:**

Create new permission list based on analysis (bundle wildcards, short-form permissions, AND script permissions):
```
**E. Ensure global marketplace permissions:**

**Bundle Wildcards:**
- Skills: {list Skill wildcard patterns}
- SlashCommands: {list SlashCommand bundle wildcard patterns}

**Short-Form Command Permissions:**
- {list SlashCommand short-form patterns}

**Validation:**
- Check for all patterns above in global settings
- Add missing permissions automatically (no prompt - standard marketplace permissions)
- Track: `marketplace_wildcards_added_to_global`, `marketplace_shortform_added_to_global`

**Note:** Script permissions are managed by Step 3D (Ensure skill script permissions) which uses the inventory script to discover and add them to project-level settings.
```

**D. Update file:**
```
Edit: marketplace/bundles/cui-utilities/commands/tools-setup-project-permissions.md
Replace Step 3E content with generated content
```

**E. Display update confirmation:**
```
✅ Updated tools-setup-project-permissions.md Step 3E with {wildcards_generated} wildcards

Updated wildcards:
{list all wildcards (skills, commands only - scripts handled separately)}

Note: Script permissions ({scripts_found * 3} total) are added via Step 3D using inventory script
```

**Error handling:**
- If Read fails: Display error, skip update, continue to summary
- If Edit fails: Display error, offer to display wildcards for manual update

### Step 7: Display Final Summary

```
╔════════════════════════════════════════════════════════════╗
║                    Audit Summary                           ║
╚════════════════════════════════════════════════════════════╝

Marketplace Coverage: 100%
- All {skills_found} skills covered
- All {commands_found} commands covered
- All {scripts_found} scripts covered ({scripts_found * 3} permissions for 3 formats)
- {wildcards_generated} wildcard permissions required

{if not --dry-run}
✅ tools-setup-project-permissions.md updated
{else}
ℹ️  Dry-run mode: No files modified
{endif}

Next Steps:
1. Review generated wildcards above
2. Run /tools-setup-project-permissions to apply changes
   - Applies skill/command wildcards to global settings
   - Applies script permissions to project-level settings
3. Verify permissions in ~/.claude/settings.json (global) and .claude/settings.json (project)
```

## CRITICAL RULES

**Scanning:**
- Use scan-marketplace-inventory.sh script for ALL resource discovery
- Scan ALL bundles in marketplace using `--resource-types all`
- Extract skills, commands, and scripts from JSON output
- Handle missing or malformed JSON gracefully

**Pattern Recognition:**
- Identify all unique prefixes (cui-, plugin-, tools-, etc.)
- Generate wildcards for each prefix found
- Never hardcode prefix list - discover dynamically
- Sort wildcards alphabetically for consistency

**Wildcard Generation:**
- Generate one `Skill({bundle-name}:*)` per bundle (exact bundle name required)
- Generate one `SlashCommand(/{bundle-name}:*)` per bundle with commands
- Generate three `Bash(...)` patterns per script (runtime, relative, absolute)
- NEVER use wildcards in bundle names (e.g., `cui-*:*` is invalid)
- Permission system requires exact bundle names per validation regex
- Include `:*` suffix for parameterized commands/skills/scripts

**Integration:**
- Always update tools-setup-project-permissions (unless --dry-run)
- Update Step 3E with skill/command wildcards (go to global settings)
- Script permissions handled separately by Step 3D (go to project-level settings)
- Never modify files in dry-run mode
- Provide clear confirmation of updates
- Maintain existing file structure

**Error Handling:**
- Non-blocking errors for individual file reads
- Critical errors for bundle discovery failures
- Clear error messages with recovery suggestions
- Continue analysis even if some files fail

## STATISTICS TRACKING

Track throughout workflow:
- `bundles_scanned`: Count of bundles examined
- `skills_found`: Total skills discovered
- `commands_found`: Total commands discovered
- `scripts_found`: Total scripts discovered
- `wildcards_generated`: Number of wildcard patterns created (includes skill/command wildcards + script permissions × 3)
- `files_updated`: Count of files modified (0 or 1)

Display all statistics in final summary.

## USAGE EXAMPLES

**Standard usage (audit and update):**
```
/tools-audit-permission-wildcards
```

**Preview without making changes:**
```
/tools-audit-permission-wildcards --dry-run
```

## RELATED

- `/tools-setup-project-permissions` - Uses wildcards discovered by this command
- `/plugin-diagnose-marketplace` - Validates marketplace structure
- Permission management skill - Permission architecture patterns
