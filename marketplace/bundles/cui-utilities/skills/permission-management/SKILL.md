---
name: permission-management
description: Permission validation, architecture patterns, anti-patterns, and best practices for Claude Code settings management
allowed-tools:
  - Read
  - Grep
  - Bash
  - Edit
  - Skill
---

# Permission Management Skill

Comprehensive permission management patterns for Claude Code settings, including validation, architecture, security anti-patterns, and lessons learned from production usage.

## What This Skill Provides

### Permission Validation Standards
- Syntax validation patterns for all permission types
- Path format validation rules
- Duplicate detection algorithms
- Permission categorization logic

### Architecture Patterns
- Global vs Local permission separation
- Universal git access patterns
- Project-specific permission patterns
- Skill and tool permission organization

### Security Anti-Patterns
- Suspicious permission detection patterns
- Critical system directory checks
- Dangerous command patterns
- Overly broad wildcard detection

### Wildcard Permission Generation
- Marketplace inventory analysis
- Bundle-based wildcard generation
- Short-form command permissions
- relative path architecture compliance

### Historical Lessons
- Production issues discovered and resolved
- Architecture evolution and rationale
- Best practices established over time

## When to Activate This Skill

Activate when:
- Building permission management commands
- Validating permission syntax
- Detecting security anti-patterns
- Understanding global/local architecture
- Implementing permission doctor commands
- **Auditing marketplace permission wildcards**

## Workflows

### Workflow: Permission Validation

#### Step 1: Load Permission Standards

```
Read: standards/permission-validation-standards.md
Read: standards/permission-architecture.md
Read: standards/permission-anti-patterns.md
```

#### Step 2: Apply Standards

Use loaded standards for:
- Permission syntax validation
- Global/local categorization
- Anti-pattern detection
- Security checks

#### Step 3: Reference Best Practices

```
Read: best-practices/lessons-learned.md
```

Apply lessons learned to avoid known pitfalls.

---

### Workflow: Audit Permission Wildcards

Scans marketplace bundles and generates the minimal set of wildcard permissions needed to cover all marketplace tools.

#### Step 1: Initialize Audit

Display:
```
╔════════════════════════════════════════════════════════════╗
║     Marketplace Permission Wildcard Audit Starting         ║
╚════════════════════════════════════════════════════════════╝

Scanning marketplace bundles...
```

#### Step 2: Get Marketplace Inventory

Invoke the marketplace-inventory skill to scan all bundles:

```
Skill: cui-plugin-development-tools:marketplace-inventory
```

The skill returns JSON with all marketplace resources (bundles, agents, commands, skills, scripts).

#### Step 3: Generate Permission Wildcards

Resolve script path:
```
Skill: cui-utilities:script-runner
Resolve: cui-utilities:permission-management/scripts/generate-permission-wildcards.py
```

Pass the inventory JSON to the wildcard generator script:
```bash
echo '<inventory-json>' | python3 {resolved_path} --format json
```

The script analyzes inventory and outputs:
- Statistics (bundles, skills, commands, wildcards)
- Skill bundle wildcards: `Skill({bundle-name}:*)`
- Command bundle wildcards: `SlashCommand(/{bundle-name}:*)`
- Command short-form permissions: `SlashCommand(/{command-name}:*)`

**Note:** Script permissions are NOT generated. The relative paths pattern in SKILL.md handles script portability automatically - Claude resolves relative paths at runtime to the skill's mounted directory.

#### Step 4: Display Results

Format and display the analysis results:

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
{For each bundle from script output}

Required Wildcard Permissions:
  Skills (Bundle Wildcards):
    {list from script output}

  SlashCommands (Bundle Wildcards):
    {list from script output}

  SlashCommands (Short-Form Permissions):
    {list from script output}

Note: Script permissions are handled by relative path architecture - no permissions needed.

Coverage Verification:
  {coverage info from script output}
```

#### Step 5: Update Configuration (if not dry-run)

If `--dry-run` is NOT specified:

**A. Read current tools-setup-project-permissions.md:**
```
Read: marketplace/bundles/cui-utilities/commands/tools-setup-project-permissions.md
```

**B. Locate and update Step 3E section with generated wildcards**

The section should list:
- Skills: {skill wildcard patterns}
- SlashCommands: {command wildcard patterns}
- Short-form: {short-form command patterns}

**C. Edit the file to update the wildcards list**

```
Edit: marketplace/bundles/cui-utilities/commands/tools-setup-project-permissions.md
```

#### Step 6: Display Summary

```
╔════════════════════════════════════════════════════════════╗
║                    Audit Summary                           ║
╚════════════════════════════════════════════════════════════╝

Marketplace Coverage: 100%
- All {skills_found} skills covered by bundle wildcards
- All {commands_found} commands covered (bundle + short-form)
- Scripts handled by relative path architecture (no permissions needed)

{if not dry-run}
✅ tools-setup-project-permissions.md updated
{else}
ℹ️  Dry-run mode: No files modified
{endif}

Next Steps:
1. Review generated wildcards above
2. Run /tools-setup-project-permissions to apply changes
3. Verify permissions in settings files
```

---

## Scripts

- `scripts/generate-permission-wildcards.py` - Analyzes inventory JSON and generates permission wildcards

## Standards Organization

- `standards/permission-validation-standards.md` - Validation patterns, syntax rules, categorization
- `standards/permission-architecture.md` - Global/Local separation, universal access patterns
- `standards/permission-anti-patterns.md` - Security patterns, suspicious permission detection
- `best-practices/lessons-learned.md` - Historical issues, evolution, established practices

## Integration

Commands using this skill:
- `tools-setup-project-permissions` - Main permission management command
- `tools-audit-permission-wildcards` - Wildcard audit command
- Doctor commands validating permission requirements
- Security audit commands

## Non-Prompting Requirements

This skill is designed to run without user prompts. Required permissions:

**Skill Invocations (covered by bundle wildcards):**
- `Skill(cui-utilities:*)` - This skill
- `Skill(cui-plugin-development-tools:*)` - marketplace-inventory skill

**Script Execution (covered by project permissions):**
- `Bash(python3:*)` - Python interpreter
- `Bash(scripts/generate-permission-wildcards.py:*)` - Wildcard generator

**File Operations (covered by project permissions):**
- `Read(//marketplace/**)` - Read marketplace files
- `Edit(//marketplace/**)` - Edit command files (for non-dry-run updates)

**Ensuring Non-Prompting:**
- All file reads use relative paths within marketplace/
- Script invocation uses `scripts/` which resolves to skill's mounted path
- Skill invocations use bundle-qualified names covered by `Skill({bundle}:*)` wildcards
- Python3 execution covered by standard `Bash(python3:*)` permission

## Critical Rules

**Wildcard Generation:**
- Generate one `Skill({bundle-name}:*)` per bundle with skills
- Generate one `SlashCommand(/{bundle-name}:*)` per bundle with commands
- Generate one `SlashCommand(/{command-name}:*)` per command (short-form)
- NEVER use wildcards in bundle names (e.g., `cui-*:*` is invalid)
- Permission validation regex requires exact bundle names
- **Script permissions are NOT generated** - the relative paths pattern handles this automatically

**Script Invocation:**
- Always use `scripts/` for script paths
- Pass inventory as stdin to Python script
- Script handles all pattern analysis and wildcard generation

**Non-Prompting Compliance:**
- Use only tools listed in `allowed-tools` frontmatter
- Use only paths covered by existing permission wildcards
- Never prompt for confirmation - workflow is fully automated

Part of: cui-utilities bundle
