# CUI Task Workflow

Plan-based task management system that transforms high-level task descriptions into executable action sequences through progressive refinement using thin agents and domain-agnostic workflow skills.

## Architecture

**Core Principle**: Thin agents load workflow skills from config.toon. Domain knowledge comes from config, not hardcoded in agents.

```
User Request → [Thin Agents] → Workflow Skills (from config.toon) → Domain Skills (from task.skills) → Result
```

### 4-Phase Model

```
init → refine → execute → finalize
```

| Phase | Agent | Purpose |
|-------|-------|---------|
| `init` | `plan-init-agent` | Create plan, detect domains, write config.toon |
| `refine` | `solution-outline-agent` → `task-plan-agent` | Create deliverables, then tasks |
| `execute` | `task-execute-agent` | Execute tasks with two-tier skill loading |
| `finalize` | (inline) | Create PR, cleanup |

## Commands

### /plan-manage
Manage task plans - list, create, refine.

```bash
/plan-manage action=list              # List active plans
/plan-manage action=init task="..."   # Create new plan and refine
/plan-manage action=refine            # Refine specific plan
```

### /plan-execute
Execute task plans - implement, verify, finalize.

```bash
/plan-execute                         # Continue current plan
/plan-execute phase=execute           # Execute specific phase
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

## Thin Agent Pattern

All 4 agents are domain-agnostic wrappers that load skills from config.toon:

| Agent | Loads From | Purpose |
|-------|------------|---------|
| `plan-init-agent` | System skills only | Creates plan, detects domains, writes workflow_skills |
| `solution-outline-agent` | `config.workflow_skills.{domain}.solution_outline` | Creates deliverables from request |
| `task-plan-agent` | `config.workflow_skills.{domain}.task_plan` | Creates tasks from deliverables |
| `task-execute-agent` | `config.workflow_skills.{domain}.{profile}` + `task.skills` | Executes single task |

## Skills

### API Contract Skill

| Skill | Purpose |
|-------|---------|
| `plan-wf-skill-api` | **API contract** for all workflow skills |

### Workflow Skills

| Skill | Purpose |
|-------|---------|
| `solution-outline` | Domain-agnostic solution outline creation |
| `task-plan` | Domain-agnostic task planning |
| `task-implementation` | Domain-agnostic implementation workflow |
| `task-testing` | Domain-agnostic testing workflow |

### Phase Skills

| Skill | Role | Purpose |
|-------|------|---------|
| `plan-init` | Setup | Create plan structure, detect domains, configure |
| `plan-refine` | Analysis | Coordinate solution outline and task plan agents |
| `plan-execute` | Execution | Coordinate task-execute-agent for each task |
| `plan-finalize` | Cleanup | Create PR, archive plan |

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
| `manage-solution-outline` | `manage-solution-outline.py` | Solution outline queries |
| `manage-tasks` | `manage-tasks.py` | Tasks + steps CRUD |
| `manage-files` | `manage-files.py` | Generic file I/O |
| `manage-config` | `manage-config.py` | config.toon domain |
| `manage-references` | `manage-references.py` | references.toon domain |
| `manage-lifecycle` | `manage-lifecycle.py` | status.toon + phases |

**Logging**: Work log entries and script execution logging are provided by `plan-marshall:logging` skill.

## Domain Configuration

Domains and workflow skills are stored in `config.toon`:

```toon
domains: [java]

workflow_skills:
  java:
    solution_outline: pm-workflow:solution-outline
    task_plan: pm-workflow:task-plan
    implementation: pm-workflow:task-implementation
    testing: pm-workflow:task-testing
```

For multi-domain plans (fullstack):
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

## Two-Tier Skill Loading

Task execution uses two-tier skill loading:

| Tier | Source | Purpose |
|------|--------|---------|
| **Tier 1** | Agent frontmatter | System skills (architecture, rules) |
| **Tier 2** | `task.skills` array | Domain-specific skills (java-core, java-cdi, etc.) |

Task-plan resolves skills during task creation:
```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
    resolve-domain-skills --domain java --profile implementation
```

## File Structure

```
pm-workflow/
├── README.md                    # This file
├── agents/
│   ├── plan-init-agent.md       # Creates plan, detects domains
│   ├── solution-outline-agent.md # Creates deliverables
│   ├── task-plan-agent.md       # Creates tasks
│   └── task-execute-agent.md    # Executes single task
├── commands/
│   ├── plan-manage.md           # Init + refine phases
│   ├── plan-execute.md          # Execute + finalize phases
│   ├── pr-doctor.md
│   └── task-implement.md
└── skills/
    ├── plan-wf-skill-api/       # API contract for workflow skills
    │   ├── SKILL.md
    │   └── standards/           # Contract documents
    ├── solution-outline/        # Solution outline workflow skill
    ├── task-plan/               # Task planning workflow skill
    ├── task-implementation/     # Implementation workflow skill
    ├── task-testing/            # Testing workflow skill
    ├── plan-init/               # Init phase skill
    ├── plan-refine/             # Refine phase coordination
    ├── plan-execute/            # Execute phase coordination
    ├── plan-finalize/           # Finalize phase skill
    ├── manage-plan-documents/   # Request/Solution document CRUD
    ├── manage-solution-outline/ # Solution outline queries
    ├── manage-tasks/            # Tasks + steps CRUD
    ├── manage-files/            # Generic file I/O
    ├── manage-config/           # config.toon domain
    ├── manage-references/       # references.toon domain
    ├── manage-lifecycle/        # status.toon + phases
    ├── git-workflow/
    ├── pr-workflow/
    └── sonar-workflow/

.plan/                           # Plan storage (per project)
├── plans/                       # Active plans
│   └── {plan-name}/
│       ├── request.md
│       ├── solution_outline.md
│       ├── config.toon
│       └── tasks/
└── archived-plans/              # Completed plans
```

## Dependencies

- **plan-marshall** - Script runner, file operations base, domain skill configuration
- **pm-plugin-development** - Plugin domain skills (plugin-architecture, plugin-create, plugin-maintain)
- **pm-dev-builder** - Build execution (maven/npm)
- **pm-dev-java** - Java domain skills (java-core, java-cdi, junit-core, etc.)
- **pm-dev-frontend** - JavaScript domain skills (cui-javascript, cui-jsdoc, etc.)

## Installation

```bash
/plugin install pm-workflow
```
