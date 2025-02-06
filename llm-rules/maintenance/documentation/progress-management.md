# Progress and Phase Management

## Purpose
Defines comprehensive standards for tracking progress and managing phase transitions across maintenance tasks.

## Related Documentation
- maintenance/java.md: Java maintenance process
- maintenance/documentation/javadoc.md: Javadoc standards
- maintenance/prepare.md: Preparation process
- maintenance/finalize.md: Finalization process

## Core Standards

### 1. Phase Management

#### Phase Structure
1. Each maintenance phase must have:
   - Clear entry criteria
   - Explicit completion requirements
   - Verification checklist
   - Transition approval process

2. Phase-Specific Requirements

   a. Test Refactoring Phase
      - Entry Criteria:
        * Clean build state
        * No uncommitted changes
        * Clear test scope defined
      - Completion Requirements:
        * All test classes follow current standards
        * No deprecated APIs in test code
        * All tests passing
        * Documentation updated
        * Changes tracked

   b. Code Refactoring Phase
      - Entry Criteria:
        * Test phase completed
        * All tests passing
        * Clear refactoring scope
      - Completion Requirements:
        * Static analysis complete
        * Deprecated APIs addressed
        * Documentation updated
        * Tests passing
        * Changes tracked

   c. Documentation Phase
      - Entry Criteria:
        * Code changes complete
        * All tests passing
        * Clear documentation scope
      - Completion Requirements:
        * All public APIs documented
        * Migration guides complete
        * Release notes updated
        * Documentation reviewed

#### Phase Transitions
1. Requirements:
   - All completion criteria met and verified
   - Documentation updated
   - Explicit approval recorded
   - Timestamp recording

2. Verification Process:
   - Review completion checklist
   - Verify all requirements met
   - Document any exceptions
   - Get explicit approval

### 2. Progress Tracking

#### File Management
- Location: `/maintenance/progress/[command-name].md`
- Naming Convention: Simple command name (e.g., `prepare.md`, `java.md`)
- All progress files must be within the progress directory

#### File Structure
```markdown
# [Command Name] Progress

## Status
- Start Time: [ISO DateTime]
- Current Phase: [Phase Name]
- Overall Status: [Not Started|In Progress|Completed|Failed]

## Configuration
- Command: [Command Name]
- Module: [Current Module]
- Package: [Current Package]

## Phase History
1. [Phase Name]
   - Started: [Timestamp]
   - Completed: [Timestamp]
   - Status: [Complete/In Progress]
   - Focus: [Current Focus]

## Current State
- Branch: [Branch Name]
- Project: [Project Name]
- Active Phase: [Phase Name]
- Current Focus: [Package/Component]

## Progress Log
### [Timestamp] - [Phase]
- Action: [Description]
- Result: [Success|Failed|Pending]
- Details: [Additional Information]

## Phase Completion Checklist
[Phase Name] - [Status]
- [ ] Requirement 1
- [ ] Requirement 2

## Completion
- End Time: [ISO DateTime]
- Final Status: [Success|Failed]
- Summary: [Overview of changes]
```

### 3. Process Steps

#### Initialization
1. Check for existing progress file
   - Validate state matches current context
   - Resume from last successful step if exists
   - Create new file if not exists

2. Initial Setup
   - Record start time (ISO format)
   - Set initial state
   - Document configuration

#### Progress Updates
1. Phase Tracking
   - Record phase start time
   - Document current activity
   - Track dependencies
   - Update status

2. Error Handling
   - Document error details
   - Record recovery attempts
   - Track resolution steps
   - Update status
   - If phase requirements cannot be met:
     * Document blockers
     * Seek explicit guidance
     * Do not proceed to next phase
     * Update tracking file with status

#### Completion
1. Final Steps
   - Record end time
   - Document final status
   - Summarize all changes

2. Archival
   - Verify completeness
   - Archive progress file
   - Update references

## Integration Requirements

### 1. Command Integration
- Import at command start
- Initialize tracking
- Update at each phase
- Complete at command end

### 2. Error Integration
- Record all errors
- Track resolution steps
- Document recovery
- Update final status

### 3. Reporting Integration
- Generate summaries
- List completed phases
- Document open items
- Track time spent

## Success Criteria

### 1. File Management
- Progress file exists
- Correct directory location
- Proper file naming
- Complete structure

### 2. Content Quality
- All phases tracked
- Errors documented
- Clear status updates
- Complete summaries

### 3. Process Completion
- Final status recorded
- Changes documented
- Time tracking complete
- References updated

### 4. Phase Management
- All phase transitions documented
- Entry criteria met for each phase
- Completion requirements satisfied
- Proper approvals recorded

## Common Patterns

### 1. Phase Updates
```markdown
### [ISO DateTime] - [Phase Name]
- Action: Started [phase] processing
- Status: In Progress
- Details: [Specific context]
```

### 2. Error Records
```markdown
### [ISO DateTime] - Error in [Phase]
- Error: [Description]
- Impact: [Affected areas]
- Resolution: [Steps taken]
- Status: [Resolved|Pending]
```

### 3. Completion Records
```markdown
### [ISO DateTime] - Completion
- Status: [Success|Failed]
- Changes: [Summary]
- Duration: [Time taken]
- Next Steps: [If any]
```
