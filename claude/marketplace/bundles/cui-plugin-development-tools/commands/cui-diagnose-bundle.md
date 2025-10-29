---
name: cui-diagnose-bundle
description: Analyze and verify entire bundle for structure, integration, quality, and marketplace readiness
---

# Bundle Doctor - Verify and Fix Bundles

Analyze, verify, and fix marketplace bundles for structure, plugin manifest quality, component integration, and overall health.

## PARAMETERS

- **bundle-name** (required): Name of the bundle to analyze (e.g., `cui-project-quality-gates`)
- **fix** (optional): Automatically fix issues found (default: prompt for each issue)

## PARAMETER VALIDATION

**If bundle-name provided:**
- Look for bundle at: `~/git/cui-llm-rules/claude/marketplace/bundles/{bundle-name}/`
- Report error if bundle not found

**If no parameters provided:**
- Display list of all bundles in marketplace
- Let user select which bundle to analyze

## TOOL USAGE REQUIREMENTS

**CRITICAL**: This command must use non-prompting tools to avoid user interruptions during diagnosis.

### Activate Diagnostic Patterns Skill

```
Skill: cui-diagnostic-patterns
```

This loads all tool usage patterns for non-prompting file operations.

### Required Tool Usage Patterns

Follow patterns from cui-diagnostic-patterns skill:

✅ **File Discovery (Pattern 1):**
- Use `Glob` tool to discover files and directories
- Never use `find` or `ls` via Bash

✅ **Existence Checks (Pattern 2):**
- Use `Read` + try/except for file existence
- Use `Glob` for directory existence
- Never use `test -f` or `test -d` via Bash

✅ **Content Search (Pattern 3):**
- Use `Grep` tool for content searching
- Never use `grep` via Bash

✅ **File Reading (Pattern 4):**
- Use `Read` tool to load file contents
- Never use `cat` via Bash

**Why**: Bash commands trigger user prompts which interrupt the diagnostic flow and create poor UX.

Refer to skill standards for complete pattern details:
- tool-usage-patterns.md - Core tool selection guide
- file-operations.md - File and directory checking patterns
- search-operations.md - Content search and integration validation

## WORKFLOW INSTRUCTIONS

### Step 1: Discover and Select Bundle

**A. Parse Parameters**

If bundle-name provided:
- Set `target_bundle` = bundle-name
- Verify exists at `~/git/cui-llm-rules/claude/marketplace/bundles/{bundle-name}/`

If no parameters:
- Use Glob to discover all bundles (Pattern 1):
  ```
  bundles = Glob(pattern="*", path="~/git/cui-llm-rules/claude/marketplace/bundles")
  bundle_names = [path.split("/")[-1] for path in bundles]
  bundle_names.sort()
  ```

Display menu:
```
Available Marketplace Bundles:

1. cui-project-quality-gates
2. cui-pull-request-workflow
3. cui-documentation-standards
4. cui-issue-implementation
5. cui-plugin-development-tools
6. cui-utility-commands
...

Enter number or bundle name:
```

Store selected bundle as `target_bundle`.

### Step 2: Initialize Analysis Statistics

Create tracking variables:
- `bundle_path`: Full path to bundle
- `total_issues`: Total issues found
- `critical_issues`: Critical issues count
- `warnings`: Warnings count
- `structure_issues`: Directory/file structure problems
- `manifest_issues`: plugin.json problems
- `integration_issues`: Cross-component problems
- `naming_issues`: Naming convention violations
- `documentation_issues`: README/docs problems
- `component_agents`: Count of agents
- `component_commands`: Count of commands
- `component_skills`: Count of skills
- `agents_with_issues`: Agents with problems
- `commands_with_issues`: Commands with problems
- `skills_with_issues`: Skills with problems

### Step 3: Validate Bundle Structure

Display:
```
==================================================
Analyzing Bundle: {target_bundle}
Location: {bundle_path}
==================================================

Step 1/8: Structure Validation
```

#### Step 3.1: Check Required Directories

Use Glob to check directory existence (Pattern 2):

```
# Check .claude-plugin/
result = Glob(pattern=".claude-plugin", path="{bundle_path}")
plugin_dir_exists = len(result) > 0

# Check component directories
agents_exists = len(Glob(pattern="agents", path="{bundle_path}")) > 0
commands_exists = len(Glob(pattern="commands", path="{bundle_path}")) > 0
skills_exists = len(Glob(pattern="skills", path="{bundle_path}")) > 0
```

Report findings:
```
Directory Structure:
✅ .claude-plugin/ exists
✅ agents/ exists
✅ commands/ exists
✅ skills/ exists
❌ Missing: .claude-plugin/ directory
⚠️  Missing: skills/ directory (optional but recommended)
```

Increment `structure_issues` for each missing required directory.

