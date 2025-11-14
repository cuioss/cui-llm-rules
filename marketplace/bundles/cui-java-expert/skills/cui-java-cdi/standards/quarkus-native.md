# Quarkus Native Optimization Process

Systematic process for optimizing Quarkus applications for native image compilation, with focus on reflection registration optimization and performance improvements.

## Overview

This process defines WHEN and WHAT to optimize in Quarkus applications for native image performance. It provides a systematic approach to identifying optimization opportunities, implementing improvements, and verifying results.

## Pre-Optimization Checklist

Before starting any native optimization work:

1. [ ] **Baseline Verification**: Ensure application builds and tests pass
   ```
   Task:
     subagent_type: maven-builder
     description: Verify baseline build
     prompt: |
       Build and install project to verify baseline functionality.

       Parameters:
       - command: clean install

       CRITICAL: Wait for completion. Ensure all tests pass before proceeding.
   ```

2. [ ] **Native Image Compatibility**: Verify project supports native compilation
   ```
   Task:
     subagent_type: maven-builder
     description: Verify native image build
     prompt: |
       Build native image to verify Quarkus native compilation works.

       Parameters:
       - command: clean package -Dnative

       CRITICAL: Wait for completion (may take several minutes).
       Record build time and image size for baseline metrics.
   ```

3. [ ] **Performance Baseline**: Record current metrics (build time, image size, startup time)

4. [ ] **Branch Creation**: Create dedicated branch for optimization work
   ```bash
   git checkout -b native-optimization-[feature-name]
   ```

## Optimization Workflow

### Phase 1: Analysis and Planning

#### 1.1 Reflection Usage Analysis

**When to Execute**: At the start of any native optimization project

**What to Analyze**:
- [ ] Scan for `@RegisterForReflection` annotations
- [ ] Identify deployment processor `ReflectiveClassBuildItem` registrations
- [ ] Review reflection scope parameters (`methods`, `fields`, `constructors`)
- [ ] Document current reflection architecture

**Commands**:
```bash
# Find all RegisterForReflection usage
find . -name "*.java" -exec grep -l "@RegisterForReflection" {} \;

# Find deployment processor registrations
find . -name "*Processor.java" -exec grep -l "ReflectiveClassBuildItem" {} \;
```

**Success Criteria**:
- Complete inventory of reflection registrations
- Clear categorization of application vs. infrastructure classes
- Identified optimization opportunities

#### 1.2 Reflection Requirements Assessment

**When to Execute**: After completing reflection usage analysis

**What to Assess**:
- [ ] Categorize classes by reflection requirements:
  * CDI beans (usually need constructors only)
  * Data classes (may need methods/fields for serialization)
  * Configuration classes (builder pattern vs. property binding)
  * Enum classes (usually need minimal reflection)
  * Annotation classes (framework-specific requirements)

- [ ] Identify usage patterns:
  * Framework-managed instantiation (CDI, dependency injection)
  * Direct constructor calls
  * Getter/setter access patterns
  * Field-based access patterns

**Success Criteria**:
- All classes categorized by reflection needs
- Usage patterns documented
- Optimization strategy defined

### Phase 2: Implementation

#### 2.1 Deployment Processor Optimization

**When to Execute**: First optimization phase - infrastructure level

**What to Optimize**:
- [ ] **Split by Reflection Requirements**: Group classes with similar reflection needs
  ```java
  // Example: Constructor-only classes
  @BuildStep
  public ReflectiveClassBuildItem registerConstructorOnlyClasses() {
      return ReflectiveClassBuildItem.builder(
              TokenValidator.class,
              SecurityEventCounter.class)
              .methods(false)
              .fields(false)
              .constructors(true)
              .build();
  }
  ```

- [ ] **Builder Pattern Classes**: Eliminate unnecessary constructor reflection
  ```java
  // Configuration classes using builder pattern
  ReflectiveClassBuildItem.builder(
          IssuerConfig.class,
          ParserConfig.class)
          .methods(true)    // Getters needed
          .fields(false)    // No direct field access
          .constructors(false) // Builder pattern
          .build();
  ```

