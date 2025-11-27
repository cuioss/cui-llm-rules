= Fix Build Mode
:toc: left
:toclevels: 3
:sectnums:

== Overview

This standard defines the fix-build mode workflow for Java implementation tasks. Fix-build mode is a special case where the task IS to fix a broken build, requiring different workflow than normal implementation.

== Core Principle

**When fixing the build, the broken build IS the task.** Skip build precondition checks and focus directly on analyzing and resolving build failures.

== Rationale

=== Why Fix-Build Mode Differs

**Normal Implementation:**

* Precondition: Build must be clean
* Task: Implement new feature
* Verification: Build still clean after implementation

**Fix-Build Implementation:**

* Precondition: Build is expected to fail (skip check)
* Task: Fix the broken build
* Verification: Build succeeds after fixes

**Key Difference:** Build precondition check would be circular - checking if build is clean when task is to make it clean.

== Fix-Build Detection

=== Detection Keywords

Automatically enter fix-build mode when task description contains:

**Primary Keywords:**

* "fix build"
* "fix compilation"
* "fix compilation errors"
* "resolve build errors"
* "resolve build failures"

**Secondary Keywords:**

* "build is broken"
* "doesn't compile"
* "compilation fails"
* "build fails"
* "fix compiler errors"

**Test-Specific Keywords:**

* "fix test failures"
* "fix failing tests"
* "resolve test failures"
* "tests are failing"

=== Detection Logic

[source]
----
description_lower = description.lower()

fix_build_keywords = [
    'fix build',
    'fix compilation',
    'resolve build',
    'build is broken',
    "doesn't compile",
    'compilation fails'
]

fix_tests_keywords = [
    'fix test',
    'fix failing test',
    'resolve test failure',
    'tests are failing',
    'tests failing'
]

is_fix_build = any(keyword in description_lower for keyword in fix_build_keywords)
is_fix_tests = any(keyword in description_lower for keyword in fix_tests_keywords)

if is_fix_build or is_fix_tests:
    Enter fix-build mode
----

=== Ambiguous Cases

**Requires clarification:**

* "Implement feature and fix any issues"
* "Update code (build might be broken)"
* "Refactor code, there are some errors"

**Action:** Ask user to clarify if this is a fix-build task or normal implementation

== Fix-Build Workflow

=== Modified Workflow Steps

[source]
----
Normal Implementation:
  Step 1: Parse parameters
  Step 2: Verify build precondition ← Check build is clean
  Step 3: Analyze code
  Step 4: Implement
  Step 5: Verify build still clean

Fix-Build Implementation:
  Step 1: Parse parameters
  Step 2: SKIP build precondition ← Build expected to fail
  Step 3: Run build to capture errors
  Step 4: Analyze errors
  Step 5: Fix errors
  Step 6: Verify build now succeeds ← Primary verification
----

=== Step 1: Parse Parameters (Same as Normal)

Parse and verify input parameters:

* types: Types to fix
* description: What to fix
* module: Module to build (if multi-module)

**No change from normal workflow**

=== Step 2: Skip Build Precondition

**Detect fix-build mode:**

[source]
----
if fix_build_detected(description):
    Log: "Fix-build mode detected - skipping build precondition"
    Skip to Step 3
else:
    Execute build precondition check (normal flow)
----

**Rationale:** Build is expected to fail, checking would be circular

=== Step 3: Execute Build to Capture Errors

**Run build to capture current errors:**

[source,bash]
----
# Single-module
mvn clean compile -l target/build-errors-before.log

# Multi-module
mvn clean compile -pl :module-name -l target/build-errors-before.log

# Capture exit code
exit_code=$?
----

**Parse errors:**

[source,bash]
----
python3 parse-maven-output.py \
  --log target/build-errors-before.log \
  --mode structured
----

**Expected output:**

[source,json]
----
{
  "status": "has-errors",
  "exit_code": 1,
  "errors": [
    {
      "file": "src/main/java/com/example/UserService.java",
      "line": 45,
      "message": "cannot find symbol: class Optional",
      "type": "symbol_error"
    },
    {
      "file": "src/main/java/com/example/TokenValidator.java",
      "line": 78,
      "message": "incompatible types: String cannot be converted to Integer",
      "type": "type_error"
    }
  ],
  "summary": {
    "error_count": 2
  }
}
----

=== Step 4: Analyze Errors

**Categorize errors by type:**

[cols="1,2,1"]
|===
|Error Type |Examples |Fix Strategy

|Symbol Errors
|cannot find symbol, package does not exist
|Add imports, fix type names

|Type Errors
|incompatible types, required X found Y
|Fix type mismatches, add casts

