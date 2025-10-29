---
name: cui-setup-project-permissions
description: Verify and fix permissions in settings by removing duplicates, fixing formats, and ensuring proper organization
---

# Setup Project Permissions Command

Verifies and fixes permissions in `.claude/settings.local.json` by removing duplicates and suspicious permissions, fixing path formats, managing temp directory permissions, and ensuring proper permission organization.

## GLOBAL/LOCAL ARCHITECTURE (Updated 2025-10-27)

**Global Permissions** (`~/.claude/settings.json`):
- `Read(//~/git/**)` - Universal read access to ALL git repositories
- All CUI marketplace skills (9 individual skills)
- `WebFetch(domain:*)` - Universal web access
- All common Bash commands (git, mvn, grep, find, etc.)

**Local Permissions** (`.claude/settings.local.json`):
- `Edit(//~/git/{current-project}/**)` - Project-specific editing
- `Write(//~/git/{current-project}/**)` - Project-specific file creation
- `Bash(~/git/{current-project}/scripts/**)` - Project-specific scripts (if applicable)
- **Typically 2-3 permissions per project**

**Key Principle:** Local settings should ONLY contain project-specific Write/Edit permissions. All Read permissions for git repos are globally covered.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a new permission anti-pattern, security issue, or better validation approach, **YOU MUST immediately update this file** with:
1. The new anti-pattern detection logic
2. Improved path normalization rules
3. Additional suspicious permission patterns
4. Better permission categorization methods
5. Enhanced security checks
6. Any lessons learned about permission management

This ensures the command evolves and becomes more effective at detecting permission issues with each execution.

## PARAMETERS

### Optional Parameters

**add=\<permission\>**
- Adds a new permission to the allow list
- Must be valid permission pattern (e.g., `Edit(//path/**)`, `Bash(command:*)`, `WebFetch(domain:example.com)`)
- Will be validated and deduplicated before adding
- Example: `/setup-project-permissions add="Edit(//~/git/project/**)"`
- Note: For git repos, use Edit/Write. Read is globally available via `Read(//~/git/**)`

**ensurePermissions=\<comma-separated-list\>**
- Ensures exact set of permissions are approved for bash commands
- Accepts comma-separated list of permission patterns
- Automatically adds missing permissions
- Detects and reports over-permissions (approved but not in list)
- Decides global vs local placement automatically
- Example: `/setup-project-permissions ensurePermissions="Bash(grep:*),Bash(find:*),Bash(wc:*)"`
- **Use case**: Called by doctor commands to ensure slash commands/agents have needed approvals

**dry-run**
- Preview changes without applying them
- Shows what would be fixed/changed
- No modifications to settings.local.json
- Example: `/setup-project-permissions dry-run`

**auto-fix**
- Automatically apply all safe fixes without prompting
- Still prompts for deletion of suspicious permissions
- Skips confirmation for duplicates, path fixes, sorting
- Example: `/setup-project-permissions auto-fix`

## PARAMETER VALIDATION

**Step 1: Parse Parameters**

Extract parameters from command arguments:
```bash
# Check for add parameter
if [[ "$args" =~ add=([^ ]+) ]]; then
    new_permission="${BASH_REMATCH[1]}"
    # Remove quotes if present
    new_permission="${new_permission//\"/}"
fi

# Check for ensurePermissions parameter
if [[ "$args" =~ ensurePermissions=([^ ]+) ]]; then
    ensure_permissions="${BASH_REMATCH[1]}"
    # Remove quotes if present
    ensure_permissions="${ensure_permissions//\"/}"
    # Split by comma into array
    IFS=',' read -ra required_permissions <<< "$ensure_permissions"
fi

# Check for flags
dry_run=false
auto_fix=false
[[ "$args" =~ dry-run ]] && dry_run=true
[[ "$args" =~ auto-fix ]] && auto_fix=true
```

**Step 2: Validate add Parameter (if provided)**

If `add` parameter is provided:
1. **Validate permission syntax:**
   - Must match pattern: `ToolName(pattern)` or `ToolName(key:value)`
   - Valid tools: Read, Write, Edit, Bash, WebFetch, WebSearch, SlashCommand, Task, etc.
   - Must have opening and closing parentheses
   - Must not be empty

2. **Validate permission pattern:**
   - For Read/Write/Edit: Must be valid file path pattern
   - For Bash: Must be valid command pattern
   - For WebFetch: Must include domain: prefix
   - For SlashCommand: Must start with /

3. **Check for duplicates:**
   - Must not already exist in allow, deny, or ask lists
   - If duplicate found, report error and skip addition

**Example validation:**
```
✅ Valid: Edit(//~/git/project/**) - Project Edit permission
✅ Valid: Write(//~/git/project/**) - Project Write permission
✅ Valid: Bash(grep:*)
⚠️  Valid but redundant: Read(//~/git/project/**) - Covered by global Read(//~/git/**)
❌ Invalid: Read() - Empty pattern
❌ Invalid: InvalidTool(pattern) - Unknown tool
❌ Invalid: Read(//tmp/**) - Suspicious temp path
```

**Step 2.5: Validate ensurePermissions Parameter (if provided)**

If `ensurePermissions` parameter is provided:

1. **Validate each permission in list:**
   - Must match pattern: `ToolName(pattern)` or `ToolName(key:value)`
   - All permissions must be valid syntax
   - If any invalid, report error and exit

2. **Store required permissions:**
   - Keep as array for later comparison
   - Will be used to add missing permissions
   - Will be used to detect over-permissions

