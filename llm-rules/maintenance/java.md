# Java Maintenance

## Command: cp: execute java maintenance

### Purpose
Executes standardized Java maintenance tasks while preserving API stability and dependency constraints.

### Critical Constraints
- API Stability:
  * Must preserve existing public API
  * No changes to method signatures
  * No changes to class hierarchies
  * No changes to package structure
  * No removal or modification of public methods
  * No changes to method return types or parameters
   
- Dependency Management:
  * No new dependencies may be added
  * This constraint takes precedence over CUI standards
  * Must work within existing dependency set
  * Cannot add CUI dependencies if not already present

### Process Steps

1. Precondition Verification
   - Verify successful build with `./mvnw clean verify`
   - Check for uncommitted changes (must be none)

2. Progress Tracking Setup
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

4. Module-by-Module Maintenance
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
         - Refactor tests to CUI standards within constraints:
           * Use JUnit 5 if available
           * Use existing test utilities
           * Add @ParameterizedTest where possible
         - Enhance test coverage:
           * Error scenarios
           * Log levels
           * Edge cases
         - Build and verify
         - Commit with descriptive message

      2. Code Refactoring Phase
         - Update progress: "Code Refactoring"
         - Apply CUI standards within constraints:
           * Use CuiLogger if available
           * Maintain API contracts
           * Enhance error handling
           * Use existing utilities
         - Build and verify
         - Commit with descriptive message

      3. Documentation Update Phase
         - Update progress: "Documentation Update"
         - Update to CUI standards:
           * Verify references
           * Add proper linking
           * Include test examples
           * Document parameters/returns
         - Build javadoc
         - Fix warnings/errors
         - Commit with descriptive message

      4. Package Completion
         - Mark package as complete
         - Record completed phases
         - Add completion timestamp

   c. Module Completion
      - Mark module as complete
      - Record timestamp
      - Update progress file

5. Process Completion
   - Update status to "Completed"
   - Add final timestamp
   - Archive progress file

### Success Criteria
- All modules processed
- All tests pass
- Documentation complete
- API stability maintained
- No new dependencies added
- Progress tracking complete
