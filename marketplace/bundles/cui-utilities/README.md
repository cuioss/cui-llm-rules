# CUI Utility Commands

Standalone utility tools including research agents and commands for CUI project development and maintenance tasks that don't fit into specific workflow bundles.

## Purpose

This bundle provides general-purpose utility tools for:
- Web research and best practices investigation
- Project setup and permissions management
- IDE diagnostics and fixes
- Documentation generation and verification
- Architecture diagram updates
- Web permissions management

These utilities are independent tools that can be used across different CUI projects and workflows.

> **Note**: Maven build verification has been moved to the **cui-maven** bundle. Use `/maven-build-and-fix` from that bundle for Maven-related build tasks.

## Components Included

### Skills (9 skills)

1. **cui-diagnostic-patterns** - Tool usage patterns for non-prompting file operations
2. **cui-general-development-rules** - Core development principles for CUI projects
3. **json-file-operations** - Generic JSON file CRUD with path notation support
4. **claude-memory** - Memory layer operations for .claude/memory/ session persistence
5. **claude-run-configuration** - Run configuration handling for .claude/run-configuration.json
6. **permission-management** - Permission validation and settings management
7. **script-runner** - Script resolution and execution with portable notation
8. **toon-usage** - TOON format specification and usage patterns for agent communication (50% token reduction)
9. **web-security-standards** - Trusted domains and security assessment patterns

### Agents (1 agent)

1. **research-best-practices** - Web research and best practices investigation
   - Performs comprehensive web research on any topic
   - Searches and analyzes top 10-15 sources
   - Provides confidence levels (HIGH/MEDIUM/LOW) based on source quality
   - Identifies contradictions and conflicting recommendations
   - Maintains complete reference trails
   - Invoked when user requests research, best practices, or topic investigation

### Commands (7 commands)

1. **audit-permission-wildcards** - Marketplace wildcard analyzer
   - Analyzes marketplace bundles to identify required permission wildcard patterns
   - Generates minimal set of wildcards for all marketplace tools
   - Usage: `/tools-audit-permission-wildcards [--dry-run]`

2. **create-update-agents-md** - agents.md generation
   - Creates or updates agents.md following OpenAI specification
   - Sources from CLAUDE.md, doc/ai-rules.md, or global standards
   - Usage: `/tools-sync-agents-file [push]`

3. **fix-intellij-diagnostics** - IDE diagnostics fixer
   - Retrieves and fixes IDE diagnostics automatically
   - Suppresses only when no reasonable fix available
   - Usage: `/tools-fix-intellij-diagnostics [file=<path>] [auto-fix=<boolean>] [push]`

4. **manage-web-permissions** - WebFetch domain manager
   - Analyzes domains across all projects
   - Consolidates safe domains to global settings
   - Performs security research on unknown domains
   - Usage: `/tools-manage-web-permissions [auto] [project=<path>] [dry-run]`

5. **setup-project-permissions** - Permission setup and verification
   - Fixes duplicates, suspicious permissions, path formats
   - Manages temp directory permissions
   - Ensures proper permission organization
   - Usage: `/tools-setup-project-permissions [add=<permission>] [ensurePermissions=<list>] [dry-run] [auto-fix]`

6. **verify-architecture-diagrams** - PlantUML diagram verification
   - Analyzes and updates PlantUML diagrams
   - Regenerates PNG images
   - Removes orphaned diagrams with approval
   - Usage: `/tools-verify-architecture-diagrams [plantuml_dir] [push]`

7. **discover-skill-scripts** - Script discovery and registration
   - Discovers all skill scripts from installed plugins
   - Generates `.claude/scripts.local.json` with path mappings
   - Usage: `/tools-discover-skill-scripts`

## Installation

```bash
/plugin install cui-utilities
```

## Usage Examples

### Research Best Practices
The research-best-practices agent is automatically invoked when you ask for research:

```
User: "Research best practices for API design"
User: "What are the recommendations for Java logging frameworks?"
User: "Investigate test automation best practices 2025"
```

The agent will:
- Search for "{topic} best practices 2025"
- Fetch and analyze top 10-15 sources
- Provide HIGH/MEDIUM/LOW confidence ratings
- Include complete source references
- Flag any conflicting recommendations

### Setup Project Permissions
```bash
# Basic verification and fixing
/tools-setup-project-permissions

# Add specific permission
/tools-setup-project-permissions add="Edit(//~/git/new-project/**)"

# Auto-fix safe issues
/tools-setup-project-permissions auto-fix
```

### Manage WebFetch Permissions
```bash
# Analyze all projects and consolidate domains
/tools-manage-web-permissions

# Auto-consolidate safe domains
/tools-manage-web-permissions auto

# Preview changes without applying
/tools-manage-web-permissions dry-run
```

### Fix IDE Diagnostics
```bash
# Fix current file automatically
/tools-fix-intellij-diagnostics

# Fix specific file with manual approval
/tools-fix-intellij-diagnostics file=src/main/java/MyClass.java auto-fix=false

# Fix and push changes
/tools-fix-intellij-diagnostics push
```

### Update agents.md
```bash
# Create/update agents.md
/tools-sync-agents-file

# Update and commit/push
/tools-sync-agents-file push
```

### Verify Architecture Diagrams
```bash
# Verify all diagrams in doc/plantuml
/tools-verify-architecture-diagrams

# Verify and commit/push changes
/tools-verify-architecture-diagrams push
```

## Dependencies

None - this bundle is standalone and can be used independently.

## Key Features

- **Independent Utilities**: Each command solves a specific maintenance task
- **Cross-Project**: Commands work across different CUI projects
- **Safe Defaults**: Includes dry-run and auto-fix modes
- **Optional Push**: Commands support optional commit/push after completion
- **Comprehensive**: Covers project setup, permissions, diagnostics, docs, and architecture

## Related Bundles

These utilities complement but don't depend on other bundles:
- `cui-maven` - Maven build verification and POM maintenance
- `cui-documentation-standards` - For documentation review (separate from diagram verification)
- `cui-plugin-development-tools` - For plugin creation tools
- `cui-task-workflow` - May use research-best-practices agent for industry standards research

## Notes

- Commands in this bundle are general-purpose utilities
- They don't form a cohesive workflow (unlike other bundles)
- Each can be used independently as needed
- Install this bundle for access to all CUI maintenance utilities
