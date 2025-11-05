---
name: cui-requirements:implementation-linkage
source_bundle: cui-requirements
description: Standards for linking specifications to implementation code and maintaining bidirectional traceability between documentation and source code
version: 1.0.0
allowed-tools: []
---

# Implementation Linkage Standards

Standards for connecting specification documents with implementation code, establishing bidirectional traceability, and maintaining documentation throughout the implementation lifecycle.

## Core Principles

### Holistic System View

Effective documentation provides a complete view at multiple levels:

- **Requirements level**: What the system must accomplish
- **Specification level**: How the system should be designed
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

Specification documents should contain:

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

Implementation code documentation (JavaDoc) should contain:

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

### Implementation Status Section

When implementation exists, add status section:

```asciidoc
== Token Validation
_See Requirement link:../Requirements.adoc#JWT-1[JWT-1: Token Validation Framework]_

=== Status: IMPLEMENTED

This specification is implemented in the following classes:

* link:../src/main/java/com/example/jwt/TokenValidator.java[TokenValidator] - Main validation orchestration
* link:../src/main/java/com/example/jwt/SignatureValidator.java[SignatureValidator] - Signature verification
* link:../src/main/java/com/example/jwt/ClaimValidator.java[ClaimValidator] - Claim validation

For detailed implementation behavior, refer to the JavaDoc of these classes.

=== Verification

This specification is verified by:

* link:../src/test/java/com/example/jwt/TokenValidatorTest.java[TokenValidatorTest]
* link:../src/test/java/com/example/jwt/integration/TokenValidationIntegrationTest.java[TokenValidationIntegrationTest]
```

### Multiple Component Implementation

When specification covers multiple components:

```asciidoc
== Security Framework
_See Requirement link:../Requirements.adoc#SEC-1[SEC-1: Security Requirements]_

=== Status: IMPLEMENTED

The security framework is implemented across the following components:

==== Authentication
* link:../src/main/java/com/example/auth/Authenticator.java[Authenticator]
* link:../src/main/java/com/example/auth/AuthenticationProvider.java[AuthenticationProvider]

==== Authorization
* link:../src/main/java/com/example/authz/Authorizer.java[Authorizer]
* link:../src/main/java/com/example/authz/PermissionChecker.java[PermissionChecker]

==== Token Management
* link:../src/main/java/com/example/token/TokenManager.java[TokenManager]
* link:../src/main/java/com/example/token/TokenStore.java[TokenStore]
```

## Code-to-Specification Linking Standards

### JavaDoc Links to Specifications

**Basic specification reference**:
```java
/**
 * Validates JWT tokens according to RFC 7519.
 * <p>
 * For architectural overview and requirements, see the
 * <a href="../../../../../../../doc/specification/token-validation.adoc">Token Validation Specification</a>.
 *
 * @author John Doe
 */
public class TokenValidator {
    // Implementation
}
```

**Requirement reference**:
```java
/**
 * Implements token signature validation.
 * <p>
 * Implements requirement: {@code JWT-1.1: Signature Validation}
 * <p>
 * For detailed requirements, see the
 * <a href="../../../../../../../doc/specification/token-validation.adoc#_signature_validation">Signature Validation Specification</a>.
 */
public class SignatureValidator {
    // Implementation
}
```

**Multiple references**:
```java
/**
 * Manages token lifecycle including validation, caching, and revocation.
 * <p>
 * Implements requirements:
 * <ul>
 *   <li>{@code JWT-1: Token Validation Framework}</li>
 *   <li>{@code JWT-8: Token Caching}</li>
 *   <li>{@code JWT-9: Token Revocation}</li>
 * </ul>
 * <p>
 * For detailed specifications, see:
 * <ul>
 *   <li><a href="../../../../../../../doc/specification/token-validation.adoc">Token Validation Specification</a></li>
 *   <li><a href="../../../../../../../doc/specification/caching.adoc">Caching Specification</a></li>
 * </ul>
 */
public class TokenManager {
    // Implementation
}
```

### Path Calculation for Relative Links

Calculate relative path from source file to doc:

**From `src/main/java/com/example/`**: `../../../../../../../doc/`

**From `src/test/java/com/example/`**: `../../../../../../../doc/`

**Formula**: Count directory levels from `src/` to file, then use that many `../` to reach project root, then add `doc/`

### Method-Level Requirement References

For methods implementing specific requirements:

```java
/**
 * Validates token expiration timestamp.
 * <p>
 * Implements requirement: {@code JWT-4: Token Expiration Handling}
 * <p>
 * Checks if the token's 'exp' claim is in the future, accounting for
 * configurable clock skew tolerance.
 *
 * @param token the JWT token to validate
 * @param clockSkew maximum allowed clock skew in seconds
 * @return true if token is not expired
 * @throws TokenExpiredException if token has expired
 */
public boolean validateExpiration(JwtToken token, int clockSkew) {
    // Implementation
}
```

