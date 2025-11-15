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

## WORKFLOW

### Step 1: Fetch Issues

```
Task:
  subagent_type: sonar-issue-fetcher
  description: Fetch Sonar issues
  prompt: Fetch all Sonar issues for current PR
```

### Step 2: Triage and Fix Each Issue

For each issue:
```
Task:
  subagent_type: sonar-issue-triager
  description: Triage issue {key}
  prompt: Analyze issue and decide fix vs suppress
```

Based on triager decision:
- **If fix**: `SlashCommand(/java-implement-code "fix {issue}")`
- **If suppress**: `AskUserQuestion` for approval, then add suppression

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

## ARCHITECTURE

```
/pr-fix-sonar-issues (Pattern 3 orchestrator)
  ├─> Task(sonar-issue-fetcher) [fetches]
  ├─> For each: Task(sonar-issue-triager) [decides]
  ├─> Delegates fixes: SlashCommand(/java-implement-code)
  └─> Verifies: SlashCommand(/maven-build-and-fix push)
```