#### Step 3.2: Check Required Files

Use Read to check file existence and load content (Pattern 2):

```
# Check plugin manifest (load content for later validation)
try:
    manifest_content = Read(file_path="{bundle_path}/.claude-plugin/plugin.json")
    manifest_exists = True
except Exception:
    manifest_exists = False
    manifest_content = None

# Check README (load content for later validation)
try:
    readme_content = Read(file_path="{bundle_path}/README.md")
    readme_exists = True
except Exception:
    readme_exists = False
    readme_content = None
```

**Benefit**: File content is loaded once and available for later validation steps.

Report findings:
```
Required Files:
✅ .claude-plugin/plugin.json exists
✅ README.md exists
❌ Missing: .claude-plugin/plugin.json (CRITICAL)
⚠️  Missing: README.md (recommended)
```

Increment `structure_issues` for missing files.

#### Step 3.3: Check for Unexpected Files

Use Glob to list files in bundle root (Pattern 1):

```
# List all files/directories in bundle root
all_items = Glob(pattern="*", path="{bundle_path}")

# List hidden files
hidden_items = Glob(pattern=".*", path="{bundle_path}")
```

Look for unexpected files:
- Hidden files (except .claude-plugin/)
- Temporary files (.tmp, .bak, ~)
- Build artifacts (.jar, .class, node_modules/)
- IDE files (.idea/, .vscode/, .DS_Store)

Report:
```
Unexpected Files:
⚠️  Found: .DS_Store (cleanup recommended)
⚠️  Found: node_modules/ (should not be in bundle)
✅ No unexpected files found
```

### Step 4: Validate plugin.json Manifest

Display:
```
Step 2/8: Plugin Manifest Validation
```

#### Step 4.1: Parse JSON

Use already loaded content from Step 3.2 (Pattern 4):

```
# Already loaded as manifest_content in Step 3.2
# Parse as JSON
import json
try:
    manifest = json.loads(manifest_content)
    json_valid = True
except json.JSONDecodeError as e:
    json_valid = False
    json_error = str(e)
```

**Validate JSON syntax:**
- Parse as JSON
- Check for syntax errors
- Check for trailing commas (invalid in JSON)
- Check for proper escaping

Report:
```
JSON Syntax:
✅ Valid JSON
❌ Syntax error at line 12: unexpected comma
❌ Invalid JSON: cannot parse
```

Increment `manifest_issues` for syntax errors.

#### Step 4.2: Validate Required Fields

Check required fields are present and valid:

**Required fields:**
- `name`: Must match directory name exactly
- `displayName`: Human-readable title
- `version`: Must follow semver (X.Y.Z)
- `description`: Clear purpose statement
- `author`: Object with name field (email optional)
- `license`: License identifier

Report findings:
```
Required Fields:
✅ name: "cui-project-quality-gates"
✅ displayName: "CUI Project Quality Gates"
✅ version: "1.0.0" (valid semver)
✅ description: "Provides tools for building..." (86 chars)
✅ author.name: "CUI Team"
✅ license: "MIT"

❌ name mismatch: plugin.json="old-name" but directory="cui-project-quality-gates"
❌ Missing required field: version
⚠️  version "1.0" not valid semver (should be "1.0.0")
⚠️  description too short (12 chars, recommend 50-300)
```

Increment `manifest_issues` for each issue.

#### Step 4.3: Validate Optional Fields

Check optional fields if present:

- `homepage`: Valid URL format
- `repository`: Object with type and url
- `components`: Object listing agents/commands/skills
- `keywords`: Array of search terms
- `engines`: Claude Code version requirements
- `dependencies`: Other bundle dependencies

Report:
```
Optional Fields:
✅ homepage: valid URL
✅ repository: proper git URL
✅ components: agents[], commands[], skills[]
✅ keywords: ["cui", "quality", "testing"]
⚠️  homepage: URL format invalid
⚠️  components: lists 3 agents but 4 found in agents/ directory
ℹ️  No dependencies specified
```

#### Step 4.4: Validate Component Lists

If `components` field present in plugin.json:

Use Glob to discover actual components (Pattern 1):

```
# Discover actual components
agents = Glob(pattern="*.md", path="{bundle_path}/agents")
actual_agent_names = [f.split("/")[-1].replace(".md", "") for f in agents]
agents_count = len(agents)

commands = Glob(pattern="*.md", path="{bundle_path}/commands")
actual_command_names = [f.split("/")[-1].replace(".md", "") for f in commands]
commands_count = len(commands)

skills = Glob(pattern="*", path="{bundle_path}/skills")
actual_skill_names = [f.split("/")[-1] for f in skills]
skills_count = len(skills)
```

