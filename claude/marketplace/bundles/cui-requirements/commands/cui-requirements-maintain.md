# Requirements and Specifications Maintenance Command

Systematic workflow for maintaining requirements and specification documents to ensure continued accuracy, traceability, and alignment with implementation.

## PARAMETERS

- **scope** - (Optional) Maintenance scope:
  - `full` - Complete requirements and specifications maintenance (default)
  - `requirements` - Focus on requirements documents only
  - `specifications` - Focus on specification documents only
  - `references` - Focus on cross-reference verification only
- **scenario** - (Optional) Specific maintenance scenario:
  - `new-feature` - Adding documentation for new functionality
  - `deprecation` - Handling deprecated or removed functionality
  - `refactoring` - Updating after code refactoring

## OVERVIEW

This command provides comprehensive requirements and specifications maintenance workflow with:

* Pre-maintenance checklist and scope identification
* Requirements review and update process
* Specification maintenance and alignment verification
* Cross-reference verification (documents and code)
* Integrity checking (no hallucinations, no duplications, verified links)
* Deprecation handling protocol (pre-1.0 vs post-1.0)
* Quality verification with comprehensive checklist
* Scenario-specific workflows

**Key Constraint**: NO hallucinations - document only existing or approved functionality.

## PREREQUISITES

**Load Required Skills**:
```
Skill: cui-requirements:requirements-maintenance
Skill: cui-requirements:requirements-documentation
Skill: cui-requirements:specification-documentation
```

This loads all requirements/specifications standards including:
- Maintenance principles (consistency, completeness, clarity, maintainability)
- Integrity requirements (no hallucinations, no duplications, verified links)
- Deprecation handling rules
- SMART requirements principles
- Specification structure standards

## WORKFLOW

### Step 1: Pre-Maintenance Checklist

**Execute pre-maintenance verification**:

1. **Identify Scope**:
   - If `scope` parameter provided: Use specified scope
   - If NO `scope` parameter: Default to full maintenance
   - If `scenario` parameter provided: Tailor workflow to scenario

2. **Verify Document Access**:
   ```
   Task:
     subagent_type: Explore
     thoroughness: quick
     description: Identify requirements and specification documents
     prompt: |
       Locate all requirements and specification documents in the project.

       Search for:
       - Requirements.adoc (typically in doc/ directory)
       - Specification documents (typically in doc/specifications/ or similar)
       - Related documentation files

       Return:
       - List of requirements documents found
       - List of specification documents found
       - Document structure and organization
   ```

3. **Load Maintenance Standards**:
   ```
   Read: claude/marketplace/bundles/cui-requirements/skills/requirements-maintenance.md
   ```

4. **Understand Current State**:
   - Review document structure
   - Identify dependencies between documents
   - Note any existing issues or warnings

**Outcome**: Scope defined, documents identified, standards loaded.

### Step 2: Requirements Review Process

**[If scope = "requirements" OR scope = "full"]**

#### Step 2a: Analyze Current Requirements State

```
Task:
  subagent_type: Explore
  thoroughness: medium
  description: Analyze requirements documents for issues
  prompt: |
    Analyze requirements documents for maintenance needs.

    Review for:

    1. **Missing or Incomplete Requirements**:
       - Requirements without descriptions
       - Missing rationale or acceptance criteria
       - Incomplete traceability links
       - TBD placeholders or gaps

    2. **Outdated References**:
       - References to deprecated functionality
       - Broken links to specifications
       - Obsolete code references
       - Incorrect package/class names

    3. **Broken Cross-References**:
       - xref: links that don't resolve
       - References to deleted documents
       - Invalid section IDs
       - External links that are broken

    4. **Inconsistent Terminology**:
       - Different terms for same concept
       - Contradictory definitions
       - Non-standard naming conventions

    5. **Duplicate Information**:
       - Same information in multiple places
       - Copy-pasted requirement text
       - Redundant definitions

    6. **Integrity Violations**:
       - Potential hallucinations (documented features that don't exist)
       - Missing verification sources
       - Unverified code references

    Apply scope filter: [scope parameter]

    Return structured analysis with:
    - Issues found by category
    - Affected requirement IDs
    - Severity (High/Medium/Low)
    - Recommended actions
```

