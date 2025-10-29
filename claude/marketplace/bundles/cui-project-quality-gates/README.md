# CUI Project Quality Gates

## Purpose

Change management infrastructure for CUI projects. This bundle provides essential tools for streamlined git commit workflows and JavaDoc documentation standards.

> **Note**: Maven build verification has been moved to the **cui-maven** bundle. Use that bundle for Maven-related build and verification tasks.

## Components Included

This bundle includes the following components:

### Agents
- **commit-changes** - Manages git staging and commits with proper formatting

### Skills
- **cui-javadoc** - JavaDoc standards and validation

## Installation Instructions

To install this plugin bundle, run:

```
/plugin install cui-project-quality-gates
```

This will make all agents and skills available in your Claude Code environment.

## Usage Examples

### Example 1: Commit Changes After Implementation

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

### Example 2: Combined Quality Gate Workflow

Typical workflow combining agents from cui-maven and cui-project-quality-gates bundles:

1. Make code changes
2. Verify build: Use **cui-maven** bundle - `/cui-build-and-verify` or maven-project-builder agent
3. Fix any issues identified
4. Commit: `/agent commit-changes` - "Commit the bug fix"

## Dependencies

### Inter-Bundle Dependencies
- None - This bundle is self-contained and has no dependencies on other plugin bundles

### External Dependencies
- Requires git repository for commit operations

### Related Bundles
- **cui-maven** - Maven build verification and POM maintenance (formerly part of this bundle)
  - Use maven-project-builder agent or /cui-build-and-verify command for Maven builds

### Used By
This bundle is commonly used by:
- **cui-issue-implementation** - Task executor uses commit-changes for git operations
- **cui-pull-request-workflow** - PR workflow uses commit-changes for git operations
- **cui-maven** - Maven agents use cui-javadoc skill for JavaDoc validation
- Various commands that need commit operations or JavaDoc standards
