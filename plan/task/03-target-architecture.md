# Target Architecture: Integrated Task Workflow with Handoff-Based Communication

## Executive Summary

Transform the current architecture from:
```
Command → Skill (direct)  OR  Command → Agent → Skill (direct)
```

To:
```
Command → [HANDOFF] → Skill/Agent → [HANDOFF] → Back to Command
```

**Key Architectural Decision**:
**Commands orchestrate workflows directly** (~120 lines). Context isolation happens at the **language-specific agent level** (java-implement-agent, js-implement-agent), NOT at the task-workflow level. This eliminates unnecessary wrapper agents (task-implement-agent, pr-fix-agent) while maintaining context isolation where it matters.

**Key Principles**:
1. **cui-task-workflow** = Main control/orchestration (commands orchestrate directly)
2. **Handoff Protocol** = Primary communication mechanism
3. **Commands** = ~120 lines (orchestrate workflows directly)
4. **Language Agents** = Context isolation happens here (java-implement-agent)
5. **Skills Hold Logic** = All business logic in skills

**Current State Analysis**: See [01-current-cui-task-workflow-analysis.md](01-current-cui-task-workflow-analysis.md) and [02-current-cui-java-expert-analysis.md](02-current-cui-java-expert-analysis.md) for detailed analysis of current architecture and identified issues.

## Target Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     CUI-TASK-WORKFLOW                            │
│                  (Main Control & Orchestration)                  │
│                                                                   │
│  Commands (orchestrate workflows directly):                     │
│  ┌─────────────────────┐  ┌──────────────────────┐            │
│  │ /task-implement     │  │ /pr-fix              │            │
│  │ (~120 lines)        │  │ (~120 lines)         │            │
│  │                     │  │                      │            │
│  │ Orchestrates:       │  │ Orchestrates:        │            │
│  │ • task-plan skill   │  │ • pr-workflow skill  │            │
│  │ • {lang}-agents     │  │ • sonar-workflow     │            │
│  │ • build-verify-agent│  │ • build-verify-agent │            │
│  │ • git-workflow skill│  │ • git-workflow skill │            │
│  └──────────┬──────────┘  └──────────┬───────────┘            │
│             │                          │                         │
└─────────────┼──────────────────────────┼─────────────────────────┘
              │                          │
              │ [HANDOFF]                │ [HANDOFF]
              ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              LANGUAGE-SPECIFIC BUNDLES                           │
│          (Invoked via Handoff from Task-Workflow)               │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              CUI-JAVA-EXPERT                            │    │
│  │                                                          │    │
│  │  Agents (invoked via handoff):                         │    │
│  │  ┌──────────────────────┐  ┌─────────────────────┐    │    │
│  │  │ java-implement-agent │  │ java-verify-agent   │    │    │
│  │  │ (70 lines)           │  │ (50 lines)          │    │    │
│  │  └──────────┬───────────┘  └──────────┬──────────┘    │    │
│  │             │ [HANDOFF]                 │ [HANDOFF]    │    │
│  │             ▼                           ▼               │    │
│  │  ┌──────────────────────┐  ┌─────────────────────┐    │    │
│  │  │ cui-java-core skill  │  │ cui-java-unit-      │    │    │
│  │  │ (600 lines)          │  │ testing skill       │    │    │
│  │  └──────────────────────┘  └─────────────────────┘    │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │           CUI-FRONTEND-EXPERT (Future)                  │    │
│  │                                                          │    │
│  │  Agents (invoked via handoff):                         │    │
│  │  ┌───────────────────┐  ┌────────────────────┐        │    │
│  │  │ js-implement-agent│  │ js-verify-agent    │        │    │
│  │  └───────────────────┘  └────────────────────┘        │    │
│  └────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
              │
              │ [HANDOFF]
              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CUI-MAVEN                                     │
