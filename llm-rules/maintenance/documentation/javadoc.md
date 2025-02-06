# Javadoc Standards and Maintenance

## Purpose
Defines comprehensive standards for Javadoc documentation and maintenance procedures.

## Related Commands
- `cp: fix javadoc`: Documentation fixes
- `cp: maintenance java perform`: Core maintenance
- `cp: maintenance java finalize`: Completion tasks

## Related Documentation
- project.md: Project standards
- technologies.md: Technology stack
- maintenance/java.md: Java maintenance process

## Core Standards

### Documentation Requirements
1. All public APIs must be documented
2. All changes require successful javadoc build with zero errors/warnings
3. Only document existing code elements - no speculative features
4. Use consistent terminology:
   - Always use "Java beans" instead of "Jakarta beans"
   - Maintain "Java Bean Specification" terminology
   - Apply consistently across all documentation types

### Structure Requirements
1. Package Documentation
   - Overview section explaining purpose and scope
   - Key Components section listing main classes/interfaces
   - Usage Examples with actual code samples
   - Best Practices section with guidelines
   - Cross-references to related components
   - Author and version information

2. Class/Interface Documentation
   - Clear purpose description
   - Parameter descriptions with validation rules
   - Return value descriptions
   - Exception documentation
   - Usage examples from unit tests
   - Version information with @since tags
   - Thread-safety notes where applicable

3. Method Documentation
   - Precise description of functionality
   - Parameter validation rules
   - Return value guarantees
   - Exception conditions
   - Thread-safety notes where applicable

## Maintenance Process

### Critical Constraints
1. Content Preservation
   - Fix ONLY Javadoc errors and warnings from build
   - Do NOT alter or improve documentation content
   - Do NOT modify any code
   - Make minimal modifications necessary
   - Focus only on formatting, references, and tags

2. Common Fixes
   - Fix invalid {@link} references
   - Fix malformed HTML tags
   - Fix missing/incorrect parameter documentation
   - Fix missing/incorrect return value documentation
   - Fix missing/incorrect exception documentation

3. Out of Scope
   - Documentation improvements
   - Code changes
   - Content rewrites
   - Style changes beyond error fixes

### Process Steps

1. Preconditions
   - Verify project builds: `./mvnw clean verify`
   - Check for uncommitted changes
   - Initialize progress tracking

2. Build Verification
   - Run appropriate command:
     * Single module: `./mvnw clean verify -Pjavadoc`
     * Multi-module: `./mvnw clean verify -Pjavadoc-mm-reporting`
   - Record any errors in progress file
   - Categorize issues:
     * Missing tags
     * Invalid references
     * Formatting problems
   - Document error locations

3. Documentation Analysis
   - For each error:
     * Record issue details
     * Analyze context
     * Plan minimal fix
     * Document proposed changes
   - Record analysis completion

4. Fix Application
   - For each documented issue:
     * Apply minimal fix
     * Verify no content loss
     * Run local javadoc check
     * Record changes made
   - Document all applied fixes

5. Final Verification
   - Run appropriate javadoc command
   - If issues remain:
     * Record in progress file
     * Return to Fix Application
   - On success:
     * Record verification
     * Commit changes with message:
       "Fix Javadoc issues
       
       - Fixed missing tags
       - Corrected invalid references
       - Resolved formatting issues"

6. Progress Completion
   - Record end time
   - Document all changes made
   - Set status to "Completed"
   - Archive progress file

## Progress Tracking
1. Initialize Progress
   - Create/update progress file
   - Record start time and state
   - Document configuration

2. Track Changes
   - Update after each step
   - Record all modifications
   - Document any issues

3. Completion
   - Record end time
   - Document final state
   - Archive progress data

## Success Criteria
1. Build Success
   - All Javadoc errors fixed
   - Build passes successfully
   - No new issues introduced

2. Content Integrity
   - No content modifications
   - Documentation preserved
   - Only format fixes applied

3. Process Completion
   - Changes committed
   - Progress tracking complete
   - All steps documented

## See Also
- project.md: Project standards
- technologies.md: Technology stack
- maintenance/java.md: Java maintenance process
