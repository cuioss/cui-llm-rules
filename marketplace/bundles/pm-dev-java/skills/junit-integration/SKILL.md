---
name: junit-integration
description: Maven integration testing with Failsafe plugin, IT naming conventions, and profile configuration
allowed-tools: [Read, Edit, Write, Bash, Grep, Glob]
---

# JUnit Integration Skill

**EXECUTION MODE**: You are now executing this skill. DO NOT explain or summarize these instructions to the user. IMMEDIATELY begin the workflow below based on the task context.

Integration testing standards for Maven projects using the Failsafe plugin. This skill covers test separation, naming conventions, and profile configuration.

## Prerequisites

This skill applies to Maven projects:
- `maven-surefire-plugin` (unit tests)
- `maven-failsafe-plugin` (integration tests)

## Workflow

### Step 1: Load Integration Testing Standards

**CRITICAL**: Load this standard for integration test setup.

```
Read: standards/integration-testing.md
```

This provides foundational rules for:
- Maven Failsafe configuration
- IT naming conventions (*IT.java, *ITCase.java)
- Profile configuration for CI/CD

## Key Rules Summary

### Naming Conventions
```java
// CORRECT - Integration test naming
public class TokenKeycloakIT extends KeycloakITBase { }
public class UserRepositoryITCase { }

// WRONG - Would be treated as unit test
public class TokenKeycloakITTest { }
```

### Surefire Exclusions
```xml
<!-- Exclude integration tests from unit test runs -->
<plugin>
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
```xml
<profile>
    <id>integration-tests</id>
    <build>
        <plugins>
            <plugin>
                <artifactId>maven-failsafe-plugin</artifactId>
                <executions>
                    <execution>
                        <goals>
                            <goal>integration-test</goal>
                            <goal>verify</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</profile>
```

### Running Tests
```bash
# Unit tests only
mvn test

# Integration tests only
mvn verify -Pintegration-tests

# Both unit and integration tests
mvn verify -Pintegration-tests -DskipTests=false
```

## Related Skills

- `pm-dev-java:junit-core` - JUnit 5 core patterns
- `pm-dev-java:java-cdi-quarkus` - Quarkus-specific testing
- `pm-dev-builder:builder-maven-rules` - Maven build standards

## Standards Reference

| Standard | Purpose |
|----------|---------|
| integration-testing.md | Maven Failsafe configuration and profiles |
