---
name: cui-setup-project-permissions
description: Verify and fix permissions in settings by removing duplicates, fixing formats, and ensuring proper organization
---

# Setup Project Permissions Command

Verifies and fixes permissions in `.claude/settings.local.json` using permission management standards from the `permission-management` skill.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/cui-update-command command-name=cui-setup-project-permissions update="[your improvement]"` with:
1. Improved permission validation patterns and syntax checking techniques
2. Better methods for detecting and consolidating redundant permissions
3. More effective consolidation strategies for global vs local permissions
4. Enhanced path normalization and format fixing approaches
5. Any lessons learned about permission architecture patterns

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

**add=<permission>** - Add new permission to allow list (e.g., `Edit(//~/git/project/**)`)

**ensurePermissions=<list>** - Ensure exact set of permissions (comma-separated)

**dry-run** - Preview changes without applying

**auto-fix** - Automatically apply safe fixes without prompting

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

### Step 4: Handle ensurePermissions Parameter (if provided)

**A. Check each required permission** against global + local

**B. Categorize**:
- GLOBALLY_APPROVED (no action needed)
- LOCALLY_APPROVED (already configured)
- MISSING (needs approval)

**C. Detect over-permissions** (approved locally but not required)

**D. Calculate Permission Fit Score**:
```
Score = (Approved Required / (Required + Over-Permissions)) * 100
- 100%: Perfect
- 90-99%: Good
- 70-89%: Fair
- <70%: Poor
```

**E. Prompt for fixes** or auto-fix if flag set

**F. Exit if 100% fit score**, continue otherwise

### Step 5: Handle add Parameter (if provided)

**A. Validate using permission-validation-standards**

**B. Check for duplicates**

**C. Add to allow list** if valid and unique

### Step 6: Detect Redundant Local Permissions

Check each local permission against global permissions using patterns from permission-architecture standards.

Report and remove redundant:
- Exact duplicates
- Permissions covered by broader global permissions
- Examples: `Read(//~/git/project/**)` covered by global `Read(//~/git/**)`

Suggest moving non-project-specific permissions to global.

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
╔════════════════════════════════════════════════════════════╗
║          Permission Setup Summary                          ║
╚════════════════════════════════════════════════════════════╝

Changes Made:
- Added: {count} new permissions
- Removed: {count} duplicates
- Removed: {count} redundant (globally covered)
- Removed: {count} suspicious
- Fixed: {count} path formats
- Moved: {count} temp permissions to deny

Final Counts:
- Allow list: {count}
- Deny list: {count}
- Ask list: {count}
```

**B. Display detailed changes**

**C. Apply changes** (unless dry-run mode)

### Step 15: Update run-configuration.md

Update `.claude/run-configuration.md` with:
- User-approved permissions
- Execution timestamp
- Change statistics

## CRITICAL RULES

**Security:**
- Never auto-remove suspicious permissions without user confirmation
- Never move Write(.claude/settings.local.json) to allow
- Always move system temp permissions to deny
- Always validate permission syntax

**Data Integrity:**
- Preserve JSON formatting (2-space indent)
- Validate JSON structure before/after
- Never lose existing permissions without user approval
- Always sort lists consistently

**User Experience:**
- Show clear summary of changes
- Explain why permissions are suspicious
- Track user-approved permissions
- Provide detailed change breakdown

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
- CUI standards NOT added (globally covered)
- Skills NOT added (globally covered)
- WebFetch domains NOT added (domain:* globally covered)

## ARCHITECTURE

This command orchestrates permission management using:
- **permission-management skill** for validation, architecture, anti-patterns
- Tool usage: Read (JSON), Glob (file discovery), Edit (JSON updates)
- References standards instead of embedding detailed logic

## RELATED

- `/cui-fix-intellij-diagnostics` - Uses ensurePermissions for MCP validation
- Permission architecture defined in permission-management skill
