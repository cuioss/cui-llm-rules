---
name: cui-logger-maintain
description: Execute systematic logging standards maintenance with plan tracking and comprehensive test coverage
---

# CUI Logger Maintain Command

Systematically implements and maintains logging standards across modules while preserving functionality and tracking progress via plan.md.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/cui-update-command command-name=cui-logger-maintain update="[your improvement]"` with:
1. Improved LogRecord discovery patterns
2. Better business logic test integration strategies
3. More efficient plan.md tracking workflows
4. Enhanced duplicate detection methods
5. Any lessons learned about logging maintenance

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- **module** - Module name for single module (optional, processes all if not specified)
- **create-plan** - Generate/regenerate plan.md from current state (optional, default: false)

## CRITICAL CONSTRAINTS

### Production Code Protection

**MUST:**
- Modify ONLY logging-related code
- Preserve all existing functionality
- Focus exclusively on logging implementation and testing

**MUST NOT:**
- Make non-logging production code changes
- Alter business logic behavior
- Change method signatures or APIs

### Bug Handling Process

**When non-logging production bugs discovered:**

1. **STOP** maintenance process immediately
2. **DOCUMENT** bug details:
   - Location (file, class, method, line)
   - Issue description
   - Potential impact
3. **ASK USER** for approval to fix non-logging production code
4. **WAIT** for explicit confirmation before proceeding
5. **SEPARATE COMMIT** for bug fix if approved (following git standards)
6. **RESUME** logging maintenance after bug fix committed

**Never fix non-logging bugs without user approval.**

### Testing Philosophy - CRITICAL

**LogAsserts MUST be in business logic tests:**

✅ **CORRECT - LogAsserts in existing business test:**
```java
@Test
void shouldRejectInvalidConfiguration() {
    // Business logic test
    assertThrows(ValidationException.class,
        () -> service.validate(badConfig));

    // Logging verification in same test
    assertLogMessagePresentContaining(TestLogLevel.ERROR,
        ERROR.INVALID_CONFIG.resolveIdentifierString());
}
```

❌ **WRONG - Standalone LogRecord coverage test:**
```java
@Test
void testLogRecordCoverage() {  // DON'T DO THIS!
    LOGGER.error(ERROR.INVALID_CONFIG.format());
    assertLogMessagePresent(...);
}
```

**Never create tests ONLY for LogRecord coverage. LogAsserts must always accompany business logic tests.**

## WORKFLOW

### Step 0: Parameter Validation

**Validate parameters:**
- If `module` specified: verify module exists
- If `create-plan` specified: will regenerate plan.md
- Determine processing scope (single module vs all)

### Step 1: Load Logging Standards

```
Skill: cui-java-core
```

This loads comprehensive logging standards including:
- logging-standards.md - Implementation standards for new code
- logging-maintenance-reference.md - Maintenance reference for existing code
- dsl-constants.md - DSL pattern for LogMessages structure

**On load failure:**
- Report error
- Cannot proceed without standards
- Abort command

### Step 2: Pre-Maintenance Verification

**2.1 Build Verification:**

```
Task:
  subagent_type: maven-builder
  description: Verify build before maintenance
  prompt: |
    Execute Maven build with pre-commit profile.

    Parameters:
    - command: -Ppre-commit clean verify -DskipTests
    - module: {module if specified, otherwise all}

    Build must pass before proceeding with logging maintenance.
```

**On build failure:**
- Display build errors
- Prompt user: "[F]ix build first / [A]bort"
- Track in `pre_verification_failures` counter
- Cannot proceed until build passes

**2.2 Module Identification:**

If `module` parameter not specified:
- Use Glob to identify all Maven modules
- Determine module processing order (dependencies first)
- Display module list to user

**2.3 Standards Review Confirmation:**

Display to user:
```
Logging Standards Loaded:
- Logger Configuration: CuiLogger only, no System.out/err
- LogRecord Usage: INFO/WARN/ERROR/FATAL must use LogRecord
- Testing Requirement: LogAsserts in BUSINESS LOGIC tests only
- Bug Handling: Must ask before fixing non-logging code

