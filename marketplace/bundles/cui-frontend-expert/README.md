# CUI Frontend Expert

Frontend development standards and tools for CUI projects - modern JavaScript, CSS, and web development.

## Purpose

This bundle provides comprehensive frontend development expertise by aggregating eight foundational frontend skills with integrated automation workflows. All agent functionality has been absorbed into skill workflows with Python scripts for deterministic analysis.

## Components Included

### Skills (8 skills with workflows)

1. **cui-javascript** - Core JavaScript development standards
   - ES modules and modern patterns
   - Async programming and code quality
   - Best practices for CUI projects

2. **cui-javascript-unit-testing** - Jest unit testing standards
   - Configuration, test structure, testing patterns
   - Coverage requirements (80% threshold)
   - **Workflow: Analyze Coverage** - Parse Jest/Istanbul coverage reports

3. **cui-javascript-project** - Project structure and build standards
   - Directory layouts, package.json configuration
   - Dependency management, Maven integration
   - **Workflow: Parse npm Build Output** - Categorize build errors/warnings

4. **cui-jsdoc** - JSDoc documentation standards
   - Documentation patterns for functions, classes, modules
   - Web component documentation (Lit)
   - **Workflow: Analyze JSDoc Violations** - Detect documentation gaps

5. **cui-javascript-linting** - ESLint, Prettier, Stylelint configuration
   - Flat config setup and rule management
   - Build integration standards

6. **cui-javascript-maintenance** - JavaScript code maintenance standards
   - Refactoring patterns and priorities
   - Code quality metrics

7. **cui-cypress** - E2E testing with Cypress
   - Test organization and best practices
   - Build integration patterns

8. **cui-css** - CSS development standards
   - Responsive design patterns
   - Quality tooling and linting

### Scripts (3 automation scripts)

| Script | Location | Purpose |
|--------|----------|---------|
| `analyze-js-coverage.py` | cui-javascript-unit-testing | Parse Jest/Istanbul coverage reports |
| `analyze-jsdoc-violations.py` | cui-jsdoc | Detect JSDoc compliance violations |
| `parse-npm-output.py` | cui-javascript-project | Categorize npm build output |

### Commands (7 goal-based orchestrators)

1. **js-implement-code** - Self-contained command: implements code + verifies + iterates
2. **js-implement-tests** - Self-contained command: writes tests + runs tests + iterates
3. **js-generate-coverage** - Self-contained command: generates coverage + analyzes reports
4. **js-fix-jsdoc** - Fixes JSDoc violations systematically
5. **js-enforce-eslint** - Enforces ESLint standards by fixing violations
6. **js-maintain-tests** - Systematic test quality improvement
7. **js-refactor-code** - Systematic JavaScript refactoring with standards compliance

**Note**: For end-to-end JavaScript task orchestration (implementation -> testing -> coverage), use `/orchestrate-language language=javascript` from the cui-task-workflow bundle.

## Architecture

```
cui-frontend-expert/
├── commands/                # 7 goal-based orchestrators
│   ├── js-implement-code.md
│   ├── js-implement-tests.md
│   ├── js-generate-coverage.md
│   ├── js-fix-jsdoc.md
│   ├── js-enforce-eslint.md
│   ├── js-maintain-tests.md
│   └── js-refactor-code.md
└── skills/
    ├── cui-javascript/          # Core JS standards
    ├── cui-javascript-unit-testing/  # Testing + coverage workflow
    │   ├── SKILL.md             # Workflow: Analyze Coverage
    │   └── scripts/
    │       └── analyze-js-coverage.py
    ├── cui-javascript-project/  # Project + build workflow
    │   ├── SKILL.md             # Workflow: Parse npm Build Output
    │   └── scripts/
    │       └── parse-npm-output.py
    ├── cui-jsdoc/               # JSDoc + violations workflow
    │   ├── SKILL.md             # Workflow: Analyze JSDoc Violations
    │   └── scripts/
    │       └── analyze-jsdoc-violations.py
    ├── cui-javascript-linting/
    ├── cui-javascript-maintenance/
    ├── cui-cypress/
    └── cui-css/
```

## Workflow Pattern

Commands are thin orchestrators that invoke skill workflows:

```
/js-generate-coverage
  ├─> Bash: npm run test:coverage
  └─> Skill(cui-javascript-unit-testing) workflow: Analyze Coverage

/js-fix-jsdoc
  ├─> Skill(cui-jsdoc) workflow: Analyze JSDoc Violations
  ├─> [fixes via /js-implement-code]
  └─> Bash: npm run lint (verification)
```

## Usage Examples

### Coverage Analysis

```
/js-generate-coverage workspace=my-workspace
```

### JSDoc Fix

```
/js-fix-jsdoc files="src/**/*.js"
```

### ESLint Enforcement

```
/js-enforce-eslint fix-mode=auto
```

### Code Implementation

```
/js-implement-code files="src/utils/validator.js" description="Implement email validation"
```

## Bundle Statistics

- **Commands**: 7 (thin orchestrators)
- **Skills**: 8 (with integrated workflows)
- **Scripts**: 3 (Python automation)
- **Agents**: 0 (all absorbed into skill workflows)

## Dependencies

### Inter-Bundle Dependencies

- **cui-task-workflow** - For `/orchestrate-language` end-to-end orchestration

### External Dependencies

- Python 3 for automation scripts
- Node.js and npm for JavaScript builds

## License

Apache-2.0

## Support

- Repository: https://github.com/cuioss/cui-llm-rules
- Bundle: marketplace/bundles/cui-frontend-expert/
