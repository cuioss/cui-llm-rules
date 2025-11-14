# CUI Skills Marketplace Setup Guide

Complete guide for setting up and using the CUI skills marketplace with Claude Code.

## Quick Setup (Automatic)

✅ **The skills are already configured!** When you clone this repository, skills are automatically available via symlinks in `.claude/skills/`.

**Verify setup:**
```bash
ls -la .claude/skills/
```

You should see 8 skill symlinks.

---

## How It Works

### Claude Code Skills Discovery

Claude Code automatically discovers skills from three locations:

1. **Personal Skills**: `~/.claude/skills/` (your machine only)
2. **Project Skills**: `.claude/skills/` (shared via git) ⬅️ **We use this**
3. **Plugin Skills**: Bundled with installed plugins

### Our Architecture

```
cui-llm-rules/
├── .claude/
│   └── skills/                          # Auto-discovered by Claude Code
│       ├── cui-java-core                # Symlink →
│       ├── cui-java-unit-testing        # Symlink →
│       └── ... (all 8 skills)           # Symlinks →
│
└── claude/
    └── marketplace/
        └── skills/                      # Source of truth
            ├── cui-java-core/           # ← Actual skill content
            │   ├── SKILL.md
            │   ├── README.md
            │   └── standards/
            ├── cui-java-unit-testing/
            └── ... (all 8 skills)
```

**Benefits**:
- ✅ Auto-discovered by Claude Code
- ✅ Single source of truth in `marketplace/skills/`
- ✅ No file duplication
- ✅ Team members get skills automatically
- ✅ Easy to maintain and update

---

## Verification

### 1. Check Skills Are Linked

```bash
cd /path/to/cui-llm-rules
ls -la .claude/skills/
```

**Expected output**: 8 symlinks pointing to `../../marketplace/skills/cui-*`

### 2. Test Skill Discovery

Open Claude Code and try:
- "Help me write Java code" → Should activate `cui-java-core`
- "Write unit tests" → Should activate `cui-java-unit-testing`
- "Document this class" → Should activate `cui-javadoc`

### 3. Check Skill Content

Each skill symlink should resolve to actual content:
```bash
cat .claude/skills/cui-java-core/SKILL.md | head -20
```

Should show YAML frontmatter and skill instructions.

---

## Troubleshooting

### Issue: Symlinks Don't Work (Windows)

**Problem**: Windows may not support symlinks without admin privileges.

**Solution 1 - Enable Developer Mode** (Windows 10/11):
1. Settings → Update & Security → For Developers
2. Enable "Developer Mode"
3. Re-clone repository

**Solution 2 - Copy Files Instead**:
```bash
cp -r marketplace/skills/cui-* .claude/skills/
```

**Downside**: Must manually sync when marketplace skills are updated.

### Issue: Skills Not Discovered

**Check 1 - Verify Directory Exists**:
```bash
ls -la .claude/skills/
```

**Check 2 - Check Symlink Targets**:
```bash
ls -la .claude/skills/cui-java-core
```

Should show it points to `../../marketplace/skills/cui-java-core`.

**Check 3 - Verify SKILL.md Files**:
```bash
find .claude/skills -name "SKILL.md"
```

Should list 8 SKILL.md files (via symlinks).

**Check 4 - Check Claude Code Settings**:
```bash
cat .claude/settings.json
```

Should allow reading `.claude/**` and `claude/**`.

### Issue: Git Shows Symlinks as Modified

**Problem**: Git on some systems shows symlinks as modified even when unchanged.

**Solution - Add to .gitattributes**:
```bash
echo ".claude/skills/* symlink" >> .gitattributes
```

Or configure git to handle symlinks:
```bash
git config core.symlinks true
```

### Issue: Permission Denied

**Problem**: Cannot read skills through symlinks.

**Check Permissions**:
```bash
ls -la marketplace/skills/cui-java-core/
```

**Fix Permissions**:
```bash
chmod -R a+r marketplace/skills/
```

---

## Manual Setup (If Needed)

If automatic setup doesn't work, create symlinks manually:

### On macOS/Linux:

```bash
cd /path/to/cui-llm-rules
mkdir -p .claude/skills

cd .claude/skills
for skill in ../../marketplace/skills/cui-*; do
  ln -sf "$skill" "$(basename "$skill")"
done
```

### On Windows (PowerShell with Admin):

```powershell
cd C:\path\to\cui-llm-rules
New-Item -ItemType Directory -Force -Path ".claude\skills"

cd .claude\skills
Get-ChildItem "..\..\claude\marketplace\skills\cui-*" | ForEach-Object {
    New-Item -ItemType SymbolicLink -Name $_.Name -Target $_.FullName
}
```

