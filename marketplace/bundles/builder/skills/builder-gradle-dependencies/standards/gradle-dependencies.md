# Gradle Dependency Standards

Standards for Gradle dependency management, version catalog usage, and build configuration quality.

## Version Catalog (libs.versions.toml)

### Location

```
gradle/libs.versions.toml
```

### Structure

```toml
[versions]
# Version declarations
spring = "6.1.0"
junit = "5.10.0"
lombok = "1.18.30"

[libraries]
# Library declarations with version references
spring-core = { module = "org.springframework:spring-core", version.ref = "spring" }
spring-context = { module = "org.springframework:spring-context", version.ref = "spring" }
junit-jupiter = { module = "org.junit.jupiter:junit-jupiter", version.ref = "junit" }
lombok = { module = "org.projectlombok:lombok", version.ref = "lombok" }

[bundles]
# Logical groupings of libraries
spring = ["spring-core", "spring-context", "spring-web"]
testing = ["junit-jupiter", "assertj-core", "mockito-core"]

[plugins]
# Plugin declarations
spring-boot = { id = "org.springframework.boot", version = "3.2.0" }
```

### Usage Rules

1. **ALL versions in catalog**: No hardcoded versions in build.gradle(.kts)
2. **Consistent naming**: Use kebab-case for library names
3. **Group related versions**: Use version references for related libraries
4. **Use bundles**: Group commonly used together libraries

### Version Reference Naming

| Type | Pattern | Example |
|------|---------|---------|
| Framework | `{framework}` | `spring`, `quarkus` |
| Testing | `{framework}` | `junit`, `mockito` |
| Tools | `{tool}` | `lombok`, `mapstruct` |
| Plugins | `{plugin}Plugin` | `spotlessPlugin` |

## Dependency Configuration

### Configurations

| Configuration | Purpose |
|--------------|---------|
| `api` | Exposed to consumers (library projects) |
| `implementation` | Internal, not exposed |
| `compileOnly` | Compile-time only |
| `runtimeOnly` | Runtime only |
| `testImplementation` | Test compile and runtime |
| `testCompileOnly` | Test compile only |
| `testRuntimeOnly` | Test runtime only |
| `annotationProcessor` | Annotation processors |

### Scope Selection Rules

```kotlin
// API: Consumers need this
api(libs.guava)  // For library projects only

// Implementation: Internal use
implementation(libs.spring.core)

// CompileOnly: Provided at runtime
compileOnly(libs.lombok)
annotationProcessor(libs.lombok)

// RuntimeOnly: Not needed at compile time
runtimeOnly(libs.postgresql.driver)

// Test: Testing only
testImplementation(libs.junit.jupiter)
testRuntimeOnly(libs.junit.platform.launcher)
```

### Scope Assignment

| Dependency Type | Configuration |
|-----------------|---------------|
| Lombok | `compileOnly` + `annotationProcessor` |
| JDBC drivers | `runtimeOnly` |
| Logging implementations | `runtimeOnly` |
| Test frameworks | `testImplementation` |
| Test launchers | `testRuntimeOnly` |
| Servlet API | `compileOnly` (container-provided) |
| Public library APIs | `api` (library projects only) |

## Build File Standards

### Kotlin DSL Preferred

```kotlin
// build.gradle.kts
plugins {
    `java-library`
    alias(libs.plugins.spring.boot)
}

dependencies {
    implementation(libs.spring.core)
    testImplementation(libs.bundles.testing)
}
```

### No Hardcoded Versions

**Incorrect**:
```kotlin
implementation("org.springframework:spring-core:6.1.0")
```

**Correct**:
```kotlin
implementation(libs.spring.core)
```

### Dependency Declaration Order

1. API dependencies
2. Implementation dependencies
3. CompileOnly dependencies
4. RuntimeOnly dependencies
5. AnnotationProcessor dependencies
6. Test dependencies

## Multi-Project Standards

### Root Build Configuration

```kotlin
// build.gradle.kts (root)
plugins {
    `java-library` apply false
}

subprojects {
    apply(plugin = "java-library")

    repositories {
        mavenCentral()
    }
}
```

### Subproject Dependencies

```kotlin
// core/build.gradle.kts
dependencies {
    implementation(project(":common"))
}
```

### Internal Dependencies

| Reference Type | When to Use |
|---------------|-------------|
| `project(":module")` | Same multi-project build |
| `libs.internal.module` | Published internal artifact |

## Dependency Analysis

### Show Dependencies

```bash
./gradlew dependencies --configuration compileClasspath
```

### Dependency Insight

```bash
./gradlew dependencyInsight --dependency log4j --configuration compileClasspath
```

### Check for Updates

Using `versions` plugin:

```bash
./gradlew dependencyUpdates
```

## Quality Criteria

### Mandatory Checks

1. **No hardcoded versions**: All versions via catalog
2. **No duplicate declarations**: Each dependency declared once
3. **Correct scopes**: Test dependencies in test configurations
4. **No unused dependencies**: Remove unused declarations
5. **No version conflicts**: Resolve conflicts explicitly

### Version Conflict Resolution

```kotlin
configurations.all {
    resolutionStrategy {
        // Force specific version
        force("com.google.guava:guava:32.1.3-jre")

        // Fail on conflict
        failOnVersionConflict()
    }
}
```

### Enforced Versions (Platform/BOM)

```kotlin
dependencies {
    // Import BOM
    implementation(platform(libs.spring.bom))

    // Dependencies without version (from BOM)
    implementation("org.springframework:spring-core")
}
```

## Repository Configuration

### Standard Setup

```kotlin
// settings.gradle.kts
dependencyResolutionManagement {
    repositories {
        mavenCentral()
        // Additional repositories if needed
    }
}
```

### Repository Order

1. Local (if development)
2. Organization internal (if applicable)
3. Maven Central
4. Specific vendor repositories (last resort)

## Migration from Hardcoded Versions

### Step 1: Inventory

List all hardcoded versions:

```bash
grep -r ":[0-9]" --include="*.gradle*" .
```

### Step 2: Extract to Catalog

Add to `gradle/libs.versions.toml`:

```toml
[versions]
extracted-lib = "1.2.3"

[libraries]
extracted-lib = { module = "com.example:lib", version.ref = "extracted-lib" }
```

### Step 3: Update Build Files

Replace:
```kotlin
implementation("com.example:lib:1.2.3")
```

With:
```kotlin
implementation(libs.extracted.lib)
```

### Step 4: Verify Build

```bash
./gradlew build
./gradlew dependencies
```
