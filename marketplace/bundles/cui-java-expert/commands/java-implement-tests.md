---
name: java-implement-tests
description: Self-contained command for JUnit test implementation with verification and iteration
---

# Java Implement Tests Command

Self-contained command that implements JUnit tests with full standards compliance, verifies with maven-builder, and iterates until tests pass.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command, **YOU MUST immediately update this file** using `/plugin-update-command command-name=cui-java-implement-tests update="[your improvement]"` with improvements discovered.

## PARAMETERS

- **task** (required): Test implementation task description
- **types** (optional): Fully qualified name(s) of existing Java type(s) to be tested
- **module** (optional): Module name for multi-module projects

## WORKFLOW (FOLLOW EXACTLY)

### Step 1: Parse and Verify Input Parameters

**Required Parameters:**
- **task** or equivalent description: Detailed description of what aspects/behaviors to test
- **types**: (Optional) Fully qualified name(s) of existing Java type(s) to be tested
- **module**: (Optional) Module name for multi-module projects; if unset, assume single-module

**Verification Process:**

1. **Verify types exist** (if provided):
   - Use Grep to search for each type in codebase
   - Verify types are in src/main/java (not test code)
   - Confirm types are accessible for testing
   - Track results: `types_found`, `types_missing`

2. **Analyze description for completeness**:
   - Check for specific test scenarios described
   - Verify clarity on what behaviors to test
   - Identify edge cases mentioned
   - Check for ambiguous language ("maybe", "probably", "could")
   - Verify coverage expectations are clear

3. **Verify module parameter** (if multi-module):
   - Use Glob to find pom.xml files
   - If module specified: verify module exists
   - If module unset: confirm single-module project
   - Track: `module_name`, `is_multi_module`

4. **Decision point**:
   - If any type missing: Return error with type names not found
   - If description incomplete/ambiguous: Return specific questions to user
   - If module invalid: Return error with available modules
   - If all verified: Proceed to Step 2

**SPECIAL CASE: Fix Build/Tests Mode**

If the description explicitly indicates the task is to **fix the build or failing tests** (e.g., "fix test failures", "resolve failing tests", "fix the build"):
- Skip Step 2 (Build Precondition) - broken build/tests ARE the task
- Proceed directly to Step 3 (Load Testing Standards)
- Step 4 verification becomes primary check that fixes worked

**Detection keywords**: "fix tests", "fix test failures", "resolve failing tests", "tests are failing", "fix build", "fix compilation"

### Step 2: Verify Build Precondition

**Build Verification:**

1. **Determine build scope**:
   - If multi-module and module specified: build only that module
   - If multi-module and module unset: build all modules
   - If single-module: build entire project

2. **Execute build verification**:
   ```
   Task:
     subagent_type: maven-builder
     description: Verify build precondition
     prompt: |
       Execute Maven build to verify clean starting point.

       Goals: clean test
       Module: {module if specified}
       Output mode: STRUCTURED

       Return structured results including all errors, warnings, and test failures.
   ```

3. **Analyze build result**:
   - If SUCCESS with 0 issues: Proceed to Step 3
   - If FAILURE or any issues: Return error to user
   - Codebase MUST compile cleanly and all existing tests must pass

**Critical Rule**: Do not proceed if build has ANY errors, warnings, or test failures. Return immediately to user.

### Step 3: Load Testing Standards and Analyze Code

**Load Testing Standards:**

1. **Always load cui-java-unit-testing skill**:
   ```
   Skill: cui-java-unit-testing
   ```
   This skill will conditionally load all applicable testing standards based on the context.

2. **Analyze code under test**:
   - Use Read to load each type to be tested
   - Identify class structure (value object? service? utility?)
   - Check for equals/hashCode/toString (value object contracts)
   - Identify public methods and behaviors
   - Check for dependencies and collaborators
   - Note frameworks in use (CDI? Quarkus?)
   - Identify logging patterns
   - Check existing test files (if any)

3. **Determine applicable testing patterns**:
   - Value object contract testing needed? (equals/hashCode/toString present)
   - Generator framework applicable? (check for test-generator dependency)
   - HTTP testing needed? (HttpClient usage detected)
   - Integration testing needed? (multi-component interaction)
   - JUL logger testing needed? (java.util.logging usage)

4. **Create holistic testing view**:
   - Map test requirements to testing standards
   - Identify test data generation strategy
   - Plan parameterized test opportunities
   - Determine assertion patterns
   - Plan edge case coverage
   - Identify exception testing needs

