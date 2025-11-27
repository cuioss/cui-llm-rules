# Current Structure Analysis: cui-task-workflow

**Date**: 2025-11-26
**Purpose**: Document the current structure, patterns, and issues in cui-task-workflow bundle

## Overview

cui-task-workflow is a **goal-based workflow bundle** that implements two primary user goals:
1. **IMPLEMENT** - Transform tasks into verified code (`/task-implement`)
2. **FIX** - Diagnose and fix PR issues (`/pr-fix`)

**Target Architecture**: See [03-target-architecture.md](03-target-architecture.md) for the proposed redesign addressing the issues identified in this analysis.

## Current Architecture

```
cui-task-workflow/
├── commands/                    # 2 goal-based commands (270 lines total)
│   ├── task-implement.md       # 116 lines - IMPLEMENT goal
│   └── pr-fix.md               # 142 lines - FIX goal
└── skills/                      # 5 skills with workflows
    ├── workflow-patterns/       # Handoff protocols & orchestration patterns
    ├── cui-task-planning/       # Plan, Execute, Review workflows
    ├── cui-git-workflow/        # Git commit workflows
    ├── pr-workflow/             # PR review handling
    └── sonar-workflow/          # Sonar issue fixing
```

### Command Analysis

#### /task-implement (116 lines)
**Purpose**: Implement GitHub issues or standalone tasks with full verification

**Pattern**: Minimal wrapper (< 150 lines) ✅
- Parameter parsing: 20 lines
- Mode determination: 10 lines
- Memory management: 15 lines
- Workflow delegation: 40 lines
- Verification: 15 lines
- Result formatting: 16 lines

**Delegation Pattern**:
```
/task-implement
  ├─> cui-task-planning skill (Review/Plan/Execute workflows)
  ├─> workflow-patterns skill (handoff protocols)
  ├─> claude-memory skill (state persistence)
  └─> SlashCommand(/maven-build-and-fix) [verification]
```

**Strengths**:
- ✅ Clean goal-based structure (IMPLEMENT)
- ✅ Thin wrapper pattern (<150 lines)
- ✅ Delegates all business logic to skills
- ✅ Uses handoff protocol for state transfer
- ✅ Memory integration for recovery
- ✅ Mode-based routing (FULL/PLAN/QUICK)

**Issues**:
- ❌ Direct SlashCommand call instead of handoff
- ❌ Language-specific verification hardcoded (Java/JavaScript)
- ❌ No agent delegation - all inline in command

#### /pr-fix (142 lines)
**Purpose**: Diagnose and fix PR issues (build, reviews, Sonar)

**Pattern**: Minimal wrapper ✅
- Parameter parsing: 25 lines
- Check determination: 15 lines
- Workflow delegation: 70 lines
- Result synthesis: 32 lines

**Delegation Pattern**:
```
/pr-fix
  ├─> pr-workflow skill (Fetch Comments, Handle Review)
  ├─> sonar-workflow skill (Fetch Issues, Fix Issues)
  └─> SlashCommand(/maven-build-and-fix) [build fixing]
```

**Strengths**:
- ✅ Goal-based structure (FIX)
- ✅ Thin wrapper pattern
- ✅ Delegates to skills
- ✅ Parallel check support

**Issues**:
- ❌ Direct SlashCommand call instead of handoff
- ❌ No agent delegation
- ❌ Limited to Java/Maven projects

### Skills Analysis

#### workflow-patterns (Reference Skill)
**Purpose**: Orchestration patterns for agent coordination and handoffs

**Contents**:
- `references/handoff-protocol.md` - Structured state transfer protocol
- `references/context-compression.md` - Context optimization strategies
- `references/integration-validation.md` - Parallel execution validation
- `references/token-budget-guidelines.md` - Context allocation guidelines
- `references/wave-processing.md` - Parallel task management
- `templates/*.json` - Handoff templates (minimal, standard, full)

