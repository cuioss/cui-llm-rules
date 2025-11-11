---
name: respond-to-review-comments
description: Fetch, triage, and respond to PR review comments
---

# Respond To Review Comments Command

Fetches review comments, triages each one, and takes appropriate action (code change, explanation, or ignore).

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Update this file using `/cui-update-command command-name=respond-to-review-comments update="[improvement]"` with discoveries.

## PRECONDITIONS

- PR checked out locally
- Review comments available
- Caller has ensured prerequisites met

## WORKFLOW

### Step 1: Fetch Comments

```
Task:
  subagent_type: review-comment-fetcher
  description: Fetch review comments
  prompt: Fetch all review comments for current PR
```

### Step 2: Triage and Respond to Each Comment

For each comment:
```
Task:
  subagent_type: review-comment-triager
  description: Triage comment {id}
  prompt: Analyze comment and decide action
```

Based on triager decision:
- **If code_change**: Delegate to appropriate command or direct Edit
- **If explain**: Post explanation comment (no code change)
- **If ignore**: Skip to next comment

### Step 3: Verify and Commit (if code changed)

```
SlashCommand: /cui-build-and-fix push
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
- **Verify + Commit**: Uses /cui-build-and-fix for verification

## ARCHITECTURE

```
/respond-to-review-comments (Pattern 3 orchestrator)
  ├─> Task(review-comment-fetcher) [fetches]
  ├─> For each: Task(review-comment-triager) [decides]
  ├─> Delegates changes: SlashCommand(/java-implement-code) or direct Edit
  └─> Verifies if needed: SlashCommand(/cui-build-and-fix push)
```
