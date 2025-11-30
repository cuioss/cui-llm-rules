---
name: plan-verify
description: Verify phase skill for plan management. Runs full build verification, code quality checks, manual testing validation, and documentation review. Ensures all acceptance criteria are met before finalization.
allowed-tools: Read, Write, Edit, Bash, Skill, Task, AskUserQuestion
---

# Plan Verify Skill

**EXECUTION MODE**: Execute verification tasks immediately. Do not explain or summarize.

**OUTPUT RULES**:
- Do NOT narrate internal process or tool invocations
- Do NOT display raw script output - format as structured status
- DO show verification results (build, tests, quality)
- Work silently until you have results to display

**Role**: Fourth phase skill in the plan management system. Verifies implementation quality through builds, tests, quality checks, and documentation review. Delegates all file I/O to `plan-files` skill.

## Standards (Load On-Demand)

### Workflow
```
Read standards/workflow.md
```
Contains: Phase overview, standard tasks, build verification, quality analysis, manual testing, documentation verification

---

## Operation: verify-build

**Input**: `plan_directory`

**Steps**:

1. **Read config**:
   ```
   Skill: cui-task-workflow:plan-files
   operation: read-config
   ```
   Extract: technology, build_system

2. **Run build**:

   **Maven**:
   ```
   Task: builder:maven-builder
   prompt: Execute mvn clean verify, report results and coverage
   ```

   **npm**:
   ```
   Task: builder:npm-builder
   prompt: Execute npm build and test, report results and coverage
   ```

3. **Handle result**:
   - Success → Report and proceed
   - Failure → AskUserQuestion: Fix/View log/Override/Abort

4. **Log build verification**:
   ```
   Skill: cui-task-workflow:work-log
   operation: log-entry
   plan_directory: {plan_directory}
   phase: verify
   task: task-1
   action: "Ran build verification"
   result: "Build passed, tests: {count}, coverage: {pct}%"
   ```

---

## Operation: verify-quality

**Input**: `plan_directory`

**Steps**:

1. **Run quality analysis**:

   **Java**:
   ```
   Task: cui-java-expert:java-quality-agent
   prompt: Analyze code quality (checkstyle, PMD, SpotBugs)
   ```

   **JavaScript**: `npm run lint`

2. **Check Sonar** (if applicable):
   ```
   mcp__sonarqube__search_sonar_issues_in_projects
   ```

3. **Handle result**:
   - Passed → Report and proceed
   - Critical issues → AskUserQuestion: Fix/View details/Accept/Abort

4. **Log quality analysis**:
   ```
   Skill: cui-task-workflow:work-log
   operation: log-entry
   plan_directory: {plan_directory}
   phase: verify
   task: task-2
   action: "Ran quality analysis"
   result: "{count} issues, {severity breakdown}"
   ```

---

## Operation: verify-manual

**Input**: `plan_directory`

**Steps**:

1. **Read acceptance criteria**:
   ```
   Skill: cui-task-workflow:plan-files
   operation: read-plan
   ```

2. **Present testing checklist** (AskUserQuestion):
   - Happy path tests
   - Edge cases
   - Error handling
   - Options: All passed / Some failed / Skip

3. **Handle failures**:
   - Record which tests failed
   - Options: Fix issues / Mark as known / Abort

---

## Operation: verify-documentation

**Input**: `plan_directory`

**Steps**:

1. **Check code documentation**:

   **Java**:
   ```
   Task: cui-java-expert:java-fix-javadoc-agent
   prompt: Check JavaDoc coverage (report only, don't fix)
   ```

   **JavaScript**: `npm run docs:check`

2. **Check README**: Verify new functionality documented

3. **Check ADR/Interface docs**:
   ```
   Skill: cui-task-workflow:plan-files
   operation: get-references
   ```
   Verify all referenced ADRs and interfaces exist.

4. **Handle incomplete**:
   - AskUserQuestion: Add missing / Proceed anyway / Mark as TODO

---

## Phase Transition

When all verify tasks complete:

AskUserQuestion:
- Proceed to finalize phase
- Review results
- Return to implement

```
Skill: cui-task-workflow:plan-files
operation: update-progress
task_id: {last-verify-task}
status: completed
```

---

## Error Handling

### Build Timeout
Options: Retry with longer timeout / Check for loops / Abort

### Coverage Below Threshold
Options: Add tests / Lower threshold (with justification) / Proceed

### Sonar Quality Gate Failed
Options: Fix issues / View details / Request exception

---

## Integration

### Command Integration
- **/plan-execute** - Primary command invoking this skill via phase-management

### Skills Used
- **plan-files** - All file I/O operations
- **maven-builder** - Java build verification
- **npm-builder** - JavaScript build verification
- **java-quality-agent** - Java quality analysis
- **java-fix-javadoc-agent** - JavaDoc verification
- **phase-management** - Orchestration (invokes this skill)
- **work-log** - Logging significant actions

### Related Skills
- **plan-init** - Init phase
- **plan-refine** - Refine phase
- **plan-implement** - Previous phase
- **plan-finalize** - Next phase

---

## Quality Checklist

- [x] Self-contained with relative paths
- [x] All file I/O delegated to plan-files skill
- [x] Build verification for Maven and npm
- [x] Quality check integration
- [x] Manual testing workflow
- [x] Documentation verification
