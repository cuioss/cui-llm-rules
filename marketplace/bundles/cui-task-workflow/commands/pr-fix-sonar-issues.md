---
name: pr-fix-sonar-issues
description: Fetch, triage, and fix Sonar issues
---

# Fix Sonar Issues Command

Fetches Sonar issues, triages each one, and delegates fixes. Self-contained with own verify + commit cycle.

## CONTINUOUS IMPROVEMENT RULE

If you discover issues or improvements during execution, record them:

1. **Activate skill**: `Skill: cui-utilities:claude-lessons-learned`
2. **Record lesson** with:
   - Component: `{type: "command", name: "pr-fix-sonar-issues", bundle: "cui-task-workflow"}`
   - Category: bug | improvement | pattern | anti-pattern
   - Summary and detail of the finding

## PRECONDITIONS

- PR checked out locally
- CI build complete
- Sonar analysis complete
- Caller has ensured prerequisites met

## PREREQUISITES

Load the sonar-workflow skill:
```
Skill: cui-task-workflow:sonar-workflow
```

## WORKFLOW

### Step 1: Fetch Issues (Skill Workflow 1)

Use **sonar-workflow** Fetch Issues workflow:
1. Determine PR context: `gh pr view --json number`
2. Use MCP tool to fetch issues:
   ```
   mcp__sonarqube__search_sonar_issues_in_projects(
     projects: ["{project_key}"],
     pullRequestId: "{pr_number}"
   )
   ```

### Step 2: Triage and Fix Each Issue (Skill Workflow 2)

For each issue, use **sonar-workflow** Fix Issues workflow:

1. The skill runs its triage script to decide fix vs suppress
2. Based on script decision:
   - **If fix**: `SlashCommand(/java-implement-code "fix {issue}")`
   - **If suppress**: `AskUserQuestion` for approval, then add suppression comment

### Step 3: Verify and Commit

```
SlashCommand: /cui-maven:maven-build-and-fix push
```

### Step 4: Return Summary

```json
{
  "issues_fixed": count,
  "issues_suppressed": count,
  "files_modified": [list]
}
```

## CRITICAL RULES

- **Pattern 3**: Fetch + Triage + Delegate
- **Self-Contained**: Handles entire fix workflow
- **User Approval**: Ask before suppressing issues
- **Verify + Commit**: Uses /maven-build-and-fix for final verification
- **Skill-Based**: Uses sonar-workflow skill for fetch and triage logic

## ARCHITECTURE

```
/pr-fix-sonar-issues (Pattern 3 orchestrator)
  ├─> Skill(sonar-workflow) Fetch workflow [fetches via MCP]
  ├─> For each: Skill(sonar-workflow) triage script [decides]
  ├─> Delegates fixes: SlashCommand(/java-implement-code)
  └─> Verifies: SlashCommand(/maven-build-and-fix push)
```