### Step 4: Create Comprehensive Test Plan

**Planning Process:**

1. **Plan test class structure**:
   - Test class name (TypeNameTest)
   - @EnableGeneratorController usage
   - Field declarations for SUT and dependencies
   - Setup methods (@BeforeEach if needed)
   - Test method organization (group by behavior)

2. **Plan individual test methods**:
   - For each public method in type under test
   - For each behavior described in requirements
   - For each edge case identified
   - Happy path tests
   - Error path tests
   - Boundary condition tests
   - Parameterized test opportunities (3+ similar variants)

3. **Plan value object contract testing** (if applicable):
   - Implement ShouldHandleObjectContracts<T>
   - Implement getUnderTest() with generators
   - Separate contract tests from behavior tests

4. **Plan test data strategy**:
   - Use Generators.* for all test data
   - Identify appropriate generator types
   - Plan composite generators for complex objects
   - No hardcoded test data

5. **Plan assertion strategy**:
   - Meaningful assertion messages (20-60 chars)
   - Appropriate assertion methods
   - Exception testing with assertThrows
   - Multiple assertions when needed (with messages)

6. **Document test plan**:

**Example Test Plan Format:**
```
Test Plan for UserValidator:

Test Class: UserValidatorTest
- @EnableGeneratorController
- @DisplayName("UserValidator Tests")

Test Methods:

1. shouldValidateCorrectEmail
   - Arrange: Generate valid email using Generators.emailAddress()
   - Act: Call validateEmail()
   - Assert: Returns true
   - Message: "Valid email should pass validation"

2. shouldRejectInvalidEmail (Parameterized)
   - @GeneratorsSource with invalid email patterns
   - Count: 5 variants
   - Assert: Returns false for each
   - Message: "Invalid email format should fail validation"

3. shouldThrowExceptionForNullEmail
   - Arrange: null email
   - Act/Assert: assertThrows(IllegalArgumentException.class)
   - Message: "Null email should throw IllegalArgumentException"

4. shouldValidateCorrectPhone
   - Arrange: Generate valid phone using Generators.strings()
   - Act: Call validatePhone()
   - Assert: Returns true
   - Message: "Valid phone number should pass validation"

Coverage: All public methods, happy paths, error paths, null checks
```

### Step 5: Implement Tests Step-by-Step

**Implementation Loop:**

For each test method in the plan:

1. **Create/modify test file**:
   - If test file doesn't exist: Use Write to create new test class
   - If test file exists: Use Edit to add new test methods
   - Place in src/test/java with same package as code under test
   - Follow AAA pattern strictly (Arrange-Act-Assert)

2. **Apply testing standards**:
   - Use @EnableGeneratorController on test class
   - Add @DisplayName to test class and methods
   - Use Generators.* for all test data
   - Include meaningful assertion messages
   - Follow proper exception testing patterns
   - No hardcoded data, no manual object creation

3. **Implement value object contracts** (if applicable):
   - Add ShouldHandleObjectContracts<T> interface
   - Implement getUnderTest() using generators
   - No additional methods needed (interface provides tests)

4. **Track implementation progress**:
   - Count test methods implemented
   - Note test patterns used
   - Track coverage areas addressed

**Implementation Patterns:**

Reference patterns from loaded `cui-java-unit-testing` skill:
- AAA (Arrange-Act-Assert) pattern from testing standards
- Test generator usage (@EnableGeneratorController, Generators API)
- Parameterized testing with @GeneratorsSource
- Exception testing with assertThrows()
- @DisplayName usage for readable test names

### Step 6: Verify Testing Standards Compliance

**Standards Verification Checklist:**

1. **Core JUnit 5 Compliance**:
   - [ ] All tests follow AAA pattern
   - [ ] All assertions have meaningful messages (20-60 chars)
   - [ ] @DisplayName used on test class and methods
   - [ ] Test independence verified (no shared state)
   - [ ] Exception testing uses assertThrows
   - [ ] No System.out or System.err

2. **CUI Test Framework Compliance**:
   - [ ] @EnableGeneratorController present on test classes
   - [ ] All test data uses Generators.* (no hardcoded data)
   - [ ] No @GeneratorSeed annotations present
   - [ ] Parameterized tests use @GeneratorsSource (for 3+ variants)
   - [ ] No prohibited libraries (Mockito, Hamcrest, PowerMock)

