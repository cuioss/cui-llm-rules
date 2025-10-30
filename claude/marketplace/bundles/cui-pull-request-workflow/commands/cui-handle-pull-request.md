---
name: cui-handle-pull-request
description: Execute comprehensive PR workflow including CI/Sonar wait, review responses, and fixes
---

# Handle Pull Request Command

Comprehensive pull request workflow handling CI/Sonar checks, code review responses, and quality fixes.

## PARAMETERS

**pr** - Pull request number or URL

## WORKFLOW

### Step 1: Get PR Information

If pr parameter not provided, prompt user. Fetch PR details via gh API.

### Step 2: Wait for CI and Sonar

Poll PR status until:
- All CI checks pass/fail
- Sonar analysis completes

Display status updates. Timeout after 30 minutes.

### Step 3: Check Build Status

If build failed:
```
Task:
  subagent_type: maven-project-builder
  description: Fix build failures
  prompt: Review build logs and fix failures
```

### Step 4: Handle Code Review Comments

```
Task:
  subagent_type: pr-review-responder
  description: Respond to review comments
  prompt: Retrieve and resolve Gemini code review comments on PR {pr}
```

Agent either fixes issues or explains why changes not applicable.

### Step 5: Handle Sonar Issues

Loop until Sonar quality gate passes or user decides to skip:

```
Task:
  subagent_type: pr-quality-fixer
  description: Fix Sonar issues
  prompt: Retrieve and resolve Sonar issues on PR {pr}
```

Agent fixes code issues, suppresses false positives, improves coverage.

Decision point: Continue fixing, skip remaining, or abort.

### Step 6: Final Verification

Run maven-project-builder to verify all changes build successfully.

### Step 7: Display Summary

```
╔════════════════════════════════════════════════════════════╗
║          PR Workflow Summary                               ║
╚════════════════════════════════════════════════════════════╝

PR: #{pr}
CI Status: {PASS/FAIL}
Sonar Quality Gate: {PASS/FAIL}
Review Comments: {count} resolved
Sonar Issues: {count} fixed, {count} suppressed
Build Status: {SUCCESS/FAILURE}
```

## CRITICAL RULES

**Workflow:**
- Must wait for CI/Sonar before proceeding
- Handle build failures before code review
- Allow user to skip Sonar if needed
- Final build verification required

**Agent Delegation:**
- Use specialized agents for each concern
- Don't duplicate agent logic in command
- Trust agent capabilities

**User Control:**
- Timeout warnings for long waits
- Decision points for Sonar loop
- Clear status updates

## USAGE EXAMPLES

**Interactive:**
```
/cui-handle-pull-request
```

**With PR number:**
```
/cui-handle-pull-request pr=123
```

**With PR URL:**
```
/cui-handle-pull-request pr=https://github.com/owner/repo/pull/123
```

## ARCHITECTURE

Orchestrates:
- maven-project-builder - Build verification
- pr-review-responder - Code review handling
- pr-quality-fixer - Sonar issue resolution

## RELATED

- pr-review-responder agent
- pr-quality-fixer agent
- maven-project-builder agent
