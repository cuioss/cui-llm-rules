# Java Maintenance Process

## Purpose
Executes standardized Java maintenance tasks while preserving API stability and dependency constraints.

## Related Commands
- `cp: maintenance java prepare`: Initial setup
- `cp: maintenance java perform`: Core maintenance
- `cp: maintenance java finalize`: Completion tasks
- `cp: fix javadoc`: Documentation fixes

## Related Documentation
- project.md: Project standards
- technologies.md: Technology stack
- maintenance/javadoc.md: Documentation standards
- maintenance/sonar.md: Quality analysis
- logging.md: Logging standards and implementation
- maintenance/progress-tracking.md: Defines the progress tracking 

## Critical Constraints

### API Stability
- Must preserve existing public API
- No changes to method signatures
- No changes to class hierarchies
- No changes to package structure
- No removal or modification of public methods
- No changes to method return types or parameters
   
### Dependency Management
- No new dependencies may be added
- This constraint takes precedence over CUI standards
- Must work within existing dependency set
- Cannot add CUI dependencies if not already present

## Process Steps

1. Precondition Verification
   - Verify successful build with `./mvnw clean verify`
   - Check for uncommitted changes (must be none)

2. Progress Tracking Setup
   - Verify progress-tracking as defined within maintenance/progress-tracking.md
   - Check for existing java-maintenance.md
   - If exists:
     * Read current progress
     * Verify state matches (branch, module, package)
     * Resume from last successful step
   - If not exists:
     * Create new java-maintenance.md
     * Initialize with current timestamp
     * Set status to "In Progress"
     * Record current state

3. Project Analysis
   - Analyze overall project structure
   - Identify all modules
   - Document dependencies and relationships
   - Note areas needing special attention
   - Document current API surface
   - Review existing dependencies
   - Update progress file with module list

4. Build Requirements
   - ALWAYS use Maven wrapper ('./mvnw')
   - For module-specific builds:
     * Use '-pl' parameter
     * Format: './mvnw clean verify -pl :module-artifactId'
     * Execute from project root directory
   - Build command structure:
     * Start with clean verify
     * Add module selection if needed
     * Include additional parameters as required
   - Never cd into module directories
   - Maintain consistent build context

5. Module-by-Module Maintenance
   For each module:

   a. Module Analysis
      - Review module structure and purpose
      - Identify all Java packages
      - Document module-specific requirements
      - Map public API surface

   b. Package-Level Maintenance
      For each package:

      1. Test Refactoring Phase
         - Update progress: "Test Refactoring"
         - CRITICAL: Production code changes are strictly prohibited without explicit user confirmation
         - Any proposed production code changes must be accompanied by detailed reasoning including:
           * Clear problem statement
           * Impact analysis
           * Potential risks
           * Alternative solutions considered
         - Only proceed with production code changes after receiving explicit user approval
         - Refactor tests to CUI standards within constraints:
           * Use JUnit 5 if available
           * Use existing test utilities
           * Add @ParameterizedTest where possible
         - Enhance test coverage:
           * Error scenarios
           * Log levels
           * Edge cases
         - If stuck on fixing a unit test:
           * Define "stuck" as 3 consecutive failed builds
           * Stop work on the test
           * Provide user with:
             + Summary of the issue
             + List of attempted fixes
             + Current test state
           * Wait for user guidance before proceeding
         - Phase Completion Requirements:
           * All test classes migrated to JUnit 5
           * Descriptive test names added
           * Test organization improved
           * Code duplication removed
           * Logging assertions updated
           * Documentation improved
           * No deprecated APIs in test code
           * All tests passing
           * Code review completed
           * Changes documented in tracking file
         - Build and verify
         - Commit after each successful module build:
           * Verify all tests pass and build succeeds
           * Group related test changes
           * Use prefix "test(module-name):"
           * Include clear description and improvements
           * Reference tracking document
           * Ensure no unintended production code changes
         - Phase Transition:
           * Update phase history with completion timestamp
           * Verify all completion requirements met
           * Document phase completion in progress log
           * Clear approval for next phase

      2. Code Refactoring Phase
         - Update progress: "Code Refactoring"
         - Production code changes allowed with explicit approval
         - Changes must be:
           * Well-documented
           * Impact-assessed
           * Risk-evaluated
           * Backward-compatible
         - Priority 1: Update to CUI logging standards
           * See logging.md for comprehensive logging requirements and implementation details
         - Priority 2: Fix deprecated API usage:
           * Identify and replace deprecated methods, classes, and annotations
           * Ensure replacements maintain API compatibility
           * Document any required migration steps
         - Minimal Changes Policy:
           * Only make changes related to logging and deprecated APIs
           * Maintain existing API contracts and behavior
           * No refactoring of working code
           * No dependency updates unless required for deprecated API fixes
         - Phase Completion Requirements:
           * Static code analysis completed
           * Deprecated API usage identified
           * Improvement opportunities documented
           * Changes proposed and reviewed
           * Implementation patterns modernized
           * Documentation updated
           * Tests passing after changes
           * Migration guide created if needed
           * Code review completed
           * Changes documented in tracking file
         - Build and verify after each change
         - Commit changes separately:
           * Logging updates: prefix with "logging(module-name):"
           * API updates: prefix with "api(module-name):"
         - Phase Transition:
           * Update phase history with completion timestamp
           * Verify all completion requirements met
           * Document phase completion in progress log
           * Clear approval for next phase

      3. Documentation Phase
         - Update progress: "Documentation"
         - Update to CUI standards:
           * Verify references
           * Add proper linking
           * Include test examples
           * Document parameters/returns
         - Focus on documentation improvements:
           * Update all affected documentation
           * Create migration guides if needed
         - Phase Completion Requirements:
           * All public API documented
           * Migration guides complete
           * Release notes updated
           * Documentation reviewed
           * Changes documented in tracking file
         - Build javadoc
         - Fix warnings/errors
         - Commit with descriptive message

   c. Module Completion
      - Verify all packages completed
      - Update module status in tracking
      - Document any remaining issues
      - Mark module as complete
      - Record timestamp
      - Update progress file

6. Progress Tracking Requirements
   - Maintain detailed java-maintenance.md
   - For each phase:
     * Clear start and end timestamps
     * Explicit completion criteria
     * Verification checklist
     * Phase transition approval
   - Document all changes and decisions
   - Track progress at package level
   - Regular status updates in progress log
   - Clear phase transition markers

7. Phase Management
   - Each phase must have:
     * Clear entry criteria
     * Explicit completion requirements
     * Verification checklist
     * Transition approval process
   - Phase transitions require:
     * All completion criteria met
     * Documentation updated
     * Explicit approval
     * Timestamp recording

8. Process Completion
   - Update status to "Completed"
   - Verify all modules processed
   - Final documentation review
   - Comprehensive testing pass

## Success Criteria
1. Code Quality
   - All tests pass
   - Documentation complete
   - API stability maintained
   - No new dependencies added

2. Process Completion
   - All modules processed
   - Progress tracking complete
   - All commits properly documented
   - No critical issues pending

## See Also
- project.md: Project configuration
- technologies.md: Technology standards
- maintenance/javadoc.md: Documentation standards
- maintenance/sonar.md: Quality analysis
- logging.md: Logging standards
