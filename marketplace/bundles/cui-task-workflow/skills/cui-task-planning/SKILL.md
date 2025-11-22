---
name: cui-task-planning
description: Comprehensive task planning and tracking with plan creation, execution, and review workflows
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(gh:*), Skill, AskUserQuestion
---

# CUI Task Planning Skill

Comprehensive task planning, execution, and review workflows for CUI projects. Provides three core workflows: **plan** (create task breakdowns), **execute** (implement tasks), and **review** (verify implementation readiness).

## What This Skill Provides

### Workflows (NEW - Absorbs Agent Functionality)

1. **Plan Workflow** - Creates actionable task breakdowns from issues
   - Analyzes GitHub issues or local issue files
   - Generates structured plan documents with acceptance criteria
   - Replaces: task-breakdown-agent

2. **Execute Workflow** - Implements tasks from plan files
   - Executes checklist items sequentially
   - Tracks progress with status updates
   - Replaces: task-executor agent

3. **Review Workflow** - Reviews issues for implementation readiness
   - Validates completeness, correctness, clarity
   - Updates documentation to achieve 100% clarity
   - Replaces: task-reviewer agent

### Standards Documentation

Unified task planning standards for three planning scenarios:

- **Project Planning** - Long-term project TODO lists
- **Issue Planning** - Single-issue implementation plans
- **Refactoring Planning** - Categorized improvement tracking

## When to Activate This Skill

**For Planning:**
- Breaking down GitHub issues into actionable tasks
- Creating implementation plans
- Generating project TODO lists

**For Execution:**
- Implementing tasks from plan files
- Tracking checklist progress
- Verifying acceptance criteria

**For Review:**
- Validating issue documentation
- Ensuring implementation readiness
- Fixing ambiguities in requirements

## Workflows

### Workflow 1: Plan (Create Task Breakdown)

**Purpose:** Analyze an issue and create a detailed implementation plan with actionable tasks.

**Input:** Issue reference (GitHub URL, issue number, or local file path)

**Steps:**

1. **Load Planning Standards**
   ```
   Read {baseDir}/standards/issue-planning-standards.md
   ```

2. **Identify Issue Source**
   - GitHub URL → Use `gh issue view {number} --repo {owner/repo}`
   - Issue number → Use `gh issue view {number}`
   - Local file → Use Read tool

3. **Analyze Issue Content**
   Run analysis script:
   ```
   python3 {baseDir}/scripts/create-task-breakdown.py {issue-file}
   ```

   Script outputs JSON with task structure:
   ```json
   {
     "issue": {"title": "...", "source": "..."},
     "tasks": [
       {
         "id": 1,
         "name": "...",
         "goal": "...",
         "references": [...],
         "acceptance_criteria": [...],
         "dependencies": []
       }
     ],
     "total_tasks": N
   }
   ```

4. **Generate Plan Document**
   Use output to create plan-issue-X.md following template in standards.

5. **Return Completion Report**
   Include: tasks identified, plan location, metrics.

**Output:** Plan file at `plan-{issue-name}.md`

---

### Workflow 2: Execute (Implement Tasks)

**Purpose:** Execute tasks from a plan file sequentially, tracking progress.

**Input:** Plan file path and optional task identifier

**Steps:**

1. **Parse Plan File**
   ```
   python3 {baseDir}/scripts/track-task-progress.py {plan-file}
   ```

   Script outputs JSON with progress state:
   ```json
   {
     "current_task": {"id": N, "name": "...", "status": "in_progress"},
     "next_task": {"id": N+1, "name": "...", "status": "pending"},
     "progress": {
       "total_tasks": N,
       "completed": N,
       "completion_percentage": N
     }
   }
   ```

2. **Identify Target Task**
   - If task specified → Find that task
   - Otherwise → Find first incomplete task

3. **Read References**
   For each reference in task:
   - Load file using Read tool
   - Synthesize understanding
   - If unclear → Use AskUserQuestion

4. **Execute Checklist Items (Sequential)**
   For each checklist item:
   - Determine item type (implement, test, document, verify)
   - Execute using appropriate tools (Edit, Write, etc.)
   - Mark item done: `[ ]` → `[x]` using Edit tool

5. **Verify Acceptance Criteria**
   ```
   python3 {baseDir}/scripts/validate-acceptance.py {plan-file} --task {id}
   ```

6. **Return Completion Report**
   Include: task completed, files modified, acceptance status.

**Output:** Updated plan file with checked items

---