Ready to proceed? [Y]es / [N]o
```

### Step 3: Create/Update Planning Document

**3.1 Check for Existing plan.md:**

```
Read: {module-path}/plan.md  # If module specified
# OR
Read: plan.md  # If processing all modules
```

**3.2 If create-plan=true OR plan.md doesn't exist:**

Run LogRecord Discovery Script to generate inventory:

```
Bash: |
  #!/bin/bash
  MODULE_PATH="${module_path:-src}"

  echo "# LogRecord Test Coverage Status" > plan.md
  echo "" >> plan.md
  echo "## Summary" >> plan.md

  # Count total LogRecords
  TOTAL=$(grep -r "LogRecord.*=" --include="*LogMessages.java" $MODULE_PATH/main/java | wc -l)
  echo "- Total LogRecords: $TOTAL" >> plan.md

  # Count tested LogRecords
  TESTED=$(grep -r "LogAsserts.*resolveIdentifierString" --include="*Test.java" $MODULE_PATH/test/java | wc -l)
  echo "- Tested with LogAsserts: $TESTED" >> plan.md

  # Calculate missing
  MISSING=$((TOTAL - TESTED))
  echo "- Missing LogAsserts: $MISSING" >> plan.md
  echo "" >> plan.md

  echo "## LogRecord Inventory" >> plan.md
  echo "| LogRecord | Production Location | Business Test Location | Status |" >> plan.md
  echo "|-----------|-------------------|----------------------|--------|" >> plan.md

  # Find all LogRecords and their usage
  for record in $(grep -rh "public static final LogRecord" --include="*LogMessages.java" $MODULE_PATH/main/java | awk '{print $5}' | sort -u); do
    # Find production usage
    PROD_LOC=$(grep -rn "$record\.format\|$record::format" --include="*.java" $MODULE_PATH/main/java | head -1 | cut -d: -f1-2 | sed 's|.*/||')

    # Find test usage
    TEST_LOC=$(grep -rn "LogAsserts.*$record\|$record.*resolveIdentifierString" --include="*Test.java" $MODULE_PATH/test/java | head -1 | cut -d: -f1-2 | sed 's|.*/||')

    if [ -n "$TEST_LOC" ]; then
      STATUS="✅"
    else
      STATUS="❌ Missing"
    fi

    echo "| $record | ${PROD_LOC:-Not found} | ${TEST_LOC:-Missing} | $STATUS |" >> plan.md
  done

  echo "" >> plan.md
  echo "Generated: $(date)" >> plan.md
```

**3.3 Display plan.md summary:**

Read and display current status:
```
Total LogRecords: {total}
Tested: {tested}
Missing: {missing}
Completion: {percentage}%
```

**3.4 Store inventory for tracking:**

Parse plan.md table to track progress throughout workflow.

### Step 4: Module-by-Module Analysis

For each module in processing order:

**4.1 Logger Audit:**

```
Task:
  subagent_type: Explore
  model: haiku
  description: Audit logger configuration
  prompt: |
    Identify logging configuration violations in module {module}.

    Search for:
    1. Non-CuiLogger usage:
       - LoggerFactory.getLogger
       - Logger.getLogger
       - @Slf4j annotations

    2. System output usage:
       - System.out.println
       - System.err.println

    3. Log level prefixes:
       - String patterns like "[DEBUG]", "[ERROR]", "[INFO]"

    4. Incorrect logger declaration:
       - Not private static final
       - Wrong name (not LOGGER)
       - Wrong instantiation pattern

    Return structured list of violations with locations.
```

**4.2 LogRecord Audit:**

```
Task:
  subagent_type: Explore
  model: haiku
  description: Audit LogRecord usage
  prompt: |
    Check LogRecord usage compliance in module {module}.

    Apply rules from logging-maintenance-reference.md:
    1. INFO/WARN/ERROR/FATAL MUST use LogRecord
    2. DEBUG/TRACE must NOT use LogRecord
    3. Parameter format must be %s (not {} or %d)
    4. Exception must be first parameter

    Search for violations and return structured findings.
