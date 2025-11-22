---
name: pr-fix-sonar-issues
description: Fetch, triage, and fix Sonar issues
---

# Fix Sonar Issues Command

Fetches Sonar issues, triages each one, and delegates fixes. Self-contained with own verify + commit cycle.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=pr-fix-sonar-issues update="[your improvement]"` with:
1. Issue triage patterns - When to automatically fix vs escalate vs suppress, detection of high-confidence vs complex issues
2. Issue categorization strategies - Grouping related issues, identifying root causes affecting multiple files, handling cascading issues
3. Fix validation patterns - How to verify fixes don't introduce new issues, regressions in related code, test coverage impact
4. Suppression criteria refinement - When suppressions are justified (e.g., false positives, architectural exceptions, intentional patterns)
5. Any lessons learned about Sonar API patterns, issue classification accuracy, or fix delegation effectiveness

This ensures the command evolves to handle increasingly complex Sonar issue scenarios with better accuracy and efficiency.

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

1. Run triage script:
   ```bash
   python3 {skillBaseDir}/scripts/triage-issue.py --issue '{json}'
   ```

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
