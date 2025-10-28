# setup-project-permissions

Comprehensive permission management command that verifies, fixes, and optimizes `.claude/settings.local.json` by removing duplicates, normalizing paths, detecting suspicious permissions, and ensuring proper global/local architecture compliance.

## Purpose

Automates permission configuration by enforcing global/local separation (Read globally, Edit/Write locally), detecting duplicates, normalizing user-absolute paths to user-relative format, flagging suspicious permissions, sorting alphabetically, and ensuring required project permissions exist.

## Usage

```bash
# Verify and fix current project permissions
/setup-project-permissions

# Add specific permission
/setup-project-permissions add="Edit(//~/git/project/**)"

# Ensure specific permissions approved (used by doctor commands)
/setup-project-permissions ensurePermissions="Bash(grep:*),Bash(find:*),Bash(wc:*)"

# Preview changes without applying
/setup-project-permissions dry-run

# Auto-apply all safe fixes
/setup-project-permissions auto-fix

# Combine parameters
/setup-project-permissions add="Write(//~/git/project/**)" auto-fix
```

## What It Does

The command performs comprehensive permission optimization across 13 steps:

1. **Read User-Approved** - Load previously approved suspicious permissions from `.claude/run-configuration.md`
2. **Read Global Permissions** - Parse `~/.claude/settings.json` to avoid duplicates
3. **Read Local Permissions** - Parse `.claude/settings.local.json`
4. **Remove Duplicates** - Delete permissions already in global or appearing multiple times
5. **Detect Suspicious** - Flag security risks (temp paths, dangerous commands)
6. **Fix Path Formats** - Convert `/Users/oliver/` to `~/` (user-relative)
7. **Fix Permission Names** - Normalize wildcards and remove redundancies
8. **Sort Permissions** - Alphabetize within each tool category
9. **Categorize Bash** - Group bash commands by type (common, build, project-specific)
10. **Handle ensurePermissions** - Add missing/remove over-permissions for doctor commands
11. **Add Standards** - Ensure CUI standards access (if not global)
12. **Add Project Defaults** - Ensure Edit/Write for current project
13. **Write Settings** - Save optimized settings.local.json

## Key Features

- **Global/Local Architecture**: Enforces Read globally (`Read(//~/git/**)`), Edit/Write locally
- **Duplicate Detection**: Removes permissions already in global or repeated locally
- **Path Normalization**: Converts user-absolute paths (`/Users/oliver/`, `/home/user/`) to `~/`
- **Suspicious Detection**: Flags temp directories, dangerous commands, unusual patterns
- **Permission Fit Score**: Calculates match quality for ensurePermissions (0-100%)
- **Over-Permission Detection**: Finds approved patterns not used by commands
- **Auto-Categorization**: Places bash commands in global vs local based on type
- **Alphabetical Sorting**: Maintains consistent organization within tool groups
- **User Approval Persistence**: Stores approved suspicious permissions in `.claude/run-configuration.md`
- **Doctor Integration**: `ensurePermissions` parameter for automated verification

## Parameters

### add (Optional)
- **Format**: `add="<permission>"`
- **Description**: Adds new permission to allow list
- **Validation**: Must be valid syntax, not duplicate, not suspicious
- **Examples**:
  - `add="Edit(//~/git/project/**)"`
  - `add="Bash(custom-script:*)"`
  - `add="WebFetch(domain:api.example.com)"`

### ensurePermissions (Optional)
- **Format**: `ensurePermissions="<permission1>,<permission2>,..."`
- **Description**: Ensures exact set of permissions approved
- **Use Case**: Called by doctor commands (diagnose-commands, diagnose-agents)
- **Actions**:
  - Adds missing permissions (globally or locally based on type)
  - Reports over-permissions (approved but not in list)
  - Calculates Permission Fit Score (0-100%)
- **Examples**:
  - `ensurePermissions="Bash(grep:*),Bash(find:*),Bash(wc:*)"`
  - `ensurePermissions="Bash(~/git/project/scripts/validator.sh:*)"`

### dry-run (Optional)
- **Format**: `dry-run` (flag)
- **Behavior**: Preview changes without applying
- **Shows**: What would be removed, added, fixed, sorted

### auto-fix (Optional)
- **Format**: `auto-fix` (flag)
- **Behavior**: Auto-apply safe fixes without prompting
- **Still Prompts**: Deletion of suspicious permissions
- **Auto-Applies**: Duplicate removal, path fixes, sorting, missing additions

## Global/Local Architecture

### Global Permissions (~/.claude/settings.json)

**Should Contain:**
- `Read(//~/git/**)` - Universal read access to ALL git repositories
- `Skill(cui-*-skills:*)` - All CUI skills
- `WebFetch(domain:*)` - Universal web access (if needed)
- `WebSearch` - Web search capability
- Common Bash commands: `git`, `mvn`, `grep`, `find`, `wc`, `ls`, `cat`, etc.