```

**4.3 LogMessages Review:**

```
Task:
  subagent_type: Explore
  model: haiku
  description: Review LogMessages structure
  prompt: |
    Review LogMessages class structure in module {module}.

    Check for:
    1. Module needs LogMessages (≥10 types or ≥10 INFO+ messages)
    2. Correct 4-level DSL hierarchy
    3. ID ranges: INFO (1-99), WARN (100-199), ERROR (200-299), FATAL (300-399)
    4. Duplicate identifiers
    5. @UtilityClass annotations present

    Return findings with specific violations.
```

**4.4 Documentation Check:**

```
Read: {module}/doc/LogMessages.adoc
```

Verify:
- File exists if module has LogMessages class
- Format follows specification
- Content matches implementation
- All INFO/WARN/ERROR/FATAL messages documented

**4.5 Duplicate Detection:**

```
Task:
  subagent_type: Explore
  model: haiku
  description: Detect duplicate log messages
  prompt: |
    Identify duplicate logging patterns in module {module}.

    Look for:
    - Identical message templates
    - Similar messages that could be parameterized
    - Redundant LogRecord declarations
    - Mixed parameter formats ({} vs %s)

    Suggest consolidation opportunities.
```

**4.6 Display Module Analysis Summary:**

```
Module: {module-name}
══════════════════════════════════════

Logger Violations: {count}
- Non-CuiLogger: {count}
- System.out/err: {count}
- Wrong declaration: {count}

LogRecord Violations: {count}
- Missing LogRecord (INFO/WARN/ERROR/FATAL): {count}
- Prohibited LogRecord (DEBUG/TRACE): {count}
- Wrong parameter format: {count}
- Exception order: {count}

LogMessages Issues: {count}
- Structure violations: {count}
- ID range violations: {count}
- Missing documentation: {count}

Duplicates Found: {count}

Total Violations: {total}
```

**Prompt user: "[P]roceed with fixes / [S]kip module / [A]bort"**

### Step 5: Implementation Phase

For each module, apply fixes systematically:

**5.1 Logger Migration:**

For each non-CuiLogger instance:

```
Task:
  subagent_type: java-code-implementer
  description: Migrate logger to CuiLogger
  prompt: |
    Replace logger with CuiLogger in {file}.

    Location: {file}:{line}
    Current: {current_logger_type}

    Apply migration pattern from logging-maintenance-reference.md:
    - Replace with: private static final CuiLogger LOGGER = new CuiLogger({ClassName}.class)
    - Update all log calls if needed
    - Remove old imports
    - Add CuiLogger import

    CRITICAL: Only modify logging code, no other changes.
```

Track in `logger_migrations` counter.

**5.2 LogRecord Implementation:**

For each missing LogRecord:

```
Task:
  subagent_type: java-code-implementer
  description: Add LogRecord usage
  prompt: |
    Convert direct logging to LogRecord in {file}.

    Location: {file}:{line}
    Current: LOGGER.info("Direct message")
    Level: {log_level}

    Steps:
    1. Check if LogMessages class exists, create if needed
    2. Add LogRecord to appropriate level (INFO/WARN/ERROR/FATAL)
    3. Update log call to use LogRecord
    4. Change {} to %s if present

    CRITICAL: Only modify logging code.
```

Track in `logrecord_implementations` counter.

**If non-logging bug discovered:**
- **STOP implementation**
- Document bug details
- Prompt user: "[F]ix bug first (separate commit) / [S]kip / [A]bort"
- Wait for confirmation
- Track in `bugs_found` counter

**5.3 LogMessages Creation/Update:**

If module needs LogMessages class:

```
Task:
  subagent_type: java-code-implementer
  description: Create/update LogMessages class
  prompt: |
    Create/update LogMessages class for module {module}.

    Follow DSL-Style Constants Pattern:
    - 4-level structure
    - @UtilityClass annotations
    - Proper ID ranges
    - %s for all parameters

    Use template from logging-maintenance-reference.md.

    CRITICAL: Only create/modify LogMessages, no other changes.
