# CUI Marketplace Architecture Skill

Architecture rules and validation patterns for Claude Code marketplace components.

## Purpose

Ensures marketplace components follow clean architecture principles:
- **Skills are self-contained** (no external file dependencies)
- **Agents use Skills** (not direct file references)
- **Clean reference patterns** (only URLs, skills, and internal files)
- **Bundle cohesion** (functional organization)

## Standards Included

### Core Architecture Rules
- **architecture-rules.md**: Four fundamental rules for marketplace components
- **reference-patterns.md**: Allowed vs prohibited reference types with examples

### Validation Procedures
- **self-containment-validation.md**: How to validate skills are self-contained
- **skill-usage-patterns.md**: How agents should properly use skills

### Scoring System
- **scoring-criteria.md**: Quantifiable compliance metrics and thresholds

## Usage

This skill is invoked by diagnostic and creation commands:

### In Creation Commands
```
/cui-create-skill

Step X: Validate Architecture
Skill: cui-marketplace-architecture

[Applies architecture rules to prevent violations]
```

### In Diagnostic Commands
```
/cui-diagnose-skills
/cui-diagnose-agents
/cui-diagnose-bundle

Step Y: Architecture Validation
Skill: cui-marketplace-architecture

[Loads validation patterns and scoring criteria]
```

## Key Concepts

### Self-Contained Skills

Skills must contain ALL content in their own directory:
```
skill-name/
├── SKILL.md
├── README.md
└── standards/
    ├── standard1.md  ← All content here
    ├── standard2.md
    └── standard3.md
```

**NOT ALLOWED**:
- `Read: ../../../../standards/external.adoc`
- `Read: ~/git/cui-llm-rules/standards/file.adoc`

**ALLOWED**:
- `Read: standards/internal.md`
- `Skill: cui-other-skill`
- `https://external-url.com`

### Skill Usage in Agents

Agents needing standards must use Skills:

✅ **CORRECT**:
```yaml
tools: Read, Edit, Write, Skill
```
```
Skill: cui-java-core
```

❌ **INCORRECT**:
```
Read: ~/git/cui-llm-rules/standards/java-core.adoc
```

## Benefits

### For Skill Authors
- Clear guidelines for creating portable skills
- Validation catches issues early
- Automatic compliance scoring

### For Bundle Maintainers
- Bundle health scoring
- Identifies architecture violations
- Ensures marketplace readiness

### For Marketplace
- All skills are distributable
- Consistent quality across bundles
- No broken dependencies

## Compliance Scoring

Components are scored 0-100:

- **90-100**: ✅ Excellent - Marketplace ready
- **75-89**: ⚠️ Good - Minor improvements
- **60-74**: ⚠️ Fair - Moderate work needed
- **< 60**: ❌ Poor - Significant issues

## Related Documentation

- Plugin Architecture: standards/plugin-architecture.md (internalized from claude/doc)
- Bundle Design: standards/bundling-architecture.md (internalized from claude/doc)
- Agent Design: standards/agent-design-principles.md (internalized from claude/doc)

## Version

1.0.0 - Initial release

## License

Apache-2.0