**Outcome**: Complete understanding of requirements maintenance needs.

#### Step 2b: Update Requirements

Apply changes following requirements documentation standards:

```
For each identified issue:

1. **Update Requirement Statements**:
   - Correct inaccurate statements
   - Complete incomplete requirements
   - Clarify ambiguous language
   - Ensure SMART compliance

2. **Maintain Requirement IDs**:
   - NEVER renumber requirements
   - Preserve traceability through ID stability
   - Only add new IDs for new requirements

3. **Preserve Requirement Rationale**:
   - Keep historical context
   - Update rationale if context changes
   - Document reason for changes

4. **Update Status Indicators**:
   - Mark deprecated requirements (if post-1.0)
   - Update implementation status
   - Reflect current project state
```

**Example Update**:
```asciidoc
// Before
=== REQ-001: Authentication

System needs auth.

// After
=== REQ-001: User Authentication

The system shall authenticate users via OAuth2 protocol with support
for multiple OIDC identity providers.

**Rationale**: OAuth2 provides industry-standard security and enables
single sign-on across multiple applications.

**Acceptance Criteria**:
- Support at least 3 OIDC providers (Google, Microsoft, Okta)
- Complete authentication within 2 seconds for 95% of requests
- Maintain session security according to OWASP standards

**Traceability**: xref:specifications/OAuth2Specification.adoc[OAuth2 Specification]
```

#### Step 2c: Verify Specification Alignment

Ensure specifications match requirements:

```
For each updated requirement:

1. **Check Specification Links**:
   - Verify xref: to specifications resolve
   - Ensure specifications exist for all requirements
   - Confirm bidirectional traceability

2. **Verify Implementation References**:
   - Check code references are accurate
   - Verify package/class names correct
   - Confirm methods/interfaces exist

3. **Update Cross-References**:
   - Add missing specification links
   - Fix broken references
   - Update changed paths

4. **Maintain Traceability Matrix** (if present):
   - Update requirement-to-specification mappings
   - Verify completeness
   - Check for orphaned entries
```

**Outcome**: Requirements updated and aligned with specifications.

### Step 3: Specification Maintenance Process

**[If scope = "specifications" OR scope = "full"]**

#### Step 3a: Review Specifications

```
Task:
  subagent_type: Explore
  thoroughness: medium
  description: Analyze specification documents for maintenance needs
  prompt: |
    Analyze specification documents for maintenance issues.

    Review for:

    1. **Alignment with Requirements**:
       - Each specification linked to requirements
       - All requirement changes reflected
       - No specifications without requirements

    2. **Accurate Implementation References**:
       - Code references point to existing files
       - Package/class names are current
       - Method signatures match code
       - Line numbers updated if specified

    3. **Complete Behavioral Descriptions**:
       - All behavior fully specified
       - Edge cases documented
       - Error handling described
       - Performance characteristics stated

    4. **Valid Cross-References**:
       - Links to requirements resolve
       - Links to other specifications work
       - Code examples are current
       - External references accessible

    Apply scope filter: [scope parameter]

    Return structured analysis of specification issues.
```

#### Step 3b: Update Specifications

Follow specification documentation standards:

```
For each identified issue:

1. **Maintain Linkage to Requirements**:
   - Ensure every specification links to requirements
   - Use clear requirement ID references
   - Update links if requirements changed

2. **Update Implementation Details**:
   - Correct code references to match current structure
   - Update package/class names after refactoring
   - Refresh code examples
   - Remove references to deleted code

3. **Preserve Specification IDs**:
   - Keep specification IDs stable
   - Maintain traceability throughout lifecycle

4. **Keep Examples Current and Valid**:
   - Verify code examples compile
   - Update examples to match current API
   - Ensure examples follow project standards
```

**Outcome**: Specifications updated and synchronized.

### Step 4: Cross-Reference Verification

**[If scope = "references" OR scope = "full"]**

#### Step 4a: Verify Document Links

Check all internal documentation links:

