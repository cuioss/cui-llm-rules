# CUI Marketplace

Reusable components for AI-assisted development in CUI projects.

## Overview

The marketplace provides production-ready, reusable components that AI assistants can use to enforce CUI standards and best practices. All components are thoroughly documented, quality-verified, and ready for production use.

## Marketplace Components

### Bundles

**Location**: `marketplace/bundles/`

**Purpose**: Self-contained, production-ready bundles combining skills, agents, and commands for specific development domains

**Active Bundles**:
- **cui-java-expert**: Java development standards and tooling (5 skills, 3 agents, 9 commands)
- **cui-frontend-expert**: JavaScript/frontend development standards and tooling (8 skills, 3 agents, 7 commands)
- **cui-maven**: Maven build and verification tools (1 skill, 1 agent, 1 command)
- **cui-task-workflow**: Complete development workflow from issue to PR (2 skills, 8 agents, 6 commands)
- **cui-documentation-standards**: AsciiDoc documentation standards and review (1 skill, 4 agents, 2 commands)
- **cui-utilities**: General-purpose utility commands and diagnostics (4 skills, 1 agent, 6 commands)
- **cui-plugin-development-tools**: Claude Code marketplace development tools (3 skills, 7 agents, 13 commands)
- **cui-requirements**: Requirements and planning documentation (4 skills, 0 agents, 1 command)

**See**: `bundles/*/README.md` for bundle documentation

---

### Agents

**Location**: `marketplace/agents/`

**Status**: Legacy directory - agents now bundled within bundles

---

### Commands & Skills

**Status**: All commands and skills are now organized within bundles for better modularity and self-containment

**Example Commands**:
- `/java-implement-tests`: Generate Java unit tests with JUnit
- `/js-implement-code`: Implement JavaScript code features
- `/doc-review-technical-docs`: Review AsciiDoc documentation
- `/maven-build-and-fix`: Build with Maven and fix issues
- `/orchestrate-workflow`: Complete issue-to-PR workflow
- `/plugin-create-skill`: Create new marketplace skills

See individual bundle READMEs for complete command listings

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

- `/plugin-diagnose-skills` - Verify skill quality and structure
- `/plugin-diagnose-agents` - Verify agent quality and architecture
- `/plugin-diagnose-commands` - Verify command quality and clarity
- `/plugin-diagnose-bundle` - Verify complete bundle integration
- `/plugin-diagnose-marketplace` - Diagnose marketplace configuration

### Standards Compliance

All components must:
- Follow CUI coding standards
- Use professional, technical tone
- Provide working, tested examples
- Integrate with existing ecosystem
- Maintain high quality scores

## Marketplace Statistics

### Current Status
- **Total Bundles**: 8
- **Total Components**: 80 (28 skills + 27 agents + 45 commands)
- **Status**: Production Ready ✅

### Component Breakdown
- **Bundles**: 8 production-ready bundles
- **Skills**: 28 across all domains
- **Agents**: 27 specialized task agents
- **Commands**: 45 slash commands

### Documentation
- **Total Lines**: 9,616
- **README Files**: 8
- **Standards Files**: Multiple per component
- **Code Examples**: 100+ across all components

## Roadmap

### Phase 1: Core Marketplace (Complete) ✅
- ✅ 28 production-ready skills
- ✅ 27 specialized agents
- ✅ 45 slash commands
- ✅ 8 integrated bundles
- ✅ Quality verification system
- ✅ Comprehensive documentation

### Phase 2: Enhanced Integration (In Progress)
- ✅ Bundle-based organization
- ✅ Agent coordination patterns
- ✅ Cross-bundle workflows
- [ ] Advanced composition patterns
- [ ] Performance optimization

### Phase 3: Expansion (Planned)
- [ ] Additional language support
- [ ] Framework-specific bundles
- [ ] Testing framework extensions
- [ ] CI/CD integration bundles

### Phase 4: Templates & Scaffolding (Planned)
- [ ] Project templates
- [ ] Code generation templates
- [ ] Documentation templates
- [ ] Test scaffolding

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

**Last Updated**: 2025-11-18
**Status**: Full marketplace production ready (8 bundles, 80 total components)
**Components**: 28 skills, 27 agents, 45 commands ⭐
