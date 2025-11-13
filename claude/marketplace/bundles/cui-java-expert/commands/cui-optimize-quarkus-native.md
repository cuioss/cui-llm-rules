---
name: cui-optimize-quarkus-native
description: Systematic Quarkus native image optimization with reflection registration and performance improvements
---

# CUI Quarkus Native Optimize Command

Orchestrates systematic Quarkus native image optimization workflow with focus on reflection registration optimization and performance tracking.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=cui-optimize-quarkus-native update="[your improvement]"` with:
1. Improved reflection analysis patterns
2. Better optimization strategies
3. More effective performance tracking
4. Enhanced native image compatibility checks
5. Any lessons learned about Quarkus native optimization

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **module** - Module name for single module optimization (optional, processes all if not specified)
- **phase** - Optimization phase: `analysis`, `deployment`, `application`, `verification`, `all` (default: `all`)

## WORKFLOW

### Step 0: Parameter Validation

**Validate parameters:**
- If `module` specified: verify module exists and is a Quarkus module
- Validate `phase` is one of: analysis, deployment, application, verification, all
- Set defaults if not provided
- Verify Quarkus native profile is configured

### Step 1: Load Optimization Standards

```
Skill: cui-java-expert:cui-java-cdi
```

This loads comprehensive Quarkus native optimization standards from `standards/quarkus-native.md`:
- Reflection registration optimization patterns
- Deployment processor optimization techniques
- Risk assessment framework
- Performance metrics tracking

**On load failure:**
- Report error
- Cannot proceed without standards
- Abort command

### Step 2: Pre-Optimization Verification

Execute pre-optimization checklist to establish baseline:

**2.1 Build Verification:**
```
Task:
  subagent_type: maven-builder
  description: Verify baseline build
  prompt: |
    Build and install project to verify baseline functionality.

    Parameters:
    - command: clean install
    - module: {module if specified, otherwise all}

    CRITICAL: Wait for completion. Ensure all tests pass before proceeding.
```

**On build failure:**
- Display build errors
- Prompt user: "[F]ix manually and retry / [A]bort"
- Cannot proceed until build passes

**2.2 Native Image Baseline:**
```
Task:
  subagent_type: maven-builder
  description: Build native image baseline
  prompt: |
    Build native image to verify Quarkus native compilation works and establish baseline metrics.

    Parameters:
    - command: clean package -Dnative
    - module: {module if specified, otherwise all}

    CRITICAL: Wait for completion (may take several minutes).
    Record and report:
    - Build time
    - Native executable size
    - Any compilation warnings or errors
```

**On native build failure:**
- Display native compilation errors
- This indicates missing reflection registration or incompatibilities
- Prompt user: "[I]nvestigate manually / [A]bort"

**2.3 Create Optimization Branch:**
```bash
git checkout -b native-optimization-{module-name or 'all'}-{timestamp}
```

**Record Baseline Metrics:**
- Native image build time: {time}
- Native executable size: {size}
- Tests passing: {count}

### Step 3: Phase 1 - Analysis and Planning

**Execute only if phase is `analysis` or `all`**

**3.1 Reflection Usage Analysis:**

Scan for reflection registrations:
```bash
# Find all RegisterForReflection usage
find . -name "*.java" -exec grep -l "@RegisterForReflection" {} \;

