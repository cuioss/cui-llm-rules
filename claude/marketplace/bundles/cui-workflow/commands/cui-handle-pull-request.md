---
name: cui-handle-pull-request
description: Execute comprehensive PR workflow including CI/Sonar wait, review responses, and fixes
---

# Handle Pull Request Command

Comprehensive pull request workflow handling CI/Sonar checks, code review responses, and quality fixes.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/cui-update-command command-name=cui-handle-pull-request update="[your improvement]"` with:
1. Improved strategies for CI/Sonar polling and timeout handling
2. Better command orchestration patterns for review/quality workflows
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
SlashCommand: /cui-maven-build-and-fix push
```

Self-contained command that fixes build + verifies + commits.

**Error handling:**
- **If command fails**: Display "Failed to fix build: {error}" and prompt "[R]etry/[M]anual fix/[A]bort"
- **If cannot fix build**: Display command report and prompt "[M]anual intervention needed/[A]bort workflow"
- Track in build_verifications counter

### Step 4: Handle Code Review Comments

```
SlashCommand: /cui-respond-to-review-comments
```

Self-contained Pattern 3 command: fetches comments → triages each → code change or explanation → verifies + commits.

**Error handling:**
- **If command fails**: Display "Failed to respond to review comments: {error}" and prompt "[R]etry/[S]kip review comments/[A]bort"
- Track resolved comments in reviews_responded_to counter (from command result)

### Step 5: Handle Sonar Issues

```
SlashCommand: /cui-fix-sonar-issues
```

Self-contained Pattern 3 command: fetches Sonar issues → triages each → fixes or suppresses (with user approval) → verifies + commits.

Command includes triage logic with user approval for suppressions internally.

**Error handling:**
- **If command fails**: Display "Failed to fix Sonar issues: {error}" and prompt "[R]etry/[S]kip Sonar/[A]bort"
- Track fixed and suppressed issues in sonar_issues_fixed counter (from command result)

### Step 6: Display Summary

**Aggregate results from self-contained commands:**
- Each command returns structured results
- Aggregate: reviews_responded_to, sonar_issues_fixed, build_verifications
- No final verification needed (commands verify themselves)

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
- No final verification needed (commands verify themselves)

**Command Orchestration:**
- Delegate to self-contained Pattern 3 commands
- Commands handle fetch → triage → fix → verify → commit internally
- Aggregate results from command structured returns

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

Simple orchestrator that delegates to self-contained commands:
- `/cui-maven-build-and-fix` - Fix build failures + verify + commit
- `/cui-respond-to-review-comments` - Handle review comments (Pattern 3: fetch → triage → respond)
- `/cui-fix-sonar-issues` - Handle Sonar issues (Pattern 3: fetch → triage → fix)

Each command is self-contained with own verify + commit cycle.

## RELATED

- `/cui-update-command` - Update this command
- `/cui-maven-build-and-fix` - Build fixing command
- `/cui-respond-to-review-comments` - Review comment handling (Pattern 3)
- `/cui-fix-sonar-issues` - Sonar issue fixing (Pattern 3)
