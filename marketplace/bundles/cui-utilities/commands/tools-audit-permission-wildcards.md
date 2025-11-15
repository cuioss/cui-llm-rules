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
4. Enhanced integration patterns with cui-setup-project-permissions
5. Any lessons learned about marketplace permission architecture

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

**--update-command** - Automatically update cui-setup-project-permissions.md Step 3D with discovered wildcards

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
  - `/cui-setup-project-permissions` → prefix: `cui`
  - `/plugin-create-bundle` → prefix: `plugin`
  - `/tools-audit-permission-wildcards` → prefix: `tools`

**C. Generate prefix sets:**
```
skill_prefixes = unique set of skill prefixes
command_prefixes = unique set of command prefixes
```

### Step 6: Generate Minimal Wildcard Set

**A. Generate Skill wildcards:**

For skills, the permission pattern is `Skill(bundle:skill-name)`, but since all bundles use the same prefix pattern (e.g., `cui-*`), we can use:
```
Skill(cui-*:*)  # Covers all cui-* bundles and their skills
```

**B. Generate SlashCommand wildcards:**

For commands, the permission pattern is `SlashCommand(/command-name)`:
```
For each prefix in command_prefixes:
  SlashCommand(/{prefix}-*:*)
```

Examples:
- `SlashCommand(/cui-*:*)` - Covers all cui-* commands
- `SlashCommand(/plugin-*:*)` - Covers all plugin-* commands
- `SlashCommand(/tools-*:*)` - Covers all tools-* commands

**C. Sort wildcards alphabetically:**
- Skill wildcards first
- SlashCommand wildcards second
- Alphabetical within each group

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

{if --update-command}
Next Step: Update cui-setup-project-permissions.md Step 3D
{endif}
```

### Step 8: Update cui-setup-project-permissions (if --update-command)

**Only execute if --update-command flag is set AND not in dry-run mode.**

**A. Read current cui-setup-project-permissions.md:**
```
Read: marketplace/bundles/cui-utilities/commands/cui-setup-project-permissions.md
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
Edit: marketplace/bundles/cui-utilities/commands/cui-setup-project-permissions.md
Replace Step 3D content with generated content
```

**E. Display update confirmation:**
```
✅ Updated cui-setup-project-permissions.md Step 3D with {wildcards_generated} wildcards

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

{if --update-command and not --dry-run}
✅ cui-setup-project-permissions.md updated
{endif}

{if --dry-run}
ℹ️  Dry-run mode: No files modified
{endif}

Next Steps:
1. Review generated wildcards above
2. Ensure wildcards are in global settings (~/.claude/settings.json)
3. Run /cui-setup-project-permissions to apply changes
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
- Use `Skill(bundle-prefix-*:*)` pattern for skills
- Use `SlashCommand(/command-prefix-*:*)` pattern for commands
- Include `:*` suffix for parameterized commands/skills
- Minimize number of wildcards (one per prefix)

**Integration:**
- Only update cui-setup-project-permissions when --update-command flag set
- Never modify files in dry-run mode
- Provide clear before/after for updates
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

**Basic audit (report only):**
```
/tools-audit-permission-wildcards
```

**Audit and update cui-setup-project-permissions:**
```
/tools-audit-permission-wildcards --update-command
```

**Preview without making changes:**
```
/tools-audit-permission-wildcards --dry-run
```

**Audit and update (auto):**
```
/tools-audit-permission-wildcards --update-command
```

## RELATED

- `/cui-setup-project-permissions` - Uses wildcards discovered by this command
- `/plugin-diagnose-marketplace` - Validates marketplace structure
- Permission management skill - Permission architecture patterns
