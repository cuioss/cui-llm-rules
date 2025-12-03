# CUI Task Workflow Architecture

## Core Design Principle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SINGLE SOURCE OF TRUTH                                │
│                                                                          │
│  Plan-type SKILLS define STRUCTURE and ACTIONABLE TASKS.                 │
│  They POPULATE plan.md with phases and checklists via scripts.           │
│                                                                          │
│  plan-execute reads plan.md and runs the checklists sequentially.        │
│  Intelligence lives in the PLAN-TYPE SKILL, not the EXECUTOR.            │
└─────────────────────────────────────────────────────────────────────────┘
```

## Layered Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Layer 1: PHASES (High-Level Ordering)                                    │
│                                                                          │
│   init ──→ refine ──→ execute ──→ finalize                              │
│                                                                          │
│   Defines workflow structure and progression gates.                      │
├─────────────────────────────────────────────────────────────────────────┤
│ Layer 2: TASKS (Containers within Phases)                                │
│                                                                          │
│   Phase: init                                                            │
│   ├── Task 1: Detect Environment                                         │
│   ├── Task 2: Confirm Configuration                                      │
│   └── (more tasks...)                                                    │
│                                                                          │
│   Each task has: Goal, Acceptance Criteria, Checklist                    │
├─────────────────────────────────────────────────────────────────────────┤
│ Layer 3: ACTIONABLE CHECKLIST ITEMS (Fine-Grained Steps)                 │
│                                                                          │
│   **Checklist**:                                                         │
│   - [ ] Check current git branch                                         │
│   - [ ] Detect build system (pom.xml, package.json, etc.)               │
│   - [ ] Parse issue from parameters or branch name                       │
│   - [ ] **Log**: Record completion in work-log                           │
│   - [ ] **Learn**: Capture lesson if unexpected behavior                 │
│                                                                          │
│   These ARE the actions to execute. Detailed is CORRECT.                 │
└─────────────────────────────────────────────────────────────────────────┘
```

## Plan-Type Skills (Single Source of Truth)

Plan-types are first-class skills that provide workflow definitions via a uniform API:

```
planning/skills/
├── plan-type-simple/           # 3-phase workflow skill
│   └── SKILL.md                # API: configure, specify, plan
│
├── plan-type-plugin/           # 4-phase workflow skill
│   ├── SKILL.md                # API: configure, specify, plan
│   └── templates/              # Internal sub-type templates
│       ├── script-task.md
│       ├── skill-task.md
│       ├── command-task.md
│       └── agent-task.md
│
├── plan-type-java/             # 4-phase workflow skill (Java)
│   └── SKILL.md                # API: configure, specify, plan
│
└── plan-type-javascript/       # 4-phase workflow skill (JavaScript)
    └── SKILL.md                # API: configure, specify, plan
```

**Uniform API** (all plan-type skills):

| Operation | Input | Output |
|-----------|-------|--------|
| `configure` | `plan_id` | Adds domain fields to references.toon + finalize config to config.toon |
| `specify` | `plan_id` | Creates SPEC files from requirements |
| `plan` | `plan_id` | Creates TASK files from specifications |

**Key Design**:
- `configure` writes finalize configuration to config.toon during init (no separate query needed)
- `specify` transforms requirements → specifications (single responsibility)
- `plan` transforms specifications → tasks (single responsibility)

**Flow**:
1. User requests task
2. `plan-init` determines plan type, creates base config/references, calls `configure`
3. `plan-refine` calls `specify` to generate specifications from requirements
4. `plan-refine` calls `plan` to generate tasks from specifications
5. `plan-execute` reads plan files → executes tasks sequentially
6. `plan-execute` reads finalize config directly from config.toon

## Domain Analysis Skills

Domain-specific analysis skills live in their respective expert bundles:

```
cui-plugin-development-tools/skills/
└── plugin-analysis/            # Analyzes plugin components

cui-java-expert/skills/
└── java-analysis/              # Analyzes Java implementation

cui-frontend-expert/skills/
└── js-analysis/                # Analyzes JavaScript implementation
```

