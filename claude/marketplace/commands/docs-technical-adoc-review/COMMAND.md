# Technical AsciiDoc Documentation Review Command

Execute comprehensive technical review of all AsciiDoc documentation using the adoc-review agent for format validation, link verification, and content quality analysis.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** with:
1. Improved directory grouping strategies
2. Better parallel execution patterns
3. Enhanced state management techniques
4. Lessons learned about agent coordination
5. More efficient workflow optimizations

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

- `push` (optional): Automatically commit and push changes after successful execution
  - Usage: `/docs-technical-adoc-review push`
  - When provided, commits all changes with descriptive message and pushes to remote

## WHAT THIS COMMAND DOES

This command orchestrates the `adoc-review` agent across your entire project:

1. **Discovers all directories containing AsciiDoc files** (excluding target/, node_modules/, .git/)
2. **Groups files by directory** for efficient agent execution
3. **Launches adoc-review agents** (can run multiple in parallel for different directories)
4. **Each agent performs**:
   - Format validation (using asciidoc-validator.sh)
   - Link verification (using verify-adoc-links.py)
   - Content quality analysis (correctness, clarity, tone, consistency, completeness)
   - Fixes issues and re-validates
5. **Consolidates results** from all agents
6. **Updates state** in .claude/run-configuration.md
7. **Commits and pushes** (if push parameter provided)

## PRE-CONDITIONS

**Verify before starting (silently unless errors):**

Run all checks in parallel using a single Bash command:
```bash
(test -f ~/.claude/agents/adoc-review.md && \
 test -f ./.claude/skills/cui-documentation/scripts/asciidoc-validator.sh && \
 test -f ./.claude/skills/cui-documentation/scripts/verify-adoc-links.py && \
 find . -name "*.adoc" -type f -not -path "*/target/*" -not -path "*/node_modules/*" -not -path "*/.git/*" | head -1 > /dev/null) && \
echo "✅ All pre-conditions verified" || echo "❌ Pre-condition check failed"
```

**If check fails, run individual checks to identify the problem:**
1. `test -f ~/.claude/agents/adoc-review.md || echo "❌ Agent missing: ~/.claude/agents/adoc-review.md"`
2. `test -f ./.claude/skills/cui-documentation/scripts/asciidoc-validator.sh || echo "❌ Validator missing"`
3. `test -f ./.claude/skills/cui-documentation/scripts/verify-adoc-links.py || echo "❌ Link verifier missing"`
4. `find . -name "*.adoc" -type f -not -path "*/target/*" -not -path "*/node_modules/*" -not -path "*/.git/*" | head -1 || echo "❌ No AsciiDoc files found"`

Display specific error and exit if any pre-condition fails.

## WORKFLOW INSTRUCTIONS

### Step 1: Read Configuration

**1.1: Read .claude/run-configuration.md State**

1. Check if `.claude/run-configuration.md` exists
2. If not, create with initial structure (see template at end)
3. Find `docs-technical-adoc-review` section
4. Extract:
   - **Skipped Files**: Files/directories to exclude
   - **Skipped Directories**: Directories to skip entirely
   - **Acceptable Warnings**: Known acceptable issues
   - **Last Execution**: Previous run metadata

**1.2: Display Execution Plan**

```
╔════════════════════════════════════════════════════════════╗
║     Technical AsciiDoc Documentation Review                ║
╔════════════════════════════════════════════════════════════╝

This command will:
1. Discover all directories with AsciiDoc files
2. Launch adoc-review agent for each directory
3. Agents perform: Format validation + Link verification + Content quality
4. Consolidate results and update state
{if push: 5. Commit and push all changes}

Starting discovery...
╚════════════════════════════════════════════════════════════
```

### Step 2: Discover Directories with AsciiDoc Files

**2.1: Find All AsciiDoc Files**

```bash
find . -name "*.adoc" -type f \
  -not -path "*/target/*" \
  -not -path "*/node_modules/*" \
  -not -path "*/.git/*" | sort
```

**2.2: Extract Unique Directories**