```

**5.4 Documentation Update:**

```
Task:
  subagent_type: java-code-implementer
  description: Update doc/LogMessages.adoc
  prompt: |
    Create or update doc/LogMessages.adoc for module {module}.

    Include all INFO/WARN/ERROR/FATAL messages.
    Follow standard table format.
    Match implementation exactly.
```

**5.5 Test Implementation - CRITICAL STEP:**

For each LogRecord needing test coverage:

```
Task:
  subagent_type: Explore
  model: haiku
  description: Find business logic test for LogRecord
  prompt: |
    Find the appropriate business logic test for LogRecord {logrecord_name}.

    Steps:
    1. Find where LogRecord is logged in production:
       - Search for {logrecord_name}.format() calls
       - Identify file, class, method

    2. Find corresponding test class:
       - Look for {ClassName}Test.java

    3. Find test method that exercises that code path:
       - Method should test the business logic
       - Should trigger the logging condition

    4. Return:
       - Test file path
       - Test method name
       - Line number where LogAsserts should be added

    CRITICAL: Must be EXISTING business logic test, not new coverage test.
```

Then add LogAsserts:

```
Task:
  subagent_type: java-code-implementer
  description: Add LogAsserts to business logic test
  prompt: |
    Add LogAsserts to EXISTING business logic test.

    Test: {test_file}
    Method: {test_method}
    LogRecord: {logrecord_name}

    Add after existing assertions:
    assertLogMessagePresentContaining(
        TestLogLevel.{LEVEL},
        {LOGRECORD}.resolveIdentifierString());

    CRITICAL:
    - Add to EXISTING test, don't create new test
    - Must be in business logic test, not standalone
    - Add @EnableTestLogger if not present
    - Add required imports

    Return status and verify LogRecord is actually logged in test.
```

Track in `tests_updated` counter.

**If no business logic test exists:**
- Document finding
- Prompt user: "[C]reate business test first / [S]kip LogRecord / [A]bort"
- Track in `tests_missing` counter

### Step 6: Verification Phase

**6.1 Module Build Verification:**

```
Task:
  subagent_type: maven-builder
  description: Verify module after changes
  prompt: |
    Execute Maven build for module {module}.

    Parameters:
    - command: clean test -pl {module}

    All tests must pass.
```

**On test failure:**
- Analyze failure
- If logging-related: fix and retry
- If non-logging: apply bug handling process
- Track in `module_verification_failures` counter

**6.2 LogRecord Coverage Verification:**

For each LogRecord in module, verify:

1. **Production Reference:**
   ```
   Grep: pattern="{LOGRECORD}\.format|{LOGRECORD}::format"
         path={module}/src/main/java
   ```
   - If found: ✅ Referenced in production
   - If not found: ⚠️ **Remove LogRecord** (not used)

2. **Test Reference:**
   ```
   Grep: pattern="LogAsserts.*{LOGRECORD}|{LOGRECORD}.*resolveIdentifierString"
         path={module}/src/test/java
   ```
   - If found: ✅ Tested with LogAsserts
   - If not found: ❌ **Add to business logic test** (return to Step 5.5)

3. **Update plan.md:**
   - Mark LogRecord as ✅ if both references found
   - Update status column in inventory table

**6.3 Update plan.md Status:**

```
Bash: |
  # Update summary statistics
  sed -i '' "s/- Tested with LogAsserts: .*/- Tested with LogAsserts: $TESTED/" plan.md
  sed -i '' "s/- Missing LogAsserts: .*/- Missing LogAsserts: $MISSING/" plan.md

  # Update specific LogRecord status
  sed -i '' "s/| $LOGRECORD .* | ❌ Missing/| $LOGRECORD ... | ✅/" plan.md
