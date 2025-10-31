# HTTP Testing with MockWebServer Standards

## Overview

For testing HTTP client interactions in CUI projects, use the `cui-test-mockwebserver-junit5` framework. This provides a lightweight, in-process HTTP server for mocking HTTP responses and testing client behavior without external dependencies.

## Framework Requirements

### Maven Dependency

```xml
<dependency>
    <groupId>de.cuioss.test</groupId>
    <artifactId>cui-test-mockwebserver-junit5</artifactId>
    <scope>test</scope>
</dependency>
```

### When to Use MockWebServer

* Testing HTTP client implementations
* Testing API integrations
* Testing retry logic and error handling
* Testing HTTP request/response handling
* Testing timeout behaviors
* Testing different HTTP status codes and responses

### When NOT to Use MockWebServer

* Integration tests with real HTTP services (use Testcontainers or similar)
* Testing HTTP server implementations (use different approach)
* End-to-end tests requiring real network calls

## Basic MockWebServer Usage

### Setup and Teardown

```java
import de.cuioss.test.mockwebserver.junit5.EnableMockWebServer;
import de.cuioss.test.mockwebserver.junit5.MockWebServerHolder;
import mockwebserver3.MockResponse;
import mockwebserver3.RecordedRequest;

@EnableMockWebServer
class HttpClientTest {

    @InjectMockWebServer
    private MockWebServerHolder serverHolder;

    @Test
    @DisplayName("Should successfully fetch user data")
    void shouldFetchUserData() throws Exception {
        // Arrange - Configure mock response
        serverHolder.enqueue(new MockResponse()
            .setResponseCode(200)
            .setBody("{\"id\": 1, \"name\": \"John Doe\"}")
            .addHeader("Content-Type", "application/json"));

        String baseUrl = serverHolder.getBaseUrl();

        // Act - Make HTTP request
        HttpClient client = new HttpClient(baseUrl);
        UserResponse response = client.getUser(1);

        // Assert - Verify response
        assertNotNull(response, "Response should not be null");
        assertEquals(1, response.getId(), "User ID should match");
        assertEquals("John Doe", response.getName(), "User name should match");

        // Verify request was made correctly
        RecordedRequest request = serverHolder.takeRequest();
        assertEquals("/users/1", request.getPath(), "Request path should match");
        assertEquals("GET", request.getMethod(), "HTTP method should be GET");
    }
}
```

## Response Mocking Patterns

### Success Responses

```java
@Test
@DisplayName("Should handle successful JSON response")
void shouldHandleSuccessResponse() {
    // Mock successful response
    serverHolder.enqueue(new MockResponse()
        .setResponseCode(200)
        .setBody("{\"status\": \"success\", \"data\": \"value\"}")
        .addHeader("Content-Type", "application/json"));

    Response response = client.fetchData(serverHolder.getBaseUrl());

    assertTrue(response.isSuccess(), "Response should indicate success");
}
```

### Error Responses

```java
@Test
@DisplayName("Should handle HTTP 404 error")
void shouldHandle404Error() {
    // Mock 404 response
    serverHolder.enqueue(new MockResponse()
        .setResponseCode(404)
        .setBody("{\"error\": \"Not Found\"}"));

    assertThrows(NotFoundException.class,
        () -> client.fetchResource(serverHolder.getBaseUrl(), "unknown-id"),
        "Should throw NotFoundException for 404 response");
}

@Test
@DisplayName("Should handle HTTP 500 server error")
void shouldHandle500Error() {
    // Mock server error
    serverHolder.enqueue(new MockResponse()
        .setResponseCode(500)
        .setBody("{\"error\": \"Internal Server Error\"}"));

    assertThrows(ServerException.class,
        () -> client.fetchResource(serverHolder.getBaseUrl(), "resource-id"),
        "Should throw ServerException for 500 response");
}
```

### Delayed Responses (Timeout Testing)

```java
@Test
@DisplayName("Should handle connection timeout")
void shouldHandleTimeout() {
    // Mock delayed response (simulating timeout)
    serverHolder.enqueue(new MockResponse()
        .setResponseCode(200)
        .setBodyDelay(5, TimeUnit.SECONDS));

    // Client with 2-second timeout
    HttpClient client = new HttpClient(serverHolder.getBaseUrl(), 2000);

    assertThrows(TimeoutException.class,
        () -> client.fetchData(),
        "Should throw TimeoutException when server response is delayed");
}
```

## Request Verification

### Verifying Request Headers

```java
@Test
@DisplayName("Should include authorization header in request")
void shouldIncludeAuthHeader() throws Exception {
    serverHolder.enqueue(new MockResponse().setResponseCode(200));

    client.fetchSecureResource(serverHolder.getBaseUrl(), "token123");

    RecordedRequest request = serverHolder.takeRequest();
    assertEquals("Bearer token123", request.getHeader("Authorization"),
        "Authorization header should be included");
}
```

### Verifying Request Body

```java
@Test
@DisplayName("Should send correct request body")
void shouldSendCorrectBody() throws Exception {
    serverHolder.enqueue(new MockResponse().setResponseCode(201));

    User user = User.builder()
        .name(Generators.strings().next())
        .email(Generators.emailAddress().next())
        .build();

    client.createUser(serverHolder.getBaseUrl(), user);

    RecordedRequest request = serverHolder.takeRequest();
    String body = request.getBody().readUtf8();

    assertTrue(body.contains(user.getName()),
        "Request body should contain user name");
    assertTrue(body.contains(user.getEmail()),
        "Request body should contain user email");
}
```

### Verifying Query Parameters

```java
@Test
@DisplayName("Should include query parameters in request")
void shouldIncludeQueryParams() throws Exception {
    serverHolder.enqueue(new MockResponse().setResponseCode(200));

    client.searchUsers(serverHolder.getBaseUrl(), "john", 10);

    RecordedRequest request = serverHolder.takeRequest();
    String path = request.getPath();

    assertTrue(path.contains("query=john"),
        "Query parameter 'query' should be present");
    assertTrue(path.contains("limit=10"),
        "Query parameter 'limit' should be present");
}
```

## Retry Logic Testing

### Testing Retry on Failure

```java
@Test
@DisplayName("Should retry on server error")
void shouldRetryOnServerError() throws Exception {
    // First request fails
    serverHolder.enqueue(new MockResponse().setResponseCode(500));
    // Second request succeeds
    serverHolder.enqueue(new MockResponse()
        .setResponseCode(200)
        .setBody("{\"status\": \"success\"}"));

    // Client configured with retry logic
    Response response = resilientClient.fetchData(serverHolder.getBaseUrl());

    assertTrue(response.isSuccess(), "Should succeed after retry");
    assertEquals(2, serverHolder.getRequestCount(),
        "Should have made 2 requests (initial + retry)");
}
```

### Testing Max Retry Attempts

```java
@Test
@DisplayName("Should fail after max retry attempts")
void shouldFailAfterMaxRetries() {
    // All requests fail
    for (int i = 0; i < 3; i++) {
        serverHolder.enqueue(new MockResponse().setResponseCode(503));
    }

    // Client configured with max 3 retries
    assertThrows(ServiceUnavailableException.class,
        () -> resilientClient.fetchData(serverHolder.getBaseUrl()),
        "Should throw exception after max retries");

    assertEquals(3, serverHolder.getRequestCount(),
        "Should have attempted exactly 3 requests");
}
```

## Multiple Requests Testing

### Sequential Requests

```java
@Test
@DisplayName("Should handle multiple sequential requests")
void shouldHandleMultipleRequests() throws Exception {
    // Queue multiple responses
    serverHolder.enqueue(new MockResponse()
        .setResponseCode(200)
        .setBody("{\"id\": 1}"));
    serverHolder.enqueue(new MockResponse()
        .setResponseCode(200)
        .setBody("{\"id\": 2}"));

    User user1 = client.getUser(serverHolder.getBaseUrl(), 1);
    User user2 = client.getUser(serverHolder.getBaseUrl(), 2);

    assertEquals(1, user1.getId(), "First user ID should match");
    assertEquals(2, user2.getId(), "Second user ID should match");
    assertEquals(2, serverHolder.getRequestCount(),
        "Should have made 2 requests");
}
```

## Integration with CUI Test Generator

Combine MockWebServer with generator framework for comprehensive testing.

For detailed generator usage patterns and requirements, see `testing-generators.md` in this skill.

```java
@EnableMockWebServer
@EnableGeneratorController
class ComprehensiveHttpTest {

    @InjectMockWebServer
    private MockWebServerHolder serverHolder;

    @ParameterizedTest
    @DisplayName("Should handle various user data")
    @GeneratorsSource(generator = GeneratorType.INTEGERS, low = "1", high = "100", count = 5)
    void shouldFetchVariousUsers(Integer userId) {
        // Generate mock response using generators
        String userName = Generators.strings().next();
        String userEmail = Generators.emailAddress().next();

        serverHolder.enqueue(new MockResponse()
            .setResponseCode(200)
            .setBody(String.format(
                "{\"id\": %d, \"name\": \"%s\", \"email\": \"%s\"}",
                userId, userName, userEmail)));

        User user = client.getUser(serverHolder.getBaseUrl(), userId);

        assertEquals(userId, user.getId(), "User ID should match");
        assertNotNull(user.getName(), "User name should not be null");
        assertNotNull(user.getEmail(), "User email should not be null");
    }
}
```

## Best Practices

### Clear Test Structure

* Follow AAA pattern (see [testing-junit-core.md](testing-junit-core.md) for details)
* Configure mock responses before making requests
* Verify both response data and request details
* Clean separation between setup and assertions

### Meaningful Assertions

* Verify response data correctness
* Check request headers, body, and parameters
* Validate retry behavior and error handling
* Use descriptive assertion messages

### Realistic Test Data

* Use CUI generators for test data creation
* Test with various response codes and payloads
* Include edge cases (empty responses, large payloads)
* Test error scenarios comprehensively

### Avoid Common Pitfalls

* Don't forget to enqueue responses before requests
* Verify request count matches expectations
* Handle InterruptedException properly when using takeRequest()
* Clean up resources (handled automatically by @EnableMockWebServer)

## Common HTTP Status Codes to Test

* **200 OK** - Successful GET/PUT requests
* **201 Created** - Successful POST requests
* **204 No Content** - Successful DELETE requests
* **400 Bad Request** - Invalid request data
* **401 Unauthorized** - Missing or invalid authentication
* **403 Forbidden** - Insufficient permissions
* **404 Not Found** - Resource not found
* **500 Internal Server Error** - Server errors
* **503 Service Unavailable** - Temporary service issues

## Additional Resources

* CUI MockWebServer JUnit5: https://github.com/cuioss/cui-test-mockwebserver-junit5
* Complete Documentation: https://gitingest.com/github.com/cuioss/cui-test-mockwebserver-junit5
* OkHttp MockWebServer: https://github.com/square/okhttp/tree/master/mockwebserver
