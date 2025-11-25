---
name: pr-respond-to-review-comments
description: Fetch, triage, and respond to PR review comments
---

# Respond To Review Comments Command

Fetches review comments, triages each one, and takes appropriate action (code change, explanation, or ignore).

## CONTINUOUS IMPROVEMENT RULE

If you discover issues or improvements during execution, record them:

1. **Activate skill**: `Skill: cui-utilities:claude-lessons-learned`
2. **Record lesson** with:
   - Component: `{type: "command", name: "pr-respond-to-review-comments", bundle: "cui-task-workflow"}`
   - Category: bug | improvement | pattern | anti-pattern
   - Summary and detail of the finding

## PRECONDITIONS

- PR checked out locally
- Review comments available
- Caller has ensured prerequisites met

## PREREQUISITES

Load the pr-workflow skill:
```
Skill: cui-task-workflow:pr-workflow
```

## WORKFLOW

### Step 1: Fetch Comments (Skill Workflow 1)

Use **pr-workflow** Fetch Comments workflow:
1. Determine PR number: `gh pr view --json number --jq '.number'`
2. Run fetch script:
   ```bash
   python3 {skillBaseDir}/scripts/fetch-pr-comments.py [--pr {number}]
   ```

### Step 2: Triage and Respond to Each Comment (Skill Workflow 2)

For each unresolved comment, use **pr-workflow** Handle Review workflow:

1. Run triage script:
   ```bash
   python3 {skillBaseDir}/scripts/triage-comment.py --comment '{json}'
   ```

2. Based on script decision:
   - **If code_change**: Delegate to appropriate command or direct Edit
   - **If explain**: Post explanation comment via `gh pr comment {pr} --body "..."`
   - **If ignore**: Skip to next comment

### Step 3: Verify and Commit (if code changed)

```
SlashCommand: /cui-maven:maven-build-and-fix push
```

### Step 4: Return Summary

```json
{
  "comments_addressed": count,
  "code_changes": count,
  "explanations": count,
  "ignored": count
}
```

## CRITICAL RULES

- **Pattern 3**: Fetch + Triage + Delegate
- **Self-Contained**: Handles entire response workflow
- **Conditional Commit**: Only if code was changed
- **Verify + Commit**: Uses /maven-build-and-fix for verification
- **Skill-Based**: Uses pr-workflow skill for fetch and triage logic

## ARCHITECTURE

```
/pr-respond-to-review-comments (Pattern 3 orchestrator)
  ├─> Skill(pr-workflow) Fetch workflow [fetches via gh CLI]
  ├─> For each: Skill(pr-workflow) triage script [decides]
  ├─> Delegates changes: SlashCommand(/java-implement-code) or direct Edit
  └─> Verifies if needed: SlashCommand(/maven-build-and-fix push)
```