From the file list, extract unique directories that contain .adoc files:

```bash
# For each file path, get its directory
# Example: ./doc/security/Threat-Model.adoc → doc/security/
```

**2.3: Filter Skipped Directories**

Remove directories matching patterns from `.claude/run-configuration.md` Skipped Directories.

**2.4: Group Directories Intelligently**

**Grouping strategy:**

1. **Prefer parent directories when all subdirectories are small** (≤ 5 files each)
   - If `doc/` has subdirs `security/`, `api/`, `guides/` each with 2-3 files
   - → Launch agent once for `doc/` directory

2. **Use subdirectories when parent has many direct files** (> 5 files)
   - If `doc/` has 10 files + subdirs with more files
   - → Launch agent for `doc/` AND each subdir separately

3. **Parallel execution candidates:**
   - Independent module directories (e.g., `oauth-sheriff-core/`, `benchmarking/`)
   - Can launch agents in parallel for these

**Display grouping plan:**
```
Directory Grouping Plan:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sequential Groups (dependencies):
  Group 1: doc/ (15 files, non-recursive)
  Group 2: doc/security/ (5 files, non-recursive)
  Group 3: doc/api/ (3 files, non-recursive)

Parallel Groups (independent):
  Parallel A: oauth-sheriff-core/ (2 files, non-recursive)
  Parallel B: benchmarking/ (4 files, non-recursive)
  Parallel C: oauth-sheriff-quarkus-parent/ (3 files, non-recursive)

Total directories: 6
Total files: 32
Estimated parallel agents: 3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Step 3: Execute adoc-review Agents

**3.1: Launch Sequential Groups First**

For each directory in sequential groups:

```
Launching adoc-review agent for: {directory}
Target: {full_path}
Files: {count} .adoc files
Mode: directory (non-recursive)
```

Use Task tool to launch agent:
```
Task(
  subagent_type="general-purpose",
  description="Review AsciiDoc files in {directory}",
  prompt="Use the adoc-review agent to comprehensively review all AsciiDoc files in directory: {full_path}

  The agent will perform:
  1. Format validation using asciidoc-validator.sh
     - Filter known false positives from output: grep -v 'line [0-9]\+: \[: .*: integer expression expected'
  2. Link verification using verify-adoc-links.py
  3. Content quality analysis (correctness, clarity, tone, consistency, completeness)
  4. Apply fixes and re-validate

  After completion, provide the agent's final report with:
  - Files processed
  - Issues found by category
  - Fixes applied
  - Validation results
  - Tool usage
  - Lessons learned (if any)
  "
)
```

Wait for completion, capture report.

**3.2: Launch Parallel Groups**

For independent directories, launch all agents in parallel:

```
Launching 3 parallel adoc-review agents:
  Agent 1: oauth-sheriff-core/
  Agent 2: benchmarking/
  Agent 3: oauth-sheriff-quarkus-parent/
```

Use multiple Task tool calls in **single message** for parallel execution:
```
Task(...) for directory 1
Task(...) for directory 2
Task(...) for directory 3
```

Wait for all to complete, capture all reports.

**3.3: Track Agent Executions**

For each agent execution, record:
- Directory processed
- Status (success/partial/issues_remain)
- Files processed
- Issues found by category
- Fixes applied
- Validation results
- Duration (if available)
- Lessons learned (if any)

### Step 4: Consolidate Results

**4.1: Aggregate Metrics**

Combine results from all agent executions:

```markdown
## Consolidated Results

### Overall Metrics
- Total directories processed: X
- Total files reviewed: Y
- Total agents launched: Z
- Parallel executions: P

### Issues Found (Total)
- Format compliance: X issues (Y fixed)
- Link validity: A issues (B fixed)
- Correctness: C issues (D fixed)
- Clarity: E issues (F fixed)
- Tone/Style: G issues (H fixed)
- Consistency: I issues (J fixed)
- Completeness: K issues (L fixed)

