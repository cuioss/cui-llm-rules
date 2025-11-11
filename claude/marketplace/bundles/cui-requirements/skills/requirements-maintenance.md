---
name: cui-requirements:requirements-maintenance
source_bundle: cui-requirements
description: Standards for maintaining requirements and specification documents with integrity, consistency, and traceability
version: 1.0.0
allowed-tools: []
---

# Requirements Maintenance Standards

Standards and principles for maintaining requirements and specification documents to ensure continued accuracy, traceability, and alignment with implementation.

## Core Documentation Principles

### Consistency

**Definition**: Uniform terminology, structure, and formatting across all requirements and specification documents.

**Requirements**:
- Use consistent terminology throughout all documents
- Apply uniform formatting for similar elements
- Maintain standard document structure
- Follow established naming conventions

**Example**:
```
✅ CORRECT - Consistent terminology
Requirement REQ-001: The system shall authenticate users via OAuth2
Specification SPEC-001: OAuth2 authentication implementation
Test TEST-001: Verify OAuth2 authentication flow

❌ WRONG - Inconsistent terminology
Requirement REQ-001: The system shall authenticate users via OAuth2
Specification SPEC-001: User login implementation
Test TEST-001: Verify authentication
```

### Completeness

**Definition**: All requirements fully documented with necessary detail and no gaps in information.

**Requirements**:
- All requirements documented with sufficient detail
- All related specifications linked
- All constraints and rationale captured
- No missing information or TBD placeholders

**Verification Checklist**:
- [ ] Every requirement has description and rationale
- [ ] All acceptance criteria defined
- [ ] All constraints documented
- [ ] All dependencies identified
- [ ] Traceability links complete

### Clarity

**Definition**: Unambiguous statements that can be understood consistently by all stakeholders.

**Requirements**:
- Use precise, unambiguous language
- Avoid subjective terms (fast, easy, user-friendly)
- Define measurable criteria
- Provide concrete examples where helpful

**Example**:
```
❌ WRONG - Ambiguous
REQ-001: The system shall provide fast authentication

✅ CORRECT - Clear and measurable
REQ-001: The system shall complete user authentication within 2 seconds
for 95% of requests under normal load conditions (≤1000 concurrent users)
```

### Maintainability

**Definition**: Documentation structure that enables easy updates, extensions, and long-term maintenance.

**Requirements**:
- Modular document structure
- Clear cross-references
- Version control friendly format
- Minimal duplication
- Self-documenting organization

## Integrity Requirements

### No Hallucinations

**CRITICAL RULE**: Document only existing or planned functionality, never fictional capabilities.

**Requirements**:
- Verify all documented features exist in code or are approved for implementation
- Remove references to removed functionality
- Mark deprecated features appropriately
- Never invent capabilities to fill documentation gaps

**Validation Process**:
1. For each requirement, verify corresponding implementation exists or is planned
2. For each code reference, verify the code exists at specified location
3. For each specification, verify it describes real system behavior
4. Flag any documentation without verification source

**Example Violations**:
```
❌ HALLUCINATION - Feature doesn't exist
REQ-042: The system shall support automatic backup to cloud storage
(When no such feature is implemented or planned)

✅ CORRECT - Document only what exists
REQ-042: [FUTURE] Cloud backup integration (planned for v2.0)
(Clearly marked as future functionality)
```

### No Duplications

**CRITICAL RULE**: Use cross-references instead of copying information between documents.

**Requirements**:
- Single source of truth for each piece of information
- Use `xref:` links to reference information in other documents
- Avoid copying requirement text into specifications
- Link to canonical definitions

**Cross-Reference Pattern**:
```asciidoc
// ✅ CORRECT - Cross-reference
See xref:Requirements.adoc#req-001[REQ-001: User Authentication] for
complete authentication requirements.

// ❌ WRONG - Duplication
REQ-001 requires that the system shall authenticate users via OAuth2
with support for multiple identity providers...
(Copying entire requirement text)
```

**Allowed Duplication**:
- Brief summaries for context (max 1 sentence)
- Requirement IDs for traceability
- Document metadata (titles, versions)

