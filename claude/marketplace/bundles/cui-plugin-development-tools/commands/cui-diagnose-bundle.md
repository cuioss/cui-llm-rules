---
name: cui-diagnose-bundle
description: Analyze and verify entire bundle for structure, integration, quality, and marketplace readiness
---

# Bundle Doctor - Verify Complete Bundle

Comprehensive analysis of entire bundle including structure, skills, commands, agents, and integration.

## PARAMETERS

- **bundle-name** (optional): Specific bundle to analyze (e.g., `cui-maven`)
- **--save-report** (optional): Write Markdown report to project root. Default: false (display only, no file created)
- **No parameters**: Analyze current bundle or prompt for selection

## TOOL USAGE REQUIREMENTS

```
Skill: cui-utility-commands:cui-diagnostic-patterns
```

✅ Use `Glob`, `Grep`, `Read` (never Bash alternatives)

## WORKFLOW INSTRUCTIONS

### Step 0: Parameter Validation

**Validate bundle-name parameter:**
1. If bundle-name provided, verify it exists:
   - Use Glob to check bundle directory exists
   - If not found: Display error "Bundle '{bundle-name}' not found" and abort
2. If not provided, discover available bundles and prompt user to select
3. Validate --save-report flag if present (boolean value)

### Workflow Overview

1. **Discover Bundle** - Identify bundle and components
2. **Validate Structure** - Check plugin.json, directories, README
3. **Analyze Components** - Delegate to specialized diagnose commands
4. **Integration Check** - Cross-component references and dependencies
5. **Report** - Comprehensive bundle health report

### Bundle Structure Validation

Check bundle follows marketplace architecture:

```
bundle-name/
├── .claude-plugin/
│   └── plugin.json          ✅ Valid JSON, correct inventory
├── README.md                 ✅ Describes bundle purpose
├── skills/                   ✅ Self-contained skills
│   └── skill-name/
│       ├── SKILL.md
│       └── standards/
├── commands/                 ✅ Slash commands (*.md files)
│   └── command-name.md
└── agents/                   ✅ Agents (*.md files)
    └── agent-name.md
```

### Step 1: Validate Component Inventory

**CRITICAL: This step MUST execute and auto-fix inventory issues without user prompts.**

**Purpose:** Ensure plugin.json correctly registers all component files that exist in the bundle.

#### 1.1: Discover Actual Components

Use Glob to find all component files in the bundle:

**Agents:**
```
Glob: claude/marketplace/bundles/{bundle-name}/agents/*.md
```
Extract filenames (without .md extension) to list: `discovered_agents`

**Commands:**
```
Glob: claude/marketplace/bundles/{bundle-name}/commands/*.md
```
Extract filenames (without .md extension) to list: `discovered_commands`

**Skills:**
```
Glob: claude/marketplace/bundles/{bundle-name}/skills/*/SKILL.md
```
Extract parent directory names to list: `discovered_skills`

**Track statistics:**
- `discovered_agents_count`
- `discovered_commands_count`
- `discovered_skills_count`

#### 1.2: Read plugin.json Registration

```
Read: claude/marketplace/bundles/{bundle-name}/.claude-plugin/plugin.json
```

Parse JSON and extract arrays (may not exist):
- `registered_agents` = plugin.json["agents"] or []
- `registered_commands` = plugin.json["commands"] or []
- `registered_skills` = plugin.json["skills"] or []

Convert paths to component names:
- `"./agents/foo.md"` → `"foo"`
- `"./commands/bar.md"` → `"bar"`
- `"./skills/baz.md"` → `"baz"`

**Track statistics:**
- `registered_agents_count`
- `registered_commands_count`
- `registered_skills_count`

#### 1.3: Compare and Detect Mismatches

For each component type, compare discovered vs registered:

**Missing registrations:**
- `missing_agents` = discovered_agents - registered_agents
- `missing_commands` = discovered_commands - registered_commands
- `missing_skills` = discovered_skills - registered_skills

**Orphaned registrations:**
- `orphaned_agents` = registered_agents - discovered_agents
- `orphaned_commands` = registered_commands - discovered_commands
- `orphaned_skills` = registered_skills - discovered_skills

