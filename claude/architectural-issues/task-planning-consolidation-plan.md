# Task Planning Consolidation Plan

**Status:** AWAITING USER APPROVAL - DO NOT IMPLEMENT

**Date:** 2025-11-10

**Objective:** Consolidate all task list/plan structures into one authoritative skill for creating plans and task documents

---

## Executive Summary

Currently, task planning and tracking is documented in three different locations with overlapping but distinct purposes:

1. **planning-documentation.md** (cui-requirements) - Long-term project planning documents
2. **task-breakdown-agent.md** (cui-workflow) - Short-term issue implementation plans
3. **refactoring-process.adoc** (standards/process) - Categorized refactoring task lists

**Proposal:** Create ONE authoritative skill `cui-task-planning` in the cui-workflow bundle that consolidates all task planning standards and serves all three use cases.

---

## Analysis of Current Structures

### Structure 1: planning-documentation.md (cui-requirements skill)

**Purpose:** Long-term project planning and progress tracking

**Format:** AsciiDoc (`doc/TODO.adoc`, `doc/ROADMAP.adoc`, `doc/BACKLOG.adoc`)

**Key Features:**
- Hierarchical organization by functional area/component/feature/phase
- 4 status indicators: `[ ]` (not started/in progress), `[x]` (completed), `[~]` (partially completed), `[!]` (blocked)
- Strong traceability to Requirements.adoc and specifications
- Task notes and implementation details
- Testing tasks organized separately
- Comprehensive example (500+ lines)

**Strengths:**
- Excellent for large-scale project tracking
- Strong requirements traceability
- Clear separation of concerns (implementation vs testing vs documentation)
- Well-suited for multi-month/multi-year projects

**Limitations:**
- Heavy structure for small tasks
- AsciiDoc format (less common in agents)
- No task identifiers for direct reference

### Structure 2: task-breakdown-agent.md (cui-workflow agent)

**Purpose:** Short-term implementation plans for single GitHub issues

**Format:** Markdown (`plan-issue-4.md`)

**Key Features:**
- Sequential numbered tasks (Task 1, Task 2, ...)
- Each task has: Goal, References, Checklist, Acceptance Criteria
- 2 status indicators: `[ ]` (incomplete), `[x]` (complete)
- Emphasis on ONE task at a time (sequential execution)
- Links to GitHub issues and specifications
- Built-in verification checklist per task
- Agent-friendly (designed for task-executor consumption)

**Strengths:**
- Perfect for single-issue implementation
- Clear sequential workflow
- Agent-consumable format
- Strong acceptance criteria
- Verification-first mindset

