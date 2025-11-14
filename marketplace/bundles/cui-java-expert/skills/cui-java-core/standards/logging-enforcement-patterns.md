# Logging Enforcement Patterns

Comprehensive patterns for enforcing CUI logging standards through automated analysis and correction.

## Overview

This document provides detailed patterns for:
- Detecting LogRecord usage violations
- Analyzing test coverage for LogRecords
- Batch correction strategies
- Identifier numbering validation

These patterns support automated enforcement tools that ensure compliance with CUI logging standards.

## Violation Detection Patterns

### Pattern 1: Find All Logging Statements

**Use Grep to locate all logger invocations:**

```
Grep: pattern="LOGGER\.(info|debug|trace|warn|error|fatal)\("
      output_mode="content"
      -n=true
```

This captures all logging statements with line numbers for analysis.

### Pattern 2: Extract Logging Context

**For each logging statement found:**

1. **Extract context**:
   - File path and line number (from Grep output)
   - Log level (info/debug/trace/warn/error/fatal)
   - Full statement (read surrounding lines if needed using Read tool)

2. **Example extraction**:
   ```
   File: src/main/java/com/example/AuthService.java:45
   Level: info
   Statement: LOGGER.info("User %s logged in", username);
   ```

### Pattern 3: Determine LogRecord Usage

**Check if statement uses LogRecord:**

Analyze the first parameter after the log level method:

**LogRecord Pattern (COMPLIANT for INFO/WARN/ERROR/FATAL):**
```java
LOGGER.info(INFO.USER_LOGIN, ...)      // LogRecord from static import
LOGGER.error(ERROR.DATABASE_FAILED, ...)
LOGGER.warn(exception, WARN.RATE_LIMIT, ...)  // With exception first
```

**Direct String Pattern (COMPLIANT for DEBUG/TRACE only):**
```java
LOGGER.debug("Starting validation")
LOGGER.trace("Token value: %s", token)
```

**Detection Logic:**
- If first parameter matches pattern `[A-Z_]+\.[A-Z_]+` → LogRecord usage
- If first parameter is string literal or format string → Direct string usage
- If first parameter is `exception` or `Throwable` → Check second parameter

### Pattern 4: Apply Validation Rules

Apply validation rules from **logging-standards.md**:
- **LogRecord for INFO/WARN/ERROR/FATAL** (lines 111-193): Violation type = MISSING_LOGRECORD if using direct string
- **Direct Strings for DEBUG/TRACE** (lines 194-210): Violation type = PROHIBITED_LOGRECORD if using LogRecord

See logging-standards.md for complete rules, rationale, and examples.

### Pattern 5: Record Violations

**Violation Record Structure:**
```
Violation Type: [MISSING_LOGRECORD | PROHIBITED_LOGRECORD]
Location: {file}:{line}
Level: {level}
Current Statement: {code}
Required Pattern: {corrected_code}
```

**Example:**
```
Violation Type: MISSING_LOGRECORD
Location: src/main/java/com/example/AuthService.java:45
Level: info
Current Statement: LOGGER.info("User %s logged in", username);
Required Pattern: LOGGER.info(INFO.USER_LOGIN, username);
```

## Coverage Analysis Patterns

### Pattern 6: Extract LogRecord Definitions

**Find all LogRecord constants in LogMessages classes:**

```
Grep: pattern="LogRecordModel\.builder\(\)"
      output_mode="content"
      -n=true
      glob="**/*LogMessages.java"
```

**For each LogRecord, extract:**
- Constant name (e.g., `USER_LOGIN`)
- Prefix (e.g., `AUTH`)
- Identifier (e.g., `1`)
- Level (from enclosing class: INFO, WARN, ERROR, FATAL)

**Example:**
```java
public static final LogRecord USER_LOGIN = LogRecordModel.builder()
    .template("User %s logged in successfully")
    .prefix("AUTH")     // Prefix: AUTH
    .identifier(1)      // Identifier: 1
    .build();           // Constant: USER_LOGIN, Level: INFO
```

### Pattern 7: Find Production Usage

**Search for LogRecord usage in production code:**

```
Grep: pattern="INFO\.USER_LOGIN|WARN\.RATE_LIMIT|ERROR\.DATABASE_ERROR"
      output_mode="files_with_matches"
      glob="src/main/**/*.java"
```

**Alternative - Search by constant reference:**
```
Grep: pattern="{LEVEL}\.{CONSTANT_NAME}"
      output_mode="files_with_matches"
```

**Result:** List of files where LogRecord is used in production code.

### Pattern 8: Find Test Coverage (LogAssert)

