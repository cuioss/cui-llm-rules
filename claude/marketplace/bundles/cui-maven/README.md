# CUI Maven Tools

Comprehensive Maven build, verification, and POM maintenance tools for CUI projects.

## Overview

This bundle provides complete Maven workflow support for CUI projects, including build verification, quality gate enforcement, POM maintenance standards, and Maven best practices. It ensures consistent build processes, proper dependency management, and comprehensive quality checks across all CUI Maven-based projects.

## Components

### Agents

Agents in this bundle:

- **maven-builder** - Central agent for executing configurable Maven builds with output capture, filtering, and performance tracking
- **maven-project-builder** - Comprehensive project verification agent that delegates build execution to maven-builder, analyzes output, fixes all issues, and ensures clean builds through iteration

### Commands

Commands in this bundle:

- **/cui-build-and-verify** - Execute comprehensive project verification by running Maven build and optionally committing changes

### Skills

Skills in this bundle:

- **cui-maven-rules** - Complete Maven standards covering build processes, POM maintenance, dependency management, and Maven integration

## Installation

This bundle is part of the CUI marketplace and can be installed via:

```bash
# Clone the repository (if not already done)
git clone https://github.com/cuioss/cui-llm-rules.git

# Navigate to marketplace bundles
cd cui-llm-rules/claude/marketplace/bundles

# The bundle is at: cui-maven/
```

## Usage

### For Users

**Commands**: Invoke commands directly in Claude Code:

```bash
# Run full build verification
/cui-build-and-verify

# Run build verification and commit/push changes
/cui-build-and-verify push
```

**Agents**:

The `maven-project-builder` agent is automatically activated when:
- User requests a full project build
- User wants to verify project after code changes
- User asks to run quality checks

Example user requests that trigger the agent:
- "I've finished implementing X, can you build the project?"
- "Run the full build with quality checks"
- "Make sure everything compiles after my changes"

The `maven-builder` agent is used for:
- Configurable Maven build execution (called by other agents)
- Direct build execution when specific commands or output modes are needed
- Integration into custom workflows requiring build execution

Example direct usage from other agents:
```
Task:
  subagent_type: maven-builder
  prompt: |
    command: "./mvnw clean test"
    outputMode: "ERRORS"
```

**Skills**: The `cui-maven-rules` skill is automatically loaded by agents that need Maven standards.

### For Developers

To add components to this bundle:

**Create an agent**:
```
/cui-create-agent scope=marketplace
# Select "cui-maven" as the bundle
```

**Create a command**:
```
/cui-create-command scope=marketplace
# Select "cui-maven" as the bundle
```

**Create a skill**:
```
/cui-create-skill scope=marketplace
# Select "cui-maven" as the bundle
```

## Architecture

### Bundle Structure

```
cui-maven/
├── .claude-plugin/
│   └── plugin.json          # Bundle manifest
├── agents/
│   ├── maven-builder.md             # Build execution agent
│   └── maven-project-builder.md     # Verification & fixing agent
├── commands/
│   └── cui-build-and-verify.md    # Build verification command
├── skills/
│   └── cui-maven-rules/     # Maven standards skill
│       ├── SKILL.md         # Skill definition
│       ├── standards/       # Standards files
│       │   ├── pom-maintenance.md
│       │   └── maven-integration.md
│       └── README.md        # Skill documentation
└── README.md                # This file
```

### Design Principles

- **Agent Delegation**: maven-project-builder delegates to maven-builder for build execution (single responsibility)
- **Automated Quality Checks**: Enforce quality gates through build verification
- **Iterative Fix Workflow**: Automatically fix issues and re-run builds until clean
- **Execution Time Tracking**: Monitor and update build duration expectations (handled by maven-builder)
- **Comprehensive Standards**: Cover all aspects of Maven usage in CUI projects
- **Integration with OpenRewrite**: Leverage automated POM cleanup recipes
- **JavaDoc Enforcement**: Mandatory JavaDoc warning fixes using CUI standards

### Key Features

#### Build Verification
- Execute Maven builds with pre-commit profile
- Analyze all output for errors, warnings, and issues
- Fix compilation errors, test failures, code warnings automatically
- Handle OpenRewrite TODO markers with auto-suppression
- Mandatory JavaDoc warning fixes
- Track execution duration with 10% change threshold

#### POM Maintenance
- BOM (Bill of Materials) management standards
- Dependency version management with properties
- Scope optimization guidance
- Maven wrapper updates
- OpenRewrite integration for automated cleanup

#### Quality Gates
- Build success verification
- Dependency analysis
- Test execution and coverage
- Format checking integration
- Linting compliance

## Dependencies

Currently no dependencies on other bundles.

## Configuration

### Project Configuration

Maven projects can configure build behavior in `.claude/run-configuration.md`:

```markdown
# Command Configuration

## ./mvnw -Ppre-commit clean install

### Last Execution Duration
- **Duration**: 120000ms (2 minutes)
- **Last Updated**: 2025-10-29

### Acceptable Warnings
- `[WARNING] Using platform encoding (UTF-8 actually) to copy filtered resources`
- `[WARNING] Parameter 'session' is deprecated`
```

### Build Profiles

Projects should define a `pre-commit` profile in their POM:

```xml
<profile>
  <id>pre-commit</id>
  <build>
    <!-- Quality checks, tests, coverage, etc. -->
  </build>
</profile>
```

## Development

### Adding New Components

1. Use creation wizards:
   - `/cui-create-agent` for agents
   - `/cui-create-command` for commands
   - `/cui-create-skill` for skills

2. Update this README.md with component descriptions

