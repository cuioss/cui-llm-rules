# CUI Marketplace

Reusable components for AI-assisted development in CUI projects.

## Overview

The marketplace provides production-ready, reusable components that AI assistants can use to enforce CUI standards and best practices. All components are thoroughly documented, quality-verified, and ready for production use.

## Marketplace Components

### Skills

**Location**: `marketplace/skills/`

**Purpose**: Comprehensive standards and patterns for specific development domains

**Count**: 8 skills (97.75/100 average quality)

**Categories**:
- **Java Development**: Core patterns, unit testing, JavaDoc, CDI/Quarkus
- **Frontend Development**: JavaScript, CSS, web components, testing
- **Documentation**: README, AsciiDoc, technical writing
- **Project Management**: Project setup, requirements engineering

**See**: [Skills README](skills/README.md) for complete catalog

---

### Agents (Planned)

**Location**: `marketplace/agents/` (future)

**Purpose**: Specialized AI agents for complex, multi-step tasks

**Examples** (future):
- code-reviewer: Comprehensive code review agent
- test-generator: Automated test generation
- doc-generator: Documentation generation
- refactoring-agent: Code refactoring automation

---

### Commands (Planned)

**Location**: `marketplace/commands/` (future)

**Purpose**: Reusable slash commands for common tasks

**Examples** (future):
- /review-pr: Review pull request
- /generate-tests: Generate unit tests
- /update-docs: Update documentation
- /analyze-coverage: Analyze test coverage

---

## Using Marketplace Components

### For AI Assistants

Marketplace components are designed to be:
- **Self-describing**: Clear metadata in frontmatter
- **Context-aware**: Activate based on task context
- **Composable**: Work together seamlessly
- **Standards-based**: Enforce consistent practices

### For Developers

Each component includes:
- **README.md**: Human-readable documentation
- **Examples**: Working code examples
- **Integration guide**: How to use with other components
- **Quality verification**: Validation and testing guidance

## Quality Standards

All marketplace components must meet:

### Structure Requirements
- ✅ Valid YAML frontmatter
- ✅ Clear purpose and description
- ✅ Proper file organization
- ✅ Human and AI documentation

### Content Requirements
- ✅ No harmful duplication
- ✅ No conflicts or contradictions
- ✅ Precise, specific guidance
- ✅ Complete domain coverage
- ✅ High coherence and usability

### Documentation Requirements
- ✅ README.md for humans
- ✅ Primary file for AI (SKILL.md, AGENT.md, etc.)
- ✅ Detailed standards/instructions
- ✅ Working code examples
- ✅ Integration guidance

### Quality Thresholds
- **Minimum acceptable**: 75/100
- **Good quality**: 85-89/100
- **Excellent quality**: 90-100/100
- **Current average**: 97.75/100 ⭐

## Component Lifecycle

### Development
1. Create component structure
2. Write primary file (SKILL.md, etc.)
3. Add human documentation (README.md)
4. Create detailed standards/instructions
5. Add working examples

### Verification
1. Run quality checker (e.g., `/diagnose-skills`)
2. Verify no duplication, conflicts, ambiguities
3. Check integration with other components
4. Test with real development tasks
5. Ensure quality score ≥ 75/100

### Maintenance
1. Update for new standards
2. Add new examples
3. Improve based on feedback
4. Re-verify quality periodically
5. Keep documentation synchronized

## Contributing

### Creating New Components

To contribute a new marketplace component:

1. **Choose component type** (skill, agent, command)
2. **Follow naming conventions** (cui-feature-name)
3. **Create required structure** (README.md, primary file, standards)
4. **Add quality content** (no duplication, precise, complete)
5. **Include examples** (from real unit tests)
6. **Verify quality** (run quality checker)
7. **Submit for review** (ensure score ≥ 75/100)

### Quality Verification Tools

- `/diagnose-skills` - Verify skill quality
- `/agent-doctor` - Verify agent quality (future)
- `/command-doctor` - Verify command quality (future)

### Standards Compliance

All components must:
- Follow CUI coding standards
- Use professional, technical tone
- Provide working, tested examples
- Integrate with existing ecosystem
- Maintain high quality scores

## Marketplace Statistics

### Current Status
- **Total Components**: 8 (skills only)
- **Average Quality**: 97.75/100
- **Critical Issues**: 0
- **Status**: Production Ready ✅

### Component Breakdown
- **Skills**: 8 (100% excellent quality)
- **Agents**: 0 (planned)
- **Commands**: 0 (planned)

### Documentation
- **Total Lines**: 9,616
- **README Files**: 8
- **Standards Files**: Multiple per component
- **Code Examples**: 100+ across all components

## Roadmap

### Phase 1: Skills (Complete) ✅
- ✅ 8 production-ready skills
- ✅ Comprehensive documentation
- ✅ Quality verification system
- ✅ Integration guidelines

### Phase 2: Agents (Planned)
- [ ] Agent marketplace structure
- [ ] Quality verification system
- [ ] Initial agent set
- [ ] Integration patterns

### Phase 3: Commands (Planned)
- [ ] Command marketplace structure
- [ ] Quality verification system
- [ ] Common command library
- [ ] Documentation system

### Phase 4: Templates (Planned)
- [ ] Project templates
- [ ] Code templates
- [ ] Documentation templates
- [ ] Test templates

## Support

For issues or questions:

1. Check component README.md files
2. Review component primary files
3. Consult standards documentation
4. Run quality verification tools
5. Report issues in repository

## License

Part of the CUI LLM Rules documentation system for CUI OSS projects.

---

**Last Updated**: 2025-10-24
**Status**: Skills marketplace production ready, future components planned
**Quality**: 97.75/100 average across all components ⭐
