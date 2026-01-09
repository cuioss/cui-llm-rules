# Solution Outline Skill Contract

Workflow skill for outline phase - transforms requests into solution outlines with deliverables.

**Implementation**: `pm-workflow:solution-outline`

---

## Purpose

Solution outline skills analyze a request and produce a structured solution outline document containing deliverables. Each deliverable follows the [Deliverable Contract](deliverable-contract.md).

**Flow**: Request → Solution Outline (with Deliverables) → config.toon.domains (intelligent decision)

---

## Invocation

**Phase**: `outline`

**Agent invocation**:
```bash
plan-phase-agent plan_id={plan_id} phase=outline
```

**Skill resolution**:
```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  resolve-workflow-skill --phase outline
```

Result:
```toon
status: success
domain: system
phase: outline
workflow_skill: pm-workflow:solution-outline
```

---

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `feedback` | string | No | User feedback from review (for revision iterations) |

---

## Workflow Skill Responsibilities

The workflow skill autonomously:

1. **Loads extensions**: Calls `resolve-workflow-skill-extension --type outline` for each domain
2. **Loads architecture data**: Retrieves module context from `analyze-project-architecture`
3. **Analyzes codebase**: Uses architecture-level knowledge (module purposes, responsibilities)
4. **Determines relevant domains**: Claude decides which domains are relevant to the request
5. **Creates deliverables**: Each with `domain`, `profile`, and `skills` fields (skills from module.proposed_skill_domains)
6. **Writes config.toon.domains**: Intelligent decision output (subset of marshal.json domains)
7. **Validates**: Calls `manage-solution-outline validate`

```
Workflow Skill Execution:
┌──────────────────────────────────────────────────────────────────┐
│ 1. Load module context from analyze-project-architecture         │
│ 2. For each domain:                                              │
│    a. resolve-workflow-skill-extension --domain X --type outline │
│ 3. Analyze request + codebase                                    │
│ 4. Determine which domains are relevant (Claude reasoning)       │
│ 5. Create deliverables with:                                     │
│    - domain + profile                                            │
│    - skills (from selected module.proposed_skill_domains)        │
│ 6. Write config.toon.domains (intelligent decision output)       │
│ 7. Validate with manage-solution-outline validate                │
└──────────────────────────────────────────────────────────────────┘
```

---

## Extension Loading

Extensions add domain-specific outline behavior:

```bash
# For each domain in marshal.json:
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  resolve-workflow-skill-extension --domain java --type outline
# → pm-dev-java:java-outline-ext (or null if none configured)
```

Extensions provide:
- Domain-specific deliverable patterns
- Component organization rules
- Change granularity guidelines

---

## Architecture Data Loading

Module context comes from `analyze-project-architecture`, which provides:

```bash
python3 .plan/execute-script.py pm-workflow:manage-solution-outline:manage-solution-outline \
  get-module-context
```

Result includes per-module:
```toon
status: success
modules:
  - name: oauth-sheriff-core
    path: oauth-sheriff-core
    responsibility: Core JWT validation logic
    purpose: library
    key_packages:
      - de.cuioss.sheriff.oauth.core.pipeline
    proposed_skill_domains: [java-core, java-cdi]
```

When creating deliverables, the selected module's `proposed_skill_domains` becomes the deliverable's `skills` field.

---

## config.toon.domains Output

The workflow skill writes detected domains to config.toon:

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config set-domains \
  --plan-id {plan_id} --domains java,javascript
```

This is an **intelligent decision output** - not a copy of marshal.json domains, but Claude's analysis of which domains are relevant to the specific request.

---

## Knowledge Level

**Source**: `analyze-project-architecture` output (module context)

**Knowledge includes**:
- Module names and paths
- Module responsibilities and purposes
- Key packages and their descriptions
- Proposed skill domains per module
- Module dependencies

**Knowledge excludes**:
- Implementation patterns (Builder, Factory, etc.)
- Specific annotations (@Inject, @Nullable)
- Testing patterns (mocking, fixtures)
- Error handling patterns

---

## Output Validation

The workflow skill MUST validate that each deliverable contains all required fields from the [Deliverable Contract](deliverable-contract.md):

- [ ] `change_type` metadata
- [ ] `execution_mode` metadata
- [ ] `domain` metadata (valid domain from marshal.json)
- [ ] `profile` metadata (`implementation`, `testing`, or `quality`)
- [ ] `skills` metadata (from module.proposed_skill_domains)
- [ ] `depends` field (`none` or valid deliverable references)
- [ ] Explicit file list (not "all files matching X")
- [ ] Verification command and criteria

---

## Script API Calls

### Solution Outline Operations

```bash
# Write solution outline
python3 .plan/execute-script.py pm-workflow:manage-solution-outline:manage-solution-outline write \
  --plan-id {plan_id} --content "$(cat <<'HEREDOC'
...content...
HEREDOC
)"

# Validate
python3 .plan/execute-script.py pm-workflow:manage-solution-outline:manage-solution-outline validate \
  --plan-id {plan_id}
```

### Config Domains Output

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config set-domains \
  --plan-id {plan_id} --domains java,javascript
```

---

## Return Structure

```toon
status: success|error
plan_id: {plan_id}
deliverable_count: {N}
domains_detected: [java, javascript]
lessons_recorded: {count}
message: {error message if status=error}
```

---

## Error Handling

| Scenario | Action |
|----------|--------|
| Request not found | Return `{status: error, message: "Request not found"}` |
| Validation fails | Fix issues or return partial with error list |
| Domain unknown | Return error with valid domains |
| Script execution fails | Record lesson-learned, return error |

---

## Phase Transition

After completion, the orchestrator triggers [User Review Protocol](user-review-protocol.md).

```
outline ──user approval gate──▶ plan
```

---

## Related Documents

- [plan-init-skill-contract.md](plan-init-skill-contract.md) - Previous phase (init)
- [task-plan-skill-contract.md](task-plan-skill-contract.md) - Next phase (plan)
- [deliverable-contract.md](deliverable-contract.md) - Deliverable structure
- [extension-api.md](extension-api.md) - Extension mechanism
- [user-review-protocol.md](user-review-protocol.md) - Approval gate after outline
