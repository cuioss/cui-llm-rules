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
| `git-workflow` | Git commit operations |
| `pr-workflow` | PR creation and management |
| `sonar-workflow` | Sonar issue handling |

### Manage Skills (Data/Artifact CRUD)

| Skill | Script | Purpose |
|-------|--------|---------|
| `manage-plan-documents` | `manage-plan-document.py` | Request/Solution document CRUD |
| `manage-tasks` | `manage-task.py` | Tasks + steps CRUD |
| `manage-files` | `manage-files.py` | Generic file I/O |
| `manage-config` | `manage-config.py` | config.toon domain |
| `manage-references` | `manage-references.py` | references.toon domain |
| `manage-lifecycle` | `manage-lifecycle.py` | status.toon + phases |
| `manage-log` | `manage-work-log.py` | Work log entries |
| `manage-lessons` | `manage-lesson.py` | Global lessons |

## Plan-Type Skill API

**Contract**: `planning:plan-type-api` skill defines the full API specification.

All plan-type skills implement:

| Element | Description |
|---------|-------------|
| `configure` operation | Adds domain-specific fields to references.toon and finalize config |
| `domain:` frontmatter | Declares goals_agent, plan_agent, verification_command |

**Key Design**:
- `configure` operation adds finalize configuration to config.toon
- `domain:` frontmatter enables command-level routing to domain agents
- Domain agents (goals_agent, plan_agent) are invoked by `/plan-manage` command via Task tool

## Skill-Based Domain Agent Routing

The refine phase uses **skill-based routing**: commands load plan-type skills and invoke domain agents from the skill's `domain:` frontmatter.

### Plan-Type Skills

Each plan-type skill declares its domain agents in structured frontmatter:

| Plan Type | Goals Agent | Plan Agent |
|-----------|-------------|------------|
| `java` | `cui-java-expert:java-goals-agent` | `cui-java-expert:java-plan-agent` |
| `javascript` | `cui-frontend-expert:js-goals-agent` | `cui-frontend-expert:js-plan-agent` |
| `plugin-development` | `cui-plugin-development-tools:plugin-goals-agent` | `cui-plugin-development-tools:plugin-plan-agent` |
| `generic` | N/A (uses plan-refine-agent fallback) | N/A |

### Refine Flow

```
/plan-manage action=refine
   │
   ├─ manage-config get --field plan_type
   │     └─ "planning:plan-type-java"
   │
   ├─ Skill: planning:plan-type-java
   │     └─ Read frontmatter.domain
   │
   ├─ Task: {domain.goals_agent}
   │     └─ Creates solution_outline.md with goals from request.md
   │
   └─ Task: {domain.plan_agent}
         └─ Creates TASK files from solution_outline.md goals
```

**Override**: Projects can customize agent mappings via marshal.json for project-specific needs.

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
    │   └── SKILL.md             # Contract: configure operation + domain frontmatter
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
    ├── manage-plan-documents/   # Request/Solution document CRUD
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
- **cui-plugin-development-tools** - Plugin doctor, plugin-goals-agent, plugin-plan-agent
- **builder** - Build execution (maven/npm)
- **cui-java-expert** - java-goals-agent, java-plan-agent, java-implement-agent
- **cui-frontend-expert** - js-goals-agent, js-plan-agent

## Installation

```bash
/plugin install planning
```
