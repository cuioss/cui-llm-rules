# Generic Workflow Patterns for Handoff-Based Task Implementation

**Date**: 2025-11-26
**Purpose**: Define reusable workflow patterns for handoff-based orchestration across all language bundles

## Overview

This document defines **generic, reusable workflow patterns** that apply to **any language bundle** (Java, JavaScript, Python, etc.) using the **handoff-based communication protocol**.

**Core Principle**: Workflows are language-agnostic orchestration patterns that delegate language-specific work via handoffs.

**Concrete Example**: See [05-specific-workflow-java-implementation.md](05-specific-workflow-java-implementation.md) for a complete concrete implementation of these patterns applied to a Java JWT authentication task.

## Pattern Hierarchy

```
┌────────────────────────────────────────────────────────────┐
│              ORCHESTRATION PATTERNS                         │
│          (cui-task-workflow responsibility)                 │
│                                                              │
│  Pattern 1: Task Implementation Workflow                    │
│  Pattern 2: Task Review Workflow                            │
│  Pattern 3: Build Verification Workflow                     │
│  Pattern 4: Quality Analysis Workflow                       │
│  Pattern 5: PR Management Workflow                          │
└────────────────────────┬───────────────────────────────────┘
                         │ [TOON HANDOFF]
                         ▼
┌────────────────────────────────────────────────────────────┐
│           LANGUAGE-SPECIFIC PATTERNS                        │
│       (Language bundle responsibility)                      │
│                                                              │
│  Pattern 6: Language Implementation Workflow                │
│  Pattern 7: Language Test Workflow                          │
│  Pattern 8: Language Fix Workflow                           │
│  Pattern 9: Language Verify Workflow                        │
└─────────────────────────────────────────────────────────────┘
```

## Core TOON Handoff Structure

All patterns use this standard TOON handoff structure (30-60% token reduction vs JSON):

```toon
from: source-component
to: target-component
handoff_id: unique-id
workflow: workflow-name
timestamp: ISO-8601

task:
  description: What needs to be done
  type: implement|fix|verify|analyze
  status: pending|in_progress|completed|failed
  progress: 0-100%

files[N]{path}:
path/to/file1
path/to/file2

artifacts:
  key: value

interfaces[N]:
- Interface description 1
- Interface description 2

decisions[N]:
- Design decision 1
- Design decision 2

context:
  language: java|javascript|python|auto
  module: module-name
  notes: Additional context

dependencies[N]:
- dependency1
- dependency2

constraints[N]:
- constraint1
- constraint2

next_action: What to do next
next_focus: What to focus on

blockers[N]:
- blocker1

alternatives[N]:
- alternative1

memory:
  category: handoffs
  identifier: workflow-step-name
  persist: true
```

**TOON Format Benefits**:
- 30-60% token reduction vs JSON
- CSV-style arrays for tabular data
- Simple key-value for scalar fields
- Lists for ordered items
- Preserves all semantic information

## Pattern 1: Task Implementation Workflow

**Orchestrator**: `/task-implement` command (cui-task-workflow)
**Purpose**: Generic task implementation with language-specific delegation
**Mode**: Adaptive (FULL/PLAN/QUICK)
**Format**: TOON handoffs throughout

### Workflow Steps

```
┌────────────────────────────────────────────────────────┐
│ Step 0: Process Handoff Input                          │
│   Parse incoming handoff from command                  │
│   Extract task, mode, context                          │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 1: Review (FULL mode only)                        │
│   Generate Handoff: review-request                     │
│   └─> Skill: task-review                              │
│       Input: [handoff]                                 │
│       Output: [handoff: review-complete]               │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 2: Plan (FULL/PLAN modes)                        │
│   Generate Handoff: plan-request                       │
│   └─> Skill: task-plan                                │
│       Input: [handoff]                                 │
│       Output: [handoff: plan-complete]                 │
│       Note: See 06-plan-management-specification/      │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 3: Detect Language                                │
│   Auto-detect: pom.xml → java                         │
│                package.json → javascript               │
│                requirements.txt → python               │
│   Update handoff context: language={detected}         │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 4: Delegate Implementation                        │
│   Generate Handoff: implement-request                  │
│   └─> Task: {language}-implement-agent                │
│       Input: [handoff]                                 │
│       Output: [handoff: implementation-complete]       │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 5: Verify Build                                   │
│   Generate Handoff: verify-request                     │
│   └─> Task: build-verify-agent                        │
│       Input: [handoff with artifacts]                  │
│       Output: [handoff: verification-complete]         │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 6: Commit Changes                                 │
│   Generate Handoff: commit-request                     │
│   └─> Skill: git-workflow                             │
│       Workflow: Commit                                 │
│       Input: [handoff with all artifacts]              │
│       Output: [handoff: commit-complete]               │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 7: Cleanup and Return                             │
│   Persist handoff to memory                            │
│   Generate final handoff: task-complete                │
│   Return to command                                    │
└────────────────────────────────────────────────────────┘
```

