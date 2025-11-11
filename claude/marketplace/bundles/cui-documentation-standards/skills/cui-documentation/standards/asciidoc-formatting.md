# AsciiDoc Formatting Standards

## Purpose
Comprehensive AsciiDoc formatting, grammar, and best practice standards for all CUI project documentation.

## Document Structure Standards

### Document Header Requirements

All AsciiDoc documents MUST include a standard header. The TOC configuration varies by document type:

**For README Files** (README.adoc, */README.adoc):

```asciidoc
= Document Title
:toc: macro
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js

Brief introduction paragraph.

toc::[]

== Main Content
```

Use `:toc: macro` to manually control TOC placement after introductory content.

**For General Documentation Files** (specifications, standards, guides):

```asciidoc
= Document Title
:toc: left
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js
```

Use `:toc: left` for automatic left sidebar TOC.

**Required Attributes**:

* **Document Title**: Clear, descriptive title using `=` syntax
* **TOC Configuration**: `:toc: macro` (READMEs) or `:toc: left` (other docs)
* **TOC Levels**: Limited to 3 levels for readability
* **Section Numbering**: Enabled for main content sections
* **Syntax Highlighting**: highlight.js for code blocks

### Section Hierarchy Standards

**Heading Levels**:

* `=` Document title (level 0) - One per document
* `==` Main sections (level 1) - Primary content divisions
* `===` Subsections (level 2) - Supporting topics
* `====` Sub-subsections (level 3) - Detailed breakdowns
* `=====` Level 4 and beyond - Use sparingly

**Section Organization**:

* Follow logical content flow
* Use consistent section naming patterns
* Ensure proper nesting hierarchy
* Group related topics appropriately

## Grammar and Formatting Requirements

### Text Formatting Standards

**Emphasis and Styling**:

* **Bold text**: Use `**bold text**` for important terms and concepts
* *Italic text*: Use `*italic text*` for emphasis and technical terms
* `Monospace text`: Use `` `monospace text` `` for code elements, file paths, and commands
* Underlined text: Use `[.underline]#text#` sparingly for special emphasis

**Code References**:

* File paths: `src/main/java/Example.java`
* Class names: `TokenValidator`
* Method names: `validateToken()`
* Configuration keys: `jwt.validation.enabled`

### List Formatting Requirements

**CRITICAL REQUIREMENT**: There MUST always be a blank line before any list.

**Unordered Lists**:

Incorrect format:
```asciidoc
This is a paragraph.
* List item 1
* List item 2
```

Correct format:
```asciidoc
This is a paragraph.

* List item 1
* List item 2
```

**Ordered Lists**:

```asciidoc
Prerequisites for setup:

1. Java 17 or higher
2. Maven 3.8+
3. IDE with AsciiDoc support
```

**Nested Lists**:

```asciidoc
Main requirements:

* Technical Standards
** Code quality standards
** Testing requirements
** Documentation requirements
* Process Standards
** Git workflow
** Review process
** Deployment process
```

**Definition Lists**:

```asciidoc
Key concepts:

Token Validation:: Process of verifying JWT token integrity and claims
Issuer Config:: Configuration defining trusted token issuers
JWKS Loader:: Component responsible for loading JSON Web Key Sets
```

### Code Block Standards

**Source Code Blocks**:

```asciidoc
[source,java]
----
@ParameterizedTest
@DisplayName("Should validate tokens")
void shouldValidateToken() {
    assertDoesNotThrow(() -> validator.validate(token));
}
----
```

**Configuration Examples**:

```asciidoc
[source,yaml]
----
jwt:
  validation:
    enabled: true
    issuer: "https://auth.example.com"
----
```

**Language Specification Requirements**:

* Always specify language for syntax highlighting
* Use appropriate language identifiers: `java`, `yaml`, `xml`, `json`, `shell`, `asciidoc`
* Include proper file extensions when relevant

## Cross-Reference Standards

### Internal Document References

**Standard Syntax**: Use `xref:` for all file references

**Same Directory References**:
```asciidoc
xref:general-standard.adoc[General Documentation Standards]
```

**Cross-Directory References**:
```asciidoc
xref:../testing/quality-standards.adoc[Testing Quality Standards]
```

**Anchored References** (to specific sections):
```asciidoc
xref:quality-standards.adoc#parameterized-tests[Parameterized Tests]
```

**Internal Anchor References** (same document):
```asciidoc
<<section-anchor,Section Title>>
```

### Link Text Standards

**Descriptive Link Text**:

* Use meaningful descriptions that indicate target content
* Avoid generic text like "click here" or "see this"
* Include context about what the reader will find

