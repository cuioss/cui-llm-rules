# Path-Single Workflow

Workflow for isolated changes that affect 1-3 components in a single bundle with no cross-references or dependencies.

## Indicators

Use Path-Single when:

| Indicator | Example |
|-----------|---------|
| "add", "create", "new" (single component) | "Add new skill" |
| "fix", "update" (localized) | "Fix command X" |
| No cross-bundle impact | Single bundle modification |
| No shared pattern changes | Isolated component work |

## Workflow Steps

For isolated changes, identify the target components directly:

1. **Identify target bundle and component type**
2. **Read existing component** (if modify/refactor scope)
3. **Build deliverables section** for each component to create/modify

## Deliverable Template

Build a deliverables markdown section with required metadata:

```markdown
### 1. {Component Action}

**Metadata:**
- change_type: {create|modify|refactor}
- execution_mode: automated
- domain: plugin
- suggested_skill: pm-plugin-development:plugin-{create|maintain}
- suggested_workflow: {create-skill|create-agent|update-component|...}
- context_skills: []
- depends: none

{Technical description}

**Type**: {skill|command|agent|script}
**Path**: `marketplace/bundles/{bundle}/{type}/{name}`
**Dependencies**: {dependencies if any}
**Standards**: {standards to follow}

**Verification:**
- Command: `/pm-plugin-development:plugin-doctor --component {path}`
- Criteria: No quality issues detected

**Success Criteria:**
- {criterion 1}
- {criterion 2}
```

## Decomposition Patterns

| Request Pattern | Typical Deliverables |
|-----------------|----------------------|
| "Add new skill" | 1. Create SKILL.md 2. Add standards docs 3. Create scripts 4. Update plugin.json |
| "Add new command" | 1. Create command.md 2. Implement skill delegation 3. Update plugin.json |
| "Add new agent" | 1. Create agent.md 2. Define tool requirements 3. Update plugin.json |
| "Fix command X" | 1. Update command with fix |

## Next Step

After building the deliverables section, proceed to **Step 3c: Create Solution Document** in the main workflow.
