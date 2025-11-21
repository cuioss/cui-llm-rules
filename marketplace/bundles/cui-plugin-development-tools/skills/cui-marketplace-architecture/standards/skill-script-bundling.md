# Skill Script Bundling Standards

Standards for bundling and executing scripts within Claude Code plugin skills using the `{baseDir}` pattern.

## Overview

Claude Code provides a `{baseDir}` variable mechanism that allows skills to reference bundled resources (scripts, templates, data files) in a portable way. This standard defines the correct patterns for script bundling and execution.

## The {baseDir} Variable

### What is {baseDir}?

When Claude Code loads a skill from a plugin bundle, it provides a `{baseDir}` variable in the skill's execution context. This variable resolves to the absolute path of the skill's directory.

**Example:**
- Skill location: `marketplace/bundles/cui-plugin-development-tools/skills/marketplace-inventory/`
- `{baseDir}` resolves to: `/Users/oliver/git/cui-llm-rules/marketplace/bundles/cui-plugin-development-tools/skills/marketplace-inventory`

### How {baseDir} Works

**Mechanism:**
- Simple variable substitution (not filesystem virtualization)
- Resolved at skill load time
- Provides absolute path to skill directory
- Same for user skills, project skills, and plugin skills

**Resolution Process:**
1. User invokes command or agent
2. Command/agent invokes skill: `Skill: bundle-name:skill-name`
3. Claude Code loads skill from bundle
4. Claude Code provides `{baseDir}` = absolute path to skill directory
5. Skill references resources: `{baseDir}/scripts/script-name.sh`
6. Variable substituted with actual path before execution

## Correct Pattern: Skills with Bundled Scripts

### Skill Structure

```
skills/
  my-skill/
    SKILL.md              # Skill definition
    scripts/              # Bundled scripts
      process-data.sh
      analyze.py
    templates/            # Optional: templates
      config.template
    data/                 # Optional: reference data
      lookup.json
```

### Skill Definition (SKILL.md)

**Pattern:**
```markdown
---
name: my-skill
description: Description of what the skill does
allowed-tools: Read, Bash, Glob
---

# My Skill

## Workflow

### Step 1: Execute Script

Run the bundled script:

bash {baseDir}/scripts/process-data.sh --param value

### Step 2: Process Results

The script outputs JSON/text that can be parsed and returned.
```

**{baseDir} resolves to:**
```bash
/full/absolute/path/to/marketplace/bundles/bundle-name/skills/my-skill
```

**Actual execution:**
```bash
bash /full/absolute/path/to/marketplace/bundles/bundle-name/skills/my-skill/scripts/process-data.sh --param value
```

### Commands/Agents Invoke Skills

**Command Pattern:**
```markdown
---
name: my-command
description: Command that uses the skill
---

# My Command

## Workflow

Invoke the skill that handles script execution:

Skill: bundle-name:my-skill

The skill executes and returns results.
```

**Agent Pattern:**
```markdown
---
name: my-agent
description: Agent that uses the skill

tools: Skill, Bash
model: sonnet
---

You are an agent that processes data using a skill.

## Workflow

Invoke the skill:

Skill: bundle-name:my-skill

Process and return the results.
```

**Key Points:**
- Commands/agents are thin wrappers
- They invoke skills, not scripts directly
- Skills encapsulate script execution
- Clean separation of concerns

## Tool Permission Requirements

### Skills

Skills declare required tools in `allowed-tools` frontmatter:

```yaml
---
name: my-skill
allowed-tools: Read, Bash, Glob
---
```

If skill executes bash scripts, must include `Bash` in allowed-tools.

### Commands

Commands have implicit access to all tools. No special configuration needed.

### Agents

Agents must explicitly declare tools in frontmatter:

```yaml
---
name: my-agent
tools: Skill, Bash
---
```

**Important:**
- If agent invokes skill that executes scripts, agent needs `Bash` in tools
- Skills don't grant tool permissions to callers
- Each component declares its own required tools