## Documentation Update Workflow

### Pre-Implementation Phase

When specifications exist but implementation hasn't started:

**Specification content**:
```asciidoc
== Token Validation
_See Requirement link:../Requirements.adoc#JWT-1[JWT-1: Token Validation Framework]_

=== Status: PLANNED

The token validation component must provide comprehensive JWT validation according to RFC 7519.

=== Expected API

[source,java]
----
public interface TokenValidator {
    ValidationResult validate(String token);
}
----

=== Validation Flow

1. Parse token into header, payload, signature
2. Verify signature using configured algorithm
3. Validate standard claims (exp, nbf, iat)
4. Return validation result
```

### During Implementation Phase

As implementation progresses:

1. **Add implementation links**:
```asciidoc
=== Status: IN PROGRESS

Currently implementing in:

* link:../src/main/java/com/example/jwt/TokenValidator.java[TokenValidator] (in progress)
```

2. **Add JavaDoc with specification references**:
```java
/**
 * Validates JWT tokens according to RFC 7519.
 * <p>
 * For requirements and design, see the
 * <a href="../../../../../../../doc/specification/token-validation.adoc">Token Validation Specification</a>.
 */
```

3. **Update specification with implementation decisions**:
```asciidoc
=== Implementation Notes

The implementation uses the jose4j library for cryptographic operations.
Configuration is provided through CDI producers.
```

### Post-Implementation Phase

After implementation is complete and tested:

1. **Update status**:
```asciidoc
=== Status: IMPLEMENTED
```

2. **Add complete implementation references**:
```asciidoc
This specification is implemented in:

* link:../src/main/java/com/example/jwt/TokenValidator.java[TokenValidator]
* link:../src/main/java/com/example/jwt/TokenValidatorFactory.java[TokenValidatorFactory]

For detailed behavior, refer to the implementation and associated JavaDoc.
```

3. **Add test references**:
```asciidoc
=== Verification

Test coverage is provided by:

* link:../src/test/java/com/example/jwt/TokenValidatorTest.java[TokenValidatorTest]
* link:../src/test/java/com/example/jwt/integration/ValidationIntegrationTest.java[ValidationIntegrationTest]
```

4. **Remove redundant content**:
- Remove code examples that duplicate actual implementation
- Remove detailed API descriptions covered in JavaDoc
- Keep architectural guidance and design rationale
- Keep standards and constraints

5. **Refine content**:
```asciidoc
== Token Validation
_See Requirement link:../Requirements.adoc#JWT-1[JWT-1: Token Validation Framework]_

=== Status: IMPLEMENTED

Implementation:

* link:../src/main/java/com/example/jwt/TokenValidator.java[TokenValidator]
* link:../src/main/java/com/example/jwt/SignatureValidator.java[SignatureValidator]
* link:../src/main/java/com/example/jwt/ClaimValidator.java[ClaimValidator]

The implementation follows RFC 7519 standards and uses the jose4j library for cryptographic operations. Configuration is provided through CDI with sensible defaults.

For detailed implementation behavior and API usage, refer to the JavaDoc of the implementing classes.

=== Verification

Test coverage:

* link:../src/test/java/com/example/jwt/TokenValidatorTest.java[TokenValidatorTest]
* link:../src/test/java/com/example/jwt/integration/ValidationIntegrationTest.java[ValidationIntegrationTest]

Test coverage exceeds 90% for validation logic.
```

## Verification and Validation Linking

### Test Specification Sections

Include test verification in specifications:

```asciidoc
== Token Validation Testing
_See Requirement link:../Requirements.adoc#JWT-1[JWT-1: Token Validation Framework]_

_See link:testing.adoc#_validation_testing[Testing Specification] for detailed test approach_

=== Status: IMPLEMENTED

=== Unit Tests

* link:../src/test/java/com/example/jwt/TokenValidatorTest.java[TokenValidatorTest] - Core validation logic
* link:../src/test/java/com/example/jwt/SignatureValidatorTest.java[SignatureValidatorTest] - Signature verification
* link:../src/test/java/com/example/jwt/ClaimValidatorTest.java[ClaimValidatorTest] - Claim validation

=== Integration Tests

* link:../src/test/java/com/example/jwt/integration/TokenValidationIntegrationTest.java[TokenValidationIntegrationTest] - End-to-end validation flows
* link:../src/test/java/com/example/jwt/integration/PerformanceTest.java[PerformanceTest] - Performance verification

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

## Example Complete Linkage

### Specification Document

```asciidoc
= JWT Token Processor - Token Validation
:toc: left
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js