**Example validation:**
```
✅ Valid: ensurePermissions="Bash(grep:*),Bash(find:*),Bash(wc:*)"
❌ Invalid: ensurePermissions="InvalidTool(*),Bash()" - Contains invalid patterns
```

**Step 3: Validate Conflicting Parameters**

- `add` and `ensurePermissions` cannot be used together (conflicting operations)
- `dry-run` and `auto-fix` cannot be used together
- If conflicts found, report error and exit

## WORKFLOW INSTRUCTIONS

### Step 1: Read User-Approved Permissions from .claude/run-configuration.md

**Purpose:** Load list of permissions previously flagged as suspicious but kept by user.

**A. Check if .claude/run-configuration.md exists**
```bash
if [ -f .claude/run-configuration.md ]; then
    # File exists, proceed to read
else
    # File doesn't exist, initialize empty approved list
fi
```

**B. Search for setup-project-permissions section**

Look for section:
```markdown
## setup-project-permissions

### User-Approved Permissions

Permissions flagged as suspicious but approved by user:
- Read(//private/tmp/**)
- Bash(dangerous-command:*)
```

**C. Parse approved permissions**
- Extract each line starting with `-` under "User-Approved Permissions"
- Store in `user_approved_permissions` array
- If section not found, initialize empty array

### Step 2: Read Global Permissions from ~/.claude/settings.json

**CRITICAL:** This step ensures we don't duplicate permissions that are already globally approved.

**A. Check if global settings exist**
```bash
global_settings="$HOME/.claude/settings.json"
if [ -f "$global_settings" ]; then
    # Global settings exist, proceed to read
else
    # No global settings, initialize empty arrays
    global_allow=()
    global_deny=()
fi
```

**B. Parse global permissions**
- Read permissions.allow array from global settings.json
- Read permissions.deny array from global settings.json
- Store in `global_allow` and `global_deny` arrays

**C. Display global permissions summary**
```
Global Settings: ~/.claude/settings.json
- Allow list: {count} permissions
- Deny list: {count} permissions

Key global permissions:
- Bash commands: {count} (git, mvn, find, grep, etc.)
- All git repositories: Read(//~/git/**) - Universal git access
- CUI standards: Read(//~/git/cui-llm-rules/**) - Redundant, covered by ~/git/**
- CUI Skills: All 9 marketplace skills
- Claude tools: SlashCommand, Read .claude/**
- WebFetch: domain:* (any domain allowed globally)
```

**D. Create merged global permission set**
- Combine built-in Claude Code permissions (from system instructions)
- Merge with global settings.json permissions
- This represents ALL globally available permissions
- Store as `all_global_permissions` for later comparison

### Step 3: Locate and Read settings.local.json

**A. Determine settings file location**

Search in order:
1. `./.claude/settings.local.json` (project-specific)
2. `~/.claude/settings.local.json` (global fallback)

**B. Read settings file**
```bash
settings_file="./.claude/settings.local.json"
if [ ! -f "$settings_file" ]; then
    settings_file="$HOME/.claude/settings.local.json"
fi

if [ ! -f "$settings_file" ]; then
    echo "❌ ERROR: No settings.local.json found"
    echo "Expected locations:"
    echo "  - ./.claude/settings.local.json"
    echo "  - ~/.claude/settings.local.json"
    exit 1
fi
```

**C. Validate JSON structure**
- Parse JSON to ensure valid format
- Verify permissions object exists
- Verify allow, deny, ask arrays exist
- If invalid, report error and exit

**D. Display current settings summary**
```
Current Settings: {settings_file}
- Allow list: {count} permissions
- Deny list: {count} permissions
- Ask list: {count} permissions
```

### Step 3.5: Ensure Required Permissions (if ensurePermissions parameter provided)

**Skip this step if ensurePermissions parameter not provided.**

**CRITICAL:** This step provides a complete permission verification and sync workflow for doctor commands.

**A. Display what's being ensured**
```
Ensuring Permissions for Command/Agent:
Required permissions ({count}):
- Bash(grep:*)
- Bash(find:*)
- Bash(wc:*)
- Bash(~/git/cui-llm-rules/scripts/validator.sh:*)
```

**B. Check each required permission against all available permissions**

For each required permission:
1. Check if exists in **global permissions** (built-in + global settings.json)
2. Check if exists in **local permissions** (settings.local.json allow list)
3. Categorize result:
   - **GLOBALLY_APPROVED**: Available globally, no local action needed
   - **LOCALLY_APPROVED**: Available locally, already configured
   - **MISSING**: Not approved anywhere, needs to be added

**C. Report current approval status**
```
Permission Status Analysis:

✅ GLOBALLY APPROVED (no local action needed):
- Bash(grep:*) - Available via global settings
- Bash(find:*) - Available via global settings

✅ LOCALLY APPROVED (already configured):
- Bash(~/git/cui-llm-rules/scripts/validator.sh:*)

❌ MISSING (needs approval):
- Bash(wc:*) - Not approved globally or locally
```

**D. Detect over-permissions**

Check local allow list for Bash(...) permissions NOT in required list:
```
⚠️  OVER-PERMISSIONS (approved locally but not required):
- Bash(asciidoctor:*) - Command/agent doesn't use this
- Bash(npm:*) - Command/agent doesn't use this

Security Risk: 2 unnecessary Bash permissions auto-approved
```

**E. Calculate Permission Fit Score**
```
Permission Fit Score: {percentage}%

Formula: (Approved Required / (Required + Over-Permissions)) * 100

Example:
- Required: 4 permissions
- Globally approved: 2
- Locally approved: 1
- Missing: 1
- Over-permissions: 2
Score: (3 / 6) * 100 = 50% (Poor fit)

Ratings:
- 100%: Perfect - All required approved, no over-permissions
- 90-99%: Good - Minor issues
- 70-89%: Fair - Some missing or over-permissions
- <70%: Poor - Needs fixing
```

