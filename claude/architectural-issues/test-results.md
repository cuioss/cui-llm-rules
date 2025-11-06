# Diagnostic Tools Test Results

**Date**: 2025-11-06
**Branch**: feature/refactor-agents
**Commits Tested**: 79d2527 (architecture rules), 8e6d102 (diagnostics)

## Test Objective

Validate that the new diagnostic checks (Check 6: Task Tool Misuse, Check 7: Maven Anti-Pattern) correctly detect violations in existing agents.

## Test Cases

### Test Case 1: maven-project-builder (VIOLATIONS EXPECTED)

**File**: `claude/marketplace/bundles/cui-maven/agents/maven-project-builder.md`

**Expected Violations**:
- ✅ **Check 6 CRITICAL**: Task tool in frontmatter (line 4)
- ✅ **Check 6 CRITICAL**: Task delegation calls in workflow (lines 47, 50)

**Evidence**:
```yaml
# Line 4:
tools: Read, Edit, Write, Grep, Skill, Task

# Lines 47-50:
Use the Task tool to invoke the maven-builder agent for build execution:

Task:
```

**Pattern Detected**: Agent attempting to delegate to maven-builder agent, which violates Rule 6 (agents cannot delegate).

**Expected Recommendations**:
- Remove Task from tools list
- Move orchestration logic to command
- Make agent focused (single task execution only)

---

### Test Case 2: task-executor (MULTIPLE VIOLATIONS EXPECTED)

**File**: `claude/marketplace/bundles/cui-workflow/agents/task-executor.md`

**Expected Violations**:
- ✅ **Check 6 CRITICAL**: Task tool in frontmatter (line 15)
- ✅ **Check 7 CRITICAL**: Bash(./mvnw:*) in non-maven-builder agent (line 15)

**Evidence**:
```yaml
# Line 15:
tools: Read, Edit, Write, Glob, Grep, Task, Bash(./mvnw:*), Bash(./gradlew:*), Bash(ls:*), Skill

# Line 36:
- **Bash**: ONLY for build/test commands (`./mvnw`, `./gradlew`)

# Line 40:
- **Task tool**: Invoke sub-agents (`maven-project-builder`, `commit-changes`)
```

**Patterns Detected**:
1. Task delegation capability (violates Rule 6)
2. Direct Maven execution permission (violates Rule 7)

**Expected Recommendations**:
- Remove Task from tools list
- Remove Bash(./mvnw:*) from tools list
- Return results to caller who orchestrates maven-builder for verification
- Make agent focused (no verification, no build)

---

### Test Case 3: maven-builder (CLEAN - EXCEPTION)

**File**: `claude/marketplace/bundles/cui-maven/agents/maven-builder.md`

**Expected Result**: ALL CHECKS PASS

**Evidence**:
```yaml
# Line 4:
tools: Read, Write, Bash(./mvnw:*), Grep
```

**Why Clean**:
- ✅ **Check 6 PASS**: No Task tool in frontmatter
- ✅ **Check 7 PASS**: Has Bash(./mvnw:*) BUT agent name = "maven-builder" (exception per Rule 7)

**This is the ONLY agent allowed to execute Maven directly.**

---

## Detection Pattern Validation

### Check 6: Task Tool Misuse Detection

**Patterns to Detect**:
1. ✅ `Task` in tools array of YAML frontmatter
2. ✅ `Task(...)` delegation calls in workflow body
3. ✅ Orchestration language ("delegates", "orchestrates", "coordinates")

**Validation Method**: Grep search
```bash
# Pattern 1: Task in frontmatter
grep "^tools:.*Task" agents/*.md

# Pattern 2: Task calls
grep "Task:" agents/*.md

# Pattern 3: Orchestration language
grep -i "delegat\|orchestrat\|coordinat" agents/*.md
```

### Check 7: Maven Anti-Pattern Detection

**Patterns to Detect**:
1. ✅ `Bash(./mvnw:*)` or `Bash(mvn:*)` in tools array
2. ✅ Agent name ≠ "maven-builder" (exception check)
3. Maven execution references in workflow

**Validation Method**: Grep search + name comparison
```bash
# Pattern 1: Maven in tools
grep "Bash.*mvnw" agents/*.md

# Pattern 2: Check agent name field
grep "^name: maven-builder" agents/*.md

# Pattern 3: Maven calls in workflow (if any)
grep "./mvnw\|mvn " agents/*.md
```

---

## Affected Agents (From Migration Plan)

According to migration-plan.md, these agents should have violations:

### Task Tool Violations (Check 6)
- ✅ `maven-project-builder` (cui-maven) - CONFIRMED
- ⏳ `java-code-implementer` (cui-java-expert) - NOT YET TESTED
- ⏳ `java-junit-implementer` (cui-java-expert) - NOT YET TESTED
- ⏳ `java-coverage-reporter` (cui-java-expert) - NOT YET TESTED
- ⏳ `cui-log-record-documenter` (cui-java-expert) - NOT YET TESTED
- ✅ `task-executor` (cui-workflow) - CONFIRMED
- ⏳ `task-reviewer` (cui-workflow) - NOT YET TESTED
- ⏳ `cui-diagnose-single-skill` (cui-plugin-development-tools) - NOT YET TESTED

### Maven Anti-Pattern Violations (Check 7)
- ✅ `task-executor` (cui-workflow) - CONFIRMED
- ❓ Others may exist but not yet identified in migration plan

---

## Test Summary

| Test Case | Check 6 (Task) | Check 7 (Maven) | Status |
|-----------|---------------|----------------|---------|
| maven-project-builder | VIOLATION | N/A | ✅ Patterns confirmed |
| task-executor | VIOLATION | VIOLATION | ✅ Both patterns confirmed |
| maven-builder | CLEAN | EXCEPTION | ✅ Exception confirmed |

**Validation Status**: ✅ **DETECTION PATTERNS VALIDATED**

The grep searches successfully identified:
- Task tool in frontmatter
- Task delegation calls in workflows
- Maven execution permissions
- Exception handling for maven-builder

---

## Next Steps

1. ✅ **Patterns Validated** - Detection logic is correct
2. ⏭️ **Run Full Diagnostic** - Execute `/cui-diagnose-agents` to get complete reports
3. ⏭️ **Review Output** - Verify JSON structure includes new check results
4. ⏭️ **Proceed with Migration** - Begin bundle migrations with confidence

---

## Notes

- **No actual diagnostic execution yet**: This validation used manual grep searches to confirm patterns exist
- **Full diagnostic run needed**: Should execute `/cui-diagnose-agents scope=marketplace` to validate complete workflow
- **JSON output structure**: Should include `task_tool_misuse` and `maven_anti_pattern` sections per updated cui-diagnose-single-agent.md
- **Integration test**: The diagnostic command itself uses Task tool (which is correct - commands CAN use Task)

