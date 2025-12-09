# CUI Task Workflow

Plan-based task management system that transforms high-level task descriptions into executable action sequences through progressive refinement.

## Architecture

**Core Principle**: Plan-Type Skills are SINGLE SOURCE OF TRUTH, phase skills execute checklists.

See [skills/plan-refine/standards/architecture.md](skills/plan-refine/standards/architecture.md) for full architecture documentation.

```
User Request → Plan-Type Skill → Phase Skills (execute checklists) → Result
```

## Commands

### /plan-manage
Manage task plans - list, create, refine.

```bash
/plan-manage action=list              # List active plans
/plan-manage action=create task="..." # Create new plan
/plan-manage action=refine            # Refine current plan
```

### /plan-execute
Execute task plans - implement, verify, finalize.

```bash
/plan-execute                         # Continue current plan
/plan-execute phase=implement         # Execute specific phase
```

### /pr-doctor
Diagnose and fix PR issues (build, reviews, Sonar).

```bash
/pr-doctor pr=123
/pr-doctor checks=sonar
```

### /task-implement
Quick task implementation (combines create + execute).

```bash
/task-implement task=123              # From GitHub issue
/task-implement task="Add feature"    # From description
```

## Skills

### Plan-Type Skills (Single Source of Truth)

All plan-type skills implement `planning:plan-type-api` contract.

| Skill | Phases | Purpose |
|-------|--------|---------|
| `plan-type-api` | - | **API contract** for all plan-type skills |
| `plan-type-generic` | 3 | Generic workflow for docs, config, quick fixes |
| `plan-type-plugin` | 4 | Plugin development with /plugin-doctor verification |
| `plan-type-java` | 4 | Java/Maven/Gradle implementation |
| `plan-type-javascript` | 4 | JavaScript/npm implementation |

### Phase Skills

| Skill | Role | Purpose |
|-------|------|---------|
| `plan-init` | Setup | Create plan structure, detect type, configure |
| `plan-refine` | Analysis | Decompose request into goals, generate tasks |
| `plan-execute` | Execution | Execute checklist items sequentially (dumb runner) |

### Support Skills

| Skill | Purpose |
|-------|---------|
| `analysis-api` | **API contract** for domain analysis skills |
| `git-workflow` | Git commit operations |
| `pr-workflow` | PR creation and management |
| `sonar-workflow` | Sonar issue handling |

### Manage Skills (Data/Artifact CRUD)

| Skill | Script | Purpose |
|-------|--------|---------|
| `manage-goals` | `manage-goal.py` | Goals CRUD |
| `manage-tasks` | `manage-task.py` | Tasks + steps CRUD |
| `manage-files` | `manage-files.py` | Generic file I/O |
| `manage-config` | `manage-config.py` | config.toon domain |
| `manage-references` | `manage-references.py` | references.toon domain |
| `manage-lifecycle` | `manage-lifecycle.py` | status.toon + phases |
| `manage-log` | `manage-work-log.py` | Work log entries |
| `manage-lessons` | `manage-lesson.py` | Global lessons |

## Plan-Type Skill API

**Contract**: `planning:plan-type-api` skill defines the full API specification.

All plan-type skills implement this uniform API:

| Operation | Input | Output | Caller |
|-----------|-------|--------|--------|
| `configure` | `plan_id` | References + config updated | plan-init |
| `decompose` | `plan_id` | GOAL files created | plan-refine |
| `plan` | `plan_id` | TASK files created | plan-refine |

**Key Design**:
- `configure` adds domain-specific fields to references.toon and finalize configuration to config.toon
- `decompose` analyzes request and creates goals
- `plan` transforms goals → tasks

## Domain Goal Decomposition

Goal decomposition is delegated to domain-specific agents in their expert bundles:

| Plan Type | Goals Agent |
|-----------|-------------|
| `plugin-development` | `cui-plugin-development-tools:plugin-goals-agent` |
| `java` | `cui-java-expert:java-goals-agent` |
| `javascript` | `cui-frontend-expert:js-goals-agent` |
| `generic` | N/A (inline in plan-type skill) |

### Refine Flow

```
plan-refine → decompose(plan_id) → plan-type-skill → domain-goals-agent
            ← (creates GOAL files from request.md)

plan-refine → plan(plan_id) → plan-type-skill → domain-plan-agent
            ← (creates TASK files from GOAL files)
```

### Sub-Type Templates

Located in `skills/plan-type-plugin/templates/` (internal to plan-type-plugin):

| Template | Trigger | Provides |
|----------|---------|----------|
| `script-task.md` | "create script" | TDD workflow |
| `skill-task.md` | "create skill" | Skill structure |
| `command-task.md` | "create command" | Command orchestration |
| `agent-task.md` | "create agent" | Agent frontmatter |

## File Structure

```
planning/
├── README.md                    # This file
├── commands/
│   ├── plan-manage.md
│   ├── plan-execute.md
│   ├── pr-doctor.md
│   └── task-implement.md
└── skills/
    ├── plan-type-api/           # API contract for all plan-type skills
    │   └── SKILL.md             # Contract: 3 operations (configure, decompose, plan)
    ├── plan-type-generic/       # Generic workflow skill (3 phases)
    │   └── SKILL.md             # Implements plan-type-api
    ├── plan-type-plugin/        # Plugin workflow skill (4 phases)
    │   ├── SKILL.md             # Implements plan-type-api
    │   └── templates/           # Sub-type templates (internal)
    ├── plan-type-java/          # Java workflow skill (4 phases)
    │   └── SKILL.md             # Implements plan-type-api
    ├── plan-type-javascript/    # JavaScript workflow skill (4 phases)
    │   └── SKILL.md             # Implements plan-type-api
    ├── plan-init/               # Init phase skill (complete initialization)
    │   ├── SKILL.md
    │   └── standards/           # Workflow reference
    ├── plan-refine/             # Refine phase skill (goals + tasks)
    │   ├── SKILL.md
    │   ├── standards/           # Architecture and workflow docs
    │   │   ├── architecture.md  # Core architecture documentation
    │   │   └── workflow.md      # Refine workflow reference
    │   └── templates/           # Artifact templates
    ├── plan-execute/            # Execute phase skill (dumb runner)
    ├── manage-goals/            # Goals CRUD
    ├── manage-tasks/            # Tasks + steps CRUD
    ├── manage-files/            # Generic file I/O
    ├── manage-config/           # config.toon domain
    ├── manage-references/       # references.toon domain
    ├── manage-lifecycle/        # status.toon + phases
    ├── manage-log/              # Work log entries
    ├── manage-lessons/          # Global lessons
    ├── git-workflow/
    ├── pr-workflow/
    └── sonar-workflow/

.plan/                           # Plan storage (per project)
├── plans/                       # Active plans
│   └── {plan-name}/
│       ├── plan.md
│       ├── config.toon
│       └── references.toon
├── archived-plans/              # Completed plans
└── lessons-learned/             # Captured lessons
```

## Dependencies

- **general-tools** - Script runner, file operations base
- **cui-plugin-development-tools** - Plugin doctor, plugin-analysis skill
- **builder** - Build execution (maven/npm)
- **cui-java-expert** - Java analysis and implementation delegation
- **cui-frontend-expert** - JavaScript analysis and implementation delegation

## Installation

```bash
/plugin install planning
```
