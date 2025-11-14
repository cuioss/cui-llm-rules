---
name: cui-java-implement-code
description: Self-contained command for Java code implementation with verification and iteration
---

# Java Implement Code Command

Self-contained command that implements Java code with full standards compliance, verifies with maven-builder, and iterates until clean.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command, **YOU MUST immediately update this file** using `/plugin-update-command command-name=cui-java-implement-code update="[your improvement]"` with improvements discovered.

## PARAMETERS

- **task** (required): Implementation task description
- **types** (optional): Existing type(s), package(s), or name(s) of type(s) to be created
- **module** (optional): Module name for multi-module projects

## WORKFLOW (FOLLOW EXACTLY)

### Step 1: Parse and Verify Input Parameters

**Required Parameters:**
- **task** or equivalent description: Detailed, precise description of what to implement
- **types**: (Optional) Existing type(s), package(s), or name(s) of type(s) to be created
- **module**: (Optional) Module name for multi-module projects; if unset, assume single-module

**Verification Process:**

1. **Parse types parameter** (if provided):
   - If existing types: Use Grep to verify existence in codebase
   - If new types: Validate naming follows Java conventions
   - If package: Verify package structure exists or needs creation
   - Track results: `types_found`, `types_to_create`

2. **Analyze description for clarity**:
   - Check for ambiguous language ("maybe", "possibly", "could")
   - Verify all requirements are specific and measurable
   - Identify any missing information
   - List assumptions that need confirmation

3. **Verify module parameter** (if multi-module):
   - Use Glob to find pom.xml files
   - If module specified: verify module exists
   - If module unset: confirm single-module project
   - Track: `module_name`, `is_multi_module`

4. **Decision point**:
   - If types don't exist when they should: Return error asking user to clarify
   - If description has ambiguities: Return specific questions to user
   - If description incomplete: Return list of missing information
   - If module invalid: Return error with available modules
   - If all clear: Proceed to Step 2

**SPECIAL CASE: Fix Build Mode**

If the description explicitly indicates the task is to **fix the build** (e.g., "fix compilation errors", "resolve build failures", "fix the build"):
- Skip Step 2 (Build Precondition) - broken build IS the task
- Proceed directly to Step 3 (Analyze Code Context)
- Step 4 verification becomes primary check that fix worked

**Detection keywords**: "fix build", "fix compilation", "resolve build errors", "build is broken", "doesn't compile"

### Step 2: Verify Build Precondition

**Build Verification:**

1. **Determine build scope**:
   - If multi-module project: identify module containing changes
   - If single module: build entire project
   - Use Glob to find pom.xml locations if needed

2. **Execute build verification**:
   ```
   Task:
     subagent_type: maven-builder
     description: Verify build precondition
     prompt: |
       Execute Maven build to verify clean starting point.

       Goals: clean compile
       Module: {module if specified}
       Output mode: STRUCTURED

       Return structured results including all errors and warnings.
   ```

3. **Analyze build result**:
   - If SUCCESS with 0 issues: Proceed to Step 3
   - If FAILURE or any issues: Return error to user
   - Codebase MUST compile cleanly before implementation

**Critical Rule**: Do not proceed if build has ANY errors or warnings. Return immediately to user.

### Step 3: Analyze Code Context

**Context Analysis:**

1. **Load existing types** (if working with existing code):
   - Use Read to load all related Java files
   - Identify class structure, dependencies, patterns
   - Note existing patterns:
     - **Creational**: Builder pattern, Factory pattern, Records for data carriers
     - **Structural**: Service classes, Repository pattern, Utility classes (@UtilityClass)
     - **Behavioral**: Strategy pattern, Command pattern, Template method
     - **Domain**: Value objects (@Value), Entities, DTOs, Domain services

2. **Analyze package structure**:
   - Use Glob to find related files in package
   - Identify naming conventions (Service, Repository, Validator, Processor, etc.)
   - Check for existing test files (*Test.java)
   - Note architectural layers:
     - **Presentation**: Controllers, REST endpoints
     - **Application**: Services, Use cases, Application logic
     - **Domain**: Entities, Value objects, Domain services
     - **Infrastructure**: Repositories, External integrations, Persistence

