# CUI Java CDI Skill

CDI and Quarkus development standards for CUI projects.

## Overview

The `cui-java-cdi` skill provides comprehensive CDI/Quarkus standards covering:

- **CDI Aspects**: Constructor injection, scopes, producers, qualifiers, interceptors
- **Container Standards**: Docker configuration, security hardening, health checks, certificates
- **CDI Testing**: QuarkusTest patterns, test profiles, coverage, integration testing
- **Native Optimization**: Reflection registration, native image configuration, deployment processors

## When to Use This Skill

Use `cui-java-cdi` when:

- Developing CDI-based applications (Quarkus, Weld)
- Implementing dependency injection patterns
- Configuring Docker containers for CUI applications
- Writing CDI integration tests
- Building Quarkus native images
- Optimizing for native compilation

## Prerequisites

**Required**:
- Java 17 or later
- Quarkus framework
- Maven build system
- CDI 2.0+ (Jakarta CDI)

**Optional**:
- Docker (for container deployment)
- GraalVM (for native image compilation)

## Standards Included

### 1. CDI Aspects (`cdi-aspects.md`)

**Always loaded** - Core CDI patterns:

- **Constructor injection ONLY** (field injection prohibited)
- Make injected fields `final`
- `@Inject` optional for single-constructor beans
- Bean scopes (@ApplicationScoped, @RequestScoped, @Dependent)
- Producer methods with proper null handling
- Qualifiers for disambiguation
- Interceptors and decorators
- `Instance<T>` for optional dependencies
- Event-driven communication with CDI events

### 2. Container Standards (`cdi-container.md`)

**Always loaded** - Container configuration:

- Dockerfile best practices
- Security hardening (OWASP compliance)
- Certificate management (PEM vs PKCS12)
- Health check implementation
- Resource limits and optimization
- Multi-stage builds
- Non-root user execution
- Minimal base images

### 3. CDI Testing (`cdi-testing.md`)

**Load when**: Writing CDI tests

- @QuarkusTest vs @QuarkusIntegrationTest
- Test profiles and configuration
- JaCoCo coverage configuration
- Mock beans and test doubles
- Integration test patterns
- Test resource lifecycle
- Configuration overrides

### 4. Quarkus Native (`quarkus-native.md`)

**Load when**: Building native images

- @RegisterForReflection patterns
- Deployment processor configuration
- Reflection registration for third-party libraries
- Resource inclusion
- Native image optimization
- Build-time vs runtime initialization
- Native test execution

## Quick Start

### 1. Constructor Injection (Mandatory Pattern)

```java
@ApplicationScoped
public class TokenValidator {
    private final TokenConfig config;
    private final SignatureVerifier verifier;

    // @Inject optional for single constructor
    public TokenValidator(TokenConfig config, SignatureVerifier verifier) {
        this.config = config;
        this.verifier = verifier;
    }
}
```

### 2. Producer Method

```java
@ApplicationScoped
public class ConfigProducer {

    @Produces
    @Dependent  // Use @Dependent for producers that may return null
    public TokenConfig produceConfig(ConfigProvider provider) {
        return provider.getTokenConfig()
            .orElse(null);  // Null allowed with @Dependent
    }

    @Produces
    @ApplicationScoped  // Never return null from normal-scoped producers
    public SignatureVerifier produceVerifier() {
        return new SignatureVerifier(getPublicKey());
    }
}
```

### 3. Quarkus Test

```java
@QuarkusTest
@TestProfile(CustomTestProfile.class)
class TokenValidatorTest {

    @Inject
    TokenValidator validator;

    @Test
    void shouldValidateToken() {
        ValidationResult result = validator.validate(token);
        assertTrue(result.isValid());
    }
}

// Test profile for configuration
public class CustomTestProfile implements QuarkusTestProfile {

    @Override
    public Map<String, String> getConfigOverrides() {
        return Map.of(
            "token.issuer", "https://test.example.com",
            "token.validity", "PT1H"
        );
    }
}
```

### 4. Native Reflection Registration

```java
@RegisterForReflection(targets = {
    TokenConfig.class,
    ValidationResult.class,
    SignatureVerifier.class
})
public class ReflectionConfiguration {
    // Registers classes for reflection in native image
}
```

### 5. Dockerfile (Security Hardened)

