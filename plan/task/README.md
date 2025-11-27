# Architectural Redesign: Task Workflow Integration with Handoff-Based Communication

## Overview

This directory contains comprehensive analysis and design documents for redesigning the interplay between task-management (cui-task-workflow) and implementation bundles (cui-java-expert, cui-frontend-expert).

**Core Goal**: Transform from isolated bundles with mixed communication patterns into an **integrated, handoff-based orchestration system** with cui-task-workflow as the main control layer.

## Documents

### 1. Current State Analysis

#### [01-current-cui-task-workflow-analysis.md](01-current-cui-task-workflow-analysis.md)
**Analysis of cui-task-workflow bundle structure**

**Key Findings**:
- ✅ Clean goal-based structure (IMPLEMENT, FIX)
- ✅ Minimal wrapper commands (< 150 lines)
- ✅ Comprehensive handoff protocol defined
- ❌ No agent delegation - commands execute directly
- ❌ Handoff protocol underutilized (memory only)
- ❌ Direct SlashCommand calls instead of handoffs

**Recommendations**:
- Introduce agents with handoff-based communication
- Replace direct calls with handoff delegation
- Enable generic language support via handoffs

#### [02-current-cui-java-expert-analysis.md](02-current-cui-java-expert-analysis.md)
**Analysis of cui-java-expert bundle structure**

**Key Findings**:
- ✅ Excellent agent-first architecture
- ✅ Minimal wrapper agents (49-72 lines)
- ✅ Context isolation working well
- ✅ Model optimization (Haiku/Sonnet)
- ❌ No handoff protocol usage
- ❌ No integration with cui-task-workflow
- ❌ Mixed delegation patterns (Task vs Skill)

**Recommendations**:
- Integrate with cui-task-workflow via handoffs
- Implement handoff I/O in all agents
- Enable skills to accept/return handoffs
- Consistent delegation via handoff protocol

### 2. Target Architecture

#### [03-target-architecture.md](03-target-architecture.md)
**Complete target architecture with ASCII diagrams**

**Key Transformations**:
```
BEFORE: Command → Skill (direct)  OR  Command → Agent → Skill (direct)
AFTER:  Command → [TOON HANDOFF] → Skill/Agent → [TOON HANDOFF] → Result
```

**Architecture Simplifications**:
- ❌ Removed task-implement-agent (command orchestrates directly)
- ❌ Removed pr-fix-agent (command orchestrates directly)
- ✅ TOON format throughout (30-60% token reduction)

**Commands**:
1. **`/task-plan`** - Create/refine Markdown plans in .claude/plans/
2. **`/task-implement`** - Implement from plan files or descriptions
3. **`/pr-fix`** - Diagnose and fix PR issues

**Architecture Layers**:
1. **cui-task-workflow** - Main control and orchestration
2. **Language Bundles** - Invoked via handoff delegation
3. **Build Tools** - Invoked via handoff delegation

**Communication Model**: Handoff protocol as primary mechanism

**Benefits**:
- ✅ Centralized orchestration
- ✅ Structured state transfer
- ✅ Context preservation
- ✅ Generic language support
- ✅ Scalable architecture

### 3. Generic Patterns

#### [04-generic-workflow-patterns.md](04-generic-workflow-patterns.md)
**Reusable workflow patterns for all language bundles**

**Patterns Defined**:
1. **Task Implementation Workflow** - Generic task orchestration
2. **Task Review Workflow** - Readiness verification
3. **Build Verification Workflow** - Generic build coordination
4. **Quality Analysis Workflow** - Parallel quality checks
5. **PR Management Workflow** - PR issue resolution
6. **Language Implementation Workflow** - Language-specific template
7. **Language Test Workflow** - Testing template
8. **Language Fix Workflow** - Error fixing template
9. **Language Verify Workflow** - Verification template

**Key Principles**:
- Language-agnostic orchestration
- TOON handoff communication (30-60% token reduction)
- Context preservation across chains
- Memory integration at sync points
- Consistent error handling
- Direct command orchestration (no unnecessary agents)

### 4. Plan Management Specification

#### [06-plan-management-specification/](06-plan-management-specification/)
**Modular plan management abstraction layer specification with phase-based workflow and reference management**

**Architecture**: One skill per phase, with plan-files as shared persistence layer

