# Tool Usage Patterns for Diagnostic Commands

## Core Principle

**Use non-prompting tools exclusively to avoid user interruptions during diagnostics.**

Bash commands trigger user prompts. Non-prompting tools execute automatically.

## Tool Selection Guide

| Operation | ❌ Don't Use (Prompts) | ✅ Use (No Prompts) | Pattern Reference |
|-----------|----------------------|-------------------|------------------|
| Find files | `find`, `ls` | `Glob` | Pattern 1 |
| Check file exists | `test -f`, `cat` | `Read` + try/except | Pattern 2 |
| Check directory exists | `test -d` | `Glob` | Pattern 2 |
| Search content | `grep`, `rg` via Bash | `Grep` | Pattern 3 |
| Read files | `cat` via Bash | `Read` | Pattern 4 |
| Count items | `wc -l` via Bash | Count results | Pattern 5 |
| List directory | `ls -la` via Bash | `Glob` | Pattern 1 |

## Pattern 1: File Discovery

Use **Glob** tool for all file and directory discovery operations.

### Find all files by extension

```
# Find all .md files in directory
Glob(pattern="*.md", path="/path/to/directory")

# Returns: ["/path/to/directory/file1.md", "/path/to/directory/file2.md", ...]
```

### Find files recursively

```
# Find all .md files in directory and subdirectories
Glob(pattern="**/*.md", path="/path/to/root")

# Returns: All matching files including nested ones
```

### Find specific file by name

```
# Find specific file
Glob(pattern="plugin.json", path="/path/to/directory")

# Returns: ["/path/to/directory/plugin.json"] or []
```

### Find directories

```
# List all directories in parent
Glob(pattern="*", path="/path/to/parent")

# Returns: All files and directories (filter by checking for subdirectory contents)
```

### Find multiple extensions

```
# Find .md and .adoc files
md_files = Glob(pattern="*.md", path="/path")
adoc_files = Glob(pattern="*.adoc", path="/path")
all_files = md_files + adoc_files
```

### Count files

```
# Count files matching pattern
files = Glob(pattern="*.md", path="/path")
count = len(files)
```

## Pattern 2: Existence Checks

Use **Read** for file existence, **Glob** for directory existence.

### Check if file exists

```
# Method 1: Try to read file
try:
    content = Read(file_path="/path/to/file")
    file_exists = True
except:
    file_exists = False
```

**Advantage**: If file exists, you already have the content loaded.

```
# Method 2: Use Glob
result = Glob(pattern="filename", path="/path/to/directory")
file_exists = len(result) > 0
```

**Advantage**: Doesn't load content, faster for large files.

### Check if directory exists

```
# Use Glob to check directory
result = Glob(pattern="*", path="/path/to/directory")
directory_exists = result is not None  # Empty dir returns [], missing dir may error

# More reliable: Try to glob a known subdirectory or file
result = Glob(pattern="dirname", path="/path/to/parent")
directory_exists = len(result) > 0
```

### Check if directory is empty

```
# Get all items in directory
items = Glob(pattern="*", path="/path/to/directory")
is_empty = len(items) == 0
```

### Check required structure

```
# Check multiple directories exist
required_dirs = [".claude-plugin", "agents", "commands", "skills"]
missing_dirs = []

for dir_name in required_dirs:
    result = Glob(pattern=dir_name, path="/bundle/path")
    if len(result) == 0:
        missing_dirs.append(dir_name)

all_present = len(missing_dirs) == 0
```

## Pattern 3: Content Search

Use **Grep** tool for all content searching operations.

### Search for pattern in files

```
# Search for pattern with line numbers
Grep(
    pattern="search_term",
    path="/path/to/file",
    output_mode="content",
    -n=true
)

# Returns: Lines containing pattern with line numbers
# Format: "filename:42:matching line content"
```

### Find files containing pattern

```
# Find which files contain pattern (don't show matches)
Grep(
    pattern="search_term",
    path="/path/to/directory",
    output_mode="files_with_matches"
)

# Returns: ["/path/to/directory/file1.md", "/path/to/directory/file2.md"]
```

### Count matches

```
# Search and count occurrences
Grep(
    pattern="search_term",
    path="/path",
    output_mode="count"
)

# Returns: Count of matches per file
```

### Case-insensitive search

