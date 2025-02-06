# Java Build Requirements

## Purpose
Defines build requirements and standards for Java maintenance tasks.

## Related Documentation
- [Project Standards](../../core/standards/project-standards.md): Project standards and technology stack
- [Documentation Standards](../../core/standards/documentation-standards.md): Documentation standards
- [Java Process](process.md): Java maintenance process
- [Java Constraints](constraints.md): Java maintenance constraints

## Core Build Requirements

### Maven Wrapper Usage
1. ALWAYS use Maven wrapper ('./mvnw')
2. Run complete module build after each change
3. Create local commit after each successful build
4. Never cd into module directories
5. Maintain consistent build context

### Build Command Structure
1. Full Project Build:
   ```bash
   ./mvnw clean verify
   ```

2. Module-Specific Build:
   ```bash
   ./mvnw clean verify -pl :module-artifactId
   ```
   - Use '-pl' parameter for module selection
   - Execute from project root directory
   - Include necessary parameters

3. Test Execution:
   ```bash
   ./mvnw test
   ```

### Build Parameters
1. Required Parameters:
   - clean: Ensure clean build
   - verify: Run full verification
   - -pl: Module selection (if needed)

2. Optional Parameters:
   - -rf: Resume from module
   - -DskipTests: Skip tests (use with caution)
   - -Pjavadoc: Enable Javadoc generation

## Build Optimization

### Multi-Module Projects
1. Resume Build:
   - Use `-rf :module-name` to resume from specific module
   - Only build affected module and downstream dependencies
   - Example: `./mvnw clean verify -rf :module-name`

2. Module Dependencies:
   - Understand module relationships
   - Build in correct order
   - Respect dependency chain

### Build Sequence
1. Core Rules:
   - Verify all tests pass before commit
   - Keep commits atomic and focused
   - Run up to 5 consecutive builds maximum without user interaction
   - Document build failures

2. Build Order:
   - Start with clean verify
   - Add module selection if needed
   - Include additional parameters as required
   - Verify documentation if changed

## Build Verification

### Success Criteria
1. Build Success:
   - All modules compiled
   - All tests passed
   - No compilation errors
   - No test failures

2. Quality Gates:
   - Code coverage met
   - Style checks passed
   - Documentation complete
   - No critical issues

### Error Handling
1. Build Failures:
   - Document error details
   - Analyze root cause
   - Fix issues systematically
   - Verify fix with clean build

2. Test Failures:
   - Record test details
   - Document failure scenario
   - Fix test or code
   - Run full test suite

## Detailed Build Requirements

### 1. Maven Wrapper Usage
- Always use mvnw wrapper
- Run from project root directory
- Never use direct maven commands
- Verify wrapper is present and executable

### 2. Build Command Structure
- Module-specific builds:
  ```bash
  ./mvnw clean verify -pl modules/path/to/module -am
  ```
- Documentation generation:
  ```bash
  ./mvnw javadoc:javadoc -pl modules/path/to/module
  ```
- Full project build:
  ```bash
  ./mvnw clean verify
  ```

### 3. Build Optimization
- Use -pl for module-specific builds
- Always include -am for dependencies
- Run from project root
- Check exit codes
- Document warnings

### 4. Error Handling
- Verify build success before proceeding
- Document any build failures
- Fix warnings before completion
- Check for dependency issues
- Ensure clean builds

### 5. Quality Requirements
- All tests must pass
- Follow [SonarCloud Integration](../../maintenance/sonar.md) for quality analysis
- No critical issues
- Documentation complete
- Standards followed

### 6. Success Criteria
- Clean build output
- All tests passing
- Quality gates passed (see [SonarCloud Integration](../../maintenance/sonar.md))
- No unresolved warnings
- Documentation verified

## See Also
- [Java Process](process.md): Java maintenance process
- [Java Constraints](constraints.md): Java maintenance constraints
- [Project Standards](../../core/standards/project-standards.md): Project standards
- [Quality Standards](../../core/standards/quality-standards.md): Quality standards
