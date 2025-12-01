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
| `templates/references-template.toon` | references.toon structure |

**Note**: config.toon and references.toon use TOON format - scripts generate from templates.

---

## Operation: create-directory

**Input**: `task_name` (kebab-case, max 50 chars)

**Steps**:

1. **Validate** - Lowercase with hyphens, no special characters
2. **Check existence**:
   ```bash
   test -d .plan/plans/{task_name}/ && echo "exists" || echo "not-exists"
   ```
3. **Handle existing** (AskUserQuestion):
   - Use existing (resume)
   - Create new (with suffix)
   - Replace (delete and recreate)
4. **Create**:
   ```bash
   mkdir -p .plan/plans/{task_name}/
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

1. **Parse via script** (supports both config.toon and legacy config.md):
   ```bash
   python3 scripts/parse-config.py {plan_directory}
   ```
2. **Return**: JSON with configuration values and format indicator

---

## Operation: get-references

**Input**: `plan_directory`

**Steps**:

1. **Parse via script** (accepts directory, finds references.toon):
   ```bash
   python3 scripts/parse-references.py {plan_directory}
   ```
2. **Return**: JSON with references data (TOON format only)

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
- `plan-type`: implementation, simple, plugin-development
- `technology`: java, javascript, mixed, none
- `build-system`: maven, gradle, npm, npx, none
- `compatibility`: breaking, deprecations
- `commit-strategy`: fine-granular, phase-specific, complete
- `finalizing`: commit-only, pr-workflow

**Output**: JSON with `file`, `plan_type`, `technology`, `build_system`, `format: toon`

**Generated TOON format**:
```toon
# Plan Configuration

plan_type: implementation
branch: feature/my-branch
issue: #123

technology: java
build_system: maven

compatibility: deprecations
commit_strategy: fine-granular
finalizing: pr-workflow
```

---

## Operation: write-references

**Pattern**: Script Automation (outputs references.toon - TOON format only)

**Input**: `plan_directory`, `action`, `section`, `value`

**Usage**:

```bash
# Set branch
python3 scripts/write-references.py \
  --plan-dir {plan_directory} \
  --action set \
  --section branch \
  --value "feature/my-branch"

# Set issue (with full JSON)
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

# Add ADR reference (CSV format: id,path,status)
python3 scripts/write-references.py \
  --plan-dir {plan_directory} \
  --action add \
  --section adrs \
  --value "ADR-001,../adr/ADR-001.md,proposed"

# Add external doc
python3 scripts/write-references.py \
  --plan-dir {plan_directory} \
  --action add \
  --section external_docs \
  --value "JWT Guide,https://jwt.io/introduction"

# Remove file
python3 scripts/write-references.py \
  --plan-dir {plan_directory} \
  --action remove \
  --section implementation_files \
  --value "src/main/java/OldFile.java"
```

**Valid actions**: add, update, remove, set

**Valid sections**: issue, issue_url, issue_title, branch, base_branch, implementation_files, config_files, test_files, adrs, interfaces, external_docs, dependencies, related_plans

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
  "file": ".plan/plans/my-task/plan.md",
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
| `write-config.py` | Create config.toon | `python3 scripts/write-config.py --help` |
| `write-references.py` | Create/update references.toon | `python3 scripts/write-references.py --help` |
| `update-progress.py` | Update checklist progress | `python3 scripts/update-progress.py --help` |
| `copy-lesson-to-plan.py` | Move lesson file to plan | `python3 scripts/copy-lesson-to-plan.py --help` |
| `parse-plan.py` | Parse plan.md | `python3 scripts/parse-plan.py {path}` |
| `parse-config.py` | Parse config.toon or config.md | `python3 scripts/parse-config.py {dir}` |
| `parse-references.py` | Parse references.toon | `python3 scripts/parse-references.py {dir}` |
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

---

## Continuous Improvement

**MANDATORY**: When executing scripts from this skill, unexpected behavior or errors MUST be documented as lessons learned immediately.

### When to Document

File a lesson learned when a script:
- Returns unexpected output
- Fails to update files as expected
- Requires a workaround to achieve the desired result
- Has unclear or misleading documentation

### How to Document

Use the `general-tools:manage-lessons-learned` skill:
```bash
python3 {write-lesson.py path} --component "planning:plan-files" --category {bug|improvement|anti-pattern} --title "Brief description" --detail "What happened, why, workaround, suggested fix"
```

**Categories**:
- `bug`: Script is broken or produces wrong results
- `improvement`: Script works but could be better
- `anti-pattern`: Script was misused or documentation unclear

**Why This Matters**: Script errors indicate gaps in validation, documentation, or implementation. Documented lessons improve future sessions and identify systemic issues.