**Typical Count:** 30-50 permissions

### Local Permissions (.claude/settings.local.json)

**Should Contain:**
- `Edit(//~/git/{current-project}/**)` - Project file editing
- `Write(//~/git/{current-project}/**)` - Project file creation
- Project-specific scripts: `Bash(~/git/{project}/scripts/**)`
- Project-specific slash commands

**Should NOT Contain:**
- Read permissions for git repos (globally covered)
- Common bash commands (globally covered)
- Duplicate permissions from global

**Typical Count:** 2-5 permissions per project

### Key Principle

Local settings should ONLY contain **project-specific Write/Edit permissions**. All Read permissions for git repos are globally covered by `Read(//~/git/**)`.

## Permission Fit Score

When `ensurePermissions` parameter is used:

**Score Calculation:**
- 100%: All required permissions approved, no over-permissions
- 80-99%: All required approved, minor over-permissions
- 60-79%: Most required approved, some missing/over
- 40-59%: Significant missing or over-permissions
- 0-39%: Major permission gaps

**Rating Scale:**
- 95-100%: Perfect
- 85-94%: Excellent
- 75-84%: Good
- 65-74%: Fair
- 50-64%: Poor
- 0-49%: Critical

**Components:**
- **Missing Permissions**: Not approved globally or locally
- **Over-Permissions**: Approved locally but not required
- **Globally Approved**: Already available (no local action needed)
- **Locally Approved**: Correctly configured in project

## Duplicate Detection

### Types Detected

1. **Global Duplicates**: Permission exists in `~/.claude/settings.json`
2. **Local Duplicates**: Permission appears multiple times in settings.local.json
3. **Covered by Global**: More specific permission than global pattern
   - Example: `Read(//~/git/project/**)` when `Read(//~/git/**)` exists globally

### Removal Strategy

- Auto-remove global duplicates (safe)
- Auto-remove local duplicates (safe)
- Prompt before removing covered permissions (user may want explicit local control)

## Path Normalization

### Conversions Applied

**User-Absolute → User-Relative:**
- `/Users/oliver/` → `~/`
- `/home/username/` → `~/`
- `/Users/oliver/git/` → `~/git/`

**Double-Slash Prefix:**
- `Read(~/git/**)` → `Read(//~/git/**)`
- `Edit(~/git/**)` → `Edit(//~/git/**)`

**Pattern Normalization:**
- `Read(/path/**/**)`  → `Read(/path/**)`
- `Bash(command:*:*)` → `Bash(command:*)`

## Suspicious Permission Detection

### Security Red Flags

**Temp Directory Access:**
- `Read(//tmp/**)`
- `Read(//private/tmp/**)`
- `Write(//tmp/**)`
- `Bash(mktemp:*)`
- `Bash(tempfile:*)`

**Dangerous Commands:**
- `Bash(rm:*)` - File deletion
- `Bash(dd:*)` - Disk operations
- `Bash(chmod:*)` - Permission changes
- `Bash(sudo:*)` - Elevated privileges
- `Bash(curl:*)` - Network access (use WebFetch instead)

**Unusual Patterns:**
- Write to system directories (`/etc/`, `/usr/`)
- Universal wildcards without justification
- Edit/Write outside `~/git/`

### Handling Strategy

1. Flag suspicious permission
2. Display security concern explanation
3. Prompt user:
   - Remove (default)
   - Keep (requires justification)
   - Skip (decide later)
4. If kept, add to user-approved list in `.claude/run-configuration.md`

## Sorting Pattern

Permissions are sorted to maintain consistency:

### Global Order (within allow list)

1. Bash(...) commands
2. Edit(...) permissions
3. Read(...) permissions
4. Skill(...) permissions
5. SlashCommand(...) permissions
6. Task(...) permissions
7. WebFetch(...) permissions
8. WebSearch
9. Write(...) permissions

### Within Each Category

Alphabetically by pattern:

**Example (Bash):**
```json
"Bash(cat:*)",
"Bash(find:*)",
"Bash(git:*)",
"Bash(grep:*)",
"Bash(ls:*)",
"Bash(mvn:*)",
"Bash(wc:*)"
```

**Example (Read):**
```json
"Read(//claude/**)",
"Read(//standards/**)",
"Read(//Users/oliver/git/**)"
```

## Bash Command Categorization

### Common Commands (Global)

Should always be in `~/.claude/settings.json`:
- `git`, `mvn`, `./mvnw`, `npm`, `yarn`
- `ls`, `cat`, `grep`, `find`, `wc`, `sort`, `uniq`
- `cp`, `mv`, `mkdir`, `touch`, `pwd`, `cd`
- `tar`, `gzip`, `zip`, `unzip`
- `curl`, `wget` (if needed)

### Project-Specific (Local)