### Workflow 3: Review (Verify Implementation Readiness)

**Purpose:** Review an issue for completeness, correctness, and clarity before implementation.

**Input:** Issue reference (file path or GitHub issue number)

**Steps:**

1. **Load Issue Content**
   - File → Use Read tool
   - GitHub issue → Use `gh issue view {number} --json title,body,labels`

2. **Deep Analysis**
   Apply ULTRATHINK reasoning to analyze:
   - What is the problem/requirement?
   - What is the proposed solution?
   - What are acceptance criteria? (Must have testable conditions)
   - What are technical constraints?
   - What are dependencies?
   - What are edge cases?

3. **Identify Gaps**
   Check for:
   - Ambiguous requirements
   - Missing acceptance criteria
   - Undefined scope boundaries
   - Unspecified error handling

4. **Research/Clarification (Conditional)**
   - If researchable → Note for caller
   - If requires user input → Use AskUserQuestion

5. **Update Documentation**
   - For files → Use Edit tool
   - For GitHub → Use `gh issue edit {number} --body "..."`

6. **Quality Review Loop**
   Verify 6 quality criteria:
   - Consistency: Zero contradictions
   - Correctness: All paths exist, versions valid
   - Unambiguous: Zero vague terms
   - No duplication: Zero semantic repeats
   - Complete: Has criteria, constraints, dependencies, edge cases
   - Actionable: Steps have file path + action verb + outcome

7. **Return Completion Report**
   Include: issues found, changes made, quality assessment.

**Output:** Updated issue documentation with 100% clarity

---

## Standards Organization

```
{baseDir}/
├── SKILL.md                     # This file (workflows + overview)
├── standards/                   # Planning standards (loaded on-demand)
│   ├── task-planning-core.md
│   ├── project-planning-standards.md
│   ├── issue-planning-standards.md
│   └── refactoring-planning-standards.md
├── scripts/                     # Automation scripts (JSON output)
│   ├── create-task-breakdown.py
│   ├── track-task-progress.py
│   └── validate-acceptance.py
└── references/                  # Detailed guides (loaded on-demand)
    ├── planning-guide.md
    ├── execution-guide.md
    └── review-guide.md
```

## Scripts

### create-task-breakdown.py

**Purpose:** Analyze issue content and generate task breakdown structure.

**Usage:**
```bash
python3 {baseDir}/scripts/create-task-breakdown.py <issue-file> [--output <file>]
```

**Input:** Issue file (markdown or JSON)
**Output:** JSON with tasks array

### track-task-progress.py

**Purpose:** Parse plan file and determine current progress.

**Usage:**
```bash
python3 {baseDir}/scripts/track-task-progress.py <plan-file>
```

**Input:** Plan markdown file
**Output:** JSON with progress state

### validate-acceptance.py

**Purpose:** Validate acceptance criteria for completed tasks.

**Usage:**
```bash
python3 {baseDir}/scripts/validate-acceptance.py <plan-file> [--task <id>]
```

**Input:** Plan file and optional task ID
**Output:** JSON with validation results

## Standards (Load On-Demand)

### Task Planning Core
```
Read {baseDir}/standards/task-planning-core.md
```
- Status indicator definitions
- Task element structure
- Traceability patterns
- Quality standards

### Issue Planning Standards
```
Read {baseDir}/standards/issue-planning-standards.md
```
- plan-issue-X.md format
- Sequential task structure
- Acceptance criteria format
- Agent-friendly structure

### Project Planning Standards
```
Read {baseDir}/standards/project-planning-standards.md
```
- doc/TODO.adoc structure
- Hierarchical organization
- Requirements traceability

### Refactoring Planning Standards
```
Read {baseDir}/standards/refactoring-planning-standards.md
```
- Category-based organization
- Task identifier format
- Priority assignment

## Integration

### Commands Using This Skill
- **/orchestrate-workflow** - Full workflow orchestration
- **/orchestrate-task** - Single task execution

### Related Skills
- **cui-git-workflow** - Commit message format for task completion
- **cui-java-core** / **cui-javascript** - Standards during execution

## Quality Verification

- [x] Self-contained with {baseDir} pattern
- [x] Progressive disclosure (standards loaded on-demand)
- [x] Scripts output JSON for machine processing
- [x] All 3 agent functionalities absorbed
- [x] Clear workflow definitions
- [x] Standards documentation maintained

## References

- Conventional Commits: https://www.conventionalcommits.org/
- Task Management Best Practices: https://www.atlassian.com/agile/project-management/user-stories
