# Simple Init

**Purpose**: Init phase implementation for lightweight workflows

**Output**: 3-phase plan (init→execute→finalize)

**Use Cases**:
- Documentation updates
- Configuration changes
- Quick fixes (even on main branch)
- Research/exploration tasks
- Plugin/skill documentation
- Non-code changes

---

## Properties

| Property | Required | Default | Auto-Detection |
|----------|----------|---------|----------------|
| Branch | Yes | Current or main | Auto-select |
| Build System | No | `none` | Optional scan |
| Technology | No | `none` | Derived from build |
| Compatibility | No | `breaking` | None |
| Commit Strategy | No | `fine-granular` | None |
| Finalizing | No | `commit-only` | None |

---

## Property Specifications

### Branch (Required)

**Detection**:
```bash
# Get current branch
branch=$(git branch --show-current)

# Use current if on specific branch, otherwise main/master
if [[ -n "$branch" ]]; then
    echo "$branch"
else
    # Fallback to default branch
    git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'
fi
```

**Logic**:
1. Get current branch name
2. If on any branch → use current (no validation)
3. If detached HEAD → use `main` or `master`

**Validation**: None - any branch allowed including `main`/`master`

**User Prompt**: Not needed - auto-selected

---

### Build System (Optional)

**Default**: `none`

**Values**:
| Value | Description | Technology |
|-------|-------------|------------|
| `maven` | Java/JVM with Maven | java |
| `gradle` | Java/JVM with Gradle | java |
| `npm` | JavaScript with npm | javascript |
| `npx` | JavaScript with npx scripts | javascript |
| `none` | No build system | none |

**Detection**: Optional - can use `builder:environment-detection` skill if user requests, otherwise defaults to `none`.

**Optional Detection via environment-detection**:
```toon
from: plan-init-skill
to: environment-detection-skill
handoff_id: env-001

operation: get-build-environment

next_action: Detect available build systems (optional)
```

**User Prompt** (when editing):
```
Select build system:

1. none (default)
   No build system needed

2. maven
   Java/JVM with Maven (pom.xml)

3. gradle
   Java/JVM with Gradle (build.gradle)

4. npm
   JavaScript with npm (package.json)

5. npx
   JavaScript with npx scripts

Select (1-5):
```

---

### Technology (Optional)

**Default**: `none`

**Derived from Build System** (via environment-detection if used):

The `builder:environment-detection` skill provides technology mapping when build system is detected:

| Build System | Technology |
|--------------|------------|
| maven | java |
| gradle | java |
| npm | javascript |
| npx | javascript |
| none | none |

**Values**:
- `java` - Java/JVM development
- `javascript` - JavaScript/TypeScript development
- `mixed` - Both Java and JavaScript
- `none` - No specific technology

**User Prompt** (when editing):
```
Select technology:

1. none (default)
   No specific technology stack

2. java
   Java/JVM development

3. javascript
   JavaScript/TypeScript development

4. mixed
   Both Java and JavaScript

Select (1-4):
```

---

### Compatibility (Optional)

**Default**: `breaking`

**Values**:
| Value | Description | Version Impact |
|-------|-------------|----------------|
| `breaking` | Breaking changes allowed | Major version bump |
| `deprecations` | Deprecate old, introduce new | Minor version bump |

**Rationale for `breaking` default**: Simple tasks typically involve documentation, config, or quick fixes where breaking changes are acceptable and don't require deprecation cycles.

**User Prompt** (when editing):
```
Select compatibility level:

1. breaking (default)
   Allow breaking changes
   → For docs, config, quick fixes

2. deprecations
   Deprecate old, introduce new alongside
   → For API-affecting changes

Select (1-2):
```

---

### Commit Strategy (Optional)

**Default**: `fine-granular`

**Values**:
| Value | Description | When to Commit |
|-------|-------------|----------------|
| `fine-granular` | Commit after each task | Most traceability |
| `phase-specific` | Commit after each phase | Moderate grouping |
| `complete` | Single commit at end | Least commits |

**User Prompt** (when editing):
```
Select commit strategy:

1. fine-granular (default)
   Commit after each completed task
   → Best traceability

2. phase-specific
   Commit at end of each phase
   → Fewer commits

3. complete
   Single commit when all done
   → Minimal commits

Select (1-3):
```

---

### Finalizing (Optional)

**Default**: `commit-only`

**Values**:
| Value | Description | Actions |
|-------|-------------|---------|
| `commit-only` | Just commit | Finalize tasks, commit changes |
| `manual-pr` | Optional PR | Create PR if requested |

**No Automatic PR**: Simple init does not trigger `/pr-fix` or automatic PR workflow.

**User Prompt** (when editing):
```
Select finalizing mode:

1. commit-only (default)
   Commit changes, no PR
   → For direct commits

2. manual-pr
   Create PR after commit
   → For optional review

Select (1-2):
```

---

## Prompting Standard

**ALWAYS use `AskUserQuestion` tool** for all user interactions during init phase:
- Confirmation dialogs
- Property editing (selection lists)
- Task description input

This ensures consistent UX and proper conversation flow.

---

## Init Phase Workflow

### Step 1: Quick Setup

**Minimal Gathering**:
```bash
# Only git branch needed
git branch --show-current
```

**From Command Parameters**:
```
Parse parameters:
- task → Task description (required)
- type → simple (already determined)
```

### Step 2: Apply Defaults

```python
config = {
    "type": "simple",
    "branch": detect_branch() or "main",
    "build_system": "none",
    "technology": "none",
    "compatibility": "breaking",
    "commit_strategy": "fine-granular",
    "finalizing": "commit-only"
}
```

