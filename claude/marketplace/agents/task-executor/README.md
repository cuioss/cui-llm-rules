# Issue Implementer Agent

Implements structured tasks from plan files one step at a time with strict adherence to checklists and acceptance criteria.

## Purpose

This agent automates the implementation of tasks defined in structured plan files by:
- Reading and understanding task requirements from plan files
- Executing checklist items in strict sequential order
- Marking each item as complete before proceeding
- Verifying all acceptance criteria before task completion
- Building and testing code before committing
- Returning control after each task (no automatic continuation)

## Usage

```bash
# Implement next open task
"Implement the next task from http-client-plan/plan-http-client-extension.md"

# Implement specific task by number
"Implement Task 2 from the plan"

# Implement specific task by name
"Implement 'Create HttpMethod Enum' from the plan"

# Continue implementation
"Continue implementing the HTTP client extension"
```

## Parameters

- **taskPlanPath** (required): Absolute path to task plan file
- **taskIdentifier** (optional): Task name or number to implement (if omitted, implements next open task)

## Skills Used

This agent leverages:
- **cui-java-core**: Java development standards, Lombok patterns, logging
- **cui-java-unit-testing**: JUnit 5 testing patterns, coverage requirements
- **cui-javadoc**: JavaDoc documentation standards

## How It Works

1. **Parse Plan**: Reads task plan file and identifies target task
2. **Read References**: Loads all referenced specifications and design docs
3. **Execute Checklist**: Completes each checklist item in strict order:
   - Marks item as in-progress
   - Executes implementation step
   - Marks item as complete
   - Updates plan file
4. **Verify Criteria**: Checks all acceptance criteria are met
5. **Return Control**: Reports completion and waits for user (doesn't auto-proceed)

## Task Plan Format

The agent expects task plan files in this format:

```markdown
### Task N: Task Name

**Goal:** Brief description

**References:**
- Specification: path/to/spec.md lines 10-50
- Package: com.example.feature

**Checklist:**
- [ ] Read and understand all references above
- [ ] If unclear, ask user for clarification (DO NOT guess)
- [ ] Create FeatureClass.java with required methods
- [ ] Add unit tests for FeatureClass
- [ ] Run `maven-project-builder` agent to verify build passes
- [ ] Analyze build results - if issues found, fix and re-run
- [ ] Commit changes using `commit-changes` agent

**Acceptance Criteria:**
- FeatureClass implements all required methods
- Test coverage ≥ 80%
- Build passes all quality checks
```

## Examples

### Example 1: Implement Next Task

```
User: "Implement the next task from project-plan.md"

Agent:
- Reads project-plan.md
- Identifies Task 3 as next incomplete task
- Reads all references (specification, design docs)
- Executes checklist items sequentially:
  ✅ Read and understand references
  ✅ Create HttpClient.java
  ✅ Add unit tests
  ✅ Run maven-project-builder → Build passes
  ✅ Commit changes
- Verifies all acceptance criteria
- Returns success report
```

### Example 2: Implement Specific Task

```
User: "Implement Task 5: Add Retry Logic from the plan"

Agent:
- Reads plan file
- Finds Task 5: Add Retry Logic
- Activates cui-java-core skill for Java standards
- Implements retry mechanism with exponential backoff
- Adds comprehensive tests
- Verifies build passes
- Commits with descriptive message
- Returns success report
```

### Example 3: Handle Build Failure

```
User: "Continue implementing the API client"

Agent:
- Identifies next task
- Implements code following checklist
- Runs maven-project-builder → Build fails (compilation error)
- Analyzes error output
- Fixes compilation issue
- Re-runs maven-project-builder → Build passes
- Proceeds with commit
- Returns success report
```

## Critical Rules

- **One Task at a Time**: Agent completes ONE task then returns control (never auto-proceeds)
- **Strict Sequencing**: Checklist items executed in exact order, no skipping
- **No Guessing**: If unclear, asks user for clarification
- **Build Verification**: Must verify build passes before committing
- **Acceptance Criteria**: All criteria must be met before task completion

## Notes

- Agent invokes `maven-project-builder` and `commit-changes` sub-agents as needed
- Uses CUI development skills for Java/testing/documentation standards
- Marks checklist items in plan file in real-time (provides progress visibility)
- Tracks all tool usage and reports in final summary
- Includes lessons learned reporting for continuous improvement

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