**Phase Skills** (6 directories):
- **[plan-init/](06-plan-management-specification/plan-init/)** - Create plan, environment detection, type routing
  - [implementation.md](06-plan-management-specification/plan-init/implementation.md) - Full dev workflow (5 phases)
  - [simple.md](06-plan-management-specification/plan-init/simple.md) - Lightweight workflow (3 phases)
  - [handoff.md](06-plan-management-specification/plan-init/handoff.md) - External interface specifications
- **[plan-refine/](06-plan-management-specification/plan-refine/)** - Analyze requirements, plan tasks, identify docs
  - [refine.md](06-plan-management-specification/plan-refine/refine.md) - Main refine phase workflow
  - [implementation-requirements-template.md](06-plan-management-specification/plan-refine/implementation-requirements-template.md) - Runtime artifact template
  - [handoff.md](06-plan-management-specification/plan-refine/handoff.md) - External interface specifications
- **[plan-implement/](06-plan-management-specification/plan-implement/)** - Execute tasks, delegate to language agents
  - [implement.md](06-plan-management-specification/plan-implement/implement.md) - Main implement phase workflow
  - [handoff.md](06-plan-management-specification/plan-implement/handoff.md) - External interface specifications
- **[plan-verify/](06-plan-management-specification/plan-verify/)** - Run builds, quality checks, documentation review
  - [verify.md](06-plan-management-specification/plan-verify/verify.md) - Main verify phase workflow
  - [handoff.md](06-plan-management-specification/plan-verify/handoff.md) - External interface specifications
- **[plan-finalize/](06-plan-management-specification/plan-finalize/)** - Commit changes, create PR, handle reviews
  - [finalize.md](06-plan-management-specification/plan-finalize/finalize.md) - Main finalize phase workflow
  - [handoff.md](06-plan-management-specification/plan-finalize/handoff.md) - External interface specifications
- **[plan-files/](06-plan-management-specification/plan-files/)** - Shared persistence layer for all phases
  - [plan-files.md](06-plan-management-specification/plan-files/plan-files.md) - Persistence operations
  - [persistence.md](06-plan-management-specification/plan-files/persistence.md) - File format specifications
  - [handoff.md](06-plan-management-specification/plan-files/handoff.md) - External interface specifications

**Top-Level Documents**:
- **[README.md](06-plan-management-specification/README.md)** - Overview and navigation
- **[architecture.md](06-plan-management-specification/architecture.md)** - Abstraction layer design and patterns
- **[plan-types.md](06-plan-management-specification/plan-types.md)** - Init phase router and selection logic
- **[templates-workflow.md](06-plan-management-specification/templates-workflow.md)** - Plan templates and phase-based workflow
- **[api.md](06-plan-management-specification/api.md)** - Complete skill API with TOON handoff interfaces
- **[decomposition.md](06-plan-management-specification/decomposition.md)** - Implementation details and checklist
- **[plan.md](06-plan-management-specification/plan.md)** - Implementation plan with task checklist

**Key Features**:
- **One skill per phase**: plan-init, plan-refine, plan-implement, plan-verify, plan-finalize
- **Shared persistence**: plan-files skill handles all file I/O operations
- **Directory Structure**: `.claude/plans/{task-name}/` with `plan.md` and `references.md`
- **Phase-based workflow**: 5 sequential phases (init, refine, implement, verify, finalize)
- **Handoff separation**: External interfaces in handoff.md, internal delegations in main specs
- **Reference Management**: Centralized tracking of files, ADRs, interfaces, issues, branches
- **TOON handoff interfaces** for all operations (30-60% token reduction)

**Document Count**: 7 top-level + 17 phase-specific = 24 documents

### 5. Specific Implementation

#### [05-specific-workflow-java-implementation.md](05-specific-workflow-java-implementation.md)
**Complete concrete example: JWT authentication implementation**

**Demonstrates**:
- 15 TOON handoffs across 7 components
- 3 bundles integrated (task-workflow, java-expert, maven)
- Complete workflow trace from user input to result
- Error handling (build failure → fix → retry → success)
- Context preservation through entire TOON chain
- Memory integration for recovery
- Direct command orchestration (no task-implement-agent)

**Handoff Chain**:
```
User → Command → Skill → Command → Agent → Skill → Command → Agent → Result
```
Note: Command orchestrates directly; build tools invoked as skills from build-verify-agent

