---
name: cui-requirements:traceability
source_bundle: cui-requirements
description: Standards for linking specifications to implementation code and maintaining bidirectional traceability between documentation and source code
version: 1.0.0
allowed-tools: []
---

# Traceability Standards

Standards for connecting specification documents with implementation code, establishing bidirectional traceability, and maintaining documentation throughout the implementation lifecycle.

## Core Principles

### Holistic System View

Effective documentation provides a complete view at multiple levels:

- **Requirements level**: What the system must accomplish
- **Specification level**: How the system is designed
- **Implementation level**: How the code actually works

Proper linkage ensures seamless navigation between these levels.

### Single Source of Truth

Each piece of information should have one authoritative location:

- **Specifications**: Architectural decisions, standards, constraints
- **Implementation code**: Detailed behavior, algorithms, edge cases
- **JavaDoc**: Usage guidance, API contracts, implementation notes

### Documentation Lifecycle

Documentation evolves through implementation:

1. **Pre-Implementation**: Specifications contain detailed design and examples
2. **During Implementation**: Specifications updated with implementation decisions
3. **Post-Implementation**: Specifications link to code, redundant details removed

## Information Distribution Standards

### What Belongs in Specifications

Specification documents must contain:

**Requirements and Constraints**:
- What the system must do (requirements traceability)
- Technical standards to follow
- Limitations and boundaries

**Architecture and Design**:
- High-level component structure
- Component relationships and dependencies
- Integration points and interfaces

**Implementation Guidance**:
- Design patterns to apply
- Frameworks and libraries to use
- Configuration requirements
- Standards compliance requirements

**References**:
- Links to implementing classes
- Links to verification tests
- Links to related specifications

### What Belongs in JavaDoc

Implementation code documentation (JavaDoc) must contain:

**API Documentation**:
- Purpose of class/method
- Usage instructions and examples
- Parameter descriptions
- Return value descriptions
- Exception conditions

**Implementation Details**:
- How the code works internally
- Algorithm descriptions
- Performance characteristics
- Thread safety guarantees

**Edge Cases**:
- Special cases and how they're handled
- Error handling specifics
- Boundary conditions

**References**:
- Links back to specification documents
- Requirement references
- Related classes and methods

### What to Avoid

**In specifications**:
- Detailed method-level implementation
- Internal algorithms and data structures
- Transitional language ("was moved", "will be refactored")
- Code that duplicates actual implementation

**In JavaDoc**:
- Extensive architectural overviews spanning multiple components
- Requirement definitions and rationale
- Standards definitions that apply broadly
- Information better suited to specifications

## Specification-to-Code Linking Standards

### Linking Format

**Java class references**:
```asciidoc
link:../src/main/java/com/example/TokenValidator.java[TokenValidator]
```

**Package references**:
```asciidoc
link:../src/main/java/com/example/jwt/[jwt package]
```

**Test references**:
```asciidoc
link:../src/test/java/com/example/TokenValidatorTest.java[TokenValidatorTest]
```

### Quick Reference: Common Patterns

**Status Section Template**:
```asciidoc
== [Component Name]
_See Requirement link:../Requirements.adoc#REQ-ID[REQ-ID: Title]_

=== Status: [PLANNED|IN PROGRESS|IMPLEMENTED]

[For IMPLEMENTED] This specification is implemented in:
* link:../src/main/java/path/ClassName.java[ClassName] - Brief description

For detailed behavior, refer to the JavaDoc of implementing classes.

=== Verification
* link:../src/test/java/path/ClassNameTest.java[ClassNameTest]
```

**JavaDoc Specification Reference Template**:
```java
/**
 * [Class purpose]
 * <p>
 * Implements requirement: {@code REQ-ID: Requirement Title}
 * <p>
 * For detailed specifications, see the
 * <a href="[relative-path]/doc/specification/[spec-file].adoc">Specification</a>.
 */
public class ClassName { }
```

**Method-Level Requirement Reference Template**:
```java
/**
 * [Method purpose]
 * <p>
 * Implements requirement: {@code REQ-ID: Requirement Title}
 * @param [param] [description]
 * @return [description]
 */
public ReturnType methodName(ParamType param) { }
```

## Code-to-Specification Linking Standards

### JavaDoc Link Format

See the **JavaDoc Specification Reference Template** in the Quick Reference section above for the standard format.

**Path Calculation**:
- **From `src/main/java/com/example/`**: `../../../../../../../doc/`
- **From `src/test/java/com/example/`**: `../../../../../../../doc/`
- **Formula**: Count directory levels from `src/` to file, then use that many `../` to reach project root, then add `doc/`