- [ ] **Replace String Constants**: Use type-safe class references
  ```java
  // Before
  ReflectiveClassBuildItem.builder("com.example.MyClass")

  // After
  ReflectiveClassBuildItem.builder(MyClass.class)
  ```

- [ ] **CDI Bean Registration**: Use type-safe AdditionalBeanBuildItem for CDI beans
  ```java
  // Type-safe CDI bean registration in deployment processor
  @BuildStep
  public AdditionalBeanBuildItem additionalBeans() {
      return AdditionalBeanBuildItem.builder()
              .addBeanClasses(
                      TokenValidatorProducer.class,
                      BearerTokenProducer.class,
                      IssuerConfigResolver.class,
                      ParserConfigResolver.class
              )
              .setUnremovable()
              .build();
  }
  ```

**CRITICAL**: When registering CDI beans in the deployment processor, remove duplicate `@RegisterForReflection` annotations from the bean classes to avoid conflicts.

**Verification Commands**:
```
# Test compilation after each change
Task:
  subagent_type: maven-builder
  description: Test compilation
  prompt: |
    Compile module to verify changes.

    Parameters:
    - command: clean compile
    - module: [module-name]

    CRITICAL: Wait for completion. Fix any compilation errors.

# Run quality verification
Task:
  subagent_type: maven-builder
  description: Run quality checks
  prompt: |
    Run pre-commit quality verification without tests.

    Parameters:
    - command: -Ppre-commit clean verify -DskipTests
    - module: [module-name]

    CRITICAL: Wait for completion. Fix any quality issues.
```

**Success Criteria**:
- All deployment processor optimizations implemented
- Compilation succeeds without errors
- Quality checks pass

#### 2.2 Application Class Annotation Optimization

**When to Execute**: After deployment processor optimization

**What to Optimize**:
- [ ] **CDI Beans**: Optimize to minimal reflection scope
  ```java
  // Most CDI beans only need constructors
  @RegisterForReflection(methods = false, fields = false)
  @ApplicationScoped
  public class MyService {
  ```

- [ ] **Data Classes**: Assess actual reflection needs
  ```java
  // Lombok classes might need methods for builders
  @RegisterForReflection // Keep default for Lombok
  @Value
  @Builder
  public class DataClass {

  // Simple data classes
  @RegisterForReflection(fields = false) // Methods for getters, no field access
  public class SimpleData {
  ```

- [ ] **Enum Classes**: Minimal reflection needed
  ```java
  @RegisterForReflection(methods = false, fields = false)
  public enum Status {
  ```

- [ ] **Annotation Classes**: Framework compatibility
  ```java
  @RegisterForReflection(methods = false, fields = false)
  @Qualifier
  public @interface MyQualifier {
  ```

**Special Cases**:
- **Lombok Classes**: Use default `@RegisterForReflection` to avoid Javadoc conflicts
- **Serializable Classes**: May need methods/fields for serialization
- **Framework Integration**: Some frameworks require specific reflection access

**Verification Process**:
```
# Compile module
Task:
  subagent_type: maven-builder
  description: Compile module
  prompt: |
    Compile module to verify reflection annotations.

    Parameters:
    - command: clean compile
    - module: [module-name]

    CRITICAL: Wait for completion. Fix any compilation errors.

# Test reflection optimization
Task:
  subagent_type: maven-builder
  description: Test reflection configuration
  prompt: |
    Run specific reflection tests to verify optimization.

    Parameters:
    - command: clean test -Dtest=[ReflectionTest]
    - module: [module-name]

    CRITICAL: Wait for completion. Verify reflection tests pass.

# Full module verification
Task:
  subagent_type: maven-builder
  description: Full module build
  prompt: |
    Build and install module with optimized reflection.

    Parameters:
    - command: clean install
    - module: [module-name]

    CRITICAL: Wait for completion. Ensure all tests pass.
```

