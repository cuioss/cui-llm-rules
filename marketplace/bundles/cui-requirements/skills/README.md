# CUI Requirements Skills

This directory contains skills that provide comprehensive knowledge about requirements and specification documentation in CUI projects.

## Skills Overview

### requirements-authoring

Comprehensive standards for creating and maintaining requirements and specification documents. Covers:

- **Requirements Format**: SMART principles, ID schemes, numbering, and structure
- **Specification Structure**: Document organization, backtracking links, and traceability patterns
- **Documentation Lifecycle**: Pre-implementation, during implementation, and post-implementation practices
- **Quality Standards**: Clarity, completeness, consistency, and testability requirements
- **Integrity Requirements**: No hallucinations, no duplications, verified links
- **Maintenance Standards**: Adding, modifying, removing, and deprecating requirements

**When to use**: Creating or maintaining requirements and specification documents, ensuring documentation quality and integrity

### setup

Standards for setting up documentation in new CUI projects. Covers:

- Standard directory structure for documentation
- Initial document creation and templates
- Requirement prefix selection process
- Creating complete documentation foundation
- Setting up traceability from project start

**When to use**: Starting a new project and establishing documentation structure

### planning

Standards for creating and maintaining project planning documents. Covers:

- TODO lists and task tracking
- Task status indicators and conventions
- Organizing tasks by component, feature, and phase
- Linking tasks to requirements and specifications
- Managing implementation progress
- Planning document maintenance

**When to use**: Creating planning documents to track implementation tasks

### traceability

Standards for linking specifications to implementation code. Covers:

- Bidirectional traceability between specs and code
- JavaDoc standards for referencing specifications
- Specification updates during and after implementation
- Linking to test implementations
- Managing documentation throughout implementation lifecycle
- Maintaining holistic system view

**When to use**: Linking specifications to implementation code and maintaining traceability

## Using These Skills

These skills work together to provide comprehensive documentation guidance:

1. **Starting a new project**: Use `setup` to establish documentation structure
2. **Writing requirements and specifications**: Use `requirements-authoring` for creating and maintaining docs
3. **Planning implementation**: Use `planning` for task tracking
4. **Connecting to code**: Use `traceability` for linking specs to implementation

## Integration

These skills integrate seamlessly with:

- **CUI Documentation Standards**: AsciiDoc formatting, general documentation
- **CUI Java Standards**: JavaDoc, code structure
- **CUI Testing Standards**: Test documentation, verification
- **CUI Workflow Standards**: Git commits, PR workflows

## Documentation Lifecycle

The skills support the complete documentation lifecycle:

1. **Setup**: Establish structure with `setup`
2. **Authoring**: Create requirements and specifications with `requirements-authoring`
3. **Planning**: Track work with `planning`
4. **Implementation**: Link code with `traceability`
5. **Maintenance**: Keep current using `requirements-authoring` and `traceability`

## Architecture Benefits

This refactored structure provides:

- **No Duplication**: Each skill has distinct responsibility without overlapping content
- **Clear Boundaries**: Easy to know which skill to use for each task
- **Self-Contained**: Each skill provides complete guidance for its domain
- **Easier Maintenance**: Changes are localized to appropriate skill
- **Better Usability**: Four focused skills instead of seven overlapping ones