**Example:**
```yaml
# ✅ Correct - agent can invoke skill and execute bash
tools: Skill, Bash

# ❌ Wrong - agent can invoke skill but bash execution fails
tools: Skill
```

## Wrong Patterns (DO NOT USE)

### ❌ Pattern 1: Hardcoded .claude/skills Path

**WRONG:**
```bash
./.claude/skills/cui-marketplace-architecture/scripts/scan-marketplace-inventory.sh
```

**Why it's wrong:**
- `./.claude/skills/` directory doesn't exist
- Assumption based on misunderstanding of skill loading
- Not portable

**Reality:**
- No mounting or symlinks occur
- Skills remain in their original bundle location
- Use `{baseDir}` for portable references

### ❌ Pattern 2: Relative Path from Repo Root

**WRONG:**
```bash
marketplace/bundles/cui-plugin-development-tools/skills/cui-marketplace-architecture/scripts/scan-marketplace-inventory.sh
```

**Why it's wrong:**
- Not portable across different installations
- Assumes specific directory structure
- Breaks if bundle is moved or installed differently

**Better:**
- Use `{baseDir}` which resolves regardless of installation location

### ❌ Pattern 3: Commands Calling Scripts Directly

**WRONG:**
```markdown
# In COMMAND.md
Bash: marketplace/bundles/.../scripts/script.sh
```

**Why it's wrong:**
- Breaks encapsulation
- Commands reach into skill internals
- Violates separation of concerns
- Not maintainable

**Better:**
```markdown
# In COMMAND.md
Skill: bundle-name:skill-name
```

Let the skill handle script execution.

### ❌ Pattern 4: Absolute Paths

**WRONG:**
```bash
bash /Users/oliver/git/cui-llm-rules/marketplace/bundles/.../scripts/script.sh
```

**Why it's wrong:**
- Hardcoded to specific machine
- Completely non-portable
- Fails on different systems

**Better:**
- Use `{baseDir}` which resolves to correct absolute path for any installation

## Key Architectural Principles

### 1. No ./.claude/skills/ Mounting

**Misconception:** Plugin skills get mounted to `./.claude/skills/` directory

**Reality:**
- No mounting occurs
- No symlinks created
- `./.claude/skills/` directory doesn't exist (verify with `ls .claude/`)
- Skills remain in their original bundle location

**Proof:**
```bash
$ ls .claude/
run-configuration.md  settings.json  settings.local.json
# NO skills/ directory!
```

### 2. {baseDir} is Variable Substitution

**Mechanism:**
- Simple string replacement
- Not filesystem virtualization
- Resolved at skill load time
- Provides absolute path to skill directory

**Process:**
1. Skill loaded
2. `{baseDir}` variable provided by Claude Code
3. Variable replaced with actual path
4. Command executed with resolved path

### 3. Skills Bundle Resources

**Best Practice:**
```
skills/
  my-skill/
    SKILL.md
    scripts/       # Scripts bundled with skill
    templates/     # Templates bundled with skill
    data/          # Data files bundled with skill
```

**Benefits:**
- Self-contained skills
- Portable across installations
- Clear ownership of resources
- Easy to test and maintain

### 4. Skills Encapsulate Execution

**Architecture:**
```
Command/Agent (thin wrapper)
    ↓ invokes
Skill (execution logic)
    ↓ uses {baseDir}
Script (business logic)
```

**Benefits:**
- Clean separation of concerns
- Commands/agents are simple
- Skills handle complexity
- Easy to reuse skills

### 5. Portability via {baseDir}

**Portable Pattern:**
```markdown
# Works on any system, any installation
bash {baseDir}/scripts/script.sh
```

**Non-Portable Pattern:**
```bash
# Only works on one specific machine
bash /Users/oliver/git/cui-llm-rules/marketplace/bundles/.../scripts/script.sh
```

## Script Development Guidelines

### Script Location

Place scripts in `scripts/` subdirectory of skill:

```
skills/
  my-skill/
    SKILL.md
    scripts/
      script1.sh
      script2.py
```

### Script Permissions

Ensure scripts are executable:

