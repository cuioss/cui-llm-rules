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
   Skill: cui-task-workflow:plan-files
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
   Skill: cui-task-workflow:plan-files
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
   Skill: cui-task-workflow:plan-files
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
   Skill: cui-task-workflow:plan-files
   operation: write-plan
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
   Skill: cui-task-workflow:plan-files
   operation: write-references
   action: add
   reference_type: adr|interface
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

---

## Phase Transition

After all refine tasks complete:

```
Skill: cui-task-workflow:plan-files
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