**F. Prompt for fixes (unless auto-fix mode)**

If missing permissions OR over-permissions found:

```
Permission Issues Found:
- Missing approvals: {count}
- Over-permissions: {count}
- Permission Fit Score: {percentage}% ({rating})

Options:
F - Fix automatically (add missing, prompt for over-permission removal)
R - Review each issue before fixing
S - Skip permission sync (continue with normal workflow)

Please choose [F/r/s]:
```

**If user selects F (Fix) or auto-fix mode:**

1. **Add missing permissions to local allow list**:
   ```
   Adding Missing Permissions to Local:
   + Bash(wc:*)

   ✅ Added 1 permission
   ```

2. **Prompt to remove over-permissions**:
   ```
   Remove Over-Permission: Bash(asciidoctor:*)
   Reason: Command/agent doesn't use asciidoctor

   Remove? [Y/n]:
   ```

   For each over-permission:
   - If yes: Remove from local allow list
   - If no: Keep (user knows best)

3. **Recalculate and report**:
   ```
   ✅ Permission Sync Complete:
   - Added: 1 permission
   - Removed: 2 over-permissions
   - New Permission Fit Score: 100% (Perfect)

   All required permissions approved, no over-permissions.
   ```

**If user selects R (Review):**

For each missing permission:
```
Missing: Bash(wc:*)
Add to local settings? [Y/n]:
```

For each over-permission:
```
Over-permission: Bash(asciidoctor:*)
Remove from local settings? [Y/n]:
```

**If user selects S (Skip):**
- Continue to Step 4 (normal workflow)
- No changes made
- Report: `ℹ️ Skipped permission sync, continuing with verification`

**G. If Permission Fit Score is 100%, skip rest of workflow**

If all required permissions approved AND no over-permissions:
```
✅ Perfect Permission Fit (100%)

All required permissions approved:
- 2 via global settings
- 1 via local settings
- 0 missing
- 0 over-permissions

No further permission changes needed.
Skipping duplicate detection and other verification steps.

Use /setup-project-permissions without parameters to run full verification.
```

**EXIT COMMAND** - Do not continue to Step 4

**H. If changes made, continue to Step 4**

If permission fit not perfect OR user wants full verification:
- Continue to Step 4 (Add New Permission)
- This allows normal workflow to clean up duplicates, paths, etc.

### Step 4: Add New Permission (if add parameter provided)

**Skip this step if add parameter not provided.**

**A. Validate new permission**
- Run validation from PARAMETER VALIDATION section
- If invalid, report error and exit

**B. Check if permission already exists**
- Search allow, deny, and ask lists
- If found, report and skip addition:
  ```
  ⚠️  Permission already exists in {allow|deny|ask} list:
  {permission}

  Skipping addition, continuing with verification...
  ```

**C. Add to allow list**
- Append to permissions.allow array
- Report:
  ```
  ✅ Added new permission to allow list:
  {new_permission}
  ```

### Step 5: Detect Redundant Local Permissions (Already Covered Globally)

**CRITICAL:** This step prevents local settings from duplicating global permissions, keeping local settings minimal and project-specific only.

**A. Check each local permission against global permissions**

For each permission in local allow list:
1. Check if EXACT match exists in `all_global_permissions`
2. Check if COVERED by broader global permission
   - Example: `Read(//~/git/any-project/**)` is covered by global `Read(//~/git/**)`
   - Example: `Read(//~/git/cui-llm-rules/standards/logging/**)` is covered by global `Read(//~/git/**)`
   - Example: `Bash(grep:*)` is covered by global `Bash(grep:*)`
   - Example: `WebFetch(domain:github.com)` is covered by global `WebFetch(domain:*)`
   - Example: `cui-java-core` is covered by global skills
3. Store redundant permissions in `redundant_local_permissions` array

**B. Report redundant permissions found**
```
Redundant Local Permissions Found ({count}):

These permissions are already globally approved and should be removed from local settings:

Exact Duplicates:
1. Bash(grep:*) - Already in global settings.json
2. SlashCommand(/create-agent) - Already in global settings.json

Covered by Broader Global Permission:
3. Read(//~/git/any-project/**) - Covered by global Read(//~/git/**) (UNIVERSAL GIT ACCESS)
4. Read(//~/git/cui-llm-rules/standards/**) - Covered by global Read(//~/git/**)
5. WebFetch(domain:github.com) - Covered by global WebFetch(domain:*)
6. cui-java-core - Covered by global skills

Total redundant: {count}
```

**C. Remove redundant permissions**

If `dry-run`:
- Display what would be removed
- Skip to next step

If `auto-fix`:
- Automatically remove all redundant permissions
- Report: `✅ Removed {count} redundant local permissions (already global)`

If neither flag:
- Prompt user:
  ```
  Remove all redundant permissions from local settings?
  These are already globally approved, so local entries are unnecessary.

  1. Yes - Remove all redundant permissions (RECOMMENDED)
  2. No - Keep redundant permissions (not recommended)

  Choice:
  ```
- If yes, remove redundant permissions
- If no, keep original lists

**D. Identify permissions that should be moved to global**

For permissions in local that are NOT project-specific:
1. Check if permission applies to ALL projects (not just this one)
2. Check if permission contains user-specific paths like `~/git/cui-llm-rules/`
3. Store in `should_be_global` array

