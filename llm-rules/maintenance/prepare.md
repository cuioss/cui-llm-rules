# Java Maintenance Preparation

## Command: cp: maintenance java prepare

### Purpose
Prepares a project for maintenance by setting up the environment and running initial verifications.

## Related Documentation
- [Progress Standards](../core/standards/progress-standards.md): Progress tracking and phase management
- [Java Process](java/process.md): Java maintenance process
- [Build Requirements](java/build.md): Build configuration

### Commit Requirements
- Each phase must be committed separately with specific commit messages
- Commits must be made immediately after successful verification
- Never proceed to next phase without committing current changes

#### Required Commit Messages
1. Build Fixes (if needed):
   ```
   Fix build issues in preparation phase
   
   - List specific fixes made
   - Reference failing tests or modules
   ```

2. Modernization Changes:
   ```
   Modernize codebase using open-rewrite
   
   Applied rewrite-modernize profile changes
   - List specific improvements
   - Note any manual adjustments
   ```

3. Cleanup Changes:
   ```
   Prepare release using open-rewrite
   
   Applied rewrite-prepare-release profile changes
   - List specific improvements
   - Note any manual adjustments
   ```

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
     * Commit fixes with descriptive message (see Commit Requirements)
     * Repeat until build succeeds
   - Record successful build in progress
   - ⚠️ REQUIRED: Commit any changes before proceeding

3. Basic Modernization (Open Rewrite)
   - Update progress: "Basic Modernization"
   See: [Progress Standards](../core/standards/progress-standards.md) for details
   - Run `./mvnw -Prewrite-modernize rewrite:run`
   - Build verification:
     * Run `./mvnw clean verify`
     * Record any issues in progress
     * Fix build issues
   - ⚠️ REQUIRED: Commit changes using modernization commit message (see Commit Requirements)
   - Record modernization completion

4. Extended Cleanup (Open Rewrite)
   - Update progress: "Extended Cleanup"
   - Run `./mvnw -Prewrite-prepare-release rewrite:run`
   - Build verification:
     * Run `./mvnw clean verify`
     * Record any issues in progress
     * Fix build issues
   - ⚠️ REQUIRED: Commit changes using cleanup commit message (see Commit Requirements)
   - Record cleanup completion

5. Progress Completion
   - Record end time
   - Document all changes made
   - Set status to "Completed"
   See: [Progress Standards](../core/standards/progress-standards.md) for details

### Success Criteria
- Project builds successfully
- OpenRewrite modernization applied
- All changes committed with required messages
- Commits made at each phase completion
- No pending build issues
- Progress tracking complete and archived

### Common Mistakes to Avoid
1. Skipping commits after each phase
2. Using incorrect commit messages
3. Combining multiple phase changes in one commit
4. Proceeding to next phase before committing

## See Also
- [Java Process](java/process.md): Java maintenance process
- [Build Requirements](java/build.md): Build configuration
- [Progress Standards](../core/standards/progress-standards.md): Progress tracking
