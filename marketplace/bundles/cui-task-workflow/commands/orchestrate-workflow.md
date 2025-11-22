---
name: orchestrate-workflow
description: Verify, plan, and implement issues through end-to-end workflow with agent coordination
---

# Implement Task Command

End-to-end issue implementation workflow coordinating multiple specialized agents for review, planning, building, and implementation.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=orchestrate-workflow update="[your improvement]"` with:
1. Agent coordination patterns and retry strategies
2. Error recovery and failure handling optimization
3. Task breakdown quality and granularity improvements
4. Build verification efficiency and integration
5. User interaction patterns and decision prompts
6. Any lessons learned about end-to-end workflow orchestration

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

**issue** - GitHub issue number or URL (optional, prompts if not provided)

**continueFrom** - Resume from specific task number (optional)

**push** - Auto-push after successful implementation (optional flag)

## PREREQUISITES

Load the task-planning skill:
```
Skill: cui-task-workflow:cui-task-planning
```

## WORKFLOW

### Step 1: Validate and Get Issue

**Parameter validation:**
1. If `issue` parameter provided:
   - Validate format: must be number (e.g., `123`) or GitHub URL (e.g., `https://github.com/org/repo/issues/123`)
   - Extract issue number from URL if needed
   - If invalid format: Display error "Invalid issue format. Provide issue number or GitHub URL" and abort
2. If `issue` not provided: Prompt user for GitHub issue number or URL
3. If `continueFrom` parameter provided:
   - Store for later use (will validate bounds after plan is created in Step 3)

**Error handling:** If issue cannot be determined or is invalid, abort with clear error message.

### Step 2: Review Issue (Skill Review Workflow)

Use **cui-task-planning** Review workflow:

1. Load issue content: `gh issue view {number} --json title,body,labels`
2. Apply deep analysis for completeness and correctness
3. Identify gaps and ambiguities
4. Update documentation if needed

**Handle results:**
- SUCCESS: Continue to Step 3
- PARTIAL: Prompt user "[C]ontinue/[R]etry review/[A]bort" - increment retry_attempts if retry chosen
- FAILURE: Prompt user "[R]etry review/[A]bort" - increment retry_attempts if retry chosen

**Error handling:** If review fails, increment agent_failures counter and prompt user "[R]etry/[A]bort".

### Step 3: Plan Implementation (Skill Plan Workflow)

Use **cui-task-planning** Plan workflow:

1. Load planning standards: `Read {skillBaseDir}/standards/issue-planning-standards.md`
2. Run analysis script:
   ```bash
   python3 {skillBaseDir}/scripts/create-task-breakdown.py {issue-file}
   ```
3. Generate plan document following standards

**Store tasks list for iteration.**

**Validate continueFrom parameter:**
- If `continueFrom` was provided in Step 1:
  - Verify `continueFrom` is <= total_tasks
  - If out of bounds: Display error "continueFrom={continueFrom} exceeds total tasks ({total_tasks})" and abort
  - If valid: Set starting task index to continueFrom

**Error handling:** If planning fails, increment agent_failures counter and prompt user "[R]etry/[A]bort".

### Step 4: Verify Build

```
SlashCommand: /cui-maven:maven-build-and-fix
```

Self-contained command that runs Maven build, fixes issues if found, verifies, and commits fixes.

**Note:** Build verification always uses Maven, regardless of task language. JavaScript projects use `frontend-maven-plugin` for Maven integration.

**Error handling:** If command fails, increment build_failures counter and prompt user "[R]etry/[A]bort".

### Step 5: Implement Tasks

**Pattern Decision: Determine if atomic or batch:**
- If plan has 1 task (atomic): Execute using skill Execute workflow + verify
- If plan has multiple tasks (batch): Delegate to /orchestrate-task for each

**For atomic (single task):**

Use **cui-task-planning** Execute workflow:
1. Parse task for references and checklist items
2. Read all referenced files
3. Execute checklist items sequentially using Edit, Write tools
4. Mark items complete

Then verify with SlashCommand(/maven-build-and-fix).

**For batch (multiple tasks):**
```
For each task in plan:
  SlashCommand: /cui-task-workflow:orchestrate-task task="{task_description}"
```

Each /orchestrate-task is self-contained (implements + verifies + iterates).

Track: tasks_completed, tasks_failed, tasks_skipped.

### Step 6: Verify Completion

Check all tasks completed. Prompt for incomplete items.

### Step 7: Final Verification and Commit

```
SlashCommand: /cui-maven:maven-build-and-fix push={push parameter}
```

Self-contained command: runs Maven build, fixes issues if found, verifies, commits all changes, and pushes if push=true.

**Note:** Final build always uses Maven, regardless of task language (Java or JavaScript). This ensures full project integration and validates frontend-maven-plugin configuration for JavaScript projects.

**Error handling:** If command fails during final verification, increment build_failures counter and prompt user "[F]ix manually/[R]etry/[A]bort".

### Step 8: Display Summary

```
╔════════════════════════════════════════════════════════════╗
║          Implementation Summary                            ║
╚════════════════════════════════════════════════════════════╝

Issue: #{issue}
Tasks completed: {count}/{total}
Build status: {SUCCESS/FAILURE}
Committed: {yes/no}
Pushed: {yes/no}
```

## STATISTICS TRACKING

Track throughout workflow:
- `agent_failures`: Count of agent execution failures
- `retry_attempts`: Count of user-initiated retries
- `build_time_ms`: Time taken for build operations
- `tasks_completed`: Successful task implementations
- `tasks_failed`: Failed task implementations
- `tasks_skipped`: Skipped tasks

Display all statistics in final summary.

## CRITICAL RULES

**Command Orchestration:**
- Delegate to self-contained commands for build/verify/commit operations
- Pattern Decision: atomic tasks use task-executor + verify, batch uses /orchestrate-task per task
- Wait for each operation to complete before next step
- Handle failures gracefully

**User Interaction:**
- Prompt on PARTIAL results
- Allow user to skip/retry/abort
- Clear decision points

**Quality Gates:**
- Must pass build before implementing
- Must pass build after implementing
- Review issue before planning

**Statistics:**
- Track all task outcomes
- Display comprehensive summary
- Report agent execution results

## USAGE EXAMPLES

**Interactive mode:**
```
/orchestrate-workflow
```

**With issue:**
```
/orchestrate-workflow issue=123
```

**Resume from task:**
```
/orchestrate-workflow issue=123 continueFrom=5
```

**Auto-push:**
```
/orchestrate-workflow issue=123 push
```

## ARCHITECTURE

Orchestrates skills and commands:
- **cui-task-planning** skill - Review, Plan, and Execute workflows
- `/orchestrate-task` command - Self-contained (for batch tasks)
- `/maven-build-and-fix` command - Build + verify + fix + commit

```
/orchestrate-workflow (orchestrator)
  ├─> Skill(cui-task-planning) Review workflow [validates issue]
  ├─> Skill(cui-task-planning) Plan workflow [creates task breakdown]
  ├─> For atomic: Skill(cui-task-planning) Execute workflow [implements]
  ├─> For batch: SlashCommand(/orchestrate-task) per task
  └─> SlashCommand(/maven-build-and-fix) [final verification]
```

## RELATED

- **cui-task-planning** skill - Review, Plan, Execute workflows
- `/orchestrate-task` command (self-contained single task)
- `/orchestrate-language` command (language-specific orchestration)
- `/maven-build-and-fix` command
