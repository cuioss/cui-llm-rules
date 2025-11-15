# CUI Marketplace Plugin Metadata

This directory contains metadata for the CUI Development Standards Marketplace, enabling it to be recognized and added as a plugin marketplace in Claude Code.

## Structure

```
.claude-plugin/
├── README.md           # This file
└── marketplace.json    # Marketplace metadata
```

## marketplace.json

The `marketplace.json` file follows the official Claude Code marketplace schema:

- **name**: `cui-development-standards`
- **owner**: Object with name (and optional email)
- **metadata**: Description and version information
- **plugins**: Array of plugin groupings, each containing:
  - `name`: Kebab-case plugin identifier
  - `description`: What the plugin provides
  - `source`: Base path (usually `./`)
  - `strict`: Validation mode (false for permissive)
  - `skills`: Array of paths to individual skill directories

## Plugin Organization

The marketplace organizes components into skill plugins and workflow bundles:

### Skill Plugins (4 plugins, 8 skills)

#### cui-java-skills (4 skills)
Java development standards including core patterns, unit testing, JavaDoc, and CDI/Quarkus
- `./skills/cui-java-core`
- `./skills/cui-java-unit-testing`
- `./skills/cui-javadoc`
- `./skills/cui-java-cdi`

#### cui-frontend-skills (1 skill)
Frontend development standards for JavaScript, CSS, web components, and testing
- `./skills/cui-frontend-development`

#### cui-documentation-skills (1 skill)
Documentation standards for README, AsciiDoc, and technical writing
- `./skills/cui-documentation`

#### cui-project-management-skills (2 skills)
Project setup and requirements engineering standards
- `./skills/cui-project-setup`
- `./skills/cui-requirements`

### Workflow Bundles (4 bundles)

#### cui-task-workflow
Complete development workflow from issue implementation to PR review and quality verification
- 5 agents (task-reviewer, task-breakdown-agent, task-executor, pr-review-responder, pr-quality-fixer)
- 2 commands (wf-orchestrate-task-workflow, wf-handle-pull-request)

#### cui-documentation-standards
AsciiDoc and documentation standards enforcement
- 1 agent, 1 skill, 1 command

#### cui-plugin-development-tools
Complete toolchain for creating and diagnosing Claude Code plugins
- 5 commands

#### cui-utilities
Standalone utility commands for project setup, permissions, diagnostics, and documentation
- 6 commands

## Adding the Marketplace to Claude Code

To add this marketplace in Claude Code:

```bash
# From within Claude Code, add the marketplace by path or repository
/plugin marketplace add /Users/oliver/git/cui-llm-rules/marketplace

# Or if hosted on GitHub:
/plugin marketplace add cuioss/cui-llm-rules/marketplace
```

## Verification

To verify the marketplace metadata is valid:

```bash
# Validate JSON structure
cat marketplace.json | jq .

# Check skills paths exist
ls -la ../skills/cui-*
```

## Version Information

- **Marketplace Name**: cui-development-standards
- **Marketplace Version**: 1.0.0
- **Skill Plugins Count**: 4
- **Workflow Bundles Count**: 6
- **Total Skills**: 8 (10 including bundled skills)
- **Total Agents**: 9
- **Total Commands**: 14
- **Status**: Production Ready ✅
- **Last Updated**: 2025-10-29

## Related Documentation

- [Marketplace Overview](../README.md)
- [Setup Guide](../SETUP.md)
- [Skills Catalog](../skills/README.md)
- [Skills Quick Reference](../skills/QUICK-REFERENCE.md)

---

## Schema Compliance

The marketplace.json structure complies with the Claude Code marketplace schema:

- ✅ Owner as object (not string)
- ✅ Plugin names in kebab-case (no spaces)
- ✅ Valid `source` field for each plugin
- ✅ Skills array with relative paths
- ✅ No unrecognized keys (removed: `id`, `type`, `path`, `category`, `version`)
- ✅ Proper metadata structure

**Note**: This metadata structure enables the CUI marketplace to be discoverable and installable as a plugin marketplace in Claude Code, providing centralized access to all CUI development standards and skills.
