# CUI JavaDoc Documentation Skill

High-quality JavaDoc documentation standards for CUI Java projects.

## Overview

The `cui-javadoc` skill provides comprehensive JavaDoc standards covering:

- **Core Principles**: Clear documentation, tag usage, order, anti-patterns, maintenance
- **Class Documentation**: Packages, classes, interfaces, enums, annotations, generics
- **Method Documentation**: Public/private methods, constructors, builders, factories, varargs
- **Code Examples**: Inline code, code blocks, links, HTML formatting, tables, lists

## When to Use This Skill

Use `cui-javadoc` when:

- Documenting new Java classes, interfaces, or methods
- Reviewing or updating existing JavaDoc
- Adding code examples to documentation
- Creating package-info.java files
- Ensuring JavaDoc completeness and quality
- Generating API documentation with `mvn javadoc:javadoc`

## Prerequisites

**Required**:
- Java 17 or later
- Maven javadoc plugin
- Understanding of documented code functionality

**Recommended**:
- IDE with JavaDoc preview (IntelliJ, Eclipse)
- JavaDoc validation in CI/CD pipeline

## Standards Included

### 1. Core JavaDoc Standards (`javadoc-core.md`)

**Always loaded** - Foundation for all JavaDoc:

- Start with clear purpose (what and why)
- Avoid stating the obvious
- Focus on behavior, not implementation
- Document contracts, not code
- Keep documentation synchronized with code
- Standard tag order (@param, @return, @throws, @see, @since, @deprecated)
- HTML tag closure and formatting
- Consistency across related classes

### 2. Class Documentation (`javadoc-class-documentation.md`)

**Load when**: Documenting classes, interfaces, packages, enums, annotations

- package-info.java files with @NullMarked documentation
- Class/interface purpose and behavior
- Thread-safety statements
- Usage examples for complex classes
- Inheritance relationships (@see superclass)
- Serialization documentation
- Generic type parameters (@param <T>)
- Abstract class contracts
- Enum value descriptions
- Annotation usage examples

### 3. Method Documentation (`javadoc-method-documentation.md`)

**Load when**: Documenting methods or fields

- All public/protected methods documented
- Parameter constraints and validation (@param)
- Return value guarantees (@return)
- Exception conditions (@throws)
- Null-safety contracts (with @NullMarked)
- Constructor documentation
- Builder pattern documentation
- Factory method documentation
- Fluent API documentation
- Generic method type parameters
- Varargs parameter documentation
- Field documentation (when public/protected)

### 4. Code Examples (`javadoc-code-examples.md`)

**Load when**: Adding code examples or complex formatting

