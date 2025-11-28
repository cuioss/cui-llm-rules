---
name: phase-management
description: Orchestrates plan-based task workflows by routing to appropriate phase skills based on plan state. Handles plan discovery, phase routing, transitions, and status reporting. Used by /plan-manage and /plan-execute commands.
allowed-tools: Read, Glob, Bash, Skill, AskUserQuestion
---

# Phase Management Skill

**EXECUTION MODE**: Execute requested operation immediately. Do not explain or summarize.

**CRITICAL CONSTRAINT - NO IMPLEMENTATION WITHOUT PLAN**:
- This skill creates and manages **plans only** - it NEVER implements tasks directly
- When user provides a task description, you MUST create plan files in `.claude/plans/` first
- NEVER write code, create components, or modify files outside `.claude/plans/`
- After plan creation, STOP and wait for user to invoke `/plan-execute`
- If you find yourself about to implement something, STOP - you are violating this constraint

**Role**: Orchestration layer for plan-based task workflows. Routes to phase skills based on plan state. Does NOT execute phase work - delegates to phase-specific skills.

## Standards (Load On-Demand)

### Orchestration
```
Read standards/orchestration.md
```
Contains: Orchestration patterns, skill delegation, user interaction coordination

### Transitions
```
Read standards/transitions.md
```
Contains: Phase transition rules, validation, completion detection

---

## Workflow: Manage Plans

Invoked by `/plan-manage` command. Handles plan lifecycle management: list, cleanup, init, refine.

**Input Parameters**:
- `action` (optional): Explicit action - list, cleanup, init, refine (default: list)
- `task_description` (optional): Task description for new plan
- `issue_url` (optional): GitHub issue URL for new plan
- `plan_name` (optional): Plan name for specific operations

**Steps**:

### Step 1: Determine Action

```
If action = "cleanup":
    → Execute Operation: cleanup-plans

Else if action = "init":
    → Execute Operation: init-plan

Else if action = "refine":
    → Execute Operation: refine-plan

Else (default "list"):
    → Execute Operation: list-plans
```

### Step 2: Execute Action

**ACTION: list-plans**
1. Run `Operation: list-plans`
2. Display selection via `AskUserQuestion`:
   - Question: "Select a plan, or use 'Type something' to enter a new task description:"
   - Options: Each existing plan as an option, plus "Cleanup completed plans"
   - Note: The "Type something" option is auto-added by AskUserQuestion for free-text input
3. **Handle response** (CRITICAL - check response type FIRST):
   - **If "Type something" used with text**: IMMEDIATELY execute init-plan action with text as task_description. Do NOT show plan list or ask further questions.
   - **If "Cleanup completed plans" selected**: Execute cleanup-plans action
   - **If existing plan selected**: Show plan summary, then offer actions via AskUserQuestion:
     - "Execute" → invoke `/plan-execute plan={name}` (for execute/verify/finalize phases)
     - "Refine" → execute refine-plan action (for init/refine phases)
     - "Edit plan" → execute edit-plan action (behavior depends on current phase)
     - "Delete plan" → confirm deletion, then resolve script and execute deletion (see Scripts section)
     - Note: Show only relevant options based on phase:
       - init/refine phase: Show "Refine", "Edit plan", "Delete plan"
       - execute/verify/finalize phase: Show "Execute", "Edit plan", "Delete plan"

**ACTION: cleanup-plans**
1. Run `Operation: cleanup-plans`
2. If no completed plans: Display message, exit
3. Display numbered list of completed plans
4. Prompt for selection (all/numbers/cancel)
5. Show what will be deleted (see Scripts section for resolve pattern):
   ```
   Skill: cui-utilities:script-runner
   Resolve: cui-task-workflow:phase-management/scripts/delete-plan.py
   ```
   ```bash
   python3 {resolved_path} .claude/plans/{plan-name}/ --dry-run
   ```
6. Confirm deletion via AskUserQuestion
7. Execute deletion:
   ```bash
   python3 {resolved_path} .claude/plans/{plan-name}/
   ```
8. Report results

**ACTION: init-plan**
1. Requires task_description or issue_url (from command parameter or "Other" input from list-plans)
2. Delegate to `Skill: cui-task-workflow:plan-init` with task_description/issue_url
3. On success, prompt: "Continue with refine phase?"
4. If yes, execute refine-plan operation