### Verified Links

**CRITICAL RULE**: All references must point to existing documents or code elements.

**Requirements**:
- All `xref:` links must resolve to existing sections
- All code references must point to existing files/classes/methods
- All external links must be accessible
- Broken links must be fixed or removed

**Verification Process**:
1. Check all `xref:` references resolve correctly
2. Verify code references exist in current codebase
3. Test external links are accessible
4. Update or remove any broken references

**Common Link Types**:
```asciidoc
// Document cross-reference
xref:Requirements.adoc#req-001[REQ-001]

// Code reference
Implementation: `de.cuioss.portal.authentication.TokenValidator`

// External reference
OAuth2 Specification: https://oauth.net/2/
```

## Deprecation Handling

### Pre-1.0 Projects

**Rule**: Update requirements directly without deprecation process.

**Rationale**: Pre-release projects are in active development. Requirements can change freely without maintaining historical record.

**Process**:
1. Identify outdated requirements
2. Update requirement text directly
3. Update linked specifications
4. Update or remove implementation references
5. No deprecation markers needed

**Example**:
```asciidoc
// Simply update the requirement
=== REQ-001: User Authentication

The system shall authenticate users via OAuth2 with support for
OIDC identity providers.

(Previous text about SAML authentication simply replaced)
```

### Post-1.0 Projects

**Rule**: Always ask user whether to deprecate or remove functionality.

**Rationale**: Released projects may have users depending on documented behavior. Changes require explicit approval.

**Decision Process**:
```
When encountering removed/changed functionality:
1. STOP maintenance process
2. Document the change details
3. ASK USER: "Should I deprecate or remove this requirement?"
   - Deprecate: Mark as deprecated, keep documentation
   - Remove: Delete requirement and update all references
4. WAIT for user decision
5. Proceed based on user choice
```

### Deprecation Process (If User Chooses Deprecate)

**Steps**:

1. **Mark Requirement as Deprecated**:
```asciidoc
=== REQ-001: User Authentication [DEPRECATED]

[WARNING]
====
**Status**: DEPRECATED as of version 2.0.0

**Reason**: Replaced by OAuth2 authentication (REQ-042)

**Migration**: See xref:#req-042[REQ-042] for new authentication approach
====

Original requirement text preserved below for reference...
```

2. **Update Specification**:
```asciidoc
== Authentication Specification [DEPRECATED]

[WARNING]
====
This specification is deprecated. See xref:OAuth2Specification.adoc[OAuth2 Specification]
for current authentication implementation.
====
```

3. **Add Migration Guidance** (if applicable):
- Document how to migrate from old to new approach
- Provide code examples if relevant
- Link to new requirements/specifications

4. **Maintain Historical Record**:
- Keep deprecated documentation in place
- Preserve traceability links
- Document deprecation timeline

### Removal Process (If User Chooses Remove)

**Steps**:

1. **Remove Requirement**:
   - Delete requirement section completely
   - Update document table of contents

2. **Update All References**:
   - Remove from traceability matrices
   - Update cross-references in other documents
   - Remove from specification documents

3. **Update Implementation References**:
   - Remove code references to deleted requirement
   - Clean up test references

4. **Update Index/TOC**:
   - Ensure no orphaned links remain

## Quality Verification Criteria

### Cross-References Validated

**Verification**:
- [ ] All `xref:` links resolve to existing sections
- [ ] All document references point to current files
- [ ] No broken internal links
- [ ] All cross-references use correct syntax

**Tools**:
- AsciiDoc link verification
- Manual spot-checking of key references

### No Duplicate Information

**Verification**:
- [ ] Each piece of information has single source
- [ ] Cross-references used instead of copying
- [ ] No conflicting statements across documents
- [ ] Information distributed following standards

**Review Process**:
1. Identify repeated information
2. Determine canonical location
3. Replace duplicates with cross-references
4. Verify consistency

### Consistent Terminology

**Verification**:
- [ ] Same terms used for same concepts
- [ ] Glossary terms used consistently
- [ ] No contradictory definitions
- [ ] Standard naming conventions followed

