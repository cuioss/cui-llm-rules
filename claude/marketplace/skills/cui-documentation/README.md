# CUI Documentation Skill

General documentation standards for README, AsciiDoc, and technical documentation in CUI projects.

## Overview

The `cui-documentation` skill provides documentation standards covering:

- **Core Documentation**: Professional tone, technical precision, conciseness, no duplication
- **README Structure**: Title, Maven coordinates, core concepts, usage, configuration, best practices
- **AsciiDoc Formatting**: Headers, cross-references, lists, code blocks, section hierarchy

**Note**: This skill covers general technical documentation. For code documentation, use:
- `cui-javadoc` for Java code documentation
- `cui-frontend-development/jsdoc-standards.md` for JavaScript documentation

## When to Use This Skill

Use `cui-documentation` when:

- Creating or updating README files
- Writing AsciiDoc documentation
- Documenting project features and usage
- Creating technical guides
- Reviewing documentation quality
- Establishing documentation consistency

## Prerequisites

**Required**:
- Text editor with AsciiDoc support (VS Code, IntelliJ)
- AsciiDoc processor (asciidoctor) for preview

**Recommended**:
- Bash shell (for format validation script)
- Python 3.6+ (for link verification script)

**Optional**:
- Documentation linters

## Standards Included

### 1. Core Documentation (`documentation-core.md`)

**Always loaded** - Foundation for all documentation:

- Professional, neutral, objective tone
- No marketing or promotional language
- Technical precision with verifiable sources
- Concise, clear language
- Document only existing features
- Use linking instead of duplication
- Consistent terminology
- Code examples from unit tests
- All public APIs documented

### 2. README Structure (`readme-structure.md`)

**Load when**: Creating or editing README files

- Title and description
- Maven coordinates placement
- Core concepts section
- Usage examples (complete and working)
- Configuration documentation
- Best practices section
- Dependencies and prerequisites
- Building and testing instructions
- License information
- Links to related documentation

### 3. AsciiDoc Formatting (`asciidoc-formatting.md`)

**Load when**: Working with AsciiDoc files

- Document header with required attributes
- Cross-reference syntax (`xref:` format)
- **CRITICAL**: Blank lines before all lists
- Code block formatting with language specification
- Section hierarchy and numbering
- Table formatting
- Link syntax
- Image inclusion

## Quick Start

### 1. Create README File

```markdown
# Project Name

Brief one-line description of the project.

## Maven Coordinates

```xml
<dependency>
    <groupId>de.cuioss</groupId>
    <artifactId>project-name</artifactId>
    <version>1.0.0</version>
</dependency>
```

## Core Concepts

Describe the main concepts and components:

- **Component A**: Purpose and role
- **Component B**: Purpose and role

## Usage

### Basic Usage

```java
// Complete, working example
TokenValidator validator = new TokenValidator(config);
ValidationResult result = validator.validate(token);
```

### Advanced Usage

```java
// More complex scenarios
TokenValidator validator = TokenValidator.builder()
    .issuer("https://auth.example.com")
    .validity(Duration.ofHours(1))
    .build();
```

## Configuration

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `token.issuer` | String | - | JWT token issuer |
| `token.validity` | Duration | PT1H | Token validity period |

## Best Practices

- Use constructor injection for dependencies
- Validate tokens before use
- Configure appropriate validity periods

## Building

```bash
mvn clean install
```

## Testing

```bash
mvn clean verify
```

## License

Apache License 2.0
```

### 2. Create AsciiDoc Document

```asciidoc
= Document Title
:toc: left
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js

== Introduction

Brief introduction to the document content.

== Core Concepts

Describe main concepts with proper formatting.

IMPORTANT: Always include blank line before lists.

=== Concept A

Description of concept A.

* Feature 1
* Feature 2
* Feature 3

=== Concept B

Description of concept B.

. Step 1
. Step 2
. Step 3

== Code Examples

=== Basic Example

[source,java]
----
public class Example {
    public void method() {
        System.out.println("Example");
    }
}
----

== Cross-References

See xref:other-document.adoc[Other Document] for details.

Refer to <<Concept A>> for more information.
```