**Missing arrays:**
- `agents_array_missing` = "agents" key not in plugin.json
- `commands_array_missing` = "commands" key not in plugin.json
- `skills_array_missing` = "skills" key not in plugin.json

**Track issues:**
- Increment `inventory_issues` for each mismatch or missing array

#### 1.4: Report Inventory Issues

Display findings:
```
[INFO] Component Inventory Check:
  Agents:
    Discovered: {discovered_agents_count}
    Registered: {registered_agents_count}
    ✗ Missing array in plugin.json (if agents_array_missing)
    ✗ Not registered: {missing_agents} (if any)
    ✗ Orphaned: {orphaned_agents} (if any)

  Commands:
    Discovered: {discovered_commands_count}
    Registered: {registered_commands_count}
    ✗ Missing array in plugin.json (if commands_array_missing)
    ✗ Not registered: {missing_commands} (if any)
    ✗ Orphaned: {orphaned_commands} (if any)

  Skills:
    Discovered: {discovered_skills_count}
    Registered: {registered_skills_count}
    ✗ Missing array in plugin.json (if skills_array_missing)
    ✗ Not registered: {missing_skills} (if any)
    ✗ Orphaned: {orphaned_skills} (if any)
```

#### 1.5: Auto-Fix Inventory Issues

**CRITICAL: NO USER PROMPTS - Fix automatically**

If any inventory issues found:

1. **Read current plugin.json**
2. **Parse JSON to object**
3. **Build correct arrays:**
   ```
   agents_array = ["./agents/{name}.md" for name in discovered_agents]
   commands_array = ["./commands/{name}.md" for name in discovered_commands]
   skills_array = ["./skills/{name}.md" for name in discovered_skills]
   ```
4. **Update JSON object:**
   - Add or replace `"agents"` key with agents_array
   - Add or replace `"commands"` key with commands_array
   - Add or replace `"skills"` key with skills_array
5. **Write updated JSON back to plugin.json**
6. **Increment `inventory_fixes` statistic**

Display:
```
[FIX] Updated plugin.json component inventory:
  ✓ Added/updated agents array: {discovered_agents_count} entries
  ✓ Added/updated commands array: {discovered_commands_count} entries
  ✓ Added/updated skills array: {discovered_skills_count} entries
```

**If no issues found:**
```
[INFO] ✓ Component inventory is accurate
```

### Component Analysis

Delegate to specialized commands:

**Skills Analysis:**
```
Run: /cui-diagnose-skills scope=bundle bundle-name=<name>
```
**Error handling:** If command fails or not available, skip skills analysis and mark as "Not Analyzed" in report.

**Commands Analysis:**
```
Run: /cui-diagnose-commands scope=bundle bundle-name=<name>
```
**Error handling:** If command fails or not available, skip commands analysis and mark as "Not Analyzed" in report.

**Agents Analysis:**
```
Run: /cui-diagnose-agents scope=bundle bundle-name=<name>
```
**Error handling:** If command fails or not available, skip agents analysis and mark as "Not Analyzed" in report.

### Integration Validation

Cross-component checks:

1. **Inventory Accuracy** - Validate plugin.json lists all components (Read plugin.json, compare with Glob results)
2. **Cross-References** - Check references are valid (Grep for skill/command references, verify they exist)
3. **Naming Consistency** - Validate naming conventions (bundle name matches directory)
4. **Self-Containment** - Check for external dependencies (Grep for absolute paths, external references)

**Decision logic:**
- If any integration check fails: Continue analysis but mark as "Integration Issues" in final report
- If plugin.json missing or malformed: Mark as CRITICAL and abort bundle analysis

### Quality Gates

**Bundle Readiness Criteria:**

✅ **Structure**: Valid plugin.json, proper directories
✅ **Skills**: All pass quality standards (score ≥ 75)
✅ **Commands**: None bloated (all < 500 lines)
✅ **Agents**: All have tool fit ≥ 75%
✅ **Integration**: No broken references
✅ **Self-Containment**: No external dependencies

