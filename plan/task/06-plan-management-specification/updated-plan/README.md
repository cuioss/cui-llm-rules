# Refactoring Plan: Task Commands Split

## Overview

Refactor the current unified `/task` command into two focused commands with clear separation of concerns:

| Command | Purpose | Primary Phases |
|---------|---------|----------------|
| `/plan-manage` | Plan lifecycle management (create, list, cleanup, refine) | init, refine |
| `/plan-execute` | Plan execution (implement, verify, finalize) | implement, verify, finalize |

## Documents

### Command Specifications
- [plan-manage.md](plan-manage.md) - Management command specification
- [plan-execute.md](plan-execute.md) - Execution command specification

### Skill Updates
- [phase-management-updates.md](phase-management-updates.md) - Changes to phase-management skill

### Migration
- [migration.md](migration.md) - Migration steps from current to new structure

## Rationale

### Current State Issues

1. **Single command doing too much**: `/task` handles creation, management, and execution
2. **Unclear user intent**: Without parameters, user must understand phase routing
3. **No cleanup mechanism**: Completed plans accumulate without removal option
4. **No list view**: Cannot see all plans with their current state

### Target State Benefits

1. **Clear separation**: Management vs execution are distinct concerns
2. **Interactive discovery**: Both commands offer numbered selection for plans
3. **Lifecycle management**: Cleanup of completed plans
4. **Phase-appropriate routing**: Each command handles appropriate phases

## Architecture Changes

```
Before:
  /task ──► phase-management ──► plan-init/refine/implement/verify/finalize

After:
  /plan-manage ──► phase-management (operations: list, cleanup, init, refine)
  /plan-execute ──► phase-management (operations: execute, continue)
```

## Implementation Order

1. **Create specifications** (this directory)
2. **Update phase-management skill** - Add new operations
3. **Create plan-manage command** - New command file
4. **Refactor task.md to plan-execute** - Strip management, add execution focus
5. **Update documentation** - README, examples
6. **Remove old /task command** - Final cleanup