If found, suggest to user:
```
ℹ️  Suggestions: These local permissions might be better in global settings:

- Bash(~/tools/common-script.sh:*) - Appears to be a general tool, not project-specific
- Read(//~/templates/**) - Template directory used across projects

Consider moving these to ~/.claude/settings.json for use in all projects.
```

### Step 6: Detect and Remove Duplicate Permissions

**A. Check for duplicates within each list**

For each list (allow, deny, ask):
1. Create sorted unique list
2. Compare with original list
3. Find duplicates

**B. Report duplicates found**
```
Duplicate Permissions Found:
- Read(//path/**) appears 3 times in allow list
- Bash(grep:*) appears 2 times in allow list

Total duplicates: {count}
```

**C. Remove duplicates**

If `dry-run`:
- Display what would be removed
- Skip to next step

If `auto-fix`:
- Automatically remove duplicates
- Report: `✅ Removed {count} duplicate permissions`

If neither flag:
- Prompt user:
  ```
  Remove all duplicates?
  1. Yes - Remove all duplicates
  2. No - Keep duplicates (not recommended)

  Choice:
  ```
- If yes, remove duplicates
- If no, keep original lists

### Step 7: Detect Suspicious Permissions

**A. Define suspicious permission patterns**

Check for:
1. **System temp directories:**
   - `Read(//tmp/**)`
   - `Read(//private/tmp/**)`
   - `Write(//tmp/**)`
   - Any permission accessing `/tmp` or `/private/tmp`

2. **Critical system directories:**
   - `Read(//dev/**)`, `Write(//dev/**)` - Device files (disks, terminals, CPU)
   - `Read(//sys/**)`, `Write(//sys/**)` - System information
   - `Read(//proc/**)`, `Write(//proc/**)` - Process information
   - `Read(//etc/**)`, `Write(//etc/**)` - System configuration
   - `Read(//boot/**)`, `Write(//boot/**)` - Boot files
   - `Read(//root/**)`, `Write(//root/**)` - Root user home
   - Any permission accessing critical system directories

3. **Overly broad wildcards:**
   - `Read(//Users/**)`
   - `Read(//**)`
   - `Bash(*)`
   - Patterns matching entire system

4. **Dangerous commands:**
   - `Bash(rm:*)` without specific path
   - `Bash(sudo:*)`
   - `Bash(chmod:*)`
   - `Bash(dd:*)`

5. **Malformed patterns:**
   - Absolute paths without user-relative format
   - `/Users/oliver/` instead of `~/`
   - Missing wildcards where needed
   - Empty patterns

6. **Redundant patterns:**
   - Specific pattern already covered by broader pattern
   - Example: `Read(//Users/oliver/git/project/src/**)` when `Read(//Users/oliver/git/project/**)` exists

**B. Scan all lists for suspicious patterns**

For each permission in allow, deny, ask:
1. Check against suspicious patterns
2. Exclude from flagging if in user_approved_permissions
3. Store matches in suspicious_permissions array

**C. Report suspicious permissions**
```
Suspicious Permissions Found ({count}):

System Temp Directories (should use target/):
1. Read(//tmp/**) - Allows reading system temp files
2. Read(//private/tmp/**) - Allows reading private temp files

Critical System Directories (SECURITY RISK):
3. Read(//dev/**) - Allows access to device files (disks, terminals, CPU)
4. Read(//etc/**) - Allows access to system configuration

Overly Broad Wildcards (security risk):
5. Read(//Users/**) - Grants access to all user files

Dangerous Commands:
6. Bash(rm:*) - Unrestricted file deletion

Path Format Issues:
7. Read(//Users/oliver/git/**) - Should use ~/git/** instead
```

**D. Prompt user for each suspicious permission**

If `dry-run`:
- Display what would be removed
- Skip to next step

If `auto-fix`:
- Skip prompts for duplicates and path fixes only
- Still prompt for suspicious deletions

For each suspicious permission:
```
Suspicious Permission #{n}:
{permission}

Issue: {description}
Location: {allow|deny|ask}

Actions:
1. Remove - Delete this permission
2. Keep - Mark as approved and keep
3. Move to deny - Add to deny list instead
4. Skip - Leave as-is for now

Choice:
```

Based on choice:
- Remove: Delete from current list
- Keep: Add to user_approved_permissions, keep in list
- Move to deny: Remove from current list, add to deny
- Skip: No action

### Step 8: Fix User-Absolute to User-Relative Paths

**A. Detect user-absolute paths**

Search for patterns:
- `/Users/oliver/` → Should be `~/`
- `/home/username/` → Should be `~/`
- Any hardcoded user home directory

**B. Create path fix mapping**

For each permission with user-absolute path:
```
Path Fixes Needed ({count}):
1. Read(//Users/oliver/git/project/**) → Read(//~/git/project/**)
2. Bash(/Users/oliver/scripts/tool.sh:*) → Bash(~/scripts/tool.sh:*)
```

**C. Apply path fixes**

If `dry-run`:
- Display what would be changed
- Skip to next step

If `auto-fix` or user confirms:
- Replace all user-absolute paths with user-relative
- Report: `✅ Fixed {count} path formats`

### Step 9: Manage System Temp Permissions

**A. Find all system temp permissions in allow list**

Search for:
- Any permission containing `/tmp/` or `/private/tmp/`
- `mktemp`, `tempfile` commands

**B. Remove from allow list**
```
Removing System Temp Permissions from Allow List:
- Read(//tmp/**)
- Read(//private/tmp/**)
- Bash(mktemp:*)

Total: {count} permissions
```

**C. Add to deny list**

For each temp permission removed:
1. Check if already in deny list
2. If not, add to deny list
3. Report:
   ```
   ✅ Added to Deny List:
   - Read(//tmp/**)
   - Read(//private/tmp/**)
   ```

