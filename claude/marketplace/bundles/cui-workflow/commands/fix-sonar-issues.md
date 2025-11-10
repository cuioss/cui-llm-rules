---
name: fix-sonar-issues
description: Fetch, triage, and fix Sonar issues
---

# Fix Sonar Issues Command

Fetches Sonar issues, triages each one, and delegates fixes. Self-contained with own verify + commit cycle.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Update this file using `/cui-update-command command-name=fix-sonar-issues update="[improvement]"` with discoveries.

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
SlashCommand: /cui-build-and-fix push
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
- **Verify + Commit**: Uses /cui-build-and-fix for final verification

## ARCHITECTURE

```
/fix-sonar-issues (Pattern 3 orchestrator)
  ├─> Task(sonar-issue-fetcher) [fetches]
  ├─> For each: Task(sonar-issue-triager) [decides]
  ├─> Delegates fixes: SlashCommand(/java-implement-code)
  └─> Verifies: SlashCommand(/cui-build-and-fix push)
```