```bash
chmod +x skills/my-skill/scripts/script1.sh
```

### Script Output

Scripts should output structured data (JSON, CSV, etc.) that skills can parse and return:

**Good:**
```bash
#!/bin/bash
echo '{"status": "success", "data": [...]}'
```

**Also Good:**
```python
#!/usr/bin/env python3
import json
result = {"status": "success", "data": [...]}
print(json.dumps(result))
```

### Script Parameters

Accept parameters via command line arguments:

```bash
bash {baseDir}/scripts/process-data.sh --input file.txt --format json
```

Script should parse arguments and handle errors:

```bash
#!/bin/bash
set -euo pipefail

INPUT=""
FORMAT="json"

while [[ $# -gt 0 ]]; do
  case $1 in
    --input) INPUT="$2"; shift 2 ;;
    --format) FORMAT="$2"; shift 2 ;;
    *) echo "Unknown parameter: $1" >&2; exit 1 ;;
  esac
done

# Process...
```

## Testing and Verification

### Verify {baseDir} Resolution

When skill loads, verify `{baseDir}` is provided:

```
Base directory for this skill: /full/path/to/skill
```

This confirms Claude Code is providing the variable.

### Test Script Execution

1. Invoke skill from command or agent
2. Verify script executes without errors
3. Verify output is returned correctly
4. Check that path resolution works

### Test Portability

Test that skill works:
1. From different working directories
2. When bundle is in different locations
3. On different systems (if possible)

Should work consistently because `{baseDir}` resolves correctly.

## Examples

### Example 1: Simple Data Processing Skill

**Skill Structure:**
```
skills/
  data-processor/
    SKILL.md
    scripts/
      process.sh
```

**SKILL.md:**
```markdown
---
name: data-processor
description: Processes data files and returns JSON
allowed-tools: Read, Bash
---

# Data Processor Skill

## Workflow

Execute the data processing script:

bash {baseDir}/scripts/process.sh --input {input_file} --format json

Return the JSON output.
```

**Command Using Skill:**
```markdown
---
name: process-data
description: Process data files
---

# Process Data Command

## Workflow

Skill: bundle-name:data-processor

Pass through the JSON results.
```

### Example 2: Multi-Script Analysis Skill

**Skill Structure:**
```
skills/
  analyzer/
    SKILL.md
    scripts/
      scan.sh
      analyze.py
      report.sh
```

**SKILL.md:**
```markdown
---
name: analyzer
description: Analyzes codebase and generates reports
allowed-tools: Read, Bash, Glob
---

# Analyzer Skill

## Workflow

### Step 1: Scan Codebase

bash {baseDir}/scripts/scan.sh --path {target_path}

### Step 2: Analyze Results

python3 {baseDir}/scripts/analyze.py --data scan_results.json

### Step 3: Generate Report

bash {baseDir}/scripts/report.sh --input analysis.json --format markdown

Return the markdown report.
```

## Migration Guide

### Migrating from Old Patterns

**Old Pattern (WRONG):**
```markdown
# In command.md
Bash: ./.claude/skills/cui-marketplace-architecture/scripts/scan-marketplace-inventory.sh
```

**New Pattern (CORRECT):**

1. Create skill if not exists:
```
skills/
  marketplace-architecture/
    SKILL.md
    scripts/
      scan-marketplace-inventory.sh
```

2. Update SKILL.md:
```markdown
bash {baseDir}/scripts/scan-marketplace-inventory.sh --scope marketplace
```

3. Update command:
```markdown
Skill: cui-plugin-development-tools:marketplace-architecture
```

### Verification After Migration

1. Restart Claude Code to reload plugin
2. Test command/agent invocation
3. Verify `{baseDir}` resolves correctly
4. Verify script executes and returns results
5. Check for any path-related errors

## References

* Claude Skills Deep Dive (baseDir pattern): https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/
* Claude Code Plugin System: https://docs.claude.com/en/docs/claude-code/plugins
* Script development: script-development.md
* Plugin specifications: plugin-specifications.md