**Examples**:

✅ Good:
```asciidoc
xref:../testing/quality-standards.adoc[Testing Quality Standards and Requirements]
```

❌ Bad:
```asciidoc
xref:../testing/quality-standards.adoc[here]
```

### Prohibited Reference Patterns

**Never Use These Patterns**:

* `<<../path/file.adoc#,Title>>` - Deprecated syntax
* `<<file.adoc#,Title>>` - Use xref: instead
* `link:file.adoc[Title]` - For external links only

## Table Formatting Standards

### Basic Table Structure

```asciidoc
.Table Caption
[cols="1,2,3", options="header"]
|===
|Column 1 |Column 2 |Column 3

|Data 1
|Data 2
|Data 3
|===
```

### Table Options

* `header` - First row as header
* `footer` - Last row as footer
* `autowidth` - Automatic column widths

## Admonition Blocks

### Standard Admonitions

```asciidoc
NOTE: Informational note

TIP: Helpful tip

IMPORTANT: Important information

WARNING: Warning about potential issues

CAUTION: Caution about critical concerns
```

### Custom Admonition Blocks

```asciidoc
[IMPORTANT]
====
Multi-line important
information block
====
```

## Document Validation Requirements

### Pre-Publication Checklist

Before finalizing any AsciiDoc document:

- [ ] **Header Attributes**: All required document attributes present
- [ ] **Section Hierarchy**: Proper heading levels and logical flow
- [ ] **List Formatting**: Blank lines before all lists
- [ ] **Cross-References**: All use `xref:` syntax for file references
- [ ] **Code Blocks**: Language specification for all source blocks
- [ ] **Grammar Check**: Proper AsciiDoc syntax throughout
- [ ] **Link Validation**: All internal references resolve correctly
- [ ] **Table of Contents**: Generated correctly with proper levels

### Common Formatting Errors

#### List Formatting Violations

**Error**: Missing blank line before list
```asciidoc
This is a paragraph.
* List item 1  ❌ INCORRECT
```

**Correction**: Add blank line
```asciidoc
This is a paragraph.

* List item 1  ✅ CORRECT
```

#### Cross-Reference Violations

**Error**: Using deprecated reference syntax
```asciidoc
<<../other/file.adoc#,Other Document>>  ❌ INCORRECT
```

**Correction**: Use xref syntax
```asciidoc
xref:../other/file.adoc[Other Document]  ✅ CORRECT
```

#### Code Block Violations

**Error**: Missing language specification
```asciidoc
----
public class Example {
}
----  ❌ INCORRECT
```

**Correction**: Include language specification
```asciidoc
[source,java]
----
public class Example {
}
----  ✅ CORRECT
```

## Validation Tools and Scripts

### Available Validation Scripts

The cui-documentation skill includes two validation scripts in the `scripts/` directory:

#### 1. AsciiDoc Format Validator (`asciidoc-validator.sh`)

Validates AsciiDoc format compliance:
* Checks for blank lines before lists
* Verifies section header formatting
* Detects list syntax issues
* Validates document structure

**Usage:**
```bash
# Validate a single file
scripts/asciidoc-validator.sh path/to/file.adoc

# Validate all files in a directory
scripts/asciidoc-validator.sh directory/

# CI/CD integration with JUnit output
scripts/asciidoc-validator.sh -f junit -s error directory/
```

**Common Validation Errors:**
* "Missing blank line before list" - Add blank line before list items
* "Invalid section header" - Check heading level syntax (`==`, `===`, etc.)
* "Unclosed code block" - Ensure code blocks have closing delimiters

#### 2. Auto-Formatting Script (`asciidoc-formatter.sh`)

Auto-fixes common AsciiDoc formatting issues:
* Adds blank lines before lists
* Converts deprecated `<<>>` syntax to `xref:`
* Fixes header attributes
* Removes trailing whitespace

**Usage:**
```bash
# Preview changes without modifying files (dry-run)
scripts/asciidoc-formatter.sh -n path/to/file.adoc

# Auto-fix all issues in a directory
scripts/asciidoc-formatter.sh directory/

# Fix only specific issue types
scripts/asciidoc-formatter.sh -t lists directory/

# Interactive mode - review each change
scripts/asciidoc-formatter.sh -i path/to/file.adoc
```

**Safe Operation:**
* Creates backup files by default (`.bak` extension)
* Use `-n` for dry-run to preview changes
* Use `-i` for interactive confirmation of each fix
* Use `-t` to target specific fix types

#### 3. Link Verification Script (`verify-adoc-links.py`)