|Method Errors
|method not found, cannot be applied
|Fix method calls, parameter types

|Syntax Errors
|';' expected, illegal start of expression
|Fix syntax issues
|===

**Prioritize errors:**

1. **Compilation blocking:** Errors preventing compilation
2. **Cascading errors:** Errors causing other errors
3. **Simple fixes:** Missing imports, typos

=== Step 5: Fix Errors

For each error:

1. **Read affected file** to understand context
2. **Determine fix** based on error type
3. **Apply fix** using Edit tool
4. **Track fix** for reporting

**Common fix patterns:**

**Missing import:**

[source,java]
----
Error: cannot find symbol: class Optional
Fix: Add import java.util.Optional;
----

**Type mismatch:**

[source,java]
----
Error: incompatible types: String cannot be converted to Integer
Fix: Change String to Integer or add Integer.parseInt()
----

**Method not found:**

[source,java]
----
Error: method getUserId() not found
Fix: Change to getId() or add getUserId() method
----

=== Step 6: Verify Build Succeeds

**Run build again to verify fixes:**

[source,bash]
----
mvn clean compile -l target/build-errors-after.log
exit_code=$?

python3 parse-maven-output.py \
  --log target/build-errors-after.log \
  --mode structured
----

**Decision point:**

[source]
----
If status == "clean":
  SUCCESS - Build fixed
  Return BUILD FIXED response

If status == "has-errors":
  Check error count:
    If error_count < previous_error_count:
      PROGRESS - Some errors fixed
      Iterate (max 3 attempts)
    Else:
      FAILURE - No progress
      Return failure with remaining errors

If iteration_count > 3:
  FAILURE - Max iterations reached
  Return failure requesting manual intervention
----

=== Step 7: Return BUILD FIXED Response

**Response format:**

[source]
----
BUILD FIXED ✓

Module: {module-name or "project"}
Command: clean compile

Status Before:
  Errors: {before_count}
  Warnings: {before_warnings}

Fixes Applied:
1. {file1}:{line} - {fix_description}
2. {file2}:{line} - {fix_description}

Status After:
  Errors: 0
  Warnings: 0
  Build: SUCCESS

Verification:
  ✓ Build compiles cleanly
  ✓ All errors resolved
  ✓ No new warnings introduced

Task completed successfully.
----

== Iteration Strategy

=== Maximum Iterations

**Limit:** 3 fix-build-verify iterations

**Rationale:**

* Prevents infinite loops
* Forces escalation if complex issues
* Encourages asking for help

=== Iteration Logic

[source]
----
iteration = 1
max_iterations = 3

while iteration <= max_iterations:
    1. Apply fixes
    2. Run build
    3. Parse results

    if build succeeds:
        Return BUILD FIXED
        break

    if error_count < previous_error_count:
        Log: "Progress made, continuing (iteration {iteration}/{max_iterations})"
        iteration += 1
        continue

    if error_count >= previous_error_count:
        Log: "No progress, stopping"
        Return failure with errors
        break

if iteration > max_iterations:
    Return failure: "Maximum iterations reached, manual intervention required"
----

=== Progress Tracking

Track progress across iterations:

[source,json]
----
{
  "iterations": [
    {
      "iteration": 1,
      "errors_before": 5,
      "fixes_applied": 3,
      "errors_after": 2,
      "progress": true
    },
    {
      "iteration": 2,
      "errors_before": 2,
      "fixes_applied": 2,
      "errors_after": 0,
      "progress": true,
      "build_status": "SUCCESS"
    }
  ],
  "total_iterations": 2,
  "final_status": "BUILD FIXED"
}
----

== Error Handling

=== When Fixes Don't Work

**Symptom:** Error count doesn't decrease after fixes

**Possible Causes:**

* Wrong fix applied
* Cascading errors (fix one, create another)
* Missing dependencies
* Complex type issues

**Action:**

1. Analyze remaining errors
2. Try different fix approach
3. If no progress after 3 iterations, return failure

**Failure Response:**

[source]
----
BUILD FIX INCOMPLETE

Iterations: 3 (maximum reached)
Errors Remaining: {count}

Errors That Could Not Be Fixed:
{
  file: src/main/java/com/example/Service.java
  line: 45
  error: incompatible types
  attempted_fixes: [
    "Changed type from String to Integer",
    "Added type cast",
    "Changed method signature"
  ]
  reason: "Complex type incompatibility requires architecture change"
}

Recommendation:
Manual intervention required. The remaining errors indicate:
- Possible architecture/design issue
- Missing dependency configuration
- Cascading type incompatibility

