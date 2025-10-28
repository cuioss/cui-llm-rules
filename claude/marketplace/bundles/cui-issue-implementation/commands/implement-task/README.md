# implement-task

End-to-end issue implementation workflow that orchestrates issue review, planning, project verification, and task-by-task implementation with comprehensive error recovery.

## Purpose

Automates the complete issue implementation lifecycle by coordinating multiple specialized agents: issue review for quality assurance → issue planning for task breakdown → project verification for clean baseline → sequential task implementation with build verification after each task.

## Usage

```bash
# Interactive mode (prompts for issue reference)
/implement-task

# With local issue directory
/implement-task issue=http-client-plan/

# With local issue file
/implement-task issue=http-client-plan/plan-http-client-extension.md

# With GitHub issue number
/implement-task issue=#123

# With GitHub issue URL
/implement-task issue=https://github.com/owner/repo/issues/123

# Resume from specific task
/implement-task issue=#123 continueFrom="Task 5"

# Auto-commit and push when complete
/implement-task issue=http-client-plan/ push
```

## What It Does

The command executes a 6-phase workflow:

1. **Obtain Issue Reference** - Validates and retrieves issue from local file/directory or GitHub
2. **Review Issue** - Runs task-reviewer agent to ensure correctness, completeness, lack of ambiguities
3. **Create/Load Plan** - Runs task-breakdown-agent agent to generate task breakdown with acceptance criteria
4. **Verify Project** - Runs maven-project-builder agent to ensure clean baseline before implementation
5. **Implement Tasks** - Sequentially executes each task using task-executor agent with build verification
6. **Final Report** - Comprehensive summary of all tasks, builds, and lessons learned

## Key Features

- **Multi-Agent Orchestration**: Coordinates 4 specialized agents across 6 phases
- **Quality Gates**: Issue review and project verification before implementation starts
- **Task-by-Task Execution**: Each task implemented and verified independently
- **Build Verification**: Full build runs after each task to catch regressions immediately
- **Error Recovery**: Loop limits, user decision points, retry options throughout
- **Resume Capability**: Can continue from specific task using `continueFrom` parameter
- **Lessons Learned Integration**: Aggregates insights from all agents for workflow improvement
- **Flexible Issue Sources**: Supports local files/directories and GitHub issues

## Parameters

