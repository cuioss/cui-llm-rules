= POM Maintenance Process
:toc: left
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js


== Purpose

This document defines the comprehensive process for maintaining and optimizing Maven POM files across Java projects. It provides systematic approaches for dependency management, BOM utilization, version optimization, and POM quality improvements while adhering to Maven best practices and enterprise standards.

== Related Documentation

* Maven Integration Standards (see maven-integration.md) - JavaScript/Maven integration patterns

== Pre-Maintenance Checklist

**Requirements**: Execute the following verification steps before starting POM maintenance:

1. [ ] **Build Verification**: `./mvnw clean verify` - ensure all modules build successfully
2. [ ] **Dependency Analysis**: `./mvnw dependency:analyze` - identify unused and undeclared dependencies
3. [ ] **Dependency Tree**: `./mvnw dependency:tree` - record current dependency structure
4. [ ] **OpenRewrite Execution**: `./mvnw -Prewrite-maven-clean rewrite:run` - fix all errors and warnings
5. [ ] **Maven Wrapper Update**: Check and update Maven wrapper to latest version
6. [ ] **Module Inventory**: List all modules and their relationships for systematic processing

== Maven Wrapper Maintenance

**Purpose**: Ensure consistent Maven version across all development environments and CI/CD pipelines.

=== Update Process

**Requirements**:

1. **Check Current Version**: `./mvnw --version`
2. **Update Wrapper**: `./mvnw wrapper:wrapper -Dmaven=<latest-version>`
3. **Verify Scripts**: Ensure both `mvnw` and `mvnw.cmd` are updated
4. **Script-Only Mode**: Use script-only mode (default since 3.2.0) to avoid binary files in repository
5. **Commit Changes**: Create separate commit for wrapper updates

=== Best Practices

* Update wrapper before starting major POM maintenance
* Use consistent wrapper version across all organization projects
* Include wrapper scripts in version control
* Document Maven version requirements in README

== BOM (Bill of Materials) Management

**Overview**: Centralized dependency version management through BOM POMs ensures consistency and reduces version conflicts across multi-module projects.

=== BOM Structure Requirements

**Mandatory Elements**:

* **Packaging Type**: Use `<packaging>pom</packaging>`
* **Dependency Management**: All versions defined in `<dependencyManagement>` section
* **No Direct Dependencies**: BOMs should not contain `<dependencies>` section
* **Property-Based Versions**: All versions defined using properties

=== BOM Usage Rules

**If a project provides a BOM**:

1. **Universal Usage**: All modules MUST import or inherit from the BOM
2. **Centralized Management**: ALL dependency management MUST reside in the BOM
3. **No Version Overrides**: Child modules must not override BOM-defined versions
4. **Single Source of Truth**: BOM is the only place for version definitions

=== BOM Implementation Pattern

[source,xml]
----
<!-- In CUI project BOM POM -->
<properties>
    <version.quarkus>3.5.0</version.quarkus>
    <version.cui.test.generator>2.4.0</version.cui.test.generator>
    <version.cui.core.ui.model>2.3.0</version.cui.core.ui.model>
</properties>

<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>io.quarkus</groupId>
            <artifactId>quarkus-bom</artifactId>
            <version>${version.quarkus}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
        <dependency>
            <groupId>de.cuioss.test</groupId>
            <artifactId>cui-test-generator</artifactId>
            <version>${version.cui.test.generator}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
----