**Search for LogAssert verification of this LogRecord:**

Method 1 - Search by identifier:
```
Grep: pattern="LogAssert.*{PREFIX}-{IDENTIFIER}"
      output_mode="files_with_matches"
      glob="src/test/**/*.java"
```

Method 2 - Search by resolveIdentifierString:
```
Grep: pattern="{CONSTANT_NAME}\.resolveIdentifierString\(\)"
      output_mode="files_with_matches"
      glob="src/test/**/*.java"
```

**Result:** List of test files that verify this LogRecord.

### Pattern 9: Determine Coverage Status

**Analysis Logic:**

| Production Usage | Test Coverage | Status | Action Required |
|-----------------|---------------|--------|-----------------|
| ❌ No | ❌ No | UNUSED | Remove LogRecord |
| ✅ Yes | ❌ No | UNTESTED | Add LogAssert test |
| ❌ No | ✅ Yes | TEST_ONLY | USER REVIEW (critical bug) |
| ✅ Yes | ✅ Yes | COMPLIANT | No action |

**Coverage Record Structure:**
```
LogRecord: {PREFIX}-{IDENTIFIER} ({CONSTANT_NAME})
Production Usage: [YES/NO] - {files if yes}
Test Coverage: [YES/NO] - {files if yes}
Status: [COMPLIANT | UNTESTED | UNUSED | TEST_ONLY]
Action: [NONE | ADD_TESTS | REMOVE_LOGRECORD | USER_REVIEW]
```

**Example:**
```
LogRecord: AUTH-001 (USER_LOGIN)
Production Usage: YES - AuthService.java, LoginHandler.java
Test Coverage: NO
Status: UNTESTED
Action: ADD_TESTS
```

## Batch Correction Strategies

### Pattern 10: Group Violations by Type

**Batch 1: Missing LogRecord Conversions**
- All INFO/WARN/ERROR/FATAL statements using direct strings
- Requires: Identify corresponding LogRecord constant or create new one
- Agent: java-code-implementer

**Batch 2: Prohibited LogRecord Removals**
- All DEBUG/TRACE statements using LogRecord
- Requires: Convert to direct string format
- Agent: java-code-implementer

**Batch 3: Unused LogRecord Cleanup**
- All LogRecords with no production or test references
- Requires: Remove from LogMessages class
- Agent: java-code-implementer

**Batch 4: Missing Test Coverage**
- All LogRecords with production usage but no tests
- Requires: Create LogAssert verification tests
- Command: /java-implement-tests

**Batch 5: Test-Only LogRecords**
- All LogRecords with test references but no production usage
- Requires: USER REVIEW (critical bug - stop execution)

### Pattern 11: Batch Execution Template

**For code changes (Batches 1-3):**
```
SlashCommand: /java-implement-code task="Fix {violation-type}:
Fix logging violations in the following locations:

{list of files with violations}

Apply corrections:
{for each violation: location, current code, required correction}

Verify compilation after changes."
```

**For test additions (Batch 4):**
```
SlashCommand: /java-implement-tests task="Add LogAssert tests:
Add LogAssert verification for untested LogRecords.

For each untested LogRecord:
- LogRecord: {PREFIX}-{IDENTIFIER} ({CONSTANT_NAME})
- Production usage: {file}:{line}
- Add test verifying this log message is produced

    Use @EnableTestLogger and LogAsserts.
    Verify tests pass.
```

**For user review (Batch 5):**
```
⚠️ CRITICAL: Test-only LogRecords detected

The following LogRecords are referenced in tests but never used in production:
{list with PREFIX-ID and constant names}

This indicates either:
1. Missing production code that should log these messages
2. Tests verifying non-existent functionality

Please review and determine action:
- Add production code that logs these messages, OR
- Remove LogRecords and associated tests

Execution stopped pending user guidance.
```

## Identifier Numbering Validation

### Pattern 12: Reference Existing Standards

**IMPORTANT**: Identifier numbering rules are fully documented in `logging-standards.md`.

**Standard Ranges:**
- INFO: 001-099
- WARN: 100-199
- ERROR: 200-299
- FATAL: 300-399

**For enforcement tools:**
1. Read identifier range rules from `logging-standards.md`
2. Apply validation: identifiers must be within correct range for level
3. Apply renumbering: identifiers should be consecutive within each range

**See:** `logging-standards.md` → Message Identifier Ranges section

### Pattern 13: Detect Numbering Issues

**Extract all identifiers from LogMessages class:**

```
Grep: pattern="\.identifier\((\d+)\)"
      output_mode="content"
      -n=true
      path="{LogMessages.java}"
```

