---
name: handle-pull-request
description: Execute comprehensive PR workflow including CI/Sonar wait, review responses, and fixes
---

# Handle Pull Request Command

Execute a comprehensive pull request workflow that creates/manages PRs, waits for CI/Sonar completion, addresses review comments, and fixes Sonar issues using specialized agents.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach for:
- Orchestrating agent execution
- Timing and sequencing operations
- Handling edge cases
- Improving workflow efficiency
- Any other aspect of the workflow

**YOU MUST immediately update this file** with:
1. The improved method/approach
2. Updated orchestration logic
3. Better examples or clarifications
4. Any lessons learned

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **url** (optional): The URL of an existing pull request to handle (e.g., `https://github.com/owner/repo/pull/123`)
- **create** (optional): Flag indicating that a new pull request should be created

## PARAMETER VALIDATION

**If both `url` AND `create` are provided:**
- Report error: "Error: Cannot specify both 'url' and 'create'. Choose one mode only."
- Exit command

**If neither `url` nor `create` is provided:**
1. Ask the user: "Would you like to create a new pull request or provide an existing PR URL? [create/url]:"
2. Wait for user response
3. Continue only after the mode is defined (create vs. handle existing)

## WORKFLOW INSTRUCTIONS

### Step 1: Read Configuration

1. Check if `.claude/run-configuration.md` exists in the project root
2. If it doesn't exist, create it with initial structure (see example at bottom)
3. Look for the `handle-pull-request` section
4. Read the `ci-sonar-duration` for this command
5. If no duration is recorded, use **300000ms (5 minutes)** as default
6. If the section doesn't exist, add it to the document with the default duration
7. Store this duration for use in Step 3

### Step 2: Verify Project Build Status

**Use Agent: maven-project-builder**

1. Invoke the `maven-project-builder` agent using Task tool:
   ```
   Task tool with:
     subagent_type: "maven-project-builder"
     prompt: "Verify the project builds and passes all quality checks"
   ```
2. Wait for agent completion (~8-10 minutes)
3. Review agent report for:
   - Build status (must be SUCCESS)
   - Issues found and fixed
   - Any warnings or errors

**Decision Point:**
- If maven-project-builder reports FAILURE: **STOP** - Report to user and exit
- If maven-project-builder reports SUCCESS: Continue to Step 3

**Purpose:** Ensure codebase is in clean state before creating/updating PR

### Step 3: Create/Update PR and Wait for CI/Sonar

**Use Agent: commit-changes**

#### A. Determine PR Mode

**If `create` parameter is provided (no existing PR):**
1. Invoke `commit-changes` agent with parameters: "push and create a pr"
2. Capture PR URL from agent output (e.g., `https://github.com/owner/repo/pull/151`)
3. Store as `PR_LINK` for subsequent steps
4. Extract PR number from URL (e.g., `151`)

**If `url` parameter is provided (existing PR):**
1. Extract PR number from URL (pattern: `/pull/(\d+)`)
2. Store URL as `PR_LINK`
3. Invoke `commit-changes` agent with parameter: "push"
4. This will push any uncommitted or unpushed changes

**Agent Invocation Example:**
```
For create mode:
  Task tool invocation:
    description: "Commit and create PR"
    subagent_type: "commit-changes"
    prompt: "push and create a pr"

For url mode:
  Task tool invocation:
    description: "Push changes"
    subagent_type: "commit-changes"
    prompt: "push"
```

#### B. Wait for CI and Sonar Build Completion

**CRITICAL:** Use `gh` tool to check build status. Do NOT use GitHub MCP server.

1. Extract PR number from `PR_LINK` (pattern: `/pull/(\d+)`)
2. Calculate wait duration: `ci-sonar-duration * 1.25` (duration + 25% buffer)
3. Execute initial wait: `sleep $((ci-sonar-duration * 1.25 / 1000))` (convert ms to seconds)
4. Start checking build status:
   ```bash
   gh pr checks <pr_number>
   ```
5. Analyze check results:
   - Look for all checks (including Sonar/SonarCloud)
   - Identify status: pending, in_progress, completed, success, failure

**Wait Strategy:**
- If any checks are still "pending" or "in_progress":
  - Wait 30 seconds
  - Check again: `gh pr checks <pr_number>`
  - Repeat until all checks complete or timeout (max 15 minutes total)
- If timeout exceeded:
  - Warn user: "Build checks did not complete within timeout"
  - Ask user: "Continue anyway or abort? [continue/abort]"
  - If abort: Exit command

**Record:**
- Track actual wait time for duration calculation later
- Store final build status for all checks

