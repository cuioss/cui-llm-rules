# Handoff Protocol

Structured state transfer between agents and skills in multi-agent workflows.

## When to Use

Use the handoff protocol when:
- Transferring work between specialized agents
- Completing a workflow stage before the next begins
- Preserving context across session boundaries
- Coordinating parallel task results

Do NOT use handoffs for:
- Simple tool calls within a single agent
- Read-only operations
- Stateless queries

---

## Handoff Structure

### Minimal Handoff

For simple task completion where context is limited.

```json
{
  "handoff": {
    "from": "code-reviewer",
    "to": "test-writer",
    "task": "Code review completed for auth module",
    "status": "completed",
    "artifacts": ["src/auth/login.ts"],
    "next_action": "Write unit tests for login function"
  }
}
```

**Use when**:
- Single file or function scope
- Clear next action
- Minimal context needed

### Standard Handoff

For multi-step workflows with moderate complexity.

```json
{
  "handoff": {
    "from": "backend-specialist",
    "to": "frontend-specialist",
    "timestamp": "2025-11-26T10:30:00Z",
    "task": {
      "description": "API endpoints for user authentication",
      "status": "completed",
      "progress": "100%"
    },
    "artifacts": {
      "files": ["src/api/auth.ts", "src/types/auth.ts"],
      "interfaces": ["AuthService", "TokenPayload"],
      "decisions": ["JWT with 24h expiry", "Refresh token rotation"]
    },
    "context": {
      "dependencies": ["jsonwebtoken@9.0.0"],
      "constraints": ["Must support SSO integration"],
      "notes": "Rate limiting configured at 100 req/min"
    },
    "next": {
      "action": "Build login form component",
      "focus": "Token storage and refresh logic",
      "blockers": []
    }
  }
}
```

**Use when**:
- Multiple files involved
- Architectural decisions made
- Specific constraints to communicate

### Full Handoff

For complex orchestration with validation requirements.

See `templates/handoff-full.json` for complete structure.

**Use when**:
- Wave-based processing
- Multiple integration points
- Validation checkpoints required
- Memory layer integration needed

---

## Format Options

### JSON Format

Preferred for programmatic consumption and validation.

```json
{
  "handoff": {
    "from": "agent-a",
    "to": "agent-b",
    "artifacts": ["file1.ts", "file2.ts"]
  }
}
```

### Markdown Format

Acceptable for human-readable handoffs.

```markdown
## Handoff: agent-a -> agent-b

### Task
Implement authentication service

### Status
Completed (100%)

### Artifacts
- `src/auth/service.ts` - Main service
- `src/auth/types.ts` - Type definitions

### Next Action
Write integration tests
```

---

## Memory Layer Integration

Handoffs can reference memory layer files for persistent context:

```json
{
  "handoff": {
    "memory_refs": [
      "2025-11-26-auth-feature",
      "task-42"
    ]
  }
}
```

### Saving Handoff to Memory

For cross-session handoffs:

```bash
python3 manage-memory.py save \
  --category handoffs \
  --identifier "task-42" \
  --content '{"task": "Auth feature", "progress": "70%"}'
```

### Loading Previous Handoff

```bash
python3 manage-memory.py load \
  --category handoffs \
  --identifier "task-42"
```

---

## Anti-Patterns

### Over-specifying Implementation Details

**Bad**: Including full file contents in handoff
```json
{
  "artifacts": {
    "file_contents": "// 500 lines of code..."
  }
}
```

**Good**: Reference files and summarize interfaces
```json
{
  "artifacts": {
    "files": ["src/auth.ts"],
    "interfaces": ["AuthService: login(), logout(), refresh()"]
  }
}
```

### Missing Critical Context

**Bad**: No constraints or decisions
```json
{
  "next_action": "Build the frontend"
}
```

**Good**: Include constraints and decisions
```json
{
  "context": {
    "constraints": ["Must work offline", "Max 100kb bundle"],
    "decisions": ["Using IndexedDB for offline storage"]
  },
  "next": {
    "action": "Build the frontend",
    "focus": "Offline-first data layer"
  }
}
```

### Circular Handoffs

**Bad**: A -> B -> A without progress
```
Agent A: "Needs B to decide X"
Agent B: "Needs A to implement Y first"
Agent A: "Can't implement Y without X"
```

**Good**: Break the cycle with explicit decision
```json
{
  "decisions": [
    {
      "decision": "Defaulting X to option 1",
      "rationale": "Unblocks Y implementation",
      "alternatives": ["Revisit if option 1 causes issues"]
    }
  ]
}
```

---

## Examples

### Simple Code Review Handoff

```json
{
  "handoff": {
    "from": "code-reviewer",
    "to": "developer",
    "task": "Review of PR #123",
    "status": "completed",
    "artifacts": ["src/utils/format.ts"],
    "next_action": "Address 2 minor comments, then merge"
  }
}
```

### Multi-Agent Feature Implementation

```json
{
  "handoff": {
    "from": "backend-specialist",
    "to": "frontend-specialist",
    "timestamp": "2025-11-26T14:00:00Z",
    "task": {
      "description": "Real-time collaboration backend",
      "status": "completed",
      "progress": "100%"
    },
    "artifacts": {
      "files": ["src/websocket/handler.ts", "src/types/events.ts"],
      "interfaces": ["WebSocketEvents", "OperationPayload"],
      "contracts": {
        "events": ["connection", "message", "disconnect"],
        "message_types": ["operation", "presence", "ack"]
      },
      "decisions": [
        {
          "decision": "Batch operations every 100ms",
          "rationale": "Balance latency vs throughput"
        }
      ]
    },
    "context": {
      "dependencies": ["ws@8.0.0"],
      "constraints": ["Max 1000 ops in memory per document"]
    },
    "next": {
      "action": "Build React components for real-time updates",
      "focus": "Optimistic UI with rollback capability",
      "context_budget": 8500
    }
  }
}
```

### Wave Completion Handoff

```json
{
  "handoff": {
    "meta": {
      "from": "orchestrator",
      "to": "integration-validator",
      "wave": 2
    },
    "task": {
      "description": "Wave 2: Service implementations",
      "status": "completed",
      "completed": ["AuthService", "UserService", "DataService"]
    },
    "validation": {
      "integration_points": [
        "AuthService -> UserService token validation",
        "DataService -> AuthService permission checks"
      ],
      "tests_required": ["Cross-service integration tests"]
    },
    "next": {
      "action": "Validate all integration points",
      "priority": "high"
    }
  }
}
```
