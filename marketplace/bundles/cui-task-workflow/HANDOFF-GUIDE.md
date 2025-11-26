# Handoff Protocol Guide

Structured state transfer between agents, skills, and workflow stages in cui-task-workflow.

## The Problem: Context Loss

When orchestrating multi-step workflows, critical information gets lost:

1. **Session Interruption** - User closes session mid-workflow, loses progress
2. **Agent Handoff** - Task A completes but Task B doesn't know what was decided
3. **Context Pollution** - Implementation details crowd out architectural context
4. **Parallel Execution** - Multiple agents produce incompatible implementations

The handoff protocol solves these problems through structured state transfer.

---

## Core Concept

A **handoff** is a structured JSON document that captures the essential state needed for the next workflow step, while excluding noise that would pollute context.

```
┌─────────────┐     handoff      ┌─────────────┐
│   Task A    │ ──────────────▶  │   Task B    │
│  (source)   │                  │  (target)   │
└─────────────┘                  └─────────────┘
      │                                │
      │  artifacts                     │  uses
      │  decisions                     │  interfaces
      │  constraints                   │  constraints
      ▼                                ▼
  ┌─────────┐                    ┌─────────┐
  │ Memory  │                    │ Memory  │
  │ Layer   │◀───────────────────│ Layer   │
  └─────────┘    (optional)      └─────────┘
```

---

## Handoff Levels

### Minimal Handoff

For simple task completions with clear next actions.

```json
{
  "handoff": {
    "from": "code-reviewer",
    "to": "test-writer",
    "task": "Review completed",
    "status": "completed",
    "artifacts": ["src/auth/login.ts"],
    "next_action": "Write unit tests"
  }
}
```

**Use when**: Single file scope, clear next step, minimal context needed.

### Standard Handoff

For multi-step workflows with moderate complexity.

```json
{
  "handoff": {
    "from": "backend-specialist",
    "to": "frontend-specialist",
    "timestamp": "2025-11-26T10:30:00Z",
    "task": {
      "description": "API endpoints for authentication",
      "status": "completed",
      "progress": "100%"
    },
    "artifacts": {
      "files": ["src/api/auth.ts"],
      "interfaces": ["AuthService", "TokenPayload"],
      "decisions": ["JWT with 24h expiry", "Refresh rotation"]
    },
    "context": {
      "dependencies": ["jsonwebtoken@9.0.0"],
      "constraints": ["Must support SSO"],
      "notes": "Rate limit: 100 req/min"
    },
    "next": {
      "action": "Build login form",
      "focus": "Token storage and refresh",
      "blockers": []
    }
  }
}
```

**Use when**: Multiple files, architectural decisions made, specific constraints.

### Full Handoff

For complex orchestration with validation requirements.

**Use when**: Wave-based processing, multiple integration points, memory layer integration.

See: `skills/workflow-patterns/templates/handoff-full.json`

---

## Tools and Skills

### workflow-patterns Skill

The primary skill for handoff protocols:

```
Skill: cui-task-workflow:workflow-patterns
```

Provides:
- `templates/handoff-minimal.json` - Simple handoff template
- `templates/handoff-standard.json` - Multi-step workflow template
- `templates/handoff-full.json` - Complex orchestration template
- `references/handoff-protocol.md` - Complete protocol documentation

### claude-memory Skill

For persisting handoffs across sessions:

```
Skill: cui-utilities:claude-memory
```

Provides:
- Memory CRUD operations
- `handoffs` category for workflow state
- `context` category for session snapshots

---

## Integration Points

### 1. cui-task-planning Skill

**When**: Transitioning from Plan to Execute workflow.

```python
# After creating plan, generate handoff
handoff = {
    "from": "plan-workflow",
    "to": "execute-workflow",
    "task": {"id": 1, "name": task_name, "status": "pending"},
    "artifacts": {"files": [plan_file]},
    "next": {"action": "Execute first task", "focus": first_task_goal}
}
```

**Memory integration**:
```bash
# Save plan for session recovery
python3 manage-memory.py save \
  --category context \
  --identifier "feature-auth" \
  --content '{"plan_file": "plan-issue-42.md", "current_task": 1}'
```

### 2. orchestrate-workflow Command

**When**: Starting workflow, between tasks, on completion.

**Step 0 - Check for pending workflow**:
```bash
python3 manage-memory.py list --category handoffs
# If found: offer to resume
```

**Between tasks - Save progress**:
```bash
python3 manage-memory.py save \
  --category handoffs \
  --identifier "workflow-42" \
  --content '{"issue": 42, "current_task": 3, "completed": [1,2]}'
```

