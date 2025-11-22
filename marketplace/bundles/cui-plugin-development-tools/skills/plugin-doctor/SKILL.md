---
name: plugin-doctor
description: Diagnose and fix quality issues in marketplace components with automated safe fixes and prompted risky fixes
allowed-tools: Read, Edit, Write, Bash, AskUserQuestion, Glob, Grep, Skill
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
| doctor-scripts | `scripts-guide.md` | `fix-catalog.md` |

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
   Read {baseDir}/references/{component}-guide.md
   ```

3. **Discover Components** (based on scope parameter)
   - marketplace scope: Use marketplace-inventory
   - global scope: Glob ~/.claude/{component}/
   - project scope: Glob .claude/{component}/

4. **Analyze Each Component** (using scripts)
   ```bash
   Bash: {baseDir}/scripts/analyze-markdown-file.sh {path} {type}
   Bash: {baseDir}/scripts/analyze-tool-coverage.sh {path}
   Bash: python3 {baseDir}/scripts/validate-references.py {path}
   ```

### Phase 2: Categorize Issues

**Safe Fixes** (auto-apply):
- Missing frontmatter fields
- Invalid YAML syntax
- Unused tools in frontmatter
- Trailing whitespace
- Missing blank lines

**Risky Fixes** (require confirmation):
- Rule 6 violations (Task tool in agents)
- Rule 7 violations (Maven usage)
- Pattern 22 violations (self-invocation)
- Structural changes
- Content removal

### Phase 3: Apply Fixes

1. **Auto-Apply Safe Fixes**
   ```bash
   Bash: echo '{fix_json}' | python3 {baseDir}/scripts/apply-fix.py - {dir}
   ```
   - Apply each safe fix automatically
   - Track success/failure
   - Log: "✅ Fixed: {description}"

2. **Prompt for Risky Fixes**
   ```
   AskUserQuestion:
     question: "Apply fix for {issue}?"
     options:
       - label: "Yes" description: "Apply this fix"
       - label: "No" description: "Skip this fix"
       - label: "Skip All" description: "Skip remaining risky fixes"
   ```

### Phase 4: Verify and Report

1. **Verify Fixes**
   ```bash
   Bash: {baseDir}/scripts/verify-fix.sh {type} {path}
   ```

2. **Generate Summary**
   ```
   Read {baseDir}/references/reporting-templates.md
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
Read {baseDir}/references/agents-guide.md
Read {baseDir}/references/fix-catalog.md
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

For each agent file:

```bash
Bash: {baseDir}/scripts/analyze-markdown-file.sh {agent_path} agent
Bash: {baseDir}/scripts/analyze-tool-coverage.sh {agent_path}
Bash: python3 {baseDir}/scripts/validate-references.py {agent_path}
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
Bash: git status --short
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
Read {baseDir}/references/commands-guide.md
Read {baseDir}/references/fix-catalog.md
```

### Step 2: Discover Commands

Same pattern as doctor-agents.

### Step 3: Analyze Each Command

```bash
Bash: {baseDir}/scripts/analyze-markdown-file.sh {cmd_path} command
Bash: python3 {baseDir}/scripts/validate-references.py {cmd_path}
```

**Check against commands-guide.md**:
- Bloat: CRITICAL if >100 lines (commands are thin orchestrators)
- Verify proper Skill invocation format
- Check parameter documentation

### Step 4-5: Categorize, Fix, Verify, Report

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
Read {baseDir}/references/skills-guide.md
Read {baseDir}/references/fix-catalog.md
```

### Step 2: Discover Skills

**marketplace scope**:
```
Skill: cui-plugin-development-tools:marketplace-inventory
```

### Step 3: Analyze Each Skill

```bash
Bash: {baseDir}/scripts/analyze-skill-structure.sh {skill_dir}
Bash: {baseDir}/scripts/analyze-markdown-file.sh {skill_dir}/SKILL.md skill
Bash: python3 {baseDir}/scripts/validate-references.py {skill_dir}/SKILL.md
```

**Check against skills-guide.md**:
- Structure score >= 70 (good) or >= 90 (excellent)
- Progressive disclosure compliance
- {baseDir} pattern usage
- No missing referenced files
- No unreferenced files

### Step 4-5: Categorize, Fix, Verify, Report

Same pattern with skill-specific checks.

---

## Workflow 4: doctor-metadata

### Parameters
- `scope` (optional, default: "marketplace"): "marketplace" | "global" | "project"
- `--no-fix` (optional): Diagnosis only, no fixes

### Step 1: Load Prerequisites and Standards

```
Skill: cui-utilities:cui-diagnostic-patterns
Read {baseDir}/references/metadata-guide.md
Read {baseDir}/references/fix-catalog.md
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
Read {baseDir}/references/scripts-guide.md
Read {baseDir}/references/fix-catalog.md
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

### Scripts ({baseDir}/scripts/)

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

### References ({baseDir}/references/)

**Diagnosis References** (5):
- `agents-guide.md` - Agent quality standards
- `commands-guide.md` - Command quality standards
- `skills-guide.md` - Skill structure standards
- `metadata-guide.md` - plugin.json schema
- `scripts-guide.md` - Script documentation standards

**Fix References** (4):
- `fix-catalog.md` - Fix categorization rules
- `safe-fixes-guide.md` - Safe fix patterns
- `risky-fixes-guide.md` - Risky fix patterns
- `verification-guide.md` - Verification procedures

**Reporting** (1):
- `reporting-templates.md` - Summary report templates

### Assets ({baseDir}/assets/)

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

## Notes

- **Unified workflow**: Diagnose → Auto-Fix → Prompt Risky → Verify
- **Progressive disclosure**: Load 2 references per workflow (~800 lines)
- **Stdlib-only scripts**: No external dependencies
- **Backup before modify**: apply-fix.py creates backups
- **User control**: Risky fixes require explicit approval