Should be in `.claude/settings.local.json`:
- `Bash(~/git/{project}/scripts/**)`
- Custom project scripts
- Project build tools not used globally

## User Approval Persistence

### Storage Location

`.claude/run-configuration.md` in project root

### Format

```markdown
## setup-project-permissions

### User-Approved Permissions

Permissions flagged as suspicious but approved by user:
- Read(//private/tmp/**) - Needed for test fixtures (2025-10-27)
- Bash(dangerous-command:*) - Required for build process (2025-10-27)
```

### Benefits

- Prevents re-prompting for previously approved permissions
- Documents why suspicious permissions are needed
- Tracks decision history with timestamps
- Can be committed to version control for team awareness

## Expected Duration

- **Quick Fix** (0-5 issues): 30-60 seconds
  - Duplicate removal: instant
  - Path normalization: instant
  - Sorting: instant

- **Moderate Cleanup** (5-15 issues): 1-3 minutes
  - Multiple duplicates: 30 sec
  - Path fixes: 30 sec
  - Suspicious review: 1-2 min

- **Major Overhaul** (15+ issues): 3-10 minutes
  - Extensive duplicates: 1-2 min
  - Many path fixes: 1-2 min
  - Multiple suspicious: 2-5 min
  - ensurePermissions analysis: 1-2 min

## Doctor Integration

### ensurePermissions Usage

**Slash-doctor** and **diagnose-agents** use this parameter to verify commands/agents have required bash approvals:

1. Doctor extracts bash commands from workflow
2. Converts to permission format (e.g., `grep` → `Bash(grep:*)`)
3. Calls `/setup-project-permissions ensurePermissions="..."`
4. Receives Permission Fit Score and recommendations
5. Offers to fix missing/over-permissions

**Example from diagnose-commands:**
```bash
# Extract bash commands from command file
required="Bash(grep:*),Bash(find:*),Bash(wc:*),Bash(~/git/project/scripts/validator.sh:*)"

# Verify permissions
/setup-project-permissions ensurePermissions="$required"

# Result: Permission Fit Score 67% (missing 1, over 2)
```

## Integration

Use this command:
- Before starting development on a new project
- After cloning a repository
- When permission prompts appear frequently
- As part of project setup checklist
- Periodically to maintain clean permissions
- After updating global settings

Often used with:
- `/manage-web-permissions` - Optimize WebFetch permissions
- `/diagnose-commands` - Verify slash command permissions
- `/diagnose-agents` - Verify agent permissions

## Example Output

```
╔════════════════════════════════════════════════════╗
║  Permission Setup Complete                         ║
╚════════════════════════════════════════════════════╝

Issues Found: 12

DUPLICATES (5):
- Read(//~/git/**) - Already in global settings ✅
- Read(//~/git/cui-llm-rules/**) - Covered by global Read(//~/git/**) ✅
- Bash(git:*) - Already in global settings ✅
- Edit(//~/git/project/**) - Appears 2 times locally ✅
- Write(//~/git/project/**) - Appears 2 times locally ✅

PATH FORMAT (3):
- Read(//Users/oliver/git/**) → Read(//~/git/**) ✅
- Edit(//Users/oliver/git/project/**) → Edit(//~/git/project/**) ✅
- Bash(/Users/oliver/git/project/scripts/build.sh:*) → Bash(~/git/project/scripts/build.sh:*) ✅

SUSPICIOUS (2):
- Read(//tmp/**) - System temp directory access ⚠️
  REMOVED after user confirmation
- Bash(rm:*) - File deletion risk ⚠️
  REMOVED after user confirmation

SORTING (2):
- Reordered 15 permissions alphabetically within categories ✅

MISSING PROJECT PERMISSIONS (2):
+ Edit(//~/git/cui-llm-rules/**) - Project file editing ✅
+ Write(//~/git/cui-llm-rules/**) - Project file creation ✅

────────────────────────────────────────────────────

Changes Applied:
- Removed: 5 duplicate permissions
- Fixed: 3 path formats
- Deleted: 2 suspicious permissions
- Sorted: 15 permissions
- Added: 2 project permissions

Final State:
- Total permissions: 8
- Global duplicates: 0
- Suspicious patterns: 0
- Path issues: 0
- Sorting: ✅ Consistent

✅ Permissions optimized and secure!
```

## Notes

- **Global/local separation critical**: Read globally, Edit/Write locally
- **Always check global first**: Avoid duplicating globally-approved permissions
- **User approval persisted**: Previously approved suspicious permissions won't re-prompt
- **Suspicious = security risk**: Always review carefully before approving
- **Path normalization improves portability**: `~/` works across users
- **Sorting maintains consistency**: Easier to review and compare
- **Doctor commands rely on ensurePermissions**: Automated verification workflow
- **Dry-run for safety**: Preview changes before applying

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