│              (Build & Verification via Handoff)                  │
│                                                                   │
│  Skill (invoked via handoff):                                   │
│  ┌──────────────────────┐                                       │
│  │ builder-maven-rules skill│                                       │
│  │ (500 lines)          │                                       │
│  │ - Handoff-enabled    │                                       │
│  │ - Execute Build      │                                       │
│  │ - Parse Errors       │                                       │
│  └──────────────────────┘                                       │
│                                                                   │
│  No agents needed - build-verify-agent provides context         │
└─────────────────────────────────────────────────────────────────┘
```

## Core Architectural Principles

### 1. Main Control with cui-task-workflow

**cui-task-workflow** is the primary orchestration layer:
- Entry point for all task implementation
- Coordinates language-specific bundles
- Manages workflow state via handoffs
- Handles memory persistence
- Provides generic workflow patterns

**Responsibilities**:
- Task planning (review, plan, execute)
- Language detection and routing
- Build verification coordination
- PR management
- Git workflow management

### 2. Handoff-Based Communication

**All inter-component communication via TOON handoff protocol**:

```toon
from_agent: source-component
to_agent: target-component
timestamp: 2025-11-26T10:00:00Z

task:
  description: Implement JWT authentication
  status: completed
  progress: 100%

artifacts[3]{type,name}:
files,AuthService.java
files,TokenValidator.java
decisions,Use JJWT library with HS256

context:
  dependencies: io.jsonwebtoken:jjwt-api
  constraints: Must follow CUI Java standards
  notes: Implemented with Lombok

next_action: Verify build compiles
next_focus: Run Maven clean verify
```

**Format**: TOON (30-60% token reduction vs JSON) - See `cui-utilities:toon-usage` skill

**Benefits**:
- Structured state transfer
- Context preservation
- Clear boundaries
- Traceable workflow
- Memory integration

### 3. Plan Files as Persistent Artifacts

**Plan files remain as persistent Markdown artifacts in `.claude/plans/`, NOT handoff content**:

**Why Plan Files are Artifacts**:
- ✅ **Human-readable** - Markdown format can be reviewed and edited manually
- ✅ **Persistent** - Survive session boundaries, stored in `.claude/plans/`
- ✅ **Efficient handoffs** - Don't duplicate entire plan in every handoff
- ✅ **Standard artifact pattern** - Like code files, configs, documentation
- ✅ **Tool-friendly** - Can be tracked in git, read by editors, versioned
- ✅ **Iterative** - Can be refined using `/task-plan` command with `plan=` parameter

**How Handoffs Reference Plan Files**:
```toon
from_agent: task-plan-skill
to_agent: task-implement-command

artifacts:
  plan_file: .claude/plans/plan-jwt-auth.md
  total_tasks: 4

context:
  plan_file: .claude/plans/plan-jwt-auth.md

