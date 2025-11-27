---
name: plan-files
description: Centralized file I/O for plan management - all phase skills delegate file operations here. Provides create-directory, read-plan, read-config, get-references, write-plan, write-config, write-references, and update-progress operations.
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion
---

# Plan Files Skill

**EXECUTION MODE**: Execute requested operation immediately. Do not explain or summarize.

**Role**: Centralized persistence layer for plan management. All phase skills delegate file I/O operations here.

## Standards (Load On-Demand)

### Architecture
```
Read standards/architecture.md
```
Contains: Skill separation, operations summary, file structure, validation rules

### Persistence
```
Read standards/persistence.md
```
Contains: Directory structure, naming conventions, file formats

### Templates

| Template | Purpose |
|----------|---------|
| `templates/plan-template.md` | Initial plan.md structure |
| `templates/config-template.md` | config.md structure |
| `templates/references-template.md` | references.md structure |

---

## Operation: create-directory

**Input**: `task_name` (kebab-case, max 50 chars)

**Steps**:

1. **Validate** - Lowercase with hyphens, no special characters
2. **Check existence**:
   ```bash
   test -d .claude/plans/{task_name}/ && echo "exists" || echo "not-exists"
   ```
3. **Handle existing** (AskUserQuestion):
   - Use existing (resume)
   - Create new (with suffix)
   - Replace (delete and recreate)
4. **Create**:
   ```bash
   mkdir -p .claude/plans/{task_name}/
   ```

**Output**: `status: created|resumed`, `plan_directory`, `existing_plan: true|false`

---

## Operation: read-plan

**Input**: `plan_directory`

**Steps**:

1. **Read**: `Read {plan_directory}/plan.md`
2. **Parse**:
   - Current Phase: `**Current Phase**:`
   - Current Task: `**Current Task**:`
   - Phase Progress Table
   - Tasks: `### Task N:`
3. **Return**:
   ```
   plan_status:
     current_phase: {init|refine|implement|verify|finalize}
     current_task: {task-id or "none"}
     overall_status: {pending|in_progress|completed}
   phases[5]: {name,status,tasks,completed}
   tasks_current_phase[N]: {id,name,status}
   ```

---

## Operation: read-config

**Input**: `plan_directory`

**Steps**:

1. **Read**: `Read {plan_directory}/config.md`
2. **Parse**:
   - Plan Type: `**Plan Type**:`
   - Build Configuration table
   - Workflow Configuration table
   - Context table
3. **Return**:
   ```
   configuration:
     plan_type: {implementation|simple}
     technology: {java|javascript|mixed|none}
     build_system: {maven|gradle|npm|npx|none}
     compatibility: {breaking|deprecations}
     commit_strategy: {fine-granular|phase-specific|complete}
     finalizing: {commit-only|pr-workflow}
     branch: {branch-name}
     issue: {issue-reference or "none"}
   ```

---

## Operation: get-references

**Input**: `plan_directory`

**Steps**:

1. **Read**: `Read {plan_directory}/references.md`
2. **Parse**:
   - Issue section
   - Related Files
   - ADRs section
   - Interfaces section
   - External Documentation
   - Dependencies
3. **Return**:
   ```
   references:
     issue: {url, title}
     branch: {branch-name}
     adrs[N]: {identifiers}
     interfaces[N]: {identifiers}
     implementation_files[N]: {paths}
     external_docs[N]: {names}
     dependencies[N]: {specs}
   ```

---

## Operation: write-plan

**Input**: `plan_directory`, `plan_content`

**Steps**:

1. **Generate markdown** from template:
   ```
   Read templates/plan-template.md
   ```
2. **Populate** with plan_content:
   - title, current_phase, current_task
   - phases array with tasks
3. **Write**: `Write {plan_directory}/plan.md`

**Output**: `status: created|updated`, `plan_file`

---

## Operation: write-config

**Input**: `plan_directory`, `configuration`

**Steps**:

1. **Generate markdown** from template:
   ```
   Read templates/config-template.md
   ```
2. **Populate** with configuration
3. **Write**: `Write {plan_directory}/config.md`

**Output**: `status: created`, `config_file`

---

## Operation: write-references

**Input**: `plan_directory`, `action` (add|update|remove), `reference_type`, `reference_data`

**Steps**:

1. **Read current** (if exists): `Read {plan_directory}/references.md`
2. **Apply action**:
   - add: Locate section, add entry
   - update: Locate entry, modify
   - remove: Locate entry, delete
3. **Write**: Use Edit (existing) or Write (new) with template:
   ```
   Read templates/references-template.md
   ```

**Output**: `status: created|updated`, `references_file`, `changes[N]`

---

## Operation: update-progress

**Input**: `plan_directory`, `task_id`, `status`, `checklist_items` (optional)

**Steps**:

1. **Read**: `Read {plan_directory}/plan.md`
2. **Locate task**: `### Task N:`
3. **Update checklist**: `[ ] → [x]` for specified items
4. **Update Phase Progress Table**: Count completed tasks
5. **Update current task**: Find next incomplete
6. **Check phase completion**: If all `[x]`, update phase status
7. **Write updates**: Use Edit tool

**Output**:
```
plan_status:
  current_phase: {phase}
  current_task: {next-task-id}
  phase_complete: true|false
phase_status:
  tasks_total: N
  tasks_completed: N
  completion_percentage: N
  phase_ready_for_transition: true|false
```

---

## Scripts

Python scripts for deterministic operations (output JSON):

| Script | Purpose | Usage |
|--------|---------|-------|
| `parse-plan.py` | Parse plan.md | `python3 scripts/parse-plan.py {path}` |
| `parse-config.py` | Parse config.md | `python3 scripts/parse-config.py {path}` |
| `parse-references.py` | Parse references.md | `python3 scripts/parse-references.py {path}` |
| `calculate-progress.py` | Progress metrics | `python3 scripts/calculate-progress.py {path}` |
| `validate-plan.py` | Validate directory | `python3 scripts/validate-plan.py {dir}` |

---

## Error Handling

### File Not Found
```
error:
  type: file_not_found
  message: {description}
alternatives:
- Create new plan with plan-init skill
- Check directory path
```

### Invalid Structure
```
error:
  type: invalid_structure
  message: Missing {section} in {file}
alternatives:
- Refine plan to fix structure
- Recreate from scratch
```

### Parse Error
```
error:
  type: parse_error
  message: Failed to parse {file}
alternatives:
- Fix file manually
- Regenerate via plan-init
```

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] All operations have clear input/output
- [x] Error handling for all scenarios
- [x] Python scripts for deterministic operations
- [x] Standards in standards/
- [x] Templates in templates/
