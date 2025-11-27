# Specific Workflow: Java Task Implementation with Handoffs

## Overview

This document provides a **complete, step-by-step example** of implementing a Java task using the handoff-based architecture, showing all components, handoffs, and interactions.

**Generic Patterns**: This example applies the generic workflow patterns defined in [04-generic-workflow-patterns.md](04-generic-workflow-patterns.md). Refer to that document for pattern definitions and language-agnostic principles.

**Scenario**: User requests implementation of JWT authentication feature via `/task-implement`

## Complete Workflow Trace

### USER REQUEST

```bash
/task-implement task="Implement JWT authentication service with token validation and refresh"
```

---

### PHASE 1: COMMAND ORCHESTRATION

#### Component: `/task-implement` command

**File**: `cui-task-workflow/commands/task-implement.md`

The command orchestrates the entire workflow directly (~120 lines).

**Step 1: Parse Parameters**
```
task="Implement JWT authentication service with token validation and refresh"
mode=PLAN (no GitHub issue number provided)
language=auto
```

**Step 2: Skip Review (mode=PLAN)**
```
Mode is PLAN, skip Review workflow
Jump to Planning step
```

**Step 3: Planning**

Command generates TOON handoff to task-plan skill:
```toon
from: task-implement-command
to: task-plan-skill
handoff_id: handoff-001
workflow: task-planning
timestamp: 2025-11-26T10:00:15Z

task:
  description: Implement JWT authentication service with token validation and refresh
  type: plan
  status: pending

context:
  mode: PLAN
  input_format: description

next_action: Create structured plan
next_focus: Task breakdown with acceptance criteria
```

**Tool Invocation**:
```markdown
Skill: cui-task-workflow:task-plan
Input: {TOON handoff above}
```

---

#### Component: `task-plan` skill

**Full Specification**: See [06-plan-management-specification/api.md](06-plan-management-specification/api.md) for complete API and abstraction pattern.

**Step 1: Analyze Requirements**
Parse task description and extract key requirements

**Step 2: Generate Task Breakdown**
Create structured breakdown with 4 tasks and acceptance criteria

**Step 3: Write Plan File to Disk**

**File Created**: `.claude/plans/plan-jwt-auth.md`

```markdown
# JWT Authentication Implementation Plan

## Overview
Implement JWT authentication service with token validation and refresh capabilities

## Technical Decisions
- Library: JJWT (io.jsonwebtoken:jjwt-api)
- Algorithm: HS256 for signing
- Access Token Expiry: 24 hours
- Refresh Token Expiry: 7 days

## Tasks

### Task 1: Create JwtService Interface and Implementation
**Acceptance Criteria**:
- Interface defines generateToken(), validateToken(), refreshToken()
- Implementation uses JJWT library

### Task 2: Create TokenValidator with Expiry Checking
**Acceptance Criteria**:
- Validates token signature
- Checks token expiry
- Returns validation result

### Task 3: Implement RefreshTokenService
**Acceptance Criteria**:
- Stores refresh tokens
- Rotates refresh tokens
- Validates refresh tokens

### Task 4: Add Configuration for JWT Secrets
**Acceptance Criteria**:
- application.properties has jwt.secret
- application.properties has jwt.expiry
```

**Step 4: Generate Handoff Response**

**Response from task-plan skill**:
```toon
from: task-plan-skill
to: task-implement-command
handoff_id: handoff-002
workflow: task-planning

task:
  description: Planning complete
  type: plan
  status: completed
  progress: 100%

artifacts:
  plan_file: .claude/plans/plan-jwt-auth.md
  task_count: 4

decisions[4]:
- Use JJWT library (io.jsonwebtoken:jjwt-api)
- HS256 algorithm for signing
- 24-hour access token expiry
- 7-day refresh token expiry

tasks[4]{id,name,acceptance_count}:
1,Create JwtService interface and implementation,2
2,Create TokenValidator with expiry checking,3
3,Implement RefreshTokenService,3
4,Add configuration for JWT secrets,2

task_details:
  task_1: Interface defines generateToken(), validateToken(), refreshToken(); Implementation uses JJWT library
  task_2: Validates token signature; Checks token expiry; Returns validation result
  task_3: Stores refresh tokens; Rotates refresh tokens; Validates refresh tokens
  task_4: application.properties has jwt.secret; application.properties has jwt.expiry

next_action: Execute implementation
next_focus: Task 1: JwtService
```

