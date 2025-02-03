# Fix Javadoc Rules

When asked to "cp: fix javadoc", follow these strict rules:

## 1. Preconditions
Verify all before proceeding:
- Project builds successfully: `./mvnw clean verify`
- No uncommitted changes exist in the repository

## 2. Verify Javadoc Generation
Use the appropriate command based on project type:
- Single module projects: `./mvnw clean verify -Pjavadoc`
- Multi-module projects: `./mvnw clean verify -Pjavadoc-mm-reporting`

## 3. Fix Strategy
- Fix ONLY Javadoc errors and warnings from the build
- Do NOT alter or improve documentation content
- Do NOT modify any code
- Make minimal modifications necessary to fix build issues
- Focus only on formatting, references, and tags

## 4. Common Fixes
- Fix invalid {@link} references
- Fix malformed HTML tags
- Fix missing/incorrect parameter documentation
- Fix missing/incorrect return value documentation
- Fix missing/incorrect exception documentation

## 5. Out of Scope
- Documentation improvements
- Code changes
- Content rewrites
- Style changes beyond error fixes

## 6. Progress Tracking
- Initialize progress in `maintenance/javadoc.md`
- Record start time and initial state
- Set status to "In Progress"
- Document current configuration
- Update progress file throughout the process
- Record end time and document all changes made
- Set status to "Completed"

## 7. Validation
- Verify all references exist
- No speculative features added
- Consistent terminology used
- Documentation structure maintained
- Changes are focused and minimal

**Note**: These strict rules only apply within the "cp: fix javadoc" context.

## Command: cp: fix javadoc

### Purpose
Fixes Javadoc build errors and warnings while preserving documentation content.

### Process Steps

1. Progress Initialization
   - Initialize progress in `maintenance/javadoc.md`
   - Record start time and initial state
   - Set status to "In Progress"
   - Document current configuration
   See: progress-tracking.md for details

2. Build Verification
   - Update progress: "Build Verification"
   - Run `./mvnw javadoc:javadoc`
   - If build fails:
     * Record errors in progress file
     * Categorize issues:
       - Missing tags
       - Invalid references
       - Formatting problems
     * Document error locations
   - Record verification results

3. Documentation Analysis
   - Update progress: "Documentation Analysis"
   - For each error:
     * Record issue details
     * Analyze context
     * Plan minimal fix
     * Document proposed changes
   - Record analysis completion

4. Fix Application
   - Update progress: "Fix Application"
   - For each documented issue:
     * Apply minimal fix
     * Verify no content loss
     * Run local javadoc check
     * Record changes made
   - Document all applied fixes

5. Final Verification
   - Update progress: "Final Verification"
   - Run `./mvnw javadoc:javadoc`
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
   See: progress-tracking.md for details

### Critical Constraints
- No content modifications
- Only fix format/structure
- Preserve existing documentation
- Minimal changes only

### Success Criteria
- All Javadoc errors fixed
- No content modifications
- Build passes successfully
- Changes committed
- Progress tracking complete
