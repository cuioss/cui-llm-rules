# Sub-Type Template: Skill Creation/Modification

**Trigger**: "Create skill", "Modify skill", "Add workflow to skill"

## Task Template

### Task: {task-title}

**Goal**: {goal-description}

**Target**: `{bundle}:{skill-name}`

**Checklist**:
- [ ] Identify target bundle in marketplace/bundles/
- [ ] Load skill: `pm-plugin-development:plugin-create`
- [ ] Create/locate SKILL.md with proper frontmatter
- [ ] Define workflows with clear Steps sections
- [ ] Create scripts/ directory if needed
- [ ] Add test coverage for any scripts
- [ ] Verify SKILL.md follows skill standards
- [ ] Run `/plugin-doctor skill={skill-name}`
- [ ] Update bundle README.md if new skill added
- [ ] **Log**: Record completion in work-log
- [ ] **Learn**: Capture lesson if standards unclear

**Acceptance Criteria**:
- SKILL.md has valid frontmatter (name, description, allowed-tools)
- At least one workflow defined with Steps
- All scripts have test coverage
- /plugin-doctor shows no critical issues

## Placeholder Reference

| Placeholder | Source | Example |
|-------------|--------|---------|
| `{task-title}` | User request | "Create metrics-collector skill" |
| `{goal-description}` | User request | "Add skill for collecting metrics" |
| `{bundle}` | Target bundle | "pm-core" |
| `{skill-name}` | New/existing skill | "metrics-collector" |