Report mismatches:
```
Component Inventory:
✅ Agents: plugin.json lists 3, found 3 (matches)
⚠️  Commands: plugin.json lists 5, found 6 (mismatch - missing cui-new-command)
⚠️  Skills: plugin.json lists 2, found 1 (mismatch - cui-old-skill not found)
```

Increment `manifest_issues` for mismatches.

### Step 5: Validate Naming Conventions

Display:
```
Step 3/8: Naming Convention Validation
```

#### Step 5.1: Bundle Name Convention

Check bundle name follows conventions:

- ✅ Starts with "cui-" prefix (recommended)
- ✅ Uses lowercase-with-hyphens (kebab-case)
- ✅ No special characters, spaces, or underscores
- ✅ Descriptive and clear

Report:
```
Bundle Name: cui-project-quality-gates
✅ Follows CUI prefix convention
✅ Uses kebab-case
✅ Descriptive name

Bundle Name: ProjectQualityGates
❌ Missing "cui-" prefix (recommended)
❌ Uses CamelCase (should be kebab-case)
```

Increment `naming_issues` for violations.

#### Step 5.2: Component Naming Conventions

**For agents:**
- Should use kebab-case
- Should be descriptive (not generic)
- Should relate to bundle purpose

**For commands:**
- Should start with "cui-" prefix
- Should use kebab-case
- Should be descriptive

**For skills:**
- Should start with "cui-" prefix
- Should use kebab-case
- Should describe domain

Check each component name:
```
Component Naming:
✅ Agents follow naming conventions (3/3)
⚠️  Command "buildVerify" should be "cui-build-verify" (2 chars)
❌ Skill "JavaCore" should be "cui-java-core" (violates conventions)
```

Increment `naming_issues` for each violation.

### Step 6: Analyze Component Health

Display:
```
Step 4/8: Component Health Analysis
```

#### Step 6.1: Scan Components

Use Glob to discover all components (Pattern 1):

```
# Find all agents
agents = Glob(pattern="*.md", path="{bundle_path}/agents")
component_agents = len(agents)

# Find all commands
commands = Glob(pattern="*.md", path="{bundle_path}/commands")
component_commands = len(commands)

# Find all skills (directories containing SKILL.md)
skill_dirs = Glob(pattern="*", path="{bundle_path}/skills")
skills = []
for skill_path in skill_dirs:
    if len(Glob(pattern="SKILL.md", path=skill_path)) > 0:
        skills.append(skill_path)
component_skills = len(skills)
```

Store counts in `component_agents`, `component_commands`, `component_skills`.

Report:
```
Component Inventory:
- Agents: {component_agents}
- Commands: {component_commands}
- Skills: {component_skills}
- Total: {sum}
```

#### Step 6.2: Quick Component Validation

For EACH component, perform quick validation:

**Agents (*.md in agents/):**
- Check YAML frontmatter exists
- Check uses 'tools' field (correct for agents)
- Check frontmatter name matches filename

**Commands (*.md in commands/):**
- Check YAML frontmatter exists
- Check has name and description fields
- Check frontmatter name matches filename

**Skills (directories in skills/):**
- Check SKILL.md exists
- Check YAML frontmatter exists
- Check uses 'allowed-tools' field (correct for skills, NOT 'tools')
- Check standards/ directory exists

Report summary:
```
Component Quick Validation:
✅ Agents: 3/3 have valid frontmatter
⚠️  Commands: 5/6 have valid frontmatter (cui-broken-command missing)
❌ Skills: 1/2 valid (cui-old-skill missing SKILL.md)
```

Update: `agents_with_issues`, `commands_with_issues`, `skills_with_issues`

#### Step 6.3: Offer Deep Component Analysis

Display:
```
Would you like to run deep component analysis?

This will execute:
- /cui-diagnose-agents for all agents in this bundle
- /cui-diagnose-commands for all commands in this bundle
- /cui-diagnose-skills for all skills in this bundle

This may take several minutes for large bundles.

Run deep analysis? [Y/n]:
```

If yes:
1. Run `/cui-diagnose-agents scope=marketplace` filtering to this bundle
2. Run `/cui-diagnose-commands scope=marketplace` filtering to this bundle
3. Run `/cui-diagnose-skills scope=marketplace` filtering to this bundle
4. Aggregate results

Report:
```
Deep Component Analysis Results:

Agents:
- maven-project-builder: ✅ Excellent (Tool Fit: 100%)
- commit-changes: ✅ Excellent (Tool Fit: 100%)
- broken-agent: ❌ Critical issues (Tool Fit: 60%)

Commands:
- cui-build-and-verify: ✅ Clean
- cui-fix-diagnostics: ⚠️  2 warnings
- cui-broken-command: ❌ 3 critical issues

Skills:
- cui-javadoc: ✅ Excellent (Content Score: 95/100)
- cui-old-skill: ❌ Critical issues (missing SKILL.md)

Summary:
- Components with issues: 3/8
- Critical component issues: 2
- Should fix before bundle release
```

