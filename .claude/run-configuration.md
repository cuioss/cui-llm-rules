/# Command Configuration

## docs-technical-adoc-review

### Skipped Files

Files excluded from technical AsciiDoc review:

(None currently)

### Skipped Directories

Directories excluded entirely:

- `target/` - Build artifacts (auto-generated)
- `node_modules/` - Dependencies
- `.git/` - Git metadata

### Acceptable Warnings

Warnings approved as acceptable:

(None currently)

### Last Execution

- Date: 2025-10-23 (second run)
- Directories processed: 1
- Files reviewed: 5
- Issues fixed: 24
- Status: SUCCESS
- Parallel agents: 0

### Lessons Learned

(None currently - all identified issues have been addressed in standards and agent implementation)

---

## manage-webfetch-domains

### WebFetch Domains for This Project

**Local Domains** (project-specific):
- `blog.sonatype.com` - Sonatype security blog for dependency security best practices
- `docs.sonarsource.com` - SonarQube/SonarCloud documentation
- `www.martinkanters.dev` - Martin Kanters' blog on Java and security topics
- `www.sonatype.com` - Sonatype documentation and resources

**Global Domains Available**:
This project has access to globally-approved domains for common development resources

**Total WebFetch Access**: 4 local domains + global domains

### Last Updated

- Date: 2025-11-04
- Action: Cleaned up permissions during setup-project-permissions execution
- Removed: Invalid/suspicious bash patterns, redundant read permissions
- Added: `Write(.claude/settings.local.json)` to ask list for security

### Notes

**Security Improvement**: Removed `WebFetch(domain:*)` from global settings and replaced with explicit domain permissions for better security control and auditability.

---

## setup-project-permissions

### Last Execution

- Date: 2025-11-22 (Sixth run - {baseDir} architecture compliance)
- Result: Fixed architecture violations, added global marketplace permissions
- Status: SUCCESS

### Changes Applied

**Global Settings Updated:**
- **ADDED 51 marketplace permissions:**
  - 8 Skill bundle wildcards: `Skill(cui-documentation-standards:*)`, etc.
  - 8 SlashCommand bundle wildcards: `SlashCommand(/cui-java-expert:*)`, etc.
  - 35 SlashCommand short-form permissions: `/java-implement-code:*`, etc.

**Local Settings Updated:**
- **REMOVED 4 incorrect permissions:**
  - `Skill(cui-diagnostic-patterns)` - Should be global, not local
  - `Skill(cui-utilities:permission-management)` - Should be global, not local
  - `Skill(cui-plugin-development-tools:marketplace-inventory)` - Should be global, not local
  - `Bash(bash /Users/.../scan-marketplace-inventory.sh:*)` - Violates {baseDir} pattern
- **KEPT 7 project-specific permissions:**
  - `Bash(claude-code:*)` - Claude Code CLI operations
  - `Edit(//~/git/cui-llm-rules/**)` - Project editing
  - `Write(//~/git/cui-llm-rules/**)` - Project file creation
  - `Read(//marketplace/**)` - Marketplace bundle access
  - `Read(//.claude/**)` - Claude configuration access
  - `Read(//standards/**)` - Standards documentation access
  - `WebFetch(domain:formulae.brew.sh)` - Homebrew formula documentation

### Critical Architecture Lesson

**Problem:** Previous approach incorrectly tried to add script permissions for 9 scripts × 3 path formats = 27 Bash permissions per project.

**Why This Was Wrong:**
- The `{baseDir}` pattern handles script portability automatically
- Scripts are invoked via `bash {baseDir}/scripts/script.sh` in SKILL.md
- Claude resolves `{baseDir}` to the skill's mounted directory at runtime
- No hardcoded absolute paths should ever be in settings

**Correct Architecture:**
- Skills use `{baseDir}/scripts/` pattern (see plugin-architecture skill)
- `{baseDir}` resolves to: `~/.claude/skills/my-skill/` (global), `.claude/skills/my-skill/` (project), or `marketplace/bundles/{bundle}/skills/my-skill/` (bundle)
- Script permissions are NOT needed in settings - the skill system handles this

### Permission Summary

**Global Settings:**
- Allow: 226 permissions
  - 145 Bash commands (comprehensive development tools)
  - 8 Skill bundle wildcards
  - 8 SlashCommand bundle wildcards
  - 35 SlashCommand short-form permissions
  - 30 WebFetch domains
  - WebSearch
- Deny: 69 permissions (dangerous commands blocked)

**Local Settings:**
- Allow: 7 permissions (project-specific only)
  - 1 Bash permission: `claude-code:*`
  - 2 Edit/Write permissions: `cui-llm-rules/**`
  - 3 Read permissions: `marketplace/**`, `.claude/**`, `standards/**`
  - 1 WebFetch permission: `formulae.brew.sh`
- Deny: 0 permissions
- Ask: 0 permissions

### Compliance Status

✅ All marketplace bundle wildcards in global settings (8 skills + 8 commands)
✅ All short-form command permissions in global settings (35 commands)
✅ No {baseDir} architecture violations
✅ No hardcoded script paths
✅ Minimal project-specific permissions
✅ Proper separation of global vs local concerns

### Architecture Notes

**{baseDir} Pattern (Critical):**
- All skill scripts use `{baseDir}/scripts/` in SKILL.md
- Claude resolves `{baseDir}` at runtime based on installation location
- NEVER add individual script path permissions to settings
- See: `plugin-architecture` skill for full details

**Permission Separation:**
- **Global**: Bash commands, Skills, SlashCommands, WebFetch domains
- **Local**: Edit/Write for specific project, project-specific Read patterns

---

## Agent Architecture Decisions

### pr-quality-fixer Agent

**Status**: Keep as monolithic agent (716 lines)

**Decision Date**: 2025-10-30

**Rationale**:
- Agent handles complex PR quality workflow with interdependent steps
- Splitting into specialized agents (sonar-issue-fixer, coverage-analyzer, test-generator) would be possible but deferred
- Future work may introduce specialized agents for specific aspects as needed

**Current Responsibilities**:
1. Retrieve and resolve Sonar code quality issues
2. Analyze code coverage gaps
3. Generate JUnit tests for uncovered code
4. Coordinate build verification and commit workflow

**Future Consideration**:
When specific aspects require independent invocation or the workflow needs more flexibility, consider extracting specialized agents for:
- Sonar issue resolution only
- Coverage analysis and test generation
- Build verification and quality gate checking

### asciidoc-reviewer Agent

**Status**: Refactored into orchestrator + 3 specialized agents

**Completion Date**: 2025-10-30

**Original**: 704 lines monolithic agent

**Result**: 4 focused agents
1. `asciidoc-format-validator.md` (182 lines) - Format compliance checking
2. `asciidoc-link-verifier.md` (260 lines) - Link and cross-reference verification
3. `asciidoc-content-reviewer.md` (342 lines) - Content quality review
4. `asciidoc-reviewer.md` (328 lines) - Orchestrator

**Benefits**:
- Users can invoke specialized agents directly for focused reviews
- Each agent has clear single responsibility
- Improved maintainability and testability
- Better tool coverage tracking per concern
