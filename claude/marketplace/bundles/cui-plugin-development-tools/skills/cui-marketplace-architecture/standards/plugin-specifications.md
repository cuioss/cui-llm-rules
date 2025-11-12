# Plugin Specifications

## Overview

Technical specifications for CUI marketplace bundles: manifests, directory structure, component formats.

## Directory Structure

### Marketplace Layout

```
claude/marketplace/
├── .claude-plugin/
│   └── marketplace.json           # Marketplace manifest
├── bundles/                        # Workflow bundles
│   ├── cui-utility-commands/
│   │   ├── .claude-plugin/
│   │   │   └── plugin.json       # Bundle manifest
│   │   ├── README.md
│   │   ├── agents/               # .md files
│   │   ├── commands/             # .md files
│   │   └── skills/               # directories
│   └── cui-workflow/
└── skills/                         # Standalone skills
    └── cui-java-core/
        ├── SKILL.md
        └── standards/
```

### Component Formats

* **Commands**: Single `.md` files (NOT directories)
* **Agents**: Single `.md` files (NOT directories)
* **Skills**: Directories containing `SKILL.md`

## Manifests

### marketplace.json

**Location**: `claude/marketplace/.claude-plugin/marketplace.json`

```json
{
  "name": "cui-development-standards",
  "owner": {"name": "CUI OSS Project"},
  "metadata": {
    "description": "CUI development standards marketplace",
    "version": "1.0.0"
  },
  "plugins": [
    {
      "name": "cui-java-skills",
      "description": "Java development standards",
      "source": "./",
      "skills": [
        "./skills/cui-java-core",
        "./skills/cui-java-unit-testing"
      ]
    },
    {
      "name": "cui-utility-commands",
      "description": "Standalone utility commands including git commit management",
      "source": "./bundles/cui-utility-commands"
    }
  ]
}
```

**Plugin config**:

* `name`: Kebab-case identifier (prefix `cui-`)
* `description`: One-sentence purpose
* `source`: Relative path to bundle root
* `skills`: Array of skill paths (for skill-only plugins)

### plugin.json (Bundle)

**Location**: `bundles/{bundle-name}/.claude-plugin/plugin.json`

```json
{
  "name": "cui-workflow",
  "version": "1.0.0",
  "description": "Complete development workflow from issue implementation to PR review",
  "author": {"name": "CUI Team"},
  "agents": [
    "./agents/commit-changes.md",
    "./agents/task-reviewer.md",
    "./agents/task-executor.md",
    "./agents/pr-review-responder.md",
    "./agents/pr-quality-fixer.md"
  ],
  "commands": [
    "./commands/cui-orchestrate-task-workflow.md",
    "./commands/cui-handle-pull-request.md"
  ],
  "skills": []
}
```

**Component fields**:

* `agents.files`: Agent filenames (without `.md`)
* `commands.files`: Command filenames (without `.md`)
* `skills.folders`: Skill directory names

## Components

### Skills

**Structure**:
```
skills/skill-name/
├── SKILL.md          # Required: Workflow with YAML frontmatter
├── README.md         # Recommended: Human documentation
└── standards/        # Optional: Standards files
```

**SKILL.md frontmatter**:
```yaml
---
name: skill-name
description: When and why to use this skill
allowed-tools: [Read, Grep, Glob]
---
```

**Self-containment**: All file references must be internal (`standards/file.md`), no external paths (`../../../../`).

### Agents

**Format**: Single `.md` file with YAML frontmatter

```yaml
---
name: agent-name
description: When to use with examples
tools: Read, Edit, Write, Bash, Skill
model: sonnet
color: green
---
```

**Structure**: See [Agent Design Principles](agent-design-principles.md)

### Commands

**Format**: Single `.md` file with YAML frontmatter

```yaml
---
name: command-name
description: What this command does
---
```

**Invocation**: User types `/command-name`

## Installation

**Add marketplace**:
```bash
/plugin marketplace add cuioss/cui-llm-rules
```

**Install plugin**:
```bash
/plugin install cui-java-skills@cui-llm-rules
```

**Update marketplace**:
```bash
/plugin marketplace update cui-llm-rules
```

## Validation

**Verify bundle**:
```bash
/cui-diagnose-bundle {bundle-name}
```

**Verify agents**:
```bash
/cui-diagnose-agents
```

**Verify skills**:
```bash
/cui-diagnose-skills
```

## Common Issues

### Missing YAML Frontmatter

**Error**: Component not recognized

**Fix**: Add frontmatter with `name` and `description`

```yaml
---
name: component-name
description: Component purpose
---
```

### Wrong File Extension

**Error**: Commands/agents must be `.md` files

**Fix**: Rename `.txt` or extensionless files to `.md`

### Directory vs File

**Error**: Commands and agents are files, not directories

**Fix**:
* ❌ `commands/my-command/command.md`
* ✅ `commands/my-command.md`

### Absolute Paths

**Error**: Skills with external file references

**Fix**: Move external content into skill's `standards/` directory

* ❌ `Read: ../../../../standards/file.adoc`
* ✅ `Read: standards/file.md`

## Cross-References

* [Plugin Architecture](architecture-overview.md)
* [Bundling Architecture](bundling-patterns.md)
* [Agent Design Principles](agent-design-principles.md)
* https://docs.claude.com/en/docs/claude-code/plugins
