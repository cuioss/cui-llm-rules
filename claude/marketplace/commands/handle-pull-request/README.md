# handle-pull-request

Comprehensive pull request workflow orchestration that creates/manages PRs, waits for CI/Sonar completion, addresses review comments, fixes Sonar issues, and implements lessons learned improvements.

## Purpose

Automates the entire PR lifecycle by orchestrating specialized agents in sequence: build verification → PR creation/update → CI/Sonar wait → Gemini comment handling → Sonar issue resolution (loop until clean) → lessons learned analysis → agent/command improvements.

## Usage

```bash
# Create new PR
/handle-pull-request create

# Handle existing PR
/handle-pull-request url=https://github.com/owner/repo/pull/123

# Interactive mode
/handle-pull-request
```

## What It Does

The command executes a comprehensive 7-step workflow:

1. **Verify Project Build** - Runs maven-project-builder agent to ensure clean codebase
2. **Create/Update PR** - Uses commit-changes agent to push and create/update PR
3. **Wait for CI/Sonar** - Monitors build checks using `gh pr checks` until complete
4. **Handle Review Comments** - Runs pr-review-responder agent to address code review feedback
5. **Fix Sonar Issues** - Loops pr-quality-fixer agent until all issues resolved
6. **Analyze Lessons Learned** - Aggregates insights from all agents, proposes improvements to agents/commands
7. **Update Configuration** - Records new CI/Sonar duration if changed >10%

## Key Features

- **Multi-Agent Orchestration**: Coordinates 4 specialized agents in sequence
- **Intelligent Waiting**: Adapts wait times based on historical CI/Sonar duration
- **Loop Until Clean**: Step 5 repeats until all Sonar issues are resolved (max 5 iterations)
- **Lessons Learned Integration**: Collects insights from all agents, proposes improvements, can auto-update agents/commands
- **Configuration Persistence**: Tracks CI/Sonar duration in `.claude/run-configuration.md`
- **Build Verification**: Each agent verifies build success before proceeding
- **Safety Limits**: Maximum iterations, timeouts, user confirmation gates

## Parameters

- **url** (optional): URL of existing PR (e.g., `https://github.com/owner/repo/pull/123`)
- **create** (optional): Flag to create new PR instead of handling existing one

**Validation:**
- Cannot specify both `url` and `create` (mutually exclusive)
- If neither provided: Interactive mode prompts user to choose

## Workflow Overview

### Step 1: Read Configuration
- Reads `.claude/run-configuration.md` for `ci-sonar-duration`
- Default: 300000ms (5 minutes) if not recorded
- Creates config file if missing

### Step 2: Verify Project Build
- **Agent**: maven-project-builder
- **Purpose**: Ensure clean codebase before PR operations
- **Duration**: ~8-10 minutes
- **Exit if fails**: Build must succeed to proceed

### Step 3: Create/Update PR and Wait for CI/Sonar
- **Agent**: commit-changes
- **Create mode**: Commits, pushes, creates PR, captures URL
- **URL mode**: Pushes uncommitted/unpushed changes to existing PR
- **Wait Strategy**: Initial wait of duration * 1.25, then check `gh pr checks` every 30s
- **Timeout**: 15 minutes maximum
- **Proceed when**: All checks completed (Sonar can be success or failure)

### Step 4: Handle Gemini Review Comments
- **Agent**: pr-review-responder
- **Input**: PR URL from Step 3
- **Actions**: Retrieves Gemini code review comments, fixes issues or marks not applicable
- **Loop back**: If commits created, return to Step 3.B (wait for CI to rerun)

### Step 5: Handle Sonar Issues (Loop Until Clean)
- **Agent**: pr-quality-fixer
- **Purpose**: Fix code issues, suppress false positives, add tests for coverage
- **Loop condition**: Repeats until "0 remaining issues"
- **Safety limit**: Maximum 5 iterations
- **Each iteration**: Waits for Sonar rescan (duration * 1.25) before re-checking

### Step 6: Aggregate Lessons Learned and Propose Improvements
- **Collects insights** from all agent executions (Steps 2-5)
- **Analyzes patterns**: Categorizes by type (agent, command, config), assesses impact (high/medium/low)
- **Proposes changes**: Generates change-set with before/after snippets
- **User decision**: Implement all / Selective / Skip
- **Implementation**: Edits agent/command files, runs doctors for validation

### Step 7: Update Duration and Generate Report
- **Updates `ci-sonar-duration`** if change >10% from previous
- **Comprehensive report**: All agent results, metrics, lessons learned, improvements implemented
- **Final status**: PR ready for review or requires attention

## Orchestrated Agents

### maven-project-builder
- **Purpose**: Verify project builds and passes quality checks
- **Tools**: Read, Edit, Write, Bash
- **Duration**: ~8-10 minutes

### commit-changes
- **Purpose**: Commit changes, push to remote, create PRs
- **Tools**: Read, Bash
- **Duration**: ~1-2 minutes

