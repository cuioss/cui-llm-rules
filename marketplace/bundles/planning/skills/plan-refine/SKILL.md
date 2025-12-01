---
name: plan-refine
description: Refine phase skill for plan management. Analyzes requirements into components, creates detailed implementation tasks with acceptance criteria, and identifies documentation needs (ADRs, interfaces). Generates implementation-requirements.md artifact.
allowed-tools: Read, Write, Edit, Skill, AskUserQuestion
---

# Plan Refine Skill

**EXECUTION MODE**: Execute refine operations immediately. Do not explain or summarize.

**OUTPUT RULES**:
- Do NOT narrate internal process or tool invocations
- Do NOT display raw script output - format as structured status
- DO show task analysis results and requirement confirmations
- Work silently until you have results to display

**Role**: Second phase skill in the plan management system. Breaks down requirements into implementable tasks with acceptance criteria. Delegates all file I/O to `plan-files` skill.

**AUTO-CONTINUE BEHAVIOR**: Execute all refine operations continuously without unnecessary user prompts. Only stop for:
- Analysis review (if analysis.md is created for complex tasks)
- Component analysis confirmation (brief approval of identified components)
- Task list approval (brief approval of generated tasks)
Do NOT prompt between operations or for routine confirmations.

**MANDATORY PROGRESS TRACKING**:

After completing each refine task, you MUST call update-progress:
```
python3 {update-progress.py} --plan-dir {plan_directory} --phase refine --task-id {task_id} --complete-items "{item_text}"
```

**NEVER skip this step**. The plan.md is the source of truth. Phase transitions WILL FAIL with `incomplete_phase` error if checklist items are not marked as `[x]`.

**Anti-Patterns** (DO NOT DO):
- Completing analysis without updating progress
- Generating tasks without marking progress
- Assuming plan.md auto-updates on operations

**MANDATORY WORK-LOG**:

After completing significant actions, you MUST log via work-log skill:
```
Skill: planning:work-log
operation: log-entry
plan_directory: {plan_directory}
phase: refine
task: {task_id}
action: "{what was done}"
result: "{outcome or artifact}"
```

**Entry Budget**: 1-2 entries for refine phase.

**Log Points**:
- Analysis complete (if analysis.md created): action="Completed strategic analysis", result="analysis.md"
- Requirements generated: action="Generated implementation tasks", result="{count} tasks planned"

**Anti-Patterns** (DO NOT DO):
- Completing refine without any work-log entries
- Logging each component analysis step

**CRITICAL CONSTRAINT - NO EDIT/WRITE TOOLS FOR PLAN FILES**:
- NEVER use Edit or Write tools directly on plan files (plan.md, config.toon, references.toon)
- **WHY**: Edit/Write tools ALWAYS trigger user permission prompts for `.plan/` directories - this is a security feature that CANNOT be bypassed regardless of settings.json permissions
- ALWAYS use Python scripts via Bash for plan file modifications
- Python scripts via Bash can write to plan storage WITHOUT prompts

| Operation | Wrong (triggers prompt) | Correct (no prompt) |
|-----------|------------------------|---------------------|
| Progress update | `Edit` on plan.md | `update-progress.py` via Bash |
| Write plan | `Write` to plan.md | `write-plan.py` via Bash |
| Update config | `Edit` on config.toon | `write-config.py` via Bash |

## Standards (Load On-Demand)

### Workflow
```
Read standards/workflow.md
```
Contains: Phase overview, operations, component analysis, task planning, documentation triggers

### Templates

| Template | Purpose |
|----------|---------|
| `templates/implementation-requirements.md` | Implementation requirements artifact |
| `templates/analysis.md` | Strategic analysis document (optional) |

---

## Operation: detect-complexity

**Input**: `plan_directory`

**Purpose**: Evaluate task complexity to determine if strategic analysis.md is needed before component breakdown.

**Detection Criteria**:

| Question | If YES → Create analysis.md |
|----------|----------------------------|
| Are multiple skills/components affected? | Yes |
| Are there breaking changes? | Yes |
| Are there architectural decisions (not just code changes)? | Yes |
| Are there complex dependencies to understand first? | Yes |
| Are there risks that need documentation? | Yes |

