# Fix Proposal: cui-diagnose-bundle.md Tool Usage

## Add Tool Usage Guidelines Section

Insert immediately after the PARAMETER VALIDATION section (before WORKFLOW INSTRUCTIONS):

```markdown
## TOOL USAGE REQUIREMENTS

**CRITICAL**: This command must use non-prompting tools to avoid user interruptions during diagnosis.

### Required Tool Usage Patterns

✅ **File Discovery (replaces find, ls):**
```
# Discover files by pattern
Glob(pattern="*.md", path="/path/to/directory")

# Discover directories
Glob(pattern="*", path="/path/to/parent")

# Recursive discovery
Glob(pattern="**/*.md", path="/path/to/root")
```

✅ **File Existence Checks (replaces test -f, test -d):**
```
# Check if file exists
try:
    Read(file_path="/path/to/file")
    # File exists
except:
    # File doesn't exist

# Check if directory exists
result = Glob(pattern="*", path="/path/to/dir")
if result:
    # Directory exists
else:
    # Directory doesn't exist
```

✅ **Content Search (replaces grep):**
```
# Search for pattern in files
Grep(pattern="search_term", path="/path", output_mode="content", -n=true)

# Find files containing pattern
Grep(pattern="search_term", path="/path", output_mode="files_with_matches")
```

❌ **DO NOT USE Bash for:**
- File discovery (find, ls)
- Existence checks (test -f, test -d)
- Content search (grep, rg)
- Directory listing

**Bash is ONLY acceptable for:**
- Git operations that require it
- Operations with no tool equivalent

**Why**: Bash commands trigger user prompts which interrupt the diagnostic flow and create poor UX.
```

## Specific Replacements

### Step 1: Discover and Select Bundle

**Current (lines 54-60):**
```markdown
If no parameters:
- List all bundles:
  ```bash
  find ~/git/cui-llm-rules/claude/marketplace/bundles -mindepth 1 -maxdepth 1 -type d -exec basename {} \; | sort
  ```
```

**Replace with:**
```markdown
If no parameters:
- Use Glob to discover all bundles:
  ```
  Glob(pattern="*", path="~/git/cui-llm-rules/claude/marketplace/bundles")
  ```
- Extract bundle names from paths (basename of each result)
- Sort alphabetically
```

### Step 3.1: Check Required Directories

**Current (lines 93-101):**
```markdown
```bash
# Check .claude-plugin/
test -d {bundle_path}/.claude-plugin

# Check component directories
test -d {bundle_path}/agents
test -d {bundle_path}/commands
test -d {bundle_path}/skills
```
```

**Replace with:**
```markdown
Use Glob to check directory existence:
```
# Check .claude-plugin/
result = Glob(pattern=".claude-plugin", path="{bundle_path}")
exists = len(result) > 0

# Check component directories
agents_exists = Glob(pattern="agents", path="{bundle_path}")
commands_exists = Glob(pattern="commands", path="{bundle_path}")
skills_exists = Glob(pattern="skills", path="{bundle_path}")
```

Alternative: Use Read on a known file within the directory to verify:
```
# If directory has files, Read any file to confirm directory exists
# Empty directories can use Glob as above
```
```

### Step 3.2: Check Required Files

**Current (lines 118-126):**
```markdown
```bash
# Check plugin manifest
test -f {bundle_path}/.claude-plugin/plugin.json

# Check README
test -f {bundle_path}/README.md
```
```

**Replace with:**
```markdown
Use Read to check file existence and load content:
```
# Check plugin manifest (will be needed anyway)
try:
    manifest_content = Read(file_path="{bundle_path}/.claude-plugin/plugin.json")
    manifest_exists = True
except:
    manifest_exists = False

# Check README (will be needed anyway)
try:
    readme_content = Read(file_path="{bundle_path}/README.md")
    readme_exists = True
except:
    readme_exists = False
```

**Benefit**: File content is loaded for later validation, avoiding redundant reads.
```

### Step 3.3: Check for Unexpected Files

**Current (lines 140-145):**
```markdown
```bash
# List all files in bundle root
ls -la {bundle_path}/
```
```

**Replace with:**
```markdown
Use Glob to list files in bundle root:
```
# List all files/directories in bundle root
all_items = Glob(pattern="*", path="{bundle_path}")

# List hidden files (except .claude-plugin/)
hidden_items = Glob(pattern=".*", path="{bundle_path}")

# Filter and check for unexpected patterns
unexpected = []
for item in all_items + hidden_items:
    if matches_unexpected_pattern(item):
        unexpected.append(item)
```

Unexpected patterns to check:
- .DS_Store
- node_modules/
- *.tmp, *.bak
- .idea/, .vscode/
```

### Step 4.1: Parse JSON

**Current (lines 179-183):**
```markdown
```bash
cat {bundle_path}/.claude-plugin/plugin.json
```
```