[source,xml]
----
<!-- In consuming CUI module -->
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>de.cuioss</groupId>
            <artifactId>cui-project-bom</artifactId>
            <version>${project.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
----

== Dependency Management Standards

**Overview**: Proper dependency management ensures build reproducibility, reduces conflicts, and simplifies maintenance.

=== General Requirements

1. **Use Dependency Management**: ALL dependency declarations must use `<dependencyManagement>` for version control
2. **Property-Based Versions**: ALL versions (dependencies and plugins) must use properties
3. **Version Reuse**: ALWAYS reuse versions from parent POMs or imported BOMs - double-check before adding new versions

=== Property Naming Conventions

[source,xml]
----
<properties>
    <!-- Dependency versions - use version.* prefix -->
    <version.quarkus>3.5.0</version.quarkus>
    <version.cui.core.ui.model>24.1.0</version.cui.core.ui.model>
    <version.cui.java.tools>2.5.1</version.cui.java.tools>
    <version.junit.jupiter>5.9.3</version.junit.jupiter>
    
    <!-- Plugin versions - use maven.*.plugin.version pattern -->
    <maven.compiler.plugin.version>3.11.0</maven.compiler.plugin.version>
    <maven.surefire.plugin.version>3.0.0-M7</maven.surefire.plugin.version>
    
    <!-- Non-maven plugin versions - use *.maven.plugin.version pattern -->
    <jacoco.maven.plugin.version>0.8.13</jacoco.maven.plugin.version>
    <asciidoctor.maven.plugin.version>3.2.0</asciidoctor.maven.plugin.version>
</properties>
----

=== Dependency Aggregation Rules

**Consolidation Criteria**:

1. **Universal Dependencies**: If ALL sub-modules use the same dependency, move declaration to parent POM
2. **Partial Usage**: If at least one sub-module does not use a parent-provided dependency, it must be moved to ALL sub-modules that need it
3. **Verification Process**: Before consolidation, verify usage across all modules using `./mvnw dependency:analyze`

=== Dependency Verification Process

**For each dependency, analyze**:

1. **Usage Verification**: Determine if dependency is actually used (not just declared)
2. **Scope Optimization**: Verify appropriate scope assignment
3. **Transitive Analysis**: Review transitive dependencies for conflicts

Note: Version updates are handled by Dependabot - focus on structure and usage only.

== Scope Optimization

**Overview**: Proper scope assignment reduces build size, improves security, and clarifies dependency purposes.

=== Scope Analysis Process

**For each dependency, evaluate**:

1. **compile → provided**: Can runtime environment provide this dependency?
2. **compile → runtime**: Is this only needed at runtime, not compilation?
3. **compile → test**: Is this only used in test code?
4. **provided → test**: Is this provided dependency only used in tests?

=== Scope Guidelines

**Scope Assignment Rules**:

* **compile**: Required for compilation and runtime, not provided by container
* **provided**: Required for compilation but provided by runtime (e.g., servlet-api, lombok)
* **runtime**: Not needed for compilation but required at runtime (e.g., JDBC drivers)
* **test**: Only needed for test compilation and execution
* **import**: Only for BOM imports in `<dependencyManagement>`
* **system**: AVOID - indicates design problem

== OpenRewrite Integration

**Purpose**: Automated POM cleanup and standardization using OpenRewrite recipes.

=== Execution Process

1. **Initial Run**: `./mvnw -Prewrite-maven-clean rewrite:run`
2. **Error Resolution**: Fix all reported errors before proceeding
3. **Warning Review**: Address warnings that impact build quality
4. **Dry Run Verification**: Use `./mvnw rewrite:dryRun` to preview changes
5. **Recipe Application**: Apply specific recipes for targeted improvements

=== Common Recipes

**Recommended Recipes**:

* **ManageDependencies**: Move versions to dependencyManagement
* **UpgradeDependencyVersion**: Update to newer versions with semantic versioning
* **RemoveUnusedImports**: Clean up unnecessary dependencies
* **OrderPomElements**: Standardize POM element ordering

== Maintenance Workflow

=== Analysis Phase

1. **Execute OpenRewrite**: `./mvnw -Prewrite-maven-clean rewrite:run` - fix all errors and warnings
2. **Dependency Analysis**: `./mvnw dependency:analyze` - identify issues
3. **Tree Analysis**: `./mvnw dependency:tree` - understand structure
4. **BOM Verification**: Verify all modules use project BOM if available
5. **Version Audit**: Check for duplicate version declarations
6. **Scope Review**: Identify misaligned dependency scopes
7. **Module Dependencies**: Map inter-module dependencies

=== Implementation Phase

==== Step 1: OpenRewrite Cleanup

[source,bash]
----
# Execute rewrite with cleanup profile
./mvnw -Prewrite-maven-clean rewrite:run

# Review and fix all errors
# Address critical warnings
----

==== Step 2: Maven Wrapper Update

[source,bash]
----
# Update to latest Maven version
./mvnw wrapper:wrapper -Dmaven=3.9.6

# Verify update
./mvnw --version
----

==== Step 3: BOM Implementation

**If project has a BOM**:

1. Move all dependency versions to BOM
2. Ensure all modules import/inherit BOM
3. Remove version overrides from child modules
4. Verify with `./mvnw dependency:tree`

==== Step 4: Dependency Management

1. **Property Extraction**: Convert all hardcoded versions to properties
2. **Version Reuse**: Check parent/imported BOMs before adding versions
3. **Consolidation**: Move common dependencies to appropriate parent level
4. **Unused Removal**: Remove dependencies identified as unused

==== Step 5: Scope Optimization

1. **Analyze Each Dependency**: Review actual usage and runtime requirements
2. **Apply Scope Changes**: Update scopes based on analysis
3. **Test Impact**: `./mvnw clean verify` after scope changes
4. **Document Changes**: Note significant scope changes in commit message

=== Verification Phase

Execute these verification steps to ensure POM maintenance was successful:

1. **Clean Build**: `./mvnw clean install`
2. **Dependency Analysis**: `./mvnw dependency:analyze`
3. **Enforcer Rules**: `./mvnw enforcer:enforce`
4. **Tree Verification**: `./mvnw dependency:tree`
5. **Module Testing**: `./mvnw clean verify -pl <module>`

== Multi-Module Considerations

=== Parent POM Management

**Requirements**:

* Place truly universal dependencies in parent `<dependencies>`
* Use `<dependencyManagement>` for version control only
* Define all plugin versions in `<pluginManagement>`
* Maintain clear separation between aggregation and inheritance

=== Module Dependency Rules

1. **Build Order**: Let Maven Reactor determine order through dependencies
2. **Inter-Module Versions**: Use `${project.version}` for internal dependencies
3. **Selective Building**: Use `-pl`, `--also-make`, `--also-make-dependents` flags
4. **Dependency Declaration**: Explicitly declare all direct dependencies

== Version Management

=== Property Organization

[source,xml]
----
<properties>
    <!-- Project version -->
    <revision>1.0.0-SNAPSHOT</revision>
    
    <!-- CUI dependency versions - use version.cui.* prefix -->
    <version.cui.core.ui.model>2.3.0</version.cui.core.ui.model>
    <version.cui.java.tools>2.5.1</version.cui.java.tools>
    <version.cui.test.generator>2.4.0</version.cui.test.generator>
    
    <!-- External dependency versions - use version.* prefix -->
    <version.quarkus>3.5.0</version.quarkus>
    <version.junit.jupiter>5.9.3</version.junit.jupiter>
    <version.lombok>1.18.38</version.lombok>
    
    <!-- Maven plugin versions - use maven.*.plugin.version pattern -->
    <maven.compiler.plugin.version>3.14.0</maven.compiler.plugin.version>
    <maven.surefire.plugin.version>3.5.3</maven.surefire.plugin.version>
    <maven.dependency.plugin.version>3.8.1</maven.dependency.plugin.version>
    
    <!-- Non-maven plugin versions - use *.maven.plugin.version pattern -->
    <jacoco.maven.plugin.version>0.8.13</jacoco.maven.plugin.version>
    <lombok-maven-plugin.version>1.18.20.0</lombok-maven-plugin.version>
    
    <!-- Configuration properties -->
    <maven.compiler.source>21</maven.compiler.source>
    <maven.compiler-plugin.release>21</maven.compiler-plugin.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
</properties>
----

=== Version Update Policy

**Important**: Dependency version updates are managed automatically by Dependabot and are NOT part of this maintenance process. Focus on structure, organization, and optimization rather than version currency.

== Common Issues and Solutions

=== Issue: Dependency Conflicts

**Solution**:

1. Use `./mvnw dependency:tree -Dverbose` to identify conflicts
2. Add explicit versions to `<dependencyManagement>`
3. Use `<exclusions>` for unwanted transitive dependencies
4. Verify resolution with enforcer plugin

=== Issue: Unused Dependencies

**Solution**:

1. Run `./mvnw dependency:analyze`
2. Review reported unused dependencies
3. Handle false positives with plugin configuration
4. Remove truly unused dependencies

=== Issue: Version Duplication

**Solution**:

1. Search for hardcoded versions across POMs
2. Extract to properties in appropriate parent/BOM
3. Reference properties consistently
4. Use OpenRewrite recipes for automation

=== Issue: Scope Misalignment

**Solution**:

1. Review dependency actual usage
2. Check runtime environment provisions
3. Update scopes appropriately
4. Test thoroughly after changes

== Quality Gates

**Mandatory Checks**:

1. [ ] All modules build successfully: `./mvnw clean install`
2. [ ] No dependency analysis warnings: `./mvnw dependency:analyze`
3. [ ] No version conflicts: `./mvnw enforcer:enforce`
4. [ ] All tests pass: `./mvnw clean verify`
5. [ ] No OpenRewrite errors: `./mvnw -Prewrite-maven-clean rewrite:run`

== Best Practices Summary

1. **Always** run OpenRewrite before starting manual maintenance
2. **Always** update Maven wrapper to latest stable version
3. **Always** use properties for all versions
4. **Always** check parent/imported BOMs before adding versions
5. **Never** override BOM-defined versions in child modules
6. **Never** use system scope dependencies
7. **Never** leave unused dependencies in POMs
8. **Always** verify build after scope changes
9. **Always** document significant changes in commit messages
10. **Never** manually update dependency versions during maintenance (handled by Dependabot)

== See Also

**Maven Documentation**:

* link:https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html[Maven Dependency Mechanism]
* link:https://maven.apache.org/enforcer/maven-enforcer-plugin/[Maven Enforcer Plugin]
* link:https://maven.apache.org/plugins/maven-dependency-plugin/[Maven Dependency Plugin]

**Related Standards**:

* Maven Integration Standards (see maven-integration.md in this skill)