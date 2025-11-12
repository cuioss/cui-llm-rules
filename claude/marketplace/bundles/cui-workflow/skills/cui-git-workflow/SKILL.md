---
name: cui-git-workflow
description: Git commit standards following conventional commits for CUI projects
allowed-tools: []
standards:
  - standards/git-commit-standards.md
---

# CUI Git Workflow Skill

Provides standardized git commit format following conventional commits specification for all CUI LLM projects.

## What This Skill Provides

This skill provides comprehensive git commit standards including:

* **Commit message format** - Type, scope, subject, body, footer structure
* **Commit types** - feat, fix, docs, style, refactor, perf, test, chore
* **Examples** - Basic commits, task-based commits, breaking changes
* **Key practices** - Atomic commits, meaningful messages, issue references
* **Guidelines** - Subject lines, body format, footer conventions
* **Anti-patterns** - Common mistakes to avoid

## When to Activate This Skill

Use this skill when:

* Creating git commits programmatically
* Validating commit message format
* Generating commit messages from changes
* Providing commit message guidance to users
* Implementing commit-related agents or commands

## Workflow

### Step 1: Load Git Commit Standards

```
Read: standards/git-commit-standards.md
```

This provides:
* Conventional commits format specification
* Commit type definitions and usage
* Subject, body, and footer guidelines
* Practical examples for different scenarios
* Best practices and anti-patterns
* Verification checklist

### Step 2: Apply Standards

Use the loaded standards to:

1. **Format commit messages** following `<type>(<scope>): <subject>` pattern
2. **Select appropriate type** from: feat, fix, docs, style, refactor, perf, test, chore
3. **Write clear subjects** in imperative mood, lowercase, max 50 chars
4. **Include body** when explaining complex changes or context
5. **Add footers** for breaking changes and issue references

### Step 3: Validate Compliance

Check commit messages against:

* Type from approved list
* Subject format (imperative, lowercase, no period)
* Subject length (≤50 chars ideal, 72 absolute max)
* Body wrapping (72 characters)
* Footer format (BREAKING CHANGE, issue refs)
* Atomic commit principle

## Standards Organization

```
standards/
  git-commit-standards.md       # Complete commit message standards
```

Single comprehensive standards file covering all aspects of git commit formatting and best practices.

## Tool Access

**No special tools required** - This skill uses standard Read tool to load markdown standards.

## Usage Examples

### Example 1: commit-changes Agent

The `commit-changes` agent should load this skill to format commits:

```markdown
### Step 1: Load Git Standards

```
Skill: cui-git-workflow
```

This loads conventional commits format and guidelines.

### Step 2: Format Commit Message

Apply standards to generate commit message with:
- Appropriate type (feat/fix/docs/etc)
- Clear, imperative subject
- Optional body with context
- Issue references in footer
```

### Example 2: Commit Message Validator

```markdown
### Step 1: Load Standards

```
Skill: cui-git-workflow
```

### Step 2: Validate Commit

Check commit message against:
- Type validation
- Subject format
- Length limits
- Footer format
```

## Integration with Workflow Bundle

This skill integrates with cui-workflow bundle components:

* **commit-changes agent** - Should load this skill to format commits properly
* **task-executor agent** - Can reference for commit message generation
* **cui-orchestrate-task-workflow command** - Uses commit-changes which should follow these standards

## Quality Verification

Standards in this skill ensure:

- [x] Self-contained (no external references)
- [x] All content in standards/ directory
- [x] Only external URLs for references
- [x] Markdown format for compatibility
- [x] Comprehensive coverage of git commits
- [x] Practical examples included

## References

* Conventional Commits: https://www.conventionalcommits.org/
* Git Commit Best Practices: https://cbea.ms/git-commit/
* Angular Commit Guidelines: https://github.com/angular/angular/blob/main/CONTRIBUTING.md#commit
