# PR Workflow Skill

Handles PR review comment workflows - fetching comments, triaging them, and generating appropriate responses.

## Workflows

1. **Fetch Comments Workflow** - Retrieves PR review comments using gh CLI
2. **Handle Review Workflow** - Processes and responds to each comment

## Scripts

- `fetch-pr-comments.py` - Fetches PR comments via gh CLI
- `triage-comment.py` - Analyzes comment and determines action (code_change/explain/ignore)

## Commands Using This Skill

- `/pr-respond-to-review-comments`
- `/pr-handle-pull-request`

## Related Skills

- **sonar-workflow** - Often used together in PR workflows
- **cui-git-workflow** - Commits changes after responses
