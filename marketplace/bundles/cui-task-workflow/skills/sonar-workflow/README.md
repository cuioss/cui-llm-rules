# Sonar Workflow Skill

Handles Sonar issue workflows - fetching issues from SonarQube, triaging them, and implementing fixes or suppressions.

## Workflows

1. **Fetch Issues Workflow** - Retrieves Sonar issues via MCP tool or API
2. **Fix Issues Workflow** - Triages and resolves each issue

## Scripts

- `fetch-sonar-issues.py` - Generates MCP tool instruction for fetching issues
- `triage-issue.py` - Analyzes issue and determines fix vs suppress action

## Commands Using This Skill

- `/pr-fix-sonar-issues`
- `/pr-handle-pull-request`

## Related Skills

- **pr-workflow** - Often used together in PR workflows
- **cui-git-workflow** - Commits fixes