### Alternative: Copy Instead of Symlink

```bash
cp -r marketplace/skills/cui-* .claude/skills/
```

**Remember**: Updates to marketplace skills won't automatically reflect in `.claude/skills/`.

---

## Updating Skills

### When Marketplace Skills Are Updated

If you're using **symlinks** (default):
- ✅ Changes automatically reflected
- No action needed

If you **copied files**:
- ❌ Must manually re-copy
```bash
rm -rf .claude/skills/cui-*
cp -r marketplace/skills/cui-* .claude/skills/
```

---

## For Developers

### Adding New Skills

1. Create skill in `marketplace/skills/new-skill/`
2. Add SKILL.md with YAML frontmatter
3. Create symlink:
```bash
cd .claude/skills
ln -sf ../../marketplace/skills/new-skill new-skill
```

### Quality Verification

Run diagnose-skills to verify quality:
```bash
/diagnose-skills new-skill
```

Target: Quality score ≥ 75/100

### Removing Skills

Remove both symlink and source:
```bash
rm .claude/skills/skill-name
rm -rf marketplace/skills/skill-name
```

---

## Team Setup

### For Team Members

When cloning the repository:

1. **Clone repository**:
```bash
git clone <repository-url>
cd cui-llm-rules
```

2. **Verify skills** (should work automatically):
```bash
ls -la .claude/skills/
```

3. **Trust repository** in Claude Code:
   - Open repository in Claude Code
   - When prompted, click "Trust"
   - Skills are now active

### For Repository Maintainers

**Adding skills**:
1. Create in `marketplace/skills/`
2. Create symlink in `.claude/skills/`
3. Run `/diagnose-skills` to verify
4. Commit both directories

**Updating skills**:
1. Edit files in `marketplace/skills/`
2. Changes automatically reflected (via symlinks)
3. Run `/diagnose-skills` to verify
4. Commit changes

**Removing skills**:
1. Remove symlink from `.claude/skills/`
2. Remove source from `marketplace/skills/`
3. Update marketplace/skills/README.md
4. Commit changes

---

## Advanced Configuration

### Custom Skill Locations

To use personal skills alongside project skills:

**Personal skills** (your machine only):
```bash
mkdir -p ~/.claude/skills
cp -r marketplace/skills/cui-java-core ~/.claude/skills/
```

**Mix personal and project**:
- Project skills: Auto-discovered from `.claude/skills/`
- Personal skills: Auto-discovered from `~/.claude/skills/`
- Claude uses both

### Plugin Distribution (Future)

To distribute skills as a plugin:

1. Create plugin structure:
```
cui-skills-plugin/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    ├── cui-java-core/
    └── ... (all skills)
```

2. Publish to marketplace
3. Users install with: `/plugin install cui-skills`

See [Plugin Marketplaces docs](https://docs.claude.com/en/docs/claude-code/plugin-marketplaces) for details.

---

## Architecture Decisions

### Why Symlinks?

**Considered alternatives**:
1. ✅ **Symlinks** (chosen)
   - Single source of truth
   - Automatic updates
   - No duplication
   - Works on most systems

2. ❌ **Copy files**
   - Duplication
   - Manual sync required
   - Inconsistency risk

3. ❌ **Direct in `.claude/skills/`**
   - Poor organization
   - No marketplace concept
   - Harder to maintain

### Why Not Custom Directory?

Claude Code **only** auto-discovers from:
- `~/.claude/skills/` (personal)
- `.claude/skills/` (project)
- Plugin-bundled skills

Custom paths like `marketplace/skills/` require explicit loading, which isn't supported for automatic skill discovery.

---

## Support

### Getting Help

1. Check this SETUP.md
2. Review `.claude/skills/README.md`
3. Read `marketplace/skills/README.md`
4. Try troubleshooting steps above
5. Report issues in repository

### Common Questions

**Q: Can I use only some skills?**
A: Yes, remove unwanted symlinks from `.claude/skills/`.

**Q: How do I know which skill is active?**
A: Claude Code indicates active skills in the UI and mentions them in responses.

**Q: Can I modify skills?**
A: Yes, edit in `marketplace/skills/`. Changes reflect via symlinks.

**Q: Do skills work offline?**
A: Yes, skills are local files. No internet needed.

**Q: How do I disable a skill temporarily?**
A: Rename symlink: `mv .claude/skills/cui-java-core .claude/skills/cui-java-core.disabled`

---

## Version Information

- **Setup Version**: 1.0
- **Skills Version**: All skills at 97.75/100 average quality
- **Last Updated**: 2025-10-24
- **Status**: Production Ready ✅

---

**You're all set! Skills should be automatically discovered by Claude Code. 🎉**
