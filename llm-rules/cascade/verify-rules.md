# LLM Rules Verification

## Command: [8] cp: verify llm-rules

### Purpose
Ensures completeness and consistency of the LLM rules documentation by performing systematic verification.

### Process Steps

1. Structure Verification
   - Check directory structure:
     ```
     /llm-rules/
     ├── README.adoc
     ├── cascade/
     │   ├── cp.md
     │   ├── commands.md
     │   ├── verify-rules.md
     │   ├── persist-memory-to-llm-rules.md
     │   └── commit-llm-rules-to-memory.md
     ├── core
     │   └── standards
     │       └── project-standards.md
     ├── maintenance/
     │   ├── prepare.md
     │   ├── java.md
     │   ├── sonar.md
     │   ├── finalize.md
     │   └── documentation/
     │       └── javadoc.md
     ├── logging.md
     ├── testing.md
     ├── documentation.md
     ├── technologies.md
     ├── project.md
     └── commit-policy.md
     ```

2. Cross-Reference Check
   For each command in README.adoc and commands.md:
   - Verify corresponding implementation file exists
   - Check all referenced files are present
   - Validate all links are functional
   - Ensure documentation paths are correct
   - Verify command descriptions match between files

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

   a. Cascade Commands:
      - cp.md:
        - [ ] Command prompt interface
        - [ ] Command selection process
        - [ ] Error handling
        - [ ] User feedback

      - commands.md:
        - [ ] Complete command listing
        - [ ] Correct categorization
        - [ ] Command descriptions
        - [ ] Usage instructions

      - persist-memory-to-llm-rules.md:
        - [ ] Memory persistence process
        - [ ] Documentation update steps
        - [ ] Validation requirements
        - [ ] Success criteria

      - commit-llm-rules-to-memory.md:
        - [ ] Memory creation process
        - [ ] Documentation transfer steps
        - [ ] Validation requirements
        - [ ] Success criteria

   b. Maintenance Commands:
      - prepare.md:
        - [ ] Branch creation steps
        - [ ] Initial verification
        - [ ] Context setup
        - [ ] Success criteria

      - java.md:
        - [ ] Code standards update
        - [ ] Test coverage improvement
        - [ ] Documentation enhancement
        - [ ] Dependency constraints

      - sonar.md:
        - [ ] Quality gate review
        - [ ] Issue examination
        - [ ] Coverage verification
        - [ ] Integration points

      - finalize.md:
        - [ ] Code cleanup steps
        - [ ] Build verification
        - [ ] Documentation check
        - [ ] Success criteria

      - documentation/javadoc.md:
        - [ ] Error fixing process
        - [ ] Content preservation
        - [ ] Quality improvements
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
7. Command descriptions consistent across all files

### Error Prevention
1. Always compare against previous version
2. Use structured verification process
3. Maintain verification history
4. Document all exceptions
5. Regular completeness checks
6. Verify command consistency between README.adoc and commands.md
