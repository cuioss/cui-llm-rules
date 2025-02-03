# Prepare Project Maintenance

## Command: cp: prepare project maintenance

### Purpose
Prepares a project for maintenance by setting up the environment and running initial verifications.

### Process Steps

1. Progress Initialization
   - Initialize progress in `maintenance/prepare.md`
   - Record start time and initial state
   - Set status to "In Progress"
   - Document current configuration
   See: progress-tracking.md for details

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
   See: progress-tracking.md for details

### Success Criteria
- Project builds successfully
- OpenRewrite modernization applied
- All changes committed
- No pending build issues
- Progress tracking complete and archived