### Step 6A: Validate Bundle Architecture Compliance

Display:
```
Step 4.5/8: Architecture Compliance Validation
```

**CRITICAL**: Validate entire bundle follows marketplace architecture rules.

**Invoke Architecture Skill**:
```
Skill: cui-marketplace-architecture
```

This loads architecture rules and validation patterns for marketplace components.

#### Step 6A.1: Validate All Skills (Self-Containment)

For each skill in `{bundle_path}/skills/`:

Use Grep to validate (Pattern 3):

```
# Check for escape sequences
escape_refs = Grep(
    pattern="\\.\\.\\.*/\\.\\.\\.*/\\.\\.",
    path="{skill_path}/SKILL.md",
    output_mode="content",
    -n=true
)

# Check for absolute paths
absolute_paths = Grep(
    pattern="~/|^/",
    path="{skill_path}/SKILL.md",
    output_mode="content",
    -n=true
)
# Filter out https:// URLs
absolute_paths = [m for m in absolute_paths if "https://" not in m]

# Check for .adoc references (likely external)
adoc_refs = Grep(
    pattern="Read:.*\\.adoc",
    path="{skill_path}/SKILL.md",
    output_mode="content",
    -n=true
)
```

Calculate self-containment score for each skill:
```
Base: 100 points

Deductions (from scoring-criteria.md):
- External file ref in workflow: -20 each
- External file ref in docs: -10 each
- Absolute path: -20 each
- Missing internal file: -10 each

skill_score = 100 - total_deductions
```

Track results:
- `skill_architecture_scores[]`: Array of scores per skill
- `skill_violations[]`: Array of violation counts per skill

#### Step 6A.2: Validate All Agents (Skill Usage)

For each agent in `{bundle_path}/agents/`:

Use Grep to validate (Pattern 3):

**A. Check if agent uses standards:**
```
standards_usage = Grep(
    pattern="standard|pattern|guideline|rule",
    path="{agent_path}",
    output_mode="files_with_matches",
    -i=true
)
```

If yes, validate skill usage:

**B. Check for Skill in tools list:**
Read agent frontmatter and parse tools field.

**C. Check for Skill invocations:**
```
skill_refs = Grep(
    pattern="Skill: cui-",
    path="{agent_path}",
    output_mode="content",
    -n=true
)
```

**D. Check for prohibited references:**
```
# Escape sequences
escape_refs = Grep(
    pattern="\\.\\.\\.*/\\.\\.\\.*/\\.\\.",
    path="{agent_path}",
    output_mode="content",
    -n=true
)

# Absolute paths (excluding URLs)
absolute_paths = Grep(
    pattern="~/|^/",
    path="{agent_path}",
    output_mode="content",
    -n=true
)
absolute_paths = [m for m in absolute_paths if "https://" not in m]

# Direct .adoc references
adoc_refs = Grep(
    pattern="Read:.*\\.adoc",
    path="{agent_path}",
    output_mode="content",
    -n=true
)
```

Calculate agent skill usage score:
```
Base: 100 points

Deductions (from scoring-criteria.md):
- Missing Skill in tools: -30
- No Skill invocations: -30
- Direct file reference: -20 each
- Absolute path: -20 each

agent_score = 100 - total_deductions
```

Track results:
- `agent_architecture_scores[]`: Array of scores per agent
- `agent_violations[]`: Array of violation counts per agent

#### Step 6A.3: Calculate Bundle Architecture Score

Apply bundle scoring from loaded standards (scoring-criteria.md):

```
# Calculate averages
skill_avg = average(skill_architecture_scores)
agent_avg = average(agent_architecture_scores)
command_avg = 100  # Commands typically don't have architecture requirements

# Weighted bundle score
bundle_architecture_score = (skill_avg × 0.6) + (agent_avg × 0.3) + (command_avg × 0.1)

# If no skills: skill_avg = 100 (N/A)
# If no agents: agent_avg = 100 (N/A)
```

#### Step 6A.4: Report Architecture Compliance

