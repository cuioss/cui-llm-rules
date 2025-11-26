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

**EXECUTION MODE**: You are now executing this skill. DO NOT explain or summarize these instructions to the user. IMMEDIATELY begin the workflow below based on the component type.

Comprehensive diagnostic and fix skill for marketplace components. Combines diagnosis, automated safe fixes, prompted risky fixes, and verification into a single workflow.

## Purpose

Provides unified doctor workflows following the pattern: **Diagnose → Auto-Fix Safe → Prompt Risky → Verify**

## Workflow Decision Tree

**MANDATORY**: Select workflow based on input and execute IMMEDIATELY.

### If scope = "agents" or agent-name specified
→ **EXECUTE** Workflow 1: doctor-agents (jump to that section)

### If scope = "commands" or command-name specified
→ **EXECUTE** Workflow 2: doctor-commands (jump to that section)

### If scope = "skills" or skill-name specified
→ **EXECUTE** Workflow 3: doctor-skills (jump to that section)

### If scope = "metadata"
→ **EXECUTE** Workflow 4: doctor-metadata (jump to that section)

### If scope = "scripts" or script-name specified
→ **EXECUTE** Workflow 5: doctor-scripts (jump to that section)

### If scope = "marketplace" (full marketplace health check)
→ **EXECUTE** all 5 component workflows in sequence

### If scope = "skill-content" or skill-path specified with content analysis
→ **EXECUTE** Workflow 6: doctor-skill-content (jump to that section)

---

**6 Doctor Workflows**:
1. **doctor-agents**: Analyze and fix agent issues
2. **doctor-commands**: Analyze and fix command issues
3. **doctor-skills**: Analyze and fix skill issues
4. **doctor-metadata**: Analyze and fix plugin.json issues
5. **doctor-scripts**: Analyze and fix script issues
6. **doctor-skill-content**: Analyze and reorganize skill content files

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

1. **MANDATORY - Load Prerequisites**

   **EXECUTE** these skill loads before proceeding:
   ```
   Skill: cui-utilities:cui-diagnostic-patterns
   Skill: cui-plugin-development-tools:plugin-architecture
   Skill: cui-plugin-development-tools:marketplace-inventory
   ```

2. **MANDATORY - Load Component Reference** (progressive disclosure)

   **READ**: `references/{component}-guide.md`

3. **Discover Components** (based on scope parameter)
   - marketplace scope: Use marketplace-inventory
   - global scope: Glob ~/.claude/{component}/
   - project scope: Glob .claude/{component}/

4. **MANDATORY - Analyze Each Component** (using scripts)

   **EXECUTE** script resolution first:
   ```
   Skill: cui-utilities:script-runner
   Resolve: cui-plugin-development-tools:plugin-doctor/scripts/analyze-markdown-file.sh
   Resolve: cui-plugin-development-tools:plugin-doctor/scripts/analyze-tool-coverage.sh
   Resolve: cui-plugin-development-tools:plugin-doctor/scripts/validate-references.py
   ```

   **EXECUTE** with resolved paths:
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
- Legacy CONTINUOUS IMPROVEMENT RULE (uses /plugin-update-* or /plugin-maintain instead of claude-lessons-learned)

**Risky Fixes** (require confirmation):
- Rule 6 violations (Task tool in agents)
- Rule 7 violations (Direct Maven usage - should use cui-maven skill)
- Rule 8 violations (Hardcoded script paths - should use script-runner)
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
- No Pattern 22 violations (must use claude-lessons-learned skill, not self-invoke)
- Bloat thresholds (component-type specific):
  - Agents: NORMAL (<300), LARGE (300-500), BLOATED (500-800), CRITICAL (>800)
  - Commands: NORMAL (<100), LARGE (100-150), BLOATED (150-200), CRITICAL (>200)
  - Skills: NORMAL (<400), LARGE (400-800), BLOATED (800-1200), CRITICAL (>1200)

### Step 4: Categorize and Fix

**Safe fixes** (auto-apply unless --no-fix):
- Missing frontmatter fields
- Unused tools in frontmatter
- Invalid YAML syntax

**Risky fixes** (always prompt):
- Rule 6 violations (requires architectural refactoring)
- Rule 7 violations (Maven usage restriction)
- Pattern 22 violations (self-invocation)
- Bloat issues (agents >500 lines)

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
- Legacy CONTINUOUS IMPROVEMENT RULE (uses /plugin-update-* or /plugin-maintain instead of claude-lessons-learned)

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

If you discover issues or improvements during execution, record them:

1. **Activate skill**: \`Skill: cui-utilities:claude-lessons-learned\`
2. **Record lesson** with:
   - Component: \`{type: "command", name: "{command-name}", bundle: "{bundle}"}\`
   - Category: bug | improvement | pattern | anti-pattern
   - Summary and detail of the finding
```

