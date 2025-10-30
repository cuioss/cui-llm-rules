---
name: cui-skill-quality-standards
description: Quality standards and analysis patterns for commands and agents in Claude Code marketplace
allowed-tools: [Read]
---

# Command and Agent Quality Standards

Quality standards, analysis patterns, and validation rules for Claude Code marketplace commands and agents.

## When to Use This Skill

Use this skill when you need to:
- Check commands for bloat, clarity, and anti-bloat compliance
- Analyze agents for tool coverage, best practices, and structural issues
- Apply consistent quality standards across marketplace components

**Note**: Skill analysis is now handled by specialized agents (cui-analyze-standards-file, cui-analyze-integrated-standards) rather than this skill.

## Workflow

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