tasks[1]{id,name,acceptance}:
1,Create JwtService,Interface defines generateToken/validateToken/refreshToken methods
```

**Pattern**:
1. Plan file created by `/task-plan` command (delegates to `task-plan` skill)
2. `task-plan` skill writes Markdown to `.claude/plans/`
3. Plan file referenced in handoffs (not embedded)
4. Skills read plan files when needed (not commands/agents directly)
5. Plan can be manually edited or refined with `/task-plan plan=...`

**Skill Abstraction** (similar to `adr-management` pattern):
- ✅ All plan file operations through `task-plan` skill
- ✅ Skill encapsulates file I/O (Read, Write, Edit)
- ✅ Implementation details hidden from callers
- ✅ Location (`.claude/plans/`) can change without breaking callers
- ✅ Format (Markdown) can evolve without breaking callers
- ✅ Additional features (validation, templates) added to skill only

**Example Abstraction**:
```
Command → Skill (plan operations) → File System
NOT: Command → File System directly
```

**Similar Patterns in Codebase**:
- `adr-management`: ADR file operations abstracted through skill
- `interface-management`: Interface spec operations abstracted through skill
- `task-plan`: Plan file operations abstracted through skill ← THIS PATTERN

**Analogy**: Just as code files are artifacts that handoffs reference (not embed), plan files are Markdown artifacts that handoffs reference (not replace). And just as ADR management is abstracted through `adr-management` skill, plan management is abstracted through `task-plan` skill.

### 4. Minimal Wrappers

**Commands** (< 50 lines):
- Parameter parsing
- Mode determination
- Agent delegation via handoff

**Agents** (< 150 lines):
- Handoff processing
- Skill invocation
- Result formatting
- Handoff generation

**Skills** (400-800 lines):
- Business logic
- Standards knowledge
- Workflows
- Verification logic

### 5. Context Isolation via Agents

**Agents provide context isolation**:
- Each agent spawns in separate context
- Skills load in agent context
- Context released after completion
- No cross-contamination

### 6. Skills Hold All Logic

**Skills are single source of truth**:
- All standards
- All implementation patterns
- All verification rules
- All workflows

## Detailed Component Architecture

### cui-task-workflow Bundle Structure

```
cui-task-workflow/
├── commands/                           # 3 commands
│   ├── task-plan.md                    # PLAN goal (~80 lines)
│   ├── task-implement.md               # IMPLEMENT goal (~120 lines)
│   └── pr-fix.md                       # FIX goal (~120 lines)
├── agents/                             # 1 agent (~80 lines)
│   └── build-verify-agent.md           # Build verification coordination
└── skills/                             # 7 skills
    ├── workflow-patterns/              # Handoff protocols (reference)
    ├── task-review/                    # Review workflow (150 lines)
    ├── task-plan/                      # Plan workflow (200 lines)
    ├── task-execute/                   # Execute workflow (150 lines)
    ├── git-workflow/                   # Git commit workflows
    ├── pr-workflow/                    # PR handling
    └── sonar-workflow/                 # Sonar issue fixing
```

#### Commands

##### /task-plan (~80 lines)
```markdown
---
name: task-plan
description: Create or refine Markdown plan document for task implementation
tools: Glob, Read, Write, Edit, Skill
model: sonnet
---

# Task Planning Command

## PURPOSE
Iteratively create and refine structured Markdown plan documents in `.claude/plans/`
that can be used as input for `/task-implement`.

## PARAMETERS
- task (required): Issue number/URL or task description
- plan (optional): Path to existing plan file to refine
- output (optional): Output path (default: .claude/plans/plan-{task-id}.md)

## WORKFLOW - Orchestrates directly via handoffs

### Step 1: Parse Parameters (10 lines)
Validate inputs, determine if creating new plan or refining existing

### Step 2: Review Task (if new plan) (15 lines)
Skill: task-review
Input: [handoff with task description]
Output: [handoff with readiness assessment and issues]

### Step 3: Generate/Refine Plan (30 lines)
Skill: task-plan
Input: [handoff with task description or existing plan path]
Output: [handoff with plan file reference]

Plan file structure (Markdown):
- Task overview and acceptance criteria
- Technical approach and decisions
- Task breakdown with checkboxes
- Dependencies and constraints
- Risk assessment

### Step 4: Write Plan File (15 lines)
Write Markdown to .claude/plans/ directory
Format: Structured, human-readable, git-friendly

### Step 5: Return Results (10 lines)
Display plan location and summary
Suggest next step: /task-implement plan="{plan_file}"
```

##### /task-implement (~120 lines)
```markdown
---
name: task-implement
description: Implement tasks from plan files or task descriptions
tools: Glob, Read, Skill, Task
model: sonnet
---

# Task Implementation Command

## PARAMETERS
- plan (optional): Path to Markdown plan file (e.g., .claude/plans/plan-auth.md)
- task (optional): Task description (will create inline plan if no plan file)
- language (optional): Auto-detects if not specified
- push (optional): Auto-push after success

Note: Either 'plan' or 'task' must be provided