3. **Identify dependencies**:
   - Check imports in related files
   - Identify frameworks in use (CDI? Quarkus?)
   - Note logging patterns
   - Check for existing utilities

4. **Document understanding**:
   - Summarize current state
   - Identify integration points
   - Note constraints or requirements
   - List related components

### Step 4: Load Standards and Create Holistic View

**Load Required Standards:**

1. **Always load core Java standards**:
   ```
   Skill: cui-java-core
   ```

2. **Load additional standards on-demand based on context**:

   **CDI/Quarkus** (load if context shows CDI annotations, @Inject, Quarkus usage):
   ```
   Skill: cui-java-cdi
   ```

3. **Create holistic implementation view**:
   - Map requirements to standards patterns
   - Identify applicable Lombok annotations
   - Determine logging needs (LogMessages?)
   - Plan null-safety approach (@NullMarked)
   - Select modern Java features (records? switch expressions?)
   - Identify exception handling patterns

4. **Document approach**:
   - List standards to apply
   - Describe implementation strategy
   - Note critical compliance points
   - Identify potential challenges

### Step 5: Create Implementation Plan

**Planning Process:**

1. **Break down into steps**:
   - Create/modify types in logical order
   - Add package-info.java if needed
   - Implement core functionality
   - Add logging infrastructure
   - Apply Lombok annotations
   - Implement null safety

2. **For each step, document**:
   - What will be created/modified
   - Which standards apply
   - Expected outcome
   - Verification criteria

3. **Example plan format**:
   ```
   Step 1: Create package-info.java with @NullMarked
   - Standards: java-null-safety.md
   - Verification: File exists, annotation present

   Step 2: Create UserValidator.java using @Value and @Builder
   - Standards: java-lombok-patterns.md, java-core-patterns.md
   - Verification: Compiles, follows immutability pattern

   Step 3: Add LogMessages class with DSL structure
   - Standards: logging-standards.md, dsl-constants.md
   - Verification: Proper identifier ranges, @UtilityClass used

   Step 4: Implement validation logic with Optional returns
   - Standards: java-null-safety.md, java-modern-features.md
   - Verification: No @Nullable on returns, proper null checks
   ```

### Step 6: Execute Implementation Step-by-Step

**Implementation Loop:**

For each step in the plan:

1. **Execute the step** using Write/Edit tools:
   - Create new files with Write
   - Modify existing files with Edit
   - Follow standards precisely
   - Apply patterns consistently

2. **Document critical decisions**:
   - Why specific approach chosen
   - Trade-offs considered
   - Assumptions made
   - **Add to JavaDoc** (not command output)

3. **Verify step completion**:
   - Check file created/modified
   - Verify syntax correctness
   - Confirm standards applied
   - Move to next step

**Example critical decision documentation (in JavaDoc):**
```java
/**
 * Validates user input using defensive null checks.
 *
 * <p><strong>Design Decision:</strong> Returns Optional rather than throwing exceptions
 * to allow callers to handle missing results gracefully. Validation errors still throw
 * IllegalArgumentException as they represent programming errors, not business logic.</p>
 *
 * @param input the user input to validate (never null)
 * @return Optional containing validated result, empty if validation rules not met
 * @throws IllegalArgumentException if input is null (programming error)
 */
```

### Step 7: Verify Build with Maven (Post-Implementation)

**Build Verification:**

1. **Determine build scope** (same as Step 2)

2. **Execute build**:
   ```
   Task:
     subagent_type: maven-builder
     description: Verify implementation build
     prompt: |
       Execute Maven build to verify implementation.

       Goals: clean compile test
       Module: {module if specified}
       Output mode: STRUCTURED

       Return structured results including all errors and warnings.
   ```

