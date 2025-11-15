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
- `wildcards_generated`: Number of wildcard patterns generated

### Step 2: Discover All Bundles

**A. Find all marketplace bundles:**
```
Glob: marketplace/bundles/*/.claude-plugin/plugin.json
```

**B. Extract bundle names:**
- Parse each path to get bundle directory name
- Store in `bundles[]` array
- Increment `bundles_scanned`

**Error handling:**
- If no bundles found: Display "No marketplace bundles found" and exit
- If Glob fails: Display error and exit

### Step 3: Scan All Skills

**A. Find all skill definition files:**
```
Glob: marketplace/bundles/*/skills/*/SKILL.md
```

**B. Extract skill names from YAML frontmatter:**
- For each SKILL.md file found:
  - Read first 10 lines to get YAML frontmatter
  - Extract `name:` field value
  - Add to `skills[]` array
  - Increment `skills_found`

**C. Categorize skills by bundle:**
- Track which bundle each skill belongs to
- Store as `skills_by_bundle[bundle_name] = [skill_names]`

**Error handling:**
- If Read fails: Log warning, skip file, continue
- If no skills found: Continue (valid for bundles with only commands)

### Step 4: Scan All Commands

**A. Find all command files:**
```
Glob: marketplace/bundles/*/commands/*.md
```

Exclude README.md files.

**B. Extract command names from YAML frontmatter:**
- For each command file found:
  - Read first 10 lines to get YAML frontmatter
  - Extract `name:` field value
  - Add to `commands[]` array
  - Increment `commands_found`

**C. Categorize commands by bundle:**
- Track which bundle each command belongs to
- Store as `commands_by_bundle[bundle_name] = [command_names]`

**Error handling:**
- If Read fails: Log warning, skip file, continue
- If no commands found: Continue (valid for bundles with only skills)

### Step 5: Analyze Naming Patterns

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

### Step 6: Generate Individual Bundle Wildcards

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

**B. Generate SlashCommand wildcards (one per bundle with commands):**

For each bundle that contains commands with parameterized names:
```
SlashCommand(/{bundle-name}:*)
```

Examples:
- `SlashCommand(/cui-java-expert:*)` - All cui-java-expert commands
- `SlashCommand(/cui-utilities:*)` - All cui-utilities commands
- `SlashCommand(/plugin-*:*)` - Invalid! Use individual bundle names

Note: Commands without parameters don't need `:*` suffix, but using it is harmless and ensures coverage.

**C. Sort wildcards alphabetically:**
- Skill wildcards first (alphabetical by bundle name)
- SlashCommand wildcards second (alphabetical by bundle name)

Increment `wildcards_generated` for each pattern created.

### Step 7: Display Coverage Analysis

**Generate comprehensive report:**

```
╔════════════════════════════════════════════════════════════╗
║     Marketplace Permission Wildcard Audit Complete         ║
╚════════════════════════════════════════════════════════════╝

Statistics:
- Bundles scanned: {bundles_scanned}
- Skills found: {skills_found}
- Commands found: {commands_found}
- Wildcards generated: {wildcards_generated}

Bundle Summary:
{For each bundle}
  • {bundle-name}
    - Skills: {skill_count} ({list skill names})
    - Commands: {command_count} ({list command names})

Naming Pattern Analysis:
  Skill Patterns:
    - Bundle prefixes: {list unique bundle prefixes}
    - All skills referenced as: bundle:skill-name

  Command Patterns:
    - Command prefixes: {list unique command prefixes}

Required Wildcard Permissions:
  Skills:
    {list Skill wildcard patterns}

  SlashCommands:
    {list SlashCommand wildcard patterns}

Coverage Verification:
  ✓ {skills_found} skills covered by {skill_wildcard_count} Skill wildcards
  ✓ {commands_found} commands covered by {command_wildcard_count} SlashCommand wildcards
```

### Step 8: Update tools-setup-project-permissions

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

Create new wildcard list based on analysis:
```
**D. Ensure global marketplace wildcard permissions:**
- Check for {list Skill wildcards} in global settings
- Check for {list SlashCommand wildcards} in global settings
- Add missing wildcards automatically (no prompt - standard marketplace permissions)
- Track: `marketplace_wildcards_added_to_global`
```

**D. Update file:**
```
Edit: marketplace/bundles/cui-utilities/commands/tools-setup-project-permissions.md
Replace Step 3D content with generated content
```

**E. Display update confirmation:**
```
✅ Updated tools-setup-project-permissions.md Step 3D with {wildcards_generated} wildcards

Updated wildcards:
{list all wildcards}
```

**Error handling:**
- If Read fails: Display error, skip update, continue to summary
- If Edit fails: Display error, offer to display wildcards for manual update

### Step 9: Display Final Summary

```
╔════════════════════════════════════════════════════════════╗
║                    Audit Summary                           ║
╚════════════════════════════════════════════════════════════╝

Marketplace Coverage: 100%
- All {skills_found} skills covered
- All {commands_found} commands covered
- {wildcards_generated} wildcard permissions required

{if not --dry-run}
✅ tools-setup-project-permissions.md updated
{else}
ℹ️  Dry-run mode: No files modified
{endif}

Next Steps:
1. Review generated wildcards above
2. Run /tools-setup-project-permissions to apply changes to global settings
3. Verify wildcards in ~/.claude/settings.json
```

## CRITICAL RULES

**Scanning:**
- Scan ALL bundles in marketplace
- Extract skill names from YAML frontmatter only
- Extract command names from YAML frontmatter only
- Handle missing or malformed YAML gracefully

**Pattern Recognition:**
- Identify all unique prefixes (cui-, plugin-, tools-, etc.)
- Generate wildcards for each prefix found
- Never hardcode prefix list - discover dynamically
- Sort wildcards alphabetically for consistency

**Wildcard Generation:**
- Generate one `Skill({bundle-name}:*)` per bundle (exact bundle name required)
- Generate one `SlashCommand(/{bundle-name}:*)` per bundle with commands
- NEVER use wildcards in bundle names (e.g., `cui-*:*` is invalid)
- Permission system requires exact bundle names per validation regex
- Include `:*` suffix for parameterized commands/skills

**Integration:**
- Always update tools-setup-project-permissions (unless --dry-run)
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
- `wildcards_generated`: Number of wildcard patterns created
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
