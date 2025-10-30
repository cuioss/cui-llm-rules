# Documentation Core Standards

## Purpose
Comprehensive standards for all documentation across CUI projects, including general documentation rules and principles.

## Key Principles

1. **Consistency**: All documentation follows the same patterns and conventions
2. **Completeness**: Documentation covers all necessary aspects of the code
3. **Clarity**: Documentation is clear and understandable
4. **Maintainability**: Documentation is easy to update and maintain

## Core Documentation Standards

### Tone and Style Requirements

**MANDATORY**: All documentation must use:

* Professional, neutral, and objective tone
* No marketing language or promotional wording
* Factual descriptions with verifiable sources
* Technical precision without subjective claims
* Concise, clear language without verbosity

#### Marketing Language Detection

**Prohibited marketing language includes**:

* Marketing adjectives: "comprehensive," "powerful," "seamless," "robust," "enterprise-grade," "cutting-edge," "revolutionary," "amazing," "best-in-class"
* Promotional phrases: "Our solution," "We provide," "Industry-leading," "Unmatched performance"
* Bold/italic emphasis on features (e.g., "**powerful** validation")
* Superlatives: "fastest," "most reliable," "easiest to use"

**Correct replacements** (factual, measurable descriptions):
* "comprehensive validation" → "validates X, Y, and Z"
* "powerful features" → "supports features A, B, C"
* "seamless integration" → "integrates via CDI injection"

#### RFC References Verification

**When citing RFC specifications**:

* Verify RFC is relevant to the documented feature
* Check: Does the RFC actually define/require this behavior?
* Only cite RFCs that directly define the feature

**Example violations**:
* Citing HTTP/2 RFC (7540) in OAuth token validation docs
* Citing HTTP/1.1 RFC (7230) when discussing JWT claims

**Correct practice**: Only cite RFCs that directly define the feature being documented

### General Principles

* Only document existing code elements - no speculative or planned features
* All references must be verified to exist
* Use linking instead of duplication
* Code examples must come from actual unit tests
* Use consistent terminology across all documentation
* All public APIs must be documented
* All changes require successful documentation build

### Terminology Standards

* Maintain consistent technical terminology
* Apply terminology consistently across all documentation types
* Follow project glossary and naming conventions
* Use technical terms consistently

### Code Example Requirements

#### Technical Requirements

* Must be complete and compilable
* Include all necessary imports
* Show proper error handling
* Follow project coding standards
* Be verified by unit tests

#### Structure Requirements

* Start with setup/configuration
* Show main functionality
* Include error handling
* Demonstrate cleanup if needed
* Use clear variable names
* Include comments for complex steps

#### Configuration Examples - Placeholder Identification

**Requirements**:
* ALL placeholders must be clearly identified
* Use inline comments to mark placeholders
* Provide example values alongside placeholders

**Example (GOOD)**:
```properties
# Replace with your issuer URL
oauth.issuer=https://your-auth-server.com  # Placeholder: your actual auth server
oauth.audience=your-api-id                  # Placeholder: your API identifier
```

**Example (BAD)**:
```properties
oauth.issuer=https://your-auth-server.com
oauth.audience=your-api-id
```

## Documentation Quality

### Review Checklist

- [ ] Professional tone maintained
- [ ] No marketing language
- [ ] All references verified
- [ ] Code examples complete
- [ ] Consistent terminology
- [ ] Public APIs documented
- [ ] Documentation builds successfully

## References

* AsciiDoc Standards: asciidoc-formatting.md
* README Structure: readme-structure.md