**Decision Logic**: If ALL answers are NO → Skip analysis.md and proceed directly to component breakdown. If ANY answer is YES → Create analysis.md.

**Steps**:

1. **Read plan context**:
   ```
   Skill: planning:plan-files
   operation: read-plan, read-config
   ```

2. **Evaluate complexity factors**:
   - Check task scope (single vs multiple components)
   - Check for breaking change indicators
   - Check for architectural keywords (design, architecture, pattern, migration)
   - Check for dependency complexity
   - Check for risk indicators

3. **Return decision** (do NOT prompt user - auto-decide):

**Output**:
```
complexity_assessment:
  needs_analysis: true|false
  complexity_factors:
    - {factor1}
    - {factor2}
  recommendation: "Create analysis.md" | "Skip to component breakdown"
```

**Auto-Continue**: This operation does NOT prompt the user. It makes the decision automatically and proceeds.

---

## Operation: create-analysis

**Input**: `plan_directory`, `complexity_factors`

**Purpose**: Create and populate analysis.md for complex tasks.

**Steps**:

1. **Read template**: `Read templates/analysis.md`

2. **Explore codebase** to gather information for each section:
   - Current State: Search for existing implementations
   - Affected Components: Identify files/modules that will change
   - Design Decisions: Document key choices being made
   - Breaking Changes: Identify any compatibility impacts
   - Risks: Assess potential issues

3. **Write analysis.md**: `Write {plan_directory}/analysis.md`

4. **Present to user for review** (AskUserQuestion):
   - Show analysis summary
   - Options: Approve / Edit / Add details
   - This is the ONLY user prompt in the analysis flow

5. **Update references**:
   ```
   Skill: planning:plan-files
   operation: write-references
   action: add
   section: implementation_files
   value: {plan_directory}/analysis.md
   ```

**Output**:
```
analysis_created:
  file: {plan_directory}/analysis.md
  sections_populated: [current_state, affected_components, design_decisions, risks, success_criteria]
  user_approved: true
```

6. **Log analysis creation**:
   ```
   Skill: planning:work-log
   operation: log-entry
   plan_directory: {plan_directory}
   phase: refine
   task: task-1
   action: "Completed strategic analysis"
   result: "analysis.md created"
   ```

---

## Operation: analyze

**Input**: `plan_directory`

**Steps**:

1. **Detect complexity first**:
   ```
   Execute Operation: detect-complexity
   ```
   - If `needs_analysis: true` → Execute Operation: create-analysis before continuing
   - If `needs_analysis: false` → Skip to step 2

2. **Read context**:
   ```
   Skill: planning:plan-files
   operation: read-plan, read-config, get-references
   ```

3. **Fetch issue** (if URL): `gh issue view {number} --json title,body,labels`

4. **Identify components**:
   - Functional components (features, APIs, services)
   - Technical boundaries (modules, packages, layers)
   - Dependencies between components
   - Complexity estimates (low/medium/high)

4. **Present analysis** (AskUserQuestion):
   - Component list with scope and complexity
   - Dependency mapping
   - Options: Proceed / Modify / Re-analyze

5. **Update progress** (after user approval):
   ```bash
   python3 {update-progress.py} --plan-dir {plan_directory} --phase refine --task-id task-1 --complete-items "Analyze requirements"
   ```

**Output**: `components[N]: {name, scope, complexity, dependencies}`

---

## Operation: plan-tasks

**Input**: `plan_directory`, `components`

**Steps**:

1. **Generate tasks per component**:
   - Create implementation task(s)
   - Add technology-specific checklist (see `standards/workflow.md`)
   - Define acceptance criteria
   - Add quality checklist items

2. **Order by dependencies**

3. **Present task list** (AskUserQuestion):
   - Task table with complexity and dependencies
   - Options: Proceed / View details / Modify / Adjust granularity

4. **Add tasks to plan**:
   ```
   Skill: planning:plan-files
   operation: write-plan
   ```