3. **Analyze build result**:
   - If SUCCESS with 0 issues: Proceed to Step 8
   - If FAILURE or issues found:
     - Analyze issues (compilation errors? test failures?)
     - If fixable: Return to Step 6, fix issues
     - Repeat up to 3 iterations total
     - If still failing after 3 iterations: Return error with details

**Iteration Counter**: Track build attempts, max 3 cycles of implement → verify → fix.

### Step 8: Verify Implementation Against Requirements

**Requirements Verification:**

1. **Review original description**:
   - List each requirement explicitly
   - Create checklist of functionality

2. **Verify each requirement**:
   - Read implemented code
   - Confirm requirement implemented
   - Check implementation correctness
   - Verify edge cases handled

3. **Decision point**:
   - If any requirement NOT implemented: Return to Step 6, implement missing functionality
   - If any requirement implemented INCORRECTLY: Return to Step 6, correct implementation
   - If all requirements verified: Proceed to Step 9

**Verification Format:**
```
Requirement Verification:

✅ Validate user email format
   - Implemented in UserValidator.validate()
   - Uses regex pattern for RFC 5322 compliance
   - Handles null input with IllegalArgumentException

✅ Return Optional for missing results
   - All query methods return Optional<T>
   - Empty Optional returned when no match found
   - Never returns null

❌ Log validation failures
   - ISSUE: Logging not implemented
   - FIX NEEDED: Add LogMessages and logger calls
```

### Step 9: Verify Standards Compliance

**Standards Verification Checklist:**

1. **Null Safety Compliance**:
   - [ ] @NullMarked present in package-info.java
   - [ ] No @Nullable used for return types
   - [ ] Optional used for "no result" scenarios
   - [ ] Defensive null checks at API boundaries
   - [ ] Objects.requireNonNull() used for validation

2. **Lombok Compliance**:
   - [ ] @Builder used for complex construction (3+ parameters)
   - [ ] @Value used for immutable objects
   - [ ] @Delegate used for composition patterns
   - [ ] @UtilityClass used for utility classes
   - [ ] No @Slf4j or SLF4J annotations

3. **Modern Features Compliance**:
   - [ ] Records used for simple data carriers
   - [ ] Switch expressions used (not statements)
   - [ ] Streams used appropriately
   - [ ] Text blocks used for multi-line strings
   - [ ] Modern collection factories used (List.of(), Set.of())

4. **Logging Compliance**:
   - [ ] CuiLogger used (not SLF4J/Log4j)
   - [ ] Logger is private static final named LOGGER
   - [ ] LogRecord used for important messages
   - [ ] Exception parameter comes first in log calls
   - [ ] %s used for substitutions
   - [ ] No System.out or System.err

5. **Core Patterns Compliance**:
   - [ ] Classes follow Single Responsibility Principle
   - [ ] Methods are focused (< 50 lines)
   - [ ] Meaningful names used throughout
   - [ ] Exception handling appropriate
   - [ ] Immutability used where possible
   - [ ] No magic numbers

**Verification Process:**

1. Read implemented files
2. Check each item systematically
3. If ANY item unchecked: Identify violations
4. Return to Step 6 to fix violations
5. Re-verify until ALL items checked
6. **NO TOLERANCE** for non-compliance

**Critical Rule**: There is ZERO tolerance for standards violations. Every checklist item must pass.

### Step 10: Return Implementation Results

**Only return to user after ALL verifications pass.**

**Return Format:**

```
IMPLEMENTATION COMPLETE

What Was Implemented:
- Created UserValidator.java with email/phone validation
- Added package-info.java with @NullMarked
- Implemented ValidationLogMessages with DSL structure
- Added defensive null checks at all API boundaries

Files Created/Modified:
- src/main/java/com/example/auth/package-info.java (created)
- src/main/java/com/example/auth/UserValidator.java (created)
- src/main/java/com/example/auth/ValidationLogMessages.java (created)

Standards Applied:
✅ Null safety (@NullMarked, Optional returns, defensive checks)
✅ Lombok (@Value, @Builder for UserValidator)
✅ Modern features (records for ValidationResult, switch expressions)
✅ CUI logging (CuiLogger, LogRecord with proper patterns)
✅ Core patterns (SRP, immutability, meaningful names)

Build Status: ✅ SUCCESS (no errors, no warnings)

Requirements Verification: ✅ ALL VERIFIED
Standards Compliance: ✅ FULL COMPLIANCE

Critical Decisions Documented in JavaDoc:
- UserValidator uses Optional returns for business logic (see class JavaDoc)
- ValidationResult implemented as record for immutability (see type JavaDoc)
- LogMessages organized by severity level (see class JavaDoc)

Summary:
- Iterations: {count}
- Build attempts: {count}
- Files created: {count}
- Files modified: {count}
```