**Success Criteria**:
- All application classes optimized appropriately
- Tests pass with optimized reflection configuration
- No regression in functionality

### Phase 3: Verification and Testing

#### 3.1 Reflection Registration Verification

**When to Execute**: After completing all reflection optimizations

**What to Verify**:
- [ ] **Create Verification Test**: Implement test to verify reflection registration
  ```java
  @Test
  void shouldHaveOptimalReflectionRegistration() {
      // Verify all required classes have appropriate annotations
      // Test reflection scope parameters are correct
      // Ensure no over-registration occurs
  }
  ```

- [ ] **Test Application Functionality**: Verify core features work
- [ ] **CDI Bean Resolution**: Test dependency injection works
- [ ] **Serialization/Deserialization**: Test data classes if applicable

**Commands**:
```
# Run reflection verification tests
Task:
  subagent_type: maven-builder
  description: Run reflection tests
  prompt: |
    Run all reflection-related tests.

    Parameters:
    - command: test -Dtest="*Reflection*Test"
    - module: [module-name]

    CRITICAL: Wait for completion. Verify all reflection tests pass.

# Run full test suite
Task:
  subagent_type: maven-builder
  description: Run full test suite
  prompt: |
    Run complete test suite with optimized reflection.

    Parameters:
    - command: clean install
    - module: [module-name]

    CRITICAL: Wait for completion. Ensure all tests pass.
```

#### 3.2 Native Image Compatibility Testing

**When to Execute**: After reflection verification passes

**What to Test**:
- [ ] **Native Compilation**: Verify native image builds successfully
  ```
  Task:
    subagent_type: maven-builder
    description: Build native image
    prompt: |
      Build native executable using GraalVM.

      Parameters:
      - command: clean package -Dnative
      - module: [module-name]

      CRITICAL: Wait for completion (may take several minutes).
      Record build time and executable size metrics.
  ```

- [ ] **Runtime Testing**: Test application functionality in native mode
- [ ] **Performance Metrics**: Compare before/after metrics:
  * Native image build time
  * Native executable size
  * Application startup time
  * Memory usage patterns

**Success Criteria**:
- Native compilation succeeds
- All tests pass in native mode
- Performance metrics improved or maintained
- No functionality regression

### Phase 4: Quality Assurance

#### 4.1 Code Quality Verification

**When to Execute**: Before committing optimizations

**Mandatory Checks**:
```
# Quality verification (mandatory)
Task:
  subagent_type: maven-builder
  description: Run quality checks
  prompt: |
    Run pre-commit quality verification without tests.

    Parameters:
    - command: -Ppre-commit clean verify -DskipTests
    - module: [module-name]

    CRITICAL: Wait for completion. Fix all quality issues before committing.

# Final verification (mandatory)
Task:
  subagent_type: maven-builder
  description: Final build verification
  prompt: |
    Run final build and test verification.

    Parameters:
    - command: clean install
    - module: [module-name]

    CRITICAL: Wait for completion. Ensure all tests and quality checks pass.
```

**Success Criteria**:
- All quality checks pass
- No code quality regressions
- Documentation updated if needed

#### 4.2 Documentation and Commit

**When to Execute**: After all verifications pass

**Documentation Requirements**:
- [ ] Update module README if reflection architecture changed significantly
- [ ] Document any special reflection requirements
- [ ] Note performance improvements achieved

**Commit Requirements**:
- [ ] Follow git commit standards
- [ ] Include performance metrics in commit message
- [ ] Reference any related issues or tasks