### Status by Directory
- ✅ {dir1}: SUCCESS - All issues resolved
- ✅ {dir2}: SUCCESS - All issues resolved
- ⚠️ {dir3}: PARTIAL - Minor issues remain
- ❌ {dir4}: ISSUES REMAIN - Needs user review
```

**4.2: Collect Lessons Learned**

From all agent reports, extract any "Lessons Learned" sections:
- Combine insights from all agents
- Identify patterns or recurring issues
- Note new warning types discovered
- Document better approaches found

**4.3: Identify Remaining Issues**

Collect all remaining issues from agents that reported "PARTIAL" or "ISSUES REMAIN":
- List file, line, issue type
- Prioritize by severity
- Group by category

### Step 5: Update State in .claude/run-configuration.md

**5.1: Update Command Section**

Find or create `docs-technical-adoc-review` section in .claude/run-configuration.md:

```markdown
## docs-technical-adoc-review

### Skipped Files

Files excluded from technical AsciiDoc review:

- {any new files user chose to skip during agent executions}

### Skipped Directories

Directories excluded entirely:

- `target/` - Build artifacts
- `node_modules/` - Dependencies
- `.git/` - Git metadata
- {any additional user-specified directories}

### Acceptable Warnings

Warnings approved as acceptable:

- {warning pattern 1}: {reason}
- {warning pattern 2}: {reason}

### Last Execution

- Date: {timestamp}
- Directories processed: {count}
- Files reviewed: {count}
- Issues fixed: {count}
- Status: {SUCCESS|PARTIAL|ISSUES_REMAIN}
- Parallel agents: {count}

### Lessons Learned

{Consolidated lessons learned from all agent executions}
```

**5.2: Write Updated Configuration**

Use Edit tool to update .claude/run-configuration.md with new state.

### Step 6: Generate Final Summary Report

**Display comprehensive final report:**

```
╔════════════════════════════════════════════════════════════╗
║     Technical AsciiDoc Review Complete                     ║
╔════════════════════════════════════════════════════════════╝

Execution Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Directories processed: {count}
Files reviewed: {count}
Agents launched: {count} ({parallel} in parallel)

Overall Status: {✅ SUCCESS | ⚠️ PARTIAL | ❌ ISSUES REMAIN}

Issues Found and Fixed:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Format compliance:    {found} found → {fixed} fixed
Link validity:        {found} found → {fixed} fixed
Correctness:          {found} found → {fixed} fixed
Clarity:              {found} found → {fixed} fixed
Tone/Style:           {found} found → {fixed} fixed
Consistency:          {found} found → {fixed} fixed
Completeness:         {found} found → {fixed} fixed

Status by Directory:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ doc/ - All issues resolved ({count} files)
✅ oauth-sheriff-core/ - All issues resolved ({count} files)
⚠️ benchmarking/ - Minor issues remain ({count} files)

{if lessons learned:}
Lessons Learned:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{consolidated lessons from all agents}

{if remaining issues:}
Remaining Issues Requiring Attention:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. {file}:{line} - {issue description}
2. {file}:{line} - {issue description}
...

Next Steps:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{if push parameter: "✅ Committing and pushing changes..."}
{if remaining issues: "⚠️ Review remaining issues listed above"}
{if lessons: "📝 Lessons learned added to .claude/run-configuration.md"}

