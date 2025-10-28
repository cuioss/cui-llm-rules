# Sonar Issue Handler Agent

Processes Sonar code quality issues on GitHub pull requests by fixing code issues, suppressing false positives, and improving code coverage by adding tests.

## Purpose

This agent automates the handling of Sonar/SonarCloud quality issues on pull requests by:
- Retrieving all unresolved Sonar issues from a PR
- Analyzing each issue to determine if it's a real problem or false positive
- Fixing code for valid issues
- Suppressing false positives (with user approval or automatic patterns)
- Identifying code coverage gaps
- Generating tests for uncovered code (when feasible and sensible)
- Verifying builds pass after changes
- Committing changes systematically
- Tracking all metrics and providing comprehensive reports

## Usage

```bash
# Handle Sonar issues by PR number
"Handle the Sonar issues on PR #151"

# Handle Sonar issues by URL
"Process Sonar feedback for https://github.com/owner/repo/pull/123"

# Handle and auto-push changes
"Handle Sonar issues on PR #42 and push"
```

## Parameters

- **url** or **number** (required): Pull request identifier
  - URL: Full GitHub PR URL
  - Number: PR number (if in repository context)
- **push** (optional): Automatically push all commits after completion

## Skills Used

This agent leverages:
- **cui-java-unit-testing**: Java unit testing standards and patterns
  - Provides: JUnit 5 patterns, CUI test generator framework, assertion standards, quality requirements
  - Loads: testing-junit-core.md, testing-generators.md, testing-value-objects.md, integration-testing.md
  - When used: When generating tests for coverage gaps

## How It Works

1. **Read Configuration**: Loads Sonar build timeout from `.claude/run-configuration.md` or uses default
2. **Validate PR**: Verifies pull request exists and is accessible
3. **Check Build Status**: Waits for Sonar build to complete (with timeout handling)
4. **Retrieve Sonar Issues**: Fetches all unresolved issues via MCP or API
5. **Retrieve Coverage Data**: Identifies uncovered lines in changed files
6. **Process Each Issue**:
   - Reads affected file and context
   - Determines if issue is real or false positive
   - **If real**: Fixes code, verifies build, commits
   - **If false positive**: Auto-suppresses known patterns or prompts user for approval
7. **Improve Coverage**: Generates tests for uncovered code (when feasible and sensible)
8. **Commit Suppressions**: Batches suppression changes into single commit
9. **Push Changes**: If requested, pushes all commits to remote
10. **Report**: Returns comprehensive summary with detailed metrics

## Resolution Strategies

**Strategy A - Fix the Code**:
- Issue represents a real bug or code smell
- Uses Edit tool to apply fix
- Runs project-builder to verify build passes
- Commits fix immediately with descriptive message
- Tracks as "fixed"

**Strategy B - Suppress as False Positive**:
- Issue not applicable or would violate standards
- **Auto-suppression** for known patterns (e.g., S2589 + @NonNull)
- **User-approved suppression** with full context and reasoning
- Batches suppressions into single commit at end
- Tracks as "suppressed"

## Test Generation

**When coverage gaps are identified:**

1. **Analyzes uncovered code**:
   - Identifies methods containing uncovered lines
   - Evaluates complexity, dependencies, visibility

2. **Determines feasibility** (can write meaningful test):
   - ✅ Simple methods with clear inputs/outputs
   - ✅ Pure functions, mockable dependencies
   - ❌ Complex async, unmockable statics, UI code

3. **Determines sensibility** (worth testing):
   - ✅ Public APIs, business logic, error handling
   - ❌ Trivial getters/setters, generated code, deprecated methods

4. **Generates tests** (if both feasible AND sensible):
   - Activates cui-java-unit-testing skill
   - Follows CUI test standards:
     - JUnit 5 framework
     - CUI test generators (NEVER Random/Faker)
     - AAA pattern (Arrange-Act-Assert)
     - Meaningful assertion messages
     - Parameterized tests for 3+ variants
     - NO Mockito, NO Hamcrest
   - Creates or updates test files
   - Verifies tests pass
   - Commits test additions

5. **Skips tests** (if not feasible or not sensible):
   - Logs reason for skipping
   - Tracks in metrics

## Known Auto-Suppress Patterns

**S2589 + @NonNull Annotation**:
- Automatically suppresses without user prompt
- Applies to null checks on @NonNull parameters
- Rationale: @NonNull is compile-time only, runtime validation required
- Adds explanatory comment with suppression

## Critical Rules

- **Every issue must be handled** (fixed OR suppressed - zero remaining)
- **Build must pass before committing** code fixes
- **User approval required** for suppressions (except known patterns)
- **Separate commits**: Code fixes individual, suppressions batched
- **Wait for Sonar build** with configurable timeout
- **Stop if non-Sonar builds failing** (fix builds first)
- **Generate tests following CUI standards** (cui-java-unit-testing skill)
- **Only generate meaningful tests** (feasible AND sensible)
- **Commit via agent** (uses commit-current-changes, not direct git)
- **Push only at end** (if requested via parameter)

## Examples

### Example 1: Handle Issues on PR

```
User: "Handle the Sonar issues on PR #151"

Agent:
- Validates PR #151
- Waits for Sonar build to complete
- Finds 8 Sonar issues
- Issue 1: Null pointer - Fixes code
  - Runs build → Passes
  - Commits fix
- Issue 2: S2589 + @NonNull - Auto-suppresses
- Issue 3: Unused variable - Prompts user
  - User: "suppress"
  - Batches for later commit
- Issues 4-8: Fixes and commits each
- Identifies 3 files with coverage gaps
- Generates 5 tests for uncovered methods
- Skips 2 trivial getters
- Commits test additions
- Commits suppressions batch
- Total: 6 fixed, 2 suppressed, 5 tests added
- 8 commits created
```

### Example 2: Handle and Push

```
User: "Process Sonar feedback for https://github.com/cuioss/cui-http/pull/42 and push"

Agent:
- Processes all Sonar issues
- Fixes 4 code issues (4 commits)
- Suppresses 2 false positives (1 commit)
- Adds 7 tests for coverage gaps (1 commit)
- Pushes all 6 commits to remote
- Returns summary with commit SHAs
```

## Notes

- Agent invokes `project-builder` to verify code changes don't break build
- Agent invokes `commit-current-changes` for all commits
- Agent invokes `cui-java-unit-testing` skill when generating tests
- Handles multiple Sonar API access methods (MCP, gh API)
- Configurable timeout for Sonar build waiting
- Tracks comprehensive metrics for reporting
- Includes lessons learned reporting for continuous improvement
- Auto-suppresses known false positive patterns (reduces user prompts)
- Code fixes committed immediately after verification (faster feedback)
- Suppressions and tests batched (more efficient)
- Test generation follows strict CUI standards (no Mockito, use generators, etc.)

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