- Inline code with {@code} and {@literal}
- Code blocks with <pre><code class="language-java">
- Links with {@link ClassName#method}
- HTML formatting (bold, italic, paragraphs)
- Tables for complex information
- Lists (ordered and unordered)
- Complete compilable examples
- Example verification in tests

## Quick Start

### 1. Document a Class

```java
/**
 * Validates JWT tokens according to RFC 7519 standards.
 *
 * <p>This validator checks token signature, expiration, and issuer claims.
 * All validations are performed according to the configured {@link TokenConfig}.
 *
 * <p><b>Thread Safety</b>: This class is immutable and thread-safe.
 *
 * <h3>Usage Example</h3>
 * <pre><code class="language-java">
 * TokenConfig config = TokenConfig.builder()
 *     .issuer("https://auth.example.com")
 *     .validity(Duration.ofHours(1))
 *     .build();
 *
 * TokenValidator validator = new TokenValidator(config);
 * ValidationResult result = validator.validate(jwtToken);
 * </code></pre>
 *
 * @see TokenConfig
 * @see ValidationResult
 * @since 1.0
 */
@NullMarked
public class TokenValidator {
    // Implementation
}
```

### 2. Document package-info.java

```java
/**
 * JWT token validation and authentication services.
 *
 * <p>This package provides comprehensive JWT token validation following RFC 7519,
 * including signature verification, expiration checking, and claim validation.
 *
 * <h2>Core Components</h2>
 * <ul>
 *   <li>{@link de.cuioss.auth.TokenValidator} - Main validation service</li>
 *   <li>{@link de.cuioss.auth.TokenConfig} - Validator configuration</li>
 *   <li>{@link de.cuioss.auth.ValidationResult} - Validation result</li>
 * </ul>
 *
 * <p><b>Null Safety</b>: All types in this package are non-null by default due to
 * {@code @NullMarked}. Use {@code @Nullable} to explicitly mark nullable types.
 *
 * @see <a href="https://tools.ietf.org/html/rfc7519">RFC 7519: JWT Specification</a>
 */
@NullMarked
package de.cuioss.auth;

import org.jspecify.annotations.NullMarked;
```

### 3. Document a Method

```java
/**
 * Validates a JWT token and returns the validation result.
 *
 * <p>This method performs comprehensive validation including:
 * <ul>
 *   <li>Signature verification using configured public key</li>
 *   <li>Expiration check with clock skew tolerance</li>
 *   <li>Issuer claim validation</li>
 *   <li>Required claims presence check</li>
 * </ul>
 *
 * @param token the JWT token to validate, must not be {@code null} or empty
 * @return validation result containing status and error details, never {@code null}
 * @throws ValidationException if token format is invalid or signature cannot be verified
 * @throws NullPointerException if {@code token} is {@code null}
 * @see ValidationResult
 * @see TokenConfig
 */
public ValidationResult validate(String token) throws ValidationException {
    Objects.requireNonNull(token, "token must not be null");
    // Implementation
}
```

### 4. Add Code Examples

```java
/**
 * Builds a new {@link TokenConfig} with the specified parameters.
 *
 * <h3>Basic Usage</h3>
 * <pre><code class="language-java">
 * TokenConfig config = TokenConfig.builder()
 *     .issuer("https://auth.example.com")
 *     .validity(Duration.ofHours(1))
 *     .build();
 * </code></pre>
 *
 * <h3>With All Options</h3>
 * <pre><code class="language-java">
 * TokenConfig config = TokenConfig.builder()
 *     .issuer("https://auth.example.com")
 *     .audience("my-api")
 *     .validity(Duration.ofHours(1))
 *     .clockSkewSeconds(30)
 *     .requiredClaim("sub")
 *     .requiredClaim("exp")
 *     .build();
 * </code></pre>
 */
public static class Builder {
    // Builder implementation
}
```

## Integration with Other Skills

**Recommended skill combinations**:

```yaml
# Complete Java development with documentation
skills:
  - cui-java-core      # Java patterns and coding standards
  - cui-javadoc        # JavaDoc standards (this skill)
  - cui-java-unit-testing  # Testing standards

# Documentation-focused
skills:
  - cui-javadoc        # Java code documentation
  - cui-documentation  # General documentation (README, AsciiDoc)
```

## Common Documentation Tasks

### Document a New Public API

1. Add class-level JavaDoc with purpose and behavior
2. Document thread-safety if applicable
3. Add usage example for complex classes
4. Document all public methods
5. Include parameter constraints and return guarantees
6. Document all exceptions
7. Add @see links to related classes
8. Add @since tag for version
9. Verify: `mvn javadoc:javadoc`

### Review Existing Documentation

1. Check for undocumented public APIs
2. Verify all parameters/returns/exceptions documented
3. Update outdated documentation
4. Fix "stating the obvious" documentation
5. Validate all {@link} references
6. Check HTML tag closure
7. Ensure tag order compliance

### Add Code Examples

1. Write complete, compilable examples
2. Use <pre><code class="language-java"> blocks
3. Include typical usage scenarios
4. Show error handling if applicable
5. Verify examples in unit tests
6. Keep examples concise (< 10 lines preferred)

## Prohibited Practices

**DO NOT**:
- State the obvious ("Returns the name" for getName())
- Document implementation details
- Duplicate information from related classes
- Use broken {@link} references
- Leave HTML tags unclosed
- Skip parameter or return documentation
- Document private implementation details
- Use wrong tag order

## Verification Checklist

After applying this skill:

**Documentation Completeness**:
- [ ] All public/protected classes documented
- [ ] All public/protected methods documented
- [ ] All parameters documented with constraints
- [ ] All return values documented
- [ ] All exceptions documented
- [ ] package-info.java files created
- [ ] Thread-safety documented where applicable

**Documentation Quality**:
- [ ] Clear purpose statements (what and why)
- [ ] No "stating the obvious" documentation
- [ ] Behavior documented, not implementation
- [ ] All {@link} references valid
- [ ] HTML tags properly closed
- [ ] Standard tag order followed
- [ ] Code examples compilable

**Build Verification**:
- [ ] JavaDoc builds without errors: `mvn javadoc:javadoc`
- [ ] All links resolve correctly
- [ ] No missing @param or @return warnings

## Quality Standards

This skill enforces:

- **Completeness**: All public APIs documented
- **Clarity**: Clear purpose and behavior descriptions
- **Accuracy**: Documentation matches code behavior
- **Consistency**: Uniform style across related classes
- **Maintainability**: Easy to update when code changes
- **Usefulness**: Adds value beyond obvious code reading

## Examples

See standards files for comprehensive examples including:

- Class documentation with usage examples
- package-info.java templates
- Method documentation with parameters/returns/exceptions
- Generic type parameter documentation
- Builder pattern documentation
- Code examples with formatting
- HTML tables and lists
- Cross-references and links

## Support

For issues or questions:

1. Review detailed standards in `standards/` directory
2. Check code examples in standards files
3. Verify JavaDoc builds: `mvn javadoc:javadoc`
4. Use IDE JavaDoc preview
5. Refer to JSpecify documentation for null-safety

## License

Part of the CUI LLM Rules documentation system for CUI OSS projects.