**On completion - Cleanup**:
```bash
python3 manage-memory.py cleanup --category handoffs --pattern "workflow-42*"
```

### 3. orchestrate-task Command

**When**: Receiving task from orchestrator, returning result.

**Accept handoff input**:
```
/orchestrate-task task="Build login form" handoff='{"from": "api-task", "artifacts": {"interfaces": ["AuthService"]}}'
```

**Return structured result with handoff**:
```json
{
  "status": "SUCCESS",
  "task_executed": "Build login form",
  "files_modified": ["src/components/Login.tsx"],
  "handoff": {
    "from": "login-form-task",
    "to": "next-task",
    "artifacts": {"files": ["src/components/Login.tsx"]},
    "decisions": ["Using controlled form pattern"],
    "next": {"action": "Add form validation"}
  }
}
```

---

## Step-by-Step: Adding Handoff to Your Command

### Step 1: Load Required Skills

```markdown
## PREREQUISITES

Load required skills:
```
Skill: cui-task-workflow:cui-task-planning
Skill: cui-utilities:claude-memory
Skill: cui-task-workflow:workflow-patterns
```
```

### Step 2: Accept Handoff Parameter

```markdown
## PARAMETERS

- **task**: Task description
- **handoff**: (Optional) Handoff structure from previous task (JSON)
```

### Step 3: Process Incoming Handoff

```markdown
### Step 0: Process Handoff Input (If Provided)

If `handoff` parameter provided:
1. Parse handoff JSON
2. Extract: artifacts.interfaces, artifacts.decisions, context.constraints
3. Load any memory_refs via claude-memory skill
```

### Step 4: Generate Outgoing Handoff

```markdown
### Final Step: Return Result with Handoff

Return structured result:
```json
{
  "status": "SUCCESS|FAILURE|BLOCKED",
  "handoff": {
    "from": "this-task",
    "to": "next-task",
    "artifacts": {...},
    "decisions": [...],
    "next": {...}
  }
}
```
```

### Step 5: Save State for Failure Recovery

```markdown
### On Failure: Save State

```bash
python3 manage-memory.py save \
  --category handoffs \
  --identifier "task-retry" \
  --content '{"task": "...", "status": "failed", "last_error": "..."}'
```
```

---

## Anti-Patterns

### Over-Specifying Details

**Bad**: Including full file contents
```json
{"artifacts": {"file_contents": "// 500 lines..."}}
```

**Good**: Reference files, summarize interfaces
```json
{"artifacts": {"files": ["src/auth.ts"], "interfaces": ["login(), logout()"]}}
```

### Missing Critical Context

**Bad**: No constraints
```json
{"next_action": "Build frontend"}
```

**Good**: Include constraints and decisions
```json
{
  "context": {"constraints": ["Must work offline"]},
  "decisions": ["Using IndexedDB"],
  "next": {"action": "Build frontend", "focus": "Offline-first data layer"}
}
```

### Circular Handoffs

**Bad**: A -> B -> A without progress

**Good**: Break cycle with explicit decision
```json
{
  "decisions": [{"decision": "Default X to option 1", "rationale": "Unblocks Y"}]
}
```

---

## Complete Example: Feature Implementation

```
Issue #42: Add user authentication

┌────────────────────────────────────────────────────────────────┐
│                    /orchestrate-workflow                        │
└────────────────────────────────────────────────────────────────┘
                              │
         Step 0: Check memory │ (none found)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Plan Workflow                                            │
│   Output: plan-issue-42.md                                       │
│   Handoff: {to: "execute", artifacts: {files: ["plan-issue-42.md"]}} │
│   Memory: save context/auth-feature                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: /orchestrate-task task="Implement AuthService"          │
│   Input handoff: {interfaces: [], constraints: ["JWT"]}         │
│   Output: {status: "SUCCESS", decisions: ["24h expiry"]}        │
│   Memory: save handoffs/workflow-42 (task 1 complete)           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: /orchestrate-task task="Build login form"               │
│   Input handoff: {interfaces: ["AuthService"], decisions: [...]}│
│   Output: {status: "SUCCESS", files: ["Login.tsx"]}             │
│   Memory: save handoffs/workflow-42 (task 2 complete)           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ Step 7: Cleanup Memory                                           │
│   Delete: handoffs/workflow-42                                   │
│   Save: context/completed-42 (summary)                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## References

- `skills/workflow-patterns/SKILL.md` - Workflow patterns overview
- `skills/workflow-patterns/references/handoff-protocol.md` - Complete protocol
- `skills/workflow-patterns/references/context-compression.md` - When to compress
- `skills/workflow-patterns/templates/` - JSON templates
- `../cui-utilities/skills/claude-memory/SKILL.md` - Memory operations