**Note**: init-plan is always invoked with a task description. Users provide this via:
- Command parameter: `/plan-manage action=init task="..."`
- "Other" input from list-plans action

**ACTION: refine-plan**
1. If plan_name provided: Verify plan exists
2. Else: Run discover-plans --filter=init,refine
3. Display numbered list for selection
4. Delegate to `Skill: cui-task-workflow:plan-refine`
5. On completion, report status

**ACTION: edit-plan**
Handles plan editing based on current phase:

1. **Determine current phase** from plan.md
2. **Route based on phase**:

   **If phase is `init` or `refine`:**
   - Delegate directly to `Skill: cui-task-workflow:plan-refine`
   - This allows structured task editing, adding/removing tasks, updating requirements

   **If phase is `execute`, `verify`, or `finalize`:**
   - Warn user: "Plan is in {phase} phase. Editing may require re-verification."
   - Offer options via AskUserQuestion:
     - "Add task to current phase" → Allow adding a new task to the current phase section
     - "Go back to refine" → Reset phase to refine, delegate to plan-refine skill
     - "Cancel" → Return to plan selection
   - If "Add task":
     - Ask for task description via AskUserQuestion (use "Type something" for input)
     - Add task to current phase in plan.md using Edit tool
     - Update task count in Phase Progress table
   - If "Go back to refine":
     - Update plan.md: set `**Current Phase**: refine`
     - Delegate to `Skill: cui-task-workflow:plan-refine`

3. **Report result** after edit completes

---

## Workflow: Execute Plans

Invoked by `/plan-execute` command. Handles execution phases: implement/execute, verify, finalize.

**Note**: `implement` is used by Implementation plans (5-phase), `execute` is used by Simple plans (3-phase).

**Input Parameters**:
- `plan_name` (optional): Plan name to execute
- `explicit_phase` (optional): Force specific phase (implement/execute/verify/finalize)

**Steps**:

### Step 1: Select Plan

```
If plan_name provided:
    → Validate plan exists
    → Validate phase is executable (not init/refine)
    → Proceed to Step 2

Else:
    → Run Operation: discover-executable
    → Display numbered list via AskUserQuestion
    → User selects plan
    → Proceed to Step 2
```

### Step 2: Validate Phase

1. Read plan current phase
2. If phase is `init` or `refine`:
   - Return error: "Plan is in '{phase}' phase - use /plan-manage"
3. If explicit_phase provided:
   - Validate override is reachable from current state
   - If invalid, show error with valid targets

### Step 3: Execute Phase

1. Run `Operation: route-phase` to get target skill
2. Invoke target skill:
   - `implement` → `Skill: cui-task-workflow:plan-implement`
   - `verify` → `Skill: cui-task-workflow:plan-verify`
   - `finalize` → `Skill: cui-task-workflow:plan-finalize`

### Step 4: Handle Phase Completion

After phase skill returns:
1. Run `Operation: transition-phase` with completed phase
2. If plan complete: Display completion summary, suggest `/plan-manage action=cleanup`
3. Else: **Auto-continue** to next phase (no user prompt needed)
   - Display brief progress status
   - Loop back to Step 3

**Note**: Do NOT prompt user to continue between phases or between tasks. Plans execute continuously until:
- Plan is complete
- An error requires user decision
- User explicitly interrupts

---

## Operation: list-plans

Lists all plans with current phase and status.

**Input**: None

**Steps**:

1. **Run discovery script**:
   ```
   Skill: cui-utilities:script-runner
   Resolve: cui-task-workflow:phase-management/scripts/discover-plans.py
   ```
   ```bash
   python3 {resolved_path} .claude/plans/
   ```

2. **Format output for display**:
   ```
   Available Plans:

   1. jwt-authentication [implement] - 3/12 tasks complete
      Path: .claude/plans/jwt-authentication/
   2. user-profile-api [refine] - Requirements analysis
      Path: .claude/plans/user-profile-api/

   0. Create new plan
   ```

3. **Return data for AskUserQuestion**

**Output**:
```
plans_found[N]{name,path,phase,status}:
  {name},{path},{phase},{status}
  ...

recommendation: {name} (most recent activity)
```

---

## Operation: cleanup-plans

Finds completed plans for cleanup.

**Input**: None

**Steps**:

1. **Run filtered discovery**:
   ```
   Skill: cui-utilities:script-runner
   Resolve: cui-task-workflow:phase-management/scripts/discover-plans.py
   ```
   ```bash
   python3 {resolved_path} .claude/plans/ --filter=completed
   ```

2. **Return list of completed plans**

**Output**:
```
completed_plans[N]{name,path,completed_date}:
  {name},{path},{date}
  ...
```

---

## Operation: init-plan

Creates a new plan, checking for existing init-phase plans first.

**Input**: `task_description`, `issue_url` (optional)

**Steps**:

1. **Check for existing init-phase plans**:
   ```
   Skill: cui-utilities:script-runner
   Resolve: cui-task-workflow:phase-management/scripts/discover-plans.py
   ```
   ```bash
   python3 {resolved_path} .claude/plans/ --filter=init
   ```

2. **If init-phase plans exist**:
   - Return list for user selection
   - Option to continue existing or create new

3. **If creating new**:
   - Delegate to `Skill: cui-task-workflow:plan-init`
   - Return new plan path

**Output**:
```
existing_init_plans[N]{name,path}:
  {name},{path}

OR

new_plan_created:
  name: {name}
  path: {path}
```

---

## Operation: refine-plan

Finds plans ready for refinement or refines a specific plan.

**Input**: `plan_name` (optional)

**Steps**:

1. **If plan_name not provided**:
   ```
   Skill: cui-utilities:script-runner
   Resolve: cui-task-workflow:phase-management/scripts/discover-plans.py
   ```
   ```bash
   python3 {resolved_path} .claude/plans/ --filter=init,refine
   ```

2. **Return list of refinable plans** or specific plan

3. **Delegate to `Skill: cui-task-workflow:plan-refine`**

**Output**:
```
refine_candidates[N]{name,path,phase}:
  {name},{path},{phase}
```

---

## Operation: discover-executable

Finds plans ready for execution (implement/execute/verify/finalize phases).

**Input**: None

**Steps**:

1. **Run filtered discovery**:
   ```
   Skill: cui-utilities:script-runner
   Resolve: cui-task-workflow:phase-management/scripts/discover-plans.py
   ```
   ```bash
   python3 {resolved_path} .claude/plans/ --filter=implement,execute,verify,finalize
   ```

2. **Exclude completed plans from results**

3. **Format output for display**:
   ```
   Executable Plans:

   1. jwt-authentication [implement] - Task 3/12: "Add token validation"
      Path: .claude/plans/jwt-authentication/
   2. user-profile-api [verify] - Build verification pending
      Path: .claude/plans/user-profile-api/

   0. Exit (use /plan-manage to create or refine plans)
   ```

**Output**:
```
executable_plans[N]{name,path,phase,current_task}:
  {name},{path},{phase},{task}
  ...
```

---

## Operation: discover-plans

Finds available plans in the workspace.

**Input**: `search_path` (optional, default: `.claude/plans/`)

**Steps**:

1. **Run discovery script**:
   ```
   Skill: cui-utilities:script-runner
   Resolve: cui-task-workflow:phase-management/scripts/discover-plans.py
   ```
   ```bash
   python3 {resolved_path} {search_path}
   ```

2. **Parse JSON output**:
   - plans: Array of {name, path, phase, status}
   - recommendation: Most recent active plan

3. **Handle results**:
   - If 0 plans: Return empty list with suggestion
   - If 1 plan: Return with auto-select recommendation
   - If N plans: Return list for user selection

**Output**:
```
plans_found[N]{name,path,phase,status}:
  {name},{path},{phase},{status}
  ...

recommendation: {name} (most recent activity)
```

---

## Operation: route-phase

Determines which phase skill to invoke based on plan state.

**Input**: `plan_directory`, `explicit_phase` (optional override)

**Steps**:

1. **Read plan status**:
   ```
   Skill: cui-task-workflow:plan-files
   operation: read-plan
   plan_directory: {plan_directory}
   ```

2. **Run routing script**:
   ```
   Skill: cui-utilities:script-runner
   Resolve: cui-task-workflow:phase-management/scripts/route-phase.py
   ```
   ```bash
   python3 {resolved_path} {current_phase} {explicit_phase}
   ```

3. **Parse JSON output**:
   - target_skill: Skill to invoke
   - phase_info: Phase metadata
   - error: If override invalid

4. **Return routing decision**:
   - target_skill name
   - Phase context for skill invocation

**Output**:
```
routing:
  plan_directory: {path}
  current_phase: {phase}
  current_task: {task-id}
  target_skill: {plan-init|plan-refine|plan-implement|plan-verify|plan-finalize}

phase_status:
  completed_phases[N]: {list}
  current_phase: {phase}
  pending_phases[N]: {list}

tasks_remaining: {count}
```

---

## Operation: transition-phase

Handles phase completion and transition to next phase.

**Input**: `plan_directory`, `completed_phase`

**Steps**:

1. **Read plan to verify completion**:
   ```
   Skill: cui-task-workflow:plan-files
   operation: read-plan
   plan_directory: {plan_directory}
   ```

2. **Run transition script**:
   ```
   Skill: cui-utilities:script-runner
   Resolve: cui-task-workflow:phase-management/scripts/transition-phase.py
   ```
   ```bash
   python3 {resolved_path} {plan_directory} {completed_phase}
   ```

3. **Parse JSON output**:
   - from_phase, to_phase: Transition info
   - is_complete: True if plan finished
   - error: If transition invalid

4. **If valid transition, update plan**:
   ```
   Skill: cui-task-workflow:plan-files
   operation: update-progress
   plan_directory: {plan_directory}
   task_id: {last-task-of-phase}
   status: completed
   ```

5. **Return transition result**

**Output** (transition success):
```
transition:
  from_phase: {phase}
  to_phase: {phase}
  success: true

plan_status:
  current_phase: {new-phase}
  current_task: {first-task-of-new-phase}
  overall_progress: {percentage}%

next_action: Execute {phase} phase tasks
```

**Output** (plan complete):
```
transition:
  from_phase: finalize
  to_phase: none
  success: true
  plan_complete: true

plan_status:
  status: completed
  all_phases_complete: true

next_action: Plan completed - archive or close
```

---

## Operation: get-status

Returns comprehensive plan status for display.

**Input**: `plan_directory`

**Steps**:

1. **Run status script**:
   ```
   Skill: cui-utilities:script-runner
   Resolve: cui-task-workflow:phase-management/scripts/get-status.py
   ```
   ```bash
   python3 {resolved_path} {plan_directory}
   ```

2. **Parse JSON output**:
   - plan_status: Overall status
   - phase_progress: Per-phase metrics
   - current_focus: Active task
   - configuration: Plan config

3. **Format for display**

**Output**:
```
plan_status:
  name: {plan-name}
  plan_type: {implementation|simple}
  overall_status: {pending|in_progress|completed}
  overall_progress: {percentage}%

phase_progress[5]{phase,status,tasks,completed}:
  init,{status},{count},{n/m}
  refine,{status},{count},{n/m}
  implement,{status},{count},{n/m}
  verify,{status},{count},{n/m}
  finalize,{status},{count},{n/m}

current_focus:
  phase: {phase}
  task: {task-id}
  task_name: "{task-name}"

configuration:
  technology: {tech}
  build_system: {build}
  branch: {branch}
```

---

## Scripts

Python scripts for deterministic operations (output JSON). Use script-runner for portable path resolution.

### Script Notation

All scripts use portable notation: `cui-task-workflow:phase-management/scripts/{script-name}`

| Script | Notation | Purpose |
|--------|----------|---------|
| `discover-plans.py` | `cui-task-workflow:phase-management/scripts/discover-plans.py` | Find plans in workspace |
| `route-phase.py` | `cui-task-workflow:phase-management/scripts/route-phase.py` | Map phase to skill |
| `transition-phase.py` | `cui-task-workflow:phase-management/scripts/transition-phase.py` | Get next phase |
| `get-status.py` | `cui-task-workflow:phase-management/scripts/get-status.py` | Aggregate status |
| `delete-plan.py` | `cui-task-workflow:phase-management/scripts/delete-plan.py` | Delete plan safely |

### Resolving Scripts

Before running any script, resolve the path:
```
Skill: cui-utilities:script-runner
Resolve: cui-task-workflow:phase-management/scripts/{script-name}
```

Then use `{resolved_path}` in bash commands.

### Script Details

**1. discover-plans.py**: Finds plans in `.claude/plans/` directory
- **Input**: search_path (optional, default: `.claude/plans/`), --filter (optional)
- **Output**: JSON with plans array, recommendation, and filter info
- **Filter Options**:
  - Phases: `init`, `refine`, `implement`, `execute`, `verify`, `finalize`
  - Statuses: `completed`, `in_progress`, `pending`
  - Multiple: comma-separated (e.g., `--filter=implement,execute,verify,finalize`)
- **Note**: `implement` is for Implementation plans (5-phase), `execute` is for Simple plans (3-phase)
- **Usage** (after resolving):
  ```bash
  python3 {resolved_path} .claude/plans/
  python3 {resolved_path} .claude/plans/ --filter=init
  python3 {resolved_path} .claude/plans/ --filter=implement,execute,verify,finalize
  python3 {resolved_path} .claude/plans/ --filter=completed
  ```

**2. route-phase.py**: Maps current phase to target skill
- **Input**: current_phase, explicit_phase (optional)
- **Output**: JSON with target_skill, phase_info
- **Usage** (after resolving):
  ```bash
  python3 {resolved_path} implement
  python3 {resolved_path} implement verify  # with override
  ```

**3. transition-phase.py**: Determines next phase in sequence
- **Input**: plan_directory, completed_phase
- **Output**: JSON with from_phase, to_phase, is_complete
- **Usage** (after resolving):
  ```bash
  python3 {resolved_path} .claude/plans/my-task/ implement
  ```

**4. get-status.py**: Aggregates comprehensive plan status
- **Input**: plan_directory
- **Output**: JSON with plan_status, phase_progress, current_focus
- **Usage** (after resolving):
  ```bash
  python3 {resolved_path} .claude/plans/my-task/
  ```

**5. delete-plan.py**: Safely deletes a plan directory
- **Input**: plan_directory, --dry-run (optional)
- **Output**: JSON with deletion result
- **Safety Checks**:
  - Validates directory exists
  - Requires plan.md to confirm it's a plan
  - Only allows deletion within `.claude/plans/` hierarchy
- **Usage** (after resolving):
  ```bash
  python3 {resolved_path} .claude/plans/my-task/
  python3 {resolved_path} .claude/plans/my-task/ --dry-run
  ```

---

## Error Handling

### Plan Not Found

```
error:
  type: plan_not_found
  message: No plans found in {search_path}

suggestion: Create a new plan with /plan-manage action=init task="description"
```

### Invalid Phase Override

```
error:
  type: invalid_phase_override
  message: Cannot skip from '{current}' to '{requested}'
  reason: Must complete phases in order

current_state:
  phase: {current}
  tasks_remaining: {count}

suggestion: Complete {current} phase first
```

### Incomplete Phase

```
error:
  type: incomplete_phase
  message: Phase '{phase}' has incomplete tasks

incomplete_tasks[N]{id,name}:
  {task-id},{task-name}
  ...

suggestion: Complete tasks or mark as skipped
```

### Invalid Plan Directory

```
error:
  type: invalid_plan_directory
  message: Plan directory not found or missing required files
  path: {plan_directory}

missing_files[N]: {list}

suggestion: Verify path or create new plan
```

---

## Integration

### Skills Used
- **plan-files** - Read plan, config, references; update progress

### Skills Delegated To
- **plan-init** - Init phase execution
- **plan-refine** - Refine phase execution
- **plan-implement** - Implement phase execution
- **plan-verify** - Verify phase execution
- **plan-finalize** - Finalize phase execution

### Command Integration
- **/plan-manage** - Plan lifecycle management (list, cleanup, init, refine)
- **/plan-execute** - Plan execution (implement, verify, finalize phases)

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] All operations have clear input/output
- [x] Error handling for all scenarios
- [x] Python scripts for deterministic operations
- [x] Standards in standards/
- [x] Orchestration only - delegates phase work
- [x] Two workflows for two commands (Manage Plans, Execute Plans)