### TOON Handoff Example

**Note**: For complete plan management API and TOON handoff interfaces, see [06-plan-management-specification/api.md](06-plan-management-specification/api.md).

**Input** (Command → Plan skill):
```toon
from: task-implement-command
to: task-plan-skill
handoff_id: handoff-001
workflow: task-planning

task:
  description: Add JWT authentication
  type: plan
  status: pending

context:
  mode: PLAN
  language: auto

next_action: Create structured plan
```

**Output** (Final result from command):
```toon
workflow: task-implementation
status: completed

task:
  description: Add JWT authentication
  type: implement
  status: completed
  progress: 100%

files[2]{path}:
src/auth/JwtService.java
src/auth/TokenValidator.java

interfaces[2]:
- JwtService
- TokenValidator

decisions[2]:
- JWT with HS256
- 24h token expiry

artifacts:
  commit_hash: abc123def456

context:
  language: java
  module: auth-service
  build_status: SUCCESS

next_alternatives[2]:
- Push to remote
- Create PR
```

## Pattern 2: Task Review Workflow

**Executor**: `task-review` skill (cui-task-workflow)
**Purpose**: Verify task readiness before implementation
**Mode**: Read-only analysis

### Workflow Steps

```
┌────────────────────────────────────────────────────────┐
│ Step 1: Process Handoff Input                          │
│   Extract task reference (issue/file)                  │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 2: Load Task Content                              │
│   If GitHub issue: gh issue view {number}             │
│   If file: Read {file_path}                           │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 3: Analyze Completeness                           │
│   Check: Description, Acceptance criteria,             │
│          Constraints, Dependencies, Edge cases         │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 4: Identify Gaps                                  │
│   List: Ambiguities, Missing criteria,                │
│         Undefined scope, Unspecified errors            │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 5: Update Documentation (Conditional)             │
│   If gaps found: Update issue/file                    │
│   Use: AskUserQuestion for clarification              │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 6: Quality Verification                           │
│   Verify: Consistency, Correctness, Clarity,          │
│           Completeness, Actionability                  │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 7: Return Handoff                                 │
│   Include: Review status, Issues found,               │
│            Changes made, Next action                   │
└────────────────────────────────────────────────────────┘
```

### TOON Handoff Example

**Output**:
```toon
from: task-review-skill
to: task-plan-workflow
workflow: task-review

task:
  description: Add JWT authentication
  status: completed
  review_status: ready

files[1]{path}:
docs/issue-123.md

artifacts:
  issues_found: 3
  issues_fixed: 3

decisions[2]:
- Use HS256 algorithm (performance)
- 24h token expiry (security balance)

context:
  quality_score: 95%
  criteria_count: 5
  edge_cases_count: 3

next_action: Proceed to planning
next_focus: Implementation strategy
```

## Pattern 3: Build Verification Workflow

**Orchestrator**: `build-verify-agent` (cui-task-workflow)
**Purpose**: Generic build verification with tool-specific delegation
**Mode**: Iterative fixing

### Workflow Steps

```
┌────────────────────────────────────────────────────────┐
│ Step 1: Process Handoff Input                          │
│   Extract artifacts, language, module                  │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 2: Detect Build Tool                              │
│   Java + pom.xml → Maven                              │
│   JavaScript + package.json → npm/yarn                │
│   Python + setup.py → pip/poetry                      │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 3: Delegate Build                                 │
│   Generate Handoff: build-request                      │
│   └─> Skill: {tool}-rules                             │
│       Workflow: Execute Build                          │
│       Input: [handoff]                                 │
│       Output: [handoff: build-result]                  │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 4: Check Build Status                             │
│   If SUCCESS → Return success handoff                  │
│   If FAILURE → Continue to Step 5                     │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 5: Delegate Fix (Iterative, max 3 attempts)      │
│   Generate Handoff: fix-request                        │
│   └─> Task: {language}-fix-build-agent                │
│       Input: [handoff with errors]                     │
│       Output: [handoff: fix-result]                    │
│   └─> Agent updates code, then loops back to Step 3   │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 6: Return Final Handoff                           │
│   Include: Build status, Fix attempts,                │
│            Remaining errors (if any)                   │
└────────────────────────────────────────────────────────┘
```

### Handoff Example

