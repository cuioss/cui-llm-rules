# Version Control Standards

## Purpose
Defines comprehensive standards for version control, including commit policies, branching strategies, and automated operations.

## Related Documentation
- core/standards/project-standards.md: Project standards and technology stack
- standards/documentation/general-standard.md: General documentation standards
- standards/documentation/javadoc-standards.md: Javadoc standards
- standards/documentation/javadoc-maintenance.md: Javadoc maintenance
- core/standards/quality-standards.md: Quality standards
- maintenance/java/process.md: Java maintenance process

## Commit Standards

### 1. Commit Message Format
- Clear and descriptive subject line
- Detailed body explaining changes
- Reference related issues or tickets
- Document any breaking changes
- Include context for future reference

### 2. Commit Content
- Single logical change per commit
- Complete and self-contained changes
- All tests passing
- Documentation updated
- No unrelated changes

### 3. Tracking File Exception
- Changes to tracking/progress files alone do not require commits
- This applies specifically to files under maintenance/progress/
- Include tracking file changes with related code commits
- Exception cases requiring commits:
  * Major milestone completions
  * Phase transitions
  * Critical status updates needing preservation

### 4. Automated Commit Policy

#### Core Requirements
1. Automatic commits ONLY allowed when:
   - Task is executing within a Cascade Prompt
   - Cascade Prompt is defined in README.adoc
2. All other scenarios require explicit user confirmation

#### Verification Process
1. Check Current Context:
   - Verify task is part of Cascade Prompt
   - Confirm prompt source is README.adoc

2. Decision Making:
   - Both conditions met → proceed with automatic commit
   - Either condition not met → require user confirmation

3. Documentation:
   - Include reference to originating Cascade Prompt
   - Document any policy deviations

#### Scope
- All cuioss organization repositories
- All repository branches
- All code and documentation changes

#### Compliance
1. Document all Cascade Prompts in README.adoc
2. Reference originating prompt in automated commits
3. Obtain user confirmation for changes outside prompts

## Branching Strategy

### 1. Branch Types
1. Main Branches:
   - main/master: Production code
   - develop: Integration branch

2. Supporting Branches:
   - feature/*: New features
   - bugfix/*: Bug fixes
   - release/*: Release preparation
   - hotfix/*: Production fixes

### 2. Branch Naming
- Use descriptive names
- Include issue/ticket references
- Follow pattern: type/description
- Use lowercase and hyphens

### 3. Branch Management
1. Creation:
   - Branch from appropriate source
   - Use correct branch type
   - Include relevant metadata

2. Maintenance:
   - Regular synchronization
   - Clean up merged branches
   - Document branch purpose

## Code Review Standards

### 1. Review Requirements
- All changes require review
- Automated checks must pass
- Documentation must be complete
- Tests must be included

### 2. Review Process
1. Preparation:
   - Complete change documentation
   - Run all tests
   - Update related docs
   - Self-review changes

2. Review Checklist:
   - Code quality
   - Test coverage
   - Documentation updates
   - Security considerations
   - Performance impact

3. Approval Process:
   - Required reviewers
   - Resolution of comments
   - Final verification
   - Merge authorization

## Version Control Best Practices

### 1. Repository Management
1. Structure:
   - Clear directory organization
   - Consistent file naming
   - Proper gitignore rules
   - Documentation in place

2. Maintenance:
   - Regular cleanup
   - Archive old branches
   - Update documentation
   - Verify configurations

### 2. Workflow Standards
1. Daily Operations:
   - Regular commits
   - Descriptive messages
   - Branch synchronization
   - Local testing

2. Release Process:
   - Version tagging
   - Release notes
   - Documentation updates
   - Deployment verification

## Success Criteria

### 1. Commit Quality
- Clear and descriptive messages
- Single logical changes
- Proper documentation
- Passing tests
- Policy compliance

### 2. Branch Management
- Proper branch usage
- Clear naming convention
- Regular maintenance
- Clean history

### 3. Process Compliance
- Documented workflows
- Consistent practices
- Regular reviews
- Policy adherence

## See Also
- core/standards/project-standards.md: Project standards
- standards/documentation/general-standard.md: General documentation standards
- standards/documentation/javadoc-standards.md: Javadoc standards
- standards/documentation/javadoc-maintenance.md: Javadoc maintenance
- core/standards/quality-standards.md: Quality standards
- maintenance/java/process.md: Java maintenance process