Suggest:
1. Review type hierarchy
2. Verify dependencies in pom.xml
3. Consider design refactoring
----

=== When Build Succeeds But Tests Fail

**Scenario:** Compilation succeeds but tests fail

[source]
----
If task was "fix build":
  Compilation success = Task complete
  Return BUILD FIXED (ignore test failures)

If task was "fix tests":
  Must fix test failures
  Continue iterating until tests pass
----

== Integration with Commands

=== java-implement-code Command

[source]
----
Step 1: Parse parameters
  ↓
Step 1.5: Check for fix-build keywords
  ↓
  If fix-build detected:
    Skip Step 2 (build precondition)
    Jump to Step 3 (analyze with build capture)
  Else:
    Normal flow (Step 2: build precondition)
  ↓
...
----

=== java-refactor-code Command

[source]
----
Similar modification:
  If "fix build" in description:
    Skip build precondition
    Execute build → Fix errors → Verify
  Else:
    Normal refactoring flow
----

== Response Format Differences

=== Normal Implementation Response

[source]
----
IMPLEMENTATION COMPLETE ✓

Changes:
- Added method foo() to UserService
- Implemented validation logic

Verification:
- Build: SUCCESS
- Tests: 5 new tests passing
----

=== Fix-Build Response

[source]
----
BUILD FIXED ✓

Status Before:
  Errors: 3

Fixes Applied:
- UserService.java:45 - Added import java.util.Optional
- TokenValidator.java:78 - Fixed type mismatch
- DataService.java:112 - Fixed method signature

Status After:
  Errors: 0
  Build: SUCCESS
----

**Key Difference:** Emphasizes before/after build status

== Best Practices

=== For Fix-Build Tasks

**DO:**

* Run build first to capture all errors
* Fix errors in priority order (blocking → cascading → simple)
* Verify after each iteration
* Track progress (error count decreasing)
* Return BUILD FIXED status when complete

**DON'T:**

* Apply build precondition check
* Guess at fixes without seeing errors
* Continue fixing if no progress
* Exceed 3 iterations without escalation
* Mix fix-build with new features

=== For Error Analysis

**DO:**

* Read full error messages including context
* Identify cascading errors (fix root cause first)
* Use script output for systematic analysis
* Categorize errors by type

**DON'T:**

* Fix errors randomly
* Apply partial fixes
* Ignore warning messages
* Skip verification between iterations

== Examples

=== Example 1: Simple Fix-Build (Success)

**Task:**

[source]
----
types: UserValidator
description: Fix compilation errors in UserValidator
module: auth-service
----

**Workflow:**

[source]
----
1. Detect "fix compilation errors" → Fix-build mode
2. Skip build precondition
3. Run build:
   Errors: 1
   - UserValidator.java:23: cannot find symbol: class Duration

4. Fix: Add import java.time.Duration

5. Verify build:
   Status: clean
   Errors: 0

6. Return BUILD FIXED ✓
----

=== Example 2: Multiple Iteration Fix (Success)

**Task:**

[source]
----
types: TokenService, UserService
description: Fix build - multiple compilation errors
----

**Workflow:**

[source]
----
Iteration 1:
  Errors before: 5
  Fixes: 3 (imports, type fixes)
  Errors after: 2
  Progress: Yes → Continue

Iteration 2:
  Errors before: 2
  Fixes: 2 (method signatures)
  Errors after: 0
  Build: SUCCESS

Return BUILD FIXED ✓ (2 iterations)
----

=== Example 3: No Progress (Failure)

**Task:**

[source]
----
description: Fix build errors in DataProcessor
----

**Workflow:**

[source]
----
Iteration 1:
  Errors before: 3
  Fixes: 3 (attempted)
  Errors after: 3 (same errors)
  Progress: No → STOP

Return:
  BUILD FIX INCOMPLETE
  Errors remaining: 3
  Reason: Complex type incompatibilities require manual review
  Recommendation: Review architecture
----

=== Example 4: Max Iterations (Failure)

**Workflow:**

[source]
----
Iteration 1: 8 errors → 6 errors (progress)
Iteration 2: 6 errors → 4 errors (progress)
Iteration 3: 4 errors → 2 errors (progress)
Max iterations reached

Return:
  BUILD FIX INCOMPLETE
  Progress: Yes (8 → 2 errors)
  Remaining: 2 complex errors
  Recommendation: Continue fix in separate task
----

== References

* xref:build-precondition-pattern.md[Build Precondition Pattern]
* xref:implementation-verification.md[Implementation Parameter Verification]
* Java Compilation Errors: https://docs.oracle.com/javase/tutorial/getStarted/problems/index.html[Oracle Java Tutorials]
