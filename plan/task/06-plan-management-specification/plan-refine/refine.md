# Refine Phase Specification

**Input**: Plan from init phase with configuration and initial structure

**Output**: Detailed implementation tasks with acceptance criteria and references

**Use Cases**:
- Breaking down GitHub issues into implementable units
- Creating detailed task checklists
- Identifying ADRs and interface specifications needed
- Establishing task dependencies and order

---

## Operations

The refine phase provides three core operations:

| Operation | Description | Output |
|-----------|-------------|--------|
| **analyze** | Break down requirements into components | Component list with relationships |
| **plan-tasks** | Create detailed implementation tasks | Tasks with acceptance criteria |
| **identify-docs** | Determine documentation needs | ADR and interface references |

---

## Prerequisites

Before refine phase can start:

1. **Init phase completed** - Plan created with configuration
2. **Plan file exists** - `.claude/plans/{task-name}/plan.md`
3. **References file exists** - `.claude/plans/{task-name}/references.md`
4. **Current phase is refine** - Either just transitioned from init or resuming

---

## Refine Phase Workflow

### Step 1: Read Context

**Load existing plan and references**:
```
Read plan.md:
- Configuration (from init phase)
- Issue reference (if provided)
- Initial tasks (from init phase)

Read references.md:
- Issue URL and details
- Branch information
- Any existing references
```

**From Issue** (if URL provided):
```
Fetch issue details via skill delegation:
- Title, description
- Acceptance criteria
- Labels, assignees
- Linked issues
```

### Step 2: Analyze Requirements

**Analysis Process**:
1. Identify functional components
2. Determine technical boundaries
3. Map dependencies between components
4. Estimate complexity per component

**User Confirmation** (via `AskUserQuestion`):
```
## Component Analysis

I've identified the following components:

1. **{Component A}**
   Scope: {description}
   Complexity: {low|medium|high}

2. **{Component B}**
   Scope: {description}
   Complexity: {low|medium|high}

3. **{Component C}**
   Scope: {description}
   Complexity: {low|medium|high}

Dependencies:
- Component B depends on Component A
- Component C can be parallel with A

Options:
1. Proceed with this analysis
2. Modify components (add/remove/change)
3. Request re-analysis with specific focus

Select (1-3):
```

### Step 3: Plan Implementation Tasks

**Task Generation Process**:
1. For each component, generate implementation tasks
2. Add standard checklist items per technology
3. Define acceptance criteria from requirements
4. Order by dependencies

**Task Structure**:
```markdown
### Task N: {Task Name}

**Phase**: implement
**Goal**: {What success looks like}

**References**:
- Issue: {Specific section/paragraph from issue}
- Specification: {Path to relevant spec, if any}
- Related Code: {Files/classes to reference}

**Acceptance Criteria**:
- {Specific, measurable criterion 1}
- {Specific, measurable criterion 2}

**Checklist**:
- [ ] Read and understand all references above
- [ ] If unclear, ask user for clarification (DO NOT guess)
- [ ] {Task-specific implementation step 1}
- [ ] {Task-specific implementation step 2}
- [ ] Implement unit tests (minimum 80% coverage)
- [ ] Run build to verify all tests pass
- [ ] Commit changes
```

**User Review** (via `AskUserQuestion`):
```
## Implementation Tasks

I've planned {N} implementation tasks:

| # | Task | Complexity | Dependencies |
|---|------|------------|--------------|
| 1 | {Task name} | {low|med|high} | none |
| 2 | {Task name} | {low|med|high} | Task 1 |
| 3 | {Task name} | {low|med|high} | Task 1, 2 |

Estimated total effort: {estimate based on complexity}

Options:
1. Proceed with these tasks
2. View task details (enter task number)
3. Modify tasks (add/remove/reorder)
4. Adjust granularity (split large / merge small)

Select (1-4):
```

**If user selects "View task details"**:
```
Which task number to view? (1-{N}):
```

Then display full task with all fields.

**If user selects "Modify tasks"**:
```
Modification options:

1. Add new task
2. Remove task (enter task number)
3. Reorder tasks
4. Modify specific task
5. Back to task list

Select (1-5):
```

**If user selects "Adjust granularity"**:
```
Granularity adjustment:

1. Split large task (enter task number)
   - Creates 2-3 smaller tasks from one large task

2. Merge small tasks (enter task numbers separated by comma)
   - Combines multiple small tasks into one

3. Auto-adjust (analyze and suggest)
   - Recommend splits for high-complexity tasks
   - Recommend merges for trivial tasks

4. Back to task list

Select (1-4):
```