**Output Handoff** (to build tool skill):
```toon
from: build-verify-agent
to: builder-maven-rules-skill
handoff_id: build-001
workflow: build-verification

task:
  description: Execute Maven build
  type: build
  status: pending

context:
  language: java
  build_tool: maven
  goals: clean verify
  module: {module}

next_action: Execute Maven build
```

**Intermediate Handoff** (when build fails, to fix agent):
```toon
from: build-verify-agent
to: java-fix-build-agent
handoff_id: fix-001
workflow: build-fix
iteration: 1

task:
  description: Fix Maven build errors
  type: fix
  status: pending

files[1]{path}:
src/auth/JwtService.java

errors[1]{file,line,message}:
src/auth/JwtService.java,42,cannot find symbol: class Algorithm

context:
  language: java
  build_tool: maven
  max_iterations: 3
  current_iteration: 1

next_action: Fix compilation errors
next_focus: Missing imports
```

## Pattern 4: Quality Analysis Workflow

**Orchestrator**: `task-orchestrator-agent` (cui-task-workflow)
**Purpose**: Parallel quality analysis
**Mode**: Wave-based parallel execution

### Workflow Steps (Wave-Based)

```
┌────────────────────────────────────────────────────────┐
│ WAVE 1: DEPLOY - Launch Analysis Agents (Parallel)     │
│   ├─> Task: {language}-quality-agent                  │
│   ├─> Task: {language}-coverage-agent                 │
│   └─> Task: {language}-verify-agent                   │
│   All receive same handoff with context               │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼ Wait for all agents
┌────────────────────────────────────────────────────────┐
│ WAVE 2: SYNTHESIZE - Merge Results                     │
│   Collect handoffs from all agents                     │
│   Aggregate findings:                                  │
│   - Quality issues                                     │
│   - Coverage gaps                                      │
│   - Standards violations                               │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ WAVE 3: PRIORITIZE - Sort by Severity                  │
│   Group by: BLOCKER, HIGH, MEDIUM, LOW                │
│   Generate action plan                                 │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ WAVE 4: RETURN - Generate Consolidated Handoff         │
│   Include: All findings, Priorities,                  │
│            Recommendations, Next actions               │
└────────────────────────────────────────────────────────┘
```

### Handoff Example

**Output Handoff** (consolidated):
```toon
from: task-orchestrator-agent
to: caller
handoff_id: quality-001
workflow: quality-analysis
wave: 4

task:
  description: Quality analysis complete
  status: completed

files[1]{path}:
src/auth/**/*.java

analysis_results:
  quality_issues: 5
  quality_score: B+
  quality_blockers: 0
  coverage_line: 78
  coverage_branch: 65
  coverage_target: 80
  standards_violations: 3
  standards_compliant: 12

decisions[3]:
- Focus on branch coverage (65% → 80%)
- Fix 3 standards violations
- Defer 5 quality issues (non-blocking)

next_action: Address coverage gaps
next_focus: TokenValidator.validate() branches
```

## Pattern 5: PR Management Workflow

**Orchestrator**: `pr-fix-agent` (cui-task-workflow)
**Purpose**: Diagnose and fix PR issues
**Mode**: Conditional workflow

### Workflow Steps

```
┌────────────────────────────────────────────────────────┐
│ Step 1: Process Handoff Input                          │
│   Extract PR number, check types                       │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 2: Fetch PR Information                           │
│   gh pr view {pr_number} --json ...                   │
│   Extract: files, checks, reviews                     │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 3: Check Build Status (Conditional)               │
│   If checks=build OR checks=all:                      │
│   Generate Handoff: build-fix-request                  │
│   └─> Task: build-verify-agent                        │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 4: Handle Review Comments (Conditional)           │
│   If checks=reviews OR checks=all:                    │
│   Generate Handoff: review-handle-request              │
│   └─> Skill: pr-workflow                              │
│       Workflow: Handle Review                          │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 5: Fix Sonar Issues (Conditional)                 │
│   If checks=sonar OR checks=all:                      │
│   Generate Handoff: sonar-fix-request                  │
│   └─> Skill: sonar-workflow                           │
│       Workflow: Fix Issues                             │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 6: Return Consolidated Handoff                    │
│   Include: All check results, Fixes applied,          │
│            Remaining issues                            │
└────────────────────────────────────────────────────────┘
```

## Language-Specific Patterns

### Pattern 6: Language Implementation Workflow

**Executor**: `{language}-implement-agent` (language bundle)
**Purpose**: Language-specific feature implementation
**Delegation**: Language-specific skill

**Generic Structure** (applies to all languages):