Display summary:
```
Architecture Compliance Report:

Skills (Self-Containment):
✅ cui-javadoc: 100/100 - Fully self-contained
✅ cui-java-core: 100/100 - Fully self-contained
❌ cui-old-skill: 40/100 - 3 external file references
   Line 45: Read: ../../../../standards/java/java-core.adoc
   Line 78: Read: ~/git/cui-llm-rules/standards/logging.adoc
   Line 102: Read: ../../doc/architecture.adoc

Skills Average: 80/100

Agents (Skill Usage):
✅ maven-project-builder: 100/100 - Proper skill usage
   Uses: Skill: cui-javadoc
   Tools: Read, Edit, Write, Bash, Skill
❌ code-reviewer: 40/100 - Direct file references
   Missing 'Skill' in tools list
   Line 67: Read: ~/git/cui-llm-rules/standards/java-core.adoc
⚠️  commit-changes: 100/100 (N/A - no standards usage)

Agents Average: 80/100

BUNDLE ARCHITECTURE SCORE: 78/100
Status: ⭐⭐⭐⭐ Good - Minor architecture improvements needed

Rating:
- 90-100: ✅ Excellent - Marketplace ready
- 75-89:  ⚠️ Good - Minor improvements
- 60-74:  ⚠️ Fair - Moderate work needed
- < 60:   ❌ Poor - Significant issues
```

#### Step 6A.5: Add Architecture Violations to Issue Report

Categorize architecture violations:

**CRITICAL Issues:**
- Skills with external file references (escape sequences or absolute paths)
- Agents using standards without `Skill` in tools
- Agents with direct file references instead of skill invocations

For each violation:
```
Add to issue report:
- Severity: CRITICAL
- Component: {skill_name} or {agent_name}
- Issue: "ARCHITECTURE VIOLATION - {description}"
- Impact: "Breaks portability / bypasses skill abstraction"
- Fix: {specific fix guidance}

Increment counters:
- architecture_violations++
- critical_issues++ (if score < 60)
- warnings++ (if score 60-89)
```

**Example issue entries:**
```
CRITICAL:
- Skill "cui-old-skill": External file references (Score: 40/100)
  Line 45: Read: ../../../../standards/java/java-core.adoc
  Impact: Skill breaks when distributed independently
  Fix: Copy file to skill/standards/ and update reference to: Read: standards/java-core.md

- Agent "code-reviewer": Direct file access instead of skills (Score: 40/100)
  Missing 'Skill' in tools list
  Line 67: Read: ~/git/cui-llm-rules/standards/java-core.adoc
  Impact: Bypasses skill abstraction, breaks portability
  Fix: Add 'Skill' to tools list, replace with: Skill: cui-java-core
```

#### Step 6A.6: Update Bundle Health Score Calculation

Integrate architecture score into overall bundle health:

```
# Add to Step 9 (Calculate Bundle Health Score)

Architecture Score (0-100):
- All skills self-contained: 60 points
- All agents use skills properly: 30 points
- No prohibited references: 10 points

# Update overall health calculation to include architecture:
Overall Health Score = average(
  structure_score,
  manifest_score,
  component_health_score,
  architecture_score,    # <-- NEW
  integration_score,
  documentation_score
)
```

#### Step 6A.7: Track Architecture Statistics

Add to bundle statistics:
- `bundle_architecture_score`: Overall architecture compliance (0-100)
- `architecture_violations`: Total violations found
- `skills_with_arch_issues`: Count of non-compliant skills
- `agents_with_arch_issues`: Count of agents with skill usage issues
- `skill_architecture_scores[]`: Individual skill scores
- `agent_architecture_scores[]`: Individual agent scores

### Step 7: Validate Cross-Component Integration

Display:
```
Step 5/8: Integration Validation
```

#### Step 7.1: Check Agent-Command Integration

Use Grep to find command references (Pattern 3):

```
# Search for command references in all agents
command_refs = Grep(
    pattern="SlashCommand|/cui-",
    path="{bundle_path}/agents",
    output_mode="content",
    -n=true
)

# Parse results to extract command names
# Example result: "filename:42:SlashCommand: /cui-build-and-verify"
for match in command_refs:
    # Extract command name and verify it exists
    command_name = extract_command_name(match)
    verify_command_exists(command_name)
```

Verify referenced commands exist in bundle or are valid external commands.

Report:
```
Agent-Command Integration:
✅ maven-project-builder references /cui-build-and-verify (exists)
❌ custom-agent references /cui-missing-command (not found)
```

Increment `integration_issues` for broken references.

#### Step 7.2: Check Agent-Skill Integration

Use Grep to find skill references (Pattern 3):

```
# Search for skill references in all agents
skill_refs = Grep(
    pattern="Skill:|skill:",
    path="{bundle_path}/agents",
    output_mode="content",
    -n=true
)

# Parse results to extract skill names
# Example result: "filename:37:Skill: cui-javadoc"
for match in skill_refs:
    # Extract skill name and verify it exists
    skill_name = extract_skill_name(match)
    verify_skill_exists(skill_name)
```

Verify referenced skills exist.

Report:
```
Agent-Skill Integration:
✅ maven-project-builder uses cui-javadoc (exists)
⚠️  code-reviewer uses cui-external-skill (external bundle - verify dependency)
❌ test-agent uses cui-missing-skill (not found)
```

Increment `integration_issues` for broken internal references.

