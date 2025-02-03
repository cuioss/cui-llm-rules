# Finalize Java Maintenance

## Command: cp: finalize java maintenance

### Purpose
Completes the Java maintenance process by performing final cleanup and verification steps.

### Process Steps

1. Progress Initialization
   - Initialize progress in `maintenance/finalize.md`
   - Record start time and initial state
   - Set status to "In Progress"
   - Document current configuration
   See: progress-tracking.md for details

2. Precondition Verification
   - Update progress: "Precondition Check"
   - Verify successful build with `./mvnw clean verify`
   - Check for uncommitted changes (must be none)
   - Record verification results

   If any precondition fails:
   - Record failure in progress file
   - Report the specific failure
   - Provide guidance for resolution
   - Do not proceed until all conditions are met

3. Quality Gate Verification
   - Update progress: "Quality Gate Check"
   - Execute command: "cp: verify sonar"
   - Wait for completion
   - If verification fails:
     * Record failure in progress
     * Address identified issues
     * Repeat verification
   - Do not proceed until quality gates pass

4. OpenRewrite Cleanup
   - Update progress: "OpenRewrite Cleanup"
   - Execute: `./mvnw -Prewrite-prepare-release rewrite:run`
   - Record any changes made
   - Document cleanup results

5. Build Verification
   - Update progress: "Build Verification"
   - Run `./mvnw clean verify`
   - If build fails:
     * Record errors in progress
     * Analyze build logs
     * Fix identified issues
     * Document fixes applied
     * Repeat until build succeeds
   - Do not proceed if build cannot be fixed
   - Record successful build

6. Documentation Cleanup
   - Update progress: "Documentation Cleanup"
   - Execute command: "cp: fix javadoc"
   - Wait for completion
   - If fixes were applied:
     * Review changes
     * Verify documentation integrity
     * Record documentation updates

7. Change Management
   - Update progress: "Change Management"
   If OpenRewrite made changes:
   - Review changes for correctness
   - Document all modifications
   - Create descriptive commit message
   - Record changes in progress file
   - Commit all changes

8. Progress Completion
   - Record end time
   - Document all changes made
   - Set status to "Completed"
   See: progress-tracking.md for details

### Success Criteria
- All preconditions met
- OpenRewrite cleanup completed
- Build passes successfully
- Changes (if any) committed
- All code quality standards met
- Documentation is complete and accurate
- No unresolved issues remain
- Progress tracking complete and archived
