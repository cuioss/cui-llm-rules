# Sub-Type Template: Command Creation/Modification

**Trigger**: "Create command", "Modify command", "Add slash command"

## Task Template

### Task: {task-title}

**Goal**: {goal-description}

**Target**: `{bundle}/commands/{command-name}.md`

**Checklist**:
- [ ] Identify target bundle in marketplace/bundles/
- [ ] Load skill: `pm-plugin-development:plugin-create`
- [ ] Create command file in bundle's commands/ directory
- [ ] Define command with proper frontmatter
- [ ] Specify required skills in command body
- [ ] Add orchestration logic (load skills, execute workflows)
- [ ] Verify command follows command standards
- [ ] Test command execution manually
- [ ] Run `/plugin-doctor command={command-name}`
- [ ] Update bundle README.md with new command
- [ ] **Log**: Record completion in work-log
- [ ] **Learn**: Capture lesson if orchestration issues found

**Acceptance Criteria**:
- Command file exists with valid frontmatter
- Orchestrates skills correctly
- Manual test demonstrates expected behavior
- /plugin-doctor shows no critical issues

## Placeholder Reference

| Placeholder | Source | Example |
|-------------|--------|---------|
| `{task-title}` | User request | "Create metrics-report command" |
| `{goal-description}` | User request | "Add command to generate metrics report" |
| `{bundle}` | Target bundle | "plan-marshall" |
| `{command-name}` | New command name | "metrics-report" |
