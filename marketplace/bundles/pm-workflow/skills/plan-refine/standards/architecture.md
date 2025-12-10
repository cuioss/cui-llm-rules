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
├── plan-type-generic/          # 3-phase workflow skill
│   └── SKILL.md                # configure + domain: frontmatter (null agents)
│
├── plan-type-plugin/           # 4-phase workflow skill
│   ├── SKILL.md                # configure + domain: frontmatter
│   └── templates/              # Internal sub-type templates
│       ├── script-task.md
│       ├── skill-task.md
│       ├── command-task.md
│       └── agent-task.md
│
├── plan-type-java/             # 4-phase workflow skill (Java)
│   └── SKILL.md                # configure + domain: frontmatter
│
└── plan-type-javascript/       # 4-phase workflow skill (JavaScript)
    └── SKILL.md                # configure + domain: frontmatter
```

**Uniform API** (all plan-type skills):

| Operation | Input | Output |
|-----------|-------|--------|
| `configure` | `plan_id` | Adds domain fields to references.toon + finalize config to config.toon |

Plan-type skills also declare domain agents in their `domain:` frontmatter section.

**Key Design**:
- `configure` writes finalize configuration to config.toon during init
- Domain agent references in skill frontmatter enable command-level routing
- Goals and plan operations are handled by domain agents invoked via Task tool

**Flow**:
1. User requests task
2. `plan-init` determines plan type, creates base config/references, calls `configure`
3. `/plan-manage` loads plan-type skill, reads `domain:` frontmatter
4. `/plan-manage` invokes domain agents via Task tool (solution_outline_agent, task_plan_agent)
5. `plan-execute` reads plan files → executes tasks sequentially
6. `plan-execute` reads finalize config directly from config.toon

## Skill-Based Domain Agent Routing

Domain agents live in their expert bundles and are invoked by commands via Task tool:

```
pm-dev-java/agents/
├── java-solution-outline-agent.md         # Decomposes request into goals
└── java-task-plan-agent.md          # Transforms goals into tasks

pm-dev-frontend/agents/
├── js-solution-outline-agent.md           # Decomposes request into goals
└── js-task-plan-agent.md            # Transforms goals into tasks

pm-plugin-development/agents/
├── plugin-solution-outline-agent.md       # Decomposes request into goals
└── plugin-task-plan-agent.md        # Transforms goals into tasks
```

### Domain Agent Mapping

Plan-type skills declare their domain agents in structured frontmatter:

```yaml
# Example: plan-type-java/SKILL.md
---
domain:
  solution_outline_agent: pm-dev-java:java-solution-outline-agent
  task_plan_agent: pm-dev-java:java-task-plan-agent
  verification_command: /pm-dev-builder:builder-build-and-fix
  pr_workflow: true
---
```

| Plan Type | Solution Outline Agent | Task Plan Agent |
|-----------|-------------|------------|
| `java` | `pm-dev-java:java-solution-outline-agent` | `pm-dev-java:java-task-plan-agent` |
| `javascript` | `pm-dev-frontend:js-solution-outline-agent` | `pm-dev-frontend:js-task-plan-agent` |
| `plugin-development` | `pm-plugin-development:plugin-solution-outline-agent` | `pm-plugin-development:plugin-task-plan-agent` |
| `generic` | N/A | N/A (uses plan-refine-agent fallback) |

### Routing Flow

```
/plan-manage action=refine
       │
       ├─ manage-config get --field plan_type
       │     └─ "pm-workflow:plan-type-java"
       │
       ├─ Skill: pm-workflow:plan-type-java
       │     └─ Read frontmatter.domain
       │
       ├─ Task: {domain.solution_outline_agent}
       │     └─ Analyzes request, creates GOAL files
       │
       └─ Task: {domain.task_plan_agent}
             └─ Reads goals, creates TASK files
```

**Key Insight**: Commands have Task tool, skills do not. Commands load plan-type skills to read agent references, then invoke agents directly.

**Generic Fallback**: For generic plans (no domain agents), falls back to `pm-workflow:plan-refine-agent` which creates goals and tasks inline.

### Why Domain Ownership

Domain agents have deep expertise in their technology:
- **Java agents**: Understand Maven/Gradle, package structure, JUnit patterns
- **JavaScript agents**: Understand npm, ES modules, Jest patterns
- **Plugin agents**: Understand marketplace structure, skill/command/agent patterns

Keeping domain agents in expert bundles:
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
                    │  /plan-manage      │ ◄── Routes to domain agents
                    │  /plan-execute     │
                    └─────────┬──────────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │ plan-init   │    │ Plan-Type   │    │plan-execute │ ◄── Phase Skills
   │   (agent)   │    │   Skills    │    │(dumb runner)│
   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
          │                  │                  │
          │                  │ frontmatter.domain
          │                  ▼                  │
          │         ┌─────────────┐             │
          │         │   Domain    │             │
          │         │   Agents    │ ◄── Invoked via Task by commands
          │         │(goals/plan) │
          │         └──────┬──────┘
          │                │
          │         ┌──────┴──────┐
          │         │             │
          │         ▼             ▼
          │  ┌──────────────────┐ ┌────────────┐
          │  │manage-plan-docs  │ │manage-tasks│ ◄── Script-based CRUD
          │  └──────────────────┘ └────────────┘
          │
          ▼
   ┌─────────────────────────────────┐
   │  Python Scripts                 │ ◄── Atomic Operations
   │  manage-config.py, manage-plan  │
   │  document.py, manage-task.py    │
   └─────────────────────────────────┘

   Domain Agents (in expert bundles):
   ┌─────────────────────────────────────────────┐
   │ pm-dev-java: java-solution-outline-agent           │
   │                  java-task-plan-agent            │
   │ pm-dev-frontend: js-solution-outline-agent         │
   │                      js-task-plan-agent          │
   │ pm-plugin-development: plugin-solution-outline  │
   │                               plugin-task-plan   │
   └─────────────────────────────────────────────┘
```

## Error Handling

When script execution fails (exit != 0):
1. Capture error context (script path, exit code, stderr)
2. Follow `plan-marshall:script-runner` Error Handling workflow
3. Continue with normal error recovery

See `plan-marshall:script-runner` SKILL.md "Workflow: Error Handling" for the lessons-learned capture pattern.

## Plan-Type Skills Summary

| Skill | Phases | Use Case |
|-------|--------|----------|
| `plan-type-generic` | init → execute → finalize | Documentation, config, quick fixes |
| `plan-type-java` | init → refine → implement → verify → finalize | Java/Maven/Gradle implementation |
| `plan-type-javascript` | init → refine → implement → verify → finalize | JavaScript/npm implementation |
| `plan-type-plugin` | init → refine → execute → finalize | Marketplace components |

**Finalize Behavior** (from config.toon, written by configure):

| Skill | Create PR | Verification |
|-------|-----------|--------------|
| `plan-type-generic` | No | None |
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

**Note**: These templates are internal to plan-type-plugin. When the `plugin-task-plan-agent` is invoked:
1. It reads GOAL files from the plan directory
2. Selects appropriate template based on component type
3. Generates tasks and writes them via manage-tasks script
4. Commands invoke domain agents, not templates directly