**For each level, check:**
1. **Range compliance**: All identifiers in correct range
2. **Ordering**: Identifiers are in sequential order
3. **Gaps**: No missing numbers in sequence
4. **Prohibited identifiers**: No identifiers outside standard ranges (would indicate DEBUG/TRACE usage)

**Issues to detect:**
- Out-of-range: INFO using identifier 150 (WARN range)
- Gaps: INFO has 1, 2, 5, 6 (missing 3, 4)
- Out-of-order: INFO has 5, 2, 8, 1
- Prohibited: Identifier 500 (no standard range - indicates DEBUG/TRACE violation)

### Pattern 14: Renumbering Protocol

**When renumbering needed:**

1. **Group by level**: Extract all identifiers for each level (INFO, WARN, ERROR, FATAL)
2. **Sort**: Order identifiers within each level
3. **Assign consecutive**: Renumber starting from level's base (001, 100, 200, 300)
4. **Create mapping**: Old identifier → New identifier

**Renumbering Map Example:**
```
INFO Level:
- USER_LOGIN: 5 → 1
- SESSION_CREATED: 12 → 2
- TOKEN_VALIDATED: 8 → 3

WARN Level:
- RATE_LIMIT: 105 → 100
- CLOCK_SKEW: 101 → 101 (no change)
```

**Apply changes:**
1. Update LogMessages class with new identifiers
2. Update LogMessages.adoc documentation with new identifiers
3. Verify no test references use hardcoded old identifiers

## Build Verification Protocol

### Pattern 15: Standard Build Verification

**Used at multiple enforcement phases:**
- Before enforcement (verify clean baseline)
- After corrections (verify changes compile)
- After renumbering (final verification)

**Standard Build Command:**
```
Task:
  subagent_type: cui-maven:maven-builder
  description: Verify build
  prompt: |
    Execute Maven build to verify codebase state.

    Parameters:
    - command: clean verify
    - outputMode: DEFAULT
    {- module: [module-name] (if specified)}

    Build must succeed with zero errors.
    Return detailed status with any errors/warnings found.
```

**Success Criteria:**
- Exit code: 0
- Build status: SUCCESS
- Errors: 0
- Test failures: 0

**Failure Handling:**
- Report: Build status, error details, test failures
- Stop execution: Do not proceed to next phase
- Return to caller: Allow user to fix issues

## Configuration Patterns

### Pattern 16: Module-Specific Configuration

**Configuration Structure in `.claude/run-configuration.md`:**

```markdown
## cui-java-enforce-logrecords

### Module: {module-name}

#### LogMessages Classes
- Package: com.example.auth → Class: AuthenticationLogMessages
- Package: com.example.token → Class: TokenLogMessages

#### LogMessages Documentation
- doc/LogMessages.adoc

### Module: {another-module}

#### LogMessages Classes
- Package: com.example.data → Class: DataLogMessages

#### LogMessages Documentation
- modules/{another-module}/doc/LogMessages.adoc
```

**Usage:**
1. Read configuration for command key: `cui-java-enforce-logrecords`
2. Find section for specified module
3. Extract LogMessages class paths
4. Extract LogMessages.adoc paths
5. If missing, attempt auto-discovery and ask user to confirm

### Pattern 17: Auto-Discovery Fallback

**If configuration missing or incomplete:**

1. **Locate LogMessages classes:**
   ```
   Glob: pattern="**/*LogMessages.java"
         path="{module-path or project-root}"
   ```

2. **Locate LogMessages documentation:**
   ```
   Glob: pattern="**/LogMessages.adoc"
         path="{module-path or project-root}"
   ```

3. **Verify confidence:**
   - 100% confident: Proceed with discovered paths
   - < 100% confident: Ask user to confirm paths

4. **Store in configuration:**
   - Update `.claude/run-configuration.md`
   - Add discovered paths for future runs

## Quality Checklist

When implementing enforcement tools using these patterns:

- [ ] Use Grep for all code searches (not Bash grep)
- [ ] Use Glob for file discovery (not Bash find)
- [ ] Apply violation detection patterns consistently
- [ ] Check both production usage and test coverage
- [ ] Group corrections into logical batches
- [ ] Execute build verification at each phase
- [ ] Handle test-only LogRecords as critical bugs
- [ ] Reference logging-standards.md for identifier rules
- [ ] Store configuration for repeated executions
- [ ] Provide clear user feedback at each phase

## Related Standards

- `logging-standards.md` - Core logging requirements and LogRecord usage rules
- `logmessages-documentation.md` - LogMessages.adoc documentation standards
- `testing-juli-logger.md` - LogAssert testing patterns