**Key Pattern**:
- **File on disk**: `.claude/plans/plan-jwt-auth.md` (persistent Markdown artifact, ~50 lines)
- **Handoff references file**: `artifacts.files` and `context.plan_file` point to the file
- **Handoff includes summary**: Task breakdown in `context.tasks` for quick access
- **Downstream components read file**: Using Read tool on `plan_file` path

This keeps handoffs lightweight while preserving full plan details on disk.

---

#### Back to `/task-implement` command

Command receives TOON handoff back from task-plan skill and continues orchestration.

**Step 4: Detect Language**
```
Glob: **/pom.xml → Found: pom.xml
Language: java
Module: auth-service (extracted from pom.xml <artifactId>)
```

**Step 5: Delegate to Java Implementation**

Command generates TOON handoff to java-implement-agent:
```toon
from: task-implement-command
to: java-implement-agent
handoff_id: handoff-003
workflow: java-implementation
timestamp: 2025-11-26T10:02:00Z

task:
  description: Implement JWT authentication service with token validation and refresh
  type: implement
  status: pending

artifacts:
  plan_file: .claude/plans/plan-jwt-auth.md
  plan_tasks: 4

decisions[4]:
- Use JJWT library (io.jsonwebtoken:jjwt-api)
- HS256 algorithm for signing
- 24-hour access token expiry
- 7-day refresh token expiry

context:
  language: java
  module: auth-service
  dependencies: io.jsonwebtoken:jjwt-api
  notes: Plan created with 4 tasks

constraints[2]:
- Must follow CUI Java standards
- Lombok usage required

next_action: Implement Java classes
next_focus: JwtService, TokenValidator, RefreshTokenService
```

**Tool Invocation**:
```markdown
Task:
  subagent_type: cui-java-expert:java-implement-agent
  description: Implement Java feature
  prompt: |
    {TOON handoff above}
```

---

### PHASE 3: JAVA IMPLEMENTATION

#### Component: `java-implement-agent`

**File**: `cui-java-expert/agents/java-implement-agent.md`

**Step 0: Process Handoff Input**
```
Parse incoming handoff:
  - task: "Implement JWT authentication..."
  - plan_file: .claude/plans/plan-jwt-auth.md
  - language: java
  - module: auth-service
  - dependencies: [jjwt-api]
  - decisions: [HS256, 24h expiry, ...]
```

**Step 1: Delegate to cui-java-core Skill**

**Generated TOON Handoff to cui-java-core**:
```toon
from: java-implement-agent
to: cui-java-core-skill
handoff_id: handoff-004
workflow: java-feature-implementation
timestamp: 2025-11-26T10:02:15Z

task:
  description: Implement JWT authentication service
  type: implement
  status: pending

artifacts:
  plan_file: .claude/plans/plan-jwt-auth.md

decisions[4]:
- Use JJWT library
- HS256 algorithm
- 24h access token expiry
- 7-day refresh token expiry

context:
  language: java
  module: auth-service

target_classes[3]:
- JwtService
- TokenValidator
- RefreshTokenService

dependencies[1]:
- io.jsonwebtoken:jjwt-api

constraints[2]:
- CUI Java standards
- Lombok patterns

standards[3]:
- null-safety
- lombok
- logging

next_action: Implement Feature workflow
next_focus: Create classes following plan
```

**Tool Invocation**:
```markdown
Skill: cui-java-expert:cui-java-core
Workflow: Implement Feature
Input: {TOON handoff above}
```

**cui-java-core Skill Actions**:
1. Read standards/java-core-patterns.md
2. Read standards/java-lombok-patterns.md
3. Read standards/logging-standards.md
4. Read .claude/plans/plan-jwt-auth.md
5. Implement JwtService.java
6. Implement TokenValidator.java
7. Implement RefreshTokenService.java
8. Update pom.xml with dependency
9. Update application.properties
10. Build verification (Maven compile)

