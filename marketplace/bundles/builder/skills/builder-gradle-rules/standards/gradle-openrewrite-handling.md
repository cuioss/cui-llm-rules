# Gradle OpenRewrite Handling

Standards for handling OpenRewrite markers in Gradle projects.

## OpenRewrite in Gradle

### Plugin Setup

```kotlin
// build.gradle.kts
plugins {
    id("org.openrewrite.rewrite") version "6.x.x"
}

rewrite {
    activeRecipe("org.openrewrite.java.cleanup.CommonStaticAnalysis")
}

dependencies {
    rewrite("org.openrewrite.recipe:rewrite-static-analysis:1.x.x")
}
```

### Running OpenRewrite

```bash
# Dry run (show changes without applying)
./gradlew rewriteDryRun

# Apply changes
./gradlew rewriteRun

# Discover available recipes
./gradlew rewriteDiscover
```

## Marker Format

OpenRewrite leaves TODO markers in code:

```java
/*~~(TODO: message about the issue)>*/affectedCode();
```

## Marker Categories

### Category 1: LogRecord Warnings (AUTO-SUPPRESS)

Markers from `CuiLogRecordPatternRecipe`:

```java
/*~~(TODO: Use LogRecord pattern for logging)>*/log.debug("message");
```

**Action**: Auto-suppress for debug/trace logging
**Reason**: Often intentional for performance in hot paths

### Category 2: Exception Warnings (AUTO-SUPPRESS)

Markers from `InvalidExceptionUsageRecipe`:

```java
/*~~(TODO: Review exception handling)>*/catch (Exception e) { ... }
```

**Action**: Auto-suppress for framework patterns
**Reason**: Some patterns are intentional

### Category 3: Other Markers (ASK USER)

All other markers require user decision:

```java
/*~~(TODO: Consider using modern API)>*/oldApi.call();
```

**Action**: Present to user for decision
**Options**:
1. Apply suggested change
2. Suppress with comment
3. Ignore (mark as acceptable)

## Suppression Syntax

### Single Line Suppression

```java
// cui-rewrite:disable RecipeName
affectedCode();
```

### Block Suppression

```java
// cui-rewrite:disable RecipeName
affectedCode1();
affectedCode2();
// cui-rewrite:enable RecipeName
```

### Multiple Recipes

```java
// cui-rewrite:disable Recipe1, Recipe2
affectedCode();
```

## Iteration Workflow

### Step 1: Search for Markers

```bash
python3 scripts/search-openrewrite-markers.py --source-dir src
```

### Step 2: Categorize Results

- `auto_suppress`: Apply suppression automatically
- `ask_user`: Present choices to user

### Step 3: Auto-Suppress Safe Markers

For auto-suppressible markers, add suppression comments:

```java
// cui-rewrite:disable CuiLogRecordPatternRecipe
log.trace("Performance-critical path");
```

### Step 4: User Decision for Others

Present remaining markers with options:
1. Apply the suggested fix
2. Add suppression comment
3. Mark as acceptable (add to acceptable patterns)

### Step 5: Verify Build

After changes:

```bash
./gradlew build
./gradlew rewriteDryRun
```

## Integration with Build Workflow

### Pre-Build Check

1. Run `search-openrewrite-markers.py`
2. Auto-suppress category 1 and 2
3. If category 3 exists, report to user

### Post-Rewrite Verification

1. Run `./gradlew rewriteRun`
2. Search for new markers
3. Categorize and handle
4. Verify clean build

## Recipe Configuration

### Disable Specific Recipes

In `build.gradle.kts`:

```kotlin
rewrite {
    activeRecipe("org.openrewrite.java.cleanup.CommonStaticAnalysis")

    // Exclude specific recipes
    exclusion("org.openrewrite.java.cleanup.UnnecessaryParentheses")
}
```

### Recipe Arguments

```kotlin
rewrite {
    activeRecipe(
        "org.openrewrite.java.ChangePackage",
        "oldPackageName" to "com.old",
        "newPackageName" to "com.new"
    )
}
```