### Step 10: Ensure Write Permission on settings.local.json is in Ask List

**A. Search for Write(.claude/settings.local.json) permission**

Check in:
1. Allow list
2. Deny list
3. Ask list

**B. Take action based on location**

If in **allow list**:
```
⚠️  SECURITY: Write(.claude/settings.local.json) is auto-approved!

This allows Claude to modify permission settings without asking.
Moving to 'ask' list for safety...

✅ Moved to ask list
```
- Remove from allow
- Add to ask (if not already there)

If in **deny list**:
```
⚠️  Write(.claude/settings.local.json) is denied!

This prevents Claude from updating settings even with permission.
Moving to 'ask' list for safety...

✅ Moved to ask list
```
- Remove from deny
- Add to ask (if not already there)

If in **ask list**:
```
✅ Write(.claude/settings.local.json) correctly in ask list
```
- No action needed

If **not found**:
```
⚠️  Write(.claude/settings.local.json) not in any list!

Adding to ask list for explicit permission...

✅ Added to ask list
```
- Add to ask list

### Step 11: Add Default Read Permissions for CUI Standards (If Not Global)

**IMPORTANT:** Only add to local if NOT already covered by global permissions.

**A. Check if CUI standards are already globally available**

Check if `all_global_permissions` contains:
- `Read(//~/git/**)` - Covers ALL git repositories (universal)
- OR `Read(//~/git/cui-llm-rules/**)` - Covers ALL cui-llm-rules
- OR specific: `Read(//~/git/cui-llm-rules/standards/**)`

If GLOBALLY covered:
```
✅ CUI Standards already globally available via:
- Read(//~/git/**) in global settings (UNIVERSAL GIT ACCESS)

This covers ALL git repositories including cui-llm-rules.
Skipping local addition (not needed).
```
- Skip to next step

**B. Define default standard permissions (if not global)**

If NOT globally covered, these are required permissions:
```
Read(//~/git/cui-llm-rules/standards/**)
Read(//~/git/cui-llm-rules/standards/documentation/**)
Read(//~/git/cui-llm-rules/standards/process/**)
Read(//~/git/cui-llm-rules/standards/testing/**)
Read(//~/git/cui-llm-rules/standards/logging/**)
```

**C. Check which permissions are missing from LOCAL**

For each standard permission:
1. Check if exists in LOCAL allow list
2. Check if NOT covered by global
3. If missing from both, add to missing_standards array

**D. Add missing standard permissions to LOCAL**

If missing permissions found:
```
Adding Default Standard Permissions to LOCAL ({count}):
- Read(//~/git/cui-llm-rules/standards/**)
- Read(//~/git/cui-llm-rules/standards/documentation/**)

⚠️  RECOMMENDATION: Consider adding Read(//~/git/**) to global settings.json
instead, so ALL git repositories are accessible to all projects (universal access).
```

If `dry-run`:
- Display what would be added
- Skip to next step

If `auto-fix` or user confirms:
- Add missing permissions to LOCAL allow list
- Report: `✅ Added {count} standard permissions to local settings`
- Suggest moving to global

### Step 12: Add Default Project Permissions (CRITICAL)

**CRITICAL IMPROVEMENT:** This step ensures Edit/Write permissions for the current project are added locally.

**IMPORTANT:** As of 2025-10-27, `Read(//~/git/**)` is globally available, so Read permissions for any git project are NOT needed locally. Only Edit and Write permissions should be added.

**A. Detect current git repository**

```bash
# Get git repository root
repo_root=$(git rev-parse --show-toplevel 2>/dev/null)

if [ -z "$repo_root" ]; then
    echo "⚠️  Not in a git repository, skipping project permissions"
else
    # Convert to user-relative path
    repo_path="${repo_root/#$HOME/~}"

    echo "📁 Detected git repository: $repo_path"
fi
```

**B. Define default project permissions**

If in a git repository, these permissions are CRITICAL for development:
```
Edit(//~/git/{repo-name}/**)   - Edit any project file
Write(//~/git/{repo-name}/**)  - Create new project files
```

**Note:** `Read(//~/git/{repo-name}/**)` is NOT needed because `Read(//~/git/**)` is globally available.

**C. Check which project permissions are missing**

For each project permission (Edit, Write):
1. Check if exists in allow list (exact or broader match)
2. If missing, add to missing_project_perms array
3. **Skip Read** - already globally available via `Read(//~/git/**)`

**D. Add missing project permissions**

If missing permissions found:
```
Adding Default Project Permissions ({count}):
- Edit(//~/git/{repo-name}/**) - Edit project files
- Write(//~/git/{repo-name}/**) - Create new files

Note: Read permission already globally available via Read(//~/git/**)
These Edit/Write permissions are essential for development work on this project.
```

If `dry-run`:
- Display what would be added
- Skip to next step

If `auto-fix` or user confirms:
- Add missing permissions to allow list
- Report: `✅ Added {count} project permissions`

**E. Add project scripts permissions (if scripts/ exists)**

```bash
if [ -d "$repo_root/scripts" ]; then
    # Only add Bash execution permission
    # Read permission already covered by global Read(//~/git/**)
    scripts_bash="Bash(~/git/{repo-name}/scripts/**)"

    # Check if missing and add
fi
```

**Note:** `Read(//~/git/{repo-name}/scripts/**)` is NOT needed because `Read(//~/git/**)` globally covers all git repos including scripts directories.

### Step 13: Add Recommended WebFetch Domains (OPTIONAL)

**A. Detect project type**

