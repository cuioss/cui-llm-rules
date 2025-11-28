---
name: plan-files
description: Centralized file I/O for plan management - all phase skills delegate file operations here. Provides create-directory, read-plan, read-config, get-references, write-plan, write-config, write-references, and update-progress operations.
allowed-tools: Read, Bash, AskUserQuestion
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

1. **Parse via script**:
   ```bash
   python3 scripts/parse-plan.py {plan_directory}/plan.md
   ```
2. **Return**: JSON with plan status, phases, and tasks

---

## Operation: read-config

**Input**: `plan_directory`

**Steps**:

1. **Parse via script**:
   ```bash
   python3 scripts/parse-config.py {plan_directory}/config.md
   ```
2. **Return**: JSON with configuration values

---

## Operation: get-references

**Input**: `plan_directory`

**Steps**:

1. **Parse via script**:
   ```bash
   python3 scripts/parse-references.py {plan_directory}/references.md
   ```
2. **Return**: JSON with references data

---

## Operation: write-plan

**Pattern**: Script Automation

**Input**: `plan_directory`, `title`, `current_phase`, `current_task`, `phases`

**Usage**:

```bash
python3 scripts/write-plan.py \
  --plan-dir {plan_directory} \
  --title "Task Title" \
  --current-phase init \
  --current-task task-1 \
  --phases-json '[{"name":"init","status":"in_progress","tasks":3}]'
```

**With detailed tasks**:

```bash
python3 scripts/write-plan.py \
  --plan-dir {plan_directory} \
  --title "Feature Implementation" \
  --current-phase init \
  --current-task task-1 \
  --phases-json '[
    {"name":"init","status":"in_progress","tasks":[
      {"name":"Setup","phase":"init","goal":"Setup environment","checklist":["Install deps","Configure tools"]}
    ]},
    {"name":"implement","status":"pending","tasks":5}
  ]'
```

**Output**: JSON with `file`, `title`, `current_phase`

---

## Operation: write-config

**Pattern**: Script Automation

**Input**: `plan_directory`, configuration values

**Usage**:

```bash
python3 scripts/write-config.py \
  --plan-dir {plan_directory} \
  --plan-type implementation \
  --technology java \
  --build-system maven \
  --compatibility deprecations \
  --commit-strategy phase-specific \
  --finalizing pr-workflow \
  [--branch feature/my-branch] \
  [--issue "#123"]
```

**Valid enum values**:
- `plan-type`: implementation, simple
- `technology`: java, javascript, mixed, none
- `build-system`: maven, gradle, npm, npx, none
- `compatibility`: breaking, deprecations
- `commit-strategy`: fine-granular, phase-specific, complete
- `finalizing`: commit-only, pr-workflow

**Output**: JSON with `file`, `plan_type`, `technology`, `build_system`

---

## Operation: write-references

**Pattern**: Script Automation

**Input**: `plan_directory`, `action`, `section`, `value`

**Usage**:

```bash
# Set branch
python3 scripts/write-references.py \
  --plan-dir {plan_directory} \
  --action set \
  --section branch \
  --value "feature/my-branch"

# Set issue
python3 scripts/write-references.py \
  --plan-dir {plan_directory} \
  --action set \
  --section issue \
  --value '{"id":"#123","title":"Issue Title","url":"https://..."}'

# Add implementation file
python3 scripts/write-references.py \
  --plan-dir {plan_directory} \
  --action add \
  --section implementation_files \
  --value "src/main/java/Foo.java"

# Add ADR reference
python3 scripts/write-references.py \
  --plan-dir {plan_directory} \
  --action add \
  --section adrs \
  --value "ADR-0015: Use Strategy Pattern"

# Remove file
python3 scripts/write-references.py \
  --plan-dir {plan_directory} \
  --action remove \
  --section implementation_files \
  --value "src/main/java/OldFile.java"
```

**Valid actions**: add, update, remove, set

**Valid sections**: issue, branch, adrs, interfaces, implementation_files, external_docs, dependencies

**Output**: JSON with `file`, `created`, `changes`

---

## Operation: update-progress

**Pattern**: Script Automation

**Input**: `plan_directory`, `phase`, `task_id`, `complete_items`

**Usage**:

```bash
python3 scripts/update-progress.py \
  --plan-dir {plan_directory} \
  --phase init \
  --task-id 1 \
  --complete-items "Check current git branch,Detect build system"
```

**Output**: JSON with progress status:
```json
{
  "success": true,
  "operation": "update-progress",
  "file": ".claude/plans/my-task/plan.md",
  "phase": "init",
  "task_id": "1",
  "items_completed": 2,
  "phase_status": {
    "total": 5,
    "completed": 2,
    "status": "in_progress",
    "phase_complete": false
  },
  "next_task": "task-1"
}
```

---

## Scripts

Python scripts for deterministic operations (output JSON):

| Script | Purpose | Usage |
|--------|---------|-------|
| `write-plan.py` | Create/update plan.md | `python3 scripts/write-plan.py --help` |
| `write-config.py` | Create config.md | `python3 scripts/write-config.py --help` |
| `write-references.py` | Create/update references.md | `python3 scripts/write-references.py --help` |
| `update-progress.py` | Update checklist progress | `python3 scripts/update-progress.py --help` |
| `parse-plan.py` | Parse plan.md | `python3 scripts/parse-plan.py {path}` |
| `parse-config.py` | Parse config.md | `python3 scripts/parse-config.py {path}` |
| `parse-references.py` | Parse references.md | `python3 scripts/parse-references.py {path}` |
| `calculate-progress.py` | Progress metrics | `python3 scripts/calculate-progress.py {path}` |
| `validate-plan.py` | Validate directory | `python3 scripts/validate-plan.py {dir}` |
| `test-plan-scripts.py` | Test suite | `python3 scripts/test-plan-scripts.py` |

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
