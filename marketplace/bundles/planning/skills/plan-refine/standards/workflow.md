# Plan Refine Workflow

## Phase Overview

The refine phase analyzes requirements and produces detailed implementation tasks:

```
Plan from Init Phase
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ REFINE PHASE                                        │
│                                                     │
│   0. Detect complexity (auto-decide)                │
│      ├─ Complex → Create analysis.md                │
│      └─ Simple → Skip to step 2                     │
│   1. Read context (plan, config, issue)             │
│   2. Analyze requirements → components              │
│   3. Plan implementation tasks                      │
│   4. Identify documentation needs                   │
│   5. Generate implementation-requirements.md        │
│   6. Transition to implement phase                  │
└─────────────────────────────────────────────────────┘
        │
        ▼
    Implement Phase
```

**Auto-Continue Behavior**: The refine phase executes continuously without user prompts except:
- Analysis review (only if analysis.md is created)
- Component analysis confirmation
- Task list approval

## Operations Summary

| Operation | Description | Output |
|-----------|-------------|--------|
| **detect-complexity** | Evaluate if strategic analysis needed | needs_analysis: boolean |
| **create-analysis** | Create and populate analysis.md | analysis.md file |
| **analyze** | Break down requirements into components | Component list with relationships |
| **plan-tasks** | Create detailed implementation tasks | Tasks with acceptance criteria |
| **identify-docs** | Determine documentation needs | ADR and interface references |

---

## Step 0: Detect Complexity

**Purpose**: Automatically determine if the task requires strategic analysis before component breakdown.

**Detection Criteria**:

| Question | If YES → analysis.md |
|----------|---------------------|
| Are multiple skills/components affected? | Create analysis |
| Are there breaking changes? | Create analysis |
| Are there architectural decisions (not just code changes)? | Create analysis |
| Are there complex dependencies to understand first? | Create analysis |
| Are there risks that need documentation? | Create analysis |

**Decision Logic**:
- ALL answers NO → Skip to component breakdown (standard flow)
- ANY answer YES → Create analysis.md first

**Auto-Decision**: This step does NOT prompt the user. It evaluates automatically and proceeds.

---

## Conditional: Create Analysis (if needed)

When `needs_analysis: true`:

1. **Create analysis.md** from `templates/analysis.md`
2. **Explore codebase** to populate sections:
   - Current State: Existing implementations
   - Affected Components: Files/modules that will change
   - Design Decisions: Key choices being made
   - Breaking Changes: Compatibility impacts (if any)
   - Risks: Potential issues and mitigations
   - Success Criteria: Measurable outcomes
3. **Present to user for review** (single prompt):
   - Options: Approve / Edit / Add details
4. **Add to references** as implementation file
5. **Continue** to component analysis

When `needs_analysis: false`:
- Skip directly to component analysis (no prompt)

## Component Analysis

Analyze requirements to identify:
1. Functional components (features, APIs, services)
2. Technical boundaries (modules, packages, layers)
3. Dependencies between components
4. Complexity estimates (low/medium/high)

## Task Planning

For each component:
1. Create implementation task(s)
2. **Apply sub-type template** if specified by plan-type (see plan-type template)
3. Add technology-specific checklist items
4. Define acceptance criteria from requirements
5. Add standard quality checklist items

**Sub-Type Templates**: Plan-type templates (e.g., plugin-development.md) specify which sub-type templates to use for specific operations. The sub-type template provides the complete actionable checklist. See `templates/` directory for available templates:
- `script-task.md` - TDD workflow for script creation
- `skill-task.md` - Skill creation workflow
- `command-task.md` - Command creation workflow
- `agent-task.md` - Agent creation workflow

Order tasks based on:
- Component dependencies
- Build order requirements
- Test isolation needs

## Technology-Specific Standards

### For Java Tasks

**Standard Checklist Items**:
```markdown
- [ ] Follow CUI Java coding standards
- [ ] Add JavaDoc to public methods
- [ ] Implement unit tests (JUnit 5)
- [ ] Verify build via `maven-builder` agent
- [ ] Check coverage ≥80%
```

**Delegation**: `cui-java-expert:java-implement-agent`

### For JavaScript Tasks

**Standard Checklist Items**:
```markdown
- [ ] Follow CUI JavaScript standards
- [ ] Add JSDoc to exported functions
- [ ] Implement unit tests (Jest)
- [ ] Verify build via `npm-builder` agent
- [ ] Check coverage ≥80%
```

**Delegation**: `cui-frontend-expert`

### For Mixed Tasks

**Standard Checklist Items**:
```markdown
- [ ] Follow technology-appropriate standards
- [ ] Add documentation per language
- [ ] Implement tests for both stacks
- [ ] Run both Maven and npm builds
```

## Documentation Identification

### ADR Triggers
- Architectural decisions (technology choices, patterns)
- Security considerations
- Integration approaches
- Performance trade-offs

### Interface Triggers
- New APIs (REST, GraphQL, etc.)
- Service interfaces
- External integrations
- Contract definitions

## Quality Gates

**Before Implement Phase**:
- [ ] All tasks have clear goals
- [ ] All tasks have acceptance criteria
- [ ] Dependencies correctly mapped
- [ ] Documentation references complete

**Per Task**:
- Test coverage: ≥80%
- Build status: passing
- Documentation: complete

---

## Validation Criteria

### Input Handling
- [ ] Accept `plan_id` parameter (never paths)
- [ ] Read config.toon to get plan_type and build_system
- [ ] Read all requirements via plan-requirements skill (findAll operation)
- [ ] Fail if no requirements found with message: "Run plan-configure first"
- [ ] Fail if config.toon missing with message: "Plan not configured"

### Domain Delegation
- [ ] Select domain skill based on plan_type:
  - `java` → `cui-java-expert:java-analysis`
  - `javascript` → `cui-frontend-expert:js-analysis`
  - `plugin-development` → `cui-plugin-development-tools:plugin-analysis`
  - `generic` → Handle directly (no delegation)
- [ ] Call plan-type:specify to transform requirements to specifications
- [ ] Call plan-type:plan to transform specifications to tasks

### Specifications Creation
- [ ] Write each specification via manage-specifications skill
- [ ] Each specification references at least one requirement
- [ ] Specifications numbered sequentially (SPEC-1, SPEC-2, etc.)

### Tasks Creation
- [ ] Write each task via manage-tasks skill
- [ ] Each task references exactly one specification
- [ ] Tasks include steps (atomic, verifiable, sequenced)
- [ ] Tasks numbered sequentially (TASK-1, TASK-2, etc.)

### Traceability Validation
- [ ] Every specification references existing requirements
- [ ] Every task references existing specification
- [ ] Every requirement has at least one specification
- [ ] Return traceability summary in output

### Integration
- [ ] Write work-log entry after creating specifications
- [ ] Write work-log entry after creating tasks
- [ ] Record lesson-learned on any script/command failure
- [ ] Transition phase from "refine" to "execute" via manage-lifecycle
- [ ] Return `plan_id`, `specifications` count, `tasks` count, and `next_phase` in output