### Step 4: Identify Documentation Needs

**Analysis Triggers**:

| Trigger | Document Type | Action |
|---------|---------------|--------|
| Architectural decision made | ADR | Create or link |
| New interface introduced | Interface | Create or link |
| External dependency added | References | Add to references.md |
| Technology choice made | ADR | Create or link |

**User Prompt for ADR** (via `AskUserQuestion`):
```
## Architecture Decision Required

The task involves: {decision description}

This appears to require an Architecture Decision Record.

Options:
1. Create new ADR
   - Will invoke adr-management skill
   - ADR will be linked to this plan

2. Link existing ADR
   - Enter ADR identifier (e.g., ADR-015)

3. Skip (no ADR needed)
   - Document decision in plan notes instead

Select (1-3):
```

**User Prompt for Interface** (via `AskUserQuestion`):
```
## Interface Specification Required

The task introduces: {interface description}

This appears to require an Interface Specification.

Options:
1. Create new Interface specification
   - Will invoke interface-management skill
   - Interface will be linked to this plan

2. Link existing Interface
   - Enter Interface identifier (e.g., IF-042)

3. Skip (no interface spec needed)
   - Document interface in code only

Select (1-3):
```

### Step 5: Persist and Transition

**Update plan.md**:
1. Add all implementation tasks to implement phase
2. Update Phase Progress Table
3. Set current_phase to `implement` (or stay in `refine` if more refinement needed)
4. Update current_task to first implement task

**Update references.md**:
1. Add any new ADR references
2. Add any new interface references
3. Add related code files identified during analysis