**Limitations:**
- No task identifiers (can't reference "Task 3" in commit)
- No priority field
- Limited to single-issue scope
- No categorization

### Structure 3: refactoring-process.adoc (standards/process, to be migrated)

**Purpose:** Categorized refactoring and improvement task tracking

**Format:** AsciiDoc (referenced in Refactorings.adoc)

**Key Features:**
- Category-based task identifiers (C1, P2, S3, T4, D5, DOC6, F7)
- Categories: Code (C), Performance (P), Security (S), Testing (T), Dependency (D), Documentation (DOC), Future (F)
- Explicit Priority field (High/Medium/Low)
- Includes Description + Rationale for each task
- 2 status indicators: `[ ]` (incomplete), `[x]` (complete)
- Commit message integration ("refactor: C1. Document Bouncy Castle Usage")

**Strengths:**
- Excellent categorization for improvement tracking
- Task identifiers enable direct reference
- Priority field for planning
- Rationale provides context
- Commit message integration

**Limitations:**
- Limited to refactoring context
- No acceptance criteria
- No checklist
- No references to requirements/specs

---

## Commonalities Across All Three

1. **Checkbox status tracking** - All use checkboxes for status
2. **Traceability emphasis** - All link to requirements, specs, or issues
3. **Progress tracking** - All support tracking completion
4. **Actionable tasks** - All focus on implementable work items
5. **AsciiDoc or Markdown** - All use standard markup formats

---

## Key Differences

| Aspect | planning-documentation | task-breakdown-agent | refactoring-process |
|--------|------------------------|----------------------|---------------------|
| **Time Horizon** | Long-term (months/years) | Short-term (days/weeks) | Ongoing (continuous) |
| **Scope** | Project-wide | Single issue | Improvement-focused |
| **Organization** | Hierarchical by area | Sequential by dependency | Categorized by type |
| **Task IDs** | None | None (Task 1, 2, ...) | Category-based (C1, P2) |
| **Priority** | Optional (in notes) | Not present | Explicit (H/M/L) |
| **Status Types** | 4 types ([ ], [x], [~], [!]) | 2 types ([ ], [x]) | 2 types ([ ], [x]) |
| **Format** | AsciiDoc | Markdown | AsciiDoc |
| **Acceptance Criteria** | No | Yes (per task) | No |
| **Checklist** | Implicit | Explicit | No |
| **Rationale** | In notes | No | Yes |

---

## Consolidation Strategy

### Approach: ONE Authoritative Skill with Multiple Use Cases

Create a single skill `cui-task-planning` that defines standards for ALL task planning scenarios:

1. **Project Planning** (replaces planning-documentation.md)
2. **Issue Implementation** (enhances task-breakdown-agent.md)
3. **Refactoring Tracking** (migrates refactoring-process.adoc)

### Skill Structure

**Bundle:** `cui-workflow` (fits workflow mission better than cui-requirements)

**Skill name:** `cui-task-planning`

**Description:** "Comprehensive task planning and tracking standards for project planning, issue implementation, and refactoring workflows"

**Standards Files:**
```
standards/
  task-planning-core.md           # Core concepts, principles, common elements
  project-planning-standards.md   # Long-term project planning (from planning-documentation)
  issue-planning-standards.md     # Short-term issue plans (from task-breakdown-agent)
  refactoring-planning-standards.md # Refactoring task tracking (from refactoring-process)
```

### Design Principles

**1. Unified Core Concepts**
- Single source of truth for status indicators
- Consistent task structure elements
- Shared traceability patterns
- Common quality standards

**2. Use-Case-Specific Extensions**
- Each use case inherits core concepts
- Each extends with specific requirements
- Clear guidance on when to use which approach

**3. Flexible Format Support**
- Support both AsciiDoc and Markdown
- Format choice based on use case and context
- Conversion guidance when needed

**4. Agent-Friendly Design**
- Clear standards agents can follow
- Structured formats agents can generate
- Verification patterns agents can apply

---

## Detailed Consolidation Plan

### Phase 1: Create cui-task-planning Skill

**Action:** Create new skill in cui-workflow bundle

**Location:** `claude/marketplace/bundles/cui-workflow/skills/cui-task-planning/`

**Files to create:**

#### 1.1: SKILL.md

```yaml
---
name: cui-task-planning
description: Comprehensive task planning and tracking standards for project planning, issue implementation, and refactoring workflows
allowed-tools: []
standards:
  - standards/task-planning-core.md
  - standards/project-planning-standards.md
  - standards/issue-planning-standards.md
  - standards/refactoring-planning-standards.md
---
```

**Content sections:**
- What This Skill Provides (all three use cases)
- When to Activate (decision tree: which use case?)
- Workflow (load appropriate standards based on use case)
- Standards Organization
- Integration with cui-workflow bundle

#### 1.2: task-planning-core.md

**Purpose:** Common elements across all task planning use cases

**Content:**
- **Core Concepts:** Task, status, traceability, progress tracking
- **Status Indicators:** Unified definitions for [ ], [x], [~], [!]
- **Task Elements:** Common fields (title, description, status, references, notes)
- **Traceability Patterns:** Linking to requirements, specs, issues, code
- **Format Guidelines:** AsciiDoc vs Markdown selection criteria
- **Quality Standards:** Clarity, completeness, actionability

#### 1.3: project-planning-standards.md

**Purpose:** Long-term project planning standards (migrated from planning-documentation.md)

**Content:**
- Document structure (doc/TODO.adoc, ROADMAP.adoc, BACKLOG.adoc)
- Hierarchical organization strategies (by component/feature/layer/phase)
- Task grouping and nesting
- 4 status indicators including [~] and [!]
- Testing task organization
- Implementation notes standards
- Traceability to requirements and specs
- Maintenance and lifecycle
- Complete example

**Source:** `claude/marketplace/bundles/cui-requirements/skills/planning-documentation.md`

#### 1.4: issue-planning-standards.md

**Purpose:** Short-term issue implementation planning (enhanced from task-breakdown-agent.md)

**Content:**
- Plan document structure (plan-issue-X.md)
- Sequential task organization (Task 1, Task 2, ...)
- Task components: Goal, References, Checklist, Acceptance Criteria
- Sequential execution emphasis (ONE task at a time)
- GitHub issue integration
- Agent-consumable format
- Verification workflows
- Complete example

**Source:** `claude/marketplace/bundles/cui-workflow/agents/task-breakdown-agent.md` (extract planning standards)

**Enhancement:** Add optional task identifiers (e.g., "T1", "T2") for commit message reference

#### 1.5: refactoring-planning-standards.md

**Purpose:** Refactoring and improvement task tracking (migrated from refactoring-process.adoc)

**Content:**
- Category-based organization
- Task identifier format (Category + Number: C1, P2, S3, etc.)
- Standard categories: Code (C), Performance (P), Security (S), Testing (T), Dependency (D), Documentation (DOC), Future (F)
- Task format: Identifier, Title, Priority, Description, Rationale
- Priority levels (High/Medium/Low)
- Commit message integration
- Adding new tasks
- Progress tracking
- Complete example

**Source:** `standards/process/refactoring-process.adoc`

#### 1.6: README.md

**Purpose:** Skill overview and integration guidance

**Content:**
- Overview of all three use cases
- Quick decision tree: which standards to use?
- Integration with cui-workflow agents
- Examples for each use case
- Migration notes from old documents

### Phase 2: Update task-breakdown-agent

**Action:** Simplify agent to load cui-task-planning skill

**Changes:**
- Add skill loading at Step 0:
  ```
  Skill: cui-task-planning
  ```
- Reference issue-planning-standards.md for plan structure
- Remove embedded plan format (delegate to skill)
- Keep agent-specific logic (GitHub integration, file discovery, etc.)
- Maintain focus: agent creates plans, skill defines what plans should contain

**Rationale:** Agent should use standards, not duplicate them

### Phase 3: Migrate refactoring-process.adoc

**Action:** Convert refactoring-process.adoc to skill reference

**Changes:**
- Move content to refactoring-planning-standards.md
- Convert AsciiDoc → Markdown
- Update standards/process/refactoring-process.adoc to reference skill:
  ```asciidoc
  == Refactoring Task Planning

  For comprehensive refactoring task planning standards, see the
  `cui-task-planning` skill in the cui-workflow bundle:

  Skill: cui-workflow:cui-task-planning

  Specifically refer to `refactoring-planning-standards.md` for:
  - Category-based task organization
  - Task identifier formats
  - Priority assignment
  - Commit message integration
  ```

**Alternative:** Remove refactoring-process.adoc entirely if it becomes redundant

### Phase 4: Update planning-documentation.md (Optional)

**Decision Point:** Keep as-is or convert to skill reference?

**Option A: Keep as-is** (Recommended)
- planning-documentation.md stays in cui-requirements bundle
- Content remains for requirements-focused context
- cui-requirements focuses on requirements/specs, cui-workflow focuses on execution

**Option B: Convert to Reference**
- Move content to project-planning-standards.md
- Update planning-documentation.md to reference cui-task-planning skill
- Consolidates all planning in one place

**Recommendation:** Option A - Keep as-is
- cui-requirements and cui-workflow serve different purposes
- Duplication is acceptable when content serves different audiences
- Requirements documentation setup vs workflow execution are distinct concerns

**If Option A:** Ensure consistency
- Core concepts must align (status indicators, traceability)
- Cross-reference between skills
- Update planning-documentation.md to reference cui-task-planning for implementation-focused plans

### Phase 5: Update Bundle Configurations

**Actions:**

1. Register skill in cui-workflow plugin.json
2. Update cui-workflow README to describe cui-task-planning skill
3. Update task-breakdown-agent.md frontmatter to include Skill tool
4. Update any commands that create plans to reference the skill

---

## Benefits of Consolidation

### For Agents
- **Single source of truth** - One skill to load for all planning scenarios
- **Clear guidance** - Know which standards apply to which use case
- **Consistent patterns** - Same core concepts across use cases
- **Reduced duplication** - Don't repeat standards in agent files

### For Users
- **Predictable structure** - Know what to expect from plans
- **Consistent tracking** - Same status indicators, same approach
- **Better traceability** - Unified linking standards
- **Clear progression** - Project planning → Issue planning → Refactoring tracking

### For Maintainers
- **Single update point** - Fix once, applies everywhere
- **Consistent evolution** - Standards improve together
- **Clear ownership** - cui-workflow bundle owns task planning
- **Easier diagnosis** - One skill to validate, not three documents

---

## Migration Impact Assessment

### Files to Create (4 new files)
- `claude/marketplace/bundles/cui-workflow/skills/cui-task-planning/SKILL.md`
- `claude/marketplace/bundles/cui-workflow/skills/cui-task-planning/README.md`
- `claude/marketplace/bundles/cui-workflow/skills/cui-task-planning/standards/task-planning-core.md`
- `claude/marketplace/bundles/cui-workflow/skills/cui-task-planning/standards/project-planning-standards.md`
- `claude/marketplace/bundles/cui-workflow/skills/cui-task-planning/standards/issue-planning-standards.md`
- `claude/marketplace/bundles/cui-workflow/skills/cui-task-planning/standards/refactoring-planning-standards.md`

### Files to Modify (3 files)
- `claude/marketplace/bundles/cui-workflow/agents/task-breakdown-agent.md` - Add skill loading, simplify plan format
- `claude/marketplace/bundles/cui-workflow/.claude-plugin/plugin.json` - Register skill
- `claude/marketplace/bundles/cui-workflow/README.md` - Document skill

### Files to Remove (Optional: 1 file)
- `standards/process/refactoring-process.adoc` - Migrated to skill
- **Alternative:** Keep as reference document pointing to skill

### Files to Keep As-Is (1 file)
- `claude/marketplace/bundles/cui-requirements/skills/planning-documentation.md` - Serves requirements audience

### Breaking Changes
**None** - All existing formats remain valid
- Agents can gradually adopt skill
- Users can continue using existing plan formats
- Standards evolve in place

---

## Implementation Order

**If Approved, implement in this order:**

1. **Create cui-task-planning skill** (Phase 1)
   - All standards files
   - SKILL.md, README.md
   - Register in plugin.json

2. **Update task-breakdown-agent** (Phase 2)
   - Load skill
   - Simplify embedded format
   - Test with real issue

3. **Migrate refactoring-process.adoc** (Phase 3)
   - Convert to Markdown
   - Move to skill
   - Update or remove original

4. **Verify consistency** (Phase 4)
   - Check planning-documentation.md alignment
   - Add cross-references if needed

5. **Test and validate**
   - Run cui-diagnose-skills on new skill
   - Verify task-breakdown-agent works correctly
   - Validate all three use cases covered

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Breaking existing workflows** | High | Keep all existing formats valid; migrate incrementally |
| **Duplication with planning-documentation** | Low | Accept duplication; serve different audiences; cross-reference |
| **Agent adoption lag** | Medium | Agents work without skill; skill improves over time |
| **Format confusion** | Medium | Clear decision tree in SKILL.md; examples for each use case |
| **Scope creep** | Low | Stick to three use cases; reject expansion requests |

---

## Decision Required

**Question for User:** Should we proceed with creating the consolidated `cui-task-planning` skill following this plan?

**Options:**
1. **APPROVE** - Proceed with implementation as described
2. **MODIFY** - Suggest changes to the plan (specify what to change)
3. **REJECT** - Keep current structure (explain why)

**Once approved, implementation will:**
- Create cui-task-planning skill in cui-workflow bundle
- Migrate refactoring-process.adoc content
- Update task-breakdown-agent to use skill
- Provide ONE authoritative source for all task planning

---

**Status:** AWAITING USER APPROVAL
