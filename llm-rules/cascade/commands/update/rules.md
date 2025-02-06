# Documentation Rules Update

## Command: cp: update llm-rules

### Purpose
Interactively updates or creates documentation according to the rules defined in [Documentation Management](../../documentation-management.md).

### Process Steps

1. Rule Consultation
   - Review latest rules from [Documentation Management](../../documentation-management.md)
   - Identify applicable documentation standards
   - Note critical requirements and constraints
   - Verify understanding of documentation structure

2. Context Analysis
   - If user provides specific update request:
     * Analyze provided context
     * Identify affected documentation areas
     * Note specific requirements
   - If no specific request:
     * Prompt user for documentation topic
     * Request key information points
     * Clarify scope and purpose

3. Document Identification
   - Search for existing documentation on topic
   - If existing document found:
     * Analyze current content
     * Identify sections needing updates
     * Note cross-references
     * Preserve valuable information
   - If new topic:
     * Determine appropriate location
     * Identify related documents
     * Plan cross-references
     * Create document structure

4. Interactive Refinement
   - Present initial understanding to user
   - Request clarification on ambiguous points
   - Confirm key aspects:
     * Document purpose
     * Core content
     * Related documentation
     * Cross-references
   - Iterate until complete clarity achieved

5. Verification Before Persistence
   - Confirm complete understanding of:
     * Document purpose
     * Required content
     * Document structure
     * Cross-references
     * Integration points
   - Present final plan to user
   - Get explicit confirmation

6. Documentation Update
   - Only proceed when understanding is complete
   - Create or update document
   - Add all required sections
   - Include proper cross-references
   - Follow documentation standards
   - Verify against rules

### Success Criteria
1. Clear understanding achieved
2. User confirmation obtained
3. Documentation follows all rules
4. Cross-references properly maintained
5. Information properly modularized
6. No ambiguities remain
7. Changes properly persisted

### Error Prevention
1. Always consult documentation-management.md first
2. Never proceed with ambiguous understanding
3. Get explicit user confirmation
4. Verify all cross-references
5. Double-check document location

## See Also
- [Documentation Management](../../documentation-management.md): Documentation management rules
- [Documentation Standards](../../../core/standards/documentation-standards.md): Documentation standards
- [Rules Verification](../verify/rules.md): Documentation verification
