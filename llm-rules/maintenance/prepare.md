# Java Maintenance Preparation

## Command: cp: maintenance java prepare

### Purpose
Prepares a project for maintenance by setting up the environment and running initial verifications.

## Related Documentation
- [Progress Standards](../core/standards/progress-standards.md): Progress tracking and phase management
- [Java Process](java/process.md): Java maintenance process
- [Build Requirements](java/build.md): Build configuration

### Process Steps

1. Progress Initialization
   - Initialize progress in `maintenance/progress/prepare.md`
   - Record start time and initial state
   - Set status to "In Progress"
   - Document current configuration
   See: [Progress Standards](../core/standards/progress-standards.md) for details

2. Initial Build and Verification
   - Update progress: "Build Verification"
   - Run `./mvnw clean verify`
   - If build fails:
     * Record error in progress file
     * Analyze build logs
     * Fix identified issues
     * Update progress with fixes
     * Commit fixes with descriptive message
     * Repeat until build succeeds
   - Record successful build in progress

3. Basic Modernization (Open Rewrite)
   - Update progress: "Basic Modernization"
   See: [Progress Standards](../core/standards/progress-standards.md) for details
   - Run `./mvnw -Prewrite-modernize rewrite:run`
   - Build verification:
     * Run `./mvnw clean verify`
     * Record any issues in progress
     * Fix build issues
     * Commit changes if any with message:
       "Modernize codebase using open-rewrite
       
       Applied rewrite-modernize profile changes"
   - Record modernization completion

4. Extended Cleanup (Open Rewrite)
   - Update progress: "Extended Cleanup"
   - Run `./mvnw -Prewrite-prepare-release rewrite:run`
   - Build verification:
     * Run `./mvnw clean verify`
     * Record any issues in progress
     * Fix build issues
     * Commit changes if any with message:
       "Prepare release using open-rewrite
       
       Applied rewrite-prepare-release profile changes"
   - Record cleanup completion

5. Progress Completion
   - Record end time
   - Document all changes made
   - Set status to "Completed"
   See: [Progress Standards](../core/standards/progress-standards.md) for details

### Success Criteria
- Project builds successfully
- OpenRewrite modernization applied
- All changes committed
- No pending build issues
- Progress tracking complete and archived

## See Also
- [Java Process](java/process.md): Java maintenance process
- [Build Requirements](java/build.md): Build configuration
- [Progress Standards](../core/standards/progress-standards.md): Progress tracking
