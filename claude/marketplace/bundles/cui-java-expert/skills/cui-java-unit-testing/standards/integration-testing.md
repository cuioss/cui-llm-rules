# Integration Testing Standards

## Overview

This document outlines best practices for configuring integration tests in Maven projects, ensuring proper separation between unit tests and integration tests using the surefire and failsafe plugins.

## Key Principles

### Test Separation

Integration tests should be completely separated from unit tests to ensure:

* Fast unit test execution during regular development builds
* Isolated integration test execution that can be run independently
* Clear distinction between test types for CI/CD pipelines
* Proper resource management for integration tests requiring external dependencies

### Maven Plugin Usage

* **Maven Surefire Plugin**: Handles unit tests during the `test` phase
* **Maven Failsafe Plugin**: Handles integration tests during the `integration-test` and `verify` phases

## Implementation Standards

### Naming Conventions

Integration tests must follow Maven's standard naming conventions:

* `**/*IT.java` - Integration Test classes
* `**/*ITCase.java` - Alternative integration test naming

```java
// ✅ Correct naming
public class TokenKeycloakIT extends KeycloakITBase {
    // Integration test implementation
}

// ❌ Incorrect naming (would be treated as unit test)
public class TokenKeycloakITTest extends KeycloakITBase {
    // This follows unit test naming convention
}
```

## Maven Configuration

### Base Configuration

Configure surefire plugin to exclude integration tests from normal builds:

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <configuration>
        <excludes>
            <exclude>**/*IT.java</exclude>
            <exclude>**/*ITCase.java</exclude>
        </excludes>
    </configuration>
</plugin>
```

### Integration Test Profile

Create a dedicated profile for integration tests:

```xml
<profile>
    <id>integration-tests</id>
    <build>
        <plugins>
            <!-- Skip Surefire Plugin (unit tests) when running integration tests -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <configuration>
                    <skipTests>true</skipTests>
                </configuration>
            </plugin>
            <!-- Maven Failsafe Plugin for Integration Tests -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-failsafe-plugin</artifactId>
                <configuration>
                    <includes>
                        <include>**/*IT.java</include>
                        <include>**/*ITCase.java</include>
                    </includes>
                </configuration>
                <executions>
                    <execution>
                        <id>integration-test</id>
                        <goals>
                            <goal>integration-test</goal>
                        </goals>
                    </execution>
                    <execution>
                        <id>verify</id>
                        <goals>
                            <goal>verify</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</profile>
```

## Critical Configuration Details

### Why Skip Unit Tests in Integration Profile

**Problem**: Without explicit unit test skipping, the integration-tests profile would run:
1. All unit tests (via surefire)
2. All integration tests (via failsafe)

**Solution**: Configure surefire to skip tests when the integration-tests profile is active:

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <configuration>
        <skipTests>true</skipTests>
    </configuration>
</plugin>
```

### Failsafe Goals

Both goals are required for proper integration test execution:

* `integration-test`: Runs the integration tests
* `verify`: Checks the results and fails the build if tests failed

## Maven Commands

### Normal Development Build

```
# Runs only unit tests, excludes integration tests
Task:
  subagent_type: maven-builder
  description: Run unit tests only
  prompt: |
    Execute unit tests only, excluding integration tests.

    Parameters:
    - command: clean test

    CRITICAL: Wait for completion. Inspect results and fix any failures.

# Full build without integration tests
Task:
  subagent_type: maven-builder
  description: Build without integration tests
  prompt: |
    Execute full build excluding integration tests.

    Parameters:
    - command: clean verify

    CRITICAL: Wait for completion. Inspect results and fix any failures.
```

### Integration Test Execution

```
# Run only integration tests (skips unit tests)
Task:
  subagent_type: maven-builder
  description: Run integration tests
  prompt: |
    Execute integration tests using the integration-tests profile.

    Parameters:
    - command: clean verify -Pintegration-tests

    CRITICAL: Wait for completion. Inspect results and fix any failures.

# Run integration tests for specific modules
Task:
  subagent_type: maven-builder
  description: Run integration tests for specific modules
  prompt: |
    Execute integration tests for specific modules only.

    Parameters:
    - command: clean verify -Pintegration-tests
    - module: module1

    Note: For multiple modules, run separate builds or modify command.

    CRITICAL: Wait for completion. Inspect results and fix any failures.
```

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Run Integration Tests
  run: ./mvnw --no-transfer-progress clean verify -Pintegration-tests -pl module1,module2
```

### Build Verification

Ensure both scenarios work correctly:

1. **Normal Build**: Should only run unit tests
2. **Integration Profile**: Should skip unit tests and only run integration tests

```
# Verify unit tests run, integration tests excluded
Task:
  subagent_type: maven-builder
  description: Verify unit test execution
  prompt: |
    Run unit tests to verify integration tests are excluded.
    Check output for *Test classes running, no *IT classes.

    Parameters:
    - command: clean test

    CRITICAL: Wait for completion. Verify output shows only *Test classes,
    no *IT or *ITCase classes executed.

# Verify integration tests run, unit tests skipped
Task:
  subagent_type: maven-builder
  description: Verify integration test execution
  prompt: |
    Run integration tests to verify unit tests are skipped.
    Check output for *IT/*ITCase classes running, *Test classes skipped.

    Parameters:
    - command: clean verify -Pintegration-tests

    CRITICAL: Wait for completion. Verify output shows only *IT/*ITCase classes,
    *Test classes show as skipped.
```

## Common Pitfalls

### ❌ Incorrect Naming Convention

```java
// Wrong - will be treated as unit test
public class TokenKeycloakITTest {
}
```

### ❌ Missing Surefire Skip Configuration

Without `<skipTests>true</skipTests>` in the integration-tests profile, both unit and integration tests will run.

### ❌ Wrong Maven Goal

```
# Wrong - only compiles and runs surefire (unit tests)
command: clean test -Pintegration-tests

# Correct - runs full lifecycle including failsafe (integration tests)
command: clean verify -Pintegration-tests
```

**Note**: When using maven-builder agent, pass goals without ./mvnw prefix.

### ❌ Missing Failsafe Executions

Without proper `<executions>` configuration, failsafe tests might not run or results might not be verified.

## JUnit 5 Nested Tests

Integration tests can use JUnit 5 nested test classes. The naming convention applies to the outer class:

```java
public class TokenKeycloakIT {

    @Nested
    class AccessTokenTests {
        @Test
        void shouldValidateAccessToken() {
            // Test implementation
        }
    }

    @Nested
    class IdTokenTests {
        @Test
        void shouldValidateIdToken() {
            // Test implementation
        }
    }
}
```

## Verification Checklist

Before considering integration test configuration complete:

- [ ] Normal build (`mvnw clean test`) excludes integration tests
- [ ] Integration profile (`mvnw clean verify -Pintegration-tests`) skips unit tests
- [ ] Integration profile successfully runs integration tests
- [ ] CI/CD workflow includes integration test execution
- [ ] Integration test naming follows Maven conventions
- [ ] Both surefire exclusions and failsafe inclusions are properly configured

## Additional Resources

* [Maven Surefire Plugin Documentation](https://maven.apache.org/surefire/maven-surefire-plugin/)
* [Maven Failsafe Plugin Documentation](https://maven.apache.org/surefire/maven-failsafe-plugin/)
* [Maven Build Lifecycle](https://maven.apache.org/guides/introduction/introduction-to-the-lifecycle.html)