### Step 3: Quick Confirmation

**Display Format** (via `AskUserQuestion`):
```
## Simple Task Configuration

**Branch**: main ✓
**Build System**: none
**Technology**: none
**Compatibility**: breaking
**Commit Strategy**: fine-granular
**Finalizing**: commit-only

Task: {task_description}

1. Proceed with this configuration
2. Edit settings
3. Cancel

Select (1-3):
```

**If user selects "Edit settings"**:
```
Which property to change?

1. Build System    - none | maven | gradle | npm | npx
2. Technology      - none | java | javascript | mixed
3. Compatibility   - breaking | deprecations
4. Commit Strategy - fine-granular | phase-specific | complete
5. Finalizing      - commit-only | manual-pr

Select (1-5):
```

Then show property-specific selection (see property sections above).

**Minimal Interaction**: Quick selection-based flow, no free-form input needed.

### Step 4: Persist and Proceed

**Write to plan.md header**:
```markdown
# Task Plan: {task_title}

**Status**: in_progress
**Current Phase**: init
**Current Task**: task-1
**Plan Type**: Simple

## Configuration

| Property | Value |
|----------|-------|
| Branch | {branch} |
| Build System | {build_system} |
| Technology | {technology} |
| Compatibility | {compatibility} |
| Commit Strategy | {commit_strategy} |
| Finalizing | {finalizing} |
```

**Transition**: Move directly to `refine` phase.

---

## Init Phase Tasks

```markdown
## Phase: init (in_progress)

### Task 1: Quick Setup
**Status**: [ ]
**Goal**: Minimal configuration with defaults

**Checklist**:
- [ ] Determine working branch (current or main)
- [ ] Apply simple init defaults
- [ ] Confirm task description

### Task 2: Persist and Proceed
**Status**: [ ]
**Goal**: Save minimal configuration and transition

**Checklist**:
- [ ] Write configuration to plan.md
- [ ] Create phase structure
- [ ] Transition to refine phase
```

---

## Init Output: Phase Structure

This init produces a streamlined phase structure (3 phases vs 5 for Implementation). When init completes, the following phases exist in plan.md:

```markdown
## Phase Progress Table

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | in_progress | 2 | 0 |
| execute | pending | {dynamic} | 0 |
| finalize | pending | 2 | 0 |

---

## Phase: init (in_progress)

### Task 1: Quick Setup
**Status**: [ ]
**Goal**: Minimal configuration with defaults

**Checklist**:
- [ ] Determine working branch (current or main)
- [ ] Apply simple init defaults
- [ ] Confirm task description

### Task 2: Persist and Proceed
**Status**: [ ]
**Goal**: Save minimal configuration and transition

**Checklist**:
- [ ] Write configuration to plan.md
- [ ] Create phase structure
- [ ] Transition to execute phase

---

## Phase: execute (pending)

{Tasks generated based on user task description}

**Template per task**:
### Task N: {Task Title}
**Status**: [ ]
**Goal**: {Goal description}

**Checklist**:
- [ ] {Action step 1}
- [ ] {Action step 2}
- [ ] Verify changes

---

## Phase: finalize (pending)

### Task 1: Review Changes
**Status**: [ ]
**Goal**: Verify all changes are complete

**Checklist**:
- [ ] Review modified files
- [ ] Check for unintended changes
- [ ] Confirm task completion

### Task 2: Commit
**Status**: [ ]
**Goal**: Commit changes to repository

**Checklist**:
- [ ] Stage changes
- [ ] Create descriptive commit message
- [ ] Push to remote (if applicable)
```

---

## Example Configuration

```markdown
## Configuration

| Property | Value |
|----------|-------|
| Branch | main |
| Build System | none |
| Technology | none |
| Compatibility | breaking |
| Commit Strategy | fine-granular |
| Finalizing | commit-only |
```

---

## Comparison with Implementation Init

| Aspect | Simple | Implementation |
|--------|--------|----------------|
| Phases | 3 (init→execute→finalize) | 5 (init→refine→implement→verify→finalize) |
| Total tasks | ~6 | ~18+ |
| Branch validation | None | Must not be main |
| Issue tracking | No | Recommended |
| Build system | `none` (optional) | Auto-detected |
| Technology | `none` (optional) | Derived |
| Compatibility | `breaking` | `deprecations` |
| PR workflow | No | Yes (`/pr-fix`) |
| User interaction | Minimal | Full confirmation |

---

## When to Use Simple vs Implementation

**Use Simple**:
- Documentation-only changes
- README updates
- Configuration file edits
- Quick exploration/research
- One-off fixes that don't need PR review

**Use Implementation**:
- Code changes requiring review
- Feature development
- Bug fixes with tests
- Changes needing CI/CD verification
- Multi-file refactoring

---

## Related

- [Handoff Protocol](handoff.md) - TOON incoming/outgoing specifications
- [Plan Types](../plan-types.md) - Init phase router
- [Implementation Init](implementation.md) - Full workflow alternative (5 phases)
- [Refine Phase](../plan-refine/refine.md) - Refine phase specification
- [Implement Phase](../plan-implement/implement.md) - Implement phase specification
- [Verify Phase](../plan-verify/verify.md) - Verify phase specification
- [Finalize Phase](../plan-finalize/finalize.md) - Finalize phase specification
- [Persistence](../plan-files/persistence.md) - File format specifications
- [Templates & Workflow](../templates-workflow.md) - Phase workflow details
- [environment-detection Skill](../../../../marketplace/bundles/builder/skills/environment-detection/SKILL.md) - Build system detection (optional)