```dockerfile
FROM registry.access.redhat.com/ubi9/openjdk-17:1.18

# Non-root user
USER 185

# Copy application
COPY --chown=185 target/quarkus-app/lib/ /deployments/lib/
COPY --chown=185 target/quarkus-app/*.jar /deployments/
COPY --chown=185 target/quarkus-app/app/ /deployments/app/
COPY --chown=185 target/quarkus-app/quarkus/ /deployments/quarkus/

# Security hardening
ENV JAVA_OPTS_APPEND="-Djava.security.egd=file:/dev/./urandom"

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8080/q/health || exit 1

EXPOSE 8080
```

## Integration with Other Skills

**Recommended skill combinations**:

```yaml
# Complete Quarkus development
skills:
  - cui-java-core          # Java patterns and logging
  - cui-java-cdi           # CDI/Quarkus standards (this skill)
  - cui-java-unit-testing  # Testing standards

# Container deployment
skills:
  - cui-java-cdi           # Container standards
  - cui-project-setup      # Project configuration
```

## Common Development Tasks

### Implement Dependency Injection

1. Use constructor injection (never field injection)
2. Make injected fields `final`
3. Select appropriate scope (@ApplicationScoped for stateless)
4. Avoid @Singleton unless eager initialization required
5. Use Instance<T> for optional dependencies
6. Add qualifiers for disambiguation

### Create Producer Method

1. Choose correct scope (@Dependent if may return null)
2. Never return null from normal-scoped producers
3. Use Instance<T> instead of Optional<T>
4. Implement Null Object pattern if appropriate
5. Document producer behavior in JavaDoc

### Write CDI Integration Test

1. Use @QuarkusTest for fast tests
2. Create QuarkusTestProfile for config overrides
3. Inject beans for testing
4. Configure JaCoCo for coverage
5. Run: `./mvnw clean verify -Pcoverage`

### Build Native Image

1. Add @RegisterForReflection to required classes
2. Configure reflection for third-party libraries
3. Test in JVM mode first: `mvn clean verify`
4. Build native: `mvn clean install -Pnative`
5. Test native: `mvn verify -Pnative`

### Create Secure Docker Image

1. Use minimal base image (UBI, distroless)
2. Run as non-root user
3. Configure health checks
4. Set resource limits
5. Use multi-stage builds
6. Scan for vulnerabilities

## Prohibited Practices

**DO NOT**:
- Use field injection (constructor injection ONLY)
- Make injected fields non-final
- Return null from normal-scoped producers
- Use @Singleton without justification
- Skip @RegisterForReflection for native compilation
- Run containers as root user
- Skip security hardening in containers
- Use large base images unnecessarily

## Verification Checklist

After applying this skill:

**Dependency Injection**:
- [ ] Constructor injection used (no field injection)
- [ ] Injected fields are `final`
- [ ] Appropriate scopes selected
- [ ] Producers configured correctly
- [ ] Null handling verified

**Testing**:
- [ ] @QuarkusTest annotations present
- [ ] Test profiles configured
- [ ] JaCoCo coverage configured
- [ ] Tests pass: `./mvnw clean test`
- [ ] Coverage verified: `./mvnw clean verify -Pcoverage`

**Container (if applicable)**:
- [ ] Secure base image selected
- [ ] Non-root user configured
- [ ] Health checks implemented
- [ ] Security hardening applied
- [ ] Vulnerability scan passed

**Native (if applicable)**:
- [ ] @RegisterForReflection annotations present
- [ ] Reflection configuration complete
- [ ] Native build succeeds: `mvn install -Pnative`
- [ ] Native tests pass: `mvn verify -Pnative`

## Quality Standards

This skill enforces:

- **Constructor injection**: Only pattern allowed for DI
- **Immutability**: Injected fields must be `final`
- **Proper scoping**: Match bean scope to lifecycle
- **Null safety**: Producer null handling rules
- **Container security**: OWASP hardening compliance
- **Native readiness**: Proper reflection registration

## Examples

See standards files for comprehensive examples including:

- Constructor injection patterns
- Producer methods with scopes
- Qualifiers and disambiguation
- QuarkusTest configurations
- Test profiles
- Dockerfile templates
- Native reflection registration
- Deployment processors

## Support

For issues or questions:

1. Review detailed standards in `standards/` directory
2. Check Quarkus documentation for framework specifics
3. Verify CDI specifications compliance
4. Test in JVM mode before native compilation
5. Consult Docker security best practices

## License

Part of the CUI LLM Rules documentation system for CUI OSS projects.