**Strengths**:
- ✅ Pure reference skill (Pattern 10)
- ✅ Progressive disclosure
- ✅ Comprehensive handoff protocol
- ✅ Multiple handoff levels (minimal, standard, full)

**Usage in Bundle**:
- Used for handoff structure templates
- Referenced in task-implement for state transfer
- NOT used for actual agent coordination (no agents yet)

#### cui-task-planning (Execution Skill)
**Purpose**: Plan, Execute, Review workflows for task implementation

**Workflows**:
1. **Plan Workflow** - Create task breakdowns from issues
2. **Execute Workflow** - Implement tasks from plan files
3. **Review Workflow** - Verify implementation readiness

**Scripts**:
- `create-task-breakdown.py` - Generate structured task plans
- `track-task-progress.py` - Parse plan progress
- `validate-acceptance.py` - Verify acceptance criteria

**Pattern**: Pattern 1 (Script Automation) + Pattern 2 (Read-Process-Write)

**Strengths**:
- ✅ Self-contained workflows
- ✅ Script automation for deterministic logic
- ✅ JSON output for structured data
- ✅ Memory integration
- ✅ Handoff generation capability

**Issues**:
- ❌ Absorbs agent functionality (Review/Plan/Execute agents merged into skill)
- ❌ Large skill (~411 lines) - close to limit
- ❌ Mixed concerns (planning + execution + review)

#### cui-git-workflow (Execution Skill)
**Purpose**: Git commit workflows with standards compliance

**Scripts**:
- `generate-commit-message.py` - Analyze changes and generate commit messages

**Pattern**: Pattern 1 (Script Automation)

**Strengths**:
- ✅ Focused skill (single responsibility)
- ✅ Script-based deterministic logic
- ✅ Standards compliance built-in

#### pr-workflow (Execution Skill)
**Purpose**: PR review comment handling

**Workflows**:
1. **Fetch Comments** - Retrieve review comments
2. **Handle Review** - Respond to comments

**Scripts**:
- `fetch-pr-comments.py` - Retrieve PR comments via gh CLI
- `analyze-review-comments.py` - Parse and categorize comments

**Pattern**: Pattern 1 (Script Automation) + Pattern 3 (Search-Analyze-Report)

**Strengths**:
- ✅ Clean workflow separation
- ✅ Script automation for gh CLI integration
- ✅ Structured JSON output

#### sonar-workflow (Execution Skill)
**Purpose**: SonarQube issue handling

**Workflows**:
1. **Fetch Issues** - Retrieve Sonar issues
2. **Fix Issues** - Apply fixes to issues

**Scripts**:
- `fetch-sonar-issues.py` - Retrieve issues via MCP tool
- `categorize-fixes.py` - Group fixes by category

**Pattern**: Pattern 1 (Script Automation) + Pattern 3 (Search-Analyze-Report)

**Strengths**:
- ✅ Clean workflow separation
- ✅ MCP tool integration
- ✅ Categorized fix approach

## Architectural Patterns

### Current Patterns in Use

#### 1. Goal-Based Organization ✅
Commands organized by user goals (IMPLEMENT, FIX) not by component types.

#### 2. Minimal Wrapper Pattern ✅
Both commands are < 150 lines and delegate to skills.

#### 3. Skills as Business Logic ✅
All standards, workflows, and implementation logic in skills.

#### 4. Script Automation ✅
Deterministic logic in Python scripts with JSON output.

#### 5. Handoff Protocol ⚠️
- Protocol defined in workflow-patterns skill
- Templates available (minimal, standard, full)
- NOT yet used for agent coordination (no agents)
- Used for memory/state persistence only

### Anti-Patterns Present

#### 1. Direct SlashCommand Calls ❌
```markdown
# In task-implement.md:
SlashCommand(/builder:maven-build-and-fix)
```

Should use TOON handoff protocol instead:
```toon
from: task-implement-command
to: build-verify-agent
workflow: build-verification

task:
  description: Verify implementation build
  type: verify

files[N]{path}:
src/**/*.java

next_action: Run Maven build and fix errors
```

