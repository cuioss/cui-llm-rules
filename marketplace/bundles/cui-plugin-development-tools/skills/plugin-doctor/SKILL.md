---
name: plugin-doctor
description: Diagnose and fix quality issues in marketplace components with automated safe fixes and prompted risky fixes
allowed-tools:
  - Read
  - Edit
  - Write
  - Bash
  - AskUserQuestion
  - Glob
  - Grep
  - Skill
---

# Plugin Doctor Skill

Comprehensive diagnostic and fix skill for marketplace components. Combines diagnosis, automated safe fixes, prompted risky fixes, and verification into a single workflow.

## Purpose

Provides unified doctor workflows following the pattern: **Diagnose → Auto-Fix Safe → Prompt Risky → Verify**

**5 Doctor Workflows** (one per component type):
1. **doctor-agents**: Analyze and fix agent issues
2. **doctor-commands**: Analyze and fix command issues
3. **doctor-skills**: Analyze and fix skill issues
4. **doctor-metadata**: Analyze and fix plugin.json issues
5. **doctor-scripts**: Analyze and fix script issues

Each workflow performs the complete cycle: discover → analyze → categorize → fix → verify.

## Progressive Disclosure Strategy

**Load ONE reference guide per workflow** (not all 10):

| Workflow | Diagnosis Reference | Fix Reference |
|----------|---------------------|---------------|
| doctor-agents | `agents-guide.md` | `fix-catalog.md` |
| doctor-commands | `commands-guide.md` | `fix-catalog.md` |
| doctor-skills | `skills-guide.md` | `fix-catalog.md` |
| doctor-metadata | `metadata-guide.md` | `fix-catalog.md` |
| doctor-scripts | `plugin-architecture:script-standards.md` | `fix-catalog.md` |

**Context Efficiency**: ~800 lines per workflow vs ~4,000 lines if loading everything.

## Common Workflow Pattern

All 5 workflows follow the same pattern:

### Phase 1: Discover and Analyze

1. **Load Prerequisites**
   ```
   Skill: cui-utilities:cui-diagnostic-patterns
   Skill: cui-plugin-development-tools:plugin-architecture
   Skill: cui-plugin-development-tools:marketplace-inventory
   ```

2. **Load Component Reference** (progressive disclosure)
   ```
   Read references/{component}-guide.md
   ```

3. **Discover Components** (based on scope parameter)
   - marketplace scope: Use marketplace-inventory
   - global scope: Glob ~/.claude/{component}/
   - project scope: Glob .claude/{component}/

4. **Analyze Each Component** (using scripts)

   Resolve script paths via script-runner:
   ```
   Skill: cui-utilities:script-runner
   Resolve: cui-plugin-development-tools:plugin-doctor/scripts/analyze-markdown-file.sh
   Resolve: cui-plugin-development-tools:plugin-doctor/scripts/analyze-tool-coverage.sh
   Resolve: cui-plugin-development-tools:plugin-doctor/scripts/validate-references.py
   ```

   Execute with resolved paths:
   ```bash
   bash {resolved_analyze_markdown} {path} {type}
   bash {resolved_analyze_tool_coverage} {path}
   python3 {resolved_validate_references} {path}
   ```

### Phase 2: Categorize Issues

**Safe Fixes** (auto-apply):
- Missing frontmatter fields
- Invalid YAML syntax
- Unused tools in frontmatter
- Trailing whitespace
- Missing blank lines
- Missing foundation skill loading (plugin-architecture, cui-diagnostic-patterns)
- Incorrect section header case (e.g., `## Workflow` → `## WORKFLOW`)
- Missing CONTINUOUS IMPROVEMENT RULE section (commands only)

**Risky Fixes** (require confirmation):
- Rule 6 violations (Task tool in agents)
- Rule 7 violations (Maven usage)
- Pattern 22 violations (self-invocation)
- Structural changes
- Content removal

### Phase 3: Apply Fixes

1. **Auto-Apply Safe Fixes (NO PROMPT)**

   **CRITICAL**: Safe fixes are applied automatically WITHOUT user confirmation.
   Do NOT use AskUserQuestion for safe fixes.

   - Apply each safe fix immediately using Edit tool
   - Track success/failure
   - Log: "✅ Fixed: {description}"

