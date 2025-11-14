# Token Validation Documentation Examples

## Purpose

This directory contains example documentation files that demonstrate documentation standards and best practices taught in the cui-documentation skill.

These examples are **illustrative** - they show how to properly organize, cross-reference, and structure technical documentation.

## Example Files

### Token Validation Documentation Set

This set demonstrates the "No Duplication" principle with proper cross-referencing:

* **[token-validation-core.md](token-validation-core.md)** - Core validation process (single source of truth)
  * Defines standard validation steps used by all token types
  * Referenced by JWT and OAuth2 specific docs

* **[jwt-validation.md](jwt-validation.md)** - JWT-specific requirements
  * Extends core validation with JWT-specific checks
  * Cross-references core doc instead of duplicating common steps

* **[oauth2-validation.md](oauth2-validation.md)** - OAuth2-specific requirements
  * Extends core validation with OAuth2-specific checks
  * Cross-references core doc instead of duplicating common steps

* **[validation-testing.md](validation-testing.md)** - Testing requirements
  * Comprehensive testing standards for token validation
  * References validation docs for requirements being tested

## Patterns Demonstrated

### ✅ No Duplication
Common validation steps are defined once in `token-validation-core.md` and referenced by other docs.

### ✅ Cross-Referencing
Each document explicitly references related documents:
```markdown
Token validation follows the [standard validation process](token-validation-core.md).
```

### ✅ Single Source of Truth
Core concepts have one authoritative location:
* Standard validation: `token-validation-core.md`
* JWT specifics: `jwt-validation.md`
* OAuth2 specifics: `oauth2-validation.md`

### ✅ Clear Structure
Each document follows consistent structure:
* Purpose section
* Requirements/Standards
* Configuration
* Error Handling
* See Also (cross-references)

## Usage

These examples are referenced in organization-standards.md to demonstrate:
* How to avoid content duplication
* How to structure cross-references
* How to organize related documentation
* How to maintain single source of truth

## See Also

* [organization-standards.md](../standards/organization-standards.md) - Documentation organization principles
* [documentation-core.md](../standards/documentation-core.md) - Core documentation standards