╚════════════════════════════════════════════════════════════
```

### Step 7: Commit and Push (if push parameter provided)

**Only execute if `push` parameter was provided:**

1. **Check for changes:**
   ```bash
   git status --porcelain
   ```

2. **If changes exist, create commit:**
   ```bash
   git add -A
   git commit -m "$(cat <<'EOF'
   docs: Technical review and refactoring of AsciiDoc documentation

   Executed comprehensive review using adoc-review agent:
   - Validated format compliance (AsciiDoc standards)
   - Verified all links (cross-references, inter-document, external)
   - Analyzed content quality (correctness, clarity, tone, consistency)

   Processed {X} directories, {Y} files
   Fixed {Z} issues across all categories

   Changes by directory:
   - {dir1}: {changes}
   - {dir2}: {changes}

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   EOF
   )"
   ```

3. **Push to remote:**
   ```bash
   git push
   ```

4. **Verify and display confirmation:**
   ```
   ✅ Changes committed and pushed successfully

   Commit: {commit_hash}
   Files changed: {count}
   ```

## CRITICAL RULES

### Agent Coordination

- **NEVER run agents on overlapping directories** - Ensure directory assignments are mutually exclusive
- **ALWAYS wait for sequential groups to complete** - Dependencies must be respected
- **ALWAYS use single message for parallel agents** - Multiple Task calls in ONE message for true parallelism
- **NEVER modify agent results** - Trust agent reports, consolidate them as-is
- **ALWAYS capture agent reports completely** - All metrics, findings, lessons learned

### Efficiency

- **PREFER directory-level execution** over file-by-file when possible
- **MAXIMIZE parallel execution** - Launch independent directory agents concurrently
- **GROUP intelligently** - Combine small subdirectories under parent when sensible
- **AVOID redundant validation** - Don't re-run validation yourself, trust agents

### State Management

- **ALWAYS update .claude/run-configuration.md** - Persist all state after execution
- **NEVER lose lessons learned** - Consolidate from all agents into command state
- **TRACK user decisions** - Skipped files, acceptable warnings, etc.
- **PRESERVE historical data** - Keep last execution metadata

### Error Handling

- **IF pre-condition fails** - Display clear error, exit immediately
- **IF agent fails** - Capture error, continue with other agents, report at end
- **IF no files found** - Display informative message, exit gracefully
- **IF push fails** - Display error, leave changes uncommitted for user review

### Quality Assurance

- **VERIFY consolidation accuracy** - Metrics must add up correctly
- **CHECK for duplicates** - Don't count same issue twice from multiple agents
- **VALIDATE directory coverage** - Ensure no .adoc files were missed
- **CONFIRM state persistence** - .claude/run-configuration.md must be updated successfully

## .claude/run-configuration.md TEMPLATE

```markdown
# Command Configuration

## docs-technical-adoc-review

### Skipped Files

Files excluded from technical AsciiDoc review:

(Empty initially - populated by user decisions during execution)

### Skipped Directories

Directories excluded entirely:

- `target/` - Build artifacts (auto-generated)
- `node_modules/` - Dependencies
- `.git/` - Git metadata

### Acceptable Warnings

Warnings approved as acceptable:

(Empty initially - populated by user decisions during agent executions)

### Last Execution

- Date: Never
- Directories processed: 0
- Files reviewed: 0
- Issues fixed: 0
- Status: NOT_RUN
- Parallel agents: 0

### Lessons Learned

(Populated during executions)
```

## USAGE EXAMPLES

### Review All Documentation
```
/docs-technical-adoc-review
```

### Review and Auto-Commit
```
/docs-technical-adoc-review push
```

## IMPORTANT NOTES

1. **Agent autonomy**: The adoc-review agent is fully autonomous - it handles all validation, fixing, and reporting. This command only orchestrates multiple agent instances.

2. **Parallel execution**: Independent module directories can be processed in parallel, significantly reducing overall execution time for large projects.

3. **Non-recursive agents**: Each agent processes one directory non-recursively, so this command must handle subdirectory iteration.

4. **Comprehensive coverage**: Every aspect is covered - format, links, AND content quality in a single execution.

5. **No JavaDoc**: This command is AsciiDoc-only. JavaDoc review is out of scope.

6. **State accumulation**: The command learns over time - acceptable warnings and skipped files accumulate in .claude/run-configuration.md.

7. **Trust the agents**: Don't second-guess or re-validate agent work. Consolidate and report their findings.

8. **Lessons learned flow**: Agents report lessons → Command consolidates → Stored in .claude/run-configuration.md → Available for future improvements

## EXPECTED DURATION

Based on typical projects:

- **Small project** (≤ 20 files, 2-3 directories): 10-15 minutes
- **Medium project** (20-50 files, 4-6 directories): 20-30 minutes
- **Large project** (50+ files, 7+ directories): 30-60 minutes

Parallel execution can reduce duration by 30-50% for projects with multiple independent modules.
