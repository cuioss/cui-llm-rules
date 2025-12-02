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

| Skill | Phases | Purpose |
|-------|--------|---------|
| `plan-type-simple` | 3 | Simple workflow for docs, config, quick fixes |
| `plan-type-plugin` | 4 | Plugin development with /plugin-doctor verification |
| `plan-type-java` | 5 | Java/Maven/Gradle implementation |
| `plan-type-javascript` | 5 | JavaScript/npm implementation |

### Phase Skills

| Skill | Role | Purpose |
|-------|------|---------|
| `plan-init` | Setup | Create plan structure using plan-type skill |
| `plan-refine` | Analysis | Analyze requirements, generate tasks (loads plan-type skill) |
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
| `manage-requirements` | `manage-requirement.py` | Requirements CRUD |
| `manage-specifications` | `manage-specification.py` | Specifications CRUD |
| `manage-tasks` | `manage-task.py` | Tasks + steps CRUD |
| `manage-handoff` | `manage-handoff.py` | Session handoff |
| `manage-files` | `manage-files.py` | Generic file I/O |
| `manage-config` | `manage-config.py` | config.toon domain |
| `manage-references` | `manage-references.py` | references.toon domain |
| `manage-lifecycle` | `manage-lifecycle.py` | status.toon + phases |
| `manage-log` | `manage-work-log.py` | Work log entries |
| `manage-lessons` | `manage-lesson.py` | Global lessons |

## Plan-Type Skill API

All plan-type skills implement a uniform API:

| Operation | Input | Output | Used By |
|-----------|-------|--------|---------|
| `get-phase-structure` | `plan_id`, `task_title` | Phase structure | plan-init |
| `generate-tasks` | `plan_id`, `components[]` | **Writes directly** to plan.md | plan-refine |
| `get-finalize-config` | `plan_id` | Finalize behavior | plan-execute |
| `get-next-phase` | `plan_id`, `current_phase` | Next phase | phase-management |

**Key Design**: `generate-tasks` writes directly to plan.md via scripts (no ping-pong between skills).

## Domain Analysis Skills

Component analysis is delegated to domain-specific skills in their expert bundles:

| Plan Type | Analysis Skill |
|-----------|----------------|
| `plugin-development` | `cui-plugin-development-tools:plugin-analysis` |
| `java` | `cui-java-expert:java-analysis` |
| `javascript` | `cui-frontend-expert:js-analysis` |
| `simple` | N/A (tasks from description) |

### Unified Analysis API

**Contract**: `planning:analysis-api` skill defines the full API specification.

All domain analysis skills implement this contract:

| Element | Description |
|---------|-------------|
| **Operation** | `analyze` |
| **Input** | `plan_id`, `task_description`, `issue_context`, `build_system` |
| **Output** | `analysis_result` with `status` and `components[]` |

See `planning:analysis-api` for full input/output specification and domain-specific fields.

### Handoff Protocol

```
plan-refine → analyze(plan_id, task, ...) → domain-analysis-skill
            ← analysis_result{status, components[]}

plan-refine → generate-tasks(plan_id, components) → plan-type-skill
            ← (writes directly to plan.md)
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
    ├── plan-type-simple/        # Simple workflow skill (3 phases)
    │   └── SKILL.md             # API: get-phase-structure, generate-tasks, etc.
    ├── plan-type-plugin/        # Plugin workflow skill (4 phases)
    │   ├── SKILL.md             # API: get-phase-structure, generate-tasks, etc.
    │   └── templates/           # Sub-type templates (internal)
    ├── plan-type-java/          # Java workflow skill (5 phases)
    │   └── SKILL.md             # API: get-phase-structure, generate-tasks, etc.
    ├── plan-type-javascript/    # JavaScript workflow skill (5 phases)
    │   └── SKILL.md             # API: get-phase-structure, generate-tasks, etc.
    ├── plan-init/               # Init phase skill
    │   ├── SKILL.md
    │   └── standards/           # Workflow reference
    ├── plan-refine/             # Refine phase skill (smart analysis)
    │   ├── SKILL.md
    │   ├── standards/           # Architecture and workflow docs
    │   │   ├── architecture.md  # Core architecture documentation
    │   │   └── workflow.md      # Refine workflow reference
    │   └── templates/           # Artifact templates
    ├── plan-execute/            # Execute phase skill (dumb runner)
    ├── manage-requirements/     # Requirements CRUD
    ├── manage-specifications/   # Specifications CRUD
    ├── manage-tasks/            # Tasks + steps CRUD
    ├── manage-handoff/          # Session handoff
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
