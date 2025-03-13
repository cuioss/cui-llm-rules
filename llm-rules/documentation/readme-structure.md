# README.adoc Structure Pattern

@llm-rules

## Overview
This document defines the standard structure for module README.adoc files in CUI projects.

## Structure Requirements

### 1. Title and Brief Description
- Module name as title (level 1 heading)
- Concise description of purpose and key functionality
- High-level overview of module's role in the system

### 2. Maven Coordinates
- Must be placed immediately after description
- Complete dependency block in XML format
- Include group and artifact IDs
```xml
[source, xml]
----
    <dependency>
        <groupId>group.id</groupId>
        <artifactId>artifact-id</artifactId>
    </dependency>
----
```

### 3. Core Concepts
- Key architectural components
- Main features and capabilities
- Integration points
- Each concept with bullet points for details
- Links to source files where appropriate

### 4. Detailed Component Documentation
- Each major component with its own section
- Links to source files using asciidoc format: `link:path/to/file[ComponentName]`
- Feature lists and capabilities
- Technical details and requirements
- Implementation considerations

### 5. Usage Examples
- Complete, working code examples
- Common use cases
- Configuration examples
- Best practice implementations
- Each example must have:
  * Clear purpose explanation
  * Complete code snippet
  * Configuration if required
  * Expected outcome

### 6. Configuration
- Available configuration options
- Property examples
- Configuration hierarchy
- Default values and fallbacks
- Environment-specific configurations

### 7. Best Practices
- Implementation guidelines
- Performance considerations
- Security aspects
- Common pitfalls to avoid
- Recommended patterns

### 8. Technical Details
- Thread safety considerations
- Memory impact
- Performance characteristics
- Implementation notes
- Dependencies and requirements

### 9. Related Documentation
- Links to specifications
- Related projects
- Additional resources
- External documentation

## Style Guidelines

### Formatting
- Use asciidoc syntax consistently
- Maintain proper heading hierarchy
- Use code blocks with language specification
- Include line breaks between sections

### Code Examples
- Must be complete and working
- Show configuration where relevant
- Use realistic variable names
- Include comments for complex logic
- Must be backed by an actual unit-test

### Links
- Use relative paths for internal links
- Use absolute URLs for external resources
- Link to source files using asciidoc format
- Verify all links are valid

### Configuration Examples
- Show all relevant properties
- Include default values
- Demonstrate override patterns
- Document configuration hierarchy

## Example Structure
```asciidoc
= Module Name

Concise description of the module's purpose and key features.

== Maven Coordinates

[source, xml]
----
<dependency>
    <groupId>group.id</groupId>
    <artifactId>artifact-id</artifactId>
</dependency>
----

== Core Concepts

=== Feature One
* Capability details
* Integration points
* Key benefits

== Usage Examples

=== Basic Usage
[source,java]
----
// Complete code example
----

== Configuration

=== Property Configuration
[source,properties]
----
# Configuration examples
----

== Best Practices
* Guideline one
* Guideline two

== Technical Details
* Thread safety notes
* Performance characteristics

== Related Documentation
* link:url[External Resource]
```
