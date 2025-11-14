# CUI Plugin Development Tools

## Purpose

Complete toolchain for creating and diagnosing Claude Code plugins. This bundle provides essential commands for plugin developers to create new components (agents, commands, skills) and diagnose issues with existing plugins, ensuring high-quality marketplace contributions.

## Components Included

This bundle includes the following components:

### Commands
- **create-agent** - Scaffolds new agent with proper structure and documentation (includes Rule 6 validation - prevents Task tool in agents)
- **create-command** - Scaffolds new command with standard format
- **diagnose-agents** - Validates agent structure, AGENT.md format, and integration (includes Checks 6-7 for Rule 6/7 violations)
- **diagnose-commands** - Validates command structure, markdown format, and metadata
- **diagnose-skills** - Validates skill structure, SKILL.md format, and documentation

### Agents (Rule 6 compliant)
- **diagnose-skill** - Analyzes single skill using Read, Grep, Glob (no Task tool - inlined validation logic)

## Installation Instructions

To install this plugin bundle, run:

```
/plugin install cui-plugin-development-tools
```

This will make all commands available in your Claude Code environment.

## Usage Examples

### Example 1: Create New Agent

Use create-agent to scaffold a new agent with proper structure:

```
/create-agent

Create a new agent named "http-client-tester" for testing HTTP client implementations.
```

The command will:
- Create agent directory structure
- Generate AGENT.md with standard sections
- Add required metadata (name, description, tags)
- Include usage instructions template
- Provide implementation guidance
- Create example prompt templates

### Example 2: Create New Command

Use create-command to scaffold a new command:

```
/create-command

Create a command "analyze-dependencies" for analyzing Maven dependency trees.
```

The command will:
- Create command markdown file
- Add standard frontmatter metadata
- Include description and usage sections
- Add parameter documentation template
- Provide example invocations
- Link to related agents

### Example 3: Diagnose Agent Issues

Use diagnose-agents to validate agent quality before publishing:

```
/diagnose-agents

Diagnose all agents in the marketplace/agents/ directory.
```

The command will:
- Scan all agent directories
- Validate AGENT.md structure
- Check required metadata presence
- Verify documentation completeness
- **Check 6: Task Tool Misuse Detection** - Validates agents don't use Task tool (Rule 6 violation)
- **Check 7: Maven Anti-Pattern Detection** - Validates only maven-builder uses Bash(./mvnw:*) (Rule 7)
- Identify missing sections
- Report formatting issues
- Suggest improvements

### Example 4: Validate Plugin Bundle

Before publishing a plugin bundle, validate all components:

```
/diagnose-agents
/diagnose-commands
/diagnose-skills

Validate all components in my new plugin bundle at /path/to/my-bundle/
```

This comprehensive check ensures:
- All components follow marketplace standards
- Documentation is complete and well-formatted
- Metadata is correctly specified
- Structure matches expected patterns
- No common issues exist

### Example 5: Fix Agent Documentation

After diagnosis identifies issues, fix and re-check:

```
# Fix identified issues in agent documentation
/diagnose-agents

Re-validate the http-client-tester agent after documentation fixes.
```

Iterative development cycle ensures quality.

## Dependencies

### Inter-Bundle Dependencies
- None - This bundle is self-contained and has no dependencies on other plugin bundles

### External Dependencies
- No build tools or external dependencies required
- Works with filesystem access for reading/writing component files

### Use Cases
This bundle is designed for:
- **Plugin developers** creating new marketplace components
- **Marketplace maintainers** verifying component quality
- **Teams** building custom internal agents/commands/skills
- **Quality assurance** ensuring components meet standards before publication

### Standards Enforced
The diagnostic commands validate:
- Directory structure conventions
- AGENT.md / SKILL.md / command.md format
- Required metadata fields (name, description, tags)
- Documentation section completeness
- Markdown formatting quality
- Cross-reference validity
- Example quality and clarity
