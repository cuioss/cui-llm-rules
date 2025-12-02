---
name: analysis-api
description: Defines the unified API contract for domain analysis skills. Load this skill to implement a domain-specific analyzer.
allowed-tools: Read
---

# Analysis API Skill

**Role**: API contract definition for domain analysis skills. This skill defines the interface that all domain analysis skills must implement.

**Usage**: Domain analysis skills load this skill to ensure they implement the correct API contract.

## API Contract

### Operation: analyze

Domain analysis skills implement this operation to analyze task requirements and identify components.

**Input Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier (e.g., "add-caching") |
| `task_description` | string | Yes | Task description from plan config |
| `issue_context` | string | No | GitHub issue body content |
| `build_system` | string | No | Build system: `maven`, `gradle`, `npm` |

**Input Example**:
```yaml
plan_id: "add-caching"
task_description: "Implement Redis caching for UserService"
issue_context: |
  ## Description
  Add caching layer to reduce database load...
build_system: "maven"
```

**Output Structure**:

```yaml
analysis_result:
  status: "success|error"
  error_message: "{message}"           # Only if status=error
  components:
    - name: "{component-name}"
      type: "{domain-type}"            # See Component Types
      scope: "create|modify|refactor"
      path: "{relative-path}"
      dependencies:
        - "{dependency-1}"
      complexity: "low|medium|high"
      notes: "{additional-context}"
      # Domain-specific fields (see below)
```

**Output Example**:
```yaml
analysis_result:
  status: "success"
  components:
    - name: "CacheConfig"
      type: "config"
      scope: "create"
      path: "src/main/java/com/example/config/CacheConfig.java"
      dependencies:
        - "spring-boot-starter-data-redis"
      complexity: "medium"
      notes: "Redis connection configuration"
      module: "core-service"
      test_required: true
      test_path: "src/test/java/com/example/config/CacheConfigTest.java"
```

---

## Component Types

Each domain defines its own component types:

| Domain | Skill | Types |
|--------|-------|-------|
| Plugin | `cui-plugin-development-tools:plugin-analysis` | `script`, `skill`, `command`, `agent` |
| Java | `cui-java-expert:java-analysis` | `class`, `interface`, `module`, `package`, `config` |
| JavaScript | `cui-frontend-expert:js-analysis` | `module`, `class`, `web-component`, `utility`, `config` |

---

## Domain-Specific Fields

### Plugin Domain

| Field | Type | Description |
|-------|------|-------------|
| `bundle` | string | Target bundle name |

### Java Domain

| Field | Type | Description |
|-------|------|-------------|
| `module` | string | Maven/Gradle module name |
| `test_required` | boolean | Whether tests are needed |
| `test_path` | string | Path to test file |

### JavaScript Domain

| Field | Type | Description |
|-------|------|-------------|
| `test_required` | boolean | Whether tests are needed |
| `test_path` | string | Path to test file |

---

## Scope Values

| Value | Meaning | Indicators |
|-------|---------|------------|
| `create` | New component | "implement", "add", "create", "new" |
| `modify` | Change existing | "fix", "update", "modify", "change" |
| `refactor` | Restructure | "refactor", "reorganize", "migrate" |

---

## Complexity Assessment

| Factor | Low | Medium | High |
|--------|-----|--------|------|
| Files affected | 1-3 | 4-8 | 9+ |
| Cross-module/bundle | No | 1 | 2+ |
| Breaking changes | None | Internal | Public API |
| Dependencies | 0-2 | 3-5 | 6+ |
| Test coverage needed | Unit only | Unit + Integration | Full suite |

---

## Handoff Protocol

```
┌─────────────┐                                              ┌─────────────┐
│             │    analyze(plan_id, task, issue, build)      │   domain    │
│ plan-refine │ ────────────────────────────────────────────►│  analysis   │
│             │                                              │   skill     │
│             │◄────────────────────────────────────────────│             │
└─────────────┘    analysis_result{status, components[]}     └─────────────┘
       │
       │ components[]
       ▼
┌─────────────┐                                              ┌─────────────┐
│             │    generate-tasks(plan_id, components)       │  plan-type  │
│ plan-refine │ ────────────────────────────────────────────►│    skill    │
│             │                                              │             │
│             │◄────────────────────────────────────────────│             │
└─────────────┘    (writes directly to plan.md)              └─────────────┘
```

### Flow

1. `plan-refine` reads plan context (task description, issue, config)
2. Based on `plan_type`, delegates to appropriate domain analysis skill
3. Domain analysis skill explores codebase, identifies components
4. Returns `analysis_result` with structured `components[]`
5. `plan-refine` passes components to plan-type skill's `generate-tasks`
6. Plan-type skill writes tasks directly to plan.md

---

## Error Handling

### Component Not Found

| Scope | Action |
|-------|--------|
| `create` | Continue (expected - component doesn't exist yet) |
| `modify` | Warn and ask for clarification |
| `refactor` | Error and request correct path |

### Ambiguous Component

When multiple files match a component name:
1. List all matches with paths
2. Ask user to select correct one
3. Re-analyze with specific path

### Analysis Failure

Return error result:
```yaml
analysis_result:
  status: "error"
  error_message: "Could not determine module structure"
  components: []
```

---

## Implementation Requirements

Domain analysis skills that implement this API must:

1. **Load this skill**: Reference `planning:analysis-api` for contract compliance
2. **Implement `analyze` operation**: Accept input, return output per contract
3. **Return structured components**: All required fields populated
4. **Include domain-specific fields**: Add fields relevant to the domain
5. **Assess complexity**: Use complexity matrix for consistent assessment
6. **Handle errors gracefully**: Return error status with message

### Implementation Template

```markdown
---
name: {domain}-analysis
description: Analyzes {domain} tasks. Implements planning:analysis-api contract.
allowed-tools: Read, Glob, Grep, Bash
---

# {Domain} Analysis Skill

**Role**: Domain analysis skill for {domain} tasks.

**API**: Implements `planning:analysis-api` contract.

## Operation: analyze

**Contract**: Load `planning:analysis-api` for input/output specification.

**Domain-Specific Process**:
1. Parse task intent
2. Detect project structure
3. Explore affected components
4. Identify dependencies
5. Determine test requirements (if applicable)
6. Assess complexity
7. Return components

**Component Types**: {list domain types}

**Domain-Specific Fields**: {list domain fields}
```

---

## Integration

### Calling Skills

| Skill | Purpose |
|-------|---------|
| `planning:plan-refine` | Primary caller - delegates analysis |

### Implementing Skills

| Skill | Domain |
|-------|--------|
| `cui-plugin-development-tools:plugin-analysis` | Plugin components |
| `cui-java-expert:java-analysis` | Java implementation |
| `cui-frontend-expert:js-analysis` | JavaScript implementation |

### Plan-Type Skills (consumers)

| Skill | Receives components from |
|-------|-------------------------|
| `planning:plan-type-plugin` | `plugin-analysis` |
| `planning:plan-type-java` | `java-analysis` |
| `planning:plan-type-javascript` | `js-analysis` |

---

## Quality Checklist

For implementing skills:

- [ ] Loads `planning:analysis-api` for contract reference
- [ ] Implements `analyze` operation with correct signature
- [ ] Returns `analysis_result` with `status` and `components[]`
- [ ] Includes all required component fields
- [ ] Adds domain-specific fields
- [ ] Assesses complexity using standard matrix
- [ ] Handles errors with status and message
