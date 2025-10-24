# Project Skills

This directory contains symlinks to CUI skills in the marketplace.

## Structure

Skills are symlinked from `claude/marketplace/skills/` to enable auto-discovery by Claude Code.

```
.claude/skills/
├── cui-java-core -> ../../claude/marketplace/skills/cui-java-core
├── cui-java-unit-testing -> ../../claude/marketplace/skills/cui-java-unit-testing
├── cui-javadoc -> ../../claude/marketplace/skills/cui-javadoc
├── cui-java-cdi -> ../../claude/marketplace/skills/cui-java-cdi
├── cui-frontend-development -> ../../claude/marketplace/skills/cui-frontend-development
├── cui-documentation -> ../../claude/marketplace/skills/cui-documentation
├── cui-project-setup -> ../../claude/marketplace/skills/cui-project-setup
└── cui-requirements -> ../../claude/marketplace/skills/cui-requirements
```

## Why Symlinks?

- **Auto-discovery**: Claude Code automatically finds skills in `.claude/skills/`
- **Single source**: Actual skill content in `claude/marketplace/skills/`
- **No duplication**: Symlinks avoid copying files
- **Easy maintenance**: Edit once, available everywhere

## Discovery Mechanism

Claude Code discovers skills from three sources:
1. Personal skills: `~/.claude/skills/` (your machine)
2. Project skills: `.claude/skills/` (shared via git) ⬅️ **This directory**
3. Plugin skills: Bundled with installed plugins

## For Team Members

When you clone this repository:
1. Skills are automatically available (via symlinks)
2. No manual installation needed
3. All 8 CUI skills ready to use

## Updating Skills

To update skills, edit files in `claude/marketplace/skills/`. Changes are automatically reflected via symlinks.

## Manual Installation (Alternative)

If symlinks don't work on your system, copy skills manually:

```bash
cp -r claude/marketplace/skills/cui-* .claude/skills/
```

## Verification

Check that skills are discovered:
```bash
ls -la .claude/skills/
```

You should see 8 skill symlinks pointing to `../../claude/marketplace/skills/`.
