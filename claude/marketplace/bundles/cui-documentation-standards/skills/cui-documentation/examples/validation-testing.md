# Token Validation Testing Standards

## Purpose

This document defines testing requirements for token validation implementations.

## Test Coverage Requirements

All token validation implementations must achieve:

* **Line Coverage**: Minimum 90%
* **Branch Coverage**: Minimum 85%
* **Mutation Score**: Minimum 80%

## Required Test Categories

### 1. Valid Token Tests

Test successful validation with valid tokens:

```java
@Test
void shouldAcceptValidToken() {
    String token = generateValidToken();
    TokenValidationResult result = validator.validate(token);

    assertTrue(result.isValid(), "Valid token should pass validation");
    assertEquals("user123", result.getSubject());
}
```

### 2. Signature Validation Tests

Test invalid signatures are rejected:

```java
@Test
void shouldRejectTokenWithInvalidSignature() {
    String token = generateTokenWithInvalidSignature();

    TokenValidationException exception = assertThrows(
        TokenValidationException.class,
        () -> validator.validate(token)
    );

    assertEquals("TOKEN_INVALID_SIGNATURE", exception.getErrorCode());
}
```

### 3. Expiration Tests

Test expired tokens are rejected:

```java
@Test
void shouldRejectExpiredToken() {
    String token = generateExpiredToken();

    TokenValidationException exception = assertThrows(
        TokenValidationException.class,
        () -> validator.validate(token)
    );

    assertEquals("TOKEN_EXPIRED", exception.getErrorCode());
}
```

### 4. Clock Skew Tests

Test clock skew tolerance works correctly:

```java
@Test
void shouldAcceptTokenWithinClockSkew() {
    Instant now = Instant.now();
    Instant expiry = now.plus ofSeconds(30); // Expires in 30 seconds

    String token = generateToken(expiry);

    // Simulate clock ahead by 40 seconds (within 60s skew tolerance)
    validator.setClock(Clock.offset(Clock.systemUTC(), Duration.ofSeconds(40)));

    TokenValidationResult result = validator.validate(token);
    assertTrue(result.isValid(), "Token within clock skew should pass");
}
```

### 5. Issuer Validation Tests

Test untrusted issuers are rejected:

```java
@Test
void shouldRejectTokenFromUntrustedIssuer() {
    String token = generateToken("https://untrusted-issuer.com");

    TokenValidationException exception = assertThrows(
        TokenValidationException.class,
        () -> validator.validate(token)
    );

    assertEquals("TOKEN_INVALID_ISSUER", exception.getErrorCode());
}
```

### 6. Audience Validation Tests

Test audience mismatch is detected:

```java
@Test
void shouldRejectTokenForDifferentAudience() {
    String token = generateToken(audience: "different-service.com");

    TokenValidationException exception = assertThrows(
        TokenValidationException.class,
        () -> validator.validate(token)
    );

    assertEquals("TOKEN_INVALID_AUDIENCE", exception.getErrorCode());
}
```

## Test Data Management

Use test fixtures for common scenarios:

```java
class TokenTestFixtures {
    static String validToken() {
        return generateToken(
            issuer: "https://auth.example.com",
            audience: "api.example.com",
            subject: "user123",
            expiry: Instant.now().plusSeconds(3600)
        );
    }

    static String expiredToken() {
        return generateToken(
            expiry: Instant.now().minusSeconds(3600)
        );
    }
}
```

## Integration Testing

Test token validation in HTTP request flow:

```java
@Test
void shouldReturn401ForInvalidToken() {
    String invalidToken = generateInvalidToken();

    given()
        .header("Authorization", "Bearer " + invalidToken)
    .when()
        .get("/api/users")
    .then()
        .statusCode(401)
        .body("error_code", equalTo("TOKEN_INVALID_SIGNATURE"));
}
```

## Performance Testing

Validate token validation performance meets SLA:

```java
@Test
void tokenValidationShouldCompleteFast() {
    String token = TokenTestFixtures.validToken();

    long startTime = System.nanoTime();
    validator.validate(token);
    long duration = System.nanoTime() - startTime;

    assertTrue(duration < 5_000_000, // 5ms SLA
        "Token validation should complete in under 5ms");
}
```

## See Also

* [Core Validation](token-validation-core.md) - Validation requirements being tested
* [JWT Validation](jwt-validation.md) - JWT-specific test requirements
* [OAuth2 Validation](oauth2-validation.md) - OAuth2-specific test requirements