### pr-review-responder
- **Purpose**: Retrieve and resolve Gemini code review comments
- **Tools**: Read, Edit, Bash, Task
- **Duration**: ~10-15 minutes (varies with comment count)

### pr-quality-fixer
- **Purpose**: Retrieve and resolve Sonar issues, improve coverage
- **Tools**: Read, Edit, Write, Bash, Task
- **Duration**: ~10-20 minutes per iteration

## Prerequisites

### Required Global Permission

This command requires `Bash(sleep:*)` to be globally approved:

```json
"Bash(sleep:*)"
```

**Why:** Used 3-5 times per PR workflow for CI/Sonar wait periods (5-7 minutes each)
**Safety:** Completely passive, no system modifications
**Add to**: `~/.claude/settings.json` in `permissions.allow` array

## Configuration Persistence

The command uses `.claude/run-configuration.md` to store:

```markdown
## handle-pull-request

### CI/Sonar Duration
- **Duration**: 300000ms (5 minutes)
- **Last Updated**: 2025-10-20

### Notes
- This duration represents the time to wait for CI and SonarCloud checks to complete
- Includes buffer time for queue delays
```

Duration is updated automatically if actual wait time differs by >10%.

## Lessons Learned Integration

This command implements a unique **continuous improvement pattern**:

1. **Collect** - Extracts "Lessons Learned" sections from all agent reports
2. **Analyze** - Categorizes insights by type (agent/command/config) and impact (high/medium/low)
3. **Propose** - Generates structured change-set with before/after snippets
4. **Implement** - Edits agent/command files based on user approval
5. **Verify** - Runs diagnose-agents or diagnose-commands to validate changes

This ensures the workflow evolves based on real execution experience.

## Expected Duration

- **Minimal PR** (no issues): ~20-25 minutes
  - Build: 8-10 min
  - PR creation: 1-2 min
  - CI/Sonar wait: 5-7 min
  - Gemini comments: 2-5 min (if any)
  - Sonar issues: 0 (clean)

- **Typical PR** (some issues): ~40-60 minutes
  - Build: 8-10 min
  - PR creation: 1-2 min
  - CI/Sonar wait: 5-7 min
  - Gemini comments: 10-15 min
  - Sonar issues (1 iteration): 15-20 min
  - Lessons learned: 5-10 min

- **Complex PR** (multiple iterations): ~90-120 minutes
  - Build: 8-10 min
  - PR creation: 1-2 min
  - Multiple CI/Sonar waits: 15-20 min
  - Gemini comments (multiple rounds): 20-30 min
  - Sonar issues (3-5 iterations): 45-100 min
  - Lessons learned: 10-15 min

## Loop Protection

- **Step 4** (Gemini comments): Loops back to Step 3.B only if commits created
- **Step 5** (Sonar issues): Maximum 5 iterations before requiring manual intervention
- **Step 3.B** (CI/Sonar wait): 15-minute timeout before prompting user

## Integration

Use this command:
- As primary PR workflow automation
- After completing feature development
- Before requesting code review
- To handle existing PRs with review comments/Sonar issues

Often used with:
- `/maven-project-builder` - Called internally as first step
- `/commit-changes` - Called internally for PR creation
- Direct agent invocations from marketplace

## Example Output

```
## PR Handling Complete

**PR URL**: https://github.com/owner/repo/pull/151
**PR Status**: open

---

### Workflow Summary

**Total Iterations**: 3
- Project verification: 1
- Gemini comment loops: 1
- Sonar issue loops: 2

**Total Execution Time**: 65 minutes

---

### Agent Execution Results

#### maven-project-builder (Step 2)
- Status: SUCCESS
- Issues fixed: 12

#### commit-changes (Step 3)
- PR created: yes
- PR URL: https://github.com/owner/repo/pull/151
- Commits pushed: 1

#### pr-review-responder (Step 4)
- Total comments: 8
- Resolved: 6
- Not applicable: 2
- Commits created: 1

#### pr-quality-fixer (Step 5)
- Iterations: 2
- Total issues: 23
- Fixed: 20
- Suppressed: 3
- Tests added: 5
- Remaining issues: 0
- Commits created: 2

---

### CI/Sonar Duration

- Previous: 300000ms
- Current: 320000ms
- Change: 6.7%
- Updated in .claude/run-configuration.md: no (change < 10%)

---

### Lessons Learned & Improvements

**Insights Collected**: 4

**Changes Implemented**: 2
- Agents updated: pr-quality-fixer
- Commands updated: handle-pull-request
- Config updated: none

**Changes Deferred**: 2 (user chose selective implementation)

---

**Status**: ✅ PR READY FOR REVIEW
```

## Notes

- **Uses `gh` tool exclusively**: NEVER uses GitHub MCP server for reliability
- **Agent autonomy**: Trusts agent reports, does not duplicate their functionality
- **Comprehensive orchestration**: Coordinates 4 agents across 7 steps
- **Continuous improvement**: Learns from each execution, proposes agent/command updates
- **Safe automation**: Multiple safety limits, user confirmation gates

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
