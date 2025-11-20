# Bundling Architecture

## Overview

Bundles organize related agents, commands, and skills into cohesive functional units installed as single packages.

**Purpose**: Group components that serve common workflows or domains.

**Distribution**: Via plugin marketplace at `marketplace/bundles/`

## Bundle Patterns

The marketplace implements 4 bundle types:

### 1. Maven Build Tools

**Bundle**: `cui-maven`

**Purpose**: Maven build verification and project management

**Components**: maven-project-builder agent, maven-builder agent, /cui-build-and-verify command, cui-maven-rules skill

**Rationale**: Specialized Maven build tooling with dedicated standards

### 2. Development Workflow

**Bundle**: `cui-task-workflow`

**Purpose**: Complete development workflow from issue implementation to PR review and quality verification

**Components**:
- Issue implementation: task-reviewer, task-breakdown-agent, task-executor agents; /orchestrate-workflow command
- PR workflow: pr-review-responder, pr-quality-fixer agents; /pr-handle-pull-request command

**Rationale**: Unified end-to-end development cycle workflow with high cohesion (issue → implementation → PR → review → quality)

### 3. Documentation Standards

**Bundle**: `cui-documentation-standards`

**Purpose**: AsciiDoc documentation enforcement

**Components**: asciidoc-reviewer agent, cui-documentation skill, /doc-review-technical-docs command

**Rationale**: Domain-specific bundle where agent loads skill for standards

### 4. Plugin Development Tools

**Bundle**: `cui-plugin-development-tools`

**Purpose**: Plugin development toolchain

**Components**: /plugin-create-agent, /plugin-create-command, /cui-diagnose-* commands

**Rationale**: Complete development lifecycle tooling

## Design Principles

**See**: `cui-marketplace-architecture` skill for complete bundle architecture rules

**Key principles**:

* **Component Count**: 2-8 per bundle (avg: 3.8)
* **Functional Cohesion**: Group by workflow/domain, not component type
* **Common Closure**: Components that change together belong together
* **Co-occurrence**: Bundle if used together >70% of time

**Examples**:

* ✅ "PR Workflow" bundle (agents + commands for PR handling)
* ✅ "Documentation Standards" (agent + skill + command for docs)
* ❌ "All Agents Bundle" (no functional cohesion)

## Structure

### Directory Layout

```
bundles/{bundle-name}/
├── .claude-plugin/
│   └── plugin.json           # Required manifest
├── README.md                  # Required documentation
├── agents/                    # .md files (optional)
├── commands/                  # .md files (optional)
└── skills/                    # directories (optional)
```

**File requirements**:

* Commands: Single `.md` files (NOT directories)
* Agents: Single `.md` files (NOT directories)
* Skills: Directories containing `SKILL.md`

### Manifest Format

**Location**: `.claude-plugin/plugin.json`

```json
{
  "name": "cui-task-workflow",
  "version": "1.0.0",
  "description": "Complete development workflow from issue implementation to PR review",
  "author": {"name": "CUI OSS Project"},
  "agents": [
    "./agents/commit-changes.md",
    "./agents/task-reviewer.md",
    "./agents/task-executor.md"
  ],
  "commands": [
    "./commands/orchestrate-workflow.md",
    "./commands/pr-handle-pull-request.md"
  ],
  "skills": []
}
```

**Required**: name, version, description

**Component paths**:

* Agents/commands: Include `.md` extension
* Skills: Directory path (no extension)
* All paths start with `./`

### README Format

**Required sections**:

1. Purpose (1-2 sentences)
2. Components Included (list with descriptions)
3. Installation (`/plugin install {bundle-name}`)
4. Usage Examples (2+ scenarios)
5. Dependencies (if any)

## Installation

**Add marketplace**:
```bash
/plugin marketplace add cuioss/cui-llm-rules
```

**Install bundle**:
```bash
/plugin install cui-utilities@cui-llm-rules
```

**Update**:
```bash
/plugin marketplace update cui-llm-rules
```

## Creating Bundles

**Decision process**:

1. **Functional cohesion**: Single task/domain?
   * NO → Keep separate
   * YES → Continue

2. **Co-occurrence**: Used together >70%?
   * NO → Keep separate
   * YES → Continue

3. **Common closure**: Change together?
   * NO → Keep separate
   * YES → Continue

4. **Component count**: 2-8 components?
   * NO → Split or keep separate
   * YES → Bundle

**Registration**: Add entry to `marketplace.json`:

```json
{
  "name": "cui-bundle-name",
  "description": "Bundle purpose",
  "source": "./bundles/bundle-name"
}
```

## Common Issues

### Command/Agent Directory Structure

**Error**: Creating directories instead of single files

**Wrong**:
```
commands/
└── cui-build/          ❌ Directory
    └── COMMAND.md     ❌ Exposed as ":COMMAND"
```

**Correct**:
```
commands/
└── cui-build.md        ✅ Single file
```

**Consequence**: Directory structure creates duplicate listings with `:COMMAND` and `:README` suffixes

### Missing .md Extension

**Error**: Manifest paths without `.md`

**Wrong**: `"./agents/maven-builder"`

**Correct**: `"./agents/maven-builder.md"`

### Absolute Paths

**Error**: Using absolute or user-specific paths

**Wrong**: `~/git/cui-llm-rules/...`

**Correct**: `./agents/...` (relative from bundle root)

## Cross-References

* [Plugin Architecture](architecture-overview.md)
* [Plugin Specifications](plugin-specifications.md)
* [Agent Design Principles](agent-design-principles.md)
* `cui-marketplace-architecture` skill - Complete bundle rules
