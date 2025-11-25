---
name: tools-setup-project-permissions
description: Verify and fix permissions in settings by removing duplicates, fixing formats, and ensuring proper organization
---

# Setup Project Permissions Command

Verifies and fixes permissions in `.claude/settings.json` (project-level settings) using permission management standards from the `permission-management` skill.

## Project-Level vs Global Settings

**Focus: Project-Level Settings** (`.claude/settings.json`)

This command focuses on **project-level settings** for version-controlled projects like the CUI marketplace:

**When to use project-level** (`.claude/settings.json`):
- ✅ Team projects (version controlled, committed to git)
- ✅ Project-specific scripts (e.g., skill scripts in `marketplace/bundles/.../scripts/`)
- ✅ Project-specific permissions everyone needs
- ✅ Shareable configuration across team

**When to use global** (`~/.claude/settings.json`):
- ✅ Personal tools (work across all projects)
- ✅ Common development tools (git, npm, docker)
- ✅ User-specific preferences
- ✅ Universal read access patterns

**Settings Hierarchy**:
1. Global (`~/.claude/settings.json`) - Base permissions for all projects
2. Project (`.claude/settings.json`) - Project-specific, team-shared (committed)
3. Local (`.claude/settings.local.json`) - Personal overrides (not committed)

**CRITICAL**: Project-level settings can restrict global permissions. For agents to access tools, permissions must be in **both** global AND project-level settings.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=tools-setup-project-permissions update="[your improvement]"` with:
1. Improved permission validation patterns and syntax checking techniques
2. Better methods for detecting and consolidating redundant permissions
3. More effective consolidation strategies for global vs local permissions
4. Enhanced path normalization and format fixing approaches
5. Any lessons learned about permission architecture patterns
6. Improvements to global settings write workflow and safety checks
7. Better user experience patterns for permission management
8. Optimizations for marketplace permission management (e.g., using wildcards instead of scanning)
9. **CRITICAL LESSON - Command Invocation Forms:** Commands can be invoked in TWO ways: (a) Short form: `/plugin-diagnose-agents` and (b) Bundle-qualified: `/cui-plugin-development-tools:plugin-diagnose-agents`. Bundle wildcards like `SlashCommand(/cui-plugin-development-tools:*)` ONLY match bundle-qualified invocations. Short-form invocations require INDIVIDUAL permissions like `SlashCommand(/plugin-diagnose-agents:*)`. Step 3E lists BOTH bundle wildcards (16 patterns) AND short-form permissions (35 patterns) to cover all invocation methods. The pattern `SlashCommand(/plugin-*:*)` is INVALID - you cannot wildcard command names, only use `:*` after exact bundle/command names.
10. **CRITICAL LESSON - Script Permissions via script-runner:** Skill scripts require explicit permissions because relative paths resolve from cwd, not skill directory. The `script-runner` skill discovers scripts and generates permissions in `.claude/scripts.local.json`. This command syncs those permissions to global settings. See Step 3F for script permission sync workflow.

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

Activate `cui-utilities:claude-run-configuration` skill to read user-approved suspicious permissions:

```
Skill: cui-utilities:claude-run-configuration
Workflow: Read Configuration
Field: commands.setup-project-permissions.user_approved_permissions
```

### Step 3: Read Global and Local Permissions

**A. Load global permissions** from `~/.claude/settings.json`

**B. Load project-level settings**:
- `./.claude/settings.json` (project-level, version-controlled)
- If not found, check `./.claude/settings.local.json` (legacy fallback)

**C. Validate JSON structure**

**D. Ensure global marketplace permissions:**

**Bundle Wildcards:**
- Skills: `Skill(cui-documentation-standards:*)`, `Skill(cui-frontend-expert:*)`, `Skill(cui-java-expert:*)`, `Skill(cui-maven:*)`, `Skill(cui-plugin-development-tools:*)`, `Skill(cui-requirements:*)`, `Skill(cui-task-workflow:*)`, `Skill(cui-utilities:*)`
- SlashCommands: `SlashCommand(/cui-documentation-standards:*)`, `SlashCommand(/cui-frontend-expert:*)`, `SlashCommand(/cui-java-expert:*)`, `SlashCommand(/cui-maven:*)`, `SlashCommand(/cui-plugin-development-tools:*)`, `SlashCommand(/cui-requirements:*)`, `SlashCommand(/cui-task-workflow:*)`, `SlashCommand(/cui-utilities:*)`

**Short-Form Command Permissions (35 commands):**
- `SlashCommand(/cui-maintain-requirements:*)`
- `SlashCommand(/doc-review-single-asciidoc:*)`
- `SlashCommand(/doc-review-technical-docs:*)`
- `SlashCommand(/java-enforce-logrecords:*)`
- `SlashCommand(/java-fix-javadoc:*)`
- `SlashCommand(/java-generate-coverage:*)`
- `SlashCommand(/java-implement-code:*)`
- `SlashCommand(/java-implement-tests:*)`
- `SlashCommand(/java-maintain-logger:*)`
- `SlashCommand(/java-maintain-tests:*)`
- `SlashCommand(/java-optimize-quarkus-native:*)`
- `SlashCommand(/java-refactor-code:*)`
- `SlashCommand(/js-enforce-eslint:*)`
- `SlashCommand(/js-fix-jsdoc:*)`
- `SlashCommand(/js-generate-coverage:*)`
- `SlashCommand(/js-implement-code:*)`
- `SlashCommand(/js-implement-tests:*)`
- `SlashCommand(/js-maintain-tests:*)`
- `SlashCommand(/js-refactor-code:*)`
- `SlashCommand(/maven-build-and-fix:*)`
- `SlashCommand(/orchestrate-language:*)`
- `SlashCommand(/orchestrate-task:*)`
- `SlashCommand(/orchestrate-workflow:*)`
- `SlashCommand(/plugin-create:*)`
- `SlashCommand(/plugin-doctor:*)`
- `SlashCommand(/plugin-maintain:*)`
- `SlashCommand(/pr-fix-sonar-issues:*)`
- `SlashCommand(/pr-handle-pull-request:*)`
- `SlashCommand(/pr-respond-to-review-comments:*)`
- `SlashCommand(/tools-audit-permission-wildcards:*)`
- `SlashCommand(/tools-fix-intellij-diagnostics:*)`
- `SlashCommand(/tools-manage-web-permissions:*)`
- `SlashCommand(/tools-setup-project-permissions:*)`
- `SlashCommand(/tools-sync-agents-file:*)`
- `SlashCommand(/tools-verify-architecture-diagrams:*)`

**Validation:**
- Check for all patterns above in global settings
- Add missing permissions automatically (no prompt - standard marketplace permissions)
- Remove invalid patterns like `SlashCommand(/plugin-*:*)` if present
- Track: `marketplace_wildcards_added_to_global`, `marketplace_shortform_added_to_global`

**E. Handle Timestamped Build Output Files:**

**Problem:** When maven-builder agent creates timestamped log files (e.g., `build-output-2025-11-20-174411.log`), each unique timestamp requires separate Bash permission approval, leading to:
- Accumulation of individual timestamped entries in settings
- Repeated permission prompts for each build execution
- Settings file bloat with redundant permissions

**Solution:** Use wildcard permissions to cover all timestamped variants:

1. **Detect timestamped build output permissions** in allow list:
   - Pattern: `Bash(/path/to/project/target/build-output-YYYY-MM-DD-HHMMSS.log)`
   - Pattern: `Bash(target/build-output-YYYY-MM-DD-HHMMSS.log)`
   - Pattern: `Bash(**/target/build-output-*.log)` (already correct wildcard)

2. **Consolidate to wildcard permissions:**
   - Replace multiple timestamped entries with:
     - `Bash(/absolute/path/to/project/**/target/build-output-*.log)` (absolute paths)
     - `Bash(**/target/build-output-*.log)` (relative paths)

3. **Remove individual timestamped entries:**
   - Track removed: `timestamped_build_outputs_consolidated`
   - Example cleanup: Remove 5+ individual timestamps, replace with 2 wildcards

**Benefits:**
- Single wildcard covers all future builds
- No more permission prompts for each build
- Cleaner settings file
- Works for nested module builds (e.g., `oauth-sheriff-core/target/build-output-*.log`)

**Track:** `timestamped_build_outputs_consolidated`, `build_output_wildcards_added`

**F. Sync Skill Script Permissions from scripts.local.json:**

**Purpose:** Skill scripts require explicit Bash permissions. The `script-runner` skill discovers scripts and stores permission patterns in `.claude/scripts.local.json`. This step syncs those permissions to global settings.

**Steps:**

1. **Check for scripts.local.json:**
   ```
   Read .claude/scripts.local.json
   ```
   - If not found: Skip this step (suggest running `/tools-discover-skill-scripts`)
   - If found: Continue with steps below

2. **Extract marketplace identifier and permissions:**
   ```json
   {
     "marketplace": "cui-development-standards",
     "permissions": [
       "Bash(bash /path/to/skill/scripts/*.sh:*)",
       "Bash(python3 /path/to/skill/scripts/*.py:*)"
     ]
   }
   ```

3. **Remove old script permissions for this marketplace:**

   In global settings `permissions.allow`, remove entries matching:
   - `Bash(bash */{marketplace_base_path}/*/skills/*/scripts/*.sh:*)`
   - `Bash(python3 */{marketplace_base_path}/*/skills/*/scripts/*.py:*)`

   Where `{marketplace_base_path}` is identified by the marketplace field (e.g., for `cui-development-standards`, look for paths containing `/cui-llm-rules/marketplace/` or similar patterns).

   **Pattern matching logic:**
   - Find any Bash permission containing both `scripts/*.sh` or `scripts/*.py` AND the marketplace's bundle names
   - Remove these before adding new ones (prevents stale permissions)

4. **Add new permissions from scripts.local.json:**

   For each permission in `scripts.local.json.permissions`:
   - Check if already exists in global settings (exact match)
   - If not exists: Add to `permissions.allow`
   - Track: `script_permissions_added_to_global`

5. **Track changes:**
   - `script_permissions_removed`: Count of old permissions removed
   - `script_permissions_added`: Count of new permissions added
   - `scripts_local_json_found`: true/false

**Note:** This is an automatic sync (no user prompt) - script permissions are required for skill functionality and are regenerated by `/tools-discover-skill-scripts`.

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
   - `SlashCommand(/cui-*:*)` - Example: `SlashCommand(/cui-java-expert:cui-java-implement-code)`
   - `SlashCommand(/plugin-*:*)` - Example: `SlashCommand(/plugin-diagnose-bundle)`
   - `SlashCommand(/tools-*:*)` - Example: `SlashCommand(/tools-setup-project-permissions)`

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
- Script permissions: {script_permissions_added} added, {script_permissions_removed} removed
- Status: {moved_to_global_status}
```

**B. Display detailed changes**

**C. Apply changes** (unless dry-run mode)

### Step 15: Update run-configuration.json

Activate `cui-utilities:claude-run-configuration` skill to record execution results:

```
Skill: cui-utilities:claude-run-configuration
Workflow: Update Execution Status
Command: setup-project-permissions
```

Update fields at path `commands.setup-project-permissions`:
- `user_approved_permissions`: User-approved suspicious permissions
- `last_execution`: Execution timestamp and status
- `lessons_learned`: User decisions and important findings

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

## Why Focus on Project-Level Settings?

**For version-controlled projects like CUI marketplace, project-level settings are preferred because:**

1. **Team Collaboration**:
   - Committed to git (`settings.json`)
   - Everyone gets same permissions automatically
   - No manual setup for new team members
   - Consistent development environment

2. **Skill Scripts (Handled by relative paths)**:
   - Scripts in `marketplace/bundles/*/skills/*/scripts/` use relative paths pattern
   - Claude resolves relative paths to skill's mounted location at runtime
   - NO script permissions needed in settings - architecture handles this automatically
   - See `plugin-architecture` skill for full details

3. **Project-Specific Tools**:
   - Project scripts in `scripts/` directory
   - Project-specific bash commands
   - Testing frameworks and tools
   - Build configurations

4. **Settings Hierarchy Protection**:
   - Global settings provide baseline (read access, common tools)
   - Project settings add project-specific needs
   - Local settings for personal experiments only
   - **Critical**: Project settings can restrict global settings (permissions must be in both)

5. **Maintenance Benefits**:
   - Single source of truth (project settings.json)
   - Changes propagate to entire team via git
   - Easier to debug permission issues
   - Version history via git commits

**Global settings remain important for**:
- Cross-project tools (`git:*`, `npm:*`, `docker:*`)
- Universal read access (`Read(//~/git/**)`)
- Marketplace bundle wildcards (`Skill(cui-documentation-standards:*)`, etc.)
- SlashCommand permissions (both bundle and short-form)
- Personal development preferences

**Key Insight**: Project-level settings complement global settings, they don't replace them. For agents to work, permissions often need to be in **BOTH** levels because project settings can restrict global permissions.

## IMPORTANT NOTES

**Settings Location Priority:**
1. **`./.claude/settings.json`** - Project-level (version-controlled, team-shared) **← PRIMARY FOCUS**
2. `./.claude/settings.local.json` - Personal overrides (not committed)
3. `~/.claude/settings.json` - Global user settings (all projects)

**Project-Level Settings Philosophy:**

For version-controlled projects (like CUI marketplace):
- ✅ **Project-level settings** (`.claude/settings.json`) - Committed to git
  - Project Edit/Write permissions
  - Project-specific Read patterns (marketplace/, .claude/, standards/)
  - Team-shared configuration

- ✅ **Global settings** (`~/.claude/settings.json`) - Personal, cross-project
  - Universal read access: `Read(//~/git/**)`
  - Common dev tools: `Bash(git:*)`, `Bash(npm:*)`
  - Marketplace bundle wildcards: `Skill(cui-documentation-standards:*)`, etc.
  - SlashCommand permissions (bundle + short-form)
  - Personal preferences

- ⚙️ **Local settings** (`.claude/settings.local.json`) - Personal overrides only
  - NOT committed to git
  - Temporary experiments
  - User-specific modifications

**CRITICAL Permission Hierarchy**:
- Project-level settings can **restrict** global permissions
- For agents to work: Permissions must be in **BOTH** global AND project-level

**Default Permissions Added to Project-Level:**
- ✅ Project Edit/Write: `Edit(//~/git/{repo}/**)`, `Write(//~/git/{repo}/**)`
- ✅ Project scripts: `Bash(~/git/{repo}/scripts/**)` (if scripts/ exists)
- ❌ Read: NOT added (globally covered via `Read(//~/git/**)`)
- ❌ Marketplace wildcards: NOT added to project (should be in global only)
- ❌ Skill scripts: Synced from `.claude/scripts.local.json` to global settings (see Step 3F)

## ARCHITECTURE

This command orchestrates permission management using:
- **permission-management skill** for validation, architecture, anti-patterns
- Tool usage: Read (JSON), Glob (file discovery), Edit (JSON updates)
- References standards instead of embedding detailed logic

## RELATED

- `/tools-discover-skill-scripts` - Discovers skill scripts and generates `.claude/scripts.local.json`
- `/tools-audit-permission-wildcards` - Analyzes marketplace to generate required wildcard permissions
- `/tools-fix-intellij-diagnostics` - Uses ensurePermissions for MCP validation
- `cui-utilities:script-runner` - Skill for script path resolution
- Permission architecture defined in permission-management skill