#### 2. Language-Specific Hardcoding ❌
```markdown
Auto-detect language: `pom.xml` → Java, `package.json` → JavaScript
Run `SlashCommand(/builder:maven-build-and-fix)`.
```

Should be generic with language delegation via TOON handoffs:
```toon
from: task-implement-command
to: java-implement-agent
workflow: implementation

context:
  language: auto-detected
  module: auth-service

next_action: Implement feature
```

#### 3. No Structured Handoff Communication ❌
- Commands invoke skills directly without handoff protocol
- No structured state transfer between components
- Missing context preservation mechanism
- No memory integration for recovery

Should use TOON handoff protocol for ALL inter-component communication.

#### 4. Fat Skill (cui-task-planning) ⚠️
- 411 lines (within limit but close)
- Mixed concerns (plan + execute + review)
- Should split into 3 focused skills (task-review, task-plan, task-execute)

## Communication Patterns

### Current Communication Flow

```
User → Command → Skill → Result
```

**No agent-to-agent or agent-to-skill handoffs currently in use.**

### Handoff Protocol Status

**Defined but Not Implemented**:
- Handoff protocol fully documented in workflow-patterns
- Templates available (JSON and Markdown)
- Memory integration supported
- **NOT USED** for command-to-agent or agent-to-agent communication

**Current Usage**:
- Memory persistence only
- State recovery across sessions
- Plan file handoff structures

## Dependencies

### Inter-Bundle Dependencies

1. **builder-maven** (required)
   - `/maven-build-and-fix` command
   - Direct SlashCommand call (should be handoff)

2. **cui-utilities** (required)
   - `claude-memory` skill for session persistence
   - Proper Skill invocation ✅

3. **cui-java-expert** (optional)
   - Mentioned but no delegation
   - Should use handoff to java-implement-agent

4. **cui-frontend-expert** (optional)
   - Mentioned but no delegation
   - Should use handoff to js-implement-agent

## Strengths

1. ✅ **Clean Goal-Based Structure** - Two clear user goals
2. ✅ **Minimal Wrapper Commands** - Both < 150 lines
3. ✅ **Comprehensive Handoff Protocol** - Well-documented patterns
4. ✅ **Script Automation** - Deterministic logic externalized
5. ✅ **Memory Integration** - Session recovery capability
6. ✅ **Mode-Based Routing** - Flexible execution modes
7. ✅ **Progressive Disclosure** - Skills loaded on-demand

## Issues to Address

### Critical Issues

1. ❌ **No Structured Handoff Communication**
   - Commands invoke skills directly without handoff protocol
   - Missing structured state transfer
   - No context preservation mechanism
   - Memory integration underutilized

2. ❌ **Direct SlashCommand Calls**
   - Should use TOON handoff protocol
   - Breaks communication pattern consistency
   - No structured state transfer

3. ❌ **Language-Specific Hardcoding**
   - Java/Maven assumptions embedded
   - Should be generic with language delegation via handoffs

### Moderate Issues

4. ⚠️ **Fat Skill (cui-task-planning)**
   - 411 lines (close to 800 line guideline)
   - Mixed concerns (plan + execute + review)
   - Could split into 3 focused skills

5. ⚠️ **Handoff Protocol Underutilized**
   - Defined but only used for memory
   - Should be core communication pattern
   - Templates available but not used

### Minor Issues

6. ⚠️ **Limited Language Support**
   - Only Java/JavaScript explicitly supported
   - Should be extensible to other languages

## Recommendations for Redesign

### 1. Direct Command Orchestration with TOON Handoffs

Commands orchestrate directly without unnecessary wrapper agents:

```
/task-implement (command - ~120 lines)
  │
  ├─> [TOON HANDOFF] → task-plan skill
  │
  ├─> [TOON HANDOFF] → java-implement-agent
  │
  ├─> [TOON HANDOFF] → build-verify-agent
  │
  └─> [TOON HANDOFF] → git-workflow skill
```

**Key Decision**: No task-implement-agent needed - command orchestrates directly (~120 lines), saving 80+ lines and 2 handoffs