**Quality Score:**
```
Bundle Score = (
  structure_score * 0.2 +
  avg_skill_score * 0.3 +
  avg_command_score * 0.2 +
  avg_agent_score * 0.2 +
  integration_score * 0.1
)

- 90-100: Excellent - Marketplace ready
- 75-89: Good - Minor improvements needed
- 60-74: Fair - Moderate work required
- <60: Poor - Major rework needed
```

### Final Report

```
==================================================
Bundle Analysis Complete: <bundle-name>
==================================================

Structure: ✅ VALID
- plugin.json: ✅
- README.md: ✅
- Directories: ✅

Component Inventory: ✅ ACCURATE
- Agents: {discovered_agents_count} discovered, {registered_agents_count} registered
  {if inventory_fixes > 0: "✓ Fixed {inventory_fixes} registration issues"}
- Commands: {discovered_commands_count} discovered, {registered_commands_count} registered
- Skills: {discovered_skills_count} discovered, {registered_skills_count} registered

Components:
- Skills: <count> (<issues_count> issues)
  Average Quality: <score>/100
- Commands: <count> (<issues_count> issues)
  Bloated: <count> (>500 lines)
- Agents: <count> (<issues_count> issues)
  Average Tool Fit: <score>/100

Integration: ✅ CLEAN
- Inventory accurate: ✅
- Cross-references valid: ✅
- Naming consistent: ✅
- Self-contained: ✅

BUNDLE QUALITY SCORE: <score>/100 (<Excellent/Good/Fair/Poor>)

Status: <Marketplace Ready / Needs Improvement / Major Issues>

Recommendations:
<if issues>
- Fix <critical_count> critical issues
- Address <bloated_count> bloated commands
- Improve <low_quality_count> low-quality components
</if>

<if ready>
✅ Bundle is marketplace ready!
</if>
```

**If --save-report flag is set:**
- Write the complete report above to `bundle-diagnosis-report.md` in project root
- Inform user: "Report saved to: bundle-diagnosis-report.md"

**Default behavior (no flag):**
- Display report only (as shown above)
- Do NOT create any files

## CRITICAL RULES

- **VALIDATE PARAMETERS** - Check bundle-name exists before proceeding
- **LOAD STANDARDS** - Reference quality standards skill
- **VALIDATE INVENTORY FIRST** - Step 1 MUST execute before component analysis
- **AUTO-FIX INVENTORY** - Automatically fix missing/incorrect component arrays (NO user prompts)
- **USE GLOB FOR DISCOVERY** - Never use Bash ls/find, only Glob tool
- **DELEGATE TO SPECIALISTS** - Use component-specific diagnose commands (handle failures gracefully)
- **CHECK INTEGRATION** - Validate cross-component references
- **ENFORCE SELF-CONTAINMENT** - No external dependencies
- **CALCULATE SCORES** - Overall bundle quality score
- **MARKETPLACE READINESS** - All quality gates must pass

## STATISTICS TRACKING

Track throughout workflow:
- `discovered_agents_count`, `discovered_commands_count`, `discovered_skills_count`: Component files found
- `registered_agents_count`, `registered_commands_count`, `registered_skills_count`: Components registered in plugin.json
- `inventory_issues`: Count of inventory mismatches (missing arrays, unregistered, orphaned)
- `inventory_fixes`: Count of inventory corrections applied
- `components_analyzed`: Total components examined
- `skills_analyzed`, `commands_analyzed`, `agents_analyzed`: Counts per component type
- `integration_issues`: Count of integration problems found
- `total_issues`: Aggregate issue count across all components
- `quality_gates_passed`: Count of quality gates passed
- `marketplace_ready`: Boolean flag

## STANDARDS

Bundle analysis delegates to specialized diagnostic commands which use their own standards:
- Skill standards - Validated by cui-analyze-standards-file and cui-analyze-integrated-standards agents
- Command standards - bundles/cui-plugin-development-tools/standards/command-quality-standards.md
- Agent standards - bundles/cui-plugin-development-tools/standards/agent-quality-standards.md

**Related Commands:**
- /cui-diagnose-skills - For detailed skill analysis
- /cui-diagnose-commands - For detailed command analysis
- /cui-diagnose-agents - For detailed agent analysis