**Response from cui-java-core skill**:
```toon
from: cui-java-core-skill
to: java-implement-agent
handoff_id: handoff-005
workflow: java-feature-implementation
timestamp: 2025-11-26T10:05:30Z

task:
  description: Java implementation complete
  type: implement
  status: completed
  progress: 100%

files[5]{path}:
src/main/java/com/example/auth/JwtService.java
src/main/java/com/example/auth/TokenValidator.java
src/main/java/com/example/auth/RefreshTokenService.java
pom.xml
src/main/resources/application.properties

interfaces[3]{class,methods}:
JwtService,generateToken(), validateToken(), refreshToken()
TokenValidator,validate(), isExpired()
RefreshTokenService,create(), rotate(), validate()

decisions[4]:
- Lombok @Service for CDI
- Lombok @Slf4j for logging
- Null-safe with @NonNull
- Log all token operations

context:
  language: java
  module: auth-service
  build_status: SUCCESS
  lines_added: 287

standards_applied[4]:
- java-core-patterns
- java-lombok-patterns
- logging-standards
- null-safety

next_action: Verify full build with tests
next_focus: Maven clean verify
```

**Step 2: Return to java-implement-agent**

Agent returns TOON handoff back to java-implement-agent, which then returns to command.

---

### PHASE 4: BUILD VERIFICATION

#### Component: `/task-implement` command (continued)

**Step 5: Verify Build**

Command generates TOON handoff to build-verify-agent:
```toon
from: task-implement-command
to: build-verify-agent
handoff_id: handoff-006
workflow: build-verification
timestamp: 2025-11-26T10:05:45Z

task:
  description: Verify Maven build for JWT implementation
  type: verify
  status: pending

files[4]{path}:
src/main/java/com/example/auth/JwtService.java
src/main/java/com/example/auth/TokenValidator.java
src/main/java/com/example/auth/RefreshTokenService.java
pom.xml

artifacts:
  module: auth-service
  changes: 287

context:
  language: java
  build_tool: maven
  module: auth-service
  max_fix_iterations: 3

next_action: Execute Maven build
next_focus: clean verify
```

**Tool Invocation**:
```markdown
Task:
  subagent_type: cui-task-workflow:build-verify-agent
  description: Verify build
  prompt: |
    {TOON handoff above}
```

#### Component: `build-verify-agent`

**File**: `cui-task-workflow/agents/build-verify-agent.md`

**Step 0: Process Handoff Input**
```
Parse incoming handoff:
  - language: java
  - build_tool: maven
  - module: auth-service
  - files: [JwtService.java, ...]
```

**Step 1: Detect Build Tool**
```
language=java + pom.xml → build_tool=maven
```

**Step 2: Delegate to Maven Build**

**Generated TOON Handoff to builder-maven-rules skill**:
```toon
from: build-verify-agent
to: builder-maven-rules-skill
handoff_id: handoff-007
workflow: maven-build
timestamp: 2025-11-26T10:06:00Z

task:
  description: Execute Maven build for auth-service
  type: build
  status: pending

artifacts:
  module: auth-service

context:
  goals: clean verify
  module: auth-service
  output_mode: errors

next_action: Run Maven build
next_focus: Compilation and tests
```

**Tool Invocation**:
```markdown
Skill: builder:builder-maven-rules
Workflow: Execute Build
Input: {TOON handoff above}
```

#### Component: `builder-maven-rules` skill

**File**: `builder-maven/skills/builder-maven-rules/SKILL.md`

**Step 0: Process Handoff Input**
```
Parse incoming handoff:
  - goals: clean verify
  - module: auth-service
  - output_mode: errors
```

**Step 1: Execute Maven Build**

**Step 2: Execute Maven Command**
```bash
./mvnw -pl auth-service clean verify
```

**Step 3: Monitor and Parse Output**

**Result**: ❌ BUILD FAILURE

