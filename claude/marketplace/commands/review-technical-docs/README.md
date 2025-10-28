# review-technical-docs

Orchestrates comprehensive technical review of all AsciiDoc documentation across your project using parallel agent execution for efficiency.

## Purpose

Coordinates the `asciidoc-reviewer` agent across multiple directories, performing format validation, link verification, and content quality analysis on all AsciiDoc files in your project with intelligent parallel execution.

## Usage

```bash
# Review all documentation
/review-technical-docs

# Review and auto-commit
/review-technical-docs push
```

## What It Does

The command performs comprehensive orchestration:

1. **Discovers all directories containing AsciiDoc files** (excluding build artifacts and dependencies)
2. **Groups files by directory** using intelligent grouping strategies
3. **Launches asciidoc-reviewer agents** in parallel for independent directories
4. **Each agent performs**:
   - Format validation using asciidoc-validator.sh
   - Link verification using verify-adoc-links.py
   - Content quality analysis (correctness, clarity, tone, consistency, completeness)
   - Fixes issues and re-validates
5. **Consolidates results** from all agent executions
6. **Updates state** in .claude/run-configuration.md
7. **Commits and pushes** (if push parameter provided)

## Key Features

- **Intelligent Grouping**: Combines small subdirectories under parent when sensible
- **Parallel Execution**: Launches multiple agents concurrently for independent directories (30-50% time reduction)
- **State Persistence**: Tracks skipped files, acceptable warnings, and lessons learned in .claude/run-configuration.md
- **Comprehensive Coverage**: Format validation + link verification + content quality in single execution
- **Agent Autonomy**: Each agent independently handles its directory without coordination overhead
- **Continuous Improvement**: Accumulates lessons learned from each execution

## Parameters

- **push** (optional): Auto-commit and push changes after successful execution
  - Usage: `/review-technical-docs push`
  - Creates descriptive commit message with summary of all changes

## Pre-Conditions

The command verifies before execution:
- `~/.claude/agents/asciidoc-reviewer.md` exists
- `./.claude/skills/cui-documentation/scripts/asciidoc-validator.sh` exists
- `./.claude/skills/cui-documentation/scripts/verify-adoc-links.py` exists
- At least one .adoc file exists in project

If any pre-condition fails, displays specific error and exits.

## Directory Grouping Strategy

1. **Prefer parent directories** when all subdirectories are small (≤ 5 files each)
   - Launches single agent for parent directory

2. **Use subdirectories** when parent has many direct files (> 5 files)
   - Launches separate agents for parent and each subdir

3. **Parallel execution** for independent module directories
   - Identifies non-overlapping directories
   - Launches all agents in single message for true parallelism

## Workflow Overview

1. Read state from `.claude/run-configuration.md`
2. Discover all AsciiDoc files and extract unique directories
3. Filter skipped directories
4. Group directories intelligently (sequential vs parallel)
5. Launch agents:
   - Sequential groups first (dependencies)
   - Parallel groups concurrently (independent)
6. Consolidate all agent reports
7. Update state with results and lessons learned
8. Generate final summary report
9. Commit and push (if requested)

## State Management

The command maintains state in `.claude/run-configuration.md`:

### Skipped Files
Files user chose to exclude during execution

### Skipped Directories
Directories excluded entirely (target/, node_modules/, .git/, etc.)

### Acceptable Warnings
Warnings approved as acceptable with rationale

### Last Execution
- Date
- Directories processed
- Files reviewed
- Issues fixed
- Status (SUCCESS/PARTIAL/ISSUES_REMAIN)
- Parallel agents count

### Lessons Learned
Consolidated insights from all agent executions

## Expected Duration

- **Small project** (≤ 20 files, 2-3 directories): 10-15 minutes
- **Medium project** (20-50 files, 4-6 directories): 20-30 minutes
- **Large project** (50+ files, 7+ directories): 30-60 minutes

Parallel execution can reduce duration by 30-50%.

## Integration

Use this command:
- As part of documentation quality gates
- Before creating documentation pull requests
- Periodically to maintain documentation quality
- After significant documentation changes

Often used with:
- `/commit-changes` - Commit documentation improvements
- `/handle-pull-request` - Create PR with reviewed documentation

## Example Output

```
╔════════════════════════════════════════════════════════════╗
║     Technical AsciiDoc Review Complete                     ║
╔════════════════════════════════════════════════════════════╝

Execution Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Directories processed: 6
Files reviewed: 32
Agents launched: 4 (3 in parallel)

Overall Status: ✅ SUCCESS

Issues Found and Fixed:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Format compliance:    12 found → 12 fixed
Link validity:        5 found → 5 fixed
Correctness:          3 found → 3 fixed
Clarity:              8 found → 8 fixed
Tone/Style:           2 found → 2 fixed
Consistency:          4 found → 4 fixed
Completeness:         1 found → 1 fixed
```

## Notes

- **Agent Autonomy**: The asciidoc-reviewer agent is fully autonomous - this command only orchestrates
- **Non-Recursive**: Each agent processes one directory non-recursively
- **Trust Agents**: Don't second-guess agent results - consolidate and report
- **AsciiDoc Only**: JavaDoc review is out of scope
- **State Accumulation**: Learns over time through .claude/run-configuration.md

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
