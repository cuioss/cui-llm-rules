# CUI Requirements Skill

Requirements engineering and planning standards for CUI projects.

## Overview

The `cui-requirements` skill provides standards for:

- **Requirements Core**: SMART criteria, structure, quality attributes, traceability
- **Specification Standards**: Technical specifications, architecture, interfaces, data models

## When to Use This Skill

Use `cui-requirements` when:

- Gathering and documenting project requirements
- Creating technical specifications
- Planning new features or modules
- Defining acceptance criteria
- Documenting non-functional requirements
- Establishing project constraints and dependencies

## Prerequisites

**Required**:
- Understanding of project domain
- Access to stakeholders
- Documentation tools (AsciiDoc, Markdown)

**Recommended**:
- Requirements management tool
- Collaboration platform
- Version control for documents

## Standards Included

### 1. Requirements Core (`requirements-core.md`)

**Always loaded** - Foundation for all requirements:

**Document Structure**:
- Clear title and overview
- Background and context
- Functional requirements (MUST, SHOULD, MAY)
- Non-functional requirements
- Constraints and dependencies
- Success criteria
- Acceptance criteria

**SMART Requirements**:
- **Specific**: Clear and unambiguous
- **Measurable**: Quantifiable criteria
- **Achievable**: Realistic and attainable
- **Relevant**: Aligned with business goals
- **Time-bound**: Clear deadlines where applicable

**Quality Attributes**:
- Completeness: All aspects covered
- Consistency: No contradictions
- Clarity: Easily understood
- Testability: Can be verified
- Traceability: Linked to design and tests

### 2. Specification Standards (`specification-standards.md`)

**Load when**: Creating technical specifications

**Technical Specifications**:
- Architecture overview
- Component design
- Interface specifications
- Data models and schemas
- API specifications
- Integration points
- Technology stack

**Design Documentation**:
- UML diagrams where appropriate
- Sequence diagrams for workflows
- Class diagrams for domain model
- Component diagrams for architecture
- Database schemas

## Quick Start

### 1. Feature Requirements Document

```markdown
# Feature: JWT Token Validation

## Overview

Implement JWT token validation following RFC 7519 standards for secure authentication.

## Background

The application needs to validate JWT tokens from external authentication providers.
Current authentication mechanism lacks standardized token validation.

## Functional Requirements

### MUST Requirements

1. **MUST** validate JWT token signature using configured public key
2. **MUST** verify token expiration with clock skew tolerance (30 seconds)
3. **MUST** validate issuer claim against configuration
4. **MUST** check presence of required claims (sub, exp)
5. **MUST** return detailed validation result with error information

### SHOULD Requirements

1. **SHOULD** support multiple token issuers
2. **SHOULD** provide configurable clock skew tolerance
3. **SHOULD** cache public keys for performance
4. **SHOULD** log validation failures with appropriate log levels

### MAY Requirements

1. **MAY** support custom claim validation
2. **MAY** provide token refresh functionality

## Non-Functional Requirements

### Performance
- Token validation **MUST** complete within 100ms (95th percentile)
- Public key caching **SHOULD** reduce validation time by 50%

### Security
- **MUST** use cryptographically secure signature verification
- **MUST** protect against timing attacks
- **MUST** validate all security-relevant claims

### Reliability
- **MUST** achieve 99.9% uptime
- **SHOULD** gracefully handle network failures

### Maintainability
- **MUST** follow CUI Java coding standards
- **MUST** achieve 80% test coverage
- **SHOULD** provide comprehensive JavaDoc

## Constraints

- **MUST** use Java 17 or later
- **MUST** be compatible with Quarkus framework
- **MUST** not introduce new external dependencies without approval

## Dependencies

- Requires public key management system
- Depends on cui-java-tools for logging
- Requires JSpecify for null-safety

## Success Criteria

- All functional requirements implemented
- All tests passing with 80%+ coverage
- Performance benchmarks met
- Security audit passed
- Documentation complete

## Acceptance Criteria

### Scenario 1: Valid Token

**Given** a valid JWT token with correct signature and claims
**When** the validator processes the token
**Then** validation result is success
**And** no errors are reported

### Scenario 2: Expired Token

**Given** a JWT token with expiration in the past
**When** the validator processes the token
**Then** validation result is failure
**And** error indicates "token expired"

### Scenario 3: Invalid Signature

**Given** a JWT token with tampered signature
**When** the validator processes the token
**Then** validation result is failure
**And** error indicates "invalid signature"
```

### 2. Technical Specification

```markdown
# Technical Specification: JWT Token Validator

## Architecture

### Components

```
┌─────────────────────┐
│ TokenValidator      │
│ (Main Interface)    │
└──────────┬──────────┘
           │
    ┌──────┴──────────────────┐
    │                         │
┌───┴────────────┐  ┌─────────┴────────┐
│ SignatureVerifier│  │ ClaimValidator   │
└────────────────┘  └──────────────────┘
```

### Component Responsibilities

**TokenValidator**:
- Orchestrates validation process
- Coordinates signature and claim validation
- Returns comprehensive validation result

**SignatureVerifier**:
- Verifies JWT signature using public key
- Handles key caching and rotation
- Protects against timing attacks

**ClaimValidator**:
- Validates standard claims (exp, iss, sub)
- Checks custom required claims
- Applies clock skew tolerance

## Interfaces

### TokenValidator Interface

```java
public interface TokenValidator {
    /**
     * Validates JWT token and returns result.
     *
     * @param token JWT token to validate
     * @return validation result with status and errors
     * @throws NullPointerException if token is null
     */
    ValidationResult validate(String token);

    /**
     * Validates JWT token and extracts user info.
     *
     * @param token JWT token to validate
     * @return user info if valid, empty if invalid
     */
    Optional<UserInfo> extractUserInfo(String token);
}
```

### ValidationResult Data Model

```java
@Value
@Builder
public class ValidationResult {
    boolean valid;
    List<String> errors;
    Instant validatedAt;

    public static ValidationResult valid() {
        return new ValidationResult(true, List.of(), Instant.now());
    }

    public static ValidationResult invalid(String... errors) {
        return new ValidationResult(false, List.of(errors), Instant.now());
    }
}
```

## Configuration

### Application Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `token.issuer` | String | - | JWT token issuer URL (required) |
| `token.validity` | Duration | PT1H | Default token validity |
| `token.clock-skew` | Integer | 30 | Clock skew tolerance (seconds) |
| `token.required-claims` | List<String> | sub,exp | Required claim names |

### Configuration Example

```java
@ConfigMapping(prefix = "token")
public interface TokenConfig {
    String issuer();
    Duration validity();
    int clockSkew();
    List<String> requiredClaims();
}
```

## Data Flow

1. Client submits JWT token
2. TokenValidator receives token
3. SignatureVerifier validates signature
4. ClaimValidator checks expiration with clock skew
5. ClaimValidator validates issuer
6. ClaimValidator checks required claims
7. ValidationResult returned to client

## Error Handling

| Error Condition | Error Code | HTTP Status | Action |
|----------------|------------|-------------|--------|
| Null token | INVALID_INPUT | 400 | Reject |
| Invalid signature | INVALID_SIGNATURE | 401 | Reject |
| Expired token | TOKEN_EXPIRED | 401 | Reject |
| Invalid issuer | INVALID_ISSUER | 401 | Reject |
| Missing claims | MISSING_CLAIMS | 401 | Reject |

## Testing Strategy

### Unit Tests
- Test signature verification with valid/invalid keys
- Test expiration validation with clock skew
- Test claim validation logic
- Test error handling for all failure scenarios

### Integration Tests
- Test with real JWT tokens from provider
- Test public key retrieval and caching
- Test performance under load
- Test concurrent validation requests

### Performance Tests
- Validate 95th percentile < 100ms
- Test with 1000 concurrent requests
- Verify cache effectiveness

## Security Considerations

- Use constant-time signature comparison
- Validate all input parameters
- Protect against replay attacks
- Log security-relevant events
- Rotate keys periodically
```

## Integration with Other Skills

**Recommended skill combinations**:

```yaml
# Requirements and documentation
skills:
  - cui-requirements      # Requirements and specs (this skill)
  - cui-documentation     # README and general docs
  - cui-project-setup     # Project setup

# Complete development workflow
skills:
  - cui-requirements      # Requirements first
  - cui-project-setup     # Then setup
  - cui-java-core         # Then development
  - cui-java-unit-testing # Then testing
```

## Common Requirements Tasks

### Create Feature Requirements

1. Document overview and background
2. Identify functional requirements (MUST/SHOULD/MAY)
3. Define non-functional requirements (performance, security)
4. List constraints and dependencies
5. Define success criteria
6. Write acceptance criteria (Given/When/Then)
7. Review with stakeholders

### Write Technical Specification

1. Design architecture and components
2. Define interfaces and contracts
3. Document data models
4. Specify configuration
5. Describe data flow
6. Plan error handling
7. Define testing strategy

### Review Requirements Quality

1. Verify SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)
2. Check completeness (all aspects covered)
3. Ensure consistency (no contradictions)
4. Validate testability (can be verified)
5. Confirm traceability (linked to design)

## Prohibited Practices

**DO NOT**:
- Use vague or ambiguous language
- Mix requirements with implementation details
- Skip non-functional requirements
- Forget acceptance criteria
- Omit constraints and dependencies
- Leave requirements untestable
- Document without stakeholder review

## Verification Checklist

After creating requirements:

**Document Structure**:
- [ ] Title and overview present
- [ ] Background and context provided
- [ ] Functional requirements categorized (MUST/SHOULD/MAY)
- [ ] Non-functional requirements defined
- [ ] Constraints and dependencies listed
- [ ] Success criteria established
- [ ] Acceptance criteria written

**Quality Attributes**:
- [ ] Requirements are specific and clear
- [ ] Requirements are measurable
- [ ] Requirements are achievable
- [ ] Requirements are relevant to goals
- [ ] Requirements are testable
- [ ] No contradictions present
- [ ] All aspects covered

**Stakeholder Review**:
- [ ] Requirements reviewed with stakeholders
- [ ] Feedback incorporated
- [ ] Acceptance criteria agreed upon
- [ ] Priorities established

## Quality Standards

This skill enforces:

- **SMART criteria**: All requirements must be specific, measurable, achievable, relevant, time-bound
- **Completeness**: All aspects documented
- **Consistency**: No contradictions
- **Testability**: Can be verified
- **Traceability**: Linked to implementation

## Examples

See standards files for comprehensive examples including:

- Feature requirements templates
- Technical specification templates
- Acceptance criteria patterns
- Non-functional requirements
- Architecture documentation
- Interface specifications

## Support

For issues or questions:

1. Review detailed standards in `standards/` directory
2. Consult stakeholders for clarification
3. Review existing requirements for patterns
4. Use templates provided in standards
5. Validate against SMART criteria

## License

Part of the CUI LLM Rules documentation system for CUI OSS projects.