## WORKFLOW - Orchestrates directly via handoffs

### Step 1: Parse Parameters & Load Plan (20 lines)
If plan file provided:
  - Read Markdown plan file
  - Extract task breakdown and decisions
Else:
  - Create inline plan from task description
  - Delegate to task-plan skill

### Step 2: Detect Language (15 lines)
Glob: **/pom.xml → java
Glob: **/package.json → javascript
Update context with detected language

### Step 3: Delegate to Language Agent (25 lines)
Task: {language}-implement-agent
Input: [handoff with plan and context]
Output: [handoff with implementation artifacts]
NOTE: Context isolation happens HERE in language-specific agent

### Step 4: Verify Build (25 lines)
Task: build-verify-agent
Input: [handoff with artifacts]
Output: [handoff with build status]

### Step 5: Commit Changes (20 lines)
Skill: git-workflow
Workflow: Commit
Input: [handoff with all artifacts]

### Step 6: Return Results (15 lines)
Format workflow summary for user
```

##### /pr-fix (~120 lines)
```markdown
Similar orchestration pattern:
1. Parse PR number
2. Determine checks to run (build, reviews, sonar)
3. Delegate to pr-workflow, sonar-workflow skills
4. Coordinate build-verify-agent if needed
5. Return synthesis of all fixes
```

#### Agents

##### build-verify-agent (80 lines)
```markdown
---
name: build-verify-agent
description: Coordinate build verification via language-specific tools
tools: Glob, Read, Skill
model: sonnet
---

# Build Verify Agent

## Workflow

### Step 1: Process Handoff Input (15 lines)
Parse artifacts, determine language/build tool

### Step 2: Delegate to Build Tool (30 lines)
[HANDOFF] → maven-build-agent (for Java)
[HANDOFF] → npm-build-agent (for JavaScript)

### Step 3: Handle Failures (20 lines)
If build fails:
  [HANDOFF] → {language}-fix-build-agent
  Iterate up to 3 times

### Step 4: Return Results (15 lines)
Generate handoff with build status
```

NOTE: build-verify-agent is the only agent in cui-task-workflow.
All orchestration happens in commands directly.

#### Skills

##### task-review (150 lines)
```markdown
---
name: task-review
description: Review tasks for implementation readiness
allowed-tools: Read, Edit, AskUserQuestion, Bash(gh:*)
---

# Task Review Skill

## Workflow: Review Task

### Input
Handoff with task reference (issue number/file)

### Process
1. Load task content
2. Analyze completeness/correctness/clarity
3. Identify gaps
4. Update documentation
5. Verify 6 quality criteria

### Output
Handoff with:
- Review status
- Issues found
- Changes made
- Next action (plan/execute)
```

##### task-plan (200 lines)
```markdown
---
name: task-plan
description: Create task breakdowns and implementation plans in Markdown format
allowed-tools: Read, Write, Edit, Bash(gh:*), Skill
---

# Task Plan Skill

**Full Specification**: See [06-plan-management-specification](06-plan-management-specification/) for complete API, abstraction pattern, and file format standards ([API](06-plan-management-specification/api.md)).

## Workflow: Plan Task

### Input
Handoff with task description or existing plan path to refine

### Process
1. Analyze task requirements
2. Generate structured breakdown
3. **Write plan file to disk** in Markdown format
   - Location: `.claude/plans/plan-{task-id}.md`
   - Uses Write tool to create Markdown file
   - Structure:
     * Task overview and acceptance criteria
     * Technical approach and architectural decisions
     * Task breakdown with checkboxes `* [ ] Task item`
     * Dependencies and constraints
     * Risk assessment
   - Human-readable, git-friendly, manually editable
   - Persists on filesystem for later reading by /task-implement
4. Identify dependencies and risks