### Linking Approaches

**Class-level references**: Link to overall specification in class JavaDoc

**Method-level references**: Reference specific requirement IDs for methods implementing specific requirements (see **Method-Level Requirement Reference Template** in Quick Reference section)

**Multiple requirements**: Use bulleted list in JavaDoc for classes implementing multiple requirements

## Documentation Update Workflow

### Lifecycle Phases

**Pre-Implementation** (Status: PLANNED):
- Specifications contain detailed design, expected API, and validation flows
- Focus on "what" and "how" the system should work

**During Implementation** (Status: IN PROGRESS):
- Update status to IN PROGRESS
- Add implementation links as classes are created
- Add JavaDoc with specification references (see Quick Reference templates above)
- Document implementation decisions and library choices

**Post-Implementation** (Status: IMPLEMENTED):
- Update status to IMPLEMENTED
- Add complete implementation references with links to all implementing classes
- Add test references in Verification section
- Remove redundant code examples that duplicate actual implementation
- Keep architectural guidance, design rationale, and standards
- Refer readers to JavaDoc for detailed API behavior

See **Status Section Template** in Quick Reference section for the standard format to use at each phase.

## Verification and Validation Linking

### Test References

Include test verification sections in specifications using the **Status Section Template** format:
- List unit tests with brief descriptions of what they test
- List integration tests for end-to-end flows
- Document test coverage metrics when available
- Reference detailed testing specifications when they exist

**Example coverage section in AsciiDoc:**
```asciidoc
=== Coverage

Test coverage metrics:

* Line coverage: 92%
* Branch coverage: 88%
* Security-critical paths: 100%
```

### Test Class JavaDoc

Reference specifications from test classes:

```java
/**
 * Unit tests for {@link TokenValidator}.
 * <p>
 * Verifies the implementation against the requirements specified in
 * <a href="../../../../../../../doc/specification/token-validation.adoc">Token Validation Specification</a>.
 * <p>
 * Tests cover:
 * <ul>
 *   <li>Valid token validation</li>
 *   <li>Expired token handling</li>
 *   <li>Invalid signature detection</li>
 *   <li>Malformed token handling</li>
 * </ul>
 */
public class TokenValidatorTest {
    // Tests
}
```

## Cross-Reference Maintenance

### When Implementation Changes

If implementation significantly changes:

1. **Update JavaDoc** with new behavior
2. **Review specification** for accuracy
3. **Update specification** if design changed
4. **Verify tests** still cover requirements
5. **Update test references** if tests changed

### When Specifications Change

If specifications are updated:

1. **Identify affected implementation**
2. **Review implementation** for compliance
3. **Update implementation** if needed
4. **Update JavaDoc** with new references
5. **Update tests** to cover new requirements

### Regular Maintenance

Periodically verify:

- [ ] All specification links point to correct files
- [ ] All JavaDoc references are accurate
- [ ] Implementation status indicators are current
- [ ] Test references are complete
- [ ] No redundant content exists

## Applying Traceability Standards

To apply these traceability standards:

1. **Use Quick Reference Templates**: Apply the templates from the Quick Reference section above for consistent formatting
2. **Follow Lifecycle Workflow**: Update documentation through pre-implementation, during implementation, and post-implementation phases
3. **Maintain Cross-References**: Keep specification, JavaDoc, and test references synchronized as implementation evolves
4. **Verify Quality**: Use the Quality Standards checklist below to ensure complete and accurate traceability

## Quality Standards

### Completeness

- [ ] All specifications link to implementation when it exists
- [ ] All implementation classes reference specifications
- [ ] All tests reference specifications
- [ ] Implementation status is current and accurate

### Accuracy

- [ ] Links point to correct files
- [ ] Requirement references are accurate
- [ ] Implementation descriptions match actual code
- [ ] Test coverage metrics are current

### Navigation

- [ ] Can easily navigate from specification to implementation
- [ ] Can easily navigate from implementation to specification
- [ ] Can easily navigate from specification to tests
- [ ] Path through documentation is logical and clear

### Maintainability

- [ ] Links are maintained as code moves
- [ ] Status indicators are updated as implementation progresses
- [ ] Redundant content is removed after implementation
- [ ] Documentation remains valuable throughout project lifecycle

## Related Standards

### Related Skills in Bundle

- `cui-requirements:requirements-authoring` - Standards for creating requirements and specifications that form the traceability foundation
- `cui-requirements:setup` - Standards for setting up documentation structure in new projects
- `cui-requirements:planning` - Standards for planning documents that track implementation tasks

### External Standards

- JavaDoc standards (for implementation documentation)
- Testing standards (for test documentation)
