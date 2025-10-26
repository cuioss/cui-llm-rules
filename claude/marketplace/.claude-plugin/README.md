# CUI Marketplace Plugin Metadata

This directory contains metadata for the CUI Development Standards Marketplace, enabling it to be recognized and added as a local plugin marketplace in Claude Code.

## Structure

```
.claude-plugin/
├── README.md           # This file
└── marketplace.json    # Marketplace metadata
```

## marketplace.json

The `marketplace.json` file contains:

- **Basic Information**: Name, ID, version, description
- **Skills Catalog**: All 8 available CUI skills with descriptions and paths
- **Categories**: Organized by development domain
- **Quality Metrics**: Current quality scores and thresholds
- **Metadata**: Repository structure and documentation links

## Adding the Marketplace to Claude Code

To add this marketplace as a local plugin marketplace in Claude Code:

```bash
# Navigate to the marketplace directory
cd /Users/oliver/git/cui-llm-rules/claude/marketplace

# Add as local marketplace (example command - adjust based on Claude Code CLI)
# The exact command depends on your Claude Code setup
```

Alternatively, reference the absolute path to this marketplace directory in your Claude Code settings.

## Marketplace Contents

**8 Production-Ready Skills** (97.75/100 average quality):

### Java Development (4 skills)
- `cui-java-core` - Core Java patterns and standards
- `cui-java-unit-testing` - JUnit 5 testing standards
- `cui-javadoc` - JavaDoc documentation standards
- `cui-java-cdi` - CDI/Quarkus development standards

### Frontend Development (1 skill)
- `cui-frontend-development` - JavaScript, CSS, web components, testing

### Documentation (1 skill)
- `cui-documentation` - README, AsciiDoc, technical writing

### Project Management (2 skills)
- `cui-project-setup` - Project initialization and configuration
- `cui-requirements` - Requirements engineering and planning

## Verification

To verify the marketplace metadata is valid:

```bash
# Validate JSON structure
cat marketplace.json | jq .

# Check skills paths exist
ls -la ../skills/cui-*
```

## Version Information

- **Marketplace Version**: 1.0.0
- **Skills Count**: 8
- **Average Quality**: 97.75/100
- **Status**: Production Ready ✅
- **Last Updated**: 2025-10-24

## Related Documentation

- [Marketplace Overview](../README.md)
- [Setup Guide](../SETUP.md)
- [Skills Catalog](../skills/README.md)
- [Skills Quick Reference](../skills/QUICK-REFERENCE.md)

---

**Note**: This metadata structure enables the CUI marketplace to be discoverable and installable as a local plugin marketplace in Claude Code, providing centralized access to all CUI development standards and skills.