### issue (Optional)
- **Format**: `issue=<path_or_github_issue>`
- **Local**: Path to directory or file containing issue description
- **GitHub**: Issue number (#123) or full URL
- **Default**: Interactive prompt if not provided

### continueFrom (Optional)
- **Format**: `continueFrom=<task_identifier>`
- **By Number**: `continueFrom="Task 5"`
- **By Name**: `continueFrom="Create HttpMethod Enum"`
- **Use Case**: Resume after interruption or skip completed tasks

### push (Optional)
- **Format**: `push` (flag)
- **Behavior**: Auto-commit and push changes after successful completion
- **Note**: Only executes if all tasks complete successfully

## Orchestrated Agents

### task-reviewer
- **Purpose**: Verify issue readiness (correctness, completeness, unambiguity)
- **When**: Phase 2 (before planning)
- **Tools**: Read, Edit, Write, Bash, Task
- **Loop**: Max 3 attempts to achieve success

### task-breakdown-agent
- **Purpose**: Create/load implementation plan with task breakdown
- **When**: Phase 3 (after issue review)
- **Tools**: Read, Write, Bash, Glob
- **Output**: Structured plan with tasks, acceptance criteria, dependencies

### maven-project-builder
- **Purpose**: Verify project builds and passes all quality checks
- **When**: Phase 4 (before implementation) and after each task
- **Tools**: Read, Edit, Write, Bash, Grep
- **Duration**: ~8-10 minutes per build

### task-executor
- **Purpose**: Implement single task from plan
- **When**: Phase 5 (for each task sequentially)
- **Tools**: Read, Edit, Write, Glob, Grep, Task, Bash
- **Duration**: Varies by task complexity (10-30 minutes typical)

## Workflow Overview

### Phase 1: Obtain Issue Reference
- Validates issue parameter or prompts user
- Supports local paths and GitHub issues
- Verifies existence before proceeding

### Phase 2: Review Issue
- **Agent**: task-reviewer
- **Purpose**: Ensure issue is implementation-ready
- **Quality Checks**: Correctness, completeness, lack of ambiguities
- **Loop Protection**: Max 3 review iterations
- **User Decision**: Continue anyway / Re-review / Abort

### Phase 3: Create/Load Plan
- **Agent**: task-breakdown-agent
- **Purpose**: Generate or load task breakdown
- **Plan Structure**: Tasks with acceptance criteria, dependencies, estimates
- **Validation**: Ensures plan has at least one task
- **Resume Support**: Can start from specific task via `continueFrom`

### Phase 4: Verify Project
- **Agent**: maven-project-builder
- **Purpose**: Establish clean baseline before changes
- **Exit if Fails**: Implementation cannot proceed with failing build
- **Duration**: ~8-10 minutes

### Phase 5: Implement Tasks (Loop)
- **For each task** in plan:
  1. Display task info (name, description, acceptance criteria)
  2. Invoke task-executor agent for task
  3. Wait for completion (~10-30 min)
  4. Invoke maven-project-builder for verification
  5. If build fails: Retry task or skip or abort
  6. Mark task complete, proceed to next
- **Loop Protection**: User can skip failing tasks or abort entirely
- **Progress Tracking**: Displays completed/total tasks

### Phase 6: Final Report
- Comprehensive summary with:
  - Total tasks completed
  - Build verifications run
  - Lessons learned from all agents
  - Next steps for remaining work
  - Option to commit and push (if `push` parameter)

## Pre-Conditions

The command verifies before execution:
1. ✅ Git repository (.git/ exists)
2. ✅ GitHub CLI (`gh`) available if GitHub issue used
3. ✅ Required agents exist:
   - `../../agents/task-reviewer/AGENT.md`
   - `../../agents/task-breakdown-agent/AGENT.md`
   - `../../agents/task-executor/AGENT.md`
   - Agent from cui-project-quality-gates bundle: maven-project-builder
4. ✅ Clean git state (no merge conflicts)

## Error Recovery

The command implements comprehensive error handling:

- **Issue Review Failures**: Retry up to 3 times, user can continue anyway or abort
- **Planning Failures**: Agent attempts to fix plan, user can provide corrections
- **Project Build Failures**: Cannot proceed (clean baseline required)
- **Task Implementation Failures**: User can retry task / skip task / abort entirely
- **Build Verification Failures**: User can retry task / skip task / abort entirely

## Resume Capability

Using the `continueFrom` parameter:

```bash
# Resume from task number
/implement-task issue=#123 continueFrom="Task 5"

# Resume from task name (partial match)
/implement-task issue=plan/ continueFrom="Create HttpMethod Enum"
```

The command:
1. Loads existing plan
2. Finds specified task
3. Marks all prior tasks as completed
4. Starts implementation from that task
5. Continues normally

## Expected Duration

- **Small issue** (3-5 tasks): 1-2 hours
  - Issue review: 5-10 min
  - Planning: 5-10 min
  - Project verification: 8-10 min
  - Task implementation: 10-30 min × 3-5 tasks
  - Build verification: 8-10 min × 3-5 tasks

- **Medium issue** (6-10 tasks): 3-5 hours
  - Issue review: 10-15 min
  - Planning: 10-15 min
  - Project verification: 8-10 min
  - Task implementation: 15-45 min × 6-10 tasks
  - Build verification: 8-10 min × 6-10 tasks

- **Large issue** (11+ tasks): 6+ hours
  - May require multiple sessions
  - Use `continueFrom` to resume after breaks

## Integration

Use this command:
- As primary feature implementation workflow
- After issue has been created and documented
- Before creating pull request
- Can be interrupted and resumed using `continueFrom`

Often used with:
- `/task-reviewer` - Called internally in Phase 2
- `/task-breakdown-agent` - Called internally in Phase 3
- `/maven-project-builder` - Called internally in Phases 4 & 5
- `/handle-pull-request` - After implementation complete

## Example Output

```
╔════════════════════════════════════════════════════════╗
║  Implementation Complete                               ║
╚════════════════════════════════════════════════════════╝

Issue: #123 - Implement HTTP Client Extension

Total Tasks: 8
✅ Completed: 8
❌ Failed: 0
⏭️  Skipped: 0

Build Verifications: 9 (1 baseline + 8 post-task)
✅ Passed: 9
❌ Failed: 0

Lessons Learned: 3 insights collected
- task-executor: Better approach for enum validation
- maven-project-builder: Test coverage patterns identified
- task-reviewer: Documentation clarity improvements

Next Steps:
✅ All tasks complete
✅ All builds passing
💡 Ready to create pull request: /handle-pull-request create

Would you like to commit and push these changes? [y/N]:
```

## Notes

- **Sequential Execution**: Tasks are implemented one at a time, not in parallel
- **Build After Each Task**: Ensures regressions caught immediately
- **Agent Autonomy**: Trusts agent reports, does not duplicate their functionality
- **Comprehensive Orchestration**: Coordinates 4 agents across 6 phases
- **Resume-Friendly**: Can be interrupted and resumed using `continueFrom`
- **Lessons Learned**: Aggregates insights from all agent executions

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