```
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.11.0:compile
[ERROR] /src/main/java/com/example/auth/JwtService.java:[23,8] cannot find symbol
[ERROR]   symbol:   class Algorithm
[ERROR]   location: class com.example.auth.JwtService
```

**Step 4: Generate Error Handoff**

**Response from builder-maven-rules**:
```toon
from: builder-maven-rules-skill
to: build-verify-agent
handoff_id: handoff-008
workflow: maven-build

task:
  description: Maven build failed
  type: build
  status: failed

errors[1]{file,line,column,message,type}:
src/main/java/com/example/auth/JwtService.java,23,8,cannot find symbol: class Algorithm,compilation

context:
  exit_code: 1
  error_count: 1
  warning_count: 0

next_action: Fix compilation errors
next_focus: Missing import for Algorithm
```

**Step 2: Return to build-verify-agent**

#### Component: `build-verify-agent` (continued)

**Step 3: Check Build Status**
```
Status: FAILED
Error count: 1
Type: compilation
```

**Step 4: Delegate to Fix Agent (Iteration 1)**

**Generated TOON Handoff to java-fix-build-agent**:
```toon
from: build-verify-agent
to: java-fix-build-agent
handoff_id: handoff-009
workflow: build-fix
iteration: 1
timestamp: 2025-11-26T10:07:00Z

task:
  description: Fix Maven compilation errors
  type: fix
  status: pending

errors[1]{file,line,column,message}:
src/main/java/com/example/auth/JwtService.java,23,8,cannot find symbol: class Algorithm

context:
  language: java
  build_tool: maven
  module: auth-service
  max_iterations: 3
  current_iteration: 1

next_action: Fix compilation errors
next_focus: Add missing import for Algorithm
```

**Tool Invocation**:
```markdown
Task:
  subagent_type: cui-java-expert:java-fix-build-agent
  description: Fix compilation errors
  prompt: |
    {TOON handoff above}
```

#### Component: `java-fix-build-agent`

**File**: `cui-java-expert/agents/java-fix-build-agent.md`

**Step 0: Process Handoff Input**
```
Parse incoming handoff:
  - errors: [cannot find symbol: class Algorithm]
  - iteration: 1
  - max_iterations: 3
```

**Step 1: Delegate to cui-java-core Skill**

**Tool Invocation**:
```markdown
Skill: cui-java-expert:cui-java-core
Workflow: Fix Compilation Errors
Input: {handoff}
```

**cui-java-core Actions**:
1. Read JwtService.java:23
2. Identify missing import: `io.jsonwebtoken.SignatureAlgorithm`
3. Edit JwtService.java: Add import
4. Verify fix

**Response**:
```toon
from: cui-java-core-skill
to: java-fix-build-agent
handoff_id: handoff-010
workflow: build-fix

task:
  description: Compilation error fixed
  type: fix
  status: completed

files[1]{path}:
src/main/java/com/example/auth/JwtService.java

artifacts:
  fixes_applied: 1

changes[1]:
- Added import io.jsonwebtoken.SignatureAlgorithm

next_action: Retry build
next_focus: Verify compilation succeeds
```

**Step 2: Return to build-verify-agent**

#### Component: `build-verify-agent` (continued)

**Step 5: Loop Back to Build (Iteration 2)**

Delegate to builder-maven-rules skill again with updated code.

**Tool Invocation**:
```markdown
Skill: builder:builder-maven-rules
Workflow: Execute Build
Input: {handoff with module=auth-service}
```

**Result**: ✅ BUILD SUCCESS

```
[INFO] BUILD SUCCESS
[INFO] Total time:  1.234 s
```

**Final TOON Handoff from builder-maven-rules**:
```toon
from: builder-maven-rules-skill
to: build-verify-agent
handoff_id: handoff-011
workflow: maven-build

task:
  description: Maven build successful
  type: build
  status: completed

test_results:
  total: 0
  passed: 0
  failed: 0

context:
  exit_code: 0
  build_time_ms: 1234

next_action: Commit changes
next_focus: Feature complete and verified
```

**Step 6: Return Final Handoff to Command**

