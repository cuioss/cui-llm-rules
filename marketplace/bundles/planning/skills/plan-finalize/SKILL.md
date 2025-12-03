---
name: plan-finalize
description: Complete plan execution with git workflow and PR management
allowed-tools: Read, Bash, Glob, SlashCommand
---

# Plan Finalize Skill

**Role**: Finalize phase skill. Handles git workflow (commit, push, PR) and plan completion. Reads configuration from config.toon written during configure phase.

**Key Pattern**: Configuration-agnostic execution. All finalize behavior determined by config.toon values.

## When to Activate This Skill

Activate when:
- Execute phase has completed (all tasks done)
- Ready to commit and potentially create PR
- Plan is in `finalize` phase

---

## Configuration Source

All finalize configuration is read from config.toon (written during configure):

Script: `planning:manage-config/scripts/manage-config.py`

```bash
python3 {script_path} read \
  --plan-id {plan_id}
```

**Config Fields Used**:

| Field | Values | Description |
|-------|--------|-------------|
| `create_pr` | true/false | Whether to create a pull request |
| `verification_required` | true/false | Whether verification must pass |
| `verification_command` | command/null | Verification command to run |
| `branch_strategy` | feature/direct | Branch strategy |

---

## Operation: finalize

**Input**: `plan_id`

### Step 1: Read Configuration

```bash
python3 {script_path} read \
  --plan-id {plan_id}
```

Extract: `create_pr`, `verification_required`, `verification_command`, `branch_strategy`

Also read references.toon for branch and issue information:

Script: `planning:manage-references/scripts/manage-references.py`

```bash
python3 {script_path} read \
  --plan-id {plan_id}
```

### Step 2: Run Verification (if required)

If `verification_required == true` and `verification_command` is set:

```bash
SlashCommand("{verification_command}")
```

Common verification commands:
- `/builder:builder-build-and-fix` - Java/Gradle/Maven
- `/builder:builder-build-and-fix system=npm` - JavaScript
- `/cui-plugin-development-tools:plugin-doctor` - Plugin development

If verification fails, report error and allow retry.

### Step 3: Commit Workflow

Stage all changes:

```bash
git add -A
```

Create commit with descriptive message (read task.md for summary):

```bash
git commit -m "{commit_message}"
```

Push to remote:

```bash
git push origin {branch}
```

### Step 4: Create PR (if enabled)

If `create_pr == true`:

Read task.md for PR summary, then create PR:

```bash
gh pr create \
  --title "{title}" \
  --body "{body_from_template}"
```

If issue is linked in references.toon, include `Closes #{issue}` in body.

### Step 5: PR Workflow (if PR created)

If PR was created and `pr_workflow` expected:

```
SlashCommand("/planning:pr-doctor")
```

This handles CI monitoring and review addressing.

### Step 6: Mark Plan Complete

Transition to complete:

Script: `planning:manage-lifecycle/scripts/manage-lifecycle.py`

```bash
python3 {script_path} transition \
  --plan-id {plan_id} \
  --completed finalize
```

### Step 7: Log Completion

```
Skill: planning:manage-log
operation: add
plan_id: {plan_id}
phase: finalize
summary: "Plan completed - {commit_hash}, {pr_url if created}"
```

---

## Output

**Success**:

```toon
status: success
plan_id: {plan_id}

actions:
  verification: {passed|skipped}
  commit: {commit_hash}
  push: success
  pr: {created #{number}|skipped}
  pr_workflow: {completed|skipped}

next_state: complete
```

**Error**:

```toon
status: error
plan_id: {plan_id}
step: {verification|commit|push|pr}
message: {error_description}
recovery: {recovery_suggestion}
```

---

## Error Handling

### Verification Failure

```toon
status: error
step: verification
message: Build failed with errors
recovery: Fix errors and re-run finalize
```

### Git Commit Failure

```toon
status: error
step: commit
message: Nothing to commit or merge conflict
recovery: Resolve conflicts, then re-run finalize
```

### Push Failure

```toon
status: error
step: push
message: Remote rejected push
recovery: Pull changes, resolve conflicts, then re-run finalize
```

### PR Creation Failure

```toon
status: error
step: pr
message: PR already exists or branch not pushed
recovery: Check existing PRs or push branch first
```

---

## Resumability

The skill checks current state before each step:

1. **Has verification passed?** Skip if already verified
2. **Are there uncommitted changes?** Skip commit if clean
3. **Is branch pushed?** Skip push if remote is current
4. **Does PR exist?** Skip creation if PR exists
5. **Is plan already complete?** Skip if finalize done

---

## Finalize by Plan Type

### Java / JavaScript

Full workflow:
1. Verification (build/test)
2. Commit
3. Push
4. Create PR
5. PR workflow (/pr-doctor)

### Plugin Development

Partial workflow:
1. Verification (/plugin-doctor)
2. Commit
3. Push
4. (No PR)

### Generic

Minimal workflow:
1. (No verification)
2. Commit
3. Push
4. (No PR)

---

## Templates

| Template | Purpose |
|----------|---------|
| `templates/pr-template.md` | PR body format |

---

## Scripts Used

| Script | Purpose |
|--------|---------|
| `planning:manage-config/scripts/manage-config.py` | Read finalize configuration |
| `planning:manage-references/scripts/manage-references.py` | Read branch, issue info |
| `planning:manage-lifecycle/scripts/manage-lifecycle.py` | Phase transition |
| `planning:manage-log/scripts/manage-work-log.py` | Log completion |

---

## Integration

### Phase Routing

This skill is invoked when plan is in `finalize` phase:

```
planning:manage-lifecycle route --phase finalize → planning:plan-finalize
```

### Command Integration

- **/plan-execute action=finalize** - May invoke this skill
- **/pr-doctor** - Used during PR workflow

### Related Skills

- **plan-execute** - Previous phase (executes tasks)
- **plan-lifecycle** - Handles phase transition
