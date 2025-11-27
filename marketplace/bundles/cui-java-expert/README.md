# CUI Java Expert

Comprehensive Java development expertise bundle with agent-first architecture for autonomous code implementation, testing, and standards compliance.

## Purpose

This bundle provides a complete Java development knowledge base with an **agent-first architecture**. Agents handle autonomous execution while commands orchestrate complex workflows. Skills contain all business logic and standards.

## Architecture

```
cui-java-expert/
├── agents/                  # 9 autonomous agents
│   ├── java-implement-agent.md      # Implement features
│   ├── java-implement-tests-agent.md # Implement tests
│   ├── java-fix-build-agent.md      # Fix compilation errors
│   ├── java-fix-tests-agent.md      # Fix test failures
│   ├── java-fix-javadoc-agent.md    # Fix JavaDoc errors
│   ├── java-refactor-agent.md       # Refactor code
│   ├── java-coverage-agent.md       # Analyze coverage (read-only)
│   ├── java-quality-agent.md        # Analyze quality (read-only)
│   └── java-verify-agent.md         # Verify compliance (read-only)
├── commands/                # 6 orchestration commands
│   ├── java-analyze-all.md          # Parallel analysis (Task tool)
│   ├── java-full-workflow.md        # Complete implement-test-verify
│   ├── java-create.md               # Interactive component creation
│   ├── java-enforce-logrecords.md   # Logging standards enforcement
│   ├── java-maintain-logger.md      # Logger maintenance workflow
│   └── java-optimize-quarkus-native.md # Native image optimization
└── skills/                  # 5 skills with workflows
    ├── cui-java-core/       # Core Java + Fix Compilation + Implement Feature
    ├── cui-java-unit-testing/ # Testing + Fix Test Failures + Implement Tests
    ├── cui-javadoc/         # JavaDoc + Fix JavaDoc Errors
    ├── cui-java-cdi/        # CDI/Quarkus standards
    └── cui-java-maintenance/ # Maintenance standards
```

## Agent-First Design

### Why Agents?

1. **Better Context Management**: Agents run in isolated contexts, reducing noise
2. **Skill Delegation**: Agents invoke skills that contain all business logic
3. **Thin Wrappers**: Each agent is < 85 lines - pure parameter routing

### Agent Types

| Agent | Purpose | Model |
|-------|---------|-------|
| java-implement-agent | Feature implementation | sonnet |
| java-implement-tests-agent | Test implementation | sonnet |
| java-fix-build-agent | Fix compilation errors | sonnet |
| java-fix-tests-agent | Fix test failures | sonnet |
| java-fix-javadoc-agent | Fix JavaDoc errors | haiku |
| java-refactor-agent | Code refactoring | sonnet |
| java-coverage-agent | Coverage analysis (read-only) | haiku |
| java-quality-agent | Quality analysis (read-only) | haiku |
| java-verify-agent | Standards verification (read-only) | haiku |

### Commands for Orchestration

Commands use the Task tool to coordinate multiple agents:

```
/java-analyze-all target=src/main/java/
    ├─> Task: java-quality-agent (parallel)
    ├─> Task: java-coverage-agent (parallel)
    └─> Task: java-verify-agent (parallel)

/java-full-workflow description="Add auth service"
    ├─> Task: java-implement-agent
    ├─> Task: java-fix-build-agent (if needed)
    ├─> Task: java-implement-tests-agent
    ├─> Task: java-fix-tests-agent (if needed)
    └─> Task: java-verify-agent
```

## Components

### Skills (5 skills with compound workflows)

1. **cui-java-core** - Core Java development standards
   - Workflow: Fix Compilation Errors (iterative)
   - Workflow: Implement Feature (with verification)
   - Standards: null safety, Lombok, logging, modern features

2. **cui-java-unit-testing** - Java unit testing standards
   - Workflow: Fix Test Failures (iterative)
   - Workflow: Implement Tests (with coverage)
   - Standards: JUnit 5, generators, value objects

3. **cui-javadoc** - JavaDoc documentation standards
   - Workflow: Fix JavaDoc Errors (iterative)
   - Standards: JavaDoc best practices, error reference

4. **cui-java-cdi** - CDI and Quarkus standards
   - Standards: CDI lifecycle, Quarkus native

5. **cui-java-maintenance** - Maintenance standards
   - Standards: refactoring, code quality

### Agents (9 autonomous agents)

**Execution Agents** (modify code):
- java-implement-agent - Implement features
- java-implement-tests-agent - Write tests
- java-fix-build-agent - Fix compilation
- java-fix-tests-agent - Fix tests
- java-fix-javadoc-agent - Fix documentation
- java-refactor-agent - Refactor code

**Analysis Agents** (read-only):
- java-coverage-agent - Coverage analysis
- java-quality-agent - Quality analysis
- java-verify-agent - Standards verification

### Commands (6 orchestration commands)

**Orchestration Commands** (use Task tool):
- java-analyze-all - Parallel analysis agents
- java-full-workflow - Complete implement→test→verify
- java-create - Interactive wizard

**Specialized Commands** (complex workflows):
- java-enforce-logrecords - Logging enforcement
- java-maintain-logger - Logger maintenance
- java-optimize-quarkus-native - Native optimization

## Installation

```bash
/plugin install cui-java-expert
```

## Usage Examples

### Quick Analysis

```
/java-analyze-all target=src/main/java/auth/
```

### Full Feature Implementation

```
/java-full-workflow description="Add user authentication service" module=auth-service
```

### Interactive Creation

```
/java-create
```

### Direct Agent Invocation

Agents can be invoked via Task tool from other commands:

```
Task:
  subagent_type: cui-java-expert:java-implement-agent
  description: Implement feature
  prompt: |
    description="Add token validation"
    module=auth-service
```

## Bundle Statistics

- **Agents**: 9 (autonomous execution)
- **Commands**: 6 (orchestration)
- **Skills**: 5 (with 5 compound workflows)
- **Scripts**: 3+ (Python automation)

## Dependencies

- **builder-maven** - For Maven build operations (builder-maven-rules skill)
- Python 3 for automation scripts

## Support

- Repository: https://github.com/cuioss/cui-llm-rules
- Bundle: marketplace/bundles/cui-java-expert/
