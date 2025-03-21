# Testing Standards

> **Note:** This document has been migrated to the standards directory. Please refer to the [Testing Core Standards](/standards/testing/core-standards.adoc) for the current version.

## Migration Notice
The detailed testing standards have been migrated to the standards directory in AsciiDoc format. Please refer to the following documents for the current standards:

- [Testing Core Standards](/standards/testing/core-standards.adoc)
- [Logging Testing Standards](/standards/testing/logging-testing.adoc)
- [Logging Testing Guide](/standards/logging/testing-guide.adoc)

## Core Testing Principles

### 1. Test Coverage
- All public methods must have unit tests
- All business logic must have appropriate test coverage
- Edge cases and error conditions must be tested
- Test coverage should aim for at least 80% line coverage

### 2. Test Independence
- Tests must be independent and not rely on other tests
- Tests must not depend on execution order
- Tests must clean up after themselves
- Tests must not have side effects that affect other tests

### 3. Test Clarity
- Test names must clearly describe what is being tested
- Test methods should follow the Arrange-Act-Assert pattern
- Each test should test one specific behavior
- Comments should explain complex test setups or assertions

### 4. Test Maintenance
- Tests must be maintained alongside production code
- Failing tests must be fixed promptly
- Tests should be refactored when production code changes
- Test code should follow the same quality standards as production code

## Test Types

### 1. Unit Tests
- Focus on testing a single unit of code in isolation
- Mock or stub dependencies
- Should be fast and lightweight
- Should cover all code paths

### 2. Integration Tests
- Test interaction between components
- May use real dependencies or test doubles
- Should verify correct integration behavior
- Should be isolated from external systems when possible

### 3. System Tests
- Test the entire system end-to-end
- May interact with external systems
- Should verify business requirements
- Should be comprehensive but focused

## Success Criteria
1. All tests pass consistently
2. Test coverage meets or exceeds targets
3. Tests are maintainable and clearly documented
4. Tests accurately verify system behavior
