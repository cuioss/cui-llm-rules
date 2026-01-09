# Deliverable Contract

Standard structure for deliverables in solution_outline.md that enables task-plan optimization and 5-phase workflow skill routing.

## Purpose

Each deliverable MUST contain sufficient information for:

1. **Grouping analysis**: Can this be aggregated with other deliverables?
2. **Split detection**: Should this be split into multiple tasks?
3. **Domain routing**: Which domain skills should be loaded?
4. **Profile routing**: Which workflow profile (implementation, testing, quality)?
5. **Verification consolidation**: Can verification commands be merged?
6. **Dependency ordering**: What order must deliverables execute in?
7. **Parallelization**: Which deliverables can run concurrently?

## Required Deliverable Structure

All solution-outline skills MUST produce deliverables following this structure:

```markdown
### N. {Deliverable Title}

**Metadata:**
- change_type: {create|modify|refactor|migrate|delete}
- execution_mode: {automated|manual|mixed}
- domain: {java|javascript|plan-marshall-plugin-dev}
- profile: {implementation|testing}
- skills: [{skill-1}, {skill-2}]
- depends: {none | N. Title | N, M}

**Affected files:**
- `{path/to/file1}`
- `{path/to/file2}`

**Change per file:** {specific change description}

**Pattern:** (optional, for format changes)
```{format}
{pattern to apply}
```

**Verification:**
- Command: `{verification command}`
- Criteria: {success criteria}

**Success Criteria:**
- {criterion 1}
- {criterion 2}
```

## Field Definitions

| Field | Required | Description | Used For |
|-------|----------|-------------|----------|
| `change_type` | Yes | Type of change | Grouping analysis |
| `execution_mode` | Yes | automated/manual/mixed | Split detection |
| `domain` | Yes | Single domain from config.domains | Domain skill loading |
| `profile` | Yes | implementation or testing | Workflow skill selection |
| `skills` | Yes | Skills from module.proposed_skill_domains | Task skill inheritance |
| `depends` | Yes | Dependencies on other deliverables | Ordering, parallelization |
| `Affected files` | Yes | Explicit file list | Step generation |
| `Change per file` | Yes | What changes | Task description |
| `Pattern` | Conditional | Code/format pattern | Implementation guide |
| `Verification` | Yes | How to verify | Task verification |

## Domain Values

The `domain` field MUST be a single value from `marshal.json skill_domains`:

| Domain | Description |
|--------|-------------|
| `java` | Java production and test code |
| `javascript` | JavaScript production and test code |
| `plan-marshall-plugin-dev` | Marketplace plugin components |

Multi-domain plans (e.g., fullstack features) have multiple domains in `marshal.json`. Each deliverable selects ONE domain for its work.

> **Note**: The `system` domain is internal-only and must NEVER be assigned to deliverables.

### Domain Validation

Solution outline skills MUST validate domains exist in marshal.json:

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains get --domain {domain}
```

Error if domain not found in marshal.json.

## Profile Values

The `profile` field determines which workflow profile is used during task execution:

| Profile | Description | Purpose |
|---------|-------------|---------|
| `implementation` | Creating/modifying production code | Implementation workflow |
| `testing` | Creating/modifying test code | Testing workflow |
| `quality` | Documentation, verification | Quality workflow |

## Skills Field

The `skills` field contains domain-specific skills inherited from `module.proposed_skill_domains` in architecture data. During solution-outline, when a module is selected for a deliverable, the module's proposed skills are assigned to the deliverable.

| Source | Description |
|--------|-------------|
| `module.proposed_skill_domains` | From `analyze-project-architecture` output |

Example: When assigning work to `oauth-sheriff-core` module, the deliverable inherits `[java-core, java-cdi]` from module context.

### Domain Trickle-Down Flow

Domain, profile, and skills flow from architecture to deliverable to task:

```
analyze-project-architecture    solution_outline.md          TASK-001.toon
┌───────────────────────────┐   ┌─────────────────┐          ┌─────────────────┐
│ oauth-sheriff-core:       │   │ domain: java    │          │ domain: java    │
│   proposed_skill_domains: │──▶│ profile: impl   │────────▶│ profile: impl   │
│     [java-core, java-cdi] │   │ skills: [...]   │          │ skills: [...]   │
└───────────────────────────┘   └─────────────────┘          └─────────────────┘
                                        │
                                        └─── solution-outline selects module,
                                             inherits module.proposed_skill_domains
