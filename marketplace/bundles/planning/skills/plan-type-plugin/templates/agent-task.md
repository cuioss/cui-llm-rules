# Sub-Type Template: Agent Creation/Modification

**Trigger**: "Create agent", "Modify agent", "Add specialized agent"

## Task Template

### Task: {task-title}

**Goal**: {goal-description}

**Target**: `{bundle}/agents/{agent-name}.md`

**Checklist**:
- [ ] Identify target bundle in marketplace/bundles/
- [ ] Load skill: `cui-plugin-development-tools:plugin-create`
- [ ] Create agent file in bundle's agents/ directory
- [ ] Define agent with proper frontmatter (tools, model)
- [ ] Write clear goal-oriented instructions
- [ ] Specify required skills for agent to load
- [ ] Define output format expectations
- [ ] Verify agent follows agent standards
- [ ] Run `/plugin-doctor agent={agent-name}`
- [ ] Update bundle README.md with new agent
- [ ] **Log**: Record completion in work-log
- [ ] **Learn**: Capture lesson if agent behavior unexpected

**Acceptance Criteria**:
- Agent file exists with valid frontmatter
- Clear goal and output format defined
- Required tools and skills specified
- /plugin-doctor shows no critical issues

## Placeholder Reference

| Placeholder | Source | Example |
|-------------|--------|---------|
| `{task-title}` | User request | "Create metrics-analyzer agent" |
| `{goal-description}` | User request | "Add agent for analyzing metrics" |
| `{bundle}` | Target bundle | "general-tools" |
| `{agent-name}` | New agent name | "metrics-analyzer" |