**Common Term Categories**:
- Technical terms (API, authentication, token)
- Domain terms (user, resource, permission)
- Action verbs (shall, should, may, must)
- Status indicators (implemented, planned, deprecated)

### Clear Traceability Maintained

**Verification**:
- [ ] Requirements have unique IDs
- [ ] Specifications link to requirements
- [ ] Implementation references specifications
- [ ] Tests reference requirements
- [ ] Traceability matrix is current

**Traceability Chain**:
```
Requirement REQ-001
    ↓ (specified by)
Specification SPEC-001
    ↓ (implemented by)
Code: TokenValidator.java
    ↓ (tested by)
Test: TokenValidatorTest.java
```

### No Hallucinated Functionality

**Verification**:
- [ ] All documented features verified in code
- [ ] All code references point to existing elements
- [ ] No fictional capabilities documented
- [ ] Future features clearly marked

**Validation Steps**:
1. For each requirement, locate implementation
2. For each specification, verify behavior exists
3. For each code reference, verify element exists
4. Flag any unverified documentation

## Common Maintenance Scenarios

### New Feature Documentation

**When**: Adding requirements for new functionality being developed.

**Process**:
1. Add requirements following established format (SMART principles)
2. Assign unique requirement IDs following project scheme
3. Create specifications linked to requirements
4. Add cross-references in related documents
5. Update traceability matrix
6. Maintain consistent terminology

**Structure**:
```asciidoc
=== REQ-NEW: Feature Name

**Priority**: [High|Medium|Low]

**Description**: Clear statement of what system must do

**Rationale**: Why this requirement exists

**Acceptance Criteria**:
- Measurable criterion 1
- Measurable criterion 2

**Dependencies**: Links to related requirements

**Traceability**: xref:Specifications.adoc#spec-new[SPEC-NEW]
```

### Refactoring Impact

**When**: Code has been refactored, need to update documentation references.

**Process**:
1. Review changed code structure
2. Update implementation references in specifications
3. Verify requirement statements remain accurate
4. Adjust code examples to match new structure
5. Maintain requirement IDs unchanged (no renumbering)
6. Update package/class names in references

**Key Principle**: Requirements describe WHAT, not HOW. Refactoring changes HOW (implementation), so requirements usually don't change, only specification implementation references.

**Example**:
```asciidoc
// Before refactoring
Implementation: `de.cuioss.portal.auth.TokenValidator`

// After refactoring (package changed)
Implementation: `de.cuioss.portal.authentication.validator.TokenValidator`

// Requirement text unchanged - still describes WHAT system must do
```

### Cross-Reference Updates

**When**: Documents have been restructured or moved.

**Process**:
1. Identify all affected cross-references
2. Update xref paths to new locations
3. Update section IDs if changed
4. Test all links resolve correctly
5. Update external documentation references

**Common Updates**:
- File path changes: `xref:old/path.adoc` → `xref:new/path.adoc`
- Section ID changes: `xref:doc.adoc#old-id` → `xref:doc.adoc#new-id`
- Document renames: Update all references to new name

## Commit Guidelines

### Commit Message Format

Follow conventional commits with `docs(requirements):` prefix:

```
docs(requirements): update authentication requirements after OAuth2 migration

- Update REQ-001 through REQ-005 for OAuth2 authentication
- Remove deprecated SAML authentication requirements
- Update cross-references to new specification structure
- Fix broken links to implementation code

Affected requirements: REQ-001, REQ-002, REQ-003, REQ-004, REQ-005
```

### Commit Content

**Include**:
- Specific changes made to requirements/specifications
- Requirement/specification IDs affected
- Rationale for changes
- Any structural changes to documents

**Avoid**:
- Vague descriptions ("updated docs")
- Missing requirement IDs
- Unexplained removals
- Large structural changes without explanation

## References

**Related Skills**:
- requirements-documentation.md - Standards for creating requirements
- specification-documentation.md - Standards for creating specifications
- implementation-linkage.md - Standards for linking specs to code

**Related Standards**:
- Documentation Standards - Core documentation principles
- Documentation Organization - Review and maintenance guidelines