### 2. Replace SlashCommand with TOON Handoffs

```
CURRENT:
SlashCommand(/maven-build-and-fix)

TARGET (TOON format):
from: task-implement-command
to: build-verify-agent
workflow: build-verification

task:
  description: Verify Maven build
  type: verify

next_action: Fix compilation errors if present
```

### 3. Generic Language Delegation

```toon
from: task-implement-command
to: java-implement-agent
workflow: implementation

context:
  language: auto-detect
  module: auth-service

next_action: Implement feature
```

### 4. Split cui-task-planning Skill

```
CURRENT:
cui-task-planning (411 lines)
  - Plan workflow
  - Execute workflow
  - Review workflow

TARGET:
task-review (150 lines)       - Review workflow only
task-plan (200 lines)          - Plan workflow only
task-execute (150 lines)       - Execute workflow only
```

### 5. Use TOON Format Throughout

Replace all JSON handoffs with TOON format for 30-60% token reduction:

```toon
from: component-a
to: component-b
handoff_id: handoff-001

task:
  description: Task description
  status: pending

files[N]{path}:
file1.java
file2.java

next_action: What to do next
```

## Migration Path

### Phase 1: Update Commands for Direct Orchestration
1. Update `/task-implement` command to orchestrate directly (~120 lines)
2. Update `/pr-fix` command to orchestrate directly (~120 lines)
3. Replace all JSON handoff templates with TOON format
4. Test direct command orchestration

### Phase 2: Implement TOON Handoffs
1. Replace SlashCommand calls with TOON handoffs
2. Add TOON handoff generation in commands
3. Update skills to accept/return TOON handoffs
4. Test TOON handoff chains

### Phase 3: Generic Language Support
1. Abstract language-specific logic in commands
2. Implement language auto-detection
3. Use TOON handoffs for language delegation
4. Test polyglot workflows

### Phase 4: Split Fat Skill
1. Extract Review workflow → task-review skill
2. Extract Plan workflow → task-plan skill (see [06-plan-management-specification](06-plan-management-specification/))
3. Keep Execute workflow → task-execute skill
4. Update agent delegation

## Metrics

### Current State
- **Commands**: 2 (270 lines total)
- **Skills**: 5 (cui-task-planning ~411 lines)
- **Agents**: 0
- **Handoff Usage**: Memory only, not for communication
- **Scripts**: 8 Python scripts

### Target State (After Redesign)
- **Commands**: 3 (~320 lines total: /task-plan ~80 lines, /task-implement ~120 lines, /pr-fix ~120 lines)
- **Skills**: 7 (split cui-task-planning into 3: task-review, task-plan, task-execute)
- **Agents**: 1 (build-verify-agent ~80 lines only)
- **Plan Files**: Markdown format in .claude/plans/ directory
- **Handoff Usage**: Primary communication pattern (TOON format)
- **Scripts**: 8+ Python scripts (same or more)

**Note**: Separate /task-plan command for iterative plan creation. No task-implement-agent or pr-fix-agent - commands orchestrate directly.

## Conclusion

cui-task-workflow demonstrates excellent **goal-based organization** and **minimal wrapper commands**, but lacks **structured handoff-based communication**. The handoff protocol is comprehensive but underutilized.

**Key Transformation Required**:
```
BEFORE: Command → Skill (direct calls)
AFTER:  Command → [TOON HANDOFF] → Skill/Agent → [TOON HANDOFF] → Result
```

**Architecture Decision**: Commands orchestrate workflows directly (~120 lines) without unnecessary wrapper agents. Context isolation happens at language-specific agent level (java-implement-agent, js-implement-agent).

This will enable:
- ✅ Structured state transfer via TOON handoffs (30-60% token reduction)
- ✅ Context preservation across workflow stages
- ✅ Generic language support via delegation
- ✅ Memory integration for recovery
- ✅ Cleaner separation of concerns
- ✅ Direct command orchestration (no unnecessary wrappers)
