# CUI Skills Marketplace

Comprehensive skills library for CUI (Common User Interface) OSS project development.

## Overview

This directory contains production-ready skills that provide standards, patterns, and best practices for CUI development. Skills are designed for AI assistants (like Claude) to enforce consistent, high-quality code across all CUI projects.

## Skill Ecosystem Quality

- **Total Skills**: 8
- **Average Quality Score**: 97.75/100
- **Status**: All skills production-ready
- **Total Documentation**: 9,616 lines
- **Critical Issues**: 0

## Available Skills

### Core Java Development

#### 1. [cui-java-core](cui-java-core/)

**Purpose**: Foundation for all Java development in CUI projects

**Covers**:
- Core patterns (code organization, naming, exception handling)
- Null safety with JSpecify @NullMarked
- Lombok patterns (@Delegate, @Builder, @Value)
- Modern Java features (records, switch expressions, streams)
- DSL-style constants organization
- CuiLogger framework

**When to Use**: Always for Java development

**Quality Score**: 99/100 ⭐⭐

---

#### 2. [cui-java-unit-testing](cui-java-unit-testing/)

**Purpose**: Comprehensive unit testing standards for CUI Java projects

**Covers**:
- JUnit 5 core patterns (AAA structure, assertions)
- Value object contract testing
- CUI test generator framework (mandatory)
- MockWebServer for HTTP testing
- Integration testing setup

**When to Use**: Writing or reviewing Java tests

**Quality Score**: 98/100 ⭐

---

#### 3. [cui-javadoc](cui-javadoc/)

**Purpose**: High-quality JavaDoc documentation standards

**Covers**:
- Core JavaDoc principles and tag order
- Class and package documentation
- Method and field documentation
- Code examples and formatting

**When to Use**: Documenting Java APIs

**Quality Score**: 98/100 ⭐

---

#### 4. [cui-java-cdi](cui-java-cdi/)

**Purpose**: CDI and Quarkus development standards

**Covers**:
- CDI dependency injection (constructor injection ONLY)
- Container security and configuration
- CDI testing patterns
- Quarkus native image optimization

**When to Use**: Developing CDI/Quarkus applications

**Quality Score**: 97/100 ⭐

---

### Frontend Development

#### 5. [cui-frontend-development](cui-frontend-development/)

**Purpose**: Frontend development standards for CUI projects

**Covers**:
- Modern JavaScript (ES2022+, vanilla preference)
- CSS development (custom properties, Grid/Flexbox)
- Lit web components
- JSDoc documentation
- Cypress E2E testing

**When to Use**: Frontend JavaScript/CSS development

**Quality Score**: 97/100 ⭐

---

### Documentation & Project Management

#### 6. [cui-documentation](cui-documentation/)

**Purpose**: General technical documentation standards

**Covers**:
- Core documentation principles (professional tone, no marketing)
- README structure and best practices
- AsciiDoc formatting (critical: blank lines before lists)

**When to Use**: Writing README, AsciiDoc, or technical guides

**Quality Score**: 98/100 ⭐

---

#### 7. [cui-project-setup](cui-project-setup/)

**Purpose**: Project initialization and configuration standards

**Covers**:
- Maven project structure and configuration
- Parent POM usage (cui-java-parent)
- Build plugin configuration (via parent POM)
- Multi-module project organization

**When to Use**: Initializing new CUI projects

**Quality Score**: 98/100 ⭐

---

#### 8. [cui-requirements](cui-requirements/)

**Purpose**: Requirements engineering and planning standards

**Covers**:
- SMART requirements criteria
- Requirements document structure
- Technical specifications
- Acceptance criteria (Given/When/Then)

**When to Use**: Gathering requirements or writing specifications

**Quality Score**: 97/100 ⭐

---

## Skill Usage Guide

### How Skills Work

Each skill contains:
- **SKILL.md** - AI-consumable instructions with workflow and standards
- **README.md** - Human-readable documentation with examples
- **standards/** - Detailed standards files for specific aspects
- **VALIDATION.md** - Quality verification report (where applicable)

### Activating Skills

Skills are activated by AI assistants based on:
1. **Context matching** - Skill description matches the task
2. **Explicit invocation** - User requests specific skill by name
3. **Automatic loading** - Based on file types or project structure

### Skill Combinations

**Complete Java Development**:
```yaml
skills:
  - cui-java-core           # Foundation
  - cui-java-unit-testing   # Testing
  - cui-javadoc             # Documentation
```

**Quarkus/CDI Projects**:
```yaml
skills:
  - cui-java-core
  - cui-java-cdi
  - cui-java-unit-testing
```

**Full-Stack Application**:
```yaml
skills:
  - cui-java-core           # Backend
  - cui-java-cdi            # CDI/Quarkus
  - cui-frontend-development # Frontend
  - cui-documentation       # Docs
```

**New Project Setup**:
```yaml
skills:
  - cui-project-setup       # Initialization
  - cui-requirements        # Planning
  - cui-documentation       # Documentation
```

## Skill Quality Standards

All skills meet these quality criteria:

### Structure
- ✅ Valid YAML frontmatter (name, description, tools)
- ✅ Clear workflow with numbered steps
- ✅ Conditional loading logic where appropriate
- ✅ Working code examples
- ✅ Quality checklists

### Content Quality
- ✅ No harmful duplication (DRY principle)
- ✅ No conflicts between standards
- ✅ Precise, specific requirements (not vague)
- ✅ Complete domain coverage
- ✅ High coherence and usability

### Documentation
- ✅ SKILL.md for AI consumption
- ✅ README.md for human developers
- ✅ Detailed standards files
- ✅ Comprehensive examples
- ✅ Integration guidance

## Creating New Skills

To create a new skill:

1. **Create skill directory** in `claude/marketplace/skills/skill-name/`
2. **Add SKILL.md** with YAML frontmatter and workflow
3. **Add README.md** for human documentation
4. **Create standards/** directory with detailed standards
5. **Add code examples** from real unit tests
6. **Verify quality** with `/diagnose-skills skill-name`

### Required YAML Frontmatter

```yaml
---
name: skill-name
description: Clear description of when and why to use this skill
tools: [Read, Edit, Write, Bash, Grep, Glob]  # Adjust as needed
---
```

### Skill Naming Conventions

- Use kebab-case: `cui-feature-name`
- Prefix with `cui-` for CUI-specific skills
- Be descriptive and specific
- Examples: `cui-java-core`, `cui-frontend-development`

## Maintenance

### Verifying Skill Quality

Run skill doctor on all skills:
```bash
/diagnose-skills global
```

Or verify specific skill:
```bash
/diagnose-skills cui-java-core
```

### Updating Skills

When updating skills:
1. Update standards files with new requirements
2. Update code examples to match
3. Run `/diagnose-skills` to verify quality
4. Update README.md with new features
5. Test with actual development tasks

### Quality Metrics

Track these metrics:
- **Duplication Score**: Minimize duplicate content (target: 95+)
- **Conflict Score**: Zero conflicts between standards (target: 100)
- **Ambiguity Score**: Precise requirements (target: 95+)
- **Coherence Score**: Logical integration (target: 95+)
- **Usability Score**: AI-friendly (target: 95+)

## Support

For issues or questions:

1. Review individual skill README.md files
2. Check SKILL.md for AI workflow instructions
3. Consult standards files for detailed guidance
4. Run `/diagnose-skills` for quality verification
5. Report issues in repository

## License

Part of the CUI LLM Rules documentation system for CUI OSS projects.

---

**Last Updated**: 2025-10-24
**Maintained By**: CUI Development Team
**Status**: Production Ready ✅