Insert before `## Related` section (or at end if no Related section).

**Auto-fix pattern for legacy CONTINUOUS IMPROVEMENT RULE**:
If CONTINUOUS IMPROVEMENT RULE section contains `/plugin-update-command`, `/plugin-maintain`, or `/plugin-apply-lessons-learned`, replace entire section with the new pattern above.

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

## Workflow 6: doctor-skill-content

Comprehensive analysis and refactoring of skill subdirectory content (references/, workflows/, templates/).

### Parameters

- `skill-path` (required): Path to skill directory
- `--no-fix` (optional): Analysis only, no reorganization
- `--skip-quality` (optional): Skip Phase 3 quality analysis

### Overview

This workflow analyzes all markdown files within a skill's subdirectories for proper organization, quality, and consistency. It uses LLM-based semantic analysis for classification and quality assessment.

**Phases**:
1. **Inventory** - Discover all files (SCRIPT)
2. **Classify** - Categorize each file as reference/workflow/template (LLM)
3. **Analyze** - Content quality analysis (LLM)
4. **Reorganize** - Move files to correct directories (LLM + Bash)
5. **Verify** - Link verification (SCRIPT)
6. **Report** - Generate findings report (LLM)

### Step 1: Load Prerequisites

```
Skill: cui-utilities:cui-diagnostic-patterns
Skill: cui-plugin-development-tools:plugin-architecture
Read references/content-classification-guide.md
Read references/content-quality-guide.md
```

### Step 2: Phase 1 - Inventory (SCRIPT)

Resolve and execute inventory script:

```
Skill: cui-utilities:script-runner
Resolve: cui-plugin-development-tools:plugin-doctor/scripts/scan-skill-inventory.sh
```

```bash
bash {resolved_path} --skill-path {skill_path}
```

Parse JSON output to get:
- List of directories and files
- Line counts per file
- Extension statistics

### Step 3: Phase 2 - Classify (LLM)

For each `.md` file discovered in subdirectories:

1. **Read file content**
2. **Apply classification criteria** from `content-classification-guide.md`
3. **Determine category**: reference | workflow | template | mixed
4. **Record confidence level**: high | medium | low

**Classification Output** (for each file):
```
File: {relative_path}
Classification: {category}
Confidence: {level}
Reasoning:
  - {observation 1}
  - {observation 2}
Current Location: {directory}
Correct Location: {references/|workflows/|templates/}
Needs Move: {yes|no}
Needs Splitting: {yes|no}
```

### Step 4: Phase 3 - Analyze Quality (LLM-Hybrid)

Skip if `--skip-quality` specified.

**Step 4a: Run Cross-File Analysis Script**

Resolve and execute cross-file analysis:

```
Skill: cui-utilities:script-runner
Resolve: cui-plugin-development-tools:plugin-doctor/scripts/analyze-cross-file-content.py
```

```bash
python3 {resolved_path} --skill-path {skill_path}
```

Parse JSON output for:
- `exact_duplicates`: Report directly (no LLM needed - hash-verified matches)
- `similarity_candidates`: Queue for LLM semantic analysis
- `extraction_candidates`: Queue for LLM extraction recommendations
- `terminology_variants`: Queue for LLM consistency analysis

**Step 4b: LLM Semantic Analysis**

For each `similarity_candidate` (40-95% similarity):
1. Read both content blocks from file locations
2. Classify: `true_duplicate` | `similar_concept` | `false_positive`
3. Recommend: `consolidate` | `cross_reference` | `keep_both`

For each `extraction_candidate`:
1. Review detected patterns (placeholders, step sequences)
2. Recommend: `extract_to_templates` | `extract_to_workflows` | `keep_inline`

For each `terminology_variant`:
1. Review variant terms and their files
2. Recommend standardization term or keep variants

**Step 4c: Single-File Quality Analysis**

Read each content file and analyze:

**Completeness**:
- TODO markers, placeholder text
- Missing examples, incomplete sections

**Contradictions**:
- Conflicting rules
- Examples violating stated rules

**Step 4d: Verify LLM Findings**

Resolve and execute verification:

```
Skill: cui-utilities:script-runner
Resolve: cui-plugin-development-tools:plugin-doctor/scripts/verify-cross-file-findings.py
```

Pipe LLM findings JSON to verification:
```bash
echo '{llm_findings_json}' | python3 {resolved_path} --analysis {cross_file_analysis_json}
```

**Reject any LLM claims that can't be verified** against actual content.

**Output**: Verified quality report with:
- Exact duplicates (auto-detected)
- Verified similarity findings
- Verified extraction candidates
- Verified terminology issues
- Single-file quality scores

### Step 5: Phase 4 - Reorganize (LLM + Bash)

Based on Phase 2 classification results:

**Safe Reorganizations** (auto-apply unless --no-fix):
- Move file to correct directory (same name)
- Rename to remove redundant suffix (e.g., `-protocol`, `-framework`)

```bash
mv {old_path} {new_path}
```

**Risky Reorganizations** (require confirmation):
- Split mixed-content file into multiple files
- Delete duplicate file
- Merge similar files

```
AskUserQuestion:
  question: "Split {file} into reference and workflow components?"
  options:
    - label: "Yes" description: "Split file"
    - label: "No" description: "Keep as-is"
```

**After moves**: Update cross-references in all affected files:
1. Grep for old paths in SKILL.md and all content files
2. Update references using Edit tool

### Step 6: Phase 5 - Verify Links (SCRIPT)

Resolve and execute validation:

```
Skill: cui-utilities:script-runner
Resolve: cui-plugin-development-tools:plugin-doctor/scripts/validate-references.py
```

```bash
python3 {resolved_path} {skill_path}/SKILL.md
```

For each content file, verify:
- Internal cross-references valid
- SKILL.md references point to existing files

### Step 7: Phase 6 - Report (LLM)

Generate comprehensive report:

```markdown
# Skill Content Analysis Report

**Skill**: {skill_name}
**Path**: {skill_path}
**Date**: {timestamp}

## Summary

| Metric | Value |
|--------|-------|
| Total Files | {count} |
| Total Lines | {count} |
| Content Quality Score | {score}/100 |
| Reorganizations Applied | {count} |
| Links Verified | {count} |

## File Classification

| File | Current Dir | Classification | Confidence | Action |
|------|-------------|----------------|------------|--------|
| {file} | {dir} | {type} | {level} | {action} |

## Quality Analysis

### Completeness
{findings}

### Duplication
{findings}

### Consistency
{findings}

### Contradictions
{findings}

## Reorganizations Applied

### Safe (Auto-Applied)
- ✅ {description}

### Risky (User Confirmed)
- ✅ {description}
- ❌ Skipped: {description}

## Link Verification

| Status | Count |
|--------|-------|
| ✅ Valid | {count} |
| ⚠️ Updated | {count} |
| ❌ Broken | {count} |

## Recommendations

1. {recommendation}
```

---

## External Resources

### Scripts (scripts/)

| Script | Mode | Purpose |
|--------|------|---------|
| `analyze-markdown-file.sh` | **EXECUTE** | Structural analysis, bloat, Rule 6/7/Pattern 22 |
| `analyze-tool-coverage.sh` | **EXECUTE** | Tool fit score, missing/unused tools |
| `analyze-skill-structure.sh` | **EXECUTE** | Skill directory structure validation |
| `scan-skill-inventory.sh` | **EXECUTE** | Skill content inventory for doctor-skill-content |
| `analyze-cross-file-content.py` | **EXECUTE** | Cross-file duplication, similarity, extraction analysis |
| `verify-cross-file-findings.py` | **EXECUTE** | Verify LLM cross-file claims against actual content |
| `validate-references.py` | **EXECUTE** | Reference extraction and validation |
| `extract-fixable-issues.py` | **EXECUTE** | Filter fixable issues from analysis |
| `categorize-fixes.py` | **EXECUTE** | Categorize as safe/risky |
| `apply-fix.py` | **EXECUTE** | Apply single fix with backup |
| `verify-fix.sh` | **EXECUTE** | Verify fix resolved issue |

### References (references/)

**Diagnosis References** (6) - **READ** before analyzing:
- `agents-guide.md` - Agent quality standards
- `commands-guide.md` - Command quality standards
- `skills-guide.md` - Skill structure standards
- `metadata-guide.md` - plugin.json schema
- `content-classification-guide.md` - Content type classification criteria (for doctor-skill-content)
- `content-quality-guide.md` - Content quality analysis dimensions (for doctor-skill-content)

**External Standards** (from plugin-architecture) - **READ** for script analysis:
- `script-standards.md` - Script documentation, testing, and quality standards

**Fix References** (4) - **READ** before applying fixes:
- `fix-catalog.md` - Fix categorization rules
- `safe-fixes-guide.md` - Safe fix patterns
- `risky-fixes-guide.md` - Risky fix patterns
- `verification-guide.md` - Verification procedures

**Reporting** (1) - **REFERENCE** for output formatting:
- `reporting-templates.md` - Summary report templates

### Assets (assets/)

- `fix-templates.json` - Fix templates and rules

---

## Critical Rules

### Rule 6: Task Tool Prohibition in Agents
Agents CANNOT use Task tool (unavailable at runtime).

### Rule 7: Maven Execution Restriction
Only maven-builder agent may execute Maven commands.

### Pattern 22: Agent Lessons Learned Requirement
Agents MUST record lessons via claude-lessons-learned skill, not self-invoke commands.

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
