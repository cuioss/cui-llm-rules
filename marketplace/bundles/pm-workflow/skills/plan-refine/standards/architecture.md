# CUI Task Workflow Architecture

## Core Design Principle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SINGLE SOURCE OF TRUTH                                │
│                                                                          │
│  Domain SKILLS define STRUCTURE and ACTIONABLE TASKS.                    │
│  They POPULATE plan.md with phases and checklists via scripts.           │
│                                                                          │
│  plan-execute reads plan.md and runs the checklists sequentially.        │
│  Intelligence lives in the DOMAIN SKILL, not the EXECUTOR.               │
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

## Thin Agent Architecture

The pm-workflow bundle uses 4 thin agents that load domain-specific skills dynamically:

```
pm-workflow/agents/
├── plan-init-agent.md          # Initialize plan, detect domains
├── solution-outline-agent.md   # Create deliverables
├── task-plan-agent.md          # Create tasks from deliverables
└── task-execute-agent.md       # Execute single task
```

**Skill Loading** (from config.toon):

| Agent | Skill Source |
|-------|--------------|
| `plan-init-agent` | System skills only |
| `solution-outline-agent` | `config.workflow_skills.{domain}.solution_outline` |
| `task-plan-agent` | `config.workflow_skills.{domain}.task_plan` |
| `task-execute-agent` | `config.workflow_skills.{domain}.{profile}` + `task.skills` |

**Key Design**:
- `plan-init` detects domains, writes workflow_skills to config.toon
- Thin agents read config.toon to determine which domain skills to load
- Domain skills provide the intelligence; agents provide the workflow

**Flow**:
1. User requests task
2. `plan-init-agent` detects domain, writes config.toon with workflow_skills
3. `/plan-manage action=refine` invokes `solution-outline-agent` → `task-plan-agent`
4. `/plan-execute` invokes `task-execute-agent` for each task
5. Thin agents load domain skills from config.toon's workflow_skills block

## Domain Skill Loading

All domains use the same 4 domain-agnostic workflow skills in pm-workflow:

```
pm-workflow/skills/
├── solution-outline/       # Domain-agnostic solution outline creation
├── task-plan/              # Domain-agnostic task planning
├── task-implementation/    # Domain-agnostic implementation workflow
└── task-testing/           # Domain-agnostic testing workflow
```

Domain-specific knowledge comes from `task.skills` array, populated during task-plan via `resolve-domain-skills`.

### config.toon Structure

The workflow_skills block in config.toon maps domains to workflow skills:

```toon
domains: [java]

workflow_skills:
  java:
    solution_outline: pm-workflow:solution-outline
    task_plan: pm-workflow:task-plan
    implementation: pm-workflow:task-implementation
    testing: pm-workflow:task-testing
```

For multi-domain plans:
```toon
domains: [java, javascript]

workflow_skills:
  java:
    solution_outline: pm-workflow:solution-outline
    task_plan: pm-workflow:task-plan
    implementation: pm-workflow:task-implementation
    testing: pm-workflow:task-testing
  javascript:
    solution_outline: pm-workflow:solution-outline
    task_plan: pm-workflow:task-plan
    implementation: pm-workflow:task-implementation
    testing: pm-workflow:task-testing
```

### Routing Flow

```
/plan-manage action=refine
       │
       ├─ Task: pm-workflow:solution-outline-agent
       │     ├─ Read config.toon workflow_skills.{domain}.solution_outline
       │     ├─ Load workflow skill (pm-workflow:solution-outline)
       │     └─ Analyzes request, creates deliverables
       │
       └─ Task: pm-workflow:task-plan-agent
             ├─ Read config.toon workflow_skills.{domain}.task_plan
             ├─ Load workflow skill (pm-workflow:task-plan)
             └─ Reads deliverables, creates tasks with domain skills
```

**Key Insight**: All domains use the same 4 workflow skills. Domain-specific knowledge is loaded via `task.skills` at execution time.

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
                    │  /plan-manage      │ ◄── Invokes thin agents
                    │  /plan-execute     │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │    Thin Agents      │ ◄── Load domain skills from config.toon
                    │  (4 generic agents) │
                    └─────────┬───────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
   ┌──────────────┐   ┌──────────────┐   ┌───────────────┐
   │ Domain Skills│   │manage-* APIs │   │ Python Scripts│
   │ (from config)│   │  (CRUD ops)  │   │(atomic ops)   │
   └──────────────┘   └──────────────┘   └───────────────┘

   Thin Agents (in pm-workflow):
   ┌─────────────────────────────────────────────┐
   │ plan-init-agent      - Initialize, detect   │
   │ solution-outline-agent - Create deliverables│
   │ task-plan-agent      - Create tasks         │
   │ task-execute-agent   - Execute single task  │
   └─────────────────────────────────────────────┘

   Domain Skills (loaded via task.skills):
   ┌─────────────────────────────────────────────┐
   │ pm-dev-java: java-core, java-cdi,          │
   │   junit-core, junit-integration, etc.      │
   │                                             │
   │ pm-dev-frontend: cui-javascript,           │
   │   cui-javascript-unit-testing, etc.        │
   │                                             │
   │ pm-plugin-development: plugin-architecture,│
   │   plugin-create, plugin-maintain, etc.     │
   └─────────────────────────────────────────────┘
```

## Error Handling

When script execution fails (exit != 0):
1. Capture error context (script path, exit code, stderr)
2. Follow `plan-marshall:script-runner` Error Handling workflow
3. Continue with normal error recovery

See `plan-marshall:script-runner` SKILL.md "Workflow: Error Handling" for the lessons-learned capture pattern.

## Domain Summary

All domains use the same 4 workflow skills. Domain-specific knowledge comes from `task.skills`:

| Domain | Workflow Skills | Domain Skills (task.skills) |
|--------|-----------------|----------------------------|
| `java` | `pm-workflow:solution-outline`, `task-plan`, `task-implementation`, `task-testing` | `java-core`, `java-cdi`, `junit-core`, etc. |
| `javascript` | `pm-workflow:solution-outline`, `task-plan`, `task-implementation`, `task-testing` | `cui-javascript`, `cui-javascript-unit-testing`, etc. |
| `plugin` | `pm-workflow:solution-outline`, `task-plan`, `task-implementation`, `task-testing` | `plugin-architecture`, `plugin-create`, etc. |

**Finalize Behavior** (from config.toon):

| Domain | Create PR | Verification |
|--------|-----------|--------------|
| `plugin` | No | `/plugin-doctor` |
| `java` | Yes | `/builder-build-and-fix` |
| `javascript` | Yes | `/builder-build-and-fix system=npm` |