```
┌────────────────────────────────────────────────────────┐
│ Step 0: Process Handoff Input                          │
│   Extract task, plan_file, context                     │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 1: Load Language Standards                        │
│   Skill: {language}-core                               │
│   Load on-demand: coding standards, patterns           │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 2: Implement Feature                              │
│   Skill: {language}-core                               │
│   Workflow: Implement Feature                          │
│   Input: [handoff]                                     │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 3: Verify Standards                               │
│   Check: Coding patterns, Best practices,             │
│          Language-specific rules                       │
└─────────────────────┬──────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────┐
│ Step 4: Return Handoff                                 │
│   Include: Files created/modified,                    │
│            Standards applied, Next action              │
└────────────────────────────────────────────────────────┘
```

**Handoff Template** (language-agnostic, TOON format):
```toon
from: {language}-implement-agent
to: build-verify-agent
handoff_id: impl-{timestamp}
workflow: language-implementation

task:
  description: Feature implementation complete
  type: implement
  status: completed

files[N]{path}:
path/to/file1
path/to/file2

interfaces[N]{name}:
PublicInterface1
PublicInterface2

context:
  language: {language}
  module: {module}
  standards_applied: Standard1,Standard2
  build_required: true

next_action: Verify build compiles
next_focus: Compilation and dependency resolution
```

## Handoff Chaining Rules

### Rule 1: Always Process Input Handoff
**Every agent/skill must have Step 0**: Process Handoff Input

```markdown
### Step 0: Process Handoff Input
If handoff parameter provided:
  - Parse TOON structure
  - Extract task, files, context
  - Load memory refs if specified
  - Validate required fields
```

### Rule 2: Always Generate Output Handoff
**Every agent/skill must generate handoff on completion**

```markdown
### Step N: Return Handoff
Generate TOON handoff structure:
  - from/to/workflow: Component routing
  - task: description/status/progress
  - files[N]: Created/modified files
  - context: language/module/environment
  - next_action/next_focus: What comes next

Return TOON handoff to caller
```

### Rule 3: Preserve Context Across Chain
**Handoff chain must maintain context**

```
Handoff-1 context: {language: "java", module: "auth"}
  └─> Handoff-2 context: {language: "java", module: "auth", ...}
      └─> Handoff-3 context: {language: "java", module: "auth", ...}
```

### Rule 4: Memory Integration
**Persist handoffs at synchronization points**

```markdown
### Memory Persistence Points
- After PLAN completion → Save plan handoff
- After IMPLEMENTATION completion → Save implementation handoff
- After VERIFICATION completion → Save verification handoff
- After COMMIT completion → Save commit handoff

Use: Skill: cui-utilities:claude-memory
     Operation: save
     Category: handoffs
     Identifier: {workflow}-{step}
```

### Rule 5: Error Handling in Handoffs

**Failed handoffs include error context** (TOON format):
```toon
task:
  status: failed

error:
  type: compilation|test|verification
  message: Error description
  details: Extended error details

next_action: Fix errors or abort

alternatives[N]:
- Alternative approach 1
- Alternative approach 2
```

## Integration Points

### With Memory Layer

**Save Handoff**:
```bash
python3 manage-memory.py save \
  --category handoffs \
  --identifier "{workflow}-{step}" \
  --content '{TOON handoff content}'
```

**Load Handoff**:
```bash
python3 manage-memory.py load \
  --category handoffs \
  --identifier "{workflow}-{step}"
```

**List Recent Handoffs**:
```bash
python3 manage-memory.py list \
  --category handoffs \
  --since 7d
```

### With workflow-patterns Skill

**Load TOON Handoff Templates**:
```
Skill: cui-task-workflow:workflow-patterns
Read: templates/handoff-standard.toon
```

**Reference Handoff Protocol**:
```
Skill: cui-task-workflow:workflow-patterns
Read: references/handoff-protocol.md
```

**TOON Specification**:
```
Skill: cui-utilities:toon-usage
Read: knowledge/toon-specification.md
```

## Summary

These generic workflow patterns provide:

1. ✅ **Language-Agnostic Orchestration** - Works with any language bundle
2. ✅ **TOON Handoff Communication** - 30-60% token reduction vs JSON
3. ✅ **Context Preservation** - State maintained across workflow stages
4. ✅ **Direct Command Orchestration** - No unnecessary wrapper agents
5. ✅ **Error Handling** - Consistent error propagation via TOON handoffs
6. ✅ **Memory Integration** - TOON handoffs persisted for recovery
7. ✅ **Composability** - Patterns combine to form complex workflows

**Usage**: All language bundles (Java, JavaScript, Python, etc.) follow these generic patterns and customize only the language-specific implementation details using TOON format throughout.
