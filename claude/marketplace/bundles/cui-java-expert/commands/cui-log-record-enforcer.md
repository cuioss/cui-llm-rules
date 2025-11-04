---
name: cui-log-record-enforcer
description: Enforce CUI logging standards by validating LogRecord usage, testing coverage, and identifier organization
---

# Log Record Enforcer Command

Comprehensive diagnostic and automation command that enforces CUI logging standards across Java modules. Validates that INFO/WARN/ERROR/FATAL use LogRecord, DEBUG/TRACE use direct logger, all LogRecords are tested with LogAssert, and identifiers are properly organized.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/cui-update-command command-name=cui-log-record-enforcer update="[your improvement]"` with:
1. Better violation detection patterns for logging statements
2. More efficient LogRecord usage analysis techniques
3. Improved LogAssert verification strategies
4. Enhanced identifier renumbering algorithms
5. Any lessons learned about logging standards enforcement workflows

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

**module** - (Optional) Module name for multi-module projects; if unset, assume single-module and verify

## WORKFLOW

### Step 1: Verify Module Parameter

**Determine project structure:**

1. Check if `.claude/run-configuration.md` exists
2. If exists, search for multi-module indicators (e.g., multiple module sections)
3. If parameter unset:
   - Single-module: Proceed with entire project
   - Multi-module: List available modules and ask user which to analyze

**Module validation:**
- If module parameter provided, verify it exists using Grep in pom.xml files
- If module not found, report error and stop
- Store validated module name for subsequent steps

### Step 2: Verify Build Precondition

Execute build verification (see Build Verification Protocol in CRITICAL RULES).

If build fails, report to caller and stop execution.

### Step 3: Load Configuration and Logging Standards

**Read configuration:**
1. Read `.claude/run-configuration.md` for module-specific paths
2. Look for section matching command key: `cui-log-record-enforcer`
3. Extract LogMessages class locations for each module
4. Extract LogMessages.adoc locations for each module

**Load logging standards:**
```
Skill: cui-java-expert:cui-java-core
```

This loads:
- `standards/logging-standards.md` - LogRecord usage rules
- `standards/logmessages-documentation.md` - Documentation requirements

**Configuration structure:**
```markdown
## cui-log-record-enforcer

### Module: [module-name]

#### LogMessages Classes
- Package: com.example.auth → Class: AuthenticationLogMessages
- Package: com.example.token → Class: TokenLogMessages

#### LogMessages Documentation
- doc/LogMessages.adoc
```

**If configuration missing or incomplete:**
- Attempt to locate LogMessages classes using Glob: `**/*LogMessages.java`
- Attempt to locate LogMessages.adoc using Glob: `**/LogMessages.adoc`
- If still uncertain (confidence < 100%), ask user for help
- Store results in configuration for future runs

### Step 4: Find and Analyze Logging Violations

**Find and analyze all logging statements:**

Use Grep to locate all logger invocations:
```
Grep: pattern="LOGGER\.(info|debug|trace|warn|error|fatal)\(" output_mode="content" -n=true
```

**Apply violation detection patterns:**

Follow violation detection patterns from cui-java-core skill:
- Extract context (file, line, level, statement)
- Determine LogRecord usage (LogRecord vs direct string)
- Apply validation rules (see CRITICAL RULES section)
- Record violations with location and type

See: `standards/logging-enforcement-patterns.md` → Patterns 1-5 (Violation Detection)

### Step 5: Verify LogRecord Usage and Test Coverage

**Analyze LogRecord coverage:**

For each LogMessages class, apply coverage analysis patterns from cui-java-core skill:
- Extract all LogRecord definitions (Pattern 6)
- Find production usage with Grep (Pattern 7)
- Find test coverage with LogAssert (Pattern 8)
- Determine coverage status (Pattern 9)

**Coverage Actions:**
- No references → Remove (unused)
- Production only → Add tests
- Test only → USER REVIEW (critical bug)
- Both → Compliant

See: `standards/logging-enforcement-patterns.md` → Patterns 6-9 (Coverage Analysis)

### Step 6: Generate Execution Plan

**Aggregate findings:**

1. **Group violations by type:**
   - Missing LogRecord (INFO/WARN/ERROR/FATAL using direct string)
   - Prohibited LogRecord (DEBUG/TRACE using LogRecord)

2. **Group LogRecord issues:**
   - Unused LogRecords (no references)
   - Untested LogRecords (production only)
   - Test-only LogRecords (critical bugs)

3. **Create batched work plan:**
   - Batch 1: Fix logging statement violations (java-code-implementer)
   - Batch 2: Remove unused LogRecords (java-code-implementer)
   - Batch 3: Add missing LogAsserts (java-junit-implementer)
   - Batch 4: User review for test-only LogRecords

**Plan format:**
```
ENFORCEMENT PLAN
================

Total Violations: {count}
Total LogRecord Issues: {count}

Batch 1: Fix Logging Statements
- {count} missing LogRecord conversions
- {count} prohibited LogRecord removals
- Agent: java-code-implementer

Batch 2: Remove Unused LogRecords
- {count} unused LogRecord definitions
- Agent: java-code-implementer

Batch 3: Add Test Coverage
- {count} untested LogRecords
- Agent: java-junit-implementer