#### Step 7.3: Check Circular Dependencies

Build dependency graph:
- Which agents call which commands
- Which agents use which skills
- Which commands invoke other commands

Detect cycles:
```
Circular Dependency Check:
✅ No circular dependencies detected
⚠️  Potential cycle: agent-a → skill-a → (agent-a uses it too) - review for logic issues
❌ Circular dependency: cmd-a → cmd-b → cmd-a
```

Increment `integration_issues` for circular dependencies.

#### Step 7.4: Check External Dependencies

If plugin.json has `dependencies` field:

Verify each dependency:
- Check if bundle exists in marketplace
- Check version compatibility
- Check for dependency conflicts

Report:
```
External Dependencies:
✅ cui-utility-commands: ^1.0.0 (found, compatible)
⚠️  cui-future-bundle: ^2.0.0 (not found in marketplace)
❌ cui-conflict-bundle: ^1.0.0 (incompatible version)
```

### Step 8: Validate Documentation

Display:
```
Step 6/8: Documentation Validation
```

#### Step 8.1: Check README.md Quality

Read `{bundle_path}/README.md`:

Verify includes:
- ✅ Title with bundle display name
- ✅ Overview/purpose section
- ✅ Component list (agents, commands, skills)
- ✅ Installation instructions
- ✅ Usage examples
- ✅ Architecture/structure description
- ✅ Contributing guidelines
- ✅ License information

