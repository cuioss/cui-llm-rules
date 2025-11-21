---
name: plugin-diagnose
description: Find and understand quality issues in marketplace components (agents, commands, skills, metadata, scripts)
allowed-tools: Read, Bash, Glob, Grep, Skill
---

# Plugin-Diagnose Skill

Comprehensive diagnostic skill for finding and understanding quality issues in marketplace components (agents, commands, skills, metadata, scripts).

## Purpose

Provides 5 diagnostic workflows following Pattern 3 (Search-Analyze-Report) + Pattern 1 (Script Automation):
1. **diagnose-agents**: Analyze agent tool coverage, structure, Rule 6/7/Pattern 22 violations
2. **diagnose-commands**: Analyze command structure, bloat, anti-bloat rules compliance
3. **diagnose-skills**: Analyze skill structure, standards files, progressive disclosure
4. **diagnose-metadata**: Analyze plugin.json, component inventory, bundle structure
5. **diagnose-scripts**: Analyze script documentation, test coverage, help output

Each workflow loads ONE reference guide on-demand (progressive disclosure) and uses deterministic scripts for validation.

## Progressive Disclosure Strategy

**3-Level Loading Hierarchy**:
1. **Frontmatter** (~3 lines): Initial skill discovery
2. **SKILL.md** (~800 lines): Full workflow instructions (this file)
3. **Reference Guide** (ONE per workflow, ~400-500 lines): Detailed standards

**Context Efficiency**:
- **Without progressive disclosure**: 800 (SKILL.md) + 2,300 (all 5 references) = ~3,100 lines
- **With progressive disclosure**: 800 (SKILL.md) + 500 (ONE reference) = ~1,300 lines
- **Context reduction**: 75%

**Key Principle**: NEVER load all 5 references at once. Each workflow loads ONLY its specific reference guide.

## Workflow 1: diagnose-agents

### Purpose
Orchestrates comprehensive agent analysis: tool coverage, structure, Rule 6/7 violations, Pattern 22 detection.

### Parameters
- `scope` (optional, default: "marketplace"): "marketplace" | "global" | "project"
- `agent-name` (optional): Analyze specific agent by name
- `auto-fix` (optional, default: true): Auto-fix safe issues; prompt for risky
- `--save-report` (optional): Write Markdown report to project root

### Step 1: Load Prerequisites

**CRITICAL**: Load required skills for diagnostic patterns and architecture rules.

```
Skill: cui-utilities:cui-diagnostic-patterns
Skill: cui-plugin-development-tools:plugin-architecture
Skill: cui-plugin-development-tools:marketplace-inventory
```

**Verify**: Skills loaded successfully before proceeding.

### Step 2: Load Agents Standards (Progressive Disclosure)

**CRITICAL**: Load ONLY this reference guide (NOT all 5 guides).

```
Read {baseDir}/references/agents-guide.md
```

**Content**: Agent quality standards, tool coverage requirements, Rule 6/7/Pattern 22 definitions, bloat detection thresholds.

### Step 3: Discover Agents

**Discovery based on scope parameter**:

**marketplace scope** (default):
```
Skill: cui-plugin-development-tools:marketplace-inventory
```
- Parse JSON inventory to extract agent paths
- Filter by agent-name if specified

**global scope**:
```
Glob: pattern="*.md", path="~/.claude/agents"
```

**project scope**:
```
Glob: pattern="*.md", path=".claude/agents"
```

**Output**: List of agent file paths.

### Step 4: Group Agents by Bundle

**Parse bundle from file path**:
- Extract bundle name from path: `marketplace/bundles/{bundle-name}/agents/{agent-name}.md`
- Group agents by bundle
- Sort bundles: cui-plugin-development-tools first, then alphabetically

**Output**: Map of bundle → agent paths

### Step 5: Bundle-by-Bundle Processing

**CRITICAL**: Process each bundle SEQUENTIALLY (not in parallel).

**For EACH bundle in sorted order**:

#### Step 5a: Analyze All Agents in Bundle

**For EACH agent in bundle**:

1. **Structural Analysis** (analyze-markdown-file.sh):
   ```bash
   Bash: {baseDir}/scripts/analyze-markdown-file.sh {agent_path} agent
   ```
   - Parse JSON output
   - Extract: line_count, bloat_classification, frontmatter validation
   - Extract: rule_6_violation (Task tool in agents), rule_7_violation (Maven usage)
   - Extract: continuous_improvement_rule validation, pattern_22_violation