5. **Log task planning**:
   ```
   Skill: planning:work-log
   operation: log-entry
   plan_directory: {plan_directory}
   phase: refine
   task: task-2
   action: "Generated implementation tasks"
   result: "{count} tasks planned"
   ```

6. **Update progress**:
   ```bash
   python3 {update-progress.py} --plan-dir {plan_directory} --phase refine --task-id task-2 --complete-items "Plan implementation tasks"
   ```

**Output**: `tasks[N]: {id, name, complexity, dependencies, acceptance_criteria}`

---

## Operation: identify-docs

**Input**: `plan_directory`, `tasks`

**Steps**:

1. **Analyze for ADR needs** (architectural decisions, security, integration, performance)

2. **Prompt for ADR** (AskUserQuestion):
   - Create new ADR (invoke adr-management)
   - Link existing ADR
   - Skip

3. **Analyze for interface needs** (new APIs, service interfaces, external integrations)

4. **Prompt for interface** (AskUserQuestion):
   - Create new Interface (invoke interface-management)
   - Link existing Interface
   - Skip

5. **Update references**:
   ```
   Skill: planning:plan-files
   operation: write-references
   action: add
   reference_type: adr|interface
   ```

6. **Update progress**:
   ```bash
   python3 {update-progress.py} --plan-dir {plan_directory} --phase refine --task-id task-3 --complete-items "Identify documentation needs"
   ```

**Output**: `adrs_linked[N]`, `interfaces_linked[N]`

---

## Generate Implementation Requirements

After all refine tasks complete:

1. **Read template**: `Read templates/implementation-requirements.md`

2. **Populate**:
   - Component summary table
   - Task details with acceptance criteria
   - Dependency graph
   - Quality gates

3. **Write**: `Write {plan_directory}/implementation-requirements.md`

4. **Log requirements generation**:
   ```
   Skill: planning:work-log
   operation: log-entry
   plan_directory: {plan_directory}
   phase: refine
   task: task-3
   action: "Created implementation requirements"
   result: "implementation-requirements.md"
   ```

---

## Phase Transition

After all refine tasks complete:

```
Skill: planning:plan-files
operation: update-progress
plan_directory: {plan_directory}
task_id: {last-refine-task}
status: completed
```

This updates: current_phase → implement, current_task → first implement task

---

## Error Handling

### Missing Issue Content
Options: Retry / Enter manually / Proceed without

### Invalid References
Options: Create missing / Remove reference / Mark as TODO

### Incomplete Analysis
Options: Define scope / Remove component / Mark as TODO

---

## Integration

### Command Integration
- **/plan-manage** - Primary command invoking this skill via phase-management (action=refine)

### Skills Used
- **plan-files** - All file I/O operations
- **adr-management** - ADR creation and verification
- **interface-management** - Interface creation and verification
- **phase-management** - Orchestration (invokes this skill)
- **work-log** - Logging significant actions

### Related Skills
- **plan-init** - Previous phase
- **plan-implement** - Next phase
- **plan-verify** - Verification phase
- **plan-finalize** - Finalization phase

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] Progressive disclosure (load on-demand)
- [x] All file I/O delegated to plan-files skill
- [x] User confirmation for all decisions
- [x] Implementation requirements artifact generated

---

## Continuous Improvement

**MANDATORY**: When executing scripts from this skill, unexpected behavior or errors MUST be documented as lessons learned immediately.

### When to Document

File a lesson learned when a script:
- Returns unexpected output
- Fails to update files as expected
- Requires a workaround to achieve the desired result
- Has unclear or misleading documentation

### How to Document

Use the `general-tools:manage-lessons-learned` skill:
```bash
python3 {write-lesson.py path} --component "planning:plan-refine" --category {bug|improvement|anti-pattern} --title "Brief description" --detail "What happened, why, workaround, suggested fix"
```

**Categories**:
- `bug`: Script is broken or produces wrong results
- `improvement`: Script works but could be better
- `anti-pattern`: Script was misused or documentation unclear

**Why This Matters**: Script errors indicate gaps in validation, documentation, or implementation. Documented lessons improve future sessions and identify systemic issues.