```
Verification process:

1. **Check xref: References**:
   - Compile list of all xref: links in documents
   - Verify each link resolves to existing section
   - Test that target sections exist
   - Confirm section IDs are correct

2. **Update Paths After Restructuring**:
   - If documents moved, update paths
   - If sections renamed, update section IDs
   - Maintain link integrity

3. **Remove References to Deleted Documents**:
   - Identify links to non-existent files
   - Either remove link or update to new location
   - Document reason for removal

4. **Add References to New Documents**:
   - When new related documents added
   - Create appropriate cross-references
   - Maintain documentation network
```

#### Step 4b: Validate Code References

**CRITICAL**: Verify implementation references exist:

```
Verification process:

1. **Verify Referenced Classes/Methods Exist**:
   For each code reference:
   - Check class exists in codebase
   - Verify method signatures correct
   - Confirm interfaces/types are accurate

2. **Update Package Names if Changed**:
   - Search for old package references
   - Update to current package structure
   - Verify new paths are correct

3. **Confirm Line Numbers if Specified**:
   - If documentation references specific lines
   - Verify line numbers are current
   - Update or remove if code changed significantly

4. **Remove References to Deleted Code**:
   - Identify references to non-existent code
   - Remove or update to replacement code
   - Document why code reference removed
```

**Tool Usage**:
```
Use Grep to find code references:
Pattern: `de\.cuioss\.[a-zA-Z.]+`

Verify each match exists in codebase.
```

**Outcome**: All cross-references verified and updated.

### Step 5: Integrity Verification

**CRITICAL CHECKS**:

#### Check 1: No Hallucinations

```
For each requirement and specification:

1. **Verify Feature Exists or Is Approved**:
   - Check implementation code exists
   - OR verify feature is in approved roadmap
   - OR mark clearly as future functionality

2. **Flag Unverified Documentation**:
   - Requirements without implementation
   - Specifications describing non-existent behavior
   - Code references to non-existent elements

3. **User Approval for Unknowns**:
   If documentation found without verification:
   - STOP maintenance process
   - Document the unverified content
   - ASK USER: "Is this documented feature planned or should it be removed?"
   - WAIT for user decision
```

#### Check 2: No Duplications

```
Search for duplicate content:

1. **Identify Repeated Information**:
   - Same requirement text in multiple places
   - Copied specifications
   - Redundant definitions

2. **Determine Canonical Location**:
   - Identify single source of truth
   - Keep most complete version
   - Note location for cross-references

3. **Replace Duplicates with Cross-References**:
   - Replace copied text with xref: link
   - Add brief context if needed (max 1 sentence)
   - Verify link resolves correctly
```

#### Check 3: Verified Links

```
Final link verification:

- [ ] All xref: links resolve
- [ ] All code references verified
- [ ] All external links accessible
- [ ] No broken references remain
```

**Outcome**: Documentation integrity verified.

### Step 6: Scenario-Specific Workflows

**[If scenario parameter provided]**

#### Scenario: New Feature Documentation

**[If scenario = "new-feature"]**

```
Workflow for documenting new features:

1. **Add Requirements**:
   - Follow SMART principles
   - Assign unique requirement ID following project scheme
   - Include rationale and acceptance criteria
   - Link to related requirements

2. **Create Specifications**:
   - Link specification to requirements
   - Describe behavior completely
   - Include implementation references
   - Add code examples if helpful

3. **Update Related Documents**:
   - Add cross-references in related requirements
   - Update traceability matrix
   - Link from overview/index documents

4. **Maintain Consistency**:
   - Use established terminology
   - Follow document structure standards
   - Apply consistent formatting
```

#### Scenario: Deprecation Handling

**[If scenario = "deprecation"]**

**CRITICAL**: Handle deprecation based on project version.

