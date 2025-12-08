# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Repository Overview

This is a **Claude Code Marketplace** repository providing development standards, automation tools, and AI-assisted workflows for CUI (Common User Interface) Open Source projects. It contains 8 production bundles with 95 components (skills, agents, and commands) that integrate with Claude Code's plugin system.

## Architecture

### Directory Structure

```
cui-llm-rules/
├── marketplace/                    # Claude Code marketplace system
│   ├── .claude-plugin/
│   │   └── marketplace.json        # Master marketplace configuration
│   └── bundles/                    # 8 production bundles
│       ├── cui-java-expert/        # Java development standards + agents
│       ├── cui-frontend-expert/    # JavaScript/CSS standards + agents
│       ├── builder/                # Maven/Gradle/npm build automation
│       ├── planning/               # Task planning & workflow management
│       ├── cui-documentation-standards/  # AsciiDoc, ADRs, interfaces
│       ├── general-tools/          # Utility commands & file operations
│       ├── cui-plugin-development-tools/ # Plugin creation toolkit
│       └── cui-requirements/       # Requirements engineering
├── test/                           # Python pytest tests for scripts
├── target/                         # Generated files and logs (gitignored)
└── .claude/                        # Project-level Claude Code configuration
```

### Component Model

The marketplace uses a three-tier component hierarchy:

| Component | Count | Purpose |
|-----------|-------|---------|
| **Skills** | 28 | Domain knowledge, standards, and reference documentation |
| **Agents** | 28 | Autonomous task executors with focused responsibilities |
| **Commands** | 39 | User-invokable slash commands that orchestrate workflows |

### Bundle Structure

Each bundle follows a consistent structure:

```
bundle-name/
├── .claude-plugin/
│   └── plugin.json         # Bundle manifest (name, version, components)
├── agents/                 # Specialized task agents (*.md)
├── commands/               # Slash commands (*.md)
├── skills/                 # Development standards
│   └── skill-name/
│       ├── SKILL.md        # Skill definition and workflows
│       ├── standards/      # Detailed standard documents (*.md)
│       ├── scripts/        # Implementation scripts (Python/Bash)
│       └── templates/      # Document/code templates
└── README.md               # Bundle documentation
```

## The 8 Production Bundles

### cui-java-expert
Java development standards covering core patterns, null safety, Lombok, CDI/Quarkus, unit testing with JUnit 5, JavaDoc, and logging. Includes agents for implementation, testing, refactoring, and build fixing.

### cui-frontend-expert
JavaScript and frontend standards for ES modules, modern patterns, CSS, JSDoc, project structure, Maven integration, ESLint/Prettier/StyleLint configuration, Cypress E2E testing, and Jest unit testing.

### builder
Unified build automation supporting Maven, Gradle, and npm. Features environment detection, build output parsing, error routing, and auto-fixing workflows.

### planning
Complete development workflow automation with 14 skills covering task planning, implementation phases, plan refinement, finalization, git workflows, PR management, work logging, and Sonar integration.

### cui-documentation-standards
Documentation standards for AsciiDoc, Architectural Decision Records (ADRs), and interface specifications. Includes validation, formatting, and maintenance workflows.

### general-tools
Utility commands for script execution, permission management, file operations, memory management, lessons learned tracking, and project configuration.

### cui-plugin-development-tools
Plugin development toolkit with creation wizards, quality diagnosis, marketplace inventory scanning, architecture guidance, and component maintenance workflows.

### cui-requirements
Requirements engineering standards covering authoring, planning, traceability, and project initialization.

## Key Design Patterns

### Skills-First Development
Standards are loaded before any code work begins. Skills provide the domain knowledge that guides implementation.

### Agent Delegation
Commands orchestrate agents for autonomous subtask execution. Agents have focused responsibilities and return structured JSON results.

### Build System Abstraction
Single interface for Maven/Gradle/npm with automatic environment detection. Consistent output parsing and error routing across all build systems.

### Structured Contracts
All agents return JSON with status, data, and metrics. Explicit error paths and partial success states enable iteration.

### Script Execution Convention

All marketplace scripts are executed via the executor:

```bash
python3 .plan/execute-script.py {notation} {subcommand} {args...}
```

**Notation format**: `{bundle}:{skill}` (e.g., `planning:manage-files`)

**Examples**:
- `python3 .plan/execute-script.py planning:manage-files add --plan-id my-plan --file task.md`
- `python3 .plan/execute-script.py builder:builder-maven-rules execute --goals verify`
- `python3 .plan/execute-script.py planning:manage-config set --plan-id my-plan --key foo --value bar`

**Executor features**:
- Embedded script mappings (no runtime file I/O)
- Notation-to-path resolution
- Two-tier execution logging (plan-scoped or global)
- Error standardization

**Setup**: Run `/plan-marshall` after bundle changes to regenerate the executor with updated mappings.

**Script Development**: See `cui-plugin-development-tools:plugin-script-architecture` skill for implementation standards.

## Working in This Repository

### File Formats

- **Skills/Commands/Agents**: Markdown with YAML frontmatter
- **Standards documents**: Markdown (some AsciiDoc templates available)
- **Scripts**: Python and Bash in `skills/*/scripts/` directories
- **Configuration**: JSON for plugin.json, marketplace.json, settings

### Naming Conventions

- Files and commands: `kebab-case` (e.g., `java-implement-code.md`)
- Bundles: Descriptive names with domain prefix (e.g., `cui-java-expert`)
- Skills: Domain-specific names (e.g., `cui-java-core`, `plan-refine`)

### Documentation Standards

- **No version history**: Never add changelogs, "RECENT CHANGES", or dated update sections
- **No timestamps**: Never add dates or version numbers to document content
- **No duplication**: Use cross-references instead of duplicating information
- **Current state only**: Document present requirements, not transitional information
- **AsciiDoc formatting**: Ensure blank line before lists, proper cross-references with `xref:` syntax

### Testing

See `cui-plugin-development-tools:plugin-script-architecture` skill for testing standards.

```bash
python3 test/run-tests.py                                          # all tests
python3 test/run-tests.py test/planning/                           # directory
python3 test/run-tests.py test/planning/plan-files/test_parse_plan.py  # single file
```

### Development Notes

- Use `target/` directory for generated files and temporary outputs
- Use proper tools (Edit, Read, Write) instead of shell commands (echo, cat)
- Use `gh` tool for GitHub access, not MCP

## Integration Points

- **Git**: `git` tool for issue/PR management
- **Build Systems**: none, md only
- **IDE**: IntelliJ MCP for diagnostics (file must be active in editor)