### Output
Handoff with:
- **Plan file location** (`artifacts.plan_file: .claude/plans/plan-xyz.md`)
- Task breakdown summary (count, key decisions)
- Dependencies
- Next action: "/task-implement plan=.claude/plans/plan-xyz.md"

**Note**: Plan file is a persistent Markdown artifact on disk at .claude/plans/, handoff only references it
```

##### task-execute (150 lines)
```markdown
---
name: task-execute
description: Execute tasks from plan files
allowed-tools: Read, Edit, Write, Skill
---

# Task Execute Skill

## Workflow: Execute Task

### Input
Handoff with plan file reference and task ID

### Process
1. **Read plan file from disk** (using Read tool on `context.plan_file`)
   - Skill abstracts file access
   - Location details hidden from caller
2. Parse markdown structure (tasks, acceptance criteria)
3. Identify target task by ID
4. Read code references
5. Execute checklist items
6. Verify acceptance criteria
7. Update progress (via Edit tool - abstracted)

### Output
Handoff with:
- Task completion status
- Files modified
- Acceptance verification
- Next action (next task/complete)

**Abstraction**: All plan file operations through skill - callers don't know location/format
```

### cui-java-expert Bundle Structure

```
cui-java-expert/
├── agents/                             # 11 agents (70 lines avg)
│   ├── java-implement-agent.md         # Feature implementation
│   ├── java-implement-tests-agent.md   # Test implementation
│   ├── java-fix-build-agent.md         # Fix compilation
│   ├── java-fix-tests-agent.md         # Fix test failures
│   ├── java-fix-javadoc-agent.md       # Fix JavaDoc
│   ├── java-refactor-agent.md          # Refactoring
│   ├── java-coverage-agent.md          # Coverage analysis
│   ├── java-quality-agent.md           # Quality analysis
│   ├── java-verify-agent.md            # Verification
│   ├── java-workflow-orchestrator.md   # Workflow coordination (NEW)
│   └── java-build-verify-agent.md      # Build verification (NEW)
├── commands/                           # 3 commands (simplified)
│   ├── java-analyze.md                 # Analysis only
│   ├── java-create.md                  # Interactive wizard
│   └── java-maintain.md                # Maintenance workflows
└── skills/                             # 5 skills (handoff-enabled)
    ├── cui-java-core/                  # Core Java + handoff I/O
    ├── cui-java-unit-testing/          # Testing + handoff I/O
    ├── cui-javadoc/                    # JavaDoc + handoff I/O
    ├── cui-java-cdi/                   # CDI/Quarkus (reference)
    └── cui-java-maintenance/           # Maintenance (reference)
```

#### Key Changes

1. **Remove /java-full-workflow** ❌
   - Replaced by cui-task-workflow/task-implement
   - Orchestration moves to cui-task-workflow

2. **Add Handoff Support to All Agents** ✅
   - Accept handoff input (Step 0)
   - Generate handoff output (Final Step)

3. **Enable Skills for Handoff I/O** ✅
   - Accept handoff parameters
   - Return handoff results
   - Support chaining

4. **Add java-workflow-orchestrator** ✅
   - Internal Java workflow coordination
   - Called by /task-implement command via handoff

5. **Add java-build-verify-agent** ✅
   - Specialized build verification
   - Maven integration via handoff

### builder-maven Bundle Structure

```
builder-maven/
└── skills/
    └── builder-maven-rules/                # Maven skill (handoff-enabled)
        ├── SKILL.md                    # Updated with handoff I/O
        └── workflows/
            ├── Execute Build           # Handoff-enabled
            └── Parse Build Output      # Handoff-enabled