```

**6.4 Documentation Validation:**

Verify doc/LogMessages.adoc:
- Exists if required
- All LogRecords documented
- Content accurate

**6.5 Full Build Verification:**

```
Task:
  subagent_type: maven-builder
  description: Final module verification
  prompt: |
    Execute full build for module {module}.

    Parameters:
    - command: -Ppre-commit clean install -pl {module}

    Complete build must pass.
```

**6.6 Module Commit:**

If all verification passes:

```
Bash: git add {module files} plan.md
Bash: git commit -m "$(cat <<'EOF'
refactor(logging): implement logging standards in {module}

Logging improvements:
- Logger migrations: {logger_migrations} completed
- LogRecord implementations: {logrecord_implementations} completed
- Tests updated: {tests_updated} business logic tests
- Documentation: doc/LogMessages.adoc updated

plan.md status: {tested}/{total} LogRecords tested

All tests passing, functionality preserved.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

Track in `modules_completed` counter.

**Proceed to next module.**

### Step 7: Final Verification (All Modules)

After all modules processed:

**7.1 Complete Build:**

```
Task:
  subagent_type: maven-builder
  description: Final build verification all modules
  prompt: |
    Execute complete build across all modules.

    Parameters:
    - command: -Ppre-commit clean install

    Full build must pass.
```

**7.2 Final plan.md Update:**

Update with final statistics and completion timestamp.

**7.3 Generate Final Report:**

Review all plan.md files and generate summary.

### Step 8: Display Summary

```
╔════════════════════════════════════════════════════════════╗
║       Logger Maintenance Summary                           ║
╚════════════════════════════════════════════════════════════╝

Scope: {module or 'all modules'}

Modules Processed: {modules_completed} / {total_modules}

Logger Migrations:
- slf4j replaced: {slf4j_count}
- System.out/err removed: {sysout_count}
- Logger declarations fixed: {declaration_count}
Total: {logger_migrations}

LogRecord Implementations:
- INFO level: {info_count}
- WARN level: {warn_count}
- ERROR level: {error_count}
- FATAL level: {fatal_count}
Total: {logrecord_implementations}

Testing:
- Business tests updated: {tests_updated}
- LogAsserts added: {logasserts_count}
- Business tests missing: {tests_missing}

LogRecord Coverage:
- Total LogRecords: {total_logrecords}
- Tested with LogAsserts: {tested_logrecords}
- Coverage: {coverage_percentage}%

Documentation:
- doc/LogMessages.adoc files created/updated: {doc_count}

Bugs Found: {bugs_found}
- Fixed (with approval): {bugs_fixed}
- Skipped: {bugs_skipped}

Build Status: {SUCCESS/FAILURE}
All Tests: {passing/total}

Time Taken: {elapsed_time}

See plan.md for detailed LogRecord inventory.
```

## STATISTICS TRACKING

Track throughout workflow:
- `pre_verification_failures`: Pre-maintenance build failures
- `modules_completed`: Modules successfully processed
- `modules_skipped`: Modules skipped by user
- `logger_migrations`: Total logger migrations
- `logrecord_implementations`: Total LogRecord implementations added
- `tests_updated`: Business logic tests updated with LogAsserts
- `tests_missing`: LogRecords without business logic tests
- `logasserts_count`: Total LogAsserts added
- `bugs_found`: Non-logging bugs discovered
- `bugs_fixed`: Bugs fixed after user approval
- `bugs_skipped`: Bugs skipped
- `module_verification_failures`: Module verification failures
- `total_logrecords`: Total LogRecords across all modules
- `tested_logrecords`: LogRecords with LogAsserts coverage
- `elapsed_time`: Total execution time

Display all statistics in final summary.

## LogRecord Discovery Script Reference

**Bash script for systematic LogRecord discovery:**

