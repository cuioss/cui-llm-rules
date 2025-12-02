---
name: plan-refine
description: Refine phase skill for plan management. Analyzes requirements into components, creates detailed implementation tasks with acceptance criteria, and identifies documentation needs (ADRs, interfaces). Generates implementation-requirements.md artifact.
allowed-tools: Read, Write, Edit, Skill, AskUserQuestion
---

# Plan Refine Skill

**Role**: Second phase skill. Intelligent analysis phase that transforms requirements into actionable implementation tasks.

**Execution Pattern**: Analyze requirements → Identify components → Generate tasks → Identify documentation needs

**CRITICAL**: Use Python scripts via Bash for plan file updates (Edit/Write tools trigger permission prompts on `.plan/` directories).

## Standards (Load On-Demand)

### Architecture
```
Read standards/architecture.md
```
Contains: Core design principle, layered architecture, plan-type skills API, domain analysis skills, handoff protocol, component dependencies

### Workflow
```
Read standards/workflow.md
```
Contains: Phase overview, operations, component analysis, task planning, documentation triggers

### Artifact Templates (local)

| Template | Purpose |
|----------|---------|
| `templates/implementation-requirements.md` | Implementation requirements artifact |
| `templates/analysis.md` | Strategic analysis document (optional) |

### Plan-Type Skill API

All plan-type skills implement a uniform API. Query the skill for what you need:

```
Skill: planning:plan-type-{plan_type}
operation: {operation}
plan_id: {plan_id}
```

| Operation | Purpose | Used By |
|-----------|---------|---------|
| `get-phase-structure` | Returns phases and their tasks | plan-init |
| `generate-tasks` | **Writes tasks directly** to plan.md | plan-refine |
| `get-finalize-config` | Returns finalize behavior (commit, PR, etc.) | plan-execute |
| `get-next-phase` | Returns next phase in workflow | phase-management |

**Key Design**: `generate-tasks` writes directly to plan.md via scripts (no ping-pong between skills).

### Domain Analysis Skills

Component analysis is delegated to domain-specific skills:

| Plan Type | Analysis Skill |
|-----------|----------------|
| `plugin-development` | `cui-plugin-development-tools:plugin-analysis` |
| `java` | `cui-java-expert:java-analysis` |
| `javascript` | `cui-frontend-expert:js-analysis` |
| `simple` | N/A (tasks from description) |

**Analysis Flow**:
1. plan-refine delegates to domain analysis skill
2. Analysis skill returns `components[]` with metadata
3. plan-refine passes components to plan-type skill's `generate-tasks`
4. plan-type skill writes tasks directly to plan.md

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

**Input**: `plan_id`

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
   Extract: `plan_type`, `task_description`, `technology`, `build_system`

3. **Fetch issue** (if URL): `gh issue view {number} --json title,body,labels`

4. **Delegate to domain analysis skill** based on plan_type:

   **For plugin-development**:
   ```
   Skill: cui-plugin-development-tools:plugin-analysis
   operation: analyze
   plan_id: {plan_id}
   task_description: {task_description}
   issue_context: {issue_body}
   ```

   **For java**:
   ```
   Skill: cui-java-expert:java-analysis
   operation: analyze
   plan_id: {plan_id}
   task_description: {task_description}
   issue_context: {issue_body}
   build_system: maven|gradle
   ```

   **For javascript**:
   ```
   Skill: cui-frontend-expert:js-analysis
   operation: analyze
   plan_id: {plan_id}
   task_description: {task_description}
   issue_context: {issue_body}
   build_system: npm
   ```

   **For simple**: Skip analysis, derive single component from task description.

5. **Receive components** from domain analysis skill:
   ```yaml
   components:
     - name: "{component-name}"
       type: "{type}"
       scope: "create|modify|refactor"
       path: "{relative-path}"
       dependencies: [...]
       complexity: "low|medium|high"
   ```

6. **Present analysis** (AskUserQuestion):
   - Component list with scope and complexity
   - Dependency mapping
   - Options: Proceed / Modify / Re-analyze

7. **Update progress** (after user approval):
   ```bash
   python3 {update-progress.py} --plan-dir .plan/plans/{plan_id} --phase refine --task-id task-1 --complete-items "Analyze requirements"
   ```

**Output**: `components[]` ready for generate-tasks

---

## Operation: plan-tasks

**Input**: `plan_id`, `components[]`

**Steps**:

1. **Read plan_type from config**:
   ```
   Skill: planning:plan-files
   operation: read-config → get plan_type
   ```

2. **Present task preview** (AskUserQuestion):
   - Component list with planned task types
   - Options: Proceed / Modify / Adjust granularity

3. **Call plan-type skill to generate and write tasks**:
   ```
   Skill: planning:plan-type-{plan_type}
   operation: generate-tasks
   plan_id: {plan_id}
   components: {components from analyze operation}
   ```

   The plan-type skill:
   - Generates tasks based on component types
   - Writes tasks directly to plan.md via scripts
   - Returns confirmation with task count

4. **Receive confirmation**:
   ```yaml
   generate_tasks_result:
     status: success
     tasks_written: {count}
     plan_file: .plan/plans/{plan_id}/plan.md
   ```

5. **Log task planning**:
   ```
   Skill: planning:work-log
   operation: log-entry
   plan_directory: .plan/plans/{plan_id}
   phase: refine
   task: task-2
   action: "Generated implementation tasks"
   result: "{count} tasks planned"
   ```

6. **Update progress**:
   ```bash
   python3 {update-progress.py} --plan-dir .plan/plans/{plan_id} --phase refine --task-id task-2 --complete-items "Plan implementation tasks"
   ```

**Output**: `generate_tasks_result` with task count and confirmation

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

**Planning Bundle**:
- **plan-files** - All file I/O operations
- **plan-type-simple** - Task generation for simple plans
- **plan-type-plugin** - Task generation for plugin plans
- **plan-type-java** - Task generation for Java plans
- **plan-type-javascript** - Task generation for JavaScript plans
- **phase-management** - Orchestration (invokes this skill)
- **work-log** - Logging significant actions

**Domain Analysis** (delegated):
- **cui-plugin-development-tools:plugin-analysis** - Plugin component analysis
- **cui-java-expert:java-analysis** - Java component analysis
- **cui-frontend-expert:js-analysis** - JavaScript component analysis

**Documentation**:
- **adr-management** - ADR creation and verification
- **interface-management** - Interface creation and verification

### Related Skills
- **plan-init** - Previous phase
- **plan-execute** - Execution phases (implement/verify/finalize)

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] Progressive disclosure (load on-demand)
- [x] All file I/O delegated to plan-files skill
- [x] User confirmation for all decisions
- [x] Implementation requirements artifact generated