Batch 4: User Review Required
- {count} test-only LogRecords (critical)
```

### Step 7: Execute Corrections

**Execute batches using agent coordination patterns:**

Follow batch execution templates from cui-java-core skill (Pattern 11).

**Batch 1:** Fix logging violations using java-code-implementer
- Pass violations list with file locations and required corrections
- Verify compilation

**Batch 2:** Remove unused LogRecords using java-code-implementer
- Pass list of unused LogRecords with locations
- Verify compilation

**Batch 3:** Add LogAssert tests using java-junit-implementer
- Pass untested LogRecords with production usage locations
- Use @EnableTestLogger and LogAsserts
- Verify tests pass

**Batch 4:** User review for test-only LogRecords
- Report test-only LogRecords as critical bugs
- Stop execution and await user guidance
- Options: Add production code or remove tests

See: `standards/logging-enforcement-patterns.md` → Pattern 11 (Batch Templates)

### Step 8: Verify Corrections

Execute build verification (see Build Verification Protocol in CRITICAL RULES).

If verification fails, report details and stop execution.

### Step 9: Review and Renumber LogMessages Identifiers

**Apply identifier numbering validation:**

For each LogMessages class:
1. Extract all identifiers with levels
2. Check for gaps, ordering issues, and range compliance
3. Apply renumbering if needed using java-code-implementer
4. Verify no DEBUG/TRACE LogRecords exist

**Standard ranges** (from logging-standards.md):
- INFO: 001-099, WARN: 100-199, ERROR: 200-299, FATAL: 300-399

See: `logging-standards.md` → Message Identifier Ranges
See: `logging-enforcement-patterns.md` → Patterns 13-14 (Identifier Validation)

### Step 10: Final Verification and Report

Execute final build verification (see Build Verification Protocol in CRITICAL RULES).

**Generate summary report:**

```
═══════════════════════════════════════════════════════════════
LOG RECORD ENFORCEMENT COMPLETE
═══════════════════════════════════════════════════════════════

Module: {module-name or "all modules"}

VIOLATIONS FIXED:
- Logging statements corrected: {count}
  • Missing LogRecord (INFO/WARN/ERROR/FATAL): {count}
  • Prohibited LogRecord (DEBUG/TRACE): {count}

LOGRECORD MAINTENANCE:
- Unused LogRecords removed: {count}
- LogAssert tests added: {count}
- Identifiers renumbered: {count}

IDENTIFIER VERIFICATION:
✓ INFO level (001-099): {count} messages, consecutive ordering
✓ WARN level (100-199): {count} messages, consecutive ordering
✓ ERROR level (200-299): {count} messages, consecutive ordering
✓ FATAL level (300-399): {count} messages, consecutive ordering
✓ No DEBUG/TRACE LogRecords found

BUILD STATUS: {SUCCESS/FAILURE}

{If failures: List remaining errors or warnings}

COMPLIANCE STATUS: {COMPLIANT / ISSUES REMAINING}

═══════════════════════════════════════════════════════════════
```

## CRITICAL RULES

**Module Handling:**
- ALWAYS verify module parameter for multi-module projects
- Ask user if module unset and project is multi-module
- Use module parameter in all maven-builder agent calls

**Build Verification Protocol:**
- Execute at Steps 2, 8, and 10
- Use maven-builder agent with `clean verify` command
- Parameters: command=clean verify, outputMode=DEFAULT, module={if specified}
- Success criteria: Exit code 0, zero errors, zero test failures
- On failure: Report details (errors, test failures) and stop execution
- See: `logging-enforcement-patterns.md` → Pattern 15

**Configuration Management:**
- Read `.claude/run-configuration.md` for module-specific paths
- Store LogMessages class and documentation locations
- Ask user for help if locations uncertain (< 100% confidence)
- Update configuration for future executions

**Violation Detection:**
- Use Grep with line numbers (`-n=true`) for all searches
- Search for: `LOGGER\.(info|debug|trace|warn|error|fatal)\(`
- Analyze each match to determine LogRecord usage
- Record file, line, level, and violation type

**LogRecord Validation Rules:**
- INFO/WARN/ERROR/FATAL: LogRecord REQUIRED → violation if missing
- DEBUG/TRACE: Direct string REQUIRED → violation if LogRecord present
- Every LogRecord MUST have production usage
- Every LogRecord MUST have test coverage (LogAssert)

**Coverage Analysis:**
- No references → Remove LogRecord (unused)
- Production only → Add LogAssert test
- Test only → USER REVIEW REQUIRED (critical bug)
- Both references → Compliant

**Agent Coordination:**
- Use java-code-implementer for production code changes
- Use java-junit-implementer for LogAssert test implementation
- Use maven-builder for all build verifications
- Execute agents in batches (grouped by change type)

**Identifier Management:**
- Standard ranges (from logging-standards.md): INFO 001-099, WARN 100-199, ERROR 200-299, FATAL 300-399
- NO identifiers for DEBUG/TRACE (prohibited)
- Renumber to eliminate gaps and ensure consecutive ordering

**Documentation Synchronization:**
- Update LogMessages.adoc when identifiers change
- Verify documentation matches implementation
- Include documentation updates in same batch as code changes

**User Interaction:**
- Ask for module selection if multi-module and parameter unset
- Ask for help if LogMessages locations uncertain
- Stop and request guidance if test-only LogRecords found
- Report all failures immediately (don't continue with broken code)

## USAGE EXAMPLES

**Single-module project:**
```
/cui-log-record-enforcer
```

**Multi-module project, specific module:**
```
/cui-log-record-enforcer module=oauth-sheriff-core
```

**Multi-module project, all modules:**
```
/cui-log-record-enforcer
(will ask which module to analyze)
```

## RELATED

- Skill: `cui-java-expert:cui-java-core` - Logging standards and enforcement patterns
- Standards: `logging-standards.md`, `logmessages-documentation.md`, `logging-enforcement-patterns.md`
- Agent: `cui-java-expert:java-code-implementer` - Fix production code
- Agent: `cui-java-expert:java-junit-implementer` - Add tests
- Agent: `cui-maven:maven-builder` - Build verification
