# Phase Management Rules

## Purpose
Defines standards and requirements for managing maintenance phase transitions and tracking progress.

## Core Rules

### Phase Structure
1. Each maintenance phase must have:
   - Clear entry criteria
   - Explicit completion requirements
   - Verification checklist
   - Transition approval process

### Phase Transitions
1. Phase transitions require:
   - All completion criteria met and verified
   - Documentation updated
   - Explicit approval recorded
   - Timestamp recording

### Progress Tracking
1. Maintain detailed tracking in java-maintenance.md
2. Each phase must record:
   - Clear start and end timestamps
   - Current status
   - Completed requirements
   - Pending items
   - Issues encountered

### Documentation Requirements
1. Phase History section must include:
   - Phase name
   - Start timestamp
   - Completion timestamp
   - Status (Complete/In Progress)
   - Focus area

### Verification Process
1. Before phase transition:
   - Review completion checklist
   - Verify all requirements met
   - Document any exceptions
   - Get explicit approval

### Phase-Specific Requirements

#### Test Refactoring Phase
1. Entry Criteria:
   - Clean build state
   - No uncommitted changes
   - Clear test scope defined

2. Completion Requirements:
   - All test classes follow current standards
   - No deprecated APIs in test code
   - All tests passing
   - Documentation updated
   - Changes tracked

#### Code Refactoring Phase
1. Entry Criteria:
   - Test phase completed
   - All tests passing
   - Clear refactoring scope

2. Completion Requirements:
   - Static analysis complete
   - Deprecated APIs addressed
   - Documentation updated
   - Tests passing
   - Changes tracked

#### Documentation Phase
1. Entry Criteria:
   - Code changes complete
   - All tests passing
   - Clear documentation scope

2. Completion Requirements:
   - All public APIs documented
   - Migration guides complete
   - Release notes updated
   - Documentation reviewed

## Implementation Guidelines

### Tracking File Structure
```markdown
## Status: [Current Status]
Started: [Timestamp]

### Phase History
1. [Phase Name]
   - Started: [Timestamp]
   - Completed: [Timestamp]
   - Status: [Complete/In Progress]
   - Focus: [Current Focus]

### Current State
- Branch: [Branch Name]
- Project: [Project Name]
- Active Phase: [Phase Name]
- Current Focus: [Package/Component]

### Phase Completion Checklist
[Phase Name] - [Status]
- [ ] Requirement 1
- [ ] Requirement 2
...

### Progress Log
- [Timestamp]: [Event/Update]
```

### Error Handling
1. If phase requirements cannot be met:
   - Document blockers
   - Seek explicit guidance
   - Do not proceed to next phase
   - Update tracking file with status