### 3. Document Feature

```markdown
## Token Validation Feature

Validates JWT tokens according to RFC 7519 standards.

### How It Works

The validator performs these checks:

1. **Signature Verification**: Validates token signature using configured public key
2. **Expiration Check**: Ensures token is not expired (with clock skew tolerance)
3. **Issuer Validation**: Verifies token issuer matches configuration
4. **Claims Validation**: Checks required claims are present

### Example

```java
TokenConfig config = TokenConfig.builder()
    .issuer("https://auth.example.com")
    .validity(Duration.ofHours(1))
    .requiredClaims(Set.of("sub", "exp"))
    .build();

TokenValidator validator = new TokenValidator(config);
ValidationResult result = validator.validate(jwtToken);

if (result.isValid()) {
    // Token is valid
} else {
    // Handle validation errors
    List<String> errors = result.getErrors();
}
```

### Configuration

Configure the validator using these properties:

- `issuer`: JWT token issuer URL (required)
- `validity`: Token validity duration (default: PT1H)
- `requiredClaims`: Set of required claim names (optional)

### Testing

```java
@Test
void shouldValidateValidToken() {
    ValidationResult result = validator.validate(validToken);
    assertTrue(result.isValid(), "Valid token should pass validation");
}
```
```

## Validation Scripts

This skill includes automated validation scripts for AsciiDoc documentation located in the `scripts/` directory.

### Available Scripts

#### 1. AsciiDoc Format Validator (`asciidoc-validator.sh`)

Validates AsciiDoc format compliance including:
- Blank lines before lists
- Section header formatting
- List syntax correctness
- Nested list indentation

**Usage**:
```bash
# Validate a single file
./scripts/asciidoc-validator.sh path/to/file.adoc

# Validate all files in a directory
./scripts/asciidoc-validator.sh directory/
```

**Output**: Reports format violations with file name and line number

#### 2. Link Verification Script (`verify-adoc-links.py`)

Validates cross-references and links in AsciiDoc files:
- Cross-reference (`xref:`) links
- Internal anchor references (`<<anchor>>`)
- File existence verification
- Anchor existence verification

**Usage**:
```bash
# Verify links in a single file
python3 scripts/verify-adoc-links.py --file path/to/file.adoc --report target/links.md

# Verify links in directory (non-recursive)
python3 scripts/verify-adoc-links.py --directory directory/ --report target/links.md

# Verify links recursively
python3 scripts/verify-adoc-links.py --directory directory/ --recursive --report target/links.md
```

**Output**: Generates a markdown report with broken links and format violations

### Validation Workflow

**Standard validation process**:

1. **Create report directory**:
   ```bash
   mkdir -p target/adoc-review
   ```

2. **Run format validation**:
   ```bash
   ./scripts/asciidoc-validator.sh path/to/docs/ 2>&1 | tee target/adoc-review/format.log
   ```

3. **Run link verification**:
   ```bash
   python3 scripts/verify-adoc-links.py \
       --directory path/to/docs/ \
       --report target/adoc-review/links.md \
       2>&1 | tee target/adoc-review/links.log
   ```

4. **Review reports**:
   - Check `target/adoc-review/format.log` for format violations
   - Check `target/adoc-review/links.md` for broken links
   - Fix reported issues
   - Re-run validation to confirm fixes

### Common Validation Issues

**Format violations**:
- Missing blank line before list
- Incorrect list syntax (using `1.` instead of `.`)
- Missing blank line after section header
- Incorrect nested list indentation