**Proceed to Step 4 only when:**
- All non-Sonar checks are "success" or "completed" (NOT failed)
- Sonar check is "completed" (can be success or failure - will handle issues in Step 5)

### Step 4: Handle Gemini Review Comments

**Use Agent: pr-review-responder**

1. Invoke `pr-review-responder` agent using Task tool:
   ```
   Task tool with:
     subagent_type: "pr-review-responder"
     prompt: "url={PR_LINK} push"
   ```
2. Wait for agent completion
3. Review agent report for:
   - Total Gemini comments processed
   - Comments resolved (fixed)
   - Comments marked not applicable
   - Commits created
   - Build verification results

**Store Lessons Learned:**
- Extract "Lessons Learned" section from agent report
- Keep in memory as list for Step 6 analysis

**Decision Point:**
- If agent made code changes (commits created > 0):
  - Go back to Step 3.B (wait for CI/Sonar to re-run on new commits)
  - Use reduced wait time: `ci-sonar-duration * 1.0` (no buffer needed)
- If no code changes made:
  - Continue to Step 5

### Step 5: Handle Sonar Issues (Loop Until Clean)

**Use Agent: pr-quality-fixer**

This step implements a loop that continues until all Sonar issues are resolved.

#### Step 5.1: Invoke Sonar Issue Handler

1. Invoke `pr-quality-fixer` agent using Task tool:
   ```
   Task tool with:
     subagent_type: "pr-quality-fixer"
     prompt: "url={PR_LINK} push"
   ```
2. Wait for agent completion (~10-15 minutes including builds)
3. Review agent report for:
   - Total Sonar issues found
   - Issues fixed (code changes)
   - Issues suppressed (false positives)
   - Tests added for coverage
   - Commits created
   - Build verification results
   - Final Sonar status

**Store Lessons Learned:**
- Extract "Lessons Learned" section from agent report
- Append to lessons learned list for Step 6 analysis

#### Step 5.2: Verify All Issues Resolved

Check agent report metrics:
- Verify: `fixed + suppressed = total issues`
- Verify: Final status shows "0 remaining issues"

**Decision Point:**

**If agent report shows "0 remaining issues" AND build is clean:**
- Sonar issues fully resolved
- Continue to Step 6

**If agent report shows remaining issues OR new issues appeared:**
- This means the fixes created new issues (common scenario)
- Calculate new wait duration: `ci-sonar-duration * 1.25`
- Wait for Sonar to re-scan: `sleep $((ci-sonar-duration * 1.25 / 1000))` (convert ms to seconds)
- Wait for build completion (same as Step 3.B)
- **Return to Step 5.1** (invoke pr-quality-fixer again)
- Repeat until clean

**Safety Limit:**
- Maximum 5 iterations of Step 5
- If limit exceeded: "Maximum iterations reached (5). Manual intervention required. Continue? [y/N]:"

### Step 6: Aggregate Lessons Learned and Propose Improvements

**CRITICAL:** This step analyzes all lessons learned from agent executions and proposes improvements.

#### Step 6.1: Collect All Lessons Learned

1. Gather "Lessons Learned" sections from:
   - maven-project-builder agent (Step 2)
   - commit-changes agent (Step 3)
   - pr-review-responder agent (Step 4)
   - pr-quality-fixer agent (Step 5, all iterations)

2. Store in memory as structured list:
   ```
   lessons_learned = [
     {
       source: "maven-project-builder",
       discovery: "...",
       why_it_matters: "...",
       suggested_improvement: "...",
       impact: "..."
     },
     {
       source: "pr-review-responder",
       discovery: "...",
       ...
     }
   ]
   ```

3. Count total lessons learned entries

**If count = 0:**
- Skip to Step 7 (no improvements needed)

**If count > 0:**
- Continue to Step 6.2

#### Step 6.2: Deep Analysis of Lessons Learned

**Carefully analyze all lessons learned to identify improvement patterns:**

For each lesson learned:
1. **Categorize by type:**
   - Agent workflow improvement (affects specific agent)
   - Command orchestration improvement (affects this command)
   - Configuration improvement (affects .claude/run-configuration.md)
   - Tool usage improvement (affects multiple agents/commands)

2. **Assess impact:**
   - High: Affects reliability, correctness, or critical functionality
   - Medium: Affects efficiency or user experience
   - Low: Minor improvement or optimization

3. **Identify affected files:**
   - Which agent files need updates
   - Which command files need updates
   - Which configuration files need updates

4. **Draft specific changes:**
   - For each affected file, draft exact changes needed
   - Include before/after snippets
   - Explain rationale

#### Step 6.3: Generate Change-Set Proposal

Create a structured proposal with:

