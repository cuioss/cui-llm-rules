---
name: cui-diagnose-bundle
description: Analyze and verify entire bundle for structure, integration, quality, and marketplace readiness
---

# Bundle Doctor - Verify Complete Bundle

Comprehensive analysis of entire bundle including structure, skills, commands, agents, and integration.

## PARAMETERS

- **bundle-name** (optional): Specific bundle to analyze (e.g., `cui-maven`)
- **No parameters**: Analyze current bundle or prompt for selection

## TOOL USAGE REQUIREMENTS

```
Skill: cui-utility-commands:cui-diagnostic-patterns
```

✅ Use `Glob`, `Grep`, `Read` (never Bash alternatives)

## WORKFLOW INSTRUCTIONS

### Load Analysis Standards

```
Skill: cui-plugin-development-tools:cui-skill-quality-standards
```

This skill provides validation standards for skills, commands, and agents.

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
- Validates all skills in bundle/skills/
- Checks self-containment, quality, standards
- Returns skill-level issues

**Commands Analysis:**
```
Run: /cui-diagnose-commands scope=bundle bundle-name=<name>
```
- Validates all commands in bundle/commands/
- Checks bloat, clarity, anti-bloat compliance
- Returns command-level issues

**Agents Analysis:**
```
Run: /cui-diagnose-agents scope=bundle bundle-name=<name>
```
- Validates all agents in bundle/agents/
- Checks tool coverage, best practices
- Returns agent-level issues

### Integration Validation

Cross-component checks:

1. **Inventory Accuracy**
   - plugin.json lists all components correctly
   - No missing/extra entries

2. **Cross-References**
   - Commands reference existing skills
   - Agents use valid skill references
   - No broken dependencies

3. **Naming Consistency**
   - Bundle name matches directory
   - Component names follow conventions
   - No conflicts with other bundles

4. **Self-Containment**
   - Skills don't reference external files
   - Commands don't reference external standards
   - Agents portable (no absolute paths)

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

## CRITICAL RULES

- **LOAD STANDARDS** - Reference quality standards skill
- **DELEGATE TO SPECIALISTS** - Use component-specific diagnose commands
- **CHECK INTEGRATION** - Validate cross-component references
- **VALIDATE INVENTORY** - Ensure plugin.json accuracy
- **ENFORCE SELF-CONTAINMENT** - No external dependencies
- **CALCULATE SCORES** - Overall bundle quality score
- **MARKETPLACE READINESS** - All quality gates must pass

## STANDARDS REFERENCED

**Skill: cui-plugin-development-tools:cui-skill-quality-standards**

**Related Commands:**
- /cui-diagnose-skills - For detailed skill analysis
- /cui-diagnose-commands - For detailed command analysis
- /cui-diagnose-agents - For detailed agent analysis
