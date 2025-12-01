# Issue #12: Implement OAuth2 Authentication Flow

## Description

Add complete OAuth2 authentication support to the security module, including:
- Authorization code flow
- Client credentials flow
- Token refresh mechanism
- Secure token storage

## Requirements

### Functional Requirements

1. **Authorization Code Flow**
   - Redirect to authorization server
   - Handle callback with authorization code
   - Exchange code for tokens
   - Store tokens securely

2. **Client Credentials Flow**
   - Direct token request with client credentials
   - Token caching
   - Automatic refresh

3. **Token Management**
   - Access token validation
   - Refresh token handling
   - Token expiration tracking
   - Secure storage (encrypted at rest)

### Technical Requirements

- Java 17+ compatibility
- Spring Security integration
- JUnit 5 test coverage >= 80%
- No external HTTP client dependencies (use JDK HttpClient)

## Acceptance Criteria

- [ ] Authorization code flow works end-to-end
- [ ] Client credentials flow works end-to-end
- [ ] Tokens are refreshed automatically before expiration
- [ ] Token storage is encrypted
- [ ] All flows have comprehensive test coverage
- [ ] Documentation includes usage examples

## Edge Cases

- Authorization server unavailable
- Invalid/expired refresh token
- Network timeout during token exchange
- Concurrent token refresh requests

## Dependencies

- Issue #10: Security Module Base Classes (COMPLETED)
- Issue #11: Encryption Utilities (IN PROGRESS)

## Labels

- enhancement
- security
- oauth2