### Unified Analysis API

**Contract Definition**: `planning:analysis-api` skill defines the full API contract.

```
Skill: planning:analysis-api
```

All domain analysis skills implement this contract by loading the analysis-api skill and providing domain-specific implementations.

**Key Elements** (see `planning:analysis-api` for full specification):

| Element | Description |
|---------|-------------|
| **Operation** | `analyze` |
| **Input** | `plan_id`, `task_description`, `issue_context`, `build_system` |
| **Output** | `analysis_result` with `status` and `components[]` |
| **Components** | name, type, scope, path, dependencies, complexity, notes |

**Component Types by Domain**:

| Domain | Skill | Types |
|--------|-------|-------|
| Plugin | `cui-plugin-development-tools:plugin-analysis` | `script`, `skill`, `command`, `agent` |
| Java | `cui-java-expert:java-analysis` | `class`, `interface`, `module`, `package`, `config` |
| JavaScript | `cui-frontend-expert:js-analysis` | `module`, `class`, `web-component`, `utility`, `config` |

### Handoff Protocol

```
┌─────────────┐    analyze(plan_id, task, issue, build)    ┌─────────────┐
│ plan-refine │ ──────────────────────────────────────────► │  domain     │
│             │                                             │  analysis   │
│             │ ◄────────────────────────────────────────── │  skill      │
└─────────────┘    analysis_result{status, components[]}    └─────────────┘
       │
       │ components[]
       ▼
┌─────────────┐    specify(plan_id)                        ┌─────────────┐
│ plan-refine │ ──────────────────────────────────────────► │  plan-type  │
│             │                                             │  skill      │
│             │ ◄────────────────────────────────────────── │             │
└─────────────┘    (creates SPEC files from REQ files)      └─────────────┘
       │
       ▼
┌─────────────┐    plan(plan_id)                           ┌─────────────┐
│ plan-refine │ ──────────────────────────────────────────► │  plan-type  │
│             │                                             │  skill      │
│             │ ◄────────────────────────────────────────── │             │
└─────────────┘    (creates TASK files from SPEC files)     └─────────────┘
```

### Analysis Flow

1. `plan-refine` reads plan context (task description, issue, config)
2. Based on `plan_type`, delegates to appropriate analysis skill
3. Analysis skill explores codebase, identifies components
4. Returns `analysis_result` with structured `components[]`
5. `plan-refine` calls `specify` to create specifications from requirements
6. `plan-refine` calls `plan` to create tasks from specifications

**Why Domain Ownership**: Analysis requires domain expertise (Java patterns, JavaScript structure, plugin architecture). Keeping analysis skills in expert bundles:
- Leverages existing domain knowledge
- Allows domain-specific evolution
- Avoids overloading planning bundle with domain logic

