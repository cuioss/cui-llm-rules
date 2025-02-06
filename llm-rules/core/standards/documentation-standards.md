# Documentation Standards

## Purpose
Defines comprehensive standards for all documentation across the codebase, including general documentation rules and specific Javadoc requirements.

## Related Commands
- `cp: fix javadoc`: Documentation fixes
- `cp: maintenance java perform`: Core maintenance
- `cp: maintenance java finalize`: Completion tasks

## Related Documentation
- [Project Standards](project-standards.md): Project standards and technology stack
- [Quality Standards](quality-standards.md): Quality and testing standards
- [Java Maintenance](../../maintenance/java.md): Java maintenance process

## Core Documentation Standards

### 1. General Principles
- Only document existing code elements - no speculative or planned features
- All references must be verified to exist
- Use linking instead of duplication
- Code examples must come from actual unit tests
- Use consistent terminology across all documentation
- All public APIs must be documented
- All changes require successful documentation build

### 2. Terminology Standards
- Always use "Java beans" instead of "Jakarta beans"
- Maintain "Java Bean Specification" terminology
- Apply consistently across all documentation types
- Follow project glossary and naming conventions
- Use technical terms consistently

### 3. Code Example Requirements
1. Technical Requirements
   - Must be complete and compilable
   - Include all necessary imports
   - Show proper error handling
   - Follow project coding standards
   - Be verified by unit tests

2. Structure Requirements
   - Start with setup/configuration
   - Show main functionality
   - Include error handling
   - Demonstrate cleanup if needed
   - Use clear variable names
   - Include comments for complex steps

## Documentation Structure

### 1. Package Documentation
1. Required Sections
   - Overview explaining purpose and scope
   - Key Components listing main classes/interfaces
   - Usage Examples with actual code samples
   - Best Practices section with guidelines
   - Cross-references to related components
   - Author and version information

2. Organization
   - Clear hierarchy of information
   - Logical grouping of related items
   - Consistent section ordering
   - Proper use of subsections

### 2. Class/Interface Documentation
1. Core Elements
   - Clear purpose description
   - Parameter descriptions with validation rules
   - Return value descriptions
   - Exception documentation
   - Usage examples from unit tests
   - Version information with @since tags
   - Thread-safety notes where applicable

2. Structure Requirements
   - Consistent organization
   - Clear separation of concerns
   - Proper grouping of related methods
   - Logical ordering of sections

### 3. Method Documentation
1. Required Elements
   - Precise description of functionality
   - Parameter validation rules
   - Return value guarantees
   - Exception conditions
   - Thread-safety notes where applicable
   - Usage examples for complex methods

2. Organization
   - Standard order of elements
   - Clear parameter descriptions
   - Explicit preconditions
   - Detailed postconditions

## Javadoc Maintenance

### 1. Critical Constraints
1. Content Preservation
   - Fix ONLY Javadoc errors and warnings from build
   - Do NOT alter or improve documentation content
   - Do NOT modify any code
   - Make minimal modifications necessary
   - Focus only on formatting, references, and tags

2. Common Fixes
   - Fix invalid {@link} references
   - Fix malformed HTML tags
   - Fix missing/incorrect parameter documentation
   - Fix missing/incorrect return value documentation
   - Fix missing/incorrect exception documentation

3. Out of Scope
   - Documentation improvements
   - Code changes
   - Content rewrites
   - Style changes beyond error fixes

### 2. Maintenance Process

#### Build Verification
- Run appropriate command:
  * Single module: `./mvnw clean verify -Pjavadoc`
  * Multi-module: `./mvnw clean verify -Pjavadoc-mm-reporting`
- Record any errors in progress file
- Categorize issues:
  * Missing tags
  * Invalid references
  * Formatting problems
- Document error locations

#### Documentation Analysis
- For each error:
  * Record issue details
  * Analyze context
  * Plan minimal fix
  * Document proposed changes
- Record analysis completion

#### Fix Application
- For each documented issue:
  * Apply minimal fix
  * Verify no content loss
  * Run local javadoc check
  * Record changes made
- Document all applied fixes

#### Final Verification
- Run appropriate javadoc command
- If issues remain:
  * Record in progress file
  * Return to Fix Application
- On success:
  * Record verification
  * Commit changes with descriptive message

## Progress Tracking

### 1. Process Steps
1. Initialize Progress
   - Create/update progress file
   - Record start time and state
   - Document configuration

2. Track Changes
   - Update after each step
   - Record all modifications
   - Document any issues

3. Completion
   - Record end time
   - Document final state
   - Archive progress data

### 2. Documentation
- Record all changes made
- Document any issues encountered
- Track progress at each step
- Maintain clear status updates

## Success Criteria

### 1. Documentation Quality
- All required sections present
- Consistent terminology used
- Clear and accurate content
- Proper cross-referencing
- No speculative features

### 2. Build Success
- All Javadoc errors fixed
- Build passes successfully
- No new issues introduced
- Documentation validates

### 3. Content Integrity
- No content modifications during fixes
- Documentation preserved
- Only format fixes applied
- Original meaning maintained

### 4. Process Completion
- Changes committed
- Progress tracking complete
- All steps documented
- Status properly updated

## See Also
- [Project Standards](project-standards.md): Project standards and technology stack
- [Quality Standards](quality-standards.md): Quality and testing standards
- [Java Maintenance](../../maintenance/java.md): Java maintenance process