3. **Value Object Contract Compliance** (if applicable):
   - [ ] ShouldHandleObjectContracts<T> interface implemented
   - [ ] getUnderTest() uses generators
   - [ ] Separate test class for contracts vs behavior

4. **Test Quality Compliance**:
   - [ ] Test methods are focused and independent
   - [ ] Meaningful test names (shouldDoXWhenY pattern)
   - [ ] Edge cases covered
   - [ ] Null checks tested where applicable
   - [ ] No commented-out code

**Verification Process:**

1. Read all implemented test files
2. Check each item systematically
3. If ANY item unchecked: Identify violations
4. Use Edit to fix violations
5. Re-verify until ALL items checked
6. **NO TOLERANCE** for non-compliance

**Critical Rule**: There is ZERO tolerance for testing standards violations. Every checklist item must pass.

### Step 7: Verify Tests with Maven

**Test Verification:**

1. **Determine test scope** (same as Step 2)

2. **Execute tests**:
   ```
   Task:
     subagent_type: maven-builder
     description: Run tests
     prompt: |
       Execute Maven build to run tests.

       Goals: test
       Module: {module if specified}
       Output mode: STRUCTURED

       Return structured results including test execution results.
   ```

3. **Analyze test result**:
   - If SUCCESS with 0 test failures: Proceed to Step 8
   - If test FAILURE:
     - Analyze failures (test bug vs production bug)
     - If test bug: Return to Step 5, fix tests
     - If production bug: Document and report
     - Repeat up to 3 iterations total for test bugs
     - If still failing after 3 iterations: Return error with details

**Iteration Counter**: Track test attempts, max 3 cycles of implement → verify → fix.

**Production Bug Detection**: If tests are correct but fail due to production code issues:
- Document the suspected production bug
- Return partial success with production issues noted
- Tests are standards-compliant and will pass once production code fixed

### Step 8: Return Test Implementation Results

**Only return to user after:**
- Test implementation is complete
- All standards compliance checks pass
- Tests execute successfully OR production bugs documented

**Success Response Format:**

```
TEST IMPLEMENTATION COMPLETE

What Was Tested:
- com.example.UserValidator: email validation, phone validation, null handling
- Coverage: all public methods, happy paths, error paths, edge cases

Test Files Created/Modified:
- src/test/java/com/example/UserValidatorTest.java (created)
  - 8 test methods
  - 3 parameterized tests
  - Full method coverage

Testing Standards Applied:
✅ Core JUnit 5 (AAA pattern, @DisplayName, meaningful assertions)
✅ CUI Framework (@EnableGeneratorController, Generators.* for all data)
✅ Test Quality (focused methods, edge cases, null checks)
✅ No prohibited libraries

Test Results: ✅ 8 tests passed, 0 failures, 0 skipped
Test Execution Time: 1.2s
Module: {module-name or "all modules"}

Test Coverage Achieved:
- UserValidator.validateEmail(): 100% (happy path, error cases, null checks)
- UserValidator.validatePhone(): 100% (happy path, error cases, null checks)
- UserValidator.validate(): 100% (integration of both validations)

Standards Compliance: ✅ FULL COMPLIANCE
- Core JUnit 5: 6/6 checks passed
- CUI Framework: 5/5 checks passed
- Test Quality: 5/5 checks passed

Summary:
- Iterations: {count}
- Test execution attempts: {count}
- Tests created: {count}
- Tests passed: {count}

Result: ✅ POSITIVE - All tests implemented successfully and passing
```

**Partial Success Response Format (production bugs found):**

```
TEST IMPLEMENTATION COMPLETE WITH PRODUCTION CODE ISSUES

What Was Tested:
- com.example.UserValidator: email validation, phone validation, null handling
- Coverage: all public methods, happy paths, error paths, edge cases

Test Files Created/Modified:
- src/test/java/com/example/UserValidatorTest.java (created)
  - 10 test methods
  - 3 parameterized tests
  - Full method coverage

Testing Standards Applied:
✅ Core JUnit 5 (AAA pattern, @DisplayName, meaningful assertions)
✅ CUI Framework (@EnableGeneratorController, Generators.* for all data)
✅ Test Quality (focused methods, edge cases, null checks)

Test Results: ⚠️ 8 tests passed, 2 failures (production code bugs)
Test Execution Time: 1.5s
Module: {module-name or "all modules"}

Standards Compliance: ✅ FULL COMPLIANCE
- All test code follows standards
- Failures are in production code

PRODUCTION CODE ISSUES DETECTED:

Issue 1:
- Type: com.example.UserValidator
- Method: validateEmail(String email)
- Failure: NullPointerException thrown instead of IllegalArgumentException
- Test: UserValidatorTest.shouldThrowExceptionForNullEmail
- Suspected Reason: Missing null check at method entry. Expected defensive
  validation with Objects.requireNonNull() or manual null check throwing
  IllegalArgumentException per API contract.

Issue 2:
- Type: com.example.UserValidator
- Method: validatePhone(String phone)
- Failure: Returns true for invalid phone number "+1234"
- Test: UserValidatorTest.shouldRejectInvalidPhoneFormat
- Suspected Reason: Regex pattern appears incomplete. Current pattern
  doesn't enforce minimum length or proper structure.

Result: ⚠️ PARTIAL SUCCESS
- All test code implemented correctly per standards
- Production code has 2 suspected defects requiring review
- Tests properly identify the issues and will pass once production code fixed
```

