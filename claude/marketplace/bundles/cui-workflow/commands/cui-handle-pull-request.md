---
name: cui-handle-pull-request
description: Execute comprehensive PR workflow including CI/Sonar wait, review responses, and fixes
---

# Handle Pull Request Command

Comprehensive pull request workflow handling CI/Sonar checks, code review responses, and quality fixes.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/cui-update-command command-name=cui-handle-pull-request update="[your improvement]"` with:
1. Improved strategies for CI/Sonar polling and timeout handling
2. Better agent coordination patterns for review/quality workflows
3. More effective error recovery strategies for build/check failures
4. Enhanced decision point prompts for user control
5. Any lessons learned about PR workflow automation

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

**pr** - Pull request number or URL
   - **Validation**: If provided, must be numeric (PR number) or valid GitHub URL
   - **Error**: If invalid: "PR must be a number or valid GitHub PR URL" and retry

## WORKFLOW

### Step 1: Get PR Information

If pr parameter not provided, prompt user.

Fetch PR details via gh API:
```
Bash: gh pr view {pr} --json number,title,state,url
```

**Error handling:**
- **If gh command fails**: Display "Failed to fetch PR details: {error}" and prompt "[R]etry/[A]bort"
- **If PR not found**: Display "PR #{pr} not found in repository" and prompt "[E]nter different PR/[A]bort"
- Track successful fetch in pr_checks_performed counter

### Step 2: Wait for CI and Sonar

Poll PR status until:
- All CI checks pass/fail
- Sonar analysis completes

Display status updates every 30 seconds.

**Timeout handling:**
- **If timeout after 30 minutes**:
  - Display: "⏱️ CI/Sonar checks still running after 30 minutes"
  - Prompt: "[C]ontinue waiting/[S]kip checks/[A]bort workflow"
  - If continue: Extend timeout by 15 minutes
  - If skip: Proceed with warning (may encounter issues later)

**Error handling:**
- Track wait time and poll count in pr_checks_performed counter

### Step 3: Check Build Status

If build failed:
```
Task:
  subagent_type: maven-project-builder
  description: Fix build failures
  prompt: Review build logs and fix failures
```

**Error handling:**
- **If agent launch fails**: Display "Failed to launch maven-project-builder: {error}" and prompt "[R]etry/[M]anual fix/[A]bort"
- **If agent cannot fix build**: Display agent report and prompt "[M]anual intervention needed/[A]bort workflow"
- Track in build_verifications counter

### Step 4: Handle Code Review Comments

```
Task:
  subagent_type: pr-review-responder
  description: Respond to review comments
  prompt: Retrieve and resolve Gemini code review comments on PR {pr}
```

Agent either fixes issues or explains why changes not applicable.

**Error handling:**
- **If agent launch fails**: Display "Failed to launch pr-review-responder: {error}" and prompt "[R]etry/[S]kip review comments/[A]bort"
- Track resolved comments in reviews_responded_to counter

### Step 5: Handle Sonar Issues

Loop until Sonar quality gate passes or user decides to skip:

```
Task:
  subagent_type: pr-quality-fixer
  description: Fix Sonar issues
  prompt: Retrieve and resolve Sonar issues on PR {pr}
```

Agent fixes code issues, suppresses false positives, improves coverage.

**Decision point after each iteration:**
- Display: "Sonar iteration complete. {count} issues fixed, {count} suppressed."
- Prompt: "[C]ontinue fixing/[S]kip remaining/[A]bort workflow"

**Error handling:**
- **If agent launch fails**: Display "Failed to launch pr-quality-fixer: {error}" and prompt "[R]etry/[S]kip Sonar/[A]bort"
- Track fixed and suppressed issues in sonar_issues_fixed counter

### Step 6: Final Verification

Run maven-project-builder to verify all changes build successfully:

```
Task:
  subagent_type: maven-project-builder
  description: Final build verification
  prompt: Run full build to verify all PR changes
```

**Error handling:**
- **If build fails**: Display "Final build failed" and prompt "[F]ix issues/[A]bort workflow"
- Track in build_verifications counter

### Step 7: Cleanup and Display Summary

**Cleanup:**
- No temporary files created (all state managed by agents)
- No cleanup required

**Display summary:**
```
╔════════════════════════════════════════════════════════════╗
║          PR Workflow Summary                               ║
╚════════════════════════════════════════════════════════════╝

PR: #{pr}
CI Status: {PASS/FAIL}
Sonar Quality Gate: {PASS/FAIL}
Review Comments: {reviews_responded_to} resolved
Sonar Issues: {sonar_issues_fixed} fixed/suppressed
Build Status: {SUCCESS/FAILURE}

Statistics:
- PR checks performed: {pr_checks_performed}
- Reviews responded to: {reviews_responded_to}
- Sonar issues fixed: {sonar_issues_fixed}
- Build verifications: {build_verifications}

Workflow duration: {elapsed_time}
```

## STATISTICS TRACKING

Track throughout workflow:
- `pr_checks_performed`: Count of CI/Sonar status checks and PR info fetches
- `reviews_responded_to`: Count of code review comments addressed
- `sonar_issues_fixed`: Count of Sonar issues fixed or suppressed
- `build_verifications`: Count of maven build runs

Display all statistics in Step 7 summary.

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
- Clear decision points with [C]ontinue/[S]kip/[A]bort patterns
- Status updates throughout workflow

**Error Handling:**
- All gh commands have retry/abort options
- All agent launches have failure recovery
- Timeouts prompt for user decision
- Track all operations in statistics

**Parameter Validation:**
- PR parameter must be numeric or valid URL
- Clear error messages for invalid inputs
- Retry logic for all validations

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

- `/cui-update-command` - Update this command
- pr-review-responder agent
- pr-quality-fixer agent
- maven-project-builder agent
