# CUI Frontend Expert

Frontend development standards and tools for CUI projects - modern JavaScript, CSS, and web development.

## Structure

```
cui-frontend-expert/
├── plugin.json
├── README.md
├── skills/              # Frontend standards (Layer 1)
│   ├── cui-javascript/
│   ├── cui-javascript-unit-testing/
│   ├── cui-javascript-linting/
│   ├── cui-javascript-project/
│   ├── cui-jsdoc/
│   ├── cui-css/
│   └── cui-cypress/
├── agents/              # Focused executors (Layer 3)
│   ├── npm-builder.md
│   ├── javascript-code-implementer.md
│   ├── javascript-coverage-analyzer.md
│   ├── javascript-test-implementer.md
│   └── jsdoc-violation-analyzer.md
└── commands/            # User utilities (Layer 2)
    ├── javascript-implement-code.md
    ├── javascript-implement-tests.md
    ├── javascript-coverage-report.md
    ├── cui-javascript-task-manager.md
    ├── cui-javascript-refactor.md
    ├── cui-jsdoc-fix.md
    └── cui-eslint-enforce.md
```

## Skills (Layer 1: Knowledge + Standards)

### Core JavaScript
- **cui-javascript** - Modern JavaScript patterns, async programming, code quality standards
- **cui-javascript-project** - Project structure, dependency management, Maven integration
- **cui-javascript-linting** - ESLint, Prettier, Stylelint configuration and standards

### Testing
- **cui-javascript-unit-testing** - Jest/Vitest patterns, coverage standards, test organization
- **cui-cypress** - E2E testing with Cypress, test organization, build integration

### Documentation & Styling
- **cui-jsdoc** - JSDoc documentation standards and patterns
- **cui-css** - CSS development standards, responsive design, quality tooling

## Agents (Layer 3: Focused Executors)

### Build Execution
- **npm-builder** - Central agent for npm/npx builds with output capture, issue categorization, performance tracking

### Code Implementation
- **javascript-code-implementer** - Implements modern JavaScript tasks with full standards compliance (focused executor - no verification)

### Test Implementation
- **javascript-test-implementer** - Implements Jest/Vitest tests with full standards compliance (focused executor - no verification)

### Analysis
- **javascript-coverage-analyzer** - Analyzes existing coverage reports (focused analyzer - no build execution)
- **jsdoc-violation-analyzer** - Analyzes JSDoc compliance and returns structured violation list (focused analyzer - no fixes)

## Commands (Layer 2: User Utilities)

### Self-Contained Implementation Commands
- **javascript-implement-code** - Self-contained command for code implementation with verification and iteration
- **javascript-implement-tests** - Self-contained command for test implementation with verification and iteration
- **javascript-coverage-report** - Coverage generation and analysis command

### Orchestration Commands
- **cui-javascript-task-manager** - End-to-end task orchestration (implementation → testing → coverage)
- **cui-javascript-refactor** - Systematic refactoring with standards compliance verification

### Maintenance Commands
- **cui-jsdoc-fix** - Fix JSDoc errors and warnings systematically
- **cui-eslint-enforce** - Enforce ESLint standards by fixing violations

## Architecture Pattern

This bundle follows the CUI marketplace three-layer architecture:

**Layer 1 (Skills)**: Self-contained standards with progressive loading
- All standards content in `skill/standards/` directory
- No external file references
- Conditional loading based on context

**Layer 2 (Commands)**: User-invoked orchestration utilities
- Orchestrate Layer 3 agents via Task tool
- Handle verification and iteration
- Make control flow decisions

**Layer 3 (Agents)**: Focused task executors
- Do ONE specific task
- Return results to Layer 2 caller
- NO Task delegation (agents cannot call other agents)
- NO build verification (agents implement/analyze only)

## Usage Examples

### Implement JavaScript Code
```bash
/javascript-implement-code files="src/utils/validator.js" description="Implement email and phone validation"
```

### Implement Tests
```bash
/javascript-implement-tests files="src/utils/validator.js" description="Implement comprehensive unit tests"
```

### Full Task Workflow
```bash
/cui-javascript-task-manager files="src/services/auth.js" description="Implement JWT authentication service"
```
This orchestrates: implementation → tests → coverage verification

### Systematic Refactoring
```bash
/cui-javascript-refactor scope=modernize priority=high
```
Modernizes JavaScript codebase (var → const/let, callbacks → async/await, etc.)

### Fix JSDoc Issues
```bash
/cui-jsdoc-fix files="src/**/*.js"
```

### Enforce ESLint
```bash
/cui-eslint-enforce fix-mode=auto
```

## Key Differences from cui-java-expert

### Build Tool
- **cui-java-expert**: maven-builder (Maven/Java builds)
- **cui-frontend-expert**: npm-builder (npm/npx builds)

### Testing Frameworks
- **cui-java-expert**: JUnit 5, test-generator framework
- **cui-frontend-expert**: Jest, Vitest, Cypress

### Documentation
- **cui-java-expert**: Javadoc with AsciiDoc patterns
- **cui-frontend-expert**: JSDoc with Markdown

### Standards
- **cui-java-expert**: Java core patterns, Lombok, CDI, Quarkus
- **cui-frontend-expert**: Modern JavaScript, async patterns, ES6+, web components

## Parallel Structure with cui-java-expert

| cui-java-expert | cui-frontend-expert | Purpose |
|----------------|---------------------|---------|
| maven-builder | npm-builder | Build execution |
| java-code-implementer | javascript-code-implementer | Code implementation |
| java-junit-implementer | javascript-test-implementer | Test implementation |
| java-coverage-analyzer | javascript-coverage-analyzer | Coverage analysis |
| cui-log-record-documenter | jsdoc-violation-analyzer | Documentation analysis |
| java-implement-code | javascript-implement-code | Self-contained implementation |
| java-implement-tests | javascript-implement-tests | Self-contained testing |
| java-coverage-report | javascript-coverage-report | Coverage generation/analysis |
| cui-java-task-manager | cui-javascript-task-manager | End-to-end orchestration |
| cui-java-refactor | cui-javascript-refactor | Systematic refactoring |
| cui-javadoc-fix | cui-jsdoc-fix | Documentation fixing |
| cui-logger-maintain | cui-eslint-enforce | Standards enforcement |

## Integration with Maven Projects

JavaScript frontend code is typically built within Maven projects using:
- frontend-maven-plugin for npm integration
- Generated artifacts in target/classes/static/ or similar
- Part of Maven build lifecycle

Skills include standards for Maven integration to ensure frontend code works within Maven-based Java projects.

## Getting Started

1. **Load a skill** to access standards:
   ```
   Skill: cui-javascript
   ```

2. **Use a command** for tasks:
   ```
   /javascript-implement-code files="..." description="..."
   ```

3. **Orchestrate workflows** with task manager:
   ```
   /cui-javascript-task-manager files="..." description="..."
   ```

## Related Bundles

- **cui-java-expert** - Java/Maven development (parallel structure)
- **cui-maven** - Maven build and dependency management
- **cui-documentation-standards** - AsciiDoc and technical documentation
- **cui-workflow** - Git workflow and task management

---

*Part of the CUI Development Standards marketplace architecture*