# Find deployment processor registrations
find . -name "*Processor.java" -exec grep -l "ReflectiveClassBuildItem" {} \;
```

**Analyze findings:**
- Count total reflection registrations
- Categorize by type (application classes, deployment processor)
- Identify optimization opportunities

**3.2 Reflection Requirements Assessment:**

Categorize classes by reflection requirements:
- **CDI beans**: Usually need constructors only
- **Data classes**: May need methods/fields for serialization
- **Configuration classes**: Builder pattern vs. property binding
- **Enum classes**: Usually need minimal reflection
- **Annotation classes**: Framework-specific requirements

**Document current state:**
- Total reflection registrations: {count}
- Application class registrations: {count}
- Deployment processor registrations: {count}
- Identified optimization opportunities: {list}

**Analysis Output:**
Present findings to user with optimization recommendations categorized by risk level (see quarkus-native.md Risk Assessment section)

### Step 4: Phase 2 - Deployment Processor Optimization

**Execute only if phase is `deployment` or `all`**

**4.1 Review Deployment Processors:**

For each deployment processor:
- Identify `ReflectiveClassBuildItem` registrations
- Group classes with similar reflection needs
- Identify opportunities to split by reflection requirements

**4.2 Implement Optimizations:**

Apply deployment processor optimizations following standards:
- Split by reflection requirements (constructor-only, methods-only, etc.)
- Replace string constants with type-safe class references
- Use AdditionalBeanBuildItem for CDI bean registration
- Optimize builder pattern classes (eliminate unnecessary constructor reflection)

**CRITICAL**: When registering CDI beans in deployment processor, remove duplicate `@RegisterForReflection` annotations from bean classes.

**4.3 Verification After Each Change:**
```
Task:
  subagent_type: maven-builder
  description: Test compilation
  prompt: |
    Compile module to verify deployment processor changes.

    Parameters:
    - command: clean compile
    - module: {module if specified, otherwise all}

    CRITICAL: Wait for completion. Fix any compilation errors immediately.
```

**4.4 Quality Verification:**
```
Task:
  subagent_type: maven-builder
  description: Run quality checks
  prompt: |
    Run pre-commit quality verification without tests.

    Parameters:
    - command: -Ppre-commit clean verify -DskipTests
    - module: {module if specified, otherwise all}

    CRITICAL: Wait for completion. Fix any quality issues.
```

### Step 5: Phase 3 - Application Class Optimization

**Execute only if phase is `application` or `all`**

**5.1 Review Application Classes:**

For each class with `@RegisterForReflection`:
- Assess actual reflection requirements
- Categorize by class type (CDI bean, data class, enum, annotation)
- Determine optimal reflection scope

**5.2 Implement Optimizations:**

Apply application class optimizations following standards:
- **CDI Beans**: Optimize to `@RegisterForReflection(methods = false, fields = false)`
- **Data Classes**: Assess serialization needs
- **Enum Classes**: Use `@RegisterForReflection(methods = false, fields = false)`
- **Annotation Classes**: Use `@RegisterForReflection(methods = false, fields = false)`

**Special Cases:**
- Lombok classes: Keep default `@RegisterForReflection`
- Serializable classes: May need methods/fields
- Framework integration: Some frameworks require specific reflection access

**5.3 Module Compilation:**
```
Task:
  subagent_type: maven-builder
  description: Compile module
  prompt: |
    Compile module to verify reflection annotations.

    Parameters:
    - command: clean compile
    - module: {module if specified, otherwise all}

    CRITICAL: Wait for completion. Fix any compilation errors.
```

**5.4 Full Module Build:**
```
Task:
  subagent_type: maven-builder
  description: Full module build
  prompt: |
    Build and install module with optimized reflection.

    Parameters:
    - command: clean install
    - module: {module if specified, otherwise all}

    CRITICAL: Wait for completion. Ensure all tests pass.
```

**On test failure:**
- Display test failures
- Optimization may be too aggressive - need to adjust reflection scope
- Prompt user: "[R]evert last change / [I]nvestigate manually / [A]bort"

### Step 6: Phase 4 - Verification and Testing

**Execute only if phase is `verification` or `all`**

**6.1 Reflection Verification Tests:**
```
Task:
  subagent_type: maven-builder
  description: Run reflection tests
  prompt: |
    Run all reflection-related tests.

    Parameters:
    - command: test -Dtest="*Reflection*Test"
    - module: {module if specified, otherwise all}

    CRITICAL: Wait for completion. Verify all reflection tests pass.
```

**6.2 Full Test Suite:**
```
Task:
  subagent_type: maven-builder
  description: Run full test suite
  prompt: |
    Run complete test suite with optimized reflection.

    Parameters:
    - command: clean install
    - module: {module if specified, otherwise all}

    CRITICAL: Wait for completion. Ensure all tests pass.
