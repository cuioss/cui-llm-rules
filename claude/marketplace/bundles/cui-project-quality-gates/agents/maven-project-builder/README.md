# Project Builder Agent

Executes comprehensive Maven builds with pre-commit verification, analyzes all output, fixes every issue found, and tracks execution time.

## Purpose

This agent automates the complete build verification process by:
- Executing Maven builds with pre-commit profile
- Analyzing compilation errors, test failures, and warnings
- Fixing JavaDoc warnings according to CUI standards
- Handling OpenRewrite TODO markers automatically
- Managing acceptable warnings configuration
- Tracking build execution time for timeout optimization
- Ensuring zero warnings before accepting build

## Usage

```bash
# Verify build after code changes
"I've finished implementing the new token validation logic"

# Run full build with quality checks
"Can you run the full build?"

# Ensure compilation succeeds
"I want to make sure everything compiles after my changes"
```

## Skills Used

This agent leverages:
- **cui-javadoc**: JavaDoc documentation standards
  - Provides: Package/class/method/field documentation requirements, mandatory fix rules
  - Loads: javadoc-standards.adoc, javadoc-maintenance.adoc
  - When used: At workflow start to guide JavaDoc warning fixes

## How It Works

1. **Activate Skills**: Loads cui-javadoc standards for JavaDoc enforcement
2. **Read Configuration**: Loads execution duration and acceptable warnings from `.claude/run-configuration.md`
3. **Execute Maven Build**: Runs `./mvnw -Ppre-commit clean install` with calculated timeout
4. **Analyze Output**: Identifies compilation errors, test failures, code warnings, JavaDoc warnings
5. **Handle OpenRewrite Markers**: Searches source files for TODO markers, auto-suppresses known patterns
6. **Fix Issues**: Addresses all errors and warnings, iterating until clean build
7. **Update Duration**: Records execution time if changed by >10%
8. **Report**: Returns comprehensive summary with metrics

## OpenRewrite Marker Handling

The agent automatically handles OpenRewrite TODO markers embedded in source code:

**Auto-Suppressed Patterns**:
- LogRecord pattern warnings: `// cui-rewrite:disable CuiLogRecordPatternRecipe`
- Exception usage warnings: `// cui-rewrite:disable InvalidExceptionUsageRecipe`

**User-Approved Patterns**:
- All other marker types prompt for user decision

**Verification**:
- Re-runs build after marker fixes to verify removal
- Fails after 3 iterations if markers persist

## JavaDoc Standards

**CRITICAL**: JavaDoc warnings are NEVER optional.

- Every public/protected class, method, field must be documented
- Missing JavaDoc → mandatory fix
- Malformed tags → mandatory fix
- Invalid references → mandatory fix
- Uses cui-javadoc skill for authoritative standards

## Critical Rules

- **Build must complete** - never cancel, always wait for timeout
- **Timeout = last_duration * 1.25** - 25% safety margin
- **Iterate after changes** - re-run build after every fix
- **OpenRewrite markers mandatory** - always search after each build
- **JavaDoc warnings non-negotiable** - always fix, never ignore
- **Default is to fix** - only ask about ignoring non-critical infrastructure warnings

## Configuration File

The agent maintains `.claude/run-configuration.md`:

```markdown
# Command Configuration

## ./mvnw -Ppre-commit clean install

### Last Execution Duration
- **Duration**: 120000ms (2 minutes)
- **Last Updated**: 2025-10-18

### Acceptable Warnings
- `[WARNING] Using platform encoding (UTF-8 actually) to copy filtered resources`
- `[WARNING] Parameter 'session' is deprecated`
```

## Examples

### Example 1: Clean Build

```
User: "I've finished implementing the new token validation logic"

Agent:
- Activates cui-javadoc skill
- Reads configuration (last duration: 120000ms)
- Executes build with 150000ms timeout (1.25x)
- Build succeeds in 115000ms
- No errors or warnings found
- Searches for OpenRewrite markers → none found
- Duration change <10% → no update needed
- Returns: "Build Status: ✅ SUCCESS"
```

### Example 2: JavaDoc Warnings

```
User: "Can you run the full build?"

Agent:
- Activates cui-javadoc skill
- Executes build
- Finds 5 JavaDoc warnings:
  - Missing package-info.java in 2 packages
  - Missing @param tag in 3 methods
- Fixes all JavaDoc warnings using cui-javadoc standards
- Re-runs build → clean
- Returns: "JavaDoc warnings: 5 (all fixed)"
```

### Example 3: OpenRewrite Markers

```
User: "Verify the build passes"

Agent:
- Executes build → SUCCESS
- Searches for OpenRewrite markers
- Finds 8 LogRecord pattern markers in 4 files
- Auto-suppresses all (adds cui-rewrite:disable comments)
- Removes TODO markers
- Re-runs build → markers gone
- Returns: "OpenRewrite markers: 8 (all suppressed)"
```

### Example 4: Multiple Iterations

```
User: "I want to make sure everything compiles"

Agent:
- Iteration 1: Build fails with 2 compilation errors
  - Fixes both errors
- Iteration 2: Build succeeds with 3 warnings
  - Fixes 2 code warnings, prompts for 1 infrastructure warning
  - User: "ignore that one"
  - Adds to acceptable warnings
- Iteration 3: Searches OpenRewrite markers → 4 found
  - Auto-suppresses all
- Iteration 4: Clean build
- Total: 4 iterations, 2 errors fixed, 2 warnings fixed, 1 warning accepted, 4 markers suppressed
```

## Notes

- Agent uses Bash tool with built-in timeout parameter (cross-platform)
- Execution time tracking optimizes future timeouts
- OpenRewrite markers are in source files, not Maven console output
- Default action is to fix, not ignore
- Tracks comprehensive metrics for reporting
- Reports lessons learned for continuous improvement

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