**Generated TOON Handoff**:
```toon
from: build-verify-agent
to: task-implement-command
handoff_id: handoff-012
workflow: build-verification
timestamp: 2025-11-26T10:08:30Z

task:
  description: Build verification complete
  type: verify
  status: completed
  progress: 100%

artifacts:
  build_status: SUCCESS
  fix_iterations: 1
  total_time_ms: 2500

context:
  build_tool: maven
  module: auth-service

next_action: Commit and complete task
next_focus: Git commit workflow
```

---

### PHASE 5: COMMIT AND COMPLETION

#### Component: `/task-implement` command (final steps)

**Step 6: Commit Changes**

**Generated TOON Handoff to git-workflow skill**:
```toon
from: task-implement-command
to: git-workflow-skill
handoff_id: handoff-013
workflow: git-commit
timestamp: 2025-11-26T10:08:45Z

task:
  description: Commit JWT authentication implementation
  type: commit
  status: pending

files[5]{path}:
src/main/java/com/example/auth/JwtService.java
src/main/java/com/example/auth/TokenValidator.java
src/main/java/com/example/auth/RefreshTokenService.java
pom.xml
src/main/resources/application.properties

artifacts:
  summary: Implement JWT authentication service

details[5]:
- Add JwtService with token generation and validation
- Add TokenValidator with expiry checking
- Add RefreshTokenService with token rotation
- Add JJWT dependency to pom.xml
- Add JWT configuration to application.properties

context:
  module: auth-service
  commit_type: feat

next_action: Generate commit and execute
next_focus: Conventional commit format
```

**Tool Invocation**:
```markdown
Skill: cui-task-workflow:git-workflow
Workflow: Commit
Input: {TOON handoff above}
```

**git-workflow Actions**:
1. Run: `git status`
2. Stage files: `git add src/ pom.xml`
3. Generate commit message via script
4. Commit: `git commit -m "..."`

**Generated Commit Message**:
```
feat(auth): implement JWT authentication service

- Add JwtService with token generation and validation
- Add TokenValidator with expiry checking
- Add RefreshTokenService with token rotation
- Add JJWT dependency to pom.xml
- Configure JWT secrets in application.properties

🤖 Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Response**:
```toon
from: git-workflow-skill
to: task-implement-command
handoff_id: handoff-014
workflow: git-commit

task:
  description: Git commit successful
  type: commit
  status: completed

artifacts:
  commit_hash: abc123def456
  files_committed: 5
  commit_message: feat(auth): implement JWT authentication service

next_action: Task complete
```

**Step 7: Cleanup and Return Final Handoff**

**Persist to Memory**:
```bash
python3 manage-memory.py save \
  --category handoffs \
  --identifier "workflow-task-001-complete" \
  --content '{final handoff JSON}'
```

**Command Prepares Final Result**:
```toon
workflow: task-implementation
timestamp: 2025-11-26T10:09:30Z
status: completed

task:
  description: Implement JWT authentication service with token validation and refresh
  type: implement
  status: completed
  progress: 100%

files[5]{path}:
src/main/java/com/example/auth/JwtService.java
src/main/java/com/example/auth/TokenValidator.java
src/main/java/com/example/auth/RefreshTokenService.java
pom.xml
src/main/resources/application.properties

artifacts:
  plan_file: .claude/plans/plan-jwt-auth.md
  tasks_completed: 4
  commit_hash: abc123def456

interfaces[3]{class,methods}:
JwtService,generateToken(), validateToken(), refreshToken()
TokenValidator,validate(), isExpired()
RefreshTokenService,create(), rotate(), validate()

decisions[6]:
- Use JJWT library (io.jsonwebtoken:jjwt-api)
- HS256 algorithm for signing
- 24-hour access token expiry
- 7-day refresh token expiry
- Lombok @Service for CDI
- Log all token operations

context:
  language: java
  module: auth-service
  build_status: SUCCESS
  fix_iterations: 1
  total_duration_ms: 570000

next_alternatives[2]:
- Push to remote
- Create PR

memory:
  category: handoffs
  identifier: workflow-task-001-complete
  persist: true