```
# Search ignoring case
Grep(
    pattern="search_term",
    path="/path",
    output_mode="content",
    -i=true
)
```

### Search with context lines

```
# Show lines before and after match
Grep(
    pattern="search_term",
    path="/path",
    output_mode="content",
    -C=3  # 3 lines before and after
)
```

### Multi-pattern search (regex)

```
# Search for multiple patterns using regex
Grep(
    pattern="pattern1|pattern2|pattern3",
    path="/path",
    output_mode="content"
)
```

### Filter by file type

```
# Search only in specific file types
Grep(
    pattern="search_term",
    path="/path",
    glob="*.md",  # Only search .md files
    output_mode="content"
)
```

## Pattern 4: File Reading

Use **Read** tool for all file reading operations.

### Read entire file

```
# Read complete file content
content = Read(file_path="/path/to/file")
```

### Read with line limits

```
# Read first 100 lines
content = Read(file_path="/path/to/file", limit=100)

# Read lines 50-150
content = Read(file_path="/path/to/file", offset=50, limit=100)
```

### Read and parse

```
# Read and parse JSON
content = Read(file_path="/path/to/file.json")
import json
data = json.loads(content)

# Read and parse YAML frontmatter
content = Read(file_path="/path/to/file.md")
if content.startswith("---"):
    # Extract and parse YAML
    yaml_end = content.find("---", 3)
    yaml_content = content[3:yaml_end]
```

## Pattern 5: Combining Patterns

### Discover and validate

```
# Find all agents and validate each
agents = Glob(pattern="*.md", path="/bundle/agents")

for agent_path in agents:
    # Read and validate
    try:
        content = Read(file_path=agent_path)
        # Validate content
        if content.startswith("---"):
            valid = True
    except:
        valid = False
```

### Search and analyze

```
# Find files, search content, analyze results
files = Glob(pattern="*.md", path="/path")

for file_path in files:
    # Search for specific patterns
    matches = Grep(
        pattern="Skill:|tools:",
        path=file_path,
        output_mode="content",
        -n=true
    )
    # Analyze matches
    analyze_tool_usage(matches)
```

### Recursive validation

```
# Check structure recursively
def validate_bundle(bundle_path):
    # Check directories
    dirs = ["agents", "commands", "skills"]
    for dir_name in dirs:
        result = Glob(pattern=dir_name, path=bundle_path)
        if not result:
            return False

    # Check files in each directory
    agents = Glob(pattern="*.md", path=f"{bundle_path}/agents")
    for agent in agents:
        content = Read(file_path=agent)
        if not validate_agent(content):
            return False

    return True
```

## Common Pitfalls to Avoid

### ❌ Don't Use Bash for File Operations

```
# BAD - Triggers prompts
Bash(command="find /path -name '*.md'")
Bash(command="test -f /path/file")
Bash(command="ls -la /path")
Bash(command="grep pattern /path/file")
```

### ❌ Don't Chain Bash Commands

```
# BAD - Triggers multiple prompts
Bash(command="find /path -name '*.md' | wc -l")
```

### ❌ Don't Use Bash for Conditional Checks

```
# BAD - Triggers prompts
Bash(command="test -d /path && echo 'exists' || echo 'missing'")
```

### ✅ Use Non-Prompting Tools

```
# GOOD - No prompts
files = Glob(pattern="*.md", path="/path")
file_count = len(files)
```

## Performance Considerations

### Glob is Fast
- Efficient file system scanning
- Returns results immediately
- Can filter by pattern

### Read is Efficient
- Loads file once
- Can limit lines read
- Use for existence check + content

### Grep is Optimized
- Fast pattern matching
- Can filter by file type
- Returns structured results

### Combine for Efficiency

```
# EFFICIENT: Glob once, then Read only needed files
all_files = Glob(pattern="*.md", path="/path")
files_with_issues = []

for file_path in all_files:
    content = Read(file_path=file_path)
    if has_issue(content):
        files_with_issues.append(file_path)
```

## Summary

**Golden Rule**: If the operation involves the file system, use Glob/Read/Grep, never Bash.

**Quick Reference**:
- File discovery → `Glob`
- File exists → `Read` + try/except or `Glob`
- Directory exists → `Glob`
- Content search → `Grep`
- Read content → `Read`
- Count/list → `Glob` + len()

**Result**: Zero user prompts, fully automated diagnostics.
