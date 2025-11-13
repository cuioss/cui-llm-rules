---
name: cui-respond-to-review-comments
description: Fetch, triage, and respond to PR review comments
---

# Respond To Review Comments Command

Fetches review comments, triages each one, and takes appropriate action (code change, explanation, or ignore).

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=cui-respond-to-review-comments update="[your improvement]"` with:
1. Comment triage patterns - How to identify actionable vs informational comments, distinguish preference feedback from requirements, detect conflicting feedback
2. Response strategy refinement - When to implement code changes vs explain design decisions vs suggest alternatives, handling subjective feedback
3. Implementation approach improvements - Optimal delegation patterns (direct Edit vs SlashCommand), handling complex multi-file changes from single comments
4. Comment complexity detection - Recognizing comments requiring architectural changes, dependency updates, or test modifications vs simple code fixes
5. Any lessons learned about reviewer patterns, common feedback themes, or effectiveness of different response types in reducing future comments

This ensures the command evolves to handle increasingly nuanced review feedback with better judgment and more effective responses.

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
SlashCommand: /cui-maven-build-and-fix push
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
- **Verify + Commit**: Uses /cui-maven-build-and-fix for verification

## ARCHITECTURE

```
/cui-respond-to-review-comments (Pattern 3 orchestrator)
  ├─> Task(review-comment-fetcher) [fetches]
  ├─> For each: Task(review-comment-triager) [decides]
  ├─> Delegates changes: SlashCommand(/java-implement-code) or direct Edit
  └─> Verifies if needed: SlashCommand(/cui-maven-build-and-fix push)
```