```

---

### PHASE 6: USER RESULT

#### Component: `/task-implement` command (final formatting)

**Format user-friendly output**:

```
╔═══════════════════════════════════════════════════════╗
║     Task Implementation Complete                       ║
╚═══════════════════════════════════════════════════════╝

Task: Implement JWT authentication service with token validation and refresh
Status: ✅ COMPLETED
Duration: 9.5 minutes

PLAN:
  Plan file: .claude/plans/plan-jwt-auth.md
  Tasks: 4 completed

IMPLEMENTATION:
  Language: Java
  Module: auth-service
  Files created: 3
    - JwtService.java
    - TokenValidator.java
    - RefreshTokenService.java
  Files modified: 2
    - pom.xml
    - application.properties

BUILD:
  Status: SUCCESS
  Fix iterations: 1
  Issue fixed: Missing import for Algorithm

COMMIT:
  Hash: abc123def456
  Message: feat(auth): implement JWT authentication service

NEXT STEPS:
  - Review the implementation
  - Add unit tests with /java-implement-tests
  - Push to remote: git push
  - Create PR: /pr-create
```

---

## Handoff Chain Summary

Complete TOON handoff chain for this workflow:

```
1.  task-implement-command → task-plan-skill              [handoff-001]
2.  task-plan-skill        → task-implement-command       [handoff-002]
3.  task-implement-command → java-implement-agent         [handoff-003]
4.  java-implement-agent   → cui-java-core-skill          [handoff-004]
5.  cui-java-core-skill    → java-implement-agent         [handoff-005]
6.  task-implement-command → build-verify-agent           [handoff-006]
7.  build-verify-agent     → builder-maven-rules-skill        [handoff-007]
8.  builder-maven-rules-skill  → build-verify-agent           [handoff-008: FAILED]
9.  build-verify-agent     → java-fix-build-agent         [handoff-009]
10. java-fix-build-agent   → cui-java-core-skill          [handoff-010]
11. build-verify-agent     → builder-maven-rules-skill        [handoff-007 retry]
12. builder-maven-rules-skill  → build-verify-agent           [handoff-011: SUCCESS]
13. build-verify-agent     → task-implement-command       [handoff-012]
14. task-implement-command → git-workflow-skill           [handoff-013]
15. git-workflow-skill     → task-implement-command       [handoff-014]
```

**Total Handoffs**: 15 (reduced from 17 via direct command orchestration)
**Components Involved**: 7 (1 command, 3 agents, 3 skills)
**Bundles Involved**: 3 (cui-task-workflow, cui-java-expert, builder-maven)
**Format**: TOON (30-60% token reduction vs JSON)

---

## Key Observations

### Context Isolation
- Each agent spawns in isolated context
- Skills load in agent context
- Context released after completion
- No cross-contamination

### State Preservation
- Every handoff preserves full context
- Artifacts accumulated through chain
- Decisions preserved and propagated
- Memory integration for recovery

### Error Handling
- Build failure detected in handoff
- Fix iteration via handoff chain
- Retry with updated code
- Success propagated back through chain

### Generic Pattern Adherence
- Pattern 1: Task Implementation Workflow ✅
- Pattern 3: Build Verification Workflow ✅
- Pattern 7: Language Implementation Workflow ✅
- Pattern 9: Language Fix Workflow ✅

### Communication Consistency
- All inter-component: Via TOON handoff ✅
- No direct Skill calls across bundles ✅
- No direct SlashCommand calls ✅
- TOON format throughout (30-60% token savings) ✅
- Command orchestrates directly (no wrapper agent) ✅

---

## Complete Handoff Data Flow

```
USER INPUT → /task-implement
    │
    ├─> PLANNING (Command → Skill)
    │   └─> [handoff-001 TOON] task="Implement JWT...", mode=PLAN
    │       └─> task-plan-skill creates .claude/plans/plan-jwt-auth.md
    │           └─> [handoff-002 TOON] tasks[4], decisions[4]
    │
    ├─> LANGUAGE DETECTION (Command logic)
    │   └─> language=java, module=auth-service
    │
    ├─> IMPLEMENTATION (Command → Agent → Skill)
    │   └─> [handoff-003 TOON] to java-implement-agent
    │       └─> [handoff-004 TOON] to cui-java-core-skill
    │           └─> Implements 3 classes, updates pom.xml
    │               └─> [handoff-005 TOON] files[5], interfaces[3], status=SUCCESS
    │
    ├─> VERIFICATION (Command → Agent → Skill)
    │   └─> [handoff-006 TOON] to build-verify-agent
    │       └─> [handoff-007 TOON] to builder-maven-rules-skill
    │           └─> Maven build executes
    │               ├─> [handoff-008 TOON] status=FAILED, errors[1]
    │               │   └─> FIX ITERATION
    │               │       └─> [handoff-009 TOON] to java-fix-build-agent
    │               │           └─> [handoff-010 TOON] fixed import
    │               │               └─> Retry build
    │               │                   └─> [handoff-011 TOON] status=SUCCESS
    │               └─> [handoff-012 TOON] verification complete
    │
    ├─> COMMIT (Command → Skill)
    │   └─> [handoff-013 TOON] to git-workflow-skill
    │       └─> Git commit executes
    │           └─> [handoff-014 TOON] commit_hash=abc123
    │
    └─> USER RESULT
        └─> Format completion message with all artifacts