Check for common issues:
- Empty sections with just placeholders
- Broken markdown links
- Missing component descriptions
- Outdated information (components listed that don't exist)

Report:
```
README.md Quality:
✅ All required sections present
✅ Component list complete and accurate
⚠️  Installation section has placeholder text
⚠️  No usage examples provided
❌ Lists "old-agent" that no longer exists
```

Increment `documentation_issues` for each issue.

#### Step 8.2: Check Component Documentation

Use Read to check README existence (Pattern 2):

```
# Check agents README
try:
    agents_readme = Read(file_path="{bundle_path}/agents/README.md")
    agents_readme_exists = True
except Exception:
    agents_readme_exists = False

# Check commands README
try:
    commands_readme = Read(file_path="{bundle_path}/commands/README.md")
    commands_readme_exists = True
except Exception:
    commands_readme_exists = False

# Check skills README
try:
    skills_readme = Read(file_path="{bundle_path}/skills/README.md")
    skills_readme_exists = True
except Exception:
    skills_readme_exists = False
```

If exists, check quality:
- Not just placeholder
- Lists actual components
- Provides guidance

Report:
```
Component Documentation:
✅ agents/README.md: complete
⚠️  commands/README.md: placeholder only
❌ skills/README.md: missing
```

Increment `documentation_issues` for issues.

### Step 9: Calculate Bundle Health Score

Display:
```
Step 7/8: Health Score Calculation
```

Calculate scores for each area:

**Structure Score (0-100):**
- Required directories: 40 points (10 each)
- Required files: 40 points (20 each for plugin.json, README)
- No unexpected files: 20 points

**Manifest Score (0-100):**
- Valid JSON: 30 points
- All required fields: 50 points (10 each)
- Optional fields complete: 20 points

**Component Health Score (0-100):**
- All components valid: 50 points
- No components with critical issues: 30 points
- Component count reasonable (>0): 20 points

**Integration Score (0-100):**
- No broken internal references: 50 points
- No circular dependencies: 30 points
- External dependencies valid: 20 points

**Documentation Score (0-100):**
- README complete: 50 points
- Component READMEs present: 30 points
- No placeholder content: 20 points

**Overall Health Score:**
- Average of all five scores
- Weight critical areas more heavily

Display:
```
Bundle Health Score:

Structure:      95/100 ⭐⭐⭐⭐⭐ Excellent
Manifest:       80/100 ⭐⭐⭐⭐   Good
Component Health: 70/100 ⭐⭐⭐    Fair
Integration:    85/100 ⭐⭐⭐⭐   Good
Documentation:  60/100 ⭐⭐⭐    Fair

OVERALL: 78/100 ⭐⭐⭐⭐ Good

Rating:
- 90-100: ⭐⭐⭐⭐⭐ Excellent - Marketplace ready
- 75-89:  ⭐⭐⭐⭐   Good - Minor improvements needed
- 60-74:  ⭐⭐⭐    Fair - Moderate work required
- 40-59:  ⭐⭐     Poor - Significant issues
- <40:    ⭐      Critical - Not ready for use
```

### Step 10: Generate Issue Report

Display:
```
Step 8/8: Issue Report
```

Categorize all issues:

**CRITICAL Issues (Must Fix):**
- Missing .claude-plugin/plugin.json
- Invalid plugin.json syntax
- Name mismatch (directory vs plugin.json)
- Broken internal references (agent → missing command)
- Circular dependencies
- Component with critical issues blocking bundle use

**WARNINGS (Should Fix):**
- Missing optional directories
- plugin.json missing optional fields
- Component count mismatch
- Naming convention violations (no cui- prefix)
- placeholder documentation
- Minor integration issues

**SUGGESTIONS (Nice to Have):**
- Add more comprehensive README sections
- Add component README files
- Improve documentation examples
- Add more keywords to plugin.json

Display full report:
```
Issue Report for {target_bundle}:

CRITICAL (3 issues):
1. plugin.json: name field "old-name" doesn't match directory "cui-project-quality-gates"
   Impact: Bundle may not be discovered correctly
   Fix: Update plugin.json name to "cui-project-quality-gates"

2. Integration: agent "custom-agent" references missing command "/cui-missing-command"
   Impact: Agent will fail when trying to invoke command
   Fix: Remove reference or create the command

3. Component: skill "cui-old-skill" missing SKILL.md file
   Impact: Skill cannot be loaded, breaks agents that reference it
   Fix: Create SKILL.md or remove skill directory

WARNINGS (5 issues):
1. Naming: command "buildVerify.md" should be "cui-build-verify.md"
   Impact: Inconsistent with bundle naming conventions
   Fix: Rename file to follow conventions

2. Documentation: README.md lists "old-agent" that doesn't exist
   Impact: Confusing for users
   Fix: Update README to remove old-agent

3. Manifest: plugin.json components lists 5 commands but 6 found
   Impact: Inventory mismatch, missing component documentation
   Fix: Add "cui-new-command" to plugin.json components list

4. Documentation: agents/README.md has placeholder content
   Impact: No guidance for developers
   Fix: Fill in actual agent descriptions

5. Structure: Found .DS_Store file in bundle root
   Impact: Unnecessary file in version control
   Fix: Remove .DS_Store, add to .gitignore

SUGGESTIONS (2 items):
1. Add more keywords to plugin.json for better discoverability
2. Add usage examples to README.md

Total: 10 issues found
Health Score: 78/100 (Good - minor improvements needed)
```

### Step 11: Offer Fixes

Display:
```
Found {total_issues} issues in {target_bundle}:
- Critical: {critical_issues}
- Warnings: {warnings}
- Suggestions: {suggestion_count}

Bundle Health Score: {score}/100 ({rating})

Options:
F - Fix all issues automatically
R - Review each issue individually before fixing
D - View detailed report only (no fixes)
Q - Quit

Please choose [F/r/d/q]:
```

**If F (Fix all):**
- Apply automatic fixes for deterministic issues
- Skip issues requiring user judgment
- Display progress

**If R (Review):**
- For each issue, show:
  - Severity
  - Problem description
  - Current state
  - Proposed fix
  - Options: Fix / Skip / Edit fix
- Apply selected fixes

**If D (Detailed report):**
- Display full report
- Save to file option
- Exit without fixes

### Step 12: Final Summary

After any fixes applied:

Display:
```
==================================================
Bundle Doctor - Analysis Complete
==================================================

Bundle: {target_bundle}
Location: {bundle_path}

Components:
- Agents: {component_agents}
- Commands: {component_commands}
- Skills: {component_skills}

Health Score: {score_before} → {score_after}/100

Issues:
- Total found: {total_issues}
- Fixed: {issues_fixed}
- Remaining: {remaining_issues}

Breakdown:
- Critical: {critical_before} → {critical_after}
- Warnings: {warnings_before} → {warnings_after}
- Suggestions: {suggestions_count}

Component Health:
- Agents with issues: {agents_with_issues}
- Commands with issues: {commands_with_issues}
- Skills with issues: {skills_with_issues}

{If score_after >= 90:}
✅ MARKETPLACE READY
This bundle meets high quality standards and is ready for distribution.
{Else if score_after >= 75:}
⚠️  GOOD QUALITY
Minor improvements recommended before marketplace release.
{Else if score_after >= 60:}
⚠️  MODERATE QUALITY
Moderate work needed before marketplace release.
{Else:}
❌ SIGNIFICANT ISSUES
Bundle needs substantial work before it can be released.
{End if}

Recommendations:
{If critical_after > 0:}
⚠️  Fix {critical_after} critical issues before using bundle
{End if}

{If deep_analysis_not_run:}
ℹ️  Run with deep component analysis for comprehensive quality check
{End if}

{If component_issues_found:}
ℹ️  Fix individual components with:
  - /cui-diagnose-agents {agent_name}
  - /cui-diagnose-commands {command_name}
  - /cui-diagnose-skills {skill_name}
{End if}

Next Steps:
1. {Highest priority fix recommendation}
2. {Second priority recommendation}
3. Re-run: /cui-diagnose-bundle {target_bundle}
```

## CRITICAL RULES

- **READ ENTIRE BUNDLE** before analyzing - holistic view essential
- **VALIDATE plugin.json THOROUGHLY** - manifest errors break discovery
- **CHECK INTEGRATION** - components must work together
- **VERIFY NAMING CONVENTIONS** - consistency across marketplace
- **CALCULATE HEALTH SCORE** - quantifiable quality metric
- **CATEGORIZE ISSUES PROPERLY** - Critical vs Warning vs Suggestion
- **OFFER COMPONENT-LEVEL ANALYSIS** - drill down for details
- **TRACK ALL METRICS** - comprehensive reporting
- **DETECT CIRCULAR DEPENDENCIES** - prevent integration problems
- **VALIDATE DOCUMENTATION** - critical for usability

## LESSONS LEARNED FROM PREVIOUS SESSIONS

### Lesson 1: Holistic Bundle View Required
**Issue**: Component-level diagnosis missed integration problems
**Solution**: Bundle-level analysis checks cross-component issues
**Prevention**: Always validate integration, not just individual components

### Lesson 2: plugin.json is Critical
**Issue**: Invalid plugin.json broke bundle discovery entirely
**Solution**: Thorough JSON validation with helpful error messages
**Prevention**: Validate syntax, required fields, and component inventory

### Lesson 3: Naming Consistency Matters
**Issue**: Inconsistent naming made marketplace confusing
**Solution**: Enforce conventions across all components
**Prevention**: Check bundle name, component names, follow "cui-" prefix

### Lesson 4: Integration Breaks are Silent
**Issue**: Agents referenced missing commands, failures at runtime
**Solution**: Validate all internal references during diagnosis
**Prevention**: Check agent→command, agent→skill, command→command references

### Lesson 5: Documentation is Often Placeholder
**Issue**: Bundles shipped with placeholder READMEs
**Solution**: Detect placeholder content, warn about low quality docs
**Prevention**: Check for "TODO", "placeholder", empty sections

### Lesson 6: Component Inventory Drift
**Issue**: plugin.json listed 5 components but 7 existed
**Solution**: Compare plugin.json with actual file count
**Prevention**: Automated inventory check, warn on mismatch

### Lesson 7: Health Score Provides Clarity
**Issue**: Hard to assess if bundle was "ready" for release
**Solution**: Quantifiable health score with clear thresholds
**Prevention**: Objective quality metric guides improvement

## USAGE EXAMPLES

### Analyze Specific Bundle
```
/cui-diagnose-bundle cui-project-quality-gates
```

### Interactive Mode (Select from List)
```
/cui-diagnose-bundle
[Select from menu]
```

### Auto-Fix Issues
```
/cui-diagnose-bundle cui-project-quality-gates fix
```

### Bundle Health Check Before Release
```
/cui-diagnose-bundle cui-my-new-bundle
# Verify score >= 90 before publishing
```

## INTEGRATION WITH OTHER COMMANDS

This command works with component-level diagnostics:

```bash
# Bundle-level analysis
/cui-diagnose-bundle my-bundle

# If component issues found, drill down:
/cui-diagnose-agents maven-project-builder
/cui-diagnose-commands cui-build-and-verify
/cui-diagnose-skills cui-javadoc

# Fix components, then re-check bundle:
/cui-diagnose-bundle my-bundle
```

## ERROR HANDLING

**If bundle not found:**
```
❌ ERROR: Bundle 'invalid-name' not found

Searched at:
- ~/git/cui-llm-rules/claude/marketplace/bundles/invalid-name/

Available bundles:
- cui-project-quality-gates
- cui-pull-request-workflow
- cui-documentation-standards
...
```

**If plugin.json invalid:**
```
❌ CRITICAL: Cannot parse plugin.json

Error: Unexpected token at line 15
File: {bundle_path}/.claude-plugin/plugin.json

This is a critical issue - bundle cannot be loaded.
Fix plugin.json syntax before continuing.
```

**If no components found:**
```
⚠️  WARNING: Bundle '{bundle_name}' has no components

Found:
- Agents: 0
- Commands: 0
- Skills: 0

An empty bundle is unusual. This bundle may be:
1. Newly created (use creation wizards to add components)
2. Incorrectly structured
3. Missing component files

Add components with:
- /cui-create-agent scope=marketplace
- /cui-create-command scope=marketplace
- /cui-create-skill scope=marketplace
```

## NOTES

- This command provides BUNDLE-LEVEL analysis (structure, integration, manifest)
- For COMPONENT-LEVEL analysis, use component-specific diagnose commands
- Health score helps objectively assess marketplace readiness
- Bundle diagnosis should be run before releasing to marketplace
- Re-run after fixing issues to verify improvements
- Combine with component diagnostics for comprehensive quality assurance
