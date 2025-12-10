# OpenRewrite Marker Handling Standards

## Purpose

This document defines standards for handling OpenRewrite TODO markers that appear in source code after recipe execution. These markers indicate code patterns that require manual review or suppression.

## Marker Format

OpenRewrite markers appear as special comments in source code:

```java
/*~~(TODO: message about the issue)>*/
```

Example:
```java
/*~~(TODO: CuiLogRecordPatternRecipe - LOGGER call does not use LogRecord)>*/
LOGGER.info("Direct string instead of LogRecord");
```

## Marker Search Pattern

Use this Grep pattern to find all markers:

```
/\*~~\(TODO:
```

Example command:
```
Grep: pattern="/\*~~\(TODO:" path="src" output_mode="files_with_matches"
```

## Marker Categories

### Category 1: LogRecord Warnings (AUTO-SUPPRESS)

**Recipe**: `CuiLogRecordPatternRecipe`

**Pattern**: LOGGER call not using LogRecord constant

**Auto-Suppression**: Add disable comment before LOGGER statement:
```java
// cui-rewrite:disable CuiLogRecordPatternRecipe
LOGGER.info("Direct message for debugging");
```

**When to suppress**:
- DEBUG/TRACE level logging (intentionally uses direct strings)
- Temporary debug statements
- Performance-critical paths where LogRecord lookup is avoided

### Category 2: Exception Warnings (AUTO-SUPPRESS)

**Recipe**: `InvalidExceptionUsageRecipe`

**Pattern**: Exception handling that doesn't follow CUI patterns

**Auto-Suppression**: Add disable comment before catch block:
```java
// cui-rewrite:disable InvalidExceptionUsageRecipe
catch (SomeException e) {
    // Intentional exception handling pattern
}
```

**When to suppress**:
- Framework-required exception handling patterns
- Interop with external libraries
- Performance-critical exception handling

### Category 3: Other Markers (ASK USER)

All other marker types require user confirmation before suppression:

1. Present the marker details to user
2. Explain what the marker means
3. Offer options: Suppress, Ignore, Manual fix
4. Document user's decision

## Suppression Syntax

### Single Line Suppression

```java
// cui-rewrite:disable RecipeName
<single statement>
```

### Block Suppression

```java
// cui-rewrite:disable RecipeName
<multiple statements>
// cui-rewrite:enable RecipeName
```

### Multiple Recipe Suppression

```java
// cui-rewrite:disable Recipe1, Recipe2
<statement>
```

## Iteration Workflow

1. **Initial Search**: Find all files with markers
2. **Categorize**: Group markers by recipe type
3. **Auto-Suppress**: Handle LogRecord and Exception categories
4. **User Decision**: Ask about other marker types
5. **Apply Changes**: Edit source files with suppressions
6. **Verify**: Re-run Maven build
7. **Check**: Confirm markers are gone

### Failure Conditions

Report failure and request manual intervention if:
- Markers persist after 3 fix iterations
- Markers multiply instead of decreasing
- Suppression syntax doesn't work for specific marker

## Example Handling Session

```
Found 5 OpenRewrite markers in 3 files:

src/main/java/Service.java:45 - CuiLogRecordPatternRecipe
  → AUTO-SUPPRESSING (LogRecord warning)

src/main/java/Handler.java:78 - InvalidExceptionUsageRecipe
  → AUTO-SUPPRESSING (Exception warning)

src/main/java/Processor.java:112 - SomeOtherRecipe
  → ASKING USER: This marker indicates [explanation]
    Options: [Suppress] [Ignore] [Manual Fix]

Applied 2 auto-suppressions, waiting for user on 1.
```

## Integration with Build Workflow

After any marker handling:

1. Run `./mvnw -l target/build-verify.log install` (without clean)
2. Parse output for remaining markers
3. If markers remain, repeat handling
4. After 3 iterations, report remaining markers

## See Also

- [Maven Build Execution Standards](maven-build-execution.md) - Build workflow integration
- [Acceptable Warnings Standards](maven-acceptable-warnings.md) - Warning management