2. **Prompt for Risky Fixes ONLY**
   ```
   AskUserQuestion:
     question: "Apply fix for {issue}?"
     options:
       - label: "Yes" description: "Apply this fix"
       - label: "No" description: "Skip this fix"
       - label: "Skip All" description: "Skip remaining risky fixes"
   ```

   **Only risky fixes prompt** - safe fixes never prompt.

### Phase 4: Verify and Report

1. **Verify Fixes**

   Resolve script path:
   ```
   Skill: cui-utilities:script-runner
   Resolve: cui-plugin-development-tools:plugin-doctor/scripts/verify-fix.sh
   ```

   Execute:
   ```bash
   bash {resolved_path} {type} {path}
   ```

2. **Generate Summary**
   ```
   Read references/reporting-templates.md
   ```
   Use summary template with metrics.

---

## Workflow 1: doctor-agents

### Parameters
- `scope` (optional, default: "marketplace"): "marketplace" | "global" | "project"
- `agent-name` (optional): Analyze specific agent
- `--no-fix` (optional): Diagnosis only, no fixes

### Step 1: Load Prerequisites and Standards

```
Skill: cui-utilities:cui-diagnostic-patterns
Skill: cui-plugin-development-tools:plugin-architecture
Read references/agents-guide.md
Read references/fix-catalog.md
```

### Step 2: Discover Agents

**marketplace scope** (default):
```
Skill: cui-plugin-development-tools:marketplace-inventory
```

**global/project scope**:
```
Glob: pattern="*.md", path="{scope_path}/agents"
```

### Step 3: Analyze Each Agent

For each agent file, first resolve script paths:

```
Skill: cui-utilities:script-runner
Resolve: cui-plugin-development-tools:plugin-doctor/scripts/analyze-markdown-file.sh
Resolve: cui-plugin-development-tools:plugin-doctor/scripts/analyze-tool-coverage.sh
Resolve: cui-plugin-development-tools:plugin-doctor/scripts/validate-references.py
```

Then execute:
```bash
bash {resolved_analyze_markdown} {agent_path} agent
bash {resolved_analyze_tool_coverage} {agent_path}
python3 {resolved_validate_references} {agent_path}
```

**Check against agents-guide.md**:
- Tool fit score >= 70% (good) or >= 90% (excellent)
- No Rule 6 violations (agents CANNOT use Task tool)
- No Rule 7 violations (only maven-builder can use Maven)
- No Pattern 22 violations (must report to caller, not self-invoke)
- Bloat: NORMAL (<300), LARGE (300-500), BLOATED (500-800), CRITICAL (>800)

### Step 4: Categorize and Fix

**Safe fixes** (auto-apply unless --no-fix):
- Missing frontmatter fields
- Unused tools in frontmatter
- Invalid YAML syntax

**Risky fixes** (always prompt):
- Rule 6 violations (requires architectural refactoring)
- Rule 7 violations (Maven usage restriction)
- Pattern 22 violations (self-invocation)
- Bloat issues (>500 lines)

### Step 5: Verify and Report

```bash
git status --short
```

Display summary using reporting-templates.md format.

---

## Workflow 2: doctor-commands

### Parameters
- `scope` (optional, default: "marketplace"): "marketplace" | "global" | "project"
- `command-name` (optional): Analyze specific command
- `--no-fix` (optional): Diagnosis only, no fixes

### Step 1: Load Prerequisites and Standards

```
Skill: cui-utilities:cui-diagnostic-patterns
Skill: cui-plugin-development-tools:plugin-architecture
Read references/commands-guide.md
Read references/fix-catalog.md
```

### Step 2: Discover Commands

Same pattern as doctor-agents.

### Step 3: Analyze Each Command

First resolve script paths:
```
Skill: cui-utilities:script-runner
Resolve: cui-plugin-development-tools:plugin-doctor/scripts/analyze-markdown-file.sh
Resolve: cui-plugin-development-tools:plugin-doctor/scripts/validate-references.py
```