3. Test components:
   - `/cui-diagnose-agents` for agents
   - `/cui-diagnose-commands` for commands
   - `/cui-diagnose-skills` for skills

4. Validate entire bundle:
   - `/cui-diagnose-bundle cui-maven`

### Quality Standards

All components must meet:
- ✅ Proper YAML frontmatter
- ✅ Clear documentation
- ✅ Appropriate tool access
- ✅ Integration with other components
- ✅ Zero critical issues in diagnosis

### Testing

Test the bundle:

```bash
# Test individual components
/cui-diagnose-agents scope=marketplace
/cui-diagnose-commands scope=marketplace
/cui-diagnose-skills scope=marketplace

# Test entire bundle integration
/cui-diagnose-bundle cui-maven
```

## Workflow Examples

### Basic Build Verification

```bash
# User: "Can you run the full build?"
# System invokes: maven-project-builder agent
# maven-project-builder:
#   1. Activates cui-maven-rules skill
#   2. Delegates to maven-builder agent with outputMode="DEFAULT"
#   3. maven-builder:
#      - Reads .claude/run-configuration.md
#      - Executes ./mvnw -Ppre-commit clean install
#      - Captures output to timestamped file
#      - Extracts errors/warnings with line numbers
#      - Tracks execution duration (updates if >10% change)
#      - Returns: status, output file, errors/warnings
#   4. Analyzes errors/warnings from maven-builder
#   5. Fixes all issues (compilation, tests, JavaDoc, code warnings)
#   6. Handles OpenRewrite markers
#   7. Re-runs build (maven-builder) until clean
#   8. Reports results
```

### Build with Automatic Commit

```bash
# User: "/cui-build-and-verify push"
# System:
#   1. Delegates to maven-project-builder agent (full build)
#   2. Delegates to commit-changes agent (commit and push)
#   3. Reports consolidated results
```

### OpenRewrite Marker Handling

```bash
# During build, agent:
#   1. Searches for /*~~(TODO: markers in source code
#   2. Auto-suppresses LogRecord and Exception warnings
#   3. Asks user for other marker types
#   4. Removes markers from source
#   5. Re-runs build to verify
#   6. Reports if markers persist after 3 iterations
```

## Contributing

To contribute to this bundle:

1. Create components using creation wizards
2. Follow CUI coding standards
3. Add comprehensive documentation
4. Test thoroughly
5. Run quality checks
6. Submit for review

## Troubleshooting

### Common Issues

**Build timeouts**:
- Check `.claude/run-configuration.md` for current duration
- Agent uses 25% safety margin (duration * 1.25)
- Update duration if builds consistently take longer

**JavaDoc warnings persist**:
- Agent MUST fix all JavaDoc warnings (not optional)
- Uses cui-javadoc skill standards for fixes
- Never add JavaDoc warnings to acceptable list

**OpenRewrite markers multiply**:
- Agent searches with Grep after EVERY build
- Auto-suppresses LogRecord/Exception markers
- Reports if markers persist after 3 fix iterations

**Components not discovered**:
- Check YAML frontmatter is valid
- Verify file naming conventions
- Ensure bundle is in correct location

**Tool access issues**:
- Review tool permissions in component frontmatter
- Check for missing approvals
- Use appropriate tool restrictions

## Standards Covered

### Maven Build Standards
- Pre-commit profile configuration
- Build success criteria
- Quality gate enforcement
- Execution time tracking

### POM Maintenance Standards
- BOM (Bill of Materials) management
- Dependency management with properties
- Version naming conventions
- Scope optimization
- OpenRewrite integration
- Maven wrapper updates

### Maven Integration Standards
- Frontend-maven-plugin configuration
- JavaScript tooling integration
- SonarQube integration
- Coverage reporting
- CI/CD integration

### Quality Standards
- Compilation error handling
- Test failure resolution
- Code warning fixes
- JavaDoc mandatory fixes
- OpenRewrite marker handling
- Acceptable warning management

## Version History

### Version 0.2.0 (Current)

- **NEW**: Created maven-builder agent - central build execution agent
  - Configurable build commands
  - Multiple output modes (FILE, DEFAULT, ERRORS, NO_OPEN_REWRITE)
  - Module and reactor build support
  - Automatic duration tracking
  - Output capture to timestamped files
  - Non-prompting execution with simple redirection
- **UPDATED**: maven-project-builder now delegates to maven-builder
  - Removed direct Maven execution
  - Focuses on analysis and fixing
  - Cleaner separation of concerns
- **UPDATED**: task-executor documentation to prefer maven-builder/maven-project-builder
- **UPDATED**: Bundle README with delegation architecture

### Version 0.1.0 (Initial Release)

- Initial bundle structure created
- Created maven-project-builder agent consolidating Maven build functionality
- Moved cui-build-and-verify command from cui-utility-commands
- Created cui-maven-rules skill with complete Maven standards
- Ready for comprehensive Maven workflow support

## License

MIT

## Support

For issues, questions, or contributions:
- Repository: https://github.com/cuioss/cui-llm-rules
- Bundle: claude/marketplace/bundles/cui-maven/

## Related Bundles

- **cui-utility-commands**: General utility commands and research capabilities
- **cui-java-expert**: Java development standards bundle (maven-project-builder uses cui-javadoc skill for JavaDoc validation)

## Acknowledgments

This bundle consolidates Maven-related functionality previously distributed across:
- cui-utility-commands (cui-build-and-verify command)
- standards/process (pom-maintenance.adoc)
- standards/javascript (maven-integration-standards.adoc)

---

*Generated by /cui-create-bundle - CUI Plugin Development Tools*
