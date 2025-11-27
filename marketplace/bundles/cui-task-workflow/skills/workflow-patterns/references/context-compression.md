# Context Compression

Strategies for mid-session context reduction to maintain quality in long-running sessions.

## Compression Triggers

### Automatic Triggers

| Trigger | Threshold | Action |
|---------|-----------|--------|
| Context usage | >70% | Consider compression |
| Quality degradation | 3+ repeated errors | Force compression |
| Implementation drift | Architecture violations | Urgent compression |

### Manual Triggers

- Before session handoff
- After completing major milestone
- When switching focus areas
- Before spawning new agents

---

## Content Classification

### High Value (Preserve)

Always retain in context:
- Architectural decisions and rationale
- Interface definitions and contracts
- Hard constraints and requirements
- Current task specification
- Active blockers

### Medium Value (Summarize)

Compress to essentials:
- Implementation details -> Interface summary
- Debugging sessions -> Final solution only
- Exploration -> Decisions made
- File contents -> Key sections only

### Low Value (Remove)

Safe to remove:
- Superseded decisions
- Failed approaches (unless instructive)
- Verbose error messages (keep summary)
- Intermediate states
- Exploration dead-ends

---

## Compression Workflow

### Step 1: Identify Compression Need

Check context usage and quality indicators:
- Repeated suggestions for already-implemented features
- Circular modifications (A -> B -> A)
- Forgetting recent decisions
- Suggesting incompatible approaches

### Step 2: Classify Content

Categorize current context:

```
HIGH VALUE:
- Task: Implement authentication
- Constraint: Must support SSO
- Decision: Using JWT with refresh tokens

MEDIUM VALUE:
- Implementation of login function (500 lines)
- Debugging session for token validation

LOW VALUE:
- Failed attempt using session cookies
- Verbose stack traces
```

### Step 3: Compress Medium Value

Transform implementation details to summaries:

**Before** (high token cost):
```typescript
// Full 200-line implementation
export class AuthService {
  private tokenStore: Map<string, Token>;
  // ... 200 lines of implementation
}
```

**After** (low token cost):
```
AuthService: login(credentials) -> Token
            logout(token) -> void
            refresh(token) -> Token
            validate(token) -> boolean
```

### Step 4: Persist to Memory (Optional)

For cross-session preservation:

```bash
python3 manage-memory.py save \
  --category context \
  --identifier "auth-implementation" \
  --content '{"interfaces": ["AuthService"], "decisions": ["JWT", "refresh rotation"]}'
```

### Step 5: Remove Low Value

Explicitly drop:
- Failed approaches
- Verbose errors
- Intermediate states

---

## Retrieval Patterns

### On-Demand Retrieval

When compressed content needed:

1. Check memory layer first
2. Read specific files if needed
3. Request only relevant sections

### Proactive Loading

Before starting related work:

1. Query memory for related context
2. Load relevant interfaces
3. Review decisions that apply

---

## Integration with Handoff Protocol

### Pre-Handoff Compression

Before creating handoff:
1. Compress current context
2. Persist important context to memory
3. Include memory refs in handoff

```json
{
  "handoff": {
    "memory_refs": ["2025-11-26-auth-context"],
    "context": {
      "compressed_from": "Full implementation session",
      "preserved": ["interfaces", "decisions", "constraints"]
    }
  }
}
```

### Post-Handoff Loading

When receiving handoff:
1. Load memory refs
2. Request only needed details
3. Avoid loading full file contents

---

## When NOT to Compress

### Active Implementation

Don't compress when:
- Actively modifying specific code
- Debugging a specific issue
- Within a single focused task

### Critical Context

Never compress:
- Security requirements
- Breaking change constraints
- Active error states
- Pending validations

### Near Completion

Avoid compression when:
- Task is >80% complete
- Only verification remaining
- About to commit changes

---

## Compression Examples

### Debugging Session Compression

**Before**:
```
Error: Cannot read property 'id' of undefined
Stack trace: ...
Attempted fix 1: Add null check - failed
Attempted fix 2: Initialize default - failed
Root cause: Race condition in async initialization
Fix: Added await to initialization call
Verification: Test passes
```

**After**:
```
Issue: Race condition in async initialization
Fix: Added await to initialization call (line 42)
```

### Implementation Session Compression

**Before**:
```
Reading file src/auth/service.ts...
[500 lines of code]
Modifying login function...
[implementation details]
Adding validation...
[more details]
```

**After**:
```
Modified: src/auth/service.ts
Changes: login(), validate(), refresh()
Interfaces: AuthService, Token, Credentials
Decisions: JWT with 24h expiry, refresh rotation
```

### Exploration Compression

**Before**:
```
Option 1: Session cookies
  Pros: Simple, built-in
  Cons: No mobile support, CSRF risk
Option 2: JWT
  Pros: Stateless, mobile-friendly
  Cons: Token revocation complexity
Option 3: OAuth
  Pros: Delegated auth
  Cons: Overkill for internal app
Decision: JWT with refresh tokens
```

**After**:
```
Decision: JWT with refresh tokens
Rationale: Stateless + mobile support
Rejected: Sessions (no mobile), OAuth (overkill)
```
