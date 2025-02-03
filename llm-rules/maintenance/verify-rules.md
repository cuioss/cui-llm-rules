# LLM Rules Verification

## Command: cp: verify llm-rules

### Purpose
Ensures completeness and consistency of the LLM rules documentation by performing systematic verification.

### Process Steps

1. Structure Verification
   - Check directory structure:
     ```
     /llm-rules/
     ├── README.adoc
     ├── maintenance/
     │   ├── prepare.md
     │   ├── java.md
     │   ├── sonar.md
     │   ├── finalize.md
     │   └── verify-rules.md
     ├── logging.md
     ├── testing.md
     ├── documentation.md
     ├── technologies.md
     ├── project.md
     └── commit-policy.md
     ```

2. Cross-Reference Check
   For each command in README.adoc:
   - Verify corresponding implementation file exists
   - Check all referenced files are present
   - Validate all links are functional
   - Ensure documentation paths are correct

3. Command Documentation Completeness
   For each command file, verify presence of:
   - Purpose statement
   - Process steps with detailed substeps
   - Error handling procedures
   - Success criteria
   - Integration points (if applicable)
   - Command-specific constraints

4. Content Verification Checklist
   For each documentation file:
   - [ ] Purpose clearly stated
   - [ ] All sections from original source covered
   - [ ] No information loss from previous versions
   - [ ] Consistent terminology used
   - [ ] Clear step-by-step procedures
   - [ ] Error scenarios documented
   - [ ] Success criteria defined
   - [ ] Dependencies and constraints listed
   - [ ] Integration points specified
   - [ ] Examples provided where needed

5. Command-Specific Verification

   a. prepare.md:
      - [ ] Build verification steps
      - [ ] OpenRewrite modernization
      - [ ] Error handling
      - [ ] Success criteria

   b. java.md:
      - [ ] Progress tracking
      - [ ] Project analysis
      - [ ] Module-by-module steps
      - [ ] Package-level maintenance
      - [ ] API stability constraints
      - [ ] Dependency constraints

   c. sonar.md:
      - [ ] Access setup
      - [ ] Quality gate review
      - [ ] Issue analysis
      - [ ] Coverage review
      - [ ] Security assessment
      - [ ] Integration points

   d. finalize.md:
      - [ ] Precondition verification
      - [ ] OpenRewrite cleanup
      - [ ] Build verification
      - [ ] Change management
      - [ ] Success criteria

6. Version Control
   - Document last verification date
   - Record changes made during verification
   - Track documentation versions
   - Note any deviations or exceptions

### Integration Requirements

1. Regular Verification Points
   - After any documentation update
   - Before major releases
   - During maintenance cycles
   - When importing external changes

2. Change Management
   - Document all changes
   - Update modification timestamps
   - Maintain change history
   - Track documentation versions

### Success Criteria
1. All files present and properly structured
2. All commands fully documented
3. No information loss from previous versions
4. All cross-references valid
5. All checklists completed
6. Version information current

### Error Prevention
1. Always compare against previous version
2. Use structured verification process
3. Maintain verification history
4. Document all exceptions
5. Regular completeness checks