```

#### Key Changes

1. **No Agents Needed** ✅
   - build-verify-agent (cui-task-workflow) provides context isolation
   - Direct skill invocation with handoff
   - Simpler architecture

**Design Rationale**: Skills can be handoff-enabled directly without agent wrappers when:
- The calling agent already provides context isolation
- No complex orchestration is needed (single skill invocation)
- No pre-processing or transformation required
- Result: 130 lines of code eliminated (agent wrappers not needed)

2. **Remove Direct Command Calls** ❌
   - No more `/maven-build-and-fix` direct calls
   - All via handoff protocol

3. **Enable Handoff I/O in Skill** ✅
   - builder-maven-rules accepts handoff input (Step 0)
   - Returns structured handoff output (Final Step)
   - Support for both handoff and traditional parameters

## Communication Flow: Complete Example

### User Request: "Implement authentication feature"

#### Phase 1: Planning (Optional - User runs /task-plan first)

```
┌──────────────────────────────────────────────────────────────┐
│ User invokes /task-plan command                              │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
/task-plan task="Implement authentication feature"
│
├─> Step 1: Review task
│   Skill: task-review
│   Input: [handoff with task description]
│
├─> Step 2: Generate plan
│   Skill: task-plan
│   Input: [handoff with reviewed task]
│   │
│   └─> Creates: .claude/plans/plan-auth-feature.md
│       Structure:
│       * Task overview and acceptance criteria
│       * Technical approach and decisions
│       * [ ] Task 1: Create JwtService interface
│       * [ ] Task 2: Implement TokenValidator
│       * [ ] Task 3: Configure JWT secrets
│       * Dependencies and constraints
│
└─> Returns: Plan location and suggests next step
    "Created plan: .claude/plans/plan-auth-feature.md"
    "Next: /task-implement plan=.claude/plans/plan-auth-feature.md"
```

#### Phase 2: Implementation (User runs /task-implement with plan)

```
┌──────────────────────────────────────────────────────────────┐
│ User invokes /task-implement command                         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
/task-implement plan=".claude/plans/plan-auth-feature.md"
│
├─> Step 1: Load plan from Markdown file
│   Read: .claude/plans/plan-auth-feature.md
│   Parse: Extract tasks, decisions, acceptance criteria
│
├─> Step 2: Detect language (command continues)
│   Glob: pom.xml → language=java
│
├─> Step 3: Delegate to Java implementation (command continues)
│   │
│   └─> Generate Handoff:
│       ```toon
│       from: task-implement-command
│       to: java-implement-agent
│
│       task:
│         description: Implement authentication feature
│         plan_file: .claude/plans/plan-auth-feature.md
│
│       context:
│         language: java
│         dependencies: [...]
│         constraints: [...]
│
│       next_action: Implement feature in Java
│       ```
│       │
│       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 3: java-implement-agent receives handoff                │
│         (CONTEXT ISOLATION HAPPENS HERE)                      │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
Task: cui-java-expert:java-implement-agent
  Prompt: [TOON handoff]
│
├─> Step 3a: Process handoff (agent in isolated context)
│   Extract task, plan_file, context
│   Read plan from: .claude/plans/plan-auth-feature.md
│
├─> Step 3b: Implement feature
│   │
│   └─> Generate Handoff:
│       ```toon
│       from: java-implement-agent
│       to: cui-java-core-skill
│
│       task: {...}
│       context: {...}
│       ```
│       │
│       ▼
│   Skill: cui-java-expert:cui-java-core
│     Workflow: Implement Feature
│     Input: [TOON handoff]
│     │
│     ├─> Read standards
│     ├─> Implement code
│     ├─> Verify patterns
│     │
│     └─> Return Handoff:
│         ```toon
│         from: cui-java-core-skill
│         to: build-verification
│
│         artifacts:
│           files[2]: AuthService.java, TokenValidator.java
│           interfaces[2]: AuthService, TokenValidator
│
│         decisions[2]:
│         - JWT with 24h expiry
│         - Refresh token rotation
│
│         next_action: Verify build compiles
│         ```
│
└─> Step 3c: Return handoff to command
    ```toon
    from: java-implement-agent
    to: task-implement-command

    artifacts:
      files[2]: AuthService.java, TokenValidator.java

    next_action: Verify Maven build
    ```
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 4: Command delegates to build-verify-agent              │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
Task: cui-task-workflow:build-verify-agent
  Prompt: [TOON handoff]
