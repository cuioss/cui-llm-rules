# Documentation Rules Verification

## Command: cp: verify llm-rules

### Purpose
Verifies all documentation against the rules defined in [Documentation Management](../../documentation-management.md).

### Process Steps

1. Pre-Update Consultation
   - Review [Documentation Management](../../documentation-management.md) rules
   - Verify complete understanding of current rules
   - Present any unclear rules to user with numbered options

2. Document Structure Verification
   - Verify directory organization:
     * `/cascade/commands/` for command documentation
     * `/maintenance/` for process documentation
     * `/core/standards/` for fundamental standards
   - Check each document contains:
     * Clear purpose statement
     * Related documentation references
     * Process steps (if applicable)
     * Success criteria (if applicable)

3. Cross-Reference Verification
   - Verify all references use markdown links
   - Check all links exist and are valid
   - Confirm all references use relative paths
   - Update any outdated references

4. Information Modularization Check
   - Identify any duplicated information
   - Present consolidation options to user
   - Update references after consolidation
   - Verify information is properly linked

5. Documentation Completeness
   For each document:
   - [ ] Clear purpose statement exists
   - [ ] Related documentation properly linked
   - [ ] Process steps included if applicable
   - [ ] Success criteria defined if applicable
   - [ ] All references use markdown links
   - [ ] No information duplication
   - [ ] Proper directory location

### Success Criteria
1. All documents follow required structure
2. All references use proper markdown links
3. No broken links exist
4. Directory structure is maintained
5. Information is properly modularized
6. No duplicated information exists
7. All documents are complete

### Error Prevention
1. Always consult documentation-management.md first
2. Use systematic verification process
3. Present options to user when in doubt
4. Document all changes and decisions
5. Maintain audit trail of significant decisions

## See Also
- [Documentation Management](../../documentation-management.md): Documentation management rules
- [Documentation Standards](../../../core/standards/documentation-standards.md): Documentation standards
