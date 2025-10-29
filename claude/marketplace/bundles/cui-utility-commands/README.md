# CUI Utility Commands

Standalone utility commands for CUI project development and maintenance tasks that don't fit into specific workflow bundles.

## Purpose

This bundle provides general-purpose utility commands for:
- Project setup and permissions management
- IDE diagnostics and fixes
- Documentation generation and verification
- Architecture diagram updates
- Web permissions management

These utilities are independent tools that can be used across different CUI projects and workflows.

## Components Included

### Commands (6 commands)

1. **build-and-verify** - Project verification and build command
   - Runs Maven build with all quality checks
   - Optionally commits and pushes changes
   - Usage: `/cui-build-and-verify [push]`

2. **create-update-agents-md** - agents.md generation
   - Creates or updates agents.md following OpenAI specification
   - Sources from CLAUDE.md, doc/ai-rules.md, or global standards
   - Usage: `/cui-create-update-agents-md [push]`

3. **fix-intellij-diagnostics** - IDE diagnostics fixer
   - Retrieves and fixes IDE diagnostics automatically
   - Suppresses only when no reasonable fix available
   - Usage: `/cui-fix-intellij-diagnostics [file=<path>] [auto-fix=<boolean>] [push]`

4. **manage-web-permissions** - WebFetch domain manager
   - Analyzes domains across all projects
   - Consolidates safe domains to global settings
   - Performs security research on unknown domains
   - Usage: `/cui-manage-web-permissions [auto] [project=<path>] [dry-run]`

5. **setup-project-permissions** - Permission setup and verification
   - Fixes duplicates, suspicious permissions, path formats
   - Manages temp directory permissions
   - Ensures proper permission organization
   - Usage: `/cui-setup-project-permissions [add=<permission>] [ensurePermissions=<list>] [dry-run] [auto-fix]`

6. **verify-architecture-diagrams** - PlantUML diagram verification
   - Analyzes and updates PlantUML diagrams
   - Regenerates PNG images
   - Removes orphaned diagrams with approval
   - Usage: `/cui-verify-architecture-diagrams [plantuml_dir] [push]`

## Installation

```bash
/plugin install cui-utility-commands
```

## Usage Examples

### Setup Project Permissions
```bash
# Basic verification and fixing
/cui-setup-project-permissions

# Add specific permission
/cui-setup-project-permissions add="Edit(//~/git/new-project/**)"

# Auto-fix safe issues
/cui-setup-project-permissions auto-fix
```

### Manage WebFetch Permissions
```bash
# Analyze all projects and consolidate domains
/cui-manage-web-permissions

# Auto-consolidate safe domains
/cui-manage-web-permissions auto

# Preview changes without applying
/cui-manage-web-permissions dry-run
```

### Build and Verify Project
```bash
# Run build and fix issues
/cui-build-and-verify

# Build, fix, commit, and push
/cui-build-and-verify push
```

### Fix IDE Diagnostics
```bash
# Fix current file automatically
/cui-fix-intellij-diagnostics

# Fix specific file with manual approval
/cui-fix-intellij-diagnostics file=src/main/java/MyClass.java auto-fix=false

# Fix and push changes
/cui-fix-intellij-diagnostics push
```

### Update agents.md
```bash
# Create/update agents.md
/cui-create-update-agents-md

# Update and commit/push
/cui-create-update-agents-md push
```

### Verify Architecture Diagrams
```bash
# Verify all diagrams in doc/plantuml
/cui-verify-architecture-diagrams

# Verify and commit/push changes
/cui-verify-architecture-diagrams push
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
- `cui-project-quality-gates` - For build verification within workflows
- `cui-documentation-standards` - For documentation review (separate from diagram verification)
- `cui-plugin-development-tools` - For plugin creation tools

## Notes

- Commands in this bundle are general-purpose utilities
- They don't form a cohesive workflow (unlike other bundles)
- Each can be used independently as needed
- Install this bundle for access to all CUI maintenance utilities