## CRITICAL RULES

**Input Verification:**
- ALWAYS verify types exist or can be created
- ALWAYS check description for ambiguities
- ALWAYS return to user if verification fails
- NEVER proceed with unclear requirements

**Build Precondition (Step 2):**
- ALWAYS verify clean compile BEFORE implementation
- NEVER proceed if build has errors
- NEVER proceed if build has warnings
- RETURN to user immediately if build not clean

**Context Analysis:**
- ALWAYS analyze existing code patterns
- ALWAYS identify related components
- ALWAYS understand integration points
- NEVER ignore architectural context

**Standards Loading:**
- ALWAYS load cui-java-core skill
- LOAD cui-java-cdi skill if CDI/Quarkus detected in context
- ALWAYS create holistic view before implementing
- NEVER skip standards loading

**Implementation:**
- ALWAYS follow plan step-by-step
- ALWAYS document critical decisions in JavaDoc
- NEVER skip standards compliance
- ALWAYS apply patterns consistently

**Post-Implementation Build Verification (Step 7):**
- ALWAYS verify with maven-builder
- ALWAYS use "clean compile test" at minimum
- NEVER proceed with build errors
- NEVER proceed with build warnings
- FIX all issues until build is clean (max 3 iterations)

**Requirements Verification:**
- ALWAYS verify against original description
- ALWAYS check each requirement explicitly
- RETURN to implementation if anything wrong
- NEVER claim completion if requirements not met

**Standards Verification:**
- ZERO TOLERANCE for non-compliance
- ALWAYS verify ALL checklist items
- RETURN to implementation if violations found
- NEVER skip verification steps
- DOUBLE CHECK everything

**Return Format:**
- ONLY return when everything verified
- ALWAYS include complete summary
- ALWAYS list files created/modified
- DOCUMENT critical decisions in JavaDoc (not return message)

## TOOL USAGE

- **Read**: Load existing Java files, analyze context
- **Write**: Create new Java files, package-info.java
- **Edit**: Modify existing Java files
- **Glob**: Find related files, pom.xml locations
- **Grep**: Search for types, patterns, dependencies
- **Skill**: Load cui-java-core (always) and cui-java-cdi (when needed)
- **Task**: Invoke maven-builder agent for build verification

## ARCHITECTURE

This is a Layer 2 self-contained command:

```
/cui-java-implement-code (Layer 2: Single-item orchestration)
  ├─> Implement code directly (no agent delegation)
  ├─> Task(maven-builder) [Layer 3: verifies builds]
  ├─> Analyze and iterate (max 3 cycles)
  └─> Return result
```

**Key Design:**
- Self-contained: Implements code directly without agent delegation
- Verification: Uses maven-builder for builds (Rule 7 compliance)
- Iteration: Max 3 build-fix cycles
- Can be invoked by users OR Layer 1 batch commands

## RELATED

- `maven-builder` - Build verification agent (Layer 3)
- `/cui-orchestrate-java-task` - Orchestrates multiple implementations (Layer 1)
- `cui-java-core` - Core Java standards skill
- `cui-java-cdi` - CDI/Quarkus standards skill

## USAGE EXAMPLES

```
/cui-java-implement-code task="Add getUserById method to UserService"

/cui-java-implement-code task="Create TokenValidator service" types="TokenValidator" module="auth-service"

/cui-java-implement-code task="Fix compilation errors in UserRepository"
```
