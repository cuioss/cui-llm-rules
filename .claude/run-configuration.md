# Command Configuration

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
- `mcpcat.io` - MCP server analytics and debugging tools, relevant for Model Context Protocol development
- `skywork.ai` - AI workspace research platform, legitimate but new service (launched May 2025)

**Global Domains Available**:
This project has access to 7 globally-approved domains:
- `github.com` - Code hosting
- `raw.githubusercontent.com` - GitHub raw content
- `medium.com` - Publishing platform
- `ux.stackexchange.com` - UX Q&A
- `www.anthropic.com` - Anthropic documentation
- `www.llamaindex.ai` - LlamaIndex LLM framework docs
- `www.usertesting.com` - UX research platform

**Total WebFetch Access**: 9 domains (2 local + 7 global)

### Last Updated

- Date: 2025-01-27
- Action: Migrated from universal access (WebFetch(domain:*)) to specific domains
- Removed redundant domains: 7 (moved to global)
- Kept local: 2 (project-specific)

### Notes

**Security Improvement**: Removed `WebFetch(domain:*)` from global settings and replaced with explicit domain permissions for better security control and auditability.

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
