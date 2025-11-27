# Plan Verify Workflow

## Phase Overview

The verify phase ensures implementation quality:

```
Implementation from Implement Phase
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ VERIFY PHASE                                        │
│                                                     │
│   1. Run full build (maven/npm)                     │
│   2. Code quality checks (lint, static analysis)    │
│   3. Manual testing validation                      │
│   4. Documentation review                           │
│   5. Acceptance criteria final verification         │
│   6. Transition to finalize phase                   │
└─────────────────────────────────────────────────────┘
        │
        ▼
    Finalize Phase
```

## Standard Tasks

| Task | Goal | Key Checks |
|------|------|------------|
| Run Full Build | Code compiles, tests pass | Build successful, coverage ≥80% |
| Code Quality | Meets quality standards | No critical violations, gates passed |
| Manual Testing | Functionality works | Happy path, edge cases, error handling |
| Documentation | Docs complete | JavaDoc/JSDoc, README, ADR/interface |

## Build Verification

### Maven
```
Task: builder:maven-builder
- mvn clean verify
- Report test results
- Report coverage
- Fail on test failures
```

### npm
```
Task: builder:npm-builder
- npm run build
- npm test
- Report coverage
- Fail on test failures
```

## Quality Analysis

### Java
```
Task: cui-java-expert:java-quality-agent
- Run checkstyle
- Run PMD/SpotBugs
- Report violations
- Categorize by severity
```

### JavaScript
```bash
npm run lint
```

### Sonar Integration
```
mcp__sonarqube__search_sonar_issues_in_projects
  projects: [{project-key}]
  pullRequestId: {pr-id}
```

## Manual Testing Checklist

### Happy Path Tests
- Primary user flows
- Expected inputs produce expected outputs
- Integration points work correctly

### Edge Cases
- Boundary values
- Empty/null inputs
- Maximum size inputs

### Error Handling
- Invalid inputs rejected gracefully
- Error messages are helpful
- Recovery from errors works

## Documentation Verification

### Code Documentation
- JavaDoc/JSDoc coverage for public APIs
- All parameters documented
- Return values described
- Examples where helpful

### Project Documentation
- README updated with new features
- Configuration documented
- API documentation current

### Architecture Documentation
- ADRs complete for decisions made
- Interface specs match implementation
- Diagrams updated if needed

## Quality Thresholds

| Metric | Threshold |
|--------|-----------|
| Test Coverage | ≥80% |
| Critical Violations | 0 |
| Blocker Sonar Issues | 0 |
| Build Status | Passing |
| Documentation | Complete |