**Replace with:**
```markdown
Use Read to load plugin.json (already loaded in Step 3.2):
```
# Already loaded as manifest_content in Step 3.2
# Parse as JSON
import json
try:
    manifest = json.loads(manifest_content)
    json_valid = True
except json.JSONDecodeError as e:
    json_valid = False
    json_error = str(e)
```

**Note**: If not already loaded, use:
```
manifest_content = Read(file_path="{bundle_path}/.claude-plugin/plugin.json")
```
```

### Step 6.1: Scan Components

**Current (lines 415-423):**
```markdown
```bash
# Find all agents
find {bundle_path}/agents -name "*.md" -type f

# Find all commands
find {bundle_path}/commands -name "*.md" -type f

# Find all skills
find {bundle_path}/skills -mindepth 1 -maxdepth 1 -type d
```
```

**Replace with:**
```markdown
Use Glob to discover all components:
```
# Find all agents
agents = Glob(pattern="*.md", path="{bundle_path}/agents")
component_agents = len(agents)

# Find all commands
commands = Glob(pattern="*.md", path="{bundle_path}/commands")
component_commands = len(commands)

# Find all skills (directories in skills/)
skills = Glob(pattern="*", path="{bundle_path}/skills")
# Filter to only directories (not files)
skill_dirs = [s for s in skills if is_directory(s)]
component_skills = len(skill_dirs)
```

**Note**: To check if path is directory, use:
```
# Glob returns paths; if path contains SKILL.md, it's a skill directory
is_skill = Glob(pattern="SKILL.md", path=potential_skill_dir)
```
```

### Step 7.1: Check Agent-Command Integration

**Current (lines 517-520):**
```markdown
```bash
grep -r "SlashCommand\|/cui-" {bundle_path}/agents/
```
```

**Replace with:**
```markdown
Use Grep to find command references in agents:
```
# Search for command references
command_refs = Grep(
    pattern="SlashCommand|/cui-",
    path="{bundle_path}/agents",
    output_mode="content",
    -n=true
)

# Parse results to extract referenced commands
# Example result: "filename:42:SlashCommand: /cui-build-and-verify"
for match in command_refs:
    # Extract command name and verify it exists
    command_name = extract_command_name(match)
    command_exists = check_command_exists(command_name)
```
```

### Step 7.2: Check Agent-Skill Integration

**Current (lines 525-528):**
```markdown
```bash
grep -r "Skill:\|skill:" {bundle_path}/agents/
```
```

**Replace with:**
```markdown
Use Grep to find skill references in agents:
```
# Search for skill references
skill_refs = Grep(
    pattern="Skill:|skill:",
    path="{bundle_path}/agents",
    output_mode="content",
    -n=true
)

# Parse results to extract referenced skills
# Example result: "filename:37:Skill: cui-javadoc"
for match in skill_refs:
    # Extract skill name and verify it exists
    skill_name = extract_skill_name(match)
    skill_exists = check_skill_exists(skill_name)
```
```

## Summary of Changes

| Operation | Before (Prompts) | After (No Prompts) | Line Numbers |
|-----------|------------------|-------------------|--------------|
| Bundle discovery | find + basename | Glob | 54-60 |
| Directory checks | test -d (4×) | Glob | 93-101 |
| File checks | test -f (2×) | Read + try/except | 118-126 |
| List root files | ls -la | Glob | 140-145 |
| Read plugin.json | cat | Read | 179-183 |
| Find agents | find | Glob | 415-423 |
| Find commands | find | Glob | 415-423 |
| Find skills | find | Glob | 415-423 |
| Search commands | grep -r | Grep | 517-520 |
| Search skills | grep -r | Grep | 525-528 |

**Total**: 15 bash operations → 0 prompts

## Testing Checklist

After applying fixes:

- [ ] Run `/cui-diagnose-bundle cui-maven`
- [ ] Verify no user prompts appear
- [ ] Confirm all directory checks work
- [ ] Confirm all file checks work
- [ ] Confirm component discovery works
- [ ] Confirm integration checks work
- [ ] Verify error handling for missing files
- [ ] Check JSON parsing still works
- [ ] Verify health score calculation
- [ ] Confirm final report generation

## Implementation Order

1. Add TOOL USAGE REQUIREMENTS section first
2. Update Step 1 (bundle discovery)
3. Update Step 3 (structure validation)
4. Update Step 4 (JSON parsing)
5. Update Step 6 (component discovery)
6. Update Step 7 (integration checks)
7. Test thoroughly
8. Apply same pattern to other diagnose commands

## Notes for Developer

- **Read tool advantage**: Can read file AND check existence in one operation
- **Glob tool advantage**: Returns empty array if path doesn't exist (no error handling needed)
- **Grep tool advantage**: Can search multiple files, filter by glob pattern
- **Error handling**: Use try/except for Read operations to check existence
- **Performance**: Non-prompting tools are actually faster (no user interaction delay)
