---
name: plan-execute
description: Execute task plans - implement, verify, and finalize phases
tools: Read, Skill, Bash, AskUserQuestion, Task
---

# Plan Execute Command

Execute task plans through implementation, verification, and finalization phases.

## PARAMETERS

| Parameter | Type | Description |
|-----------|------|-------------|
| `plan` | optional | Plan name to execute (e.g., `jwt-auth`, not path) |
| `phase` | optional | Force specific phase: `implement`, `verify`, `finalize` |

**Note**: The `plan` parameter accepts the plan **name** only, not the full path. Paths are shown in displays for reference but not used as parameters.

## WORKFLOW

1. **Load phase-management skill**:
   ```
   Skill: cui-task-workflow:phase-management
   ```

2. **Execute Execute Plans workflow** with parameters:
   - `plan_name`: Value of `plan` parameter (if provided)
   - `explicit_phase`: Value of `phase` parameter (if provided)

The phase-management skill handles:
- Discovery of executable plans (implement/verify/finalize phases)
- Phase validation (rejects init/refine - use /plan-manage)
- Phase routing to appropriate skill
- Phase transitions on completion
- User interaction via AskUserQuestion

## BEHAVIOR

### Default (no parameters)

Shows executable plans for selection:

```
/plan-execute
```

Shows:
```
Executable Plans:

1. jwt-authentication [implement] - Task 3/12: "Add token validation"
   Path: {plan-storage}/jwt-authentication/
2. user-profile-api [verify] - Build verification pending
   Path: {plan-storage}/user-profile-api/

0. Exit (use /plan-manage to create or refine plans)

Select plan to execute:
```

### With plan parameter

Execute specific plan from its current phase:

```
/plan-execute plan="jwt-auth"
```

If plan is in init or refine phase:
```
Plan 'jwt-auth' is in 'refine' phase.

This command handles execution phases only (implement, verify, finalize).
Use /plan-manage to complete init/refine phases first.
```

### With phase override

Force execution of specific phase:

```
/plan-execute plan="jwt-auth" phase="verify"
```

If override is invalid:
```
Cannot skip to 'finalize' phase.

Current phase: implement
Pending tasks: 5 of 12

Complete implementation tasks first.
```

## USAGE EXAMPLES

```bash
# Select from executable plans (interactive)
/plan-execute

# Execute specific plan (continues current phase)
/plan-execute plan="jwt-auth"

# Force specific phase
/plan-execute plan="jwt-auth" phase="verify"

# Resume implementation
/plan-execute plan="jwt-auth" phase="implement"
```

## PHASE EXECUTION

### Implement Phase

Executes implementation tasks:
- Delegates to language-specific agents (java-implement-agent, etc.)
- Updates progress via plan-files skill
- Offers continuation to next task or verify phase

### Verify Phase

Runs verification checks:
- Build project
- Run tests
- Quality checks
- Documentation review

### Finalize Phase

Completes the plan:
- Commit changes
- Create/update PR
- Handle PR workflow

## RELATED

| Command | Relationship |
|---------|--------------|
| `/plan-manage` | Manage plans (init, refine, list, cleanup) |

| Skill | Purpose |
|-------|---------|
| `cui-task-workflow:phase-management` | Plan discovery, routing, workflows |
| `cui-task-workflow:plan-implement` | Implementation phase execution |
| `cui-task-workflow:plan-verify` | Verification phase execution |
| `cui-task-workflow:plan-finalize` | Finalization phase execution |