```
## Lessons Learned Analysis - PR #{pr_number}

**Total Insights**: {count}

**High Impact**: {count}
**Medium Impact**: {count}
**Low Impact**: {count}

---

### Proposed Changes

#### Agent Updates Required

{For each agent requiring updates:}

**Agent**: {agent_name}.md
**Insights Applied**: {count}
**Impact Level**: {High/Medium/Low}

**Changes:**
1. {Change description}
   - Current: {snippet}
   - Proposed: {snippet}
   - Rationale: {explanation}

2. {Next change...}

---

#### Command Updates Required

{For each command requiring updates:}

**Command**: {command_name}.md
**Insights Applied**: {count}
**Impact Level**: {High/Medium/Low}

**Changes:**
1. {Change description}
   - Current: {snippet}
   - Proposed: {snippet}
   - Rationale: {explanation}

---

#### Configuration Updates Required

{For .claude/run-configuration.md or other config files:}

**File**: {file_path}
**Changes**: {description}

---

### Implementation Plan

**Total Files to Update**: {count}
- Agents: {list}
- Commands: {list}
- Config: {list}

**Estimated Time**: {minutes} minutes

**Quality Verification Steps**:
1. Run diagnose-agents for each changed agent
2. Run diagnose-commands for each changed command
3. Test updated workflow with sample PR

**Would you like me to implement these changes?**

[Yes - Implement all] [Selective - Choose which] [No - Skip]
```

#### Step 6.4: Wait for User Decision

**If user chooses "Yes - Implement all":**
- Continue to Step 6.5

**If user chooses "Selective - Choose which":**
- Ask user to specify which changes to implement
- Filter change-set to selected items
- Continue to Step 6.5 with filtered list

**If user chooses "No - Skip":**
- Log that improvements were identified but not implemented
- Continue to Step 7

#### Step 6.5: Implement Approved Changes

For each approved change:

**For Agent Updates:**
1. Read current agent file
2. Apply proposed changes using Edit tool
3. Save updated agent file
4. Invoke `/diagnose-agents` using SlashCommand tool:
   ```
   command: "/diagnose-agents {agent_name}"
   ```
5. Wait for diagnose-agents completion
6. Review report for validation errors
7. If errors found: Fix and re-run diagnose-agents
8. Repeat until clean

**For Command Updates:**
1. Read current command file
2. Apply proposed changes using Edit tool
3. Save updated command file
4. Invoke `/diagnose-commands` using SlashCommand tool:
   ```
   command: "/diagnose-commands {command_name}"
   ```
5. Wait for diagnose-commands completion
6. Review report for validation errors
7. If errors found: Fix and re-run diagnose-commands
8. Repeat until clean

**For Configuration Updates:**
1. Read current config file (e.g., .claude/run-configuration.md)
2. Apply proposed changes using Edit tool
3. Save updated config file

**Track:**
- Count of agents updated
- Count of commands updated
- Count of config files updated

### Step 7: Update Duration and Generate Final Report

#### Step 7.1: Update CI/Sonar Duration (If Changed)

1. Calculate total Sonar wait time from all iterations (Step 3 + Step 5 repeats)
2. Calculate average Sonar completion time
3. Calculate percentage change: `|new_duration - old_duration| / old_duration * 100`
4. If the change is **greater than 10%**, update `ci-sonar-duration` in `.claude/run-configuration.md`

#### Step 7.2: Display Comprehensive Summary Report

```
## PR Handling Complete

**PR URL**: {PR_LINK}
**PR Status**: {open/merged/closed}

---

### Workflow Summary

**Total Iterations**: {count}
- Project verification: 1
- Gemini comment loops: {count}
- Sonar issue loops: {count}

**Total Execution Time**: {minutes} minutes

---

### Agent Execution Results

#### maven-project-builder (Step 2)
- Status: {SUCCESS/FAILURE}
- Issues fixed: {count}

#### commit-changes (Step 3)
- PR created: {yes/no}
- PR URL: {url if created}
- Commits pushed: {count}

#### pr-review-responder (Step 4)
- Total comments: {count}
- Resolved: {count}
- Not applicable: {count}
- Commits created: {count}

#### pr-quality-fixer (Step 5)
- Iterations: {count}
- Total issues: {count}
- Fixed: {count}
- Suppressed: {count}
- Tests added: {count}
- Remaining issues: 0 (MUST be zero)
- Commits created: {count}

---

### CI/Sonar Duration

- Previous: {old_duration}ms
- Current: {new_duration}ms
- Change: {percentage}%
- Updated in .claude/run-configuration.md: {yes/no}

---

### Lessons Learned & Improvements

**Insights Collected**: {count}

**Changes Implemented**: {count}
- Agents updated: {list}
- Commands updated: {list}
- Config updated: {list}

**Changes Deferred**: {count}
{List if any were proposed but not implemented}

---

### Final Metrics

**Total Commits Created**: {count}
**Total Files Modified**: {count}
**Total Build Verifications**: {count}
**All Checks Passing**: {yes/no}

---

**Status**: ✅ PR READY FOR REVIEW | ⚠️ REQUIRES ATTENTION
```

