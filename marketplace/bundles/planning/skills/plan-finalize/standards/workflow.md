# Plan Finalize Workflow

## Phase Overview

The finalize phase completes the work:

```
Verified Implementation from Verify Phase
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ FINALIZE PHASE                                      │
│                                                     │
│   1. Final commit(s) per strategy                   │
│   2. Create/update pull request                     │
│   3. PR workflow (Sonar fixes, reviews)             │
│   4. Mark plan as complete                          │
│   5. Archive plan results                           │
└─────────────────────────────────────────────────────┘
        │
        ▼
    Plan Complete
```

## Standard Tasks

| Task | Goal | Key Outputs |
|------|------|-------------|
| Commit Changes | Final commit(s) per strategy | Commits pushed |
| Create PR | PR with summary | PR URL, linked issue |
| PR Workflow | Handle automation | Sonar fixed, reviews requested |

## Finalizing Modes

### pr-workflow (Full Automation)

```
1. Commit all changes
2. Push to remote
3. Create PR with summary
4. Link to issue
5. Run /pr-doctor for:
   - Sonar fixes
   - Review request
   - CI monitoring
6. Report completion
```

### manual-pr (PR Only)

```
1. Commit all changes
2. Push to remote
3. Create PR with summary
4. Link to issue
5. Report "manual follow-up required"
```

### commit-only (No PR)

```
1. Commit all changes
2. Push to remote (optional)
3. Report commit status
4. No PR created
```

## Commit Strategy Handling

| Strategy | Finalize Action |
|----------|-----------------|
| fine-granular | Verify commits exist, no additional commit |
| phase-specific | Single commit for all phase changes |
| complete | Single commit for all work |

**Important**: Only implementation code is committed (source files, tests, docs). Plan files (plan storage directory) are NOT committed - they are excluded by `.gitignore` and are session working documents.

## PR Description Template

```markdown
## Summary

{Brief description from plan}

**Related Issue**: {issue-link}

## Changes

{List of key changes from implement phase tasks}

## Testing

{Summary of verification from verify phase}

- Build: ✅ Passed
- Tests: {count} passed
- Coverage: {percentage}%
- Quality: No critical issues

## Checklist

- [x] Code follows standards
- [x] Tests added/updated
- [x] Documentation updated
- [x] No breaking changes (or documented)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Completion Report Template

```markdown
## Plan Complete

### Summary

**Task**: {task-title}
**Duration**: {start-date} to {end-date}
**Status**: ✅ Complete

### Phase Summary

| Phase | Tasks | Status |
|-------|-------|--------|
| init | {count} | ✅ Complete |
| refine | {count} | ✅ Complete |
| implement | {count} | ✅ Complete |
| verify | {count} | ✅ Complete |
| finalize | {count} | ✅ Complete |

### Artifacts

**Code**:
- Files created: {count}
- Files modified: {count}
- Tests added: {count}

**Documentation**:
- ADRs: {list}
- Interfaces: {list}

**Git**:
- Commits: {count}
- Branch: {branch}
- PR: #{pr-number}

### Quality

- Build: Passed
- Tests: {count} passed
- Coverage: {percentage}%
- Quality Gate: Passed
```
