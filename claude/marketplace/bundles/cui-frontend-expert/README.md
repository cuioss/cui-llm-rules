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
│   ├── javascript-coverage-analyzer.md
│   └── jsdoc-violation-analyzer.md
└── commands/            # User utilities (Layer 2)
    ├── cui-js-implement-code.md
    ├── cui-js-implement-tests.md
    ├── cui-js-generate-coverage.md
    ├── cui-orchestrate-js-task.md
    ├── cui-js-refactor-code.md
    ├── cui-js-fix-jsdoc.md
    └── cui-js-enforce-eslint.md
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

### Analysis
- **javascript-coverage-analyzer** - Analyzes existing coverage reports (focused analyzer - no build execution)
- **jsdoc-violation-analyzer** - Analyzes JSDoc compliance and returns structured violation list (focused analyzer - no fixes)

## Commands (Layer 2: User Utilities)

### Self-Contained Implementation Commands
- **cui-js-implement-code** - Self-contained command for code implementation with verification and iteration
- **cui-js-implement-tests** - Self-contained command for test implementation with verification and iteration
- **cui-js-generate-coverage** - Coverage generation and analysis command

### Orchestration Commands
- **cui-orchestrate-js-task** - End-to-end task orchestration (implementation → testing → coverage)
- **cui-js-refactor-code** - Systematic refactoring with standards compliance verification

### Maintenance Commands
- **cui-js-fix-jsdoc** - Fix JSDoc errors and warnings systematically
- **cui-js-enforce-eslint** - Enforce ESLint standards by fixing violations

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
/cui-js-implement-code files="src/utils/validator.js" description="Implement email and phone validation"
```

### Implement Tests
```bash
/cui-js-implement-tests files="src/utils/validator.js" description="Implement comprehensive unit tests"
```

### Full Task Workflow
```bash
/cui-orchestrate-js-task files="src/services/auth.js" description="Implement JWT authentication service"
```
This orchestrates: implementation → tests → coverage verification

### Systematic Refactoring
```bash
/cui-js-refactor-code scope=modernize priority=high
```
Modernizes JavaScript codebase (var → const/let, callbacks → async/await, etc.)

### Fix JSDoc Issues
```bash
/cui-js-fix-jsdoc files="src/**/*.js"
```

### Enforce ESLint
```bash
/cui-js-enforce-eslint fix-mode=auto
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
| java-coverage-analyzer | javascript-coverage-analyzer | Coverage analysis |
| cui-log-record-documenter | jsdoc-violation-analyzer | Documentation analysis |
| java-implement-code | cui-js-implement-code | Self-contained implementation |
| java-implement-tests | cui-js-implement-tests | Self-contained testing |
| java-coverage-report | cui-js-generate-coverage | Coverage generation/analysis |
| cui-orchestrate-java-task | cui-orchestrate-js-task | End-to-end orchestration |
| cui-java-refactor-code | cui-js-refactor-code | Systematic refactoring |
| cui-java-fix-javadoc | cui-js-fix-jsdoc | Documentation fixing |
| cui-java-maintain-logger | cui-js-enforce-eslint | Standards enforcement |

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
   /cui-js-implement-code files="..." description="..."
   ```

3. **Orchestrate workflows** with task manager:
   ```
   /cui-orchestrate-js-task files="..." description="..."
   ```

## Related Bundles

- **cui-java-expert** - Java/Maven development (parallel structure)
- **cui-maven** - Maven build and dependency management
- **cui-documentation-standards** - AsciiDoc and technical documentation
- **cui-workflow** - Git workflow and task management

---

*Part of the CUI Development Standards marketplace architecture*