2. **Tool Coverage Analysis** (analyze-tool-coverage.sh):
   ```bash
   Bash: {baseDir}/scripts/analyze-tool-coverage.sh {agent_path}
   ```
   - Parse JSON output
   - Extract: tool_fit_score, rating, missing_tools, unused_tools
   - Extract: critical_violations (has_task_tool, maven_calls, backup_file_patterns)

3. **Reference Validation** (validate-references.py):
   ```bash
   Bash: python3 {baseDir}/scripts/validate-references.py {agent_path}
   ```
   - Parse JSON output
   - Extract: references array with line numbers and types
   - Extract: pre_filter statistics

4. **Apply Quality Standards from agents-guide.md**:
   - Check tool_fit_score >= 90% (excellent) or >= 70% (good)
   - Verify no Rule 6 violations (agents CANNOT use Task tool)
   - Verify no Rule 7 violations (only maven-builder agent can use Maven)
   - Verify no Pattern 22 violations (agents MUST report to caller, not self-invoke)
   - Check bloat: NORMAL (<300), LARGE (300-500), BLOATED (500-800), CRITICAL (>800 lines)

**Output**: Analysis results for all agents in bundle

#### Step 5b: Categorize Issues

**Safe fixes** (auto-fix when auto-fix=true):
- Missing frontmatter fields (name, description, tools)
- Unused tools in frontmatter (tool declared but not used)
- Invalid YAML frontmatter syntax

**Risky fixes** (always prompt):
- Rule 6 violations (Task tool usage - requires architectural refactoring)
- Rule 7 violations (Maven usage in non-maven-builder agents)
- Pattern 22 violations (self-invocation instead of reporting to caller)
- Bloat issues (file >500 lines)
- Low tool fit score (<70%)
- Missing required tools

**Output**: Categorized issue lists

#### Step 5c: Generate Bundle Summary

**Display**:
```
╔════════════════════════════════════════════════════════════╗
║     Bundle: {bundle-name}                                 ║
╚════════════════════════════════════════════════════════════╝

Agents analyzed: {count}

Quality Metrics:
- Average tool fit score: {avg_score}%
- Agents with excellent fit (>=90%): {excellent_count}
- Agents with issues: {issues_count}

Critical Violations:
- Rule 6 violations (Task tool): {rule6_count}
- Rule 7 violations (Maven usage): {rule7_count}
- Pattern 22 violations (self-invoke): {pattern22_count}

Bloat:
- NORMAL (<300 lines): {normal_count}
- LARGE (300-500): {large_count}
- BLOATED (500-800): {bloated_count}
- CRITICAL (>800): {critical_count}

Issues:
- Safe fixes available: {safe_count}
- Risky fixes required: {risky_count}
```

#### Step 5d: Apply Fix Workflow

**If auto-fix=true**:
- Apply safe fixes automatically using Edit tool
- Count files modified

**For risky fixes** (always prompt):
```
AskUserQuestion:
  Question: Apply risky fix for {agent_name}?
  Options:
    1. Apply fix (Edit tool)
    2. Skip this fix
    3. Skip all remaining fixes
```

#### Step 5e: POST-FIX VERIFICATION (MANDATORY)

**CRITICAL**: After ANY fixes, verify actual file changes.

```bash
Bash: git status --short
```

**Verify**:
- Count files actually modified
- Compare to fixes claimed
- Report PASS if counts match, FAIL if mismatch

**If FAIL**: Report discrepancy, investigate which files were not actually modified.

#### Step 5f: MANDATORY Bundle Completion Check

**CRITICAL**: Before proceeding to next bundle, verify:
- ✅ All agents analyzed
- ✅ All issues categorized
- ✅ Fix workflow completed
- ✅ POST-FIX VERIFICATION passed
- ✅ Bundle summary generated

**Only after ALL steps complete**: Proceed to next bundle

### Step 6: Generate Final Report

**Summary across all bundles**:
```
╔════════════════════════════════════════════════════════════╗
║     Agent Diagnosis Complete                              ║
╚════════════════════════════════════════════════════════════╝

Total agents analyzed: {total_count}
Total bundles: {bundle_count}

Overall Quality:
- Average tool fit score: {overall_avg}%
- Agents with excellent fit: {overall_excellent_count}
- Agents with issues: {overall_issues_count}

Critical Violations:
- Rule 6: {total_rule6}
- Rule 7: {total_rule7}
- Pattern 22: {total_pattern22}

Fixes Applied:
- Safe fixes: {total_safe_fixes}
- Risky fixes: {total_risky_fixes}
- Files modified: {files_modified}
```

