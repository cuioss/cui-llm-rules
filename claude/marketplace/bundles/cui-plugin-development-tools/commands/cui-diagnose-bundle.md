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
- **DELEGATE TO SPECIALISTS** - Use component-specific diagnose commands (handle failures gracefully)
- **CHECK INTEGRATION** - Validate cross-component references
- **VALIDATE INVENTORY** - Ensure plugin.json accuracy (abort if missing/invalid)
- **ENFORCE SELF-CONTAINMENT** - No external dependencies
- **CALCULATE SCORES** - Overall bundle quality score
- **MARKETPLACE READINESS** - All quality gates must pass

## STATISTICS TRACKING

Track throughout workflow:
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