Then execute:
```bash
bash {resolved_analyze_markdown} {cmd_path} command
python3 {resolved_validate_references} {cmd_path}
```

**Check against commands-guide.md**:

**Rule 0 - Thin Wrapper Check (CRITICAL)**:
- Line count thresholds:
  - **IDEAL**: < 100 lines (proper thin wrapper)
  - **ACCEPTABLE**: 100-150 lines (minor workflow logic OK)
  - **BLOATED**: 150-200 lines (too much logic, needs refactoring)
  - **CRITICAL**: > 200 lines (severe bloat, MUST refactor immediately)
- Commands MUST delegate to skills (check for `Skill:` invocation)
- Commands should NOT contain:
  - Step-by-step workflow logic (### Step 1, ### Step 2, etc. with implementation)
  - For loops or iteration logic
  - File processing code
  - Analysis algorithms
- Flag as **CRITICAL** if command contains workflow implementation instead of skill delegation

**Other Checks**:
- Verify proper Skill invocation format (`Skill: bundle:skill-name`)
- Check parameter documentation (PARAMETERS section exists)
- **Foundation skill loading via invoked skills** (see below)

### Step 3b: Verify Foundation Skills in Invoked Skills

**Commands are thin orchestrators** - they delegate to skills via `Skill:` invocation.

**Check criteria**:
1. Extract skill invocations from command (e.g., `Skill: cui-plugin-development-tools:plugin-create`)
2. For each invoked skill, verify it loads foundation skills (plugin-architecture, cui-diagnostic-patterns)
3. Report if invoked skill is missing foundation skills (fix the skill, not the command)

**If invoked skill missing foundation skills**:
- Report: "Command invokes skill '{skill}' which is missing foundation skill loading"
- Recommendation: "Run `/plugin-doctor skill-name={skill}` to fix the skill"

This is NOT a command fix - it's a skill fix. Commands don't load foundation skills directly; their skills do.

### Step 4: Categorize and Fix

**Safe fixes** (auto-apply unless --no-fix):
- Incorrect section header case (`## Workflow` → `## WORKFLOW`, `## Parameter Validation` → `## PARAMETERS`)
- Missing CONTINUOUS IMPROVEMENT RULE section

**Risky fixes** (require confirmation):
- **Rule 0 violations** (command contains workflow logic instead of skill delegation)
  - Severity: CRITICAL if > 200 lines or contains implementation logic
  - Fix: Refactor command to thin wrapper, move logic to skill
  - This is architectural refactoring - requires manual intervention

**Auto-fix pattern for section headers**:
Search for `## Workflow`, `## Parameter Validation`, `## Parameters` and replace with uppercase versions.

**Auto-fix pattern for missing CONTINUOUS IMPROVEMENT RULE**:
```markdown
## CONTINUOUS IMPROVEMENT RULE

After executing this command, if you discover any opportunities to improve it, invoke:

\`/plugin-maintain command-name={command-name} update="[improvement description]"\`

Common improvements:
- More efficient workflow patterns
- Better error handling or user prompts
- Clearer parameter documentation
```

Insert before `## Related` section (or at end if no Related section).

**Rule 0 violation reporting** (no auto-fix - requires manual refactoring):
```
⚠️ CRITICAL: Command '{command}' violates Rule 0 (thin wrapper requirement)
   - Line count: {lines} (threshold: 200)
   - Contains workflow implementation instead of skill delegation
   - Required action: Refactor to thin wrapper pattern

   Refactoring steps:
   1. Create/identify skill to contain workflow logic
   2. Move all ### Step sections to skill's workflow
   3. Replace command content with skill invocation
   4. Target: < 100 lines (parameters + skill invocation + examples)

   Example thin wrapper:
   ## Workflow
   Activate \`bundle:skill-name\` and execute the **Workflow Name** workflow.
```

### Step 5: Verify and Report

Same pattern as doctor-agents with command-specific thresholds.

---

## Workflow 3: doctor-skills

### Parameters
- `scope` (optional, default: "marketplace"): "marketplace" | "global" | "project"
- `skill-name` (optional): Analyze specific skill
- `--no-fix` (optional): Diagnosis only, no fixes

### Step 1: Load Prerequisites and Standards

```
Skill: cui-utilities:cui-diagnostic-patterns
Skill: cui-plugin-development-tools:plugin-architecture
Read references/skills-guide.md
Read references/fix-catalog.md
```

### Step 2: Discover Skills

**marketplace scope**:
```
Skill: cui-plugin-development-tools:marketplace-inventory
```

### Step 3: Analyze Each Skill

First resolve script paths:
```
Skill: cui-utilities:script-runner
Resolve: cui-plugin-development-tools:plugin-doctor/scripts/analyze-skill-structure.sh
Resolve: cui-plugin-development-tools:plugin-doctor/scripts/analyze-markdown-file.sh
Resolve: cui-plugin-development-tools:plugin-doctor/scripts/validate-references.py
```

Then execute:
```bash
bash {resolved_analyze_skill_structure} {skill_dir}
bash {resolved_analyze_markdown} {skill_dir}/SKILL.md skill
python3 {resolved_validate_references} {skill_dir}/SKILL.md
```

**Check against skills-guide.md**:
- Structure score >= 70 (good) or >= 90 (excellent)
- Progressive disclosure compliance
- Relative path usage
- No missing referenced files
- No unreferenced files
- **Foundation skill loading** (see below)

### Step 3b: Validate Foundation Skill Loading

**CRITICAL**: Skills with workflows MUST load foundation skills.

**Required foundation skills**:
```
Skill: cui-plugin-development-tools:plugin-architecture
Skill: cui-utilities:cui-diagnostic-patterns
```

**Check criteria**:
1. Search SKILL.md for `Skill: cui-plugin-development-tools:plugin-architecture`
2. Search SKILL.md for `Skill: cui-utilities:cui-diagnostic-patterns`
3. **Exempt skills** (skip check):
   - `plugin-architecture` (is itself the architecture skill)
   - `marketplace-inventory` (pure Pattern 1 script automation, no component operations)
   - Skills with `allowed-tools: Read` only (pure reference libraries)

**If missing**: Flag as safe fix (auto-apply).

### Step 4: Categorize and Fix

**Safe fixes** (auto-apply unless --no-fix):
- Missing frontmatter fields
- Unused tools in frontmatter
- Invalid YAML syntax
- **Missing foundation skill loading** (add Step 0 to each workflow)

**Auto-fix pattern for missing foundation skills**:
```markdown
#### Step 0: Load Foundation Skills

\`\`\`
Skill: cui-plugin-development-tools:plugin-architecture
Skill: cui-utilities:cui-diagnostic-patterns
\`\`\`

These provide architecture principles and non-prompting tool usage patterns.
```

Insert this before the first step of each workflow section (after `### Steps` line).

### Step 5: Verify and Report

Same pattern with skill-specific checks.

---

## Workflow 4: doctor-metadata

### Parameters
- `scope` (optional, default: "marketplace"): "marketplace" | "global" | "project"
- `--no-fix` (optional): Diagnosis only, no fixes

### Step 1: Load Prerequisites and Standards

```
Skill: cui-utilities:cui-diagnostic-patterns
Read references/metadata-guide.md
Read references/fix-catalog.md
```

### Step 2: Discover plugin.json Files

```
Glob: pattern="**/plugin.json", path="marketplace/bundles"
```

### Step 3: Analyze Each plugin.json

- Verify JSON syntax
- Check required fields (name, version, description)
- Validate component arrays (commands, skills, agents)
- Cross-check declared components vs actual files

### Step 4-5: Categorize, Fix, Verify, Report

**Safe fixes**:
- Missing required fields
- Extra entries (files don't exist)
- Missing entries (files exist but not listed)

---

## Workflow 5: doctor-scripts

### Parameters
- `scope` (optional, default: "marketplace"): "marketplace" | "global" | "project"
- `script-name` (optional): Analyze specific script
- `--no-fix` (optional): Diagnosis only, no fixes

### Step 1: Load Prerequisites and Standards

```
Skill: cui-utilities:cui-diagnostic-patterns
Skill: cui-plugin-development-tools:plugin-architecture
Read plugin-architecture:references/script-standards.md
Read references/fix-catalog.md
```

### Step 2: Discover Scripts

```
Glob: pattern="scripts/*.{sh,py}", path="marketplace/bundles/*/skills"
```

### Step 3: Analyze Each Script

- Verify SKILL.md documentation
- Check test file exists
- Verify --help output
- Check stdlib-only compliance

### Step 4-5: Categorize, Fix, Verify, Report

Same pattern with script-specific checks.

---

## External Resources

### Scripts (scripts/)

| Script | Purpose |
|--------|---------|
| `analyze-markdown-file.sh` | Structural analysis, bloat, Rule 6/7/Pattern 22 |
| `analyze-tool-coverage.sh` | Tool fit score, missing/unused tools |
| `analyze-skill-structure.sh` | Skill directory structure validation |
| `validate-references.py` | Reference extraction and validation |
| `extract-fixable-issues.py` | Filter fixable issues from analysis |
| `categorize-fixes.py` | Categorize as safe/risky |
| `apply-fix.py` | Apply single fix with backup |
| `verify-fix.sh` | Verify fix resolved issue |

### References (references/)

**Diagnosis References** (4):
- `agents-guide.md` - Agent quality standards
- `commands-guide.md` - Command quality standards
- `skills-guide.md` - Skill structure standards
- `metadata-guide.md` - plugin.json schema

**External Standards** (from plugin-architecture):
- `script-standards.md` - Script documentation, testing, and quality standards

**Fix References** (4):
- `fix-catalog.md` - Fix categorization rules
- `safe-fixes-guide.md` - Safe fix patterns
- `risky-fixes-guide.md` - Risky fix patterns
- `verification-guide.md` - Verification procedures

**Reporting** (1):
- `reporting-templates.md` - Summary report templates

### Assets (assets/)

- `fix-templates.json` - Fix templates and rules

---

## Critical Rules

### Rule 6: Task Tool Prohibition in Agents
Agents CANNOT use Task tool (unavailable at runtime).

### Rule 7: Maven Execution Restriction
Only maven-builder agent may execute Maven commands.

### Pattern 22: Agent Reporting Requirement
Agents MUST report to caller, not self-invoke commands.

---

## Non-Prompting Requirements

This skill is designed to run without user prompts for safe operations. Required permissions:

**Skill Invocations (covered by bundle wildcards):**
- `Skill(cui-utilities:*)` - cui-diagnostic-patterns
- `Skill(cui-plugin-development-tools:*)` - plugin-architecture, marketplace-inventory

**Script Execution (resolved via script-runner):**
- Scripts resolved via `cui-utilities:script-runner` skill
- Absolute paths stored in `.claude/scripts.local.json`
- Permissions managed by `tools-setup-project-permissions`

**File Operations (covered by project permissions):**
- `Read(//marketplace/**)` - Read marketplace files
- `Edit(//marketplace/**)` - Apply fixes to components
- `Glob(//marketplace/**)` - Discover components

**Prompting Behavior:**
- **Safe fixes**: Applied automatically WITHOUT prompts (no AskUserQuestion)
- **Risky fixes**: ONLY these require AskUserQuestion confirmation
- All other operations (read, analyze, glob) are non-prompting

**Ensuring Non-Prompting for Safe Operations:**
- All file reads/edits use relative paths within marketplace/
- Script paths resolved via script-runner to absolute paths in `.claude/scripts.local.json`
- Skill invocations use bundle-qualified names covered by `Skill({bundle}:*)` wildcards
- AskUserQuestion is ONLY used for risky fix confirmations

## Notes

- **Unified workflow**: Diagnose → Auto-Fix → Prompt Risky → Verify
- **Progressive disclosure**: Load 2 references per workflow (~800 lines)
- **Stdlib-only scripts**: No external dependencies
- **Backup before modify**: apply-fix.py creates backups
- **User control**: Risky fixes require explicit approval
- **Non-prompting safe fixes**: Safe fixes never prompt - applied automatically