### Step 7.3: Wait for User Acknowledgment

Display message:
```
PR handling workflow complete. Please review the PR and merge when ready.

PR URL: {PR_LINK}
```

## PREREQUISITES

### Required Global Permissions

This command requires the following permission to be globally approved to avoid repetitive prompts during CI/Sonar wait periods:

- **`Bash(sleep:*)`** - Essential for waiting between build checks
  - Usage: Waits for CI and Sonar builds to complete (typically 5-7 minutes per wait)
  - Safety: Completely passive command with no system modifications
  - Location: Add to `~/.claude/settings.json` in `permissions.allow` array

**Why globally approved:**
- Used 3-5 times per PR workflow (initial build, after fixes, final verification)
- Safe and passive (similar to `date`, `cal`, `history` which are already approved)
- Essential for automation - prevents workflow interruption

**To add:**
```json
"Bash(sleep:*)"
```

## CRITICAL RULES

- **ALWAYS use specialized agents** - Never duplicate agent functionality in this command
- **ALWAYS use `gh` tool** for GitHub interactions - NEVER use GitHub MCP server
- **ALWAYS wait for agent completion** before proceeding to next step
- **ALWAYS extract and store lessons learned** from each agent execution
- **ALWAYS loop Step 5** until Sonar issues = 0 (max 5 iterations)
- **ALWAYS return to Step 3.B** after code changes in Step 4
- **ALWAYS perform deep analysis** of lessons learned in Step 6
- **ALWAYS run diagnose-agents** after updating agents (Step 6.5)
- **ALWAYS run diagnose-commands** after updating commands (Step 6.5)
- **ALWAYS verify all checks pass** before completing workflow
- **UPDATE duration only if change > 10%**
- **ALWAYS track** total wait times for all Sonar builds
- **NEVER proceed** if maven-project-builder fails in Step 2
- **NEVER skip** lessons learned analysis if insights exist
- **ALWAYS use standard commit format** with Claude Code footer (agents handle this)
- **ALWAYS update this file** when you discover better orchestration approaches

## AGENT USAGE REFERENCE

### maven-project-builder
**Purpose:** Verify project builds and passes all quality checks
**When:** Step 2 (initial verification)
**Tools:** Read, Edit, Write, Bash
**Duration:** ~8-10 minutes

### commit-changes
**Purpose:** Commit changes, push to remote, create PRs
**When:** Step 3 (create/update PR)
**Parameters:** "push", "push and create a pr"
**Tools:** Read, Bash
**Duration:** ~1-2 minutes

### pr-review-responder
**Purpose:** Retrieve and resolve Gemini code review comments
**When:** Step 4 (after PR created and builds complete)
**Parameters:** "url={PR_LINK} push"
**Tools:** Read, Edit, Bash, Task
**Duration:** ~10-15 minutes (varies with comment count)

### pr-quality-fixer
**Purpose:** Retrieve and resolve all Sonar issues, improve coverage
**When:** Step 5 (loop until clean)
**Parameters:** "url={PR_LINK} push"
**Tools:** Read, Edit, Write, Bash, Task
**Duration:** ~10-20 minutes per iteration (varies with issue count)

## DOCTOR COMMAND REFERENCE

### /diagnose-agents {agent_name}
**Purpose:** Validate agent file structure and compliance
**When:** After updating agent in Step 6.5
**Validates:** Frontmatter, rules embedding, tool coverage, response format

### /diagnose-commands {command_name}
**Purpose:** Validate slash command structure and documentation
**When:** After updating command in Step 6.5
**Validates:** Parameter documentation, workflow clarity, examples

## Example .claude/run-configuration.md Structure

```markdown
# Command Configuration

## handle-pull-request

### CI/Sonar Duration
- **Duration**: 300000ms (5 minutes)
- **Last Updated**: 2025-10-20

### Notes
- This duration represents the time to wait for CI and SonarCloud checks to complete
- Includes buffer time for queue delays
```

## Usage Examples

### Create New PR
```
/handle-pull-request create
```

### Handle Existing PR
```
/handle-pull-request url=https://github.com/owner/repo/pull/123
```

### Interactive Mode (No Parameters)
```
/handle-pull-request
```
Will prompt: "Would you like to create a new pull request or provide an existing PR URL?"