```

**6.3 Native Image Compilation:**
```
Task:
  subagent_type: maven-builder
  description: Build native image
  prompt: |
    Build native executable using GraalVM with optimized reflection.

    Parameters:
    - command: clean package -Dnative
    - module: {module if specified, otherwise all}

    CRITICAL: Wait for completion (may take several minutes).
    Record and report:
    - Build time
    - Native executable size
    - Any compilation warnings or errors
```

**6.4 Performance Metrics Comparison:**

Compare baseline metrics with optimized metrics:
```
BASELINE:
- Native image build time: {baseline_time}
- Native executable size: {baseline_size}

OPTIMIZED:
- Native image build time: {optimized_time}
- Native executable size: {optimized_size}

IMPROVEMENTS:
- Build time: {percentage change}
- Executable size: {percentage change}
```

**Success Criteria:**
- Native compilation succeeds
- All tests pass
- Performance metrics improved or maintained
- No functionality regression

### Step 7: Quality Assurance

**7.1 Final Quality Verification:**
```
Task:
  subagent_type: maven-builder
  description: Run quality checks
  prompt: |
    Run pre-commit quality verification without tests.

    Parameters:
    - command: -Ppre-commit clean verify -DskipTests
    - module: {module if specified, otherwise all}

    CRITICAL: Wait for completion. Fix all quality issues before committing.
```

**7.2 Final Build Verification:**
```
Task:
  subagent_type: maven-builder
  description: Final build verification
  prompt: |
    Run final build and test verification.

    Parameters:
    - command: clean install
    - module: {module if specified, otherwise all}

    CRITICAL: Wait for completion. Ensure all tests and quality checks pass.
```

### Step 8: Documentation and Commit

**8.1 Documentation Updates:**
- Check if module README needs updates for reflection architecture changes
- Document any special reflection requirements discovered
- Note performance improvements achieved

**8.2 Commit Changes:**

Follow git commit standards with performance metrics:

```
feat(native): optimize Quarkus reflection for native image performance

- Split deployment processor by reflection requirements ({count} specialized BuildSteps)
- Apply fine-grained @RegisterForReflection parameters to application classes
- Eliminate unnecessary method/field reflection for CDI beans
- Replace string constants with type-safe references

Performance improvements:
- Native image size: reduced by ~{percentage}%
- Build time: improved by ~{percentage}%
- Maintained full functionality

Module: {module-name}

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## ERROR HANDLING

### Build Failures
- Display detailed error output
- Identify root cause (compilation, tests, quality)
- Prompt for action: fix manually and retry, or abort

### Native Compilation Failures
- Display GraalVM error output
- Identify missing reflection registrations
- Suggest adding missing reflection or adjusting scope
- Prompt for action: investigate manually or abort

### Test Failures After Optimization
- Indicates reflection scope may be too restrictive
- Revert last optimization change
- Adjust reflection parameters
- Retry verification

### Performance Regression
- Compare metrics carefully
- Verify measurements are accurate
- Check for unintended reflection removal
- Consider whether trade-off is acceptable

## OPTIMIZATION TRIGGERS

Apply this command when:
- **New Quarkus Project**: Initial native optimization setup
- **Performance Issues**: Native image size or build time concerns
- **Reflection Errors**: Native compilation failures due to missing reflection
- **Framework Updates**: After major Quarkus version upgrades
- **Code Reviews**: Identifying over-registered reflection
- **Performance Audits**: Systematic optimization reviews

## SUCCESS METRICS

Track and report these metrics:

### Performance Metrics
- **Native Image Size**: Target 10-20% reduction
- **Build Time**: Target 5-15% improvement
- **Startup Time**: Maintain or improve
- **Memory Usage**: Maintain or improve

### Quality Metrics
- **Reflection Registration Accuracy**: Zero over-registration
- **Test Coverage**: Maintain 100% of original coverage
- **Functionality**: Zero regression
- **Code Quality**: Maintain or improve quality scores

### Process Metrics
- **Time to Complete**: Track optimization effort
- **Issues Found**: Number of reflection-related bugs prevented
- **Changes Made**: Count of optimizations applied

## REFERENCES

- Skill: `cui-java-expert:cui-java-cdi` - Contains `standards/quarkus-native.md` with detailed technical guidance
- [Quarkus Native Applications Guide](https://quarkus.io/guides/writing-native-applications-tips)