**If --save-report flag**: Write report to `{project-root}/agent-diagnosis-report.md`

---

## Workflow 2: diagnose-commands

### Purpose
Orchestrates comprehensive command analysis: structure, bloat, anti-bloat rules (8 rules), orchestration patterns.

### Parameters
- `scope` (optional, default: "marketplace"): "marketplace" | "global" | "project"
- `command-name` (optional): Analyze specific command by name
- `auto-fix` (optional, default: true): Auto-fix safe issues; prompt for risky
- `--save-report` (optional): Write Markdown report to project root

### Step 1: Load Prerequisites

```
Skill: cui-utilities:cui-diagnostic-patterns
Skill: cui-plugin-development-tools:plugin-architecture
Skill: cui-plugin-development-tools:marketplace-inventory
```

### Step 2: Load Commands Standards (Progressive Disclosure)

**CRITICAL**: Load ONLY this reference guide (NOT all 5 guides).

```
Read {baseDir}/references/commands-guide.md
```

**Content**: Command quality standards, 8 anti-bloat rules, orchestration patterns, structure requirements.

### Step 3: Discover Commands

**Discovery based on scope parameter**:

**marketplace scope** (default):
```
Skill: cui-plugin-development-tools:marketplace-inventory
```
- Filter commands from inventory
- Filter by command-name if specified

**global scope**:
```
Glob: pattern="*.md", path="~/.claude/commands"
```

**project scope**:
```
Glob: pattern="*.md", path=".claude/commands"
```

**Output**: List of command file paths.

### Step 4: Group Commands by Bundle

**Parse bundle from file path**:
- Extract bundle name from path
- Group commands by bundle
- Sort bundles: cui-plugin-development-tools first, then alphabetically

**Output**: Map of bundle → command paths

### Step 5: Bundle-by-Bundle Processing

**CRITICAL**: Process each bundle SEQUENTIALLY.

**For EACH bundle in sorted order**:

#### Step 5a: Analyze All Commands in Bundle

**For EACH command in bundle**:

1. **Structural Analysis** (analyze-markdown-file.sh):
   ```bash
   Bash: {baseDir}/scripts/analyze-markdown-file.sh {command_path} command
   ```
   - Parse JSON output
   - Extract: line_count, bloat_classification (CRITICAL if >500 lines)
   - Extract: frontmatter validation, section_count, has_param_section
   - Extract: continuous_improvement_rule validation

2. **Reference Validation** (validate-references.py):
   ```bash
   Bash: python3 {baseDir}/scripts/validate-references.py {command_path}
   ```
   - Parse JSON output
   - Extract: references with line numbers and types
   - Verify SlashCommand invocations (should NOT have bundle prefix)
   - Verify Task invocations (MUST have bundle prefix in commands)
   - Verify Skill invocations (MUST have bundle prefix)

3. **Apply Quality Standards from commands-guide.md**:
   - **Bloat Detection**: CRITICAL if >500 lines (commands MUST be concise orchestrators)
   - **8 Anti-Bloat Rules** (from commands-guide.md):
     1. Commands MUST delegate to agents (not contain inline logic)
     2. Commands MUST use Task tool for complex operations
     3. Commands MUST NOT duplicate agent logic
     4. Commands MUST have clear parameter documentation
     5. Commands MUST follow bundle-by-bundle orchestration (if processing multiple components)
     6. Commands MUST use progressive disclosure (load skills on-demand)
     7. Commands MUST have mandatory completion checks (bundle-by-bundle)
     8. Commands MUST NOT contain embedded standards (use reference guides)
   - Verify proper use of SlashCommand: invocations (no bundle prefix)
   - Verify proper Task invocations (bundle prefix required)
   - Check CONTINUOUS IMPROVEMENT RULE presence and format

**Output**: Analysis results for all commands in bundle

#### Step 5b: Categorize Issues

**Safe fixes**:
- Missing frontmatter fields
- Missing parameter documentation section
- Invalid YAML frontmatter

**Risky fixes** (always prompt):
- Bloat issues (>500 lines = CRITICAL for commands)
- Anti-bloat rule violations
- Incorrect reference formats (bundle prefix issues)
- Missing CONTINUOUS IMPROVEMENT RULE

**Output**: Categorized issue lists

#### Step 5c-5f: Generate Summary, Apply Fixes, Verify, Complete

**Same pattern as Workflow 1 (diagnose-agents)**:
- Display bundle summary
- Apply safe fixes (if auto-fix=true)
- Prompt for risky fixes
- POST-FIX VERIFICATION (git status)
- MANDATORY bundle completion check

### Step 6: Generate Final Report

**Summary across all bundles** (similar to Workflow 1 but command-specific metrics).

**If --save-report flag**: Write report to `{project-root}/command-diagnosis-report.md`

---

## Workflow 3: diagnose-skills

### Purpose
Orchestrates comprehensive skill analysis: structure validation, standards files quality, progressive disclosure compliance, optional cross-duplication detection.

### Parameters
- `scope` (optional, default: "marketplace"): "marketplace" | "global" | "project"
- `skill-name` (optional): Analyze specific skill by name
- `--check-cross-duplication` (optional): Detect duplication BETWEEN skills (expensive O(n²))
- `auto-fix` (optional, default: true): Auto-fix safe issues; prompt for risky
- `--save-report` (optional): Write Markdown report to project root

### Step 1: Load Prerequisites

```
Skill: cui-utilities:cui-diagnostic-patterns
Skill: cui-plugin-development-tools:plugin-architecture
Skill: cui-plugin-development-tools:marketplace-inventory
```

### Step 2: Load Skills Standards (Progressive Disclosure)

**CRITICAL**: Load ONLY this reference guide (NOT all 5 guides).

```
Read {baseDir}/references/skills-guide.md
```

**Content**: Skill structure validation, frontmatter standards, progressive disclosure patterns, standards file quality (minimize-without-loss principle), cross-duplication detection.

### Step 3: Discover Skills

**Discovery based on scope parameter**:

**marketplace scope** (default):
```
Skill: cui-plugin-development-tools:marketplace-inventory
```
- Filter skills from inventory
- Filter by skill-name if specified

**global scope**:
```
Glob: pattern="*/", path="~/.claude/skills"
```

**project scope**:
```
Glob: pattern="*/", path=".claude/skills"
```

**Output**: List of skill directory paths.

### Step 4: Group Skills by Bundle

**Parse bundle from directory path**:
- Extract bundle name
- Group skills by bundle
- Sort bundles: cui-plugin-development-tools first, then alphabetically

**Output**: Map of bundle → skill paths

### Step 5: Bundle-by-Bundle Processing

**CRITICAL**: Process each bundle SEQUENTIALLY.

**For EACH bundle in sorted order**:

#### Step 5a: Analyze All Skills in Bundle

**For EACH skill in bundle**:

1. **Skill Structure Analysis** (analyze-skill-structure.sh):
   ```bash
   Bash: {baseDir}/scripts/analyze-skill-structure.sh {skill_dir}
   ```
   - Parse JSON output
   - Extract: skill_md.exists, skill_md.yaml_valid
   - Extract: standards_files.missing_files (referenced but don't exist)
   - Extract: standards_files.unreferenced_files (exist but not referenced)
   - Extract: structure_score (0-100)

2. **SKILL.md Analysis** (if exists):
   ```bash
   Bash: {baseDir}/scripts/analyze-markdown-file.sh {skill_dir}/SKILL.md skill
   ```
   - Parse JSON output
   - Extract: line_count, frontmatter validation
   - Extract: section_count
   - Check: Progressive disclosure patterns (references to {baseDir}/references/)

3. **Reference Validation** (validate-references.py):
   ```bash
   Bash: python3 {baseDir}/scripts/validate-references.py {skill_dir}/SKILL.md
   ```
   - Parse JSON output
   - Verify {baseDir} usage for all internal references
   - Verify Skill invocations (MUST have bundle prefix)
   - Check for prohibited patterns (absolute paths, ../../../../)

4. **Standards Files Quality** (if skill has standards/ directory):
   - Read each standards file in skill
   - Apply minimize-without-loss principle from skills-guide.md:
     * Zero-information content (Remove "it is important", "best practice", fluff)
     * Duplication within skill (Cross-reference instead of duplicate)
     * Ambiguity (Vague statements without specifics)
     * Formatting issues (Inconsistent structure)
   - Check integrated standards coherence (no conflicts, gaps, inconsistencies)

**Output**: Analysis results for all skills in bundle

#### Step 5b: Categorize Issues

**Safe fixes**:
- Missing SKILL.md (create skeleton)
- Invalid YAML frontmatter
- Missing frontmatter fields
- Unreferenced files (add to SKILL.md references)
- Invalid {baseDir} usage (fix paths)

**Risky fixes** (always prompt):
- Missing files (referenced but don't exist)
- Low structure score (<70)
- Standards file quality issues
- Progressive disclosure violations

**Output**: Categorized issue lists

#### Step 5c: Optional Cross-Duplication Detection

**If --check-cross-duplication flag provided**:

**WARNING**: This is O(n²) comparison across all skills in bundle. Expensive operation.

**For each pair of skills**:
1. Load both SKILL.md files
2. Extract content sections
3. Compare for duplication (LCS algorithm or similar)
4. Report duplicated content blocks >100 characters
5. Suggest consolidation (move to shared reference or skill dependency)

**Output**: Duplication report for bundle

#### Step 5d-5f: Generate Summary, Apply Fixes, Verify, Complete

**Same pattern as Workflow 1**:
- Display bundle summary (with structure_score metrics)
- Apply safe fixes (if auto-fix=true)
- Prompt for risky fixes
- POST-FIX VERIFICATION (git status)
- MANDATORY bundle completion check

### Step 6: Generate Final Report

**Summary across all bundles** (skill-specific metrics: structure_score, progressive disclosure compliance).

**If --save-report flag**: Write report to `{project-root}/skill-diagnosis-report.md`

---

## Workflow 4: diagnose-metadata

### Purpose
Validates plugin.json files, component inventory, and bundle structure compliance.

### Parameters
- `scope` (optional, default: "marketplace"): "marketplace" | "global" | "project"
- `auto-fix` (optional, default: true): Auto-fix safe schema issues
- `--save-report` (optional): Write Markdown report to project root

### Step 1: Load Prerequisites

```
Skill: cui-utilities:cui-diagnostic-patterns
Skill: cui-plugin-development-tools:plugin-architecture
Skill: cui-plugin-development-tools:marketplace-inventory
```

### Step 2: Load Metadata Standards (Progressive Disclosure)

**CRITICAL**: Load ONLY this reference guide (NOT all 5 guides).

```
Read {baseDir}/references/metadata-guide.md
```

**Content**: plugin.json schema, component inventory validation, bundle structure requirements.

### Step 3: Discover Bundles and plugin.json Files

**Based on scope**:

**marketplace scope**:
```
Glob: pattern="*/plugin.json", path="marketplace/bundles"
```

**global scope**:
```
Glob: pattern="plugin.json", path="~/.claude/bundles"
```

**project scope**:
```
Glob: pattern="plugin.json", path=".claude/bundles"
```

**Output**: List of plugin.json file paths.

### Step 4: Process Each Bundle

**For EACH plugin.json file**:

1. **Read and Parse JSON**:
   ```
   Read {plugin_json_path}
   ```
   - Verify valid JSON syntax
   - Parse: name, version, description, agents, commands, skills

2. **Schema Validation** (from metadata-guide.md):
   - Verify required fields present (name, version, description)
   - Verify field types correct (arrays for agents/commands/skills)
   - Check version format (semantic versioning)
   - Validate component entries (name, description, path)

3. **Component Inventory Validation**:
   ```bash
   # Scan for actual components in bundle
   Glob: "{bundle_dir}/agents/*.md"
   Glob: "{bundle_dir}/commands/*.md"
   Glob: "{bundle_dir}/skills/*/SKILL.md"
   ```
   - Compare plugin.json to actual files:
     * Missing entries (files exist but not in plugin.json)
     * Extra entries (in plugin.json but files don't exist)
     * Path mismatches (plugin.json path doesn't match actual)

4. **Bundle Structure Validation** (from metadata-guide.md):
   - Verify directory structure: {bundle}/agents/, {bundle}/commands/, {bundle}/skills/
   - Check naming conventions match plugin.json
   - Verify all component files exist at declared paths

**Output**: Metadata analysis for bundle

### Step 5: Categorize Issues and Apply Fixes

**Safe fixes** (auto-fix when auto-fix=true):
- Missing required fields (add with placeholder)
- Invalid field types (correct type)
- Missing component entries (add to plugin.json)
- Extra component entries (remove from plugin.json)
- Path corrections (update to actual paths)

**Risky fixes** (always prompt):
- Invalid JSON syntax (may require manual fix)
- Version conflicts
- Bundle structure violations

**Apply fixes using Edit tool**

**POST-FIX VERIFICATION** (git status)

### Step 6: Generate Final Report

**Summary across all bundles**:
```
Metadata Diagnosis Complete

Total bundles: {count}
Issues found: {issues_count}

Schema Issues: {schema_issues}
Inventory Issues: {inventory_issues}
Structure Issues: {structure_issues}

Fixes Applied: {fixes_count}
```

**If --save-report flag**: Write report to `{project-root}/metadata-diagnosis-report.md`

---

## Workflow 5: diagnose-scripts

### Purpose
Validates script documentation in SKILL.md, test coverage, and help output standards.

### Parameters
- `scope` (optional, default: "marketplace"): "marketplace" | "global" | "project"
- `script-name` (optional): Analyze specific script by name
- `auto-fix` (optional, default: true): Auto-fix safe issues
- `--save-report` (optional): Write Markdown report to project root

### Step 1: Load Prerequisites

```
Skill: cui-utilities:cui-diagnostic-patterns
Skill: cui-plugin-development-tools:plugin-architecture
Skill: cui-plugin-development-tools:marketplace-inventory
```

### Step 2: Load Scripts Standards (Progressive Disclosure)

**CRITICAL**: Load ONLY this reference guide (NOT all 5 guides).

```
Read {baseDir}/references/scripts-guide.md
```

**Content**: Script documentation requirements in SKILL.md, test file naming conventions, help output format, stdlib-only requirement.

### Step 3: Discover Scripts

**Based on scope**:

**marketplace scope**:
```
Glob: pattern="scripts/*.sh", path="marketplace/bundles/*/skills"
Glob: pattern="scripts/*.py", path="marketplace/bundles/*/skills"
```

**global scope**:
```
Glob: pattern="scripts/*", path="~/.claude/skills"
```

**project scope**:
```
Glob: pattern="scripts/*", path=".claude/skills"
```

**Output**: List of script file paths.

### Step 4: Group Scripts by Skill

**Parse skill from script path**:
- Extract skill directory
- Group scripts by skill
- Sort by bundle, then skill

**Output**: Map of skill → script paths

### Step 5: Process Each Skill's Scripts

**For EACH skill with scripts**:

1. **Verify SKILL.md Documentation**:
   ```
   Read {skill_dir}/SKILL.md
   ```
   - Check scripts are referenced in SKILL.md (from scripts-guide.md requirements):
     * Script purpose documented
     * Input parameters documented
     * Output format documented
     * Usage examples provided
   - Verify {baseDir}/scripts/*.sh references exist

2. **Test File Verification** (from scripts-guide.md):
   - Check test file exists: `test/{bundle}/{skill}/test-{script-name}.sh`
   - Verify test file is executable: `ls -l {test_file}`
   - Run test: `Bash: {test_file}` (capture output and exit code)
   - Parse test results (PASS/FAIL count)

3. **Help Output Verification** (from scripts-guide.md):
   ```bash
   Bash: {script_path} --help
   ```
   - Verify script prints usage information
   - Check for: Usage line, parameter descriptions, example usage
   - Verify exit code 0 for --help

4. **Stdlib-Only Check**:
   - Read script content
   - Check for prohibited dependencies:
     * Python: No pip imports (only stdlib)
     * Shell: No external binaries (jq, yq allowed as documented exceptions)
   - Report any violations

**Output**: Analysis results for skill's scripts

### Step 6: Categorize Issues and Apply Fixes

**Safe fixes** (auto-fix when auto-fix=true):
- Missing script references in SKILL.md (add documentation section)
- Missing --help output (add help function to script)

**Risky fixes** (always prompt):
- Missing test files (requires creating test from scratch)
- Failing tests (requires debugging)
- External dependencies (requires refactoring)

**Apply fixes using Edit tool**

**POST-FIX VERIFICATION** (git status)

### Step 7: Generate Final Report

**Summary**:
```
Script Diagnosis Complete

Total scripts: {count}
Skills with scripts: {skill_count}

Documentation Issues: {doc_issues}
Test Issues: {test_issues}
Help Output Issues: {help_issues}
Dependency Issues: {dep_issues}

Fixes Applied: {fixes_count}
```

**If --save-report flag**: Write report to `{project-root}/script-diagnosis-report.md`

---

## External Resources

### Scripts (in {baseDir}/scripts/)

**4 scripts for deterministic validation**:

1. **analyze-markdown-file.sh**: Analyzes file structure, frontmatter, bloat, Rule 6/7/Pattern 22 violations
   - Input: file path, component type
   - Output: JSON with structural analysis

2. **analyze-tool-coverage.sh**: Analyzes tool coverage and fit for agents/commands
   - Input: file path
   - Output: JSON with tool analysis (score, missing, unused, critical violations)

3. **analyze-skill-structure.sh**: Analyzes skill directory structure and file references
   - Input: skill directory path
   - Output: JSON with structure analysis (score, missing files, unreferenced files)

4. **validate-references.py**: Python script for reference pre-filtering and extraction
   - Input: file path
   - Output: JSON with detected references and pre-filter statistics

**All scripts**:
- Stdlib-only (no external dependencies)
- JSON output format
- Executable permissions
- Help output (--help flag)

### Reference Guides (in {baseDir}/references/)

**5 reference guides loaded on-demand** (~2,300 lines total):

1. **agents-guide.md** (~500 lines): Agent quality standards, tool coverage, Rule 6/7/Pattern 22
   - Loaded by: diagnose-agents workflow

2. **commands-guide.md** (~500 lines): Command quality standards, 8 anti-bloat rules, orchestration
   - Loaded by: diagnose-commands workflow

3. **skills-guide.md** (~500 lines): Skill structure, progressive disclosure, standards quality
   - Loaded by: diagnose-skills workflow

4. **metadata-guide.md** (~400 lines): plugin.json schema, inventory validation, bundle structure
   - Loaded by: diagnose-metadata workflow

5. **scripts-guide.md** (~400 lines): Script documentation, test coverage, help output, stdlib-only
   - Loaded by: diagnose-scripts workflow

**Progressive Disclosure**: Each workflow loads ONLY its specific reference guide.

## Critical Rules

### Rule 6: Task Tool Prohibition in Agents

**CRITICAL VIOLATION**: Agents CANNOT use Task tool (unavailable at runtime).

**Detection**: analyze-markdown-file.sh checks for Task in agent frontmatter tools.

**Fix**: Architectural refactoring required - convert agent to command or inline logic.

### Rule 7: Maven Execution Restriction

**CRITICAL VIOLATION**: Only maven-builder agent may execute Maven commands.

**Detection**: analyze-markdown-file.sh checks for Bash(mvn|./mvnw|maven) in non-maven-builder agents.

**Fix**: Replace direct Maven calls with Task tool invoking maven-builder agent.

### Pattern 22: Agent Reporting Requirement

**CRITICAL VIOLATION**: Agents MUST report improvements to caller (not self-invoke commands).

**Detection**: analyze-markdown-file.sh checks CONTINUOUS IMPROVEMENT RULE format.

**Valid Pattern** (caller-reporting):
```
Return structured improvement suggestion in your analysis result.
The caller can then invoke /plugin-update-agent based on your report.
```

**Invalid Pattern** (self-update):
```
If you discover improvements, invoke /plugin-update-agent directly.
```

**Fix**: Update CONTINUOUS IMPROVEMENT RULE section to use caller-reporting pattern.

### Bundle-by-Bundle Orchestration

**CRITICAL REQUIREMENT**: All workflows processing multiple components MUST use sequential bundle processing.

**Pattern**:
1. Group components by bundle
2. Sort bundles (cui-plugin-development-tools first)
3. For EACH bundle sequentially:
   - Analyze all components
   - Categorize issues
   - Apply fix workflow
   - POST-FIX VERIFICATION
   - MANDATORY completion check
4. Proceed to next bundle ONLY after completion

**Anti-Pattern**: Processing all components in parallel without bundle grouping (causes chaos, no verification).

---

## Notes

- **Stdlib-only**: All scripts use standard library only (no external dependencies)
- **Progressive disclosure**: Load ONE reference per workflow (~500 lines on-demand)
- **Typical context load**: ~1,300 lines (SKILL.md ~800 + one reference ~500)
- **Context reduction**: 75% via progressive disclosure vs loading all references upfront
- **Pattern**: Search-Analyze-Report + Script Automation
- **Consolidates**: 13 components (5 commands + 8 agents) → 1 skill with 5 workflows