**Example Commit Message**:
```
feat: optimize Quarkus reflection for native image performance

- Split deployment processor by reflection requirements (5 specialized BuildSteps)
- Apply fine-grained @RegisterForReflection parameters to application classes
- Eliminate unnecessary method/field reflection for CDI beans
- Replace string constants with type-safe references

Performance improvements:
- Native image size: reduced by ~15%
- Build time: improved by ~8%
- Maintained full functionality

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## When to Apply This Process

### Optimization Triggers

Apply this process when:

* **New Quarkus Project**: Initial native optimization setup
* **Performance Issues**: Native image size or build time concerns
* **Reflection Errors**: Native compilation failures due to missing reflection
* **Framework Updates**: After major Quarkus version upgrades
* **Code Reviews**: Identifying over-registered reflection
* **Performance Audits**: Systematic optimization reviews

### Module-by-Module Strategy

For large projects:

1. **Start with Extension Modules**: Deployment processors first
2. **Application Modules**: Core application classes second
3. **Test Modules**: Verify optimization effectiveness
4. **Integration Testing**: Full application native testing

### Risk Assessment

**How to Determine Risk Level**:

Use these concrete criteria to assess optimization safety:

**Low Risk** - Classes you own with no framework interaction:
- ✅ Simple domain objects/DTOs without framework annotations
- ✅ Utility classes with only static methods
- ✅ Value objects (records, @Value classes) with no serialization
- ✅ Classes that you fully control and can test comprehensively

**Medium Risk** - Classes with framework annotations but standard patterns:
- ⚠️ CDI beans with `@ApplicationScoped`, `@RequestScoped` using standard injection patterns
- ⚠️ JAX-RS resources with standard `@Path`, `@GET`, `@POST` annotations
- ⚠️ Data classes using Jackson/JSON-B with simple serialization
- ⚠️ Classes with inheritance where parent classes are also in your codebase

**High Risk** - Classes implementing framework SPIs or using advanced features:
- ❌ Classes implementing Quarkus/CDI SPIs (e.g., `BeanConfigurator`, `Interceptor`)
- ❌ Classes with runtime proxy generation (CDI interceptors, decorators)
- ❌ Classes using advanced reflection features (dynamic class loading, annotation synthesis)
- ❌ Third-party library classes (you don't control the code)
- ❌ Classes with complex annotation processing or meta-annotations

**Examples**:

```java
// LOW RISK - Simple domain object
public record UserData(String name, String email) {}

// MEDIUM RISK - Standard CDI bean
@ApplicationScoped
public class UserService {
    @Inject UserRepository repository;
    public User findUser(String id) { ... }
}

// HIGH RISK - Framework SPI implementation
@Interceptor
@Logged
public class LoggingInterceptor {
    @AroundInvoke
    public Object logInvocation(InvocationContext ctx) { ... }
}
```

## Success Metrics

Track these metrics to measure optimization effectiveness:

### Performance Metrics
* **Native Image Size**: Target 10-20% reduction
* **Build Time**: Target 5-15% improvement
* **Startup Time**: Maintain or improve
* **Memory Usage**: Maintain or improve

### Quality Metrics
* **Reflection Registration Accuracy**: Zero over-registration
* **Test Coverage**: Maintain 100% of original coverage
* **Functionality**: Zero regression
* **Code Quality**: Maintain or improve quality scores

### Process Metrics
* **Time to Complete**: Track optimization effort
* **Issues Found**: Number of reflection-related bugs prevented
* **Review Feedback**: Quality of optimization implementation

## Troubleshooting

### Common Issues

**Native Compilation Failures**:
1. Check for missing reflection registration
2. Verify reflection scope parameters are sufficient
3. Test individual class reflection requirements

**Runtime Errors in Native Mode**:
1. Identify missing method/field reflection
2. Check for dynamic class loading issues
3. Verify CDI bean instantiation works

**Performance Regressions**:
1. Review reflection scope - may be too restrictive
2. Check for unintended reflection removal
3. Verify framework integration still works

### Rollback Procedures

If optimization causes issues:
1. Revert to previous reflection configuration
2. Isolate problematic changes
3. Apply incremental optimization
4. Test each change independently

## References

* [Quarkus Native Applications Guide](https://quarkus.io/guides/writing-native-applications-tips)
