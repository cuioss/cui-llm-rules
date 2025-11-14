# Core Token Validation

## Purpose

This document defines the standard validation process common to all token types (JWT, OAuth2, etc.).

## Standard Validation Process

All token validation must follow these steps:

1. **Parse the token**
   - Extract header, payload, and signature components
   - Validate token structure and format

2. **Verify signature**
   - Use appropriate algorithm (RS256, HS256, etc.)
   - Validate against configured public key or shared secret
   - Reject tokens with invalid signatures

3. **Check expiration**
   - Validate `exp` claim is in the future
   - Apply configurable clock skew tolerance (default: 60 seconds)
   - Reject expired tokens

4. **Validate issuer**
   - Check `iss` claim matches expected issuer
   - Support multiple trusted issuers via configuration
   - Reject tokens from unknown issuers

5. **Verify audience**
   - Check `aud` claim contains expected audience
   - Reject tokens not intended for this service

## Configuration

```yaml
token-validation:
  clock-skew-seconds: 60
  trusted-issuers:
    - https://auth.example.com
    - https://auth-staging.example.com
  expected-audience: api.example.com
```

## Error Handling

* **Invalid Format**: Return HTTP 401 with error code `TOKEN_MALFORMED`
* **Invalid Signature**: Return HTTP 401 with error code `TOKEN_INVALID_SIGNATURE`
* **Expired Token**: Return HTTP 401 with error code `TOKEN_EXPIRED`
* **Invalid Issuer**: Return HTTP 401 with error code `TOKEN_INVALID_ISSUER`
* **Invalid Audience**: Return HTTP 401 with error code `TOKEN_INVALID_AUDIENCE`

## See Also

* [JWT Validation](jwt-validation.md) - JWT-specific validation requirements
* [OAuth2 Validation](oauth2-validation.md) - OAuth2-specific validation requirements
* [Testing Standards](validation-testing.md) - Testing requirements for token validation