│
├─> Step 4a: Process handoff (agent in isolated context)
│   Extract artifacts, detect build tool (Maven)
│
├─> Step 4b: Delegate to Maven build
│   │
│   └─> Generate Handoff:
│       ```toon
│       from: build-verify-agent
│       to: builder-maven-rules-skill
│
│       task:
│         description: Verify Maven build
│         goals: clean verify
│
│       artifacts: {...}
│       ```
│       │
│       ▼
│   Skill: builder:builder-maven-rules
│     Workflow: Execute Build
│     Input: [TOON handoff]
│     │
│     ├─> Process handoff input
│     ├─> Execute Maven build
│     ├─> Parse results
│     │
│     └─> Return Handoff:
│         ```toon
│         from: maven-build-agent
│         to: result-processor
│
│         task:
│           status: SUCCESS
│
│         next_action: Commit changes
│         ```
│
└─> Step 4c: Return to command
    ```toon
    from: build-verify-agent
    to: task-implement-command

    task:
      status: completed
      build_status: SUCCESS

    next_action: Commit and complete
    ```
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 5: Command completes workflow                           │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
├─> Step 5a: Commit changes (command continues)
│   │
│   └─> Skill: cui-task-workflow:git-workflow
│         Workflow: Commit
│         Input: [artifacts from handoff chain]
│
└─> Step 5b: Return final result to user
    Task implementation completed:
    - Plan: .claude/plans/plan-auth-feature.md
    - Implementation: AuthService.java, TokenValidator.java
    - Build: SUCCESS
    - Commit: {commit_hash}
```

## Handoff Chain Visualization

```
Phase 1: /task-plan (optional - creates Markdown plan)
  │
  ├─> [HANDOFF: review-request]
  │   │
  │   └─> task-review skill
  │       │
  │       └─> [HANDOFF: review-complete] → back to command
  │
  ├─> [HANDOFF: plan-request]
  │   │
  │   └─> task-plan skill
  │       │
  │       ├─> Creates: .claude/plans/plan-xyz.md
  │       │
  │       └─> [HANDOFF: plan-complete] → back to command
  │
  └─> Returns plan location to user
      "Created: .claude/plans/plan-xyz.md"
      "Next: /task-implement plan=.claude/plans/plan-xyz.md"

Phase 2: /task-implement (uses plan from Phase 1 or creates inline)
  │
  ├─> Load plan from Markdown file (or create inline if needed)
  │
  ├─> [HANDOFF: implement-request, language=java]
  │   │
  │   └─> java-implement-agent ← CONTEXT ISOLATION
  │       │
  │       ├─> Reads: .claude/plans/plan-xyz.md
  │       │
  │       ├─> [HANDOFF: feature-request]
  │       │   │
  │       │   └─> cui-java-core skill
  │       │       │
  │       │       └─> [HANDOFF: implementation-complete]
  │       │
  │       └─> [HANDOFF: implementation-result] → back to command
  │
  ├─> [HANDOFF: verify-request]
  │   │
  │   └─> build-verify-agent
  │       │
  │       ├─> [HANDOFF: maven-build-request]
  │       │   │
  │       │   └─> builder-maven-rules skill
  │       │       │
  │       │       └─> [HANDOFF: build-complete]
  │       │
  │       └─> [HANDOFF: verification-complete] → back to command
  │
  ├─> [HANDOFF: commit-request]
  │   │
  │   └─> git-workflow skill
  │       │
  │       └─> [HANDOFF: commit-complete] → back to command
  │
  └─> Return final result to user
