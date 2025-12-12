# Custom Plan-Type Wizard

Interactive flow for creating project-local plan-types.

---

## Step 1: Gather Basic Information

```
AskUserQuestion:
  question: "Name for custom plan-type (kebab-case):"
  type: text
```

```
AskUserQuestion:
  question: "Description:"
  type: text
```

---

## Step 2: Define File Patterns

```
AskUserQuestion:
  question: "File patterns (comma-separated, e.g., *.java,*.kt):"
  type: text
```

---

## Step 3: Configure Agents

```
AskUserQuestion:
  question: "Solution outline agent (notation or 'null' for none):"
  type: text
```

```
AskUserQuestion:
  question: "Task plan agent (notation or 'null' for none):"
  type: text
```

---

## Step 4: Create Custom Plan-Type

1. Read template from `templates/custom-plan-type.md`
2. Create `.claude/plan-types/{name}/SKILL.md` with filled template
3. Add to marshal.json:

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config custom-types add \
  --name {name} \
  --skill-path .claude/plan-types/{name}/SKILL.md \
  --solution-outline-agent {solution_outline_agent} \
  --task-plan-agent {task_plan_agent}
```

---

## Step 5: Confirmation

Output confirmation:

```toon
status: success
operation: custom_plan_type_created

name: {name}
skill_path: .claude/plan-types/{name}/SKILL.md
solution_outline_agent: {solution_outline_agent}
task_plan_agent: {task_plan_agent}
```

---

Return to the calling context (wizard Step 6 or Configuration: Plan-Types menu).