```
Process:

1. **Determine Project Version**:
   - Check if project is pre-1.0 or post-1.0
   - Apply appropriate deprecation rule

2. **Pre-1.0 Projects**:
   - Update requirements directly
   - No deprecation markers needed
   - Simply remove or update content
   - Update linked specifications

3. **Post-1.0 Projects - ASK USER**:
   STOP and ask user:

   Use AskUserQuestion tool:
   Question: "This functionality appears to be removed or changed.

   Details:
   - Affected requirements: [list IDs]
   - Affected specifications: [list docs]
   - Current status: [description]

   Should I deprecate (mark as deprecated but keep) or remove (delete)?

   Deprecate: Maintains historical record, shows migration path
   Remove: Cleans up documentation, removes outdated info"

   Options:
   - "Deprecate - mark as deprecated and add migration guidance"
   - "Remove - delete requirements and update all references"

4. **If User Chooses Deprecate**:
   - Mark requirements with [DEPRECATED] in title
   - Add deprecation warning block
   - Document replacement functionality
   - Add migration guidance
   - Preserve original content
   - Update specification status

5. **If User Chooses Remove**:
   - Delete requirement sections
   - Remove from traceability matrix
   - Update all cross-references
   - Remove from specifications
   - Clean up implementation references
```

#### Scenario: Refactoring Impact

**[If scenario = "refactoring"]**

```
Workflow after code refactoring:

1. **Identify Refactoring Changes**:
   - List moved/renamed classes
   - List changed package names
   - List modified method signatures
   - Note structural changes

2. **Update Implementation References**:
   - Search for old package names in specifications
   - Replace with new package/class names
   - Update method signatures if changed
   - Verify all references resolve

3. **Verify Requirement Statements**:
   - Confirm requirements still accurate
   - Requirements describe WHAT, not HOW
   - Usually requirements don't change
   - Only update if behavior changed

4. **Adjust Examples**:
   - Update code examples to new structure
   - Verify examples still compile
   - Ensure examples follow current standards

5. **Maintain Requirement IDs**:
   - NEVER renumber requirements
   - Keep traceability intact
   - Only update content, not IDs
```

**Outcome**: Scenario-specific updates applied correctly.

### Step 7: Quality Verification

**Complete comprehensive quality checklist**:

```
Quality Verification:

- [ ] **Cross-References Validated**:
  - All xref: links resolve correctly
  - All document references point to current files
  - No broken internal links
  - Cross-references use correct syntax

- [ ] **No Duplicate Information**:
  - Each piece of information has single source
  - Cross-references used instead of copying
  - No conflicting statements across documents
  - Information distributed following standards

- [ ] **Consistent Terminology**:
  - Same terms used for same concepts
  - Glossary terms used consistently
  - No contradictory definitions
  - Standard naming conventions followed

- [ ] **Clear Traceability Maintained**:
  - Requirements have unique IDs
  - Specifications link to requirements
  - Implementation references specifications
  - Traceability complete and current

- [ ] **No Hallucinated Functionality**:
  - All documented features verified in code
  - All code references point to existing elements
  - No fictional capabilities documented
  - Future features clearly marked

- [ ] **Integrity Maintained**:
  - No hallucinations present
  - No duplications remain
  - All links verified and working
  - Documentation reflects reality
```

**If ANY check fails**:
1. Document the failure
2. Fix the issue
3. Re-run verification
4. Continue only when all checks pass

**Outcome**: Quality standards met.

### Step 8: Commit Changes

**Create focused commit following standards**:

1. **Review All Changes**:
   - Check what was modified
   - Ensure changes are intentional
   - Verify no unintended edits

2. **Prepare Commit Message**:
   ```
   docs(requirements): [brief description of changes]

   [Detailed description of maintenance performed]

   - [Specific change 1]
   - [Specific change 2]
   - [Specific change 3]

   Affected requirements: [list requirement IDs]
   [Optional: Affected specifications: list spec IDs]
   [Optional: Structural changes: describe]

   🤖 Generated with Claude Code
   Co-Authored-By: Claude <noreply@anthropic.com>
   ```

3. **Execute Commit**:
   ```bash
   git add [affected files]
   git commit -m "$(cat <<'EOF'
   [commit message from above]
   EOF
   )"
   ```

