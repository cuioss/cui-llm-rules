# OAuth2 Token Validation

## Purpose

This document defines OAuth2-specific validation requirements that extend the [standard validation process](token-validation-core.md).

## OAuth2-Specific Validation

OAuth2 tokens follow the [standard validation process](token-validation-core.md) with additional OAuth2-specific checks:

### Scope Validation

* **Required Scopes**: Validate token contains all required scopes for the requested resource
* **Scope Format**: Scopes must be space-separated as per OAuth2 specification
* **Scope Hierarchy**: Support hierarchical scope checking (e.g., `read:admin` implies `read:user`)

### Token Type Validation

* **Access Token**: Must have `token_type: "Bearer"`
* **Refresh Token**: Must not be used for API access (return HTTP 403)

### OAuth2-Specific Claims

* **Scope (scope)**: Space-separated list of granted scopes
* **Client ID (client_id)**: Identifier of the OAuth2 client
* **Token Type (token_type)**: Must be "Bearer" for access tokens

### OAuth2-Specific Error Codes

* **Insufficient Scope**: Return HTTP 403 with error code `OAUTH2_INSUFFICIENT_SCOPE`
* **Invalid Token Type**: Return HTTP 401 with error code `OAUTH2_INVALID_TOKEN_TYPE`
* **Missing Client ID**: Return HTTP 401 with error code `OAUTH2_MISSING_CLIENT_ID`

## Scope Requirements by Endpoint

| Endpoint | Required Scopes |
|----------|----------------|
| GET /api/users | `read:users` |
| POST /api/users | `write:users` |
| DELETE /api/users/{id} | `write:users`, `admin` |
| GET /api/admin/* | `admin` |

## Configuration

```yaml
oauth2-validation:
  scope-separator: " "
  enable-scope-hierarchy: true
  require-client-id: true
```

## See Also

* [Core Validation](token-validation-core.md) - Common validation requirements
* [Testing Standards](validation-testing.md) - Testing requirements for OAuth2 validation
