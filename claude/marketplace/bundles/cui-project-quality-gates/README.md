# CUI Project Quality Gates

## Purpose

Build verification and change management infrastructure for CUI projects. This bundle provides the essential tools to ensure code quality through automated Maven builds and streamlined git commit workflows.

## Components Included

This bundle includes the following components:

### Agents
- **maven-project-builder** - Executes Maven build lifecycle with pre-commit verification
- **commit-changes** - Manages git staging and commits with proper formatting

### Skills
- **cui-javadoc** - JavaDoc standards and validation (used by maven-project-builder)

## Installation Instructions

To install this plugin bundle, run:

```
/plugin install cui-project-quality-gates
```

This will make all agents and skills available in your Claude Code environment.

## Usage Examples

### Example 1: Verify Project Build

Use the maven-project-builder agent to run a full build verification:

```
/agent maven-project-builder

Verify the project builds correctly with all quality gates.
```

The agent will:
- Execute `./mvnw -Ppre-commit clean verify`
- Run all tests and quality checks
- Report build status and any issues
- Provide detailed error analysis if build fails

### Example 2: Commit Changes After Implementation

After implementing changes, use commit-changes agent to create a properly formatted commit:

```
/agent commit-changes

Commit the implementation changes for the HttpClient retry logic feature.
```

The agent will:
- Review staged and unstaged changes
- Analyze git diff and git status
- Create commit message following repository conventions
- Stage relevant files and create the commit
- Add standard co-authorship attribution

### Example 3: Combined Quality Gate Workflow

Typical workflow combining both agents:

1. Make code changes
2. Verify build: `/agent maven-project-builder` - "Run pre-commit verification"
3. Fix any issues identified
4. Commit: `/agent commit-changes` - "Commit the bug fix"

## Dependencies

### Inter-Bundle Dependencies
- None - This bundle is self-contained and has no dependencies on other plugin bundles

### External Dependencies
- Requires Maven wrapper (`./mvnw`) in project root
- Requires git repository for commit operations
- Skill `cui-javadoc` is automatically invoked by maven-project-builder when validating JavaDoc standards

### Used By
This bundle is commonly used by:
- **cui-issue-implementation** - Task executor uses maven-project-builder for build verification
- **cui-pull-request-workflow** - PR quality fixer uses maven-project-builder for validation
- Various commands that need build verification or commit operations
