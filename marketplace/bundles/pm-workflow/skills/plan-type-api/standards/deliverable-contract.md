# Deliverable Contract

Standard structure for deliverables in solution_outline.md that enables task-plan-agent optimization.

## Purpose

Each deliverable MUST contain sufficient information for:

1. **Grouping analysis**: Can this be aggregated with other deliverables?
2. **Split detection**: Should this be split into multiple tasks?
3. **Delegation mapping**: Which skill/workflow should execute this?
4. **Verification consolidation**: Can verification commands be merged?
5. **Dependency ordering**: What order must deliverables execute in?
6. **Parallelization**: Which deliverables can run concurrently?

## Required Deliverable Structure

All solution-outline agents MUST produce deliverables following this structure:

```markdown
### N. {Deliverable Title}

**Metadata:**
- change_type: {create|modify|refactor|migrate|delete}
- execution_mode: {automated|manual|mixed}
- domain: {java|java-testing|javascript|javascript-testing|plugin}
- suggested_skill: {bundle}:{skill-name}
- suggested_workflow: {workflow-name}
- context_skills: [{optional-skill-1}, {optional-skill-2}]
- depends: {none | deliverable number(s)}

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
| `domain` | Yes | Skill domain for loading defaults | Skill loading |
| `suggested_skill` | Yes | Skill for delegation | Delegation mapping |
| `suggested_workflow` | Yes | Workflow within skill | Delegation mapping |
| `context_skills` | No | Optional skills from domain's optionals list | Skill loading |
| `depends` | Yes | Dependencies on other deliverables (by number) | Ordering, parallelization |
| `Affected files` | Yes | Explicit file list | Step generation |
| `Change per file` | Yes | What changes | Task description |
| `Pattern` | Conditional | Code/format pattern | Implementation guide |
| `Verification` | Yes | How to verify | Task verification |

## Domain Values

| Domain | Description | Default Skills | Optional Skills |
|--------|-------------|----------------|-----------------|
| `java` | Production Java code | pm-dev-java:cui-java-core | pm-dev-java:cui-java-cdi |
| `java-testing` | Java test code | pm-dev-java:cui-java-unit-testing | (none) |
| `javascript` | Production JavaScript | pm-dev-frontend:cui-javascript | (none) |
| `javascript-testing` | JavaScript test code | pm-dev-frontend:cui-javascript-unit-testing | pm-dev-frontend:cui-cypress |
| `plugin` | Marketplace plugins | pm-plugin-development:plugin-architecture | pm-plugin-development:plugin-script-architecture |

Use `plan-marshall-config skill-domains get-defaults --domain {domain}` to retrieve current domain configuration.

## Dependency Specification

The `depends` field enables task-plan-agent to determine execution order and parallelization.

| Value | Meaning | Example |
|-------|---------|---------|
| `none` | No dependencies, can run in parallel | Independent refactoring |
| Single number | Must complete after numbered deliverable | `1` |
| Multiple numbers | Must complete after ALL numbered deliverables | `1, 2, 4` |

### Dependency Rules

- Use `none` when the deliverable has no prerequisites
- Reference deliverables by their number (e.g., `1`, `2`, `4`)
- Multiple dependencies are comma-separated
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

Solution outline agents MUST validate that each deliverable contains:

- [ ] `change_type` metadata
- [ ] `execution_mode` metadata
- [ ] `domain` metadata (valid domain from config)
- [ ] `suggested_skill` and `suggested_workflow`
- [ ] `context_skills` (empty list or valid optionals for domain)
- [ ] `depends` field (`none` or valid deliverable references)
- [ ] Explicit file list (not "all files matching X")
- [ ] Verification command and criteria

## Anti-patterns (INVALID deliverables)

- Missing metadata block
- Missing `domain` field (prevents skill loading)
- "Update all agents" without file enumeration
- No suggested_skill (forces task-plan-agent to guess)
- `context_skills` containing skills not in domain's optionals
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
- suggested_skill: pm-dev-java:java-implement
- suggested_workflow: implement
- context_skills: [pm-dev-java:cui-java-cdi]
- depends: 1

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
- No suggested_skill for delegation
- "Check manually" is not an automatable verification

### Vague File References

```markdown
### 2. Update Planning Agents

**Metadata:**
- change_type: modify
- execution_mode: automated
- domain: plugin
- suggested_skill: pm-plugin-development:plugin-maintain
- suggested_workflow: update-component
- context_skills: []
- depends: none

**Affected files:**
- All files in marketplace/bundles/planning/agents/

**Verification:**
- Command: `grep -l '```toon' *.md`
- Criteria: All files match
```

**Why invalid:**
- `Affected files` uses "All files in..." instead of explicit paths
- Task-plan agent cannot generate steps from vague references
- Validation will reject this deliverable
