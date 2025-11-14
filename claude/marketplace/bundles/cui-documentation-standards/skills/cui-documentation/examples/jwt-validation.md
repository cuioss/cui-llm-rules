# JWT Token Validation

## Purpose

This document defines JWT-specific validation requirements that extend the [standard validation process](token-validation-core.md).

## JWT-Specific Validation

Token validation follows the [standard validation process](token-validation-core.md) with these additional JWT-specific checks:

### Header Validation

* **Algorithm**: Must be one of the allowed algorithms (RS256, RS384, RS512)
* **Type**: Must be `JWT`
* **Key ID**: Must reference a known public key when using RS* algorithms

### Payload Validation

In addition to standard claims (exp, iss, aud), validate JWT-specific claims:

* **Subject (sub)**: Must be present and non-empty
* **Issued At (iat)**: Must be present and not in the future
* **JWT ID (jti)**: When present, must be unique (check against revocation list)

### JWT-Specific Error Codes

* **Missing Subject**: Return HTTP 401 with error code `JWT_MISSING_SUBJECT`
* **Future Issued At**: Return HTTP 401 with error code `JWT_INVALID_IAT`
* **Revoked JWT ID**: Return HTTP 401 with error code `JWT_REVOKED`

## Configuration

```yaml
jwt-validation:
  allowed-algorithms:
    - RS256
    - RS384
    - RS512
  require-jti: false
  revocation-check-enabled: true
```

## See Also

* [Core Validation](token-validation-core.md) - Common validation requirements
* [Testing Standards](validation-testing.md) - Testing requirements for JWT validation
