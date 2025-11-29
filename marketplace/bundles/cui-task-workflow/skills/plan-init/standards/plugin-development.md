# Plugin Development Init Standards

**Output**: 3-phase plan (init→execute→finalize)

**Use Cases**:
- Creating new marketplace components (agents, commands, skills)
- Updating existing marketplace components
- Plugin maintenance and refactoring
- Bundle restructuring

## Key Difference from Simple Plan

**Mandatory Verification**: Every component added or modified in the execute phase MUST have a corresponding verification task using `/plugin-doctor` before finalization.

## Phase Structure Template

When creating a plugin-development plan, generate this structure:

```markdown
# Task Plan: {task_title}

**Configuration**: See [config.toon](./config.toon)
**References**: See [references.md](./references.md)

**Current Phase**: init
**Current Task**: task-1

---

## Phase Progress

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | in_progress | 2 | 0/2 |
| execute | pending | 0 | 0/0 |
| finalize | pending | 3 | 0/3 |

---

## Phase: init (in_progress)

### Task 1: Detect Environment

**Phase**: init
**Goal**: Gather marketplace and plugin context

**Acceptance Criteria**:
- Current branch identified
- Target bundle identified
- Component types to add/modify identified

**Checklist**:
- [ ] Check current git branch
- [ ] Identify target bundle(s) in marketplace/bundles/
- [ ] List components to add or modify
- [ ] Verify plugin.json exists for target bundle

### Task 2: Confirm Configuration

**Phase**: init
**Goal**: Quick confirmation of defaults

**Acceptance Criteria**:
- User has confirmed settings
- Component scope is clear

**Checklist**:
- [ ] Display detected configuration
- [ ] List components to be created/modified
- [ ] Confirm component naming conventions
- [ ] Transition to execute phase

---

## Phase: execute (pending)

{Tasks generated from task description}

**IMPORTANT**: After all implementation tasks, add verification sub-tasks:

For each component added/modified, add a verification task:
- **verify-{component-type}-{component-name}**: Run `/plugin-doctor {component-type}={component-name}`

---

## Phase: finalize (pending)

### Task 1: Verify All Components

**Phase**: finalize
**Goal**: Run plugin-doctor on all added/modified components

**Acceptance Criteria**:
- All components pass plugin-doctor checks
- No critical issues remaining

**Checklist**:
- [ ] For each added/modified agent: `/plugin-doctor agent={name}`
- [ ] For each added/modified command: `/plugin-doctor command={name}`
- [ ] For each added/modified skill: `/plugin-doctor skill={name}`
- [ ] Address any reported issues
- [ ] Re-run until clean

### Task 2: Commit Changes

**Phase**: finalize
**Goal**: Commit all changes

**Acceptance Criteria**:
- All changes committed
- Commit message follows conventions

**Checklist**:
- [ ] Stage all changes
- [ ] Create commit with descriptive message
- [ ] Push to branch (if remote)

### Task 3: Verify Completion

**Phase**: finalize
**Goal**: Ensure task is complete

**Acceptance Criteria**:
- All acceptance criteria met
- Plugin-doctor passes on all components

**Checklist**:
- [ ] Verify all components created/modified
- [ ] Verify plugin.json updated if needed
- [ ] Mark plan complete

---

## Completion Criteria

All phases must be completed and all tasks marked with `[x]` before plan is complete.

**Plugin-Development Specific Requirements**:
- [ ] All added/modified components verified with `/plugin-doctor`
- [ ] No Rule 6 violations (Task tool in agents)
- [ ] No Rule 7 violations (Maven usage)
- [ ] No Rule 0 violations (thin wrapper commands)
- [ ] All components have proper frontmatter
```

## Config Format (TOON)

```toon
# Plan Configuration

plan_type: plugin-development
branch: {branch-name}
issue: none

technology: none
build_system: none

compatibility: breaking
commit_strategy: fine-granular
finalizing: commit-only

# Plugin-specific
target_bundle: {bundle-name}
component_types: {agents, commands, skills}
```

## References Template

```markdown
# References

## Context

**Branch**: `{branch}`
**Target Bundle**: `{bundle-name}`

## Components

**Components to Add**:
- (populated during execute phase)

**Components to Modify**:
- (populated during execute phase)

## Related Files

**Bundle Path**: marketplace/bundles/{bundle-name}/
**Plugin Config**: marketplace/bundles/{bundle-name}/plugin.json

## Verification Commands

**After completing execute phase, run these verifications**:

```bash
# For agents
/plugin-doctor agent={name}

# For commands
/plugin-doctor command={name}

# For skills
/plugin-doctor skill={name}

# For full bundle
/plugin-doctor metadata
```

## Notes

(add any relevant notes)
```

## Execute Phase Task Generation

When generating execute phase tasks for plugin development:

### For Adding New Components

```markdown
### Task N: Create {component-type} {component-name}

**Phase**: execute
**Goal**: Create new {component-type} following standards

**Acceptance Criteria**:
- {component-type} file created in correct location
- Frontmatter complete and valid
- Content follows {component-type} template

**Checklist**:
- [ ] Create {path}
- [ ] Add required frontmatter (name, description, allowed-tools)
- [ ] Implement required sections
- [ ] **Verify**: `/plugin-doctor {component-type}={component-name}`
```

### For Modifying Existing Components

```markdown
### Task N: Update {component-type} {component-name}

**Phase**: execute
**Goal**: Apply changes to existing {component-type}

**Acceptance Criteria**:
- Changes applied correctly
- No new violations introduced

**Checklist**:
- [ ] Read current content
- [ ] Apply required modifications
- [ ] Preserve existing valid structure
- [ ] **Verify**: `/plugin-doctor {component-type}={component-name}`
```

## Verification Task Template

Add this task after each implementation task:

```markdown
### Task N+1: Verify {component-name}

**Phase**: execute
**Goal**: Ensure component passes quality checks

**Acceptance Criteria**:
- No critical issues
- All safe fixes auto-applied
- No risky fixes pending (or addressed)

**Checklist**:
- [ ] Run `/plugin-doctor {type}={name}`
- [ ] Review any reported issues
- [ ] Fix issues if found
- [ ] Re-verify until clean
```

## Key Differences from Simple and Implementation

| Aspect | Simple | Implementation | Plugin-Development |
|--------|--------|----------------|-------------------|
| Phases | 3 | 5 | 3 |
| Branch | Any | Feature branch | Any |
| Issue | Not used | Recommended | Not used |
| Build System | None | Auto-detect | None |
| PR Workflow | No | Yes | No |
| **Verification** | Basic | Build + Tests | `/plugin-doctor` |
| **Component Tracking** | No | No | Yes |
| Total Tasks | ~6 | ~18+ | ~6 + N (per component) |

## Auto-Detection Criteria

Use plugin-development plan type when:
1. Task involves marketplace components (agents, commands, skills)
2. Path contains `marketplace/bundles/`
3. Task mentions "plugin", "component", "agent", "command", or "skill" creation/modification
4. Branch starts with `plugin/`, `component/`, or similar