**Timeline**: ~9.5 minutes end-to-end
**Components**: 1 command, 3 agents, 3 skills
**Handoffs**: 15 TOON handoffs (reduced from 17 JSON handoffs)
**Token Savings**: 30-60% vs original JSON design

## Key Architectural Principles

### 1. Main Control with cui-task-workflow

**cui-task-workflow** is the orchestration layer:
- Entry point for all tasks
- Language detection and routing
- Build verification coordination
- PR and git management

### 2. TOON Handoff-Based Communication

**All inter-component communication via TOON handoff protocol**:
- TOON format (30-60% token reduction vs JSON)
- Context preservation
- State transfer
- Memory integration

**TOON Handoff Structure**: See [04-generic-workflow-patterns.md](04-generic-workflow-patterns.md#toon-handoff-structure) for complete structure definition with all fields.

**TOON Specification**: See `target/toon/architecture.md` for format details and token reduction analysis.

### 3. Plan Directories as Persistent Artifacts

**Plan directories are organized Markdown artifacts in `.claude/plans/{task-name}/`, NOT handoff content**:
- ✅ **Directory Structure**: Each plan has dedicated subdirectory with `plan.md` and `references.md`
- ✅ Markdown format - human-readable, manually editable, GitHub-compatible
- ✅ Created by `/task-plan` command (delegates to `task-plan` skill)
- ✅ Persist across session boundaries in .claude/plans/
- ✅ Integrate with memory and git
- ✅ Keep handoffs efficient (reference directory path, not embed content)
- ✅ Follow standard artifact pattern (like code files)
- ✅ Iteratively refined with `/task-plan plan=.claude/plans/{task-name}/`
- ✅ **Reference Management**: Separate `references.md` for ADRs, interfaces, files, issues, branches

**Abstraction Pattern** (like `adr-management` and `interface-management`):
- All plan operations abstracted through `task-plan` skill
- Skill handles directory creation and file I/O (Bash, Read, Write, Edit)
- Implementation details (location, format, structure) can change without affecting callers
- Skills provide consistent interface for plan and reference management
- Seamless integration with `adr-management` and `interface-management` skills
- **Full specification**: See [06-plan-management-specification](06-plan-management-specification/) ([API](06-plan-management-specification/api.md))

**Pattern**:
1. `/task-plan` command delegates to `task-plan` skill
2. Skill creates directory `.claude/plans/{task-name}/` with `plan.md` and `references.md`
3. Handoffs reference plan directory path
4. `/task-implement` delegates to skills for plan reading (both files)
5. Plans and references can be manually edited or refined through skill abstraction
6. References managed via skill integration with `adr-management` and `interface-management`

### 4. Minimal Wrappers

**Size Guidelines**:
- Commands: ~120 lines (parameter parsing, orchestration, TOON handoff generation)
- Agents: ~80 lines (context isolation, TOON handoff processing, orchestration)
- Skills: 400-800 lines (business logic, standards, workflows)

**Responsibility Split**:
- Commands: User-facing entry points, parameter parsing, direct orchestration, TOON handoff generation
- Agents: Context isolation (cross-bundle only), TOON handoff processing, result formatting
- Skills: Business logic, standards knowledge, workflows, TOON handoff I/O

### 5. Context Isolation via Agents

**Benefits**:
- Each agent spawns in isolated context
- Skills load in agent context
- Context released after completion
- No cross-contamination

### 6. Skills Hold All Logic

**Single Source of Truth**:
- All standards knowledge
- All implementation patterns
- All verification rules
- All workflows

### 7. When to Use Agents vs Direct Skills

**Use Agents When**:
- Context isolation needed (cross-bundle calls)
- Multiple skill orchestration within bundle
- Complex pre-processing or transformation
- Iterative error recovery logic

**Call Skills Directly When**:
- Single skill invocation
- Calling agent already provides context
- Simple pass-through (no orchestration)
- Example: `build-verify-agent → Skill: builder:builder-maven-rules-rules` ✅

This pattern eliminates unnecessary wrapper agents while maintaining handoff benefits.

## Migration Strategy

### Phase 1: Add Handoff Infrastructure
- Create handoff-enabled agents in cui-task-workflow
- Update workflow-patterns with templates
- Test handoff chains

### Phase 2: Update cui-java-expert
- Add handoff I/O to all agents
- Update skills for handoff support
- Test integration

### Phase 3: Enable builder-maven for Handoffs
- Update builder-maven-rules skill for handoff I/O
- No agents needed (build-verify-agent provides context)
- Replace direct SlashCommand calls with handoffs

### Phase 4: Remove Deprecated Patterns
- Remove /java-full-workflow
- Remove direct SlashCommand calls
- Update documentation

### Phase 5: Extend to cui-frontend-expert
- Apply same patterns to JavaScript
- Create js-implement-agent, js-verify-agent
- Enable polyglot support

## Success Metrics

See [03-target-architecture.md](03-target-architecture.md#success-metrics) for detailed metrics covering:
- **Code Metrics** - Component size targets and handoff usage
- **Architecture Metrics** - Control, communication, and isolation patterns
- **Integration Metrics** - Language bundle and build tool integration

## Benefits Summary

### For Users
- ✅ Iterative planning (`/task-plan`) creates organized plan directories in `.claude/plans/{task-name}/`
- ✅ **Directory Structure**: Separate `plan.md` and `references.md` for clean organization
- ✅ **Reference Management**: Centralized tracking of ADRs, interfaces, files, issues, branches, external docs
- ✅ Single implementation entry point (`/task-implement`)
- ✅ Consistent workflow across languages
- ✅ Transparent orchestration
- ✅ Recoverable sessions
- ✅ Plan files and references can be manually edited or refined
- ✅ Plan operations abstracted through skills (implementation flexibility)
- ✅ Seamless integration with `adr-management` and `interface-management` skills

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

## Implementation Checklist

See [05-specific-workflow-java-implementation.md](05-specific-workflow-java-implementation.md#implementation-checklist) for complete implementation checklist covering:
- **cui-task-workflow** - Command updates, skill splits, agent creation
- **cui-java-expert** - Handoff I/O integration for all agents and skills
- **builder-maven** - Skill updates for TOON handoff support
- **Testing** - Complete test scenarios for handoff chains and recovery

## Related Architecture Patterns

### Plugin Architecture Principles
- **Minimal Wrapper Pattern** - Thin orchestrators < 150 lines
- **Skills as Business Logic** - Single source of truth
- **Progressive Disclosure** - Load on-demand
- **Relative Path Pattern** - Portable resource paths
- **Context Isolation** - Agents for isolation

### Workflow Patterns
- **TOON Handoff Protocol** - Structured state transfer (30-60% token savings)
- **Direct Command Orchestration** - No unnecessary wrapper agents
- **Context Compression** - Long-running sessions
- **Integration Validation** - Parallel consistency
- **Token Budget** - Context allocation with TOON format

## References

### External Resources
- [Claude Skills Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
- [Claude Code Plugin Documentation](https://docs.claude.com/en/docs/claude-code/plugins)
- [Conventional Commits](https://www.conventionalcommits.org/)

### Internal Skills
- `cui-plugin-development-tools:plugin-architecture` - Architecture principles
- `cui-task-workflow:workflow-patterns` - Handoff protocols
- `cui-utilities:claude-memory` - State persistence

## Next Steps

1. **Review Documents**: Read through all 5 documents in order
2. **Validate Architecture**: Ensure design meets all requirements
3. **Plan Implementation**: Prioritize changes by phase
4. **Start Phase 1**: Begin with handoff infrastructure
5. **Iterate**: Test → Fix → Refine → Repeat

## Conclusion

This architectural redesign transforms isolated bundles into an **integrated, TOON handoff-based orchestration system** that provides:

**Key Transformations**:
```
BEFORE: Standalone bundles, direct calls, JSON handoffs, mixed patterns
AFTER:  Integrated system, TOON handoffs, direct command orchestration
```

**Communication Model**:
```
BEFORE: Command → Skill OR Command → Agent → Skill (JSON)
AFTER:  Command → [TOON HANDOFF] → Skill/Agent → [TOON HANDOFF] → Result
```

**Architecture Improvements**:
- ✅ TOON format: 30-60% token reduction
- ✅ Direct command orchestration (removed task-implement-agent, pr-fix-agent)
- ✅ 15 handoffs (down from 17 in original JSON design)
- ✅ 7 components (down from 9 in original design)

**Result**: A scalable, maintainable, and token-efficient architecture that serves as the foundation for all future development workflows across any programming language.