```bash
#!/bin/bash
# Find all LogRecords and verify test coverage

MODULE_PATH="${1:-src}"

echo "=== Finding all LogRecords ==="
grep -r "public static final LogRecord" --include="*LogMessages.java" $MODULE_PATH/main/java | \
  awk '{print $5}' | sort -u

echo ""
echo "=== Checking Production and Test Coverage ==="
for record in $(grep -r "public static final LogRecord" --include="*LogMessages.java" $MODULE_PATH/main/java | awk '{print $5}' | sort -u); do
    echo "LogRecord: $record"

    echo "  Production usage:"
    grep -rn "$record\.format\|$record::format" --include="*.java" $MODULE_PATH/main/java | head -3
    PROD_COUNT=$(grep -r "$record\.format\|$record::format" --include="*.java" $MODULE_PATH/main/java | wc -l)

    echo "  Test coverage (must be in business logic test):"
    grep -rn "LogAsserts.*$record\|$record.*resolveIdentifierString" --include="*Test.java" $MODULE_PATH/test/java | head -3
    TEST_COUNT=$(grep -r "LogAsserts.*$record\|$record.*resolveIdentifierString" --include="*Test.java" $MODULE_PATH/test/java | wc -l)

    if [ $PROD_COUNT -eq 0 ]; then
        echo "  ⚠️  WARNING: LogRecord not used in production - consider removing"
    elif [ $TEST_COUNT -eq 0 ]; then
        echo "  ❌ WARNING: No LogAsserts found - add to business logic test"
    else
        echo "  ✅ OK: Production ($PROD_COUNT) and Test ($TEST_COUNT) coverage"
    fi
    echo ""
done

echo "=== Summary ==="
echo "Update plan.md with findings before proceeding"
```

## CRITICAL RULES SUMMARY

**Production Code:**
- ✅ Modify ONLY logging code
- ✅ Preserve ALL functionality
- ❌ No non-logging changes without user approval

**Testing:**
- ✅ LogAsserts in EXISTING business logic tests
- ✅ Test business logic AND logging together
- ❌ Never create standalone LogRecord coverage tests

**Bug Handling:**
- ✅ Stop and ask user before fixing non-logging bugs
- ✅ Separate commit for bug fixes
- ❌ Never silently fix non-logging bugs

**Coverage Requirements:**
- ✅ Every LogRecord in production code (.format() call)
- ✅ Every LogRecord in business logic test (LogAsserts)
- ❌ Remove LogRecords not referenced anywhere

**Plan Tracking:**
- ✅ Maintain plan.md with inventory table
- ✅ Update status as LogRecords are tested
- ✅ Track completion percentage

## ERROR HANDLING

**Build Failures:**
- Display detailed error information
- Distinguish logging vs non-logging errors
- Apply bug handling protocol for non-logging issues

**Test Failures:**
- Analyze failure cause
- If logging-related: fix and retry
- If business logic: apply bug handling protocol
- Never proceed with failing tests

**Missing Business Logic Tests:**
- Document LogRecords without tests
- Prompt user for guidance
- Cannot add LogAsserts without business test
- Consider creating business test first

**Non-Logging Bugs:**
- STOP immediately
- Document thoroughly
- Ask user for approval
- Separate commit if approved
- Resume logging work after bug fixed

## USAGE EXAMPLES

**Process all modules:**
```
/cui-logger-maintain
```

**Process single module:**
```
/cui-logger-maintain module=auth-service
```

**Generate/regenerate plan:**
```
/cui-logger-maintain create-plan
```

**Process module and regenerate plan:**
```
/cui-logger-maintain module=user-api create-plan
```

## ARCHITECTURE

Orchestrates agents and commands:
- **cui-java-core skill** - Logging standards and maintenance reference
- **Explore agent** - Violation detection and business test location
- **java-code-implementer agent** - Logging code modifications (Layer 3)
- **maven-builder agent** - Build and test verification (Layer 3)
- **Bash** - LogRecord discovery script and plan.md updates

## RELATED

- `cui-java-core` skill - Logging standards and maintenance reference
- `java-code-implementer` agent - Code modifications
- `maven-builder` agent - Build verification
- `/cui-java-refactor` command - Broader code refactoring
- `/cui-log-record-enforcer` command - Automated logging enforcement
