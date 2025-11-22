# CUI Plugin Development Tools

## Purpose

Complete toolchain for creating, diagnosing, fixing, and maintaining Claude Code marketplace components. This bundle provides goal-based commands and skills for plugin developers to manage the full lifecycle of marketplace components (commands, skills, bundles).

## Architecture

This bundle follows the **goal-based organization** pattern where components are organized by user goals rather than technical types:

- **CREATE** - Create new components
- **DIAGNOSE** - Find and understand issues
- **FIX** - Apply fixes to issues
- **MAINTAIN** - Keep marketplace healthy
- **VERIFY** - Validate complete marketplace

## Components

### Commands (5 goal-based thin orchestrators)

| Command | Description |
|---------|-------------|
| `/plugin-create` | Create new marketplace component (agent, command, skill, or bundle) |
| `/plugin-diagnose` | Find and understand quality issues in marketplace components |
| `/plugin-fix` | Apply fixes to issues identified by /plugin-diagnose |
| `/plugin-maintain` | Maintain marketplace health (update, add-knowledge, readme, refactor) |
| `/plugin-verify` | Run comprehensive marketplace verification |

### Skills (6)

| Skill | Description |
|-------|-------------|
| `plugin-architecture` | Architecture principles, skill patterns, and design guidance |
| `plugin-create` | Workflows for creating new marketplace components |
| `plugin-diagnose` | Diagnostic workflows for quality analysis |
| `plugin-fix` | Fix workflows with categorization and verification |
| `plugin-maintain` | Maintenance workflows (update, readme, refactor) |
| `marketplace-inventory` | Scan and report complete marketplace inventory |

### Agents

None - All agent functionality has been consolidated into skills following the goal-based architecture pattern.

## Installation

```
/plugin install cui-plugin-development-tools
```

## Usage Examples

### Create a New Component

```
/plugin-create agent
/plugin-create command
/plugin-create skill
/plugin-create bundle
```

The workflow guides you through:
- Interactive questionnaire for component details
- Duplication detection against existing components
- Generation with proper structure and frontmatter
- Validation against architecture rules
- Summary with next steps

### Diagnose Issues

```
# Diagnose specific component
/plugin-diagnose agent=my-agent
/plugin-diagnose command=my-command
/plugin-diagnose skill=my-skill

# Diagnose all components of a type
/plugin-diagnose agents
/plugin-diagnose commands
/plugin-diagnose skills

# Diagnose entire marketplace
/plugin-diagnose marketplace
```

### Fix Issues

```
# After running /plugin-diagnose
/plugin-fix

# Applies safe fixes automatically
# Prompts for risky fixes requiring confirmation
```

### Maintain Components

```
# Update components
/plugin-maintain update agent=my-agent
/plugin-maintain update command=my-command

# Add knowledge to skill
/plugin-maintain add-knowledge skill=my-skill source=url

# Update READMEs
/plugin-maintain readme
/plugin-maintain readme bundle=my-bundle

# Refactor structure
/plugin-maintain refactor
```

### Verify Marketplace

```
/plugin-verify

# Runs comprehensive health check across all components
# Reports issues by severity
# Offers fix option
```

## Dependencies

- **Inter-Bundle Dependencies**: None - self-contained
- **External Dependencies**: None - works with filesystem access only

## Standards Enforced

The diagnostic and creation workflows validate:

- **Architecture Rules**: Self-containment, {baseDir} pattern, progressive disclosure
- **Goal-Based Organization**: Commands organized by user goals
- **Thin Orchestrator Pattern**: Commands <100 lines, delegate to skills
- **Skill Patterns**: Proper workflow structure, script automation, references
- **Quality Standards**: Frontmatter format, documentation completeness, cross-references
