---
name: plan-refine
description: Refine phase skill for generic domain only
allowed-tools: Read, Bash, Skill, AskUserQuestion
---

# Plan Refine Skill

**SCOPE**: This skill is ONLY for **generic domain** without domain-specific skills.

**Role**: Fallback refine phase for generic plans. Creates solution document and tasks using inline logic.

**CRITICAL**: Use Python scripts via Bash for plan file updates.

---

## Scripts

| Script | Notation |
|--------|----------|
| manage-plan-document | `pm-workflow:manage-plan-documents:manage-plan-documents` |
| manage-solution-outline | `pm-workflow:manage-solution-outline:manage-solution-outline` |
| manage-config | `pm-workflow:manage-config:manage-config` |
| manage-lifecycle | `pm-workflow:manage-lifecycle:manage-lifecycle` |
| manage-log | `plan-marshall:logging:manage-log` |
| manage-task | `pm-workflow:manage-tasks:manage-tasks` |

---

## Thin Agent Routing

The `/plan-manage` command uses thin agents with domain skill loading:

1. Reads config.toon for domain and workflow_skills
2. Loads domain-specific skills via workflow_skills block
3. Falls back to this skill when domain has no specific skills

**This skill is the fallback** for generic domain (no domain-specific solution outline skill).

```
/plan-manage action=refine plan=X
  │
  ├─ Read config.toon workflow_skills.{domain}
  │
  ├─ If solution_outline skill is NOT null:
  │    → Task: solution-outline-agent (loads domain skill)
  │    → Task: task-plan-agent (loads domain skill)
  │
  └─ If solution_outline skill IS null (generic):
       → Task: plan-refine-agent
         → Skill: plan-refine ← THIS SKILL
           → Write tool → solution_outline.md (direct)
           → manage-solution-outline validate (Bash)
           → manage-task add (Bash)
```

---

## Primary Operation: refine

**Input**: `plan_id`

### Step 0: Load Solution Outline Skill

Load the solution outline skill for structure and examples:

```
Skill: pm-workflow:manage-solution-outline
```

This provides:
- Required document structure (Summary, Overview, Deliverables)
- ASCII diagram patterns
- Deliverable reference format

### Step 1: Log Phase Start

```bash
python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  work {plan_id} INFO "Starting refine phase"
```

### Step 2: Validate Domain

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config get \
  --plan-id {plan_id} --field domain
```

**IF domain is specific** (java, javascript, plugin):
```toon
status: error
error_type: wrong_routing
message: "Domain-specific plans must be refined via /plan-manage command, not plan-refine skill"
context:
  domain: {domain}
  correct_command: "/plan-manage action=refine plan={plan_id}"
```
Return this error. Do NOT proceed.

**IF domain is generic**: Continue to Step 3.

### Step 3: Read Request

Read the request document to understand the task:

```bash
python3 .plan/execute-script.py pm-workflow:manage-plan-documents:manage-plan-documents \
  request read \
  --plan-id {plan_id}
```

### Step 4: Create Solution Document

For generic plans, write the solution document directly using Claude Code's Write tool to: `.plan/plans/{plan_id}/solution_outline.md`

**Solution Document Template for Generic Plans:**
```markdown
# Solution: {request_title}

plan_id: {plan_id}
created: {timestamp}

## Summary

{brief summary of what will be done}

## Overview

```
Request → Analyze → Implement → Verify
```

## Deliverables

### 1. Complete Task

{request_summary}

**Success Criteria:**
- Task completed as requested
- Results verified

## Approach

Execute the request as specified.

## Dependencies

None identified.

## Risks and Mitigations

None identified.
```

Then validate the structure:

```bash
python3 .plan/execute-script.py pm-workflow:manage-solution-outline:manage-solution-outline validate \
  --plan-id {plan_id}
```

**Why direct Write?** Solution outlines can contain ASCII diagrams and rich content that don't fit CLI parameter passing.

### Step 4.5: MANDATORY USER REVIEW (NEVER SKIP)

After creating solution_outline.md, you MUST halt and request user review:

1. **Display the solution outline for review**:
   ```
   ## Solution Outline Created

   📄 **Review your solution outline**: .plan/plans/{plan_id}/solution_outline.md

   Please review the deliverables before proceeding.
   ```

2. **Ask the user to confirm or request changes**:
   ```
   AskUserQuestion:
     questions:
       - question: "Have you reviewed the solution outline? How would you like to proceed?"
         header: "Review"
         options:
           - label: "Proceed to create tasks"
             description: "Solution outline looks good, continue to task creation"
           - label: "Request changes"
             description: "I have feedback to improve the solution outline"
         multiSelect: false
   ```

3. **Handle user response**:
   - **If "Proceed to create tasks"**: Continue to Step 5
   - **If "Request changes"** or user provides custom feedback:
     - Incorporate feedback into solution_outline.md via Edit tool
     - Re-validate the document
     - Loop back to Step 4.5 (show updated outline, ask again)

This halt is **NOT OPTIONAL**. The workflow MUST pause here for user review before creating tasks.

### Step 5: Create Tasks

Create execution tasks referencing the deliverable in the solution document using heredoc:

```bash
python3 .plan/execute-script.py pm-workflow:manage-tasks:manage-tasks add \
  --plan-id {plan_id} <<'EOF'
title: Execute request
deliverables: [1]
domain: generic
description: |
  Complete the requested task

steps:
  - Analyze requirements
  - Implement solution
  - Verify result
EOF
```

**Note**: Task deliverable reference is numeric (`deliverables: [1]`) referencing the deliverable number in solution_outline.md.

### Step 6: Log Completion

```bash
python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  work {plan_id} INFO "Completed refine: solution document created, {tasks_created} tasks"
```

### Step 7: Phase Transition

```bash
python3 .plan/execute-script.py pm-workflow:manage-lifecycle:manage-lifecycle transition \
  --plan-id {plan_id} \
  --completed refine
```

---

## Error Handling

On any error, **first log the error** to work-log:

```bash
python3 .plan/execute-script.py plan-marshall:logging:manage-log \
  work {plan_id} ERROR "ERROR: {error_type} - {error_context}"
```

---

## Integration

### Command Integration
- **/plan-manage action=refine** - Routes to this skill for generic plans

### Scripts Used

| Script | Command | Purpose |
|--------|---------|---------|
| `pm-workflow:manage-plan-documents:manage-plan-documents` | `request read` | Read request document |
| `pm-workflow:manage-solution-outline:manage-solution-outline` | `validate` | Validate solution structure |
| `pm-workflow:manage-config:manage-config` | `get` | Read domain |
| `pm-workflow:manage-tasks:manage-tasks` | `add` | Create tasks |
| `pm-workflow:manage-lifecycle:manage-lifecycle` | `transition` | Phase transition |
| `plan-marshall:logging:manage-log` | `work` | Log progress and completion |

### Standards (Load On-Demand)

| Standard | Purpose |
|----------|---------|
| `standards/workflow.md` | Step-by-step refine workflow |
| `standards/architecture.md` | Skill-based routing architecture |

### Related Skills
- **manage-solution-outline** - Solution document structure and examples
- **plan-init** - Previous phase (creates request.md, config, status)
- **plan-execute** - Next phase (executes tasks)
- **Domain skills** - Loaded by thin agents via config.toon workflow_skills
