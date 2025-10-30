---
name: cui-java-cdi
description: CDI and Quarkus development standards for CUI projects, including CDI aspects, container configuration, testing, and native optimization
allowed-tools: [Read, Edit, Write, Bash, Grep, Glob]
---

# CUI Java CDI Skill

Standards and patterns for CDI and Quarkus development in CUI projects. This skill provides comprehensive guidance on CDI dependency injection, Quarkus container configuration, testing practices, and native image optimization.

## Workflow

### Step 1: Load Foundational Java Patterns

**CRITICAL**: Load foundational Java development patterns first.

```
Skill: cui-java-core
```

The cui-java-core skill provides essential foundational patterns that CDI builds upon:
- Constructor injection principles and benefits
- Dependency management and null safety patterns
- Immutability and defensive programming
- Exception handling standards
- Modern Java features (records, sealed classes, pattern matching)

These core Java patterns are prerequisites for CDI-specific development.

### Step 2: Load Applicable CDI Standards

**CRITICAL**: Load current CDI standards to use as enforcement criteria.

1. **Always load foundational CDI standards**:
   ```
   Read: standards/cdi-aspects.md
   Read: standards/cdi-container.md
   ```
   These provide core CDI patterns and container configuration always needed for development.

2. **Conditional loading based on context**:

   - If writing CDI tests or integration tests:
     ```
     Read: standards/cdi-testing.md
     ```

   - If working with Quarkus native compilation:
     ```
     Read: standards/quarkus-native.md
     ```

3. **Extract key requirements from all loaded standards**

4. **Store in working memory** for use during task execution

### Step 3: Analyze Existing CDI Code

**When to Execute**: After loading standards

**What to Analyze**:

1. **Dependency Injection Patterns**:
   - Verify constructor injection usage (field injection is prohibited)
   - Check for proper `@Inject` annotation usage
   - Validate CDI bean scopes (`@ApplicationScoped`, `@RequestScoped`, etc.)
   - Review producer methods and their scope configurations

2. **CDI Component Structure**:
   - Identify CDI beans and their dependencies
   - Check for circular dependencies
   - Verify proper use of `Instance<T>` for optional dependencies
   - Review qualifier usage and ambiguous dependency resolution

3. **Container Configuration** (if applicable):
   - Review Dockerfile and base image selection
   - Verify security hardening (OWASP compliance)
   - Check certificate management approach (PEM vs PKCS12)
   - Validate health check implementation

4. **Testing Configuration** (if testing context):
   - Review `@QuarkusTest` vs `@QuarkusIntegrationTest` usage
   - Check JaCoCo coverage configuration
   - Verify test profiles and configuration overrides
   - Validate test resource configuration

5. **Native Optimization** (if native context):
   - Analyze reflection registration patterns
   - Review `@RegisterForReflection` annotations
   - Check deployment processor configurations
   - Identify optimization opportunities

### Step 4: Apply CDI Standards to Development Task

**When to Execute**: During implementation or code review

**What to Apply**:

1. **Constructor Injection Standard**:
   - Convert any field injection to constructor injection
   - Make injected fields `final`
   - Remove unnecessary `@Inject` for single-constructor beans
   - Add `@Inject` to correct constructor when multiple exist

2. **CDI Scope Selection**:
   - Apply `@ApplicationScoped` for stateless services
   - Use `@RequestScoped` for request-specific data
   - Avoid `@Singleton` unless eager initialization required
   - Validate scope matches lifecycle requirements

3. **Producer Method Patterns**:
   - Use `@Dependent` scope for producers that may return null
   - Ensure normal-scoped producers never return null
   - Prefer `Instance<T>` over `Optional<T>` in producers
   - Implement Null Object pattern when appropriate

4. **Container Security** (if container context):
   - Use distroless base image for production
   - Implement internal health checks (no curl/wget)
   - Configure OWASP security hardening
   - Set up PEM certificates with proper permissions

5. **Testing Practices** (if testing context):
   - Configure JaCoCo for Quarkus correctly
   - Use `@QuarkusTest` for CDI injection tests
   - Use `@QuarkusIntegrationTest` for packaged app tests
   - Ensure `@{argLine}` in Surefire configuration

6. **Native Optimization** (if native context):
   - Minimize reflection scope to actual needs
   - Split deployment processor by reflection requirements
   - Use type-safe class references (not strings)
   - Remove duplicate annotations after deployment processor registration

### Step 5: Verify Implementation Quality

**When to Execute**: After applying standards

**Quality Checks**:

1. **CDI Pattern Verification**:
   - [ ] All dependencies use constructor injection
   - [ ] All injected fields are `final`
   - [ ] Proper CDI scopes applied
   - [ ] No field or setter injection present
   - [ ] Producer methods follow scope rules

2. **Testing Verification** (if testing context):
   - [ ] JaCoCo properly configured
   - [ ] Test coverage collected successfully
   - [ ] Test profiles configured correctly
   - [ ] All CDI components tested

3. **Container Verification** (if container context):
   - [ ] Distroless base image used
   - [ ] Security hardening applied
   - [ ] Health checks implemented correctly
   - [ ] Certificates configured with proper permissions

4. **Native Optimization Verification** (if native context):
   - [ ] Reflection registration optimized
   - [ ] Native compilation succeeds
   - [ ] Tests pass in native mode
   - [ ] Performance metrics maintained or improved

5. **Compilation and Build**:
   ```bash
   # Compile the module
   ./mvnw clean compile -pl [module-name]

   # Run tests
   ./mvnw clean test -pl [module-name]

   # Quality verification
   ./mvnw -Ppre-commit clean verify -DskipTests -pl [module-name]

   # Final verification
   ./mvnw clean install -pl [module-name]
   ```

6. **Native Build** (if native context):
   ```bash
   # Native compilation
   ./mvnw clean package -Dnative -pl [module-name]
   ```

### Step 5: Document Changes and Commit

**When to Execute**: After verification passes

**Documentation Updates**:
- Update module README if CDI architecture changed
- Document any special configuration requirements
- Note any deviations from standards with rationale
- Include performance metrics if applicable

**Commit Standards**:
- Follow standard commit message format
- Reference related issues or tasks
- Include "Zero information loss verified" if migrating code
- Add co-authored-by line for Claude Code

## Common Patterns and Error Prevention

For detailed CDI patterns and troubleshooting, see the loaded standards files:
- **CDI Patterns**: Constructor injection, optional dependencies, producer methods - see `standards/cdi-aspects.md`
- **Common Issues**: Resolution exceptions, testing problems, native compilation - see `standards/cdi-aspects.md` and `standards/cdi-testing.md`
- **Container Configuration**: DevUI, health checks - see `standards/cdi-container.md`
- **Native Optimization**: Reflection configuration, build settings - see `standards/quarkus-native.md`

## Quality Verification

All changes must pass:
- [x] Constructor injection used exclusively
- [x] All injected fields are `final`
- [x] Proper CDI scopes applied
- [x] Producer methods follow scope rules
- [x] Tests pass with coverage collected
- [x] Quality checks pass (`-Ppre-commit`)
- [x] Native compilation succeeds (if applicable)

## References

* CDI 2.0 Specification: https://docs.oracle.com/javaee/7/tutorial/cdi-basic.htm
* Quarkus CDI Guide: https://quarkus.io/guides/cdi
* Quarkus Testing Guide: https://quarkus.io/guides/getting-started-testing
* Docker Security Best Practices: https://docs.docker.com/develop/security-best-practices/
* Quarkus Native Guide: https://quarkus.io/guides/writing-native-applications-tips