```

**Key Differences**:
- Separate `/task-plan` command creates Markdown plans in `.claude/plans/`
- `/task-implement` can use existing plans or create inline
- Command orchestrates directly, context isolation at language-specific agent level
- Plan files are persistent artifacts, can be manually edited

## Migration Strategy

### Phase 1: Update cui-task-workflow Commands
1. Create /task-plan command (~80 lines) - creates Markdown plans in .claude/plans/
2. Update /task-implement command to accept plan= parameter (~120 lines)
3. Update /pr-fix command to orchestrate directly (~120 lines)
4. Replace JSON handoff templates with TOON format (see cui-utilities:toon-usage)
5. Create build-verify-agent (~80 lines)
6. Test plan creation and implementation workflows

### Phase 2: Update cui-java-expert
1. Add handoff input processing to all agents (Step 0)
2. Add handoff output generation to all agents (Final Step)
3. Update skills to accept/return handoffs
4. Test integration with cui-task-workflow

### Phase 3: Enable builder-maven for Handoffs
1. Update builder-maven-rules skill to accept handoff input (Step 0)
2. Update builder-maven-rules skill to return handoff output (Final Step)
3. Add handoff templates and examples to skill
4. Test direct skill invocation with handoffs from build-verify-agent
5. Replace direct SlashCommand calls with handoffs

### Phase 4: Remove Deprecated Patterns
1. Remove /java-full-workflow command
2. Remove direct SlashCommand calls
3. Remove direct Skill calls across bundles
4. Update all documentation

### Phase 5: Extend to cui-frontend-expert
1. Apply same patterns to JavaScript bundle
2. Create js-implement-agent, js-verify-agent
3. Integrate with cui-task-workflow via handoffs
4. Enable polyglot project support

## Success Metrics

### Code Metrics
- **cui-task-workflow commands**: 3 commands (task-plan ~80 lines, task-implement ~120 lines, pr-fix ~120 lines)
- **cui-task-workflow agents**: Only build-verify-agent (~80 lines)
- **Language-specific agents**: ~70-80 lines (java-implement-agent, etc.)
- **Plan files**: Markdown format in .claude/plans/ directory
- **Handoff usage**: 100% of inter-component communication
- **Direct calls**: 0 (remove all SlashCommand/direct Skill calls)

### Architecture Metrics
- **Main control**: cui-task-workflow (centralized)
- **Communication**: Handoff-based (structured)
- **Context isolation**: Agent-based (maintained)
- **State preservation**: Handoff chain (continuous)

### Integration Metrics
- **Language bundles**: Called via handoff only
- **Build tools**: Invoked via handoff only
- **Memory integration**: Handoffs persisted to memory
- **Recovery**: Resume from any handoff point

## Benefits Summary

### For Users
- ✅ Single entry point for all tasks (`/task-implement`)
- ✅ Consistent workflow across languages
- ✅ Transparent orchestration
- ✅ Recoverable sessions

### For Development
- ✅ Clear separation of concerns
- ✅ Modular architecture
- ✅ Testable components
- ✅ Maintainable codebase

### For Extension
- ✅ Easy to add new languages (follow handoff pattern)
- ✅ Easy to add new build tools (follow handoff pattern)
- ✅ Easy to add new workflows (use orchestrator patterns)
- ✅ Composable via handoff chains

## Conclusion

The target architecture transforms isolated bundles into an **integrated, handoff-based orchestration system** with **cui-task-workflow as main control** and **language-specific bundles as specialized delegates**.

**Key Transformation**:
```
BEFORE: Standalone bundles, direct calls, mixed patterns
AFTER:  Integrated system, handoff-based, consistent patterns
```

**Communication Model**:
```
BEFORE: Command → Skill OR Command → Agent → Skill
AFTER:  Command → [HANDOFF] → Agent → [HANDOFF] → Skill → [HANDOFF]
```

This enables:
- ✅ Centralized orchestration
- ✅ Structured state transfer
- ✅ Context preservation
- ✅ Generic language support
- ✅ Scalable architecture
- ✅ Consistent patterns
- ✅ Maintainable system
