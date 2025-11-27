# CUI Task Workflow

Goal-based development workflow from task implementation to PR quality verification.

## Purpose

Complete development workflow with two simple commands:
1. **IMPLEMENT** - Transform tasks into verified code
2. **DOCTOR** - Diagnose and fix PR issues

## Commands

### /task-implement (IMPLEMENT)
Implement GitHub issues or standalone tasks with full verification.

**Modes**:
- FULL: Review → Plan → Execute (GitHub issues)
- PLAN: Plan → Execute (task descriptions)
- QUICK: Execute only (immediate implementation)

**Examples**:
```
/task-implement task=123
/task-implement task="Add validation" quick
/task-implement task=456 push
```

### /pr-doctor (DOCTOR)
Diagnose and fix PR issues (build, reviews, Sonar).

**Checks**:
- build: Fix compilation errors
- reviews: Respond to review comments
- sonar: Fix quality issues
- all: Complete PR workflow

**Examples**:
```
/pr-doctor pr=123
/pr-doctor checks=sonar
/pr-doctor auto-fix
```

## Skills

5 specialized skills provide all business logic:
- **cui-task-planning** - Review, Plan, Execute workflows
- **pr-workflow** - Fetch Comments, Handle Review
- **sonar-workflow** - Fetch Issues, Fix Issues
- **cui-git-workflow** - Commit workflow
- **workflow-patterns** - Handoff protocols (uses TOON format for 50% token reduction)

## Benefits

**Before**: 6 commands, 1,161 lines
**After**: 2 commands, 270 lines
**Reduction**: 77% code reduction

**Simplified Architecture**:
```
User Goal → One Command → Skills → Result

IMPLEMENT: /task-implement (116 lines)
DOCTOR:    /pr-doctor     (142 lines)
```

## Installation

```bash
/plugin install cui-task-workflow
```

## Architecture

```
cui-task-workflow/
├── README.md           # This file
├── commands/           # 2 goal-based commands
│   ├── task-implement.md
│   └── pr-doctor.md
└── skills/             # 5 skills with workflows
    ├── workflow-patterns/
    │   ├── SKILL.md    # Orchestration patterns overview
    │   ├── templates/  # Handoff TOON templates (token-efficient format)
    │   └── references/ # Protocol documentation
    ├── cui-task-planning/
    │   ├── SKILL.md    # Plan, Execute, Review workflows
    │   ├── scripts/    # 3 Python scripts
    │   └── standards/  # Planning standards
    ├── cui-git-workflow/
    │   ├── SKILL.md    # Commit workflow
    │   ├── scripts/    # 1 Python script
    │   └── standards/  # Git commit standards
    ├── pr-workflow/
    │   ├── SKILL.md    # Fetch Comments, Handle Review workflows
    │   └── scripts/    # 2 Python scripts
    └── sonar-workflow/
        ├── SKILL.md    # Fetch Issues, Fix Issues workflows
        └── scripts/    # 2 Python scripts
```

## Dependencies

### Inter-Bundle Dependencies
- **builder-maven** (required) - Commands use /maven-build-and-fix for verification
- **cui-utilities** (required) - claude-memory skill for session persistence
- **cui-java-expert** (optional) - For Java implementation delegation
- **cui-frontend-expert** (optional) - For JavaScript implementation delegation

### External Dependencies
- GitHub CLI (`gh`) for issue and PR operations
- Maven wrapper (`./mvnw`) for build verification
- SonarQube MCP tool for Sonar issue fetching

## Bundle Statistics

- **Commands**: 2 (minimal wrappers, ~130 lines each)
- **Skills**: 5 (workflow-patterns + 4 with 8 Python scripts total)
- **Total Lines**: 258 command lines (77% reduction from 1,161)

## Support

- Repository: https://github.com/cuioss/cui-llm-rules
- Bundle: marketplace/bundles/cui-task-workflow/