```bash
# Check for Java/Maven project
if [ -f "pom.xml" ]; then
    project_type="java-maven"
# Check for Node.js project
elif [ -f "package.json" ]; then
    project_type="nodejs"
# Check for Python project
elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    project_type="python"
else
    project_type="unknown"
fi
```

**B. Define recommended domains by project type**

```
Java/Maven projects:
- WebFetch(domain:maven.apache.org)
- WebFetch(domain:docs.oracle.com)
- WebFetch(domain:junit.org)
- WebFetch(domain:quarkus.io)
- WebFetch(domain:stackoverflow.com)

Node.js projects:
- WebFetch(domain:nodejs.org)
- WebFetch(domain:npmjs.com)
- WebFetch(domain:developer.mozilla.org)
- WebFetch(domain:stackoverflow.com)

Python projects:
- WebFetch(domain:python.org)
- WebFetch(domain:pypi.org)
- WebFetch(domain:docs.python.org)
- WebFetch(domain:stackoverflow.com)
```

**C. Check which domains are missing**

For each recommended domain:
1. Check if exists in allow list
2. If missing, add to missing_domains array

**D. Optionally add recommended domains**

If missing domains found:
```
Recommended WebFetch Domains for {project_type} ({count}):
- WebFetch(domain:maven.apache.org) - Maven documentation
- WebFetch(domain:docs.oracle.com) - Java API documentation
- WebFetch(domain:junit.org) - JUnit testing framework
- WebFetch(domain:stackoverflow.com) - Developer Q&A

Add these domains? (Optional but recommended)
1. Yes - Add all recommended domains
2. No - Skip domain additions

Choice:
```

If user chooses yes or `auto-fix`:
- Add missing domains to allow list
- Report: `✅ Added {count} documentation domains`

If user chooses no or `dry-run`:
- Skip domain additions
- Report: `ℹ️  Skipped {count} optional domain additions`

### Step 14: Sort All Permission Lists Alphabetically

**A. Sort each list**

For allow, deny, and ask lists:
1. Sort alphabetically (case-insensitive)
2. Group by permission type (Read, Write, Bash, etc.)
3. Within each group, sort by pattern

**Sorting order:**
```
1. Bash(...) commands
2. Edit(...) permissions
3. Read(...) permissions
4. SlashCommand(...) permissions
5. Task(...) permissions
6. WebFetch(...) permissions
7. WebSearch
8. Write(...) permissions
```

**B. Report sorting**
```
✅ Sorted all permission lists alphabetically
```

### Step 15: Preview or Apply Changes

**A. Generate change summary**

Calculate:
- Permissions added: {count}
- Permissions removed: {count}
- Permissions moved: {count}
- Duplicates removed: {count}
- Paths fixed: {count}
- Total changes: {count}

**B. Display comprehensive summary**

```
╔════════════════════════════════════════════════════════════╗
║          Permission Setup Summary                          ║
╔════════════════════════════════════════════════════════════╝

Changes Made:
- ✅ Added {count} new permissions
- ✅ Removed {count} duplicate permissions
- ✅ Removed {count} suspicious permissions
- ✅ Fixed {count} path formats (user-absolute → user-relative)
- ✅ Moved {count} system temp permissions to deny list
- ✅ Ensured Write(.claude/settings.local.json) in ask list
- ✅ Added {count} default standard permissions
- ✅ Added {count} default project permissions
- ✅ Added {count} optional documentation domains
- ✅ Sorted all permission lists alphabetically

Final Permission Counts:
- Allow list: {count} permissions
- Deny list: {count} permissions
- Ask list: {count} permissions

User-Approved Suspicious Permissions: {count}
(Tracked in .claude/run-configuration.md)

╚════════════════════════════════════════════════════════════
```

**C. Display detailed changes**

For each change category:
```
Added Permissions:
+ Edit(//~/git/OAuth-Sheriff/**) - Edit project files
+ Write(//~/git/OAuth-Sheriff/**) - Create project files

Removed Permissions (redundant - globally covered):
- Read(//~/git/OAuth-Sheriff/**) - Covered by global Read(//~/git/**)
- Read(//~/git/cui-llm-rules/**) - Covered by global Read(//~/git/**)
- cui-java-core - Covered by global skills
- WebFetch(domain:github.com) - Covered by global WebFetch(domain:*)

Path Fixes Applied:
  Read(//Users/oliver/git/**) → Read(//~/git/**)
  Bash(/Users/oliver/scripts/**) → Bash(~/scripts/**)

Moved to Deny:
→ Read(//tmp/**)
→ Read(//private/tmp/**)
```

**D. Apply changes or preview only**

If `dry-run`:
```
🔍 DRY RUN MODE - No changes applied

The above changes would be applied to:
{settings_file}

To apply these changes, run without dry-run flag.
```
- Exit without modifying settings.local.json
- Skip Step 14

If NOT dry-run:
- Write updated JSON to settings.local.json
- Preserve JSON formatting (2-space indent)
- Report: `✅ Updated {settings_file}`

### Step 16: Update .claude/run-configuration.md with User-Approved Permissions

**Skip this step if dry-run mode.**

**A. Create or update setup-project-permissions section**

If .claude/run-configuration.md exists:
1. Search for `## setup-project-permissions` section
2. If found, replace entire section
3. If not found, append new section

If .claude/run-configuration.md doesn't exist:
1. Create new file
2. Add setup-project-permissions section

**B. Write section content**

Write `## setup-project-permissions` section to .claude/run-configuration.md with:
- User-approved permissions list (or "None" if empty)
- Last execution timestamp and change statistics
- Permission categories breakdown (Bash, Edit, Read, Write, etc.)
- Security notes (removed permissions, path security, settings protection)

