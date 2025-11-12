# Test Quality Analysis Checklist

Comprehensive checklist for analyzing Java test quality and identifying improvement opportunities.

## Analysis Categories

### 1. AI Artifact Detection

Identify AI-generated code artifacts that should be cleaned:

- Method names exceeding 75 characters
- Excessive obvious comments that don't add value
- Verbose @DisplayName annotations
- Boilerplate AAA (Arrange-Act-Assert) comments

### 2. Unit Test Coverage Audit

Verify proper unit test organization:

- Each type has dedicated unit test focusing exclusively on that class
- Comprehensive corner case and edge case coverage
- No test duplication across unit tests

### 3. Forbidden Anti-Pattern Detection

Critical violations requiring immediate removal:

- **Conditional logic**: if-else, switch, ternary operators
- **Optional.orElse()** usage in assertions
- **try-catch blocks** in tests
- Missing assertThrows/assertDoesNotThrow for exception scenarios

### 4. Exception Handling Audit

Verify proper exception testing:

- Throws declarations for checked exceptions
- assertThrows usage for expected exceptions
- assertDoesNotThrow for explicit no-exception verification

### 5. Non-Sensible Test Review

Identify tests that should be removed:

- Meaningless constructor tests
- Framework behavior tests
- Getter/setter only tests without validation logic
- Reflection workarounds (CRITICAL - always indicates a bug)

### 6. CUI Framework Audit

Verify framework adoption:

- Manual data creation instead of Generators
- Missing @GeneratorsSource annotations
- Forbidden libraries: Mockito, Hamcrest, PowerMock

### 7. Value Object Review

Identify value objects needing contract testing:

- Objects with custom equals/hashCode implementations
- Domain data with value semantics
- Classes used in collections/maps
- Verify NO incorrect application to: enums, utilities, infrastructure objects

### 8. Test Duplication Detection

Find redundant test coverage:

- Multiple unit tests testing the same method
- Integration tests repeating unit test scenarios

### 9. Test Classification

Apply prioritization framework for targeted maintenance:

- **HIGH Priority**: Business logic, domain objects, API contracts, security components
- **MEDIUM Priority**: Value objects, configuration objects, domain enums
- **LOW Priority**: Infrastructure, HTTP clients, framework integration

### 10. Findings Documentation

Create structured report including:

- Test file inventory with priority classification
- Violations by category with counts
- Enhancement recommendations prioritized by impact
- Estimated effort per improvement category

## Usage in Commands

Reference this checklist when implementing test analysis:

```
Read: claude/marketplace/bundles/cui-java-expert/skills/cui-java-unit-testing/standards/test-quality-analysis-checklist.md

Execute comprehensive analysis following the 10-category checklist.
Apply priority filter: [priority parameter]
Return structured analysis report.
```

## Related Standards

- `testing-maintenance-reference.md` - Test improvement implementation patterns
- `test-quality-standards.md` - Core quality requirements
- `value-object-testing.md` - Value object contract patterns
