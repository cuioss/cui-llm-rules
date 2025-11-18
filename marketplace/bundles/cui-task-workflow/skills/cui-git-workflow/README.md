# CUI Git Workflow Skill

Git commit standards following conventional commits specification for CUI LLM projects.

## Overview

This skill provides comprehensive standards for formatting git commit messages following the conventional commits specification. It ensures consistent, professional commit messages across all CUI projects.

## What's Included

### Standards Files

* **git-commit-standards.md** - Complete git commit format specification
  * Commit message structure (type, scope, subject, body, footer)
  * Commit types and their usage (feat, fix, docs, etc.)
  * Subject line guidelines (imperative mood, length limits)
  * Body and footer formatting rules
  * Practical examples for common scenarios
  * Best practices and anti-patterns
  * Verification checklist

## Key Features

### Conventional Commits Format

```text
<type>(<scope>): <subject>

<body>

<footer>
```

### Supported Commit Types

* **feat** - New features
* **fix** - Bug fixes
* **docs** - Documentation changes
* **style** - Formatting changes
* **refactor** - Code refactoring
* **perf** - Performance improvements
* **test** - Test additions/corrections
* **chore** - Build/tooling changes

### Guidelines Provided

* **Subject lines** - Imperative mood, max 50 chars, no period
* **Body format** - Wrap at 72 characters, explain "why" not "what"
* **Footers** - Breaking changes, issue references
* **Best practices** - Atomic commits, meaningful messages

## Usage

### In Agents

```markdown
### Step 1: Load Git Standards

```
Skill: cui-task-workflow:cui-git-workflow
```

### Step 2: Format Commits

Use loaded standards to generate conventional commit messages.
```

### In Commands

Commands that create commits should delegate to agents that load this skill.

## Integration

This skill integrates with:

* **commit-changes agent** - Should load this skill for commit formatting
* **task-executor agent** - Can use for commit message generation
* **PR workflow commands** - Any command creating commits

## Examples

For complete commit message examples including feature commits, bug fixes, breaking changes, and anti-patterns, see [git-commit-standards.md](standards/git-commit-standards.md).

## References

* Conventional Commits: https://www.conventionalcommits.org/
* Git Commit Best Practices: https://cbea.ms/git-commit/
* Angular Guidelines: https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit

## Bundle

Part of the **cui-task-workflow** bundle - Complete development workflow from issue to PR.
