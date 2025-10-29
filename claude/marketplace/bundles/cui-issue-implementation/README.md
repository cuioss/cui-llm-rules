# CUI Issue Implementation

## Purpose

Complete issue implementation workflow from review to execution. This bundle provides a structured end-to-end process for transforming GitHub issues and requirements into fully implemented, tested, and verified code changes.

## Components Included

This bundle includes the following components:

### Agents
- **task-reviewer** - Reviews task plans and provides feedback on clarity and completeness
- **task-breakdown-agent** - Breaks down complex issues into structured, actionable task plans
- **task-executor** - Executes task plan steps sequentially with build verification

### Commands
- **implement-task** - Orchestrates the complete issue implementation workflow

## Installation Instructions

To install this plugin bundle, run:

```
/plugin install cui-issue-implementation
```

This will make all agents and commands available in your Claude Code environment.

## Usage Examples

### Example 1: Implement GitHub Issue End-to-End

Use the implement-task command for complete workflow orchestration:

```
/implement-task

Implement GitHub issue #42: Add OAuth2 token refresh capability
```

The command will:
1. Analyze the issue requirements
2. Create a structured task plan
3. Execute each task sequentially
4. Verify builds after each change
5. Commit changes with proper messages
6. Report completion status

### Example 2: Break Down Complex Issue

Use task-breakdown-agent for planning before execution:

```
/agent task-breakdown-agent

Break down the OAuth2 implementation issue into a detailed task plan.
```

The agent will:
- Analyze requirements and specifications
- Research relevant best practices
- Create numbered tasks with acceptance criteria
- Define clear implementation steps
- Identify dependencies and risks

### Example 3: Execute Existing Task Plan

Use task-executor for implementing from an existing plan:

```
/agent task-executor

Execute Task 3 from the plan at /path/to/oauth-plan.md
```

The agent will:
- Read and parse the task plan
- Execute checklist items sequentially
- Mark items as done after completion
- Run build verification when required
- Verify acceptance criteria
- Return detailed completion report

### Example 4: Review Task Plan Quality

Use task-reviewer before starting implementation:

```
/agent task-reviewer

Review the task plan at /path/to/feature-plan.md for quality and completeness.
```

The agent will:
- Check for clear acceptance criteria
- Verify implementation steps are specific
- Identify missing technical details
- Suggest improvements
- Validate plan structure

## Dependencies

### Inter-Bundle Dependencies
- **cui-maven** (recommended) - Task executor invokes maven-project-builder for build verification
- **cui-project-quality-gates** (recommended) - Task executor invokes commit-changes for commits

### Standalone Agent Dependencies
- **research-best-practices** (general-purpose agent) - Task-reviewer and task-breakdown-agent may invoke this for researching industry best practices

### External Dependencies
- Requires GitHub CLI (`gh`) for issue operations when working with GitHub issues
- Requires git repository for commit operations
- Task executor requires Maven wrapper (`./mvnw`) for build verification

### Internal Component Dependencies
- **task-reviewer** may invoke **research-best-practices** for validation
- **task-breakdown-agent** invokes **research-best-practices** for industry standards
- **implement-task** command orchestrates: task-breakdown-agent → task-executor workflow