## Task Runner Pattern

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      PHASE SKILL = DUMB TASK RUNNER                      │
│                                                                          │
│  The plan-execute skill is a SIMPLE RUNNER for all execution phases:     │
│                                                                          │
│      ┌──────────────────────────────────────────────────────────┐       │
│      │                                                          │       │
│      │  1. LOCATE    →  Find current task in plan.md           │       │
│      │       │                                                  │       │
│      │       ▼                                                  │       │
│      │  2. EXECUTE   →  Run checklist items (delegate to       │       │
│      │       │           agents/skills as specified)            │       │
│      │       ▼                                                  │       │
│      │  3. UPDATE    →  Mark items [x], call update-progress   │       │
│      │       │                                                  │       │
│      │       ▼                                                  │       │
│      │  4. NEXT      →  Move to next task or phase             │       │
│      │                                                          │       │
│      └──────────────────────────────────────────────────────────┘       │
│                                                                          │
│  NO BUSINESS LOGIC - just sequential execution of checklists.            │
└─────────────────────────────────────────────────────────────────────────┘
```

## Why Detailed Checklists Are Correct

The checklist items in templates are **actionable tasks** - they describe exactly what scripts to run or operations to perform. This is intentional:

```
CORRECT (actionable):                    WRONG (vague):
- [ ] Check current git branch           - [ ] Setup environment
- [ ] Detect build system                - [ ] Configure
- [ ] Parse issue from branch name       - [ ] Initialize
```

The detail level ensures:
1. **Reproducibility**: Same checklist → Same actions
2. **Delegation**: Task runner can execute without interpretation
3. **Tracking**: Each step can be independently verified

## Component Dependencies

```
                           Commands
                    ┌────────────────────┐
                    │  /plan-manage      │
                    │  /plan-execute     │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │  phase-management  │ ◄── Orchestration
                    │     (skill)        │
                    └─────────┬──────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │ plan-init   │    │ plan-refine │    │plan-execute │ ◄── Phase Skills
   │             │    │(orchestrate)│    │(dumb runner)│
   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
          │                  │                  │
          │         ┌────────┴────────┐         │
          │         │                 │         │
          │         ▼                 ▼         │
          │  ┌─────────────┐  ┌─────────────┐   │
          │  │   Domain    │  │ Plan-Type   │   │
          │  │  Analysis   │  │   Skills    │◄──┘
          │  │   Skills    │  │             │
          │  └─────────────┘  └──────┬──────┘
          │         │                │
          │         │  components[]  │
          │         └───────►────────┘
          │                          │
          │    ┌─────────────────────┘
          │    │ specify + plan
          ▼    ▼ (writes directly)
   ┌─────────────────────────────────┐
   │    plan-files (skill)           │ ◄── File I/O Abstraction
   └─────────────────────────────────┘
                    │
                    ▼
   ┌─────────────────────────────────┐
   │  Python Scripts                 │ ◄── Atomic Operations
   │  write-plan.py, update-progress │
   │  transition-phase.py            │
   └─────────────────────────────────┘

   Domain Analysis Skills (in expert bundles):
   ┌─────────────────────────────────────────────┐
   │ cui-plugin-development-tools:plugin-analysis│
   │ cui-java-expert:java-analysis               │
   │ cui-frontend-expert:js-analysis             │
   └─────────────────────────────────────────────┘
```

## Error Handling

When script execution fails (exit != 0):
1. Capture error context (script path, exit code, stderr)
2. Follow `general-tools:script-runner` Error Handling workflow
3. Continue with normal error recovery

See `general-tools:script-runner` SKILL.md "Workflow: Error Handling" for the lessons-learned capture pattern.

## Plan-Type Skills Summary

| Skill | Phases | Use Case |
|-------|--------|----------|
| `plan-type-simple` | init → execute → finalize | Documentation, config, quick fixes |
| `plan-type-java` | init → refine → implement → verify → finalize | Java/Maven/Gradle implementation |
| `plan-type-javascript` | init → refine → implement → verify → finalize | JavaScript/npm implementation |
| `plan-type-plugin` | init → refine → execute → finalize | Marketplace components |

**Finalize Behavior** (from config.toon, written by configure):

| Skill | Create PR | Verification |
|-------|-----------|--------------|
| `plan-type-simple` | No | None |
| `plan-type-java` | Yes | `/builder-build-and-fix` |
| `plan-type-javascript` | Yes | `/builder-build-and-fix system=npm` |
| `plan-type-plugin` | No | `/plugin-doctor` |

## Sub-Type Templates

Located in `plan-type-plugin/templates/` (internal to plan-type-plugin skill):

| Template | Trigger | Provides |
|----------|---------|----------|
| `script-task.md` | component.type = "script" | TDD workflow (red→green) |
| `skill-task.md` | component.type = "skill" | Skill structure workflow |
| `command-task.md` | component.type = "command" | Command orchestration workflow |
| `agent-task.md` | component.type = "agent" | Agent frontmatter workflow |

**Note**: These templates are internal to plan-type-plugin. When `plan` operation is called:
1. It reads specifications from SPEC files
2. Selects appropriate template based on `component.type`
3. Generates tasks and writes them directly to TASK files
4. Phase skills never access templates directly
