# CUI Maven Rules Skill

Comprehensive Maven standards for build verification, POM maintenance, dependency management, and Maven integration.

## Overview

This skill provides authoritative Maven standards for CUI projects. It covers all aspects of Maven usage including build processes, POM file maintenance, dependency management, Maven wrapper updates, and integration with JavaScript tooling and quality tools.

## Standards Files

### pom-maintenance.md
Comprehensive POM maintenance process covering:
- Maven wrapper maintenance and updates
- BOM (Bill of Materials) management
- Dependency management standards
- Scope optimization (compile, provided, runtime, test)
- Property naming conventions
- OpenRewrite integration
- Multi-module considerations
- Version management policies

**Key sections:**
- Pre-maintenance checklist
- Maven wrapper updates
- BOM structure and usage rules
- Dependency aggregation and consolidation
- Scope analysis and optimization
- OpenRewrite recipe execution
- Quality gates and verification

### maven-integration.md
Maven integration with build tools and JavaScript tooling:
- Frontend-maven-plugin configuration
- Node.js and npm version management
- Maven phase integration
- Script integration with package.json
- SonarQube integration and coverage paths
- Build environment standards
- CI/CD integration
- Project-specific adaptations

**Key sections:**
- Frontend-maven-plugin setup
- Maven phase mapping
- Node.js version management
- Environment variables
- SonarQube properties
- Troubleshooting common issues
- Performance optimization

## Usage

This skill is automatically activated by agents that need Maven standards, particularly:

- **maven-project-builder agent**: Loads this skill at workflow start to understand build verification standards, quality gate criteria, and issue handling procedures
- **POM maintenance workflows**: Reference this skill for dependency management and BOM patterns
- **Integration workflows**: Use this skill for configuring Maven with JavaScript tooling

## Skill Activation

```
Skill: cui-maven-rules
```

When activated, the skill loads all standards files, making Maven best practices and patterns available to the agent.

## Standards Coverage

### Build Verification ✅
- Pre-commit profile execution
- Build success criteria
- Timeout calculation and tracking
- Output analysis
- Iterative fix workflow

### POM Maintenance ✅
- BOM management patterns
- Property naming conventions
- Dependency aggregation
- Scope optimization
- OpenRewrite integration

### Maven Integration ✅
- Frontend-maven-plugin
- Node.js version management
- Maven phase mapping
- SonarQube integration
- CI/CD standards

### Quality Standards ✅
- Compilation error handling
- Test failure resolution
- Code warning fixes
- JavaDoc mandatory fixes
- Dependency analysis

## Tool Access

Allowed tools:
- **Read**: Load standards files
- **Grep**: Search standards content

## Integration

This skill integrates with:
- **cui-javadoc skill**: For JavaDoc fix standards
- **cui-java-unit-testing skill**: For testing standards
- **cui-frontend-development skill**: For JavaScript Maven integration

## Version History

### 0.1.0 (Initial Release)
- Consolidated POM maintenance standards
- Consolidated Maven integration standards
- Created as part of cui-maven bundle
- Standards sourced from:
  - standards/process/pom-maintenance.adoc
  - standards/javascript/maven-integration-standards.adoc

## Maintenance

To update standards:
1. Edit files in the `standards/` directory
2. Changes take effect on next skill activation
3. Test with agents that use this skill
4. Validate with `/cui-diagnose-skills`

## Related Documentation

- Bundle README: ../../README.md
- maven-project-builder agent: ../../agents/maven-project-builder.md
- cui-build-and-verify command: ../../commands/cui-build-and-verify.md

---

*Part of the CUI Maven Tools bundle - Comprehensive Maven support for CUI projects*