Validates cross-reference links:
* Checks for broken file references
* Verifies anchor existence
* Detects deprecated link syntax
* Reports link integrity issues

**Usage:**
```bash
# Verify links in a single file
python3 scripts/verify-adoc-links.py --file path/to/file.adoc --report target/links.md

# Verify links in directory (non-recursive)
python3 scripts/verify-adoc-links.py --directory directory/ --report target/links.md

# Verify links recursively
python3 scripts/verify-adoc-links.py --directory directory/ --recursive --report target/links.md
```

**Interpreting Results:**

* **Syntax Valid + Target Exists**: ✅ Link is correct
* **Syntax Valid + Target Missing**: ❌ Reference to non-existent file
  - Common cause: Documentation for planned/future features
  - Action: Either create the target document or remove the reference
  - Do NOT leave references to non-existent files
* **Syntax Invalid**: ❌ Malformed cross-reference
  - Fix syntax to use proper `xref:path[text]` format

#### 4. Documentation Metrics Script (`documentation-stats.sh`)

Generates comprehensive statistics for AsciiDoc documentation:
* File counts and sizes
* Line and word counts
* Section structure and depth
* Cross-reference usage
* Media elements (images)
* Code blocks, tables, and lists

**Usage:**
```bash
# Basic statistics for current directory
scripts/documentation-stats.sh

# Generate JSON report for processing
scripts/documentation-stats.sh -f json directory/ > stats.json

# Detailed markdown report
scripts/documentation-stats.sh -f markdown -d > metrics.md

# Find largest documentation areas
scripts/documentation-stats.sh -s lines -g directory standards/
```

**Use Cases:**
* Track documentation growth over time
* Identify areas needing attention
* Generate metrics for reporting
* Monitor documentation health

### Validation Workflow

1. **Run format validation:**
   ```bash
   scripts/asciidoc-validator.sh target_file_or_directory 2>&1
   ```

2. **Auto-fix common issues (optional):**
   ```bash
   # Preview changes first
   scripts/asciidoc-formatter.sh -n target_file_or_directory

   # Apply fixes
   scripts/asciidoc-formatter.sh target_file_or_directory
   ```

3. **Run link verification:**
   ```bash
   mkdir -p target/asciidoc-reviewer
   python3 scripts/verify-adoc-links.py --file target.adoc --report target/asciidoc-reviewer/links.md 2>&1
   ```

4. **Review validation output and fix remaining issues**

5. **Re-run validation to confirm all fixes**

6. **Generate metrics (optional):**
   ```bash
   scripts/documentation-stats.sh -f markdown > doc-metrics.md
   ```

### Quality Assurance Standards

#### AsciiDoc Processing Compatibility

**Requirements:**
* Ensure compatibility with standard AsciiDoc processors
* Validate output in multiple rendering environments
* Test document generation in CI/CD pipelines
* Verify TOC generation and cross-reference resolution

#### Content Quality Standards

**Technical Writing Requirements:**
* Use clear, professional technical writing
* Maintain active voice where appropriate
* Use consistent terminology throughout documents
* Structure content logically with clear section flow
* Provide sufficient context for all technical concepts

**Documentation Completeness:**
* Include comprehensive examples for complex topics
* Provide step-by-step instructions for procedures
* Link to related documentation appropriately
* Include troubleshooting information where relevant

### CI/CD Integration

**Automated Checks:**
* AsciiDoc syntax validation
* Cross-reference link validation
* Document generation testing
* Style guide compliance verification

**Example CI/CD Integration:**
```yaml
documentation-validation:
  script:
    - scripts/asciidoc-validator.sh docs/
    - python3 scripts/verify-adoc-links.py --directory docs/ --recursive --report target/validation-report.md
  artifacts:
    reports:
      - target/validation-report.md
```

## Quality Checklist

- [ ] Document header complete with all required attributes
- [ ] Cross-references use `xref:` syntax
- [ ] Blank lines before all lists
- [ ] Code blocks have language specification
- [ ] Section hierarchy follows standards
- [ ] Links have descriptive text
- [ ] Tables properly formatted
- [ ] Admonitions used appropriately
- [ ] All validation scripts pass without errors
- [ ] All cross-reference links resolve correctly
- [ ] Document renders correctly in AsciiDoc processors

## References

* [documentation-core.md](documentation-core.md) - Core documentation principles
* [readme-structure.md](readme-structure.md) - README structure patterns
* [tone-and-style.md](tone-and-style.md) - Professional tone requirements
* [organization-standards.md](organization-standards.md) - Organization and structure