**Example Commit Message**:
```
docs(requirements): update authentication requirements after OAuth2 migration

Comprehensive maintenance of authentication requirements and specifications
following code refactoring to OAuth2 implementation.

- Updated REQ-001 through REQ-005 for OAuth2 authentication
- Removed deprecated SAML authentication requirements (pre-1.0 project)
- Updated implementation references to new package structure
- Fixed broken cross-references to specifications
- Verified all code references resolve correctly

Affected requirements: REQ-001, REQ-002, REQ-003, REQ-004, REQ-005
Affected specifications: OAuth2Specification.adoc, AuthenticationFlows.adoc
```

**Outcome**: Changes committed with proper documentation.

### Step 9: Summary Report

**Provide comprehensive maintenance summary**:

Report:

1. **Scope Processed**:
   - Scope: [scope parameter value]
   - Scenario: [scenario parameter value if provided]
   - Documents reviewed: [list]

2. **Requirements Updated**:
   - Requirements reviewed: [count]
   - Requirements updated: [list of IDs]
   - New requirements added: [list if any]
   - Requirements deprecated/removed: [list if any]

3. **Specifications Updated**:
   - Specifications reviewed: [count]
   - Specifications updated: [list]
   - Implementation references corrected: [count]

4. **Cross-References Fixed**:
   - Broken document links fixed: [count]
   - Broken code references fixed: [count]
   - New cross-references added: [count]

5. **Integrity Checks**:
   - Hallucinations found and resolved: [count]
   - Duplications removed: [count]
   - Links verified: [total count]

6. **Quality Verification**: All checks passed ✓

7. **Commit Created**: [commit hash] ✓

## PARAMETERS USAGE

**Example 1: Full maintenance**
```
scope: "full"
```
Performs complete requirements and specifications maintenance with all verification checks.

**Example 2: Requirements only**
```
scope: "requirements"
```
Focuses on requirements documents, skips specification-specific updates.

**Example 3: New feature documentation**
```
scope: "full"
scenario: "new-feature"
```
Tailors workflow for documenting new functionality with proper traceability.

**Example 4: Handle deprecation (post-1.0 project)**
```
scope: "full"
scenario: "deprecation"
```
Executes deprecation workflow, asks user whether to deprecate or remove.

**Example 5: After refactoring**
```
scope: "specifications"
scenario: "refactoring"
```
Updates implementation references after code refactoring.

## ERROR HANDLING

### Unverified Documentation Found

If documentation is found without verification source:
1. Stop maintenance process
2. Document the unverified content details
3. Ask user: "Is this documented feature planned or should it be removed?"
4. Wait for user decision
5. Proceed based on user choice

### Broken Links Cannot Be Fixed

If cross-reference target is missing:
1. Document the broken link
2. Try to locate moved content
3. If found: Update link
4. If not found: Ask user for guidance
5. Remove link only with user approval

### Conflicting Information

If duplicate information conflicts:
1. Document both versions
2. Identify most authoritative source
3. Ask user which version is correct
4. Update to correct version
5. Replace duplicates with cross-references

## CONSTRAINTS

**STRICT REQUIREMENTS**:

* **NO hallucinations**: Document only existing or approved functionality
* **NO duplications**: Use cross-references, not copies
* **Verified links**: All references must resolve correctly
* **Ask before removing**: For post-1.0 projects, ask user about deprecation vs removal
* **Preserve IDs**: Never renumber requirements or specifications
* **Maintain traceability**: Keep complete requirement-to-implementation chain

## SUCCESS CRITERIA

Requirements maintenance is complete when:

- [ ] All requirements reviewed and updated
- [ ] All specifications aligned with requirements
- [ ] All cross-references verified and working
- [ ] No duplicate information remains
- [ ] Consistent terminology throughout
- [ ] No hallucinated functionality documented
- [ ] All integrity checks passed
- [ ] Quality verification checklist complete
- [ ] Changes committed with proper message
- [ ] Summary report provided

## REFERENCES

**Skills Used**:
* cui-requirements:requirements-maintenance - Maintenance standards and principles
* cui-requirements:requirements-documentation - Requirements creation standards
* cui-requirements:specification-documentation - Specification creation standards

**Agents Orchestrated**:
* Explore - Document analysis and issue identification