**C. Report update**
```
✅ Updated .claude/run-configuration.md
- User-approved permissions: {count}
- Last execution timestamp recorded
```

## CRITICAL RULES

### Security Rules

- **NEVER auto-remove suspicious permissions without user confirmation** - Always prompt for deletion decisions
- **NEVER move Write(.claude/settings.local.json) to allow** - Must stay in ask for security
- **ALWAYS move system temp permissions to deny** - These are security risks in Maven contexts
- **ALWAYS validate permission syntax** before adding new permissions
- **NEVER apply changes in dry-run mode** - Strictly preview only
- **ALWAYS add project Read/Edit/Write permissions** - Critical for development work

### Data Integrity Rules

- **ALWAYS preserve JSON formatting** - Use 2-space indentation
- **ALWAYS validate JSON structure** before and after changes
- **ALWAYS create backup** of settings.local.json before modifications (mentally note original state)
- **NEVER lose existing permissions** - Only remove with user approval or duplicate detection
- **ALWAYS sort lists consistently** - Alphabetical order for maintainability

### User Experience Rules

- **ALWAYS show clear summary** of what will change
- **ALWAYS explain why permissions are suspicious** - Help user make informed decisions
- **ALWAYS track user-approved permissions** - Don't re-flag approved suspicious permissions
- **PROVIDE detailed change breakdown** - User should understand every modification
- **USE clear prompts** - Number choices, explain consequences

### Path Handling Rules

- **ALWAYS convert user-absolute to user-relative** - Use `~/` instead of `/Users/username/`
- **NEVER break valid path patterns** - Preserve wildcards and glob patterns
- **ALWAYS validate paths after conversion** - Ensure patterns still work
- **HANDLE edge cases** - Check for paths that can't be made user-relative

### State Management Rules

- **ALWAYS persist user-approved permissions** - Track in .claude/run-configuration.md
- **NEVER re-prompt for approved permissions** - Respect user decisions
- **UPDATE state after every run** - Keep .claude/run-configuration.md current
- **INCLUDE timestamps** - Track when permissions were approved

## USAGE EXAMPLES

### Basic Usage (Verify and Fix)
```
/setup-project-permissions
```
- Reads `./.claude/settings.local.json`
- Detects duplicates, suspicious permissions, path issues
- **Automatically adds project Edit/Write permissions** (Read is global)
- Removes redundant permissions covered by global settings
- Prompts for each change
- Applies fixes and sorts lists

