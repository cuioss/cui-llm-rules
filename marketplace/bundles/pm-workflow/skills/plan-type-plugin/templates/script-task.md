# Sub-Type Template: Script Creation/Modification

**Trigger**: "Create script", "Modify script", "Add script to skill"

## Task Template

### Task: {task-title}

**Goal**: {goal-description}

**Target**: `{bundle}:{skill}/scripts/{script-name}`

**Checklist** (Test-Driven Development):
- [ ] Identify target skill and scripts/ directory
- [ ] Load skill: `pm-plugin-development:plugin-create`
- [ ] Locate or create test file in skill's test directory
- [ ] Write test case for expected script behavior
- [ ] Run test (verify it fails - TDD red phase)
- [ ] Implement script in `scripts/` directory
- [ ] Run test (verify it passes - TDD green phase)
- [ ] Run all skill tests (no regressions)
- [ ] Run `/plugin-doctor skill={skill-name}`
- [ ] **Log**: Record completion in work-log
- [ ] **Learn**: Capture lesson if unexpected behavior encountered

**Acceptance Criteria**:
- Script exists in skill's `scripts/` directory
- Test coverage for script functionality
- All tests pass
- /plugin-doctor shows no critical issues

## Placeholder Reference

| Placeholder | Source | Example |
|-------------|--------|---------|
| `{task-title}` | User request | "Create update-metrics.py" |
| `{goal-description}` | User request | "Add metrics update script" |
| `{bundle}` | Target bundle | "planning" |
| `{skill}` | Target skill | "plan-files" |
| `{script-name}` | New script name | "update-metrics.py" |
| `{skill-name}` | For plugin-doctor | "plan-files" |