**Generate implementation-requirements.md** (runtime artifact):
See [Implementation Requirements Template](#implementation-requirements-template) below.

---

## Refine Phase Tasks

```markdown
## Phase: refine (in_progress)

### Task 1: Analyze Requirements
**Goal**: Break down task into implementable components

**Checklist**:
- [ ] Read issue/task requirements
- [ ] Identify functional components
- [ ] Map dependencies between components
- [ ] Confirm analysis with user

### Task 2: Plan Implementation Tasks
**Goal**: Create detailed task list for implement phase

**Checklist**:
- [ ] Generate tasks per component
- [ ] Define acceptance criteria
- [ ] Add standard checklists per technology
- [ ] Order by dependencies
- [ ] Review with user

### Task 3: Identify Documentation Needs
**Goal**: Determine ADRs and interfaces needed

**Checklist**:
- [ ] Check if ADR needed for architectural decisions
- [ ] Check if interface specs needed for new APIs
- [ ] Create or link required documentation
- [ ] Update references.md
```

---

## Prompting Standard

**ALWAYS use `AskUserQuestion` tool** for all user interactions during refine phase:
- Component analysis confirmation
- Task list review and modification
- Granularity adjustments
- Documentation needs decisions

This ensures consistent UX and proper conversation flow.

---

## Implementation Requirements Template

When refine phase completes, generate `.claude/plans/{task-name}/implementation-requirements.md`:

```markdown
# Implementation Requirements: {Task Title}

**Generated**: {date}
**Phase**: refine → implement transition

---

## Component Summary

| Component | Description | Complexity | Tasks |
|-----------|-------------|------------|-------|
| {Component A} | {scope} | {complexity} | {task-ids} |
| {Component B} | {scope} | {complexity} | {task-ids} |

---

## Implementation Tasks

### Task {N}: {Task Name}

**Dependencies**: {task-ids or "none"}

**Goal**:
{Clear description of what success looks like}

**Implementation Guidance**:
{Specific technical guidance for this task}

**Files to Create/Modify**:
- {file-path-1} - {description}
- {file-path-2} - {description}

**Acceptance Criteria**:
- [ ] {Criterion 1}
- [ ] {Criterion 2}

**Quality Requirements**:
- Test coverage: ≥80%
- Build status: passing
- Documentation: {required|optional}

---

[Repeat for all tasks...]

---

## Dependencies and Order

```
Task 1 (Foundation)
    ↓
Task 2 (Core Implementation)
    ↓
Task 3 ──┬── Task 4 (Parallel)
         │
Task 5 (Integration)
    ↓
Task 6 (Polish)
```

---

## References

### Documentation
- Issue: {issue-link}
- ADRs: {adr-list}
- Interfaces: {interface-list}

### Code References
- {path/to/file.java} - {description}
- {path/to/component/} - {description}

### External Resources
- {external-link} - {description}

---

## Quality Checklist

Before proceeding to implement phase:

- [ ] All tasks have clear goals
- [ ] All tasks have acceptance criteria
- [ ] Dependencies are correctly mapped
- [ ] Documentation references are complete
- [ ] Technology is correctly identified per task
- [ ] Complexity estimates are reasonable

---

**Generated by**: plan-refine skill
```

---

## Input/Output Summary

### Input

| Source | Data | Required |
|--------|------|----------|
| plan.md | Configuration, issue reference, init tasks | Yes |
| references.md | Issue URL, branch, existing refs | Yes |
| Issue URL | Title, description, acceptance criteria | If provided |
| User | Component confirmation, task review | Yes |

### Output

| Artifact | Location | Content |
|----------|----------|---------|
| Updated plan.md | `.claude/plans/{task}/plan.md` | Implementation tasks |
| Updated references.md | `.claude/plans/{task}/references.md` | ADR/interface refs |
| Implementation requirements | `.claude/plans/{task}/implementation-requirements.md` | Runtime artifact |

---

## Technology-Specific Standards

### For Java Tasks

**Standard Checklist Items**:
```markdown
- [ ] Follow CUI Java coding standards
- [ ] Add JavaDoc to public methods
- [ ] Implement unit tests (JUnit 5)
- [ ] Verify build via `maven-builder` agent
- [ ] Check coverage via `java-coverage-agent`
```

**Skill Delegation**: `cui-java-expert:java-implement-agent`

### For JavaScript Tasks

**Standard Checklist Items**:
```markdown
- [ ] Follow CUI JavaScript standards
- [ ] Add JSDoc to exported functions
- [ ] Implement unit tests (Jest)
- [ ] Verify build via `npm-builder` agent
- [ ] Check coverage via `js-generate-coverage` command
```

**Skill Delegation**: `cui-frontend-expert:npm-builder`

### For Mixed Tasks

**Standard Checklist Items**:
```markdown
- [ ] Follow technology-appropriate standards
- [ ] Add documentation per language
- [ ] Implement tests for both stacks
- [ ] Run both Maven and npm builds
- [ ] Check coverage ≥80% for both
```

---

## Error Handling

### Missing Issue Content

```
Issue URL provided but content could not be fetched.

Options:
1. Retry fetching issue
2. Enter issue details manually
3. Proceed without issue content

Select (1-3):
```

### Invalid References

```
Reference validation failed:
- ADR-015: Not found
- IF-042: File exists but format invalid

Options:
1. Create missing ADR (ADR-015)
2. Remove invalid references
3. Proceed anyway (mark as TODO)

Select (1-3):
```

### Incomplete Analysis

```
Analysis incomplete - some components unclear:
- Component B: Scope undefined

Options:
1. Define scope for Component B
2. Remove Component B from plan
3. Mark as TODO for later refinement

Select (1-3):
```

---

## Comparison with Init Phase

| Aspect | Init Phase | Refine Phase |
|--------|------------|--------------|
| **Focus** | Configuration and setup | Analysis and planning |
| **Input** | User task description | Init phase output |
| **Output** | Plan structure, configuration | Implementation tasks |
| **User Interaction** | Property selection | Component/task review |
| **Documentation** | references.md created | ADRs/interfaces identified |
| **Runtime Artifact** | None | implementation-requirements.md |

---

## Integration Points

### With plan-init

Refine phase receives:
- Configuration (technology, build system, compatibility)
- Issue reference
- Initial plan structure

### With plan-implement

Refine phase produces:
- Detailed implementation tasks
- Acceptance criteria
- Technology assignments
- Dependency order

### With adr-management

During refine phase:
- Check if ADRs exist
- Create new ADRs if needed
- Link ADRs to references.md

### With interface-management

During refine phase:
- Check if interfaces exist
- Create new interfaces if needed
- Link interfaces to references.md

---

## Related

- [Handoff Protocol](handoff.md) - TOON incoming/outgoing specifications
- [Plan Types](../plan-types.md) - Init phase router
- [Implementation Init](../plan-init/implementation.md) - Full workflow init
- [Simple Init](../plan-init/simple.md) - Lightweight init
- [Implement Phase](../plan-implement/implement.md) - Implement phase specification (follows refine)
- [Verify Phase](../plan-verify/verify.md) - Verify phase specification (follows implement)
- [Finalize Phase](../plan-finalize/finalize.md) - Finalize phase specification (follows verify)
- [Templates & Workflow](../templates-workflow.md) - Phase workflow details
- [Persistence](../plan-files/persistence.md) - File format specifications
