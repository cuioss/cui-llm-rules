# Documentation Management Rules for @llm-rules

## Purpose
Defines the rules that must be followed when creating, updating, or deleting documents within @llm-rules.

## Related Documentation
- [Documentation Standards](../core/standards/documentation-standards.md)
- [Project Standards](../core/standards/project-standards.md)
- [Progress Standards](../core/standards/progress-standards.md)

## Core Rules

### 1. Pre-Update Consultation
- Always consult this document before any documentation changes
- Verify complete understanding of current rules
- If any rule is unclear, prompt user with numbered options

### 2. Information Preservation
- Information must never be lost during updates unless explicitly instructed
- When faced with uncertainty about information preservation:
  1. Stop the current operation
  2. Present numbered options to user
  3. Wait for explicit choice
  4. Document the decision

### 3. Modularization
- Information must not be duplicated across documents
- Use references to link to information in other documents
  Example: `[Progress Standards](../core/standards/progress-standards.md)`
- When finding duplicated information:
  1. Identify all instances
  2. Present user with numbered options for consolidation
  3. Update all references after consolidation

### 4. Document Structure
- Follow directory organization:
  * `/cascade/commands/` for command documentation
  * `/maintenance/` for process documentation
  * `/core/standards/` for fundamental standards
- Each document must contain:
  * Clear purpose statement
  * Related documentation references
  * Process steps (if applicable)
  * Success criteria (if applicable)

### 5. Cross-References
- Use markdown links: `[Title](path/to/file.md)`
- Always verify reference exists before adding
- Update all references when moving documents
- Use relative paths from current file location

### 6. User Interaction
When in doubt about any decision, present options as:
```
Please choose an option:
1. [Clear description of option 1]
2. [Clear description of option 2]
...
```

## Document Operations

### Creating Documents
1. Verify no existing document covers the topic
2. Choose appropriate directory based on content type:
   - Commands: [commands/](commands/)
   - Standards: [core/standards/](../core/standards/)
   - Maintenance: [maintenance/](../maintenance/)
3. Follow standard document structure
4. Add all necessary cross-references
5. Present to user for confirmation

### Updating Documents
1. Preserve all existing information
2. Update cross-references if needed
3. Maintain document structure as defined in [Documentation Standards](../core/standards/documentation-standards.md)
4. Verify no information loss
5. Present changes to user if significant

### Deleting Documents
1. Require explicit user confirmation
2. Identify all documents referencing this document
3. Present plan for handling references
4. Archive valuable information if instructed
5. Update all dependent documents

## Success Criteria
1. All references use markdown links
2. No broken links exist
3. Directory structure is maintained
4. Information is properly modularized
5. User is consulted for significant changes

## See Also
- [Command Documentation](commands/core/cp.md)
- [Project Standards](../core/standards/project-standards.md)
- [Documentation Standards](../core/standards/documentation-standards.md)

## Important Notes
- Primary audience is LLM, not humans
- All rules are normative and must be applied unconditionally
- When in doubt, always ask user
- Keep audit trail of significant decisions
- Reference rules with '@llm-rules'