```

## Dependency Specification

The `depends` field enables task-plan to determine execution order and parallelization.

| Value | Meaning | Example |
|-------|---------|---------|
| `none` | No dependencies, can run in parallel | Independent refactoring |
| `N` | Must complete after deliverable N | `1` |
| `N. Title` | Must complete after deliverable N (with title for clarity) | `1. Create Database Schema` |
| `N, M` | Must complete after ALL numbered deliverables | `1, 2, 4` |

### Dependency Rules

- Use `none` when the deliverable has no prerequisites
- Reference deliverables by number alone (e.g., `1`) or with title (e.g., `1. Create Schema`)
- Title format improves readability - task-plan parses the number prefix
- Multiple dependencies are comma-separated (numbers only for brevity)
- Circular dependencies are INVALID
- Dependencies should reference earlier deliverable numbers (lower numbers first)

## Change Types

| Type | Description | Grouping Hint |
|------|-------------|---------------|
| `create` | New file/component | Group by component type |
| `modify` | Update existing | Group by change similarity |
| `refactor` | Restructure without behavior change | Keep separate (risky) |
| `migrate` | Format/API migration | Group by target format |
| `delete` | Remove file/component | Group by bundle |

## Execution Modes

| Mode | Description | Task-Plan Behavior |
|------|-------------|-------------------|
| `automated` | Can run without human intervention | Can aggregate |
| `manual` | Requires human judgment/action | Must split |
| `mixed` | Contains both auto and manual parts | Must split into separate tasks |

## Validation Checklist

Solution outline skills MUST validate that each deliverable contains:

- [ ] `change_type` metadata
- [ ] `execution_mode` metadata
- [ ] `domain` metadata (single value from config.domains)
- [ ] `profile` metadata (implementation or testing)
- [ ] `skills` metadata (from module.proposed_skill_domains)
- [ ] `depends` field (`none` or valid deliverable references)
- [ ] Explicit file list (not "all files matching X")
- [ ] Verification command and criteria

## Deliverable ID Format

| Format | Example | Usage |
|--------|---------|-------|
| Number only | `1`, `2` | `task.deliverables: [1, 2]` |
| Full reference | `1. Create CacheConfig` | `depends: 1. Create CacheConfig` |

**Parsing rule**: Extract leading integer, ignore title portion.

## Anti-patterns (INVALID deliverables)

- Missing metadata block
- Missing `domain` field (prevents domain skill loading)
- Missing `profile` field (prevents workflow skill selection)
- Missing `skills` field (prevents task skill inheritance)
- Invalid domain (domain not in marshal.json `skill_domains`)
- System domain (using `system` as deliverable domain - internal only)
- "Update all agents" without file enumeration
- Verification: "manual review" for automatable checks
- Missing `depends` field (prevents parallelization analysis)
- Circular dependencies (D1 depends on D2, D2 depends on D1)
- Forward dependencies (D1 depends on D3, where D3 comes after D1)

## Example Deliverable

```markdown
### 2. Add Auth Endpoint

**Metadata:**
- change_type: create
- execution_mode: automated
- domain: java
- profile: implementation
- skills: [java-core, java-cdi]
- depends: 1. Create Database Schema

**Affected files:**
- `src/main/java/de/cuioss/auth/AuthController.java`
- `src/main/java/de/cuioss/auth/dto/AuthRequest.java`
- `src/main/java/de/cuioss/auth/dto/AuthResponse.java`

**Change per file:** Create REST endpoint for user authentication with request/response DTOs.

**Pattern:**
```java
@Path("/auth")
@ApplicationScoped
public class AuthController {
    @POST
    public AuthResponse authenticate(AuthRequest request) { ... }
}
```

**Verification:**
- Command: `mvn test -Dtest=AuthControllerTest`
- Criteria: All auth tests pass

**Success Criteria:**
- REST endpoint accepts POST /auth with username/password
- Returns JWT token on successful authentication
- Returns 401 on invalid credentials
```

## Invalid Examples (Anti-patterns)

### Missing Metadata Block

```markdown
### 1. Update Agent Outputs

Update all agent outputs to use TOON format.

**Verification:** Check manually
```

**Why invalid:**
- No `**Metadata:**` block
- No explicit file list ("all agents" is vague)
- "Check manually" is not an automatable verification

### Vague File References

```markdown
### 2. Update Planning Agents

**Metadata:**
- change_type: modify
- execution_mode: automated
- domain: plan-marshall-plugin-dev
- profile: implementation
- depends: none

**Affected files:**
- All files in marketplace/bundles/planning/agents/

**Verification:**
- Command: `grep -l '```toon' *.md`
- Criteria: All files match
```

**Why invalid:**
- `Affected files` uses "All files in..." instead of explicit paths
- Task-plan cannot generate steps from vague references
- Validation will reject this deliverable