**Link issues**:
- Broken file references (file doesn't exist)
- Missing anchors (anchor ID not found)
- Deprecated link syntax (using `link:` instead of `xref:`)
- Incorrect relative paths

### Prerequisites for Scripts

**Format validator** (`asciidoc-validator.sh`):
- Bash shell
- awk (standard Unix utility)
- grep (standard Unix utility)

**Link verifier** (`verify-adoc-links.py`):
- Python 3.6+
- No external dependencies (uses standard library)

### Example Validation Session

```bash
# 1. Validate format
$ ./scripts/asciidoc-validator.sh standards/documentation/
Checking standards/documentation/general-standard.adoc
Line 45: Missing blank line before list
Line 89: Missing blank line after section header

# 2. Fix reported issues in editor
# 3. Re-validate
$ ./scripts/asciidoc-validator.sh standards/documentation/
All files valid ✓

# 4. Verify links
$ python3 scripts/verify-adoc-links.py \
    --directory standards/documentation/ \
    --report target/links.md
Processed 5 files
Found 2 broken links
Report generated: target/links.md

# 5. Review and fix broken links
$ cat target/links.md
## Broken Links
- File: general-standard.adoc, Line 34: xref:missing.adoc[Label]
  Error: File not found

# 6. Fix links and re-verify
$ python3 scripts/verify-adoc-links.py \
    --directory standards/documentation/ \
    --report target/links.md
Processed 5 files
All links valid ✓
```

## Integration with Other Skills

**Recommended skill combinations**:

```yaml
# Complete documentation suite
skills:
  - cui-documentation   # General docs (this skill)
  - cui-javadoc         # Java code documentation
  - cui-frontend-development  # JSDoc for JavaScript

# Project setup with documentation
skills:
  - cui-project-setup   # Project initialization
  - cui-documentation   # README and docs
```

## Common Documentation Tasks

### Create Project README

1. Add title and brief description
2. Include Maven coordinates
3. Document core concepts
4. Provide usage examples (complete and working)
5. Document configuration options
6. Add best practices section
7. Include build and test instructions
8. Add license information

### Write AsciiDoc Guide

1. Create document header with attributes
2. Structure with proper section hierarchy
3. Add table of contents
4. **Ensure blank lines before all lists**
5. Use proper code block syntax with language
6. Add cross-references with xref:
7. Include working code examples
8. Verify rendering with asciidoctor

### Document New Feature

1. Describe feature purpose and behavior
2. Provide working code examples
3. Document configuration options
4. Include best practices
5. Add troubleshooting section if needed
6. Link to related documentation
7. Keep examples from unit tests

## Prohibited Practices

**DO NOT**:
- Use marketing or promotional language
- Include future features or plans
- Duplicate information across documents
- Forget blank lines before lists (AsciiDoc)
- Use vague or imprecise language
- Include broken links or references
- Document implementation details
- Skip code example verification

## Verification Checklist

After applying this skill:

**General Documentation**:
- [ ] Professional, neutral tone used
- [ ] No marketing language
- [ ] Technical precision verified
- [ ] Only existing features documented
- [ ] Consistent terminology used
- [ ] All links valid

**README Files**:
- [ ] Title and description present
- [ ] Maven coordinates included
- [ ] Core concepts explained
- [ ] Usage examples complete and working
- [ ] Configuration documented
- [ ] Best practices included
- [ ] Build/test instructions present

**AsciiDoc Files**:
- [ ] Header with required attributes
- [ ] Blank lines before all lists
- [ ] Code blocks have language tags
- [ ] Cross-references use xref: syntax
- [ ] Section hierarchy logical
- [ ] Renders correctly with asciidoctor

**Code Examples**:
- [ ] All examples compilable
- [ ] Examples from unit tests
- [ ] Complete (not fragments)
- [ ] Properly formatted
- [ ] Language specified in code blocks

## Quality Standards

This skill enforces:

- **Professionalism**: Neutral, objective tone
- **Accuracy**: Factual with verifiable sources
- **Clarity**: Concise, clear language
- **Completeness**: All aspects documented
- **Consistency**: Uniform terminology and style
- **Maintainability**: Easy to update with code changes

## Examples

See standards files for comprehensive examples including:

- README.md templates
- AsciiDoc document structures
- Code example formatting
- Configuration tables
- Cross-reference syntax
- List formatting
- Section hierarchies

## Support

For issues or questions:

1. Review detailed standards in `standards/` directory
2. Check AsciiDoc syntax guide for formatting
3. Run validation scripts in `scripts/` directory:
   - `asciidoc-validator.sh` for format validation
   - `verify-adoc-links.py` for link verification
4. Verify code examples compile
5. Use AsciiDoc preview in IDE

## License

Part of the CUI LLM Rules documentation system for CUI OSS projects.