### Add New Permission
```
/setup-project-permissions add="Edit(//~/git/new-project/**)"
```
- Adds new permission to allow list
- Then runs full verification and fixing
- Note: Use Edit/Write for project permissions, Read is globally covered via Read(//~/git/**)

### Preview Mode (No Changes)
```
/setup-project-permissions dry-run
```
- Shows what would be changed
- No modifications applied
- Useful for checking current state

### Auto-Fix Safe Changes
```
/setup-project-permissions auto-fix
```
- Automatically removes duplicates
- Automatically fixes paths
- Automatically adds project permissions
- Automatically sorts lists
- Still prompts for suspicious permission deletions

### Combined Parameters
```
/setup-project-permissions add="Bash(~/tools/custom.sh:*)" auto-fix
```
- Adds new permission
- Auto-fixes safe issues
- Prompts only for suspicious deletions

## IMPORTANT NOTES

### Settings File Location

The command searches for settings.local.json in order:
1. `./.claude/settings.local.json` (project-specific, gitignored)
2. `~/.claude/settings.local.json` (global fallback)

**Recommendation:** Use project-specific settings for project-specific permissions.

### Backup and Safety

Before making changes:
- Command validates JSON structure
- Creates mental backup of original state
- Changes are atomic (all or nothing)
- Dry-run mode available for preview

### User-Relative Paths

Some permissions CANNOT be made user-relative:
- System paths: `/etc/`, `/usr/`, `/tmp/`
- Generic patterns: `//**` (matches everything)
- These are flagged as suspicious instead

### Permission Syntax Reference

Valid permission formats:
```
Read(//absolute/path/**)          - File reading
Write(//absolute/path/**)         - File writing
Edit(//absolute/path/**)          - File editing
Bash(command:*)                   - Bash commands
SlashCommand(/command-name)       - Slash commands
WebFetch(domain:example.com)      - Web fetching
WebSearch                         - Web search (no parameters)
Task(...)                         - Task execution
```

### Default Permissions Added Automatically

**CUI Standards (SKIP - globally covered as of 2025-10-27):**
- `Read(//~/git/cui-llm-rules/**)` - Globally available via `Read(//~/git/**)`
- All CUI standards Read permissions are globally covered
- No local additions needed for CUI standards

**Project Permissions (always added if in git repo):**
- `Edit(//~/git/{repo-name}/**)` - Edit project files
- `Write(//~/git/{repo-name}/**)` - Create new project files
- **Read is NOT added** - Already globally available via `Read(//~/git/**)`

**Project Scripts (added if scripts/ directory exists):**
- `Bash(~/git/{repo-name}/scripts/**)` - Execute project scripts
- **Read is NOT added** - Already globally available via `Read(//~/git/**)`

**CUI Skills (SKIP - globally covered as of 2025-10-27):**
- All CUI marketplace skills globally available
- No local additions needed for any CUI skills

**WebFetch Domains (SKIP - globally covered as of 2025-10-27):**
- `WebFetch(domain:*)` is globally available for all domains
- No local additions needed for any domain

### Continuous Evolution

This command improves itself over time. When you discover:
- New anti-patterns (like missing project permissions)
- Better validation rules
- More suspicious permission patterns
- Improved categorization logic

**Update this file** to include these improvements for future runs.

## LESSONS LEARNED

### 2025-10-21: Missing Project Permissions Bug

**Discovery:** Command did not automatically add Read/Edit/Write permissions for current git repository, requiring manual intervention.

**Root Cause:** No step to detect current git repo and add essential development permissions.

**Fix:** Added Step 10 - "Add Default Project Permissions" to automatically detect git repository and add:
- Read(//~/git/{repo-name}/**)
- Edit(//~/git/{repo-name}/**)
- Write(//~/git/{repo-name}/**)

**Impact:** Critical fix - these permissions are essential for any development work. Command now properly supports active development workflows out of the box.

**Validation:** User identified missing Edit permission, leading to discovery that Read and Write were also missing. All three are now added automatically.

### 2025-10-21: Redundant Local Permissions - Global vs Local Architecture

**Discovery:** Local settings.local.json duplicated many permissions already available globally (Bash commands, WebFetch domains, CUI standards, slash commands), creating unnecessary clutter and maintenance burden.

**Root Cause:** Command did not check global settings.json or built-in Claude Code permissions before adding to local settings. This led to:
- 30+ redundant Bash permissions in local (already in global)
- 10+ redundant WebFetch domains in local (global has domain:*)
- Redundant SlashCommand permissions
- Redundant CUI standards Read permissions

**Architecture Problem:** No separation of concerns between:
- **Global permissions**: Apply to ALL projects (common tools, standards)
- **Local permissions**: Project-specific only (this project's files)

**Fix Implemented:**

1. **Updated global settings.json** (`~/.claude/settings.json`) with CUI-specific defaults:
   - `Read(//~/git/cui-llm-rules/\*\*)` - All CUI standards
   - `Read(//~/.claude/agents/\*\*)` - Claude agent definitions
   - `Read(//~/.claude/commands/\*\*)` - Claude command definitions
   - `Bash(~/git/cui-llm-rules/scripts/\*\*)` - CUI validation scripts
   - `SlashCommand(/agents-\*, /slash-\*)` - Global Claude commands

2. **Cleaned local settings** to only project-specific permissions:
   - `Read(//~/git/OAuth-Sheriff/\*\*)`
   - `Edit(//~/git/OAuth-Sheriff/\*\*)`
   - `Write(//~/git/OAuth-Sheriff/\*\*)`
   - Reduced from 30+ permissions to 3 core permissions

3. **Added Step 2**: Read and merge global permissions before processing local

4. **Added Step 4**: Detect redundant local permissions already covered globally

5. **Updated Step 11**: Check global before adding CUI standards to local

**Benefits:**
- **Cleaner local settings**: Only project-specific permissions, easy to understand
- **No duplication**: Global permissions apply to all projects automatically
- **Easier maintenance**: Update global once, applies everywhere
- **Better organization**: Clear separation between global and project concerns

**Impact:** Local settings file reduced from 44 lines to 13 lines. Command now maintains architectural cleanliness and prevents permission drift.

**Validation:** User identified that Bash(cat:*), WebFetch domains, and CUI standards were redundant in local settings, leading to architectural review and global/local separation.

**Best Practice Established:**
- **Global**: Common tools, standards, shared scripts, universal domains, ALL git repos (Read), ALL CUI skills
- **Local**: THIS project's Edit/Write permissions only (Read is global)
- **Command ensures**: Local never duplicates global

### 2025-10-27: Universal Git Access and CUI Skills Globalization

**Enhancement:** Extended global permissions to provide universal git access and all CUI skills globally.

**Changes Made to Global Settings:**

1. **Universal Git Read Access**: Added `Read(//~/git/**)` to global settings
   - Covers ALL git repositories in ~/git/
   - Eliminates need for project-specific Read permissions in local settings
   - `Read(//~/git/cui-llm-rules/**)` now redundant but kept for clarity

2. **Universal CUI Skills Access**: Added individual skills to global settings
   - `cui-documentation` - Documentation standards
   - `cui-frontend-development` - Frontend standards
   - `cui-java-cdi` - CDI and Quarkus standards
   - `cui-java-core` - Core Java standards
   - `cui-java-unit-testing` - Unit testing standards
   - `cui-javadoc` - JavaDoc standards
   - `cui-marketplace-architecture` - Marketplace architecture
   - `cui-project-setup` - Project setup standards
   - `cui-requirements` - Requirements engineering
   - Covers all 9 marketplace skills

**Impact on Command Behavior:**

1. **Step 5 (Redundant Local Permissions)**: Now detects any `Read(//~/git/{project}/**)` as redundant
2. **Step 11 (CUI Standards)**: Skips local addition since `Read(//~/git/**)` covers it
3. **Step 12 (Project Permissions)**: Only adds Edit/Write, skips Read (globally covered)
4. **Step 13 (WebFetch Domains)**: Skips all domains since `domain:*` is global

**New Local Settings Profile:**

Typical local settings now contain ONLY:
- `Edit(//~/git/{current-project}/**)` - Project-specific editing
- `Write(//~/git/{current-project}/**)` - Project-specific file creation
- `Bash(~/git/{current-project}/scripts/**)` - Project-specific script execution (if scripts/ exists)

**Benefits:**
- **Minimal local settings**: Typically 2-3 permissions per project
- **Universal read access**: Can reference any git repo from any project
- **Simplified onboarding**: New projects start with minimal config
- **Consistency**: Same global permissions across all projects

**Architecture Now:**
- **Global (~/.claude/settings.json)**: Universal read access, all tools, all skills, all domains
- **Local (.claude/settings.local.json)**: THIS project's write capabilities only