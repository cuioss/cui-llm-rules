# Integration Testing Standards

## Purpose

Standards for implementing integration tests in Quarkus applications that test the complete application stack through external API interfaces using production-like configurations.

## Core Principles

### API-Only Testing

Integration tests **MUST** test only through published APIs, never through internal CDI injection:

* **No CDI Injection**: Tests must not use `@Inject` for services
* **External Client Perspective**: Tests simulate real client interactions
* **Protocol Compliance**: Use actual HTTP/HTTPS protocols
* **Container Isolation**: Application runs in separate process/container

### Production Equivalence

Integration tests **MUST** use production-equivalent configurations:

* **HTTPS Required**: All tests use TLS with proper certificates
* **Real Networking**: Actual TCP/IP communication, not in-memory
* **Container Runtime**: Application runs in Docker container
* **Resource Constraints**: Same memory/CPU limits as production

## Test Structure

### Directory Organization

```
src/test/java/
└── integration/           # All integration tests here
    ├── BaseIntegrationTest.java    # Common setup
    ├── *Test.java                  # Individual test classes
    └── *IT.java                    # Alternative naming pattern
```

### Maven Profile Configuration

**Critical**: Use profile-based configuration to avoid duplicate native builds.

```xml
<profiles>
    <profile>
        <id>integration-tests</id>
        <properties>
            <!-- Skip unit tests for integration test profile -->
            <skipITs>false</skipITs>

            <!-- Enable native image building -->
            <quarkus.native.container-build>true</quarkus.native.container-build>
            <quarkus.native.enabled>true</quarkus.native.enabled>

            <!-- External port from docker-compose -->
            <test.https.port>10443</test.https.port>
        </properties>

        <build>
            <plugins>
                <!-- Quarkus Maven Plugin for native builds -->
                <plugin>
                    <groupId>io.quarkus</groupId>
                    <artifactId>quarkus-maven-plugin</artifactId>
                    <executions>
                        <!-- Single execution prevents duplicate builds -->
                        <execution>
                            <goals>
                                <goal>generate-code</goal>
                                <goal>generate-code-tests</goal>
                                <goal>build</goal>
                            </goals>
                        </execution>
                    </executions>
                    <configuration>
                        <properties>
                            <quarkus.native.enabled>true</quarkus.native.enabled>
                            <quarkus.package.jar.enabled>false</quarkus.package.jar.enabled>
                        </properties>
                    </configuration>
                </plugin>

                <!-- Skip unit tests -->
                <plugin>
                    <artifactId>maven-surefire-plugin</artifactId>
                    <configuration>
                        <skipTests>true</skipTests>
                    </configuration>
                </plugin>

                <!-- Application lifecycle via scripts -->
                <plugin>
                    <groupId>org.codehaus.mojo</groupId>
                    <artifactId>exec-maven-plugin</artifactId>
                    <executions>
                        <execution>
                            <id>start-integration-app</id>
                            <phase>pre-integration-test</phase>
                            <goals><goal>exec</goal></goals>
                            <configuration>
                                <executable>./scripts/start-integration-container.sh</executable>
                            </configuration>
                        </execution>
                        <execution>
                            <id>stop-integration-app</id>
                            <phase>post-integration-test</phase>
                            <goals><goal>exec</goal></goals>
                            <configuration>
                                <executable>./scripts/stop-integration-container.sh</executable>
                            </configuration>
                        </execution>
                    </executions>
                </plugin>

                <!-- Integration test execution -->
                <plugin>
                    <artifactId>maven-failsafe-plugin</artifactId>
                    <executions>
                        <execution>
                            <goals>
                                <goal>integration-test</goal>
                                <goal>verify</goal>
                            </goals>
                            <configuration>
                                <includes>
                                    <include>**/integration/**/*IT.java</include>
                                </includes>
                                <systemPropertyVariables>
                                    <test.https.port>${test.https.port}</test.https.port>
                                </systemPropertyVariables>
                                <skipITs>${skipITs}</skipITs>
                            </configuration>
                        </execution>
                    </executions>
                </plugin>
            </plugins>
        </build>
    </profile>
</profiles>
```

### Critical Configuration Requirements

**Single Execution Pattern**: Use one execution with all goals to prevent duplicate native builds

**Anti-Pattern** (causes duplicate builds):
```xml
<!-- ❌ WRONG: Causes duplicate native builds -->
<executions>
    <execution>
        <id>default</id>
        <goals>
            <goal>generate-code</goal>
        </goals>
    </execution>
    <execution>
        <id>build-native</id>  <!-- DUPLICATE BUILD! -->
        <goals>
            <goal>build</goal>
        </goals>
    </execution>
</executions>
```

**Modern Properties**: Use `quarkus.native.enabled` instead of deprecated `quarkus.package.type`

## Base Test Class Pattern

```java
public abstract class BaseIntegrationTest {

    private static final String DEFAULT_TEST_PORT = "10443";

    @BeforeAll
    static void setUpBaseIntegrationTest() {
        // Configure HTTPS with relaxed validation for self-signed certificates
        RestAssured.useRelaxedHTTPSValidation();
        RestAssured.baseURI = "https://localhost";

        // Use external port from docker-compose (10443:8443)
        String testPort = System.getProperty("test.https.port", DEFAULT_TEST_PORT);
        RestAssured.port = Integer.parseInt(testPort);
    }
}
```

## Individual Test Pattern

```java
/**
 * Integration tests for health check endpoints.
 * Tests verify functionality through REST API calls against external application.
 */
class HealthCheckIntegrationTest extends BaseIntegrationTest {

    @Test
    void shouldProvideOverallHealthStatus() {
        given()
                .when()
                .get("/q/health")
                .then()
                .statusCode(200)
                .contentType("application/json")
                .body("status", equalTo("UP"));
    }

    @Test
    void shouldProvideReadinessCheck() {
        given()
                .when()
                .get("/q/health/ready")
                .then()
                .statusCode(200)
                .body("status", equalTo("UP"));
    }
}
```

## Application Configuration

### HTTPS Configuration

Application **MUST** be configured for HTTPS-only operation:

```properties
# HTTPS Configuration
quarkus.http.ssl-port=8443
quarkus.http.insecure-requests=disabled

# TLS Configuration (Docker volume mount paths)
quarkus.http.ssl.certificate.files=/app/certificates/localhost.crt
quarkus.http.ssl.certificate.key-files=/app/certificates/localhost.key

# Enhanced TLS Security
quarkus.http.ssl.cipher-suites=TLS_AES_256_GCM_SHA384,TLS_CHACHA20_POLY1305_SHA256,TLS_AES_128_GCM_SHA256
quarkus.http.ssl.protocols=TLSv1.3,TLSv1.2
```

### Port Mapping Strategy

* **Internal Port**: `8443` (application listening port)
* **External Port**: `10443` (docker-compose exposed port)
* **Test Configuration**: Tests connect to external port `10443`

## Script-Based Lifecycle Management

### Start Script Pattern

```bash
#!/bin/bash
# scripts/start-integration-container.sh

set -e

echo "🚀 Starting Integration Tests with Docker Compose"

cd "${PROJECT_DIR}"

# Native image should already be built by Maven lifecycle
echo "📦 Using native image from target directory..."

# Start with Docker Compose
echo "🐳 Starting Docker container with native image..."
docker compose up -d

# Wait for service readiness with timing
echo "⏳ Waiting for service to be ready..."
START_TIME=$(date +%s)
for i in {1..30}; do
    if curl -k -s https://localhost:10443/q/health/live > /dev/null 2>&1; then
        END_TIME=$(date +%s)
        TOTAL_TIME=$((END_TIME - START_TIME))
        echo "✅ Service is ready!"
        echo "📈 Actual startup time: ${TOTAL_TIME}s (container + application)"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Service failed to start within 30 seconds"
        echo "Check logs with: docker compose logs"
        exit 1
    fi
    echo "⏳ Waiting... (attempt $i/30)"
    sleep 1
done

# Extract native startup time from logs
NATIVE_STARTUP=$(docker compose logs 2>/dev/null | grep "started in" | sed -n 's/.*started in \([0-9.]*\)s.*/\1/p' | tail -1)
if [ ! -z "$NATIVE_STARTUP" ]; then
    echo "⚡ Native app startup: ${NATIVE_STARTUP}s (application only)"
fi
```

### Stop Script Pattern

```bash
#!/bin/bash
# scripts/stop-integration-container.sh

set -e

echo "🛑 Stopping Integration Tests Docker containers"

cd "${PROJECT_DIR}"

# Stop and remove containers
echo "📦 Stopping Docker containers..."
docker compose down

echo "✅ Integration Tests stopped successfully"

# Show final status
if docker compose ps | grep -q "Up"; then
    echo "⚠️  Some containers are still running:"
    docker compose ps
else
    echo "✅ All containers are stopped"
fi
```

## Docker Compose Integration

### Container Configuration

```yaml
services:
  app-integration-tests:
    build:
      context: .
      dockerfile: src/main/docker/Dockerfile.native

    ports:
      - "10443:8443"  # External:Internal port mapping

    volumes:
      - ./src/main/docker/certificates:/app/certificates:ro

    # OWASP Security hardening
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    read_only: true
    tmpfs:
      - /tmp:rw,noexec,nosuid,size=100m

    healthcheck:
      test: ["CMD", "/app/health-check.sh"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Certificate Management

Certificates **MUST** be mounted as read-only volumes:

* **Host Path**: `./src/main/docker/certificates/`
* **Container Path**: `/app/certificates/`
* **Permissions**: Read-only mount (`:ro`)
* **Files**: `localhost.crt` and `localhost.key`

## Test Execution Phases

### Maven Lifecycle Integration

```
1. compile          → Build application
2. test-compile     → Compile integration tests
3. test             → SKIP (unit tests disabled)
4. package          → Create Quarkus application package
5. pre-integration-test → Execute start-integration-test.sh
6. integration-test → Run *Test.java files via failsafe
7. post-integration-test → Execute stop-integration-test.sh
8. verify           → Check test results
```

### Build Commands

```bash
# Run integration tests
./mvnw verify -Pintegration-tests -pl integration-test-module

# Skip integration tests
./mvnw package -pl integration-test-module
```

## Testing Patterns

### Health Check Testing

```java
@Test
void shouldProvideComprehensiveHealthCheck() {
    given()
            .when()
            .get("/q/health")
            .then()
            .statusCode(200)
            .body("status", equalTo("UP"))
            .body("checks", notNullValue());
}
```

### Metrics Testing

```java
@Test
void shouldExposePrometheusMetrics() {
    given()
            .when()
            .get("/q/metrics")
            .then()
            .statusCode(200)
            .contentType(containsString("text"))
            .body(containsString("# HELP"))
            .body(containsString("# TYPE"));
}
```

### API Endpoint Testing

```java
@Test
void shouldHandleValidRequest() {
    given()
            .contentType("application/json")
            .body("""
                {
                    "field": "value"
                }
                """)
            .when()
            .post("/api/endpoint")
            .then()
            .statusCode(201)
            .body("id", notNullValue())
            .body("status", equalTo("created"));
}
```

## Security Considerations

### HTTPS Requirements

* **Self-Signed Certificates**: Acceptable for integration tests
* **Certificate Validation**: Use `RestAssured.useRelaxedHTTPSValidation()`
* **TLS Versions**: Support TLS 1.2 and 1.3
* **Cipher Suites**: Use strong cipher suites only

### Container Security

* **Non-Root Execution**: Application runs as `nonroot` user
* **Read-Only Filesystem**: Root filesystem mounted read-only
* **Capability Dropping**: All capabilities dropped except required
* **Resource Limits**: Memory and CPU constraints applied

## Anti-Patterns

### Forbidden Practices

* ❌ **CDI Injection in Tests**: Never use `@Inject` in integration tests
* ❌ **@QuarkusTest Usage**: Use for unit tests only, not integration tests
* ❌ **HTTP in Production**: All integration tests must use HTTPS
* ❌ **Embedded Testing**: Application must run in separate process
* ❌ **Hardcoded Ports**: Always use configurable port properties
* ❌ **Duplicate Maven Executions**: Multiple executions cause duplicate native builds
* ❌ **Deprecated Properties**: Using `quarkus.package.type` instead of modern alternatives

### Legacy Pattern Migration

When converting from embedded to external testing:

1. **Remove Test Annotations**: Delete `@QuarkusTest`, `@QuarkusIntegrationTest`
2. **Remove CDI Injection**: Replace `@Inject` with REST API calls
3. **Add RestAssured**: Convert to HTTP client calls
4. **Configure HTTPS**: Update base URL and SSL handling
5. **Update Maven**: Configure script-based lifecycle

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs

# Verify certificates
ls -la src/main/docker/certificates/

# Test certificate validity
openssl x509 -in src/main/docker/certificates/localhost.crt -text -noout
```

### Connection Refused

```bash
# Check port mapping
docker compose ps

# Verify application is listening
docker compose exec app netstat -tlnp | grep 8443

# Test internal connectivity
docker compose exec app curl -k https://localhost:8443/q/health
```

### SSL Certificate Errors

```bash
# Regenerate certificates
cd src/main/docker/certificates
./generate-certificates.sh

# Verify certificate chain
openssl verify -CAfile localhost.crt localhost.crt
```

## Performance Considerations

### Native Image Benefits

* **Startup Time**: 0.15s cold start (application only), 1-2s total (container + application)
* **Memory Usage**: <150MB runtime memory
* **Container Size**: ~93MB with distroless base
* **Build Time**: 1.5 minutes optimized (single build), ~3 minutes unoptimized (duplicate builds)

### Test Execution Optimization

* **Parallel Execution**: Configure failsafe for parallel test execution
* **Container Reuse**: Keep container running for multiple test classes
* **Image Caching**: Use Docker layer caching for faster builds

## References

* [Quarkus Testing Guide](https://quarkus.io/guides/getting-started-testing)
* [REST Assured Documentation](https://rest-assured.io/)
* [Maven Failsafe Plugin](https://maven.apache.org/surefire/maven-failsafe-plugin/)
* [Docker Compose Documentation](https://docs.docker.com/compose/)
