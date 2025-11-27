# Integration Validation

Patterns for validating consistency across parallel skill executions and multi-agent workflows.

## Validation Types

### Interface Validation

Ensures type and contract alignment between components.

**Check for**:
- Type signature mismatches
- Missing required properties
- Incompatible return types
- Parameter order differences

**Example issue**:
```
Frontend expects: { userId: string, name: string }
Backend returns:  { user_id: number, userName: string }
```

### Contract Validation

Ensures API contracts are honored.

**Check for**:
- Endpoint path mismatches
- HTTP method disagreements
- Request/response schema differences
- Error format inconsistencies

**Example issue**:
```
API spec: POST /api/users
Frontend: PUT /api/user
```

### Dependency Validation

Ensures version and import consistency.

**Check for**:
- Version conflicts
- Duplicate dependencies
- Missing peer dependencies
- Incompatible versions

**Example issue**:
```
Service A: lodash@4.17.21
Service B: lodash@3.10.1 (incompatible)
```

### State Validation

Ensures shared state coherence.

**Check for**:
- Race conditions
- Stale state usage
- Missing state synchronization
- Conflicting state updates

---

## Validation Checkpoints

### Pre-Execution Validation

Before parallel execution:

| Check | Purpose |
|-------|---------|
| Interface definitions | All agents use same interfaces |
| Dependency versions | No version conflicts |
| Shared constraints | All agents aware of constraints |
| Task boundaries | No overlapping modifications |

### Post-Execution Validation

After parallel execution:

| Check | Purpose |
|-------|---------|
| Interface implementation | Types match definitions |
| Contract compliance | APIs match specifications |
| Integration points | Cross-component calls work |
| State consistency | Shared state is coherent |

### Wave Boundary Validation

Between processing waves:

| Check | Purpose |
|-------|---------|
| Wave outputs | All tasks in wave completed |
| Dependency satisfaction | Next wave inputs available |
| Conflict detection | No conflicting changes |
| Merge feasibility | Changes can be combined |

---

## Common Issues and Prevention

### Type Mismatches

**Issue**: Different agents use different type names or structures.

**Prevention**:
- Define canonical types in shared location
- Include type definitions in handoffs
- Validate types at integration points

**Detection**:
```
Check: AuthService.login() returns Token
Found: AuthService.login() returns string
Mismatch: Expected Token type, got primitive
```

### API Contract Violations

**Issue**: Frontend and backend disagree on API shape.

**Prevention**:
- Define API contracts before implementation
- Include contracts in agent context
- Generate types from contracts

**Detection**:
```
Contract: GET /users/:id -> User
Implementation: GET /users/:id -> { data: User }
Violation: Response wrapped in unexpected object
```

### Race Conditions

**Issue**: Concurrent operations corrupt shared state.

**Prevention**:
- Identify shared resources before parallel execution
- Define synchronization points
- Use wave-based processing for dependent tasks

**Detection**:
```
Agent A: Reads counter = 5
Agent B: Reads counter = 5
Agent A: Writes counter = 6
Agent B: Writes counter = 6
Expected: counter = 7
```

### Missing Error Handlers

**Issue**: One component throws, another doesn't catch.

**Prevention**:
- Define error contracts
- Include error handling in handoffs
- Validate error propagation

---

## Validation Checklist

### Interface Checklist

- [ ] All shared types defined in one location
- [ ] Type names consistent across components
- [ ] Property names match (camelCase vs snake_case)
- [ ] Nullability handled consistently
- [ ] Generic types instantiated correctly

### Contract Checklist

- [ ] API paths match
- [ ] HTTP methods match
- [ ] Request bodies match schema
- [ ] Response bodies match schema
- [ ] Error responses defined and handled

### Dependency Checklist

- [ ] No version conflicts
- [ ] Peer dependencies satisfied
- [ ] No duplicate packages
- [ ] Lockfile in sync

### State Checklist

- [ ] Shared state identified
- [ ] Synchronization points defined
- [ ] Race conditions addressed
- [ ] State initialization ordered correctly

---

## Validation in Handoffs

Include validation requirements in handoffs:

```json
{
  "handoff": {
    "validation": {
      "interfaces": ["AuthService", "Token"],
      "contracts": ["POST /auth/login", "POST /auth/refresh"],
      "integration_points": [
        "AuthService -> TokenStore",
        "LoginForm -> AuthService"
      ],
      "tests_required": [
        "Auth flow integration test",
        "Token refresh test"
      ]
    }
  }
}
```

---

## Validation Examples

### Post-Wave Validation

After Wave 2 (service implementations):

```
VALIDATION REPORT - Wave 2

Interface Validation:
  ✓ AuthService matches IAuthService
  ✓ UserService matches IUserService
  ✗ DataService.fetch() returns Promise<Data[]>, expected Data[]

Contract Validation:
  ✓ POST /auth/login - implemented correctly
  ✓ GET /users/:id - implemented correctly
  ✗ PUT /data/:id - missing error response for 404

Dependency Validation:
  ✓ No version conflicts
  ✓ All peer dependencies satisfied

State Validation:
  ✓ AuthState synchronized
  ✗ DataCache - potential race condition in invalidation

ACTIONS REQUIRED:
1. Fix DataService.fetch() return type
2. Add 404 error response to PUT /data/:id
3. Add mutex to DataCache.invalidate()
```

### Pre-Merge Validation

Before combining parallel changes:

```
MERGE VALIDATION

File Conflicts:
  ✗ src/types/index.ts - both agents modified

Interface Conflicts:
  ✓ No conflicting interface definitions

Import Conflicts:
  ✗ src/services/auth.ts - different import paths

RESOLUTION:
1. Manual merge for src/types/index.ts
2. Standardize import paths in auth.ts
```
