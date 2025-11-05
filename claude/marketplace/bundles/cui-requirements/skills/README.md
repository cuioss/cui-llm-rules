# CUI Requirements Skills

This directory contains skills that provide comprehensive knowledge about requirements and specification documentation in CUI projects.

## Skills Overview

### requirements-documentation

Standards for creating and maintaining requirements documents following SMART principles. Covers:

- Requirements document structure and format
- SMART requirements principles
- Requirement numbering and ID schemes
- Requirement prefix selection
- Requirements maintenance and lifecycle
- Traceability to specifications

### specification-documentation

Standards for creating specification documents with proper structure and traceability. Covers:

- Specification document structure and organization
- Backtracking links to requirements
- Implementation status tracking
- Pre-implementation vs. post-implementation content
- Linking specifications to source code and tests
- Specification maintenance throughout project lifecycle

### project-setup

Standards for setting up documentation in new CUI projects. Covers:

- Standard directory structure for documentation
- Initial document creation and templates
- Requirement prefix selection process
- Creating complete documentation foundation
- Setting up traceability from project start

### planning-documentation

Standards for creating and maintaining project planning documents. Covers:

- TODO lists and task tracking
- Task status indicators and conventions
- Organizing tasks by component, feature, and phase
- Linking tasks to requirements and specifications
- Managing implementation progress
- Planning document maintenance

### implementation-linkage

Standards for linking specifications to implementation code. Covers:

- Bidirectional traceability between specs and code
- JavaDoc standards for referencing specifications
- Specification updates during and after implementation
- Linking to test implementations
- Managing documentation throughout implementation lifecycle
- Maintaining holistic system view

## Using These Skills

These skills work together to provide comprehensive documentation guidance:

1. **Starting a new project**: Use `project-setup` to establish documentation structure
2. **Writing requirements**: Use `requirements-documentation` for SMART requirements
3. **Creating specifications**: Use `specification-documentation` for detailed design
4. **Planning implementation**: Use `planning-documentation` for task tracking
5. **Connecting to code**: Use `implementation-linkage` for traceability

## Integration

These skills integrate seamlessly with:

- CUI documentation standards (AsciiDoc formatting, general documentation)
- CUI Java standards (JavaDoc, code structure)
- CUI testing standards (test documentation, verification)

## Documentation Lifecycle

The skills support the complete documentation lifecycle:

1. **Setup**: Establish structure with `project-setup`
2. **Requirements**: Define needs with `requirements-documentation`
3. **Specification**: Detail design with `specification-documentation`
4. **Planning**: Track work with `planning-documentation`
5. **Implementation**: Link code with `implementation-linkage`
6. **Maintenance**: Keep current using all skills as needed