## CRITICAL RULES

**Input Verification:**
- ALWAYS verify types exist in codebase
- ALWAYS check description for completeness
- ALWAYS verify module parameter if multi-module
- NEVER proceed with missing types or unclear requirements
- RETURN to user immediately if verification fails

**Build Precondition (Step 2):**
- ALWAYS verify requirements are met BEFORE implementing tests
- NEVER proceed if types to test are missing
- RETURN to user immediately if preconditions fail
- Codebase must compile and all existing tests must pass

**Standards Loading:**
- ALWAYS load cui-java-unit-testing skill
- TRUST skill to load applicable standards conditionally
- ALWAYS create holistic testing view before implementing
- NEVER skip standards loading

**Code Analysis:**
- ALWAYS analyze code under test thoroughly
- ALWAYS identify applicable testing patterns
- ALWAYS plan comprehensive test coverage
- NEVER skip edge cases or error paths

**Test Implementation:**
- ALWAYS follow AAA pattern strictly
- ALWAYS use Generators.* for test data
- ALWAYS include meaningful assertion messages
- ALWAYS use @DisplayName for readability
- NEVER use hardcoded test data
- NEVER use prohibited testing libraries

**Test Verification:**
- ALWAYS verify tests with maven-builder
- ALWAYS use "test" goal at minimum
- ANALYZE test failures (test bug vs production bug)
- FIX test bugs and iterate (max 3 iterations)
- DOCUMENT production bugs but do not fix them

**Standards Verification:**
- ALWAYS verify all testing standards compliance
- CHECK every compliance item systematically
- FIX any standards violations immediately
- ZERO tolerance for non-compliance
- Return only after full compliance achieved
- NO CHANGES to production code ever

**Return Format:**
- RETURN when test implementation is complete and standards compliant
- ALWAYS include complete test summary
- ALWAYS list files created/modified
- ALWAYS report standards compliance status
- DOCUMENT production bugs if found

## TOOL USAGE

- **Read**: Load types under test, existing tests, analyze code structure
- **Write**: Create new test files
- **Edit**: Modify existing test files, fix standards violations
- **Glob**: Find pom.xml files, identify modules, locate test files
- **Grep**: Verify types exist, search for patterns, find dependencies
- **Skill**: Load cui-java-unit-testing (loads all applicable testing standards)
- **Task**: Invoke maven-builder agent for test verification

## ARCHITECTURE

This is a Layer 2 self-contained command:

```
/java-implement-tests (Layer 2: Single-item orchestration)
  ├─> Implement tests directly (no agent delegation)
  ├─> Task(maven-builder) [Layer 3: executes tests]
  ├─> Analyze and iterate (max 3 cycles)
  └─> Return result
```

**Key Design:**
- Self-contained: Implements tests directly without agent delegation
- Verification: Uses maven-builder for test execution (Rule 7 compliance)
- Iteration: Max 3 test-fix cycles
- Can be invoked by users OR Layer 1 batch commands
- Production bug detection: Documents production issues without fixing them

## RELATED

- `maven-builder` - Test execution agent (Layer 3)
- `/orchestrate-java-task` - Orchestrates multiple test tasks (Layer 1)
- `cui-java-unit-testing` - Testing standards skill
- `/java-implement-code` - Production code implementation (Layer 2)

## USAGE EXAMPLES

```
/java-implement-tests task="Test UserService.getUserById method"

/java-implement-tests task="Create comprehensive tests for TokenValidator" types="com.example.auth.TokenValidator" module="auth-service"

/java-implement-tests task="Fix failing tests in UserRepository"
```
