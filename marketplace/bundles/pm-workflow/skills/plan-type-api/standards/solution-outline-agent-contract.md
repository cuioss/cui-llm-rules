# Solution Outline Agent Contract

Standard contract for solution outline agents that transform requests into solution outlines with deliverables.

## Purpose

Solution outline agents analyze a request and produce a structured solution outline document containing deliverables. Each deliverable follows the [Deliverable Contract](deliverable-contract.md).

**Flow**: Request → Solution Outline (with Deliverables)

## Invocation

**Invoked by**: `/plan-manage action=refine` command

The command reads the `domain.solution_outline_agent` field from the plan-type skill's frontmatter and invokes the agent via Task tool.

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `feedback` | string | No | User feedback from review (for revision iterations) |

## Responsibilities

1. Load `pm-workflow:manage-solution-outline` skill for structure guidance
2. Read request.md for the request
3. Analyze codebase with domain knowledge
4. Write solution_outline.md via `pm-workflow:manage-solution-outline:manage-solution-outline write` with heredoc (includes ASCII overview diagram)
5. Document deliverables as numbered `### N. Title` sections with [Deliverable Contract](deliverable-contract.md) metadata
6. Validate with `pm-workflow:manage-solution-outline:manage-solution-outline validate --plan-id {plan_id}`
7. Record lessons-learned on issues
8. **If `feedback` provided**: Incorporate user feedback into existing solution_outline.md

## Output Validation

The agent MUST validate that each deliverable contains all required fields from the [Deliverable Contract](deliverable-contract.md):

- [ ] `change_type` metadata
- [ ] `execution_mode` metadata
- [ ] `domain` metadata (valid domain from config)
- [ ] `suggested_skill` and `suggested_workflow`
- [ ] `context_skills` (empty list or valid optionals for domain)
- [ ] `depends` field (`none` or valid deliverable references)
- [ ] Explicit file list (not "all files matching X")
- [ ] Verification command and criteria

## Return Structure

```toon
status: success|error
plan_id: {plan_id}
deliverable_count: {N}
lessons_recorded: {count}
message: {error message if status=error}
```

## Domain Agent Implementations

| Plan Type | Agent |
|-----------|-------|
| `java` | `pm-dev-java:java-solution-outline-agent` |
| `javascript` | `pm-dev-frontend:js-solution-outline-agent` |
| `plugin-development` | `pm-plugin-development:plugin-solution-outline-agent` |
| `generic` | None (inline in command) |

## Script Execution Tracing

When executing scripts, agents MUST pass plan context for logging:

### Scripts with `--plan-id` Parameter

Scripts that accept `--plan-id` (manage-* scripts) use it for both logic AND logging:

```bash
python3 .plan/execute-script.py pm-workflow:manage-solution-outline:manage-solution-outline write \
  --plan-id {plan_id} --content "$(cat <<'HEREDOC'
...content...
HEREDOC
)"
```

### Scripts without `--plan-id` Parameter

Scripts that don't accept `--plan-id` use `--trace-plan-id` for logging only:

```bash
python3 .plan/execute-script.py some-bundle:some-skill:analyze-script \
  --trace-plan-id {plan_id} --other-args
```

The `--trace-plan-id` parameter is:
- Extracted by the executor for logging purposes
- Stripped before passing to the script (script never sees it)
- Enables plan-scoped logging in `.plan/plans/{plan_id}/script-execution.log`

## Error Handling

| Scenario | Action |
|----------|--------|
| Request not found | Return `{status: error, message: "Request not found"}` |
| Validation fails | Fix issues or return partial with error list |
| Domain unknown | Return error with valid domains |
| Script execution fails | Record lesson-learned, return error |

## Integration

**Callers**: `/plan-manage action=refine` command

**Data Layer**:
- `pm-workflow:manage-plan-documents:manage-plan-documents` - Request document operations
- `pm-workflow:manage-solution-outline:manage-solution-outline` - Solution outline validation and queries

**Next Step**: After completion, command triggers [User Review Protocol](user-review-protocol.md)