```

**Key Changes from Original Architecture**:
- ❌ Removed: task-implement-agent (unnecessary wrapper)
- ✅ Command orchestrates directly (~120 lines)
- ✅ TOON format (30-60% token reduction)
- ✅ 15 handoffs (down from 17)

---

## Implementation Checklist

For implementing this specific workflow in the codebase:

### cui-task-workflow Changes
- [ ] Update `/task-implement` command to orchestrate directly (~120 lines)
- [ ] Generate TOON handoffs to skills and agents
- [ ] Update `task-plan` skill to accept/return TOON handoffs (see [06-plan-management-specification/api.md](06-plan-management-specification/api.md))
- [ ] Create `build-verify-agent.md` (80 lines)
- [ ] Update `git-workflow` skill to accept/return TOON handoffs
- [ ] Replace all JSON handoff templates with TOON format

### cui-java-expert Changes
- [ ] Update `java-implement-agent.md` to process TOON handoff input (Step 0)
- [ ] Update `java-implement-agent.md` to generate TOON handoff output (Final Step)
- [ ] Update `cui-java-core` skill to accept/return TOON handoffs
- [ ] Update `java-fix-build-agent.md` for TOON handoff I/O
- [ ] Update `cui-java-core` Fix Compilation workflow for TOON handoffs

### builder-maven Changes
- [ ] Update `builder-maven-rules` skill to accept TOON handoff input (Step 0)
- [ ] Update `builder-maven-rules` skill to return TOON handoff output (Final Step)
- [ ] Add TOON handoff templates for build results
- [ ] Add TOON handoff templates for error details
- [ ] Support both TOON handoff and traditional parameter modes

### Testing
- [ ] Test TOON handoff chain with simple task
- [ ] Test TOON handoff chain with build failure
- [ ] Test TOON handoff chain with multiple fix iterations
- [ ] Test memory persistence at each stage
- [ ] Test recovery from interrupted workflow
- [ ] Verify 30-60% token reduction with TOON format

---

## Conclusion

This specific workflow demonstrates:

✅ **TOON handoff-based communication** - 15 handoffs (30-60% token savings vs JSON)
✅ **Direct command orchestration** - No unnecessary wrapper agents
✅ **Context preservation** - Full state maintained through TOON chain
✅ **Error handling** - Build failure → Fix → Retry → Success
✅ **Generic patterns** - Reusable across languages
✅ **Integration** - cui-task-workflow orchestrates language bundles
✅ **Memory integration** - TOON handoffs persisted for recovery
✅ **Clean architecture** - Minimal wrappers (~120 line command), skills hold logic

**Key Architecture Improvements**:
- Command orchestrates directly (removed task-implement-agent)
- TOON format throughout (significant token reduction)
- 15 handoffs (down from 17 in original design)
- 7 components (down from 9 in original design)

**This serves as the reference implementation** for all future language-specific workflows.
