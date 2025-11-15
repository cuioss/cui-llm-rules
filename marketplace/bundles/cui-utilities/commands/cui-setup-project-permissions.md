---
name: cui-setup-project-permissions
description: Verify and fix permissions in settings by removing duplicates, fixing formats, and ensuring proper organization
---

# Setup Project Permissions Command

Verifies and fixes permissions in `.claude/settings.local.json` using permission management standards from the `permission-management` skill.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=cui-setup-project-permissions update="[your improvement]"` with:
1. Improved permission validation patterns and syntax checking techniques
2. Better methods for detecting and consolidating redundant permissions
3. More effective consolidation strategies for global vs local permissions
4. Enhanced path normalization and format fixing approaches
5. Any lessons learned about permission architecture patterns
6. Improvements to global settings write workflow and safety checks
7. Better user experience patterns for permission management
8. Optimizations for marketplace permission management (e.g., using wildcards instead of scanning)

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

**add=<permission>** - Add new permission to allow list (e.g., `Edit(//~/git/project/**)`)

**ensurePermissions=<list>** - Ensure exact set of permissions (comma-separated)

**dry-run** - Preview changes without applying

**auto-fix** - Automatically apply safe fixes without prompting (includes global settings updates)

## WORKFLOW

### Step 1: Load Permission Management Standards

```
Skill: permission-management
```

Loads:
- Permission validation standards (syntax, categorization)
- Permission architecture (global/local separation patterns)
- Permission anti-patterns (security checks)
- Historical lessons learned

### Step 2: Read User-Approved Permissions

Check `.claude/run-configuration.md` for setup-project-permissions section containing user-approved suspicious permissions.

### Step 3: Read Global and Local Permissions

**A. Load global permissions** from `~/.claude/settings.json`

**B. Locate and load local settings**:
- `./.claude/settings.local.json` (project-specific)
- `~/.claude/settings.local.json` (fallback)

**C. Validate JSON structure**

**D. Ensure global marketplace wildcard permissions:**
- Check for `Skill(cui-*:*)`, `Skill(plugin-*:*)`, `Skill(tools-*:*)` in global settings
- Check for `SlashCommand(/cui-*:*)`, `SlashCommand(/plugin-*:*)`, `SlashCommand(/tools-*:*)` in global settings
- Add missing wildcards automatically (no prompt - standard marketplace permissions)
- Track: `marketplace_wildcards_added_to_global`

### Step 4: Handle ensurePermissions Parameter (if provided)

Check required permissions, calculate fit score, prompt for fixes if needed. Exit if 100% fit.

### Step 5: Handle add Parameter (if provided)

Validate using permission-validation-standards, check for duplicates, add if valid.

### Step 6: Detect Redundant Local Permissions

Check each local permission against global permissions using patterns from permission-architecture standards.

**A. Check standard redundancies:**
- Exact duplicates
- Permissions covered by broader global permissions
- Examples: `Read(//~/git/project/**)` covered by global `Read(//~/git/**)`

**B. Detect marketplace permissions (should be global):**

Iterate through local permissions and identify:

1. **Marketplace Skills patterns:**
   - `Skill(cui-*:*)` - Example: `Skill(cui-java-expert:*)`
   - `Skill(plugin-*:*)` - Example: `Skill(plugin-tools:*)`
   - `Skill(tools-*:*)` - Example: `Skill(tools-utils:*)`

2. **Marketplace SlashCommands patterns:**
   - `SlashCommand(/cui-*:*)` - Example: `SlashCommand(/cui-setup-project-permissions)`
   - `SlashCommand(/plugin-*:*)` - Example: `SlashCommand(/plugin-diagnose-bundle)`
   - `SlashCommand(/tools-*:*)` - Example: `SlashCommand(/tools-analyze)`

These are universal marketplace tools that should be globally available.

**C. Categorize and track:**
- Add detected marketplace permissions to redundant list
- Track count: `marketplace_permissions_removed`
- Generate suggestion message: "These marketplace permissions should be in global settings (~/.claude/settings.json) to be available across all projects"

**D. Remove from local settings:**
- Remove all detected marketplace permissions from local allow list
- Do not prompt user (safe automatic removal - should be global anyway)

Suggest moving non-project-specific permissions to global.

**E. Move Marketplace Permissions to Global (if detected):**

If `marketplace_permissions_removed > 0`:

1. **Display detected permissions:**
   ```
   Found {count} marketplace permissions in local settings.
   These are universal tools that should be in global settings for all projects.

   Detected permissions:
   - {list of marketplace permissions}
   ```

2. **Determine action based on mode:**
   - If `dry-run`: Display only, skip to Step 7 (no modifications)
   - If `auto-fix`: Skip prompt, proceed to step 3 (automatic update)
   - Otherwise: Prompt user using AskUserQuestion with options:
     - "Add to global settings" (recommended)
     - "Skip - don't add to global"

3. **If proceeding (auto-fix or user approved):**

   **A. Read and validate global settings:**
   ```
   - Load ~/.claude/settings.json
   - Validate JSON structure
   - Check permissions.allow array exists
   ```

   **B. Create backup:**
   ```
   - Store original global settings in memory
   - For rollback if write fails
   ```

   **C. Merge permissions safely:**
   ```
   - For each marketplace permission detected:
     - Check if already exists in global (exact match)
     - If not exists: Add to global permissions.allow
     - Track: marketplace_permissions_added_to_global (count)
   - Sort global permissions.allow list alphabetically
   ```

   **D. Write to global settings:**
   ```
   - Write updated JSON to ~/.claude/settings.json
   - Preserve formatting (2-space indent)
   - Validate JSON after write
   ```

   **E. Handle errors:**
   ```
   - If write fails: Rollback (no changes to global)
   - Log error message
   - Continue with local cleanup
   - Mark marketplace_permissions_moved_to_global = false
   ```

   **F. On success:**
   ```
   - Set marketplace_permissions_moved_to_global = true
   - Track count: marketplace_permissions_added_to_global
   ```

4. **If user skips:**
   - Set marketplace_permissions_moved_to_global = false
   - Generate suggestion message (see Step 14 output)

### Step 7: Remove Duplicate Permissions

Within each list (allow, deny, ask), detect and remove duplicates.

### Step 8: Detect Suspicious Permissions

Apply anti-patterns from permission-anti-patterns standards:
- System temp directories
- Critical system directories
- Overly broad wildcards
- Dangerous commands
- Malformed patterns

Exclude user-approved permissions. Prompt for removal or approval.

### Step 9: Fix Path Formats

Convert user-absolute to user-relative paths:
- `/Users/oliver/` → `~/`
- `/home/username/` → `~/`

### Step 10: Manage System Temp Permissions

Move system temp permissions from allow to deny list for security.

### Step 11: Ensure Settings Write Permission in Ask List

Verify `Write(.claude/settings.local.json)` is in ask list (not allow or deny) for security.

### Step 12: Add Default Project Permissions

**A. Detect current git repository**

**B. Add if missing**:
- `Edit(//~/git/{repo-name}/**)` - Edit project files
- `Write(//~/git/{repo-name}/**)` - Create project files
- **Skip Read** - covered by global `Read(//~/git/**)`

**C. Add project scripts** (if scripts/ exists):
- `Bash(~/git/{repo-name}/scripts/**)` - Execute project scripts

### Step 13: Sort Permission Lists

Sort alphabetically by type: Bash, Edit, Read, SlashCommand, Task, WebFetch, WebSearch, Write

### Step 14: Preview or Apply Changes

**A. Generate comprehensive summary**:
```
Permission Setup Summary
========================

Local Changes:
- Added/Removed/Fixed: {counts}
- Final: {allow_count} allow, {deny_count} deny, {ask_count} ask

Global Changes (if any):
- Marketplace wildcards: {marketplace_wildcards_added_to_global}
- Marketplace permissions: {marketplace_permissions_added_to_global}
- Status: {moved_to_global_status}
```

**B. Display detailed changes**

**C. Apply changes** (unless dry-run mode)

### Step 15: Update run-configuration.md

Update `.claude/run-configuration.md` with:
- User-approved permissions
- Execution timestamp
- Change statistics for local settings
- Global settings modifications (if any):
  - Count of marketplace wildcards added (if any)
  - Count of marketplace permissions added to global
  - List of permissions added
  - Success/failure status
- User decisions (moved to global vs. skipped)

## CRITICAL RULES

**Security:**
- Never auto-remove suspicious permissions without user confirmation
- Never move Write(.claude/settings.local.json) to allow
- Always move system temp permissions to deny
- Always validate permission syntax
- **Never write to global settings without user approval** (unless auto-fix is set)
- Create backup before modifying global settings
- Rollback global changes on write failure

**Data Integrity:**
- Preserve JSON formatting (2-space indent)
- Validate JSON structure before/after
- Never lose existing permissions without user approval
- Always sort lists consistently
- **Validate global settings JSON before and after write**
- **Check for duplicates before adding to global**
- **Never corrupt global settings file** (atomic write with backup)

**User Experience:**
- Show clear summary of changes
- Explain why permissions are suspicious
- Track user-approved permissions
- Provide detailed change breakdown
- **Clearly indicate global vs local changes**
- **Provide options for moving marketplace permissions to global**
- **Explain consequences of moving to global** (available in all projects)

## USAGE EXAMPLES

**Basic Verification:**
```
/setup-project-permissions
```

**Add Permission:**
```
/setup-project-permissions add="Edit(//~/git/project/**)"
```

**Preview Mode:**
```
/setup-project-permissions dry-run
```

**Auto-Fix:**
```
/setup-project-permissions auto-fix
```

**Ensure Specific Permissions:**
```
/setup-project-permissions ensurePermissions="Bash(grep:*),Bash(find:*)"
```

**Note:** Marketplace permissions are always moved to global settings (with user confirmation prompt unless auto-fix is used).

## IMPORTANT NOTES

**Settings Location:**
1. `./.claude/settings.local.json` (project-specific, preferred)
2. `~/.claude/settings.local.json` (global fallback)

**Global/Local Architecture:**
- Global: Universal read access, common tools, all skills
- Local: Project-specific Edit/Write only (2-3 permissions typical)
- Read covered globally via `Read(//~/git/**)`

**Default Permissions:**
- Project Edit/Write added automatically
- Project scripts Bash added if scripts/ exists
- Read NOT added (globally covered)
- **Marketplace skills/commands NOT added** (should be in global settings via wildcards, not project-specific)
- WebFetch domains NOT added (domain-specific permissions should be in global settings)

## ARCHITECTURE

This command orchestrates permission management using:
- **permission-management skill** for validation, architecture, anti-patterns
- Tool usage: Read (JSON), Glob (file discovery), Edit (JSON updates)
- References standards instead of embedding detailed logic

## RELATED

- `/tools-audit-permission-wildcards` - Analyzes marketplace to generate required wildcard permissions
- `/cui-fix-intellij-diagnostics` - Uses ensurePermissions for MCP validation
- Permission architecture defined in permission-management skill
