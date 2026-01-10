# Module Selection

LLM-driven module selection using architecture data. Scripts provide DATA, the LLM provides REASONING.

---

## Data Layer (Scripts)

Scripts provide structured data for LLM consumption.

**EXECUTE**:
```bash
# Project overview
python3 .plan/execute-script.py plan-marshall:analyze-project-architecture:architecture info

# All modules with summary
python3 .plan/execute-script.py plan-marshall:analyze-project-architecture:architecture modules

# Detailed module context (for candidate modules)
python3 .plan/execute-script.py plan-marshall:analyze-project-architecture:architecture module \
  --name {module-1}
python3 .plan/execute-script.py plan-marshall:analyze-project-architecture:architecture module \
  --name {module-2}
```

Output format: `plan-marshall:analyze-project-architecture/standards/client-api.md`

---

## Reasoning Layer (LLM in solution-outline workflow)

The LLM analyzes the data and produces reasoned selection:

```markdown
## Module Selection Analysis

**Task**: {task description}

**Candidate Modules**:

| Module | Responsibility | Purpose | Relevance |
|--------|---------------|---------|-----------|
| {module-1} | "{from architecture}" | {purpose} | {HIGH/LOW - reasoning} |
| {module-2} | "{from architecture}" | {purpose} | {HIGH/LOW - reasoning} |

**Selected Module**: `{module}`

**Reasoning**: {Why this module matches the task based on responsibility and purpose}

**Package Selection**:

From `key_packages`:
- `{package}`: "{description}" with {existing components}

**Selected Package**: `{package}`

**Reasoning**: {Why this package matches based on existing components and patterns}
```

---

## Output in Deliverable

The reasoning becomes part of the deliverable documentation:

```markdown
### {N}. {Deliverable Title}

**Module Context:**
- module: {module}
- package: {package}
- placement_rationale: {reasoning for placement}
```

---

## Scoring Heuristics

For systematic module selection:

| Factor | Weight | Score Criteria |
|--------|--------|----------------|
| responsibility match | 3 | Keywords in task match responsibility |
| purpose fit | 2 | Purpose compatible with change type |
| key_packages match | 3 | Task aligns with package descriptions |
| dependency position | 2 | Correct layer for the change |

**Selection threshold**: Modules with weighted score >= 6 are candidates.

### Scoring Example

**Task**: {task description}

| Module | responsibility (3) | purpose (2) | key_packages (3) | dependency (2) | Total |
|--------|-------------------|-------------|------------------|----------------|-------|
| {module-1} | {0-3} ({reason}) | {0-2} ({purpose}) | {0-3} ({match}) | {0-2} ({layer}) | {sum} |
| {module-2} | {0-3} ({reason}) | {0-2} ({purpose}) | {0-3} ({match}) | {0-2} ({layer}) | {sum} |

**Winner**: {module with highest score >= 6}

---

## Package Placement

Within selected module, determine where new code belongs using full package structure.

### Load Complete Package Structure

**EXECUTE**:
```bash
python3 .plan/execute-script.py plan-marshall:analyze-project-architecture:architecture module \
  --name {module} --full
```

### Use key_packages as Semantic Anchors

| key_package | Description | Role |
|-------------|-------------|------|
| ...core.pipeline | "validation pipeline components" | Main logic |
| ...core.model | "domain models for tokens" | Data classes |

### Use packages for Complete Structure

| Package | has_package_info | Consideration |
|---------|------------------|---------------|
| ...core.pipeline | true | Documented, well-defined |
| ...core.util | false | Utility, less formal |
| ...core.internal | false | Internal implementation |

### Decision Matrix

| Scenario | Action |
|----------|--------|
| Task matches key_package description | Place in that key_package |
| Task needs utility location | Check for existing util package |
| New cross-cutting concern | Create new package (document reasoning) |
| Unclear placement | Check has_package_info packages first |

### Validation

- New class follows existing naming patterns (e.g., *Validator suffix)
- Package aligns with module's responsibility scope
- Prefer packages with package_info (better documented)

---

## Complex Task Decomposition

For multi-module tasks, decompose before selecting modules.

### Decomposition Process

1. Identify distinct functional areas in the request
2. Map each area to a module based on responsibility
3. Use `internal_dependencies` to order deliverables

### Decomposition Pattern

**Task**: {multi-module task description}

**Decomposition**:
1. {functional area 1} → {module-1}
2. {functional area 2} → {module-2} (depends on 1)
3. {functional area 3} → {module-3} (depends on 1)

**Dependency Graph** (from architecture `internal_dependencies`):
```
{module-2}
    ↓
{module-1}
    ↓
{module-3}
```

**Deliverable Order** (reverse of dependency graph):
1. {module-3} changes (base layer)
2. {module-1} changes (depends on base)
3. {module-2} changes (depends on core)
