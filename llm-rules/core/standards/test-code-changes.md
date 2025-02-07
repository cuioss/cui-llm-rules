# Test Code Changes

## Purpose
Defines standards and guidelines for making changes to test code while maintaining code quality and focus.

## Core Standards

### 1. Scope of Changes
1. Focus Rule:
   - When adapting test code (e.g., to new logging standards), changes must be strictly limited to the test-related modifications
   - DO NOT modify production code that is unrelated to the current task
   - DO NOT refactor or "improve" other aspects of the code while working on test changes
   - Each change should have a single, clear purpose

2. Examples:
   ```java
   // When updating tests for new logging standard
   
   // CORRECT - Only change logging related code
   - import static de.cuioss.portal.core.PortalCoreLogMessages.SERVLET;  // New import
   - assertLogMessagePresentContaining(TestLogLevel.WARN, SERVLET.WARN.USER_NOT_LOGGED_IN);  // Updated assertion
   
   // INCORRECT - Making unrelated changes
   - Refactoring test method names
   - Changing test data structures
   - Modifying production code formatting
   - Adding new test cases unrelated to logging
   ```

### 2. Implementation Guidelines
1. Change Strategy:
   - Identify all affected test files
   - Plan changes before implementation
   - Make changes systematically and consistently
   - Review changes to ensure they stay within scope

2. Documentation:
   - Document the specific purpose of test changes
   - Note any test-specific configurations or requirements
   - Keep commit messages focused on the test changes

### 3. Quality Assurance
1. Verification:
   - Run affected test suites
   - Verify only intended changes were made
   - Check for unintended side effects
   - Ensure test coverage remains consistent

2. Review Process:
   - Separate test changes from production code changes
   - Focus review on the specific test modifications
   - Verify no unrelated changes were included

## Success Criteria
1. Changes are strictly limited to the intended test modifications
2. No unrelated production code is modified
3. Test coverage and quality are maintained
4. Changes are well-documented and focused

## See Also
- core/standards/testing-standards.md: General testing standards
- core/standards/quality-standards.md: Quality standards
- core/standards/logging-standards.md: Logging standards
- maintenance/java/process.md: Java maintenance process
