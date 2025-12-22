# Plan Init Skill Contract

Initialize plan structure with status.toon, config.toon, and references.toon.

---

## Purpose

The init phase creates the plan directory structure and initial files needed for subsequent phases. It is the entry point for all plan workflows.

---

## Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier (kebab-case) |
| `title` | string | Conditional | Plan title for display (if not from lesson) |
| `issue_url` | string | No | GitHub issue URL if plan is from issue |
| `lesson_id` | string | No | Lesson ID to convert to plan |
| `branch` | string | No | Git branch name (auto-generated if not provided) |

**Source mutual exclusivity**: Provide ONE of: `title`, `issue_url`, or `lesson_id`.

---

## Output

### Directory Structure Created

```
.plan/plans/{plan_id}/
├── status.toon        # Plan lifecycle state
├── config.toon        # Plan configuration
└── references.toon    # File and branch references
```

### Files Created

#### status.toon

```toon
title: {title}
current_phase: init
phases[5]{name,status}:
init,in_progress
outline,pending
plan,pending
execute,pending
finalize,pending

created: {timestamp}
updated: {timestamp}
```

#### config.toon

```toon
plan_id: {plan_id}
domains: []              # Empty until outline phase detects domains
```

#### references.toon

```toon
branch: {branch}
base_branch: main
issue_url: {issue_url}   # If provided
modified_files: []
config_files: []
test_files: []
```

---

## Workflow

### Step 1: Validate Input

Validate:
- `plan_id` format (kebab-case)
- Plan doesn't already exist

### Step 2: Create Plan Directory

```bash
python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle create \
  --plan-id {plan_id} \
  --title "{title}" \
  --domain generic \
  --phases init,outline,plan,execute,finalize
```

### Step 3: Create Config

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config create \
  --plan-id {plan_id}
```

### Step 4: Create References

```bash
python3 .plan/execute-script.py pm-workflow:manage-references:manage-references create \
  --plan-id {plan_id} \
  --branch {branch} \
  [--issue-url {issue_url}]
```

### Step 5: Create Git Branch

If branch doesn't exist, create it:

```bash
git checkout -b {branch}
```

### Step 6: Transition to Outline

```bash
python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle transition \
  --plan-id {plan_id} \
  --completed init
```

---

## Auto-Continue

Init phase **auto-continues** to outline phase. No user approval gate.

```
init ──auto──▶ outline
```

---

## Skill Loading

Init phase uses **system defaults only**:

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains get-defaults --domain system
```

No domain-specific skills are loaded during init (domains not yet determined).

---

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| `plan_exists` | Plan ID already in use | Choose different plan_id or delete existing |
| `invalid_plan_id` | Plan ID not kebab-case | Use valid format |
| `branch_exists` | Git branch already exists | Use existing branch or choose different name |

---

## Output Format

### Success

```toon
status: success
plan_id: {plan_id}
phase: init
files_created:
  - status.toon
  - config.toon
  - references.toon
branch: {branch}
next_phase: outline
auto_continue: true
```

### Error

```toon
status: error
plan_id: {plan_id}
error: plan_exists
message: "Plan '{plan_id}' already exists"
```

---

## Related Documents

- [solution-outline-skill-contract.md](solution-outline-skill-contract.md) - Next phase (outline)
- [architecture-overview.md](architecture-overview.md) - Phase flow overview
- [config-toon-format.md](config-toon-format.md) - Config.toon structure
