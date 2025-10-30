---
name: cui-skill-quality-standards
description: Quality standards and analysis patterns for skills, commands, and agents in Claude Code marketplace
allowed-tools: [Read, Grep, Glob]
---

# Skill Quality Standards

Quality standards, analysis patterns, and validation rules for Claude Code marketplace components (skills, commands, agents).

## When to Use This Skill

Use this skill when you need to:
- Validate skills for structure, YAML frontmatter, and content quality
- Check commands for bloat, clarity, and anti-bloat compliance
- Analyze agents for tool coverage, best practices, and structural issues
- Apply consistent quality standards across marketplace components

## Workflow

### For Skill Analysis

Read skill quality standards and patterns:

```
Read: standards/skill-quality-standards.md
Read: standards/skill-analysis-patterns.md
```

These provide:
- 16 common skill issue patterns
- Quality scoring criteria (architecture, content)
- Structural requirements
- YAML frontmatter standards
- Content quality requirements (duplication, conflicts, ambiguities)
- "Minimize without information loss" principle

### For Command Analysis

Read command quality standards and patterns:

```
Read: standards/command-quality-standards.md
Read: standards/command-analysis-patterns.md
```

These provide:
- 20 common command issue patterns
- 8 anti-bloat rules (CRITICAL for preventing bloat)
- Command best practices (15 practices)
- Bloat detection algorithm (>500 lines = bloated)
- Restructuring strategies (extract to skills)

### For Agent Analysis

Read agent quality standards and patterns:

```
Read: standards/agent-quality-standards.md
Read: standards/agent-analysis-patterns.md
```

These provide:
- 20 common agent issue patterns
- Agent best practices (9 core practices)
- Tool coverage analysis (Tool Fit Score formula)
- Quality scoring criteria (Tool Fit, Precision, Compliance)
- Essential Rules synchronization patterns

## Standards Structure

### Skill Standards

**standards/skill-quality-standards.md** - Comprehensive quality requirements:
- Structural requirements (12 rules)
- Content quality requirements (8 rules)
- Scoring criteria (architecture + integrated content)
- YAML frontmatter standards
- Tool access standards
- Directory structure standards

**standards/skill-analysis-patterns.md** - 16 common issue patterns:
- Pattern 1-5: Structural issues
- Pattern 6, 10: Configuration issues
- Pattern 7, 9: Integration issues
- Pattern 11-16: Content quality issues

### Command Standards

**standards/command-quality-standards.md** - Command quality requirements:
- Command best practices (15 practices)
- Anti-bloat rules (8 CRITICAL rules)
- YAML frontmatter standards
- Complexity scoring (bloat detection)
- "Minimize without information loss" principle
- Restructuring pattern (when to extract to skills)

**standards/command-analysis-patterns.md** - 20 common issue patterns:
- Pattern 1-10: Workflow and structure issues
- Pattern 11: Bloat detection (>500 lines)
- Pattern 12-15: Content quality issues
- Pattern 16-20: YAML and documentation issues

### Agent Standards

**standards/agent-quality-standards.md** - Agent quality requirements:
- Agent best practices (9 core practices)
- YAML frontmatter standards
- Tool coverage analysis
- Quality thresholds (Tool Fit, Precision, Compliance)
- Essential Rules format and synchronization
- Permission patterns validation

**standards/agent-analysis-patterns.md** - 20 common issue patterns:
- Pattern 1-6: Tool coverage and configuration
- Pattern 7-10: Essential Rules and content
- Pattern 11-17: Quality and complexity
- Pattern 18-20: Documentation and permissions

## Key Principles

**Minimize Content Without Information Loss:**
- Remove documentation-only noise (external/broken links)
- Remove duplicate content (consolidate, cross-reference)
- Remove ambiguous language (use specific criteria)
- Keep all actual information

**Quality Thresholds:**
- Architecture Score: 90-100 = Excellent, 75-89 = Good, <75 = Needs work
- Integrated Content Score: 90-100 = Excellent, 75-89 = Good, <60 = Poor

**Pattern Priority:**
- CRITICAL: Must fix before use (structural, broken refs, conflicts)
- WARNING: Should fix for quality (config, ambiguities, noise)
- SUGGESTION: Nice to have (documentation, examples)