link:../Specification.adoc[Back to Main Specification]

== Token Validation Architecture
_See Requirement link:../Requirements.adoc#JWT-1[JWT-1: Token Validation Framework]_

=== Status: IMPLEMENTED

The token validation architecture provides comprehensive JWT validation according to RFC 7519.

=== Implementation

The following classes implement this specification:

* link:../src/main/java/com/example/jwt/TokenValidator.java[TokenValidator] - Main validation orchestration
* link:../src/main/java/com/example/jwt/SignatureValidator.java[SignatureValidator] - Signature verification
* link:../src/main/java/com/example/jwt/ClaimValidator.java[ClaimValidator] - Claim validation

The implementation uses the jose4j library for cryptographic operations and provides a fluent API for configuration.

For detailed behavior and API usage, refer to the JavaDoc of these classes.

=== Verification

Test coverage is provided by:

* link:../src/test/java/com/example/jwt/TokenValidatorTest.java[TokenValidatorTest]
* link:../src/test/java/com/example/jwt/SignatureValidatorTest.java[SignatureValidatorTest]
* link:../src/test/java/com/example/jwt/ClaimValidatorTest.java[ClaimValidatorTest]
* link:../src/test/java/com/example/jwt/integration/ValidationIntegrationTest.java[ValidationIntegrationTest]

Test coverage: 92% line coverage, 88% branch coverage.
```

### Implementation JavaDoc

```java
package com.example.jwt;

/**
 * Validates JWT tokens according to RFC 7519.
 * <p>
 * This class provides comprehensive token validation including signature verification,
 * claim validation, and expiration checking.
 * <p>
 * <strong>Requirements:</strong> Implements requirement {@code JWT-1: Token Validation Framework}
 * <p>
 * <strong>Specification:</strong> For architectural overview and design details, see the
 * <a href="../../../../../../../doc/specification/token-validation.adoc">Token Validation Specification</a>.
 *
 * <h2>Usage Example</h2>
 * <pre>{@code
 * TokenValidator validator = TokenValidatorFactory.create();
 * ValidationResult result = validator.validate(jwtToken);
 *
 * if (result.isValid()) {
 *     TokenClaims claims = result.getClaims().get();
 *     // Process valid token
 * } else {
 *     // Handle validation errors
 *     result.getErrors().forEach(error -> log.warn("Validation error: {}", error));
 * }
 * }</pre>
 *
 * <h2>Thread Safety</h2>
 * This class is thread-safe and can be shared across multiple threads.
 *
 * <h2>Performance</h2>
 * Validation typically completes in under 10ms for valid tokens. Performance degrades
 * gracefully for invalid tokens with early termination of validation checks.
 *
 * @author John Doe
 * @see TokenValidatorFactory
 * @see ValidationResult
 * @since 1.0.0
 */
public class TokenValidator {

    /**
     * Validates a JWT token.
     * <p>
     * Implements requirement: {@code JWT-1: Token Validation Framework}
     * <p>
     * The validation process:
     * <ol>
     *   <li>Parses token into header, payload, and signature</li>
     *   <li>Verifies signature using configured algorithm</li>
     *   <li>Validates standard claims (exp, nbf, iat)</li>
     *   <li>Validates custom claims if configured</li>
     * </ol>
     *
     * @param token the JWT token string to validate
     * @return validation result containing claims if valid, or errors if invalid
     * @throws IllegalArgumentException if token is null or empty
     */
    public ValidationResult validate(String token) {
        // Implementation
    }
}
```

### Test JavaDoc

```java
package com.example.jwt;

/**
 * Unit tests for {@link TokenValidator}.
 * <p>
 * Verifies implementation against the
 * <a href="../../../../../../../doc/specification/token-validation.adoc">Token Validation Specification</a>.
 * <p>
 * <strong>Coverage:</strong> Tests cover all validation scenarios including:
 * <ul>
 *   <li>Valid token validation</li>
 *   <li>Expired token handling (JWT-4)</li>
 *   <li>Invalid signature detection (JWT-1.1)</li>
 *   <li>Malformed token handling (JWT-2)</li>
 *   <li>Missing required claims (JWT-3)</li>
 * </ul>
 *
 * @author John Doe
 */
public class TokenValidatorTest {
    // Tests
}
```

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

- `cui-requirements:specification-documentation` - Standards for creating specification documents that link to implementation
- `cui-requirements:requirements-documentation` - Standards for requirements documentation providing traceability foundation
- `cui-requirements:project-setup` - Standards for setting up documentation structure in new projects
- `cui-requirements:planning-documentation` - Standards for planning documents that track implementation tasks

### External Standards

- JavaDoc standards (for implementation documentation)
- Testing standards (for test documentation)
