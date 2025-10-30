# Agent Quality Standards

Quality standards and best practices for Claude Code agents.

## Agent Best Practices

A well-formed agent must follow these 9 core practices:

### 1. Tool Coverage
- Agent must have access to ALL tools required for its stated task
- Missing critical tools → Agent cannot complete its job
- Tool Fit Score should be **≥ 90%** (excellent), minimum **75%** (acceptable)

### 2. Autonomy
- Agent should be able to complete tasks independently
- Clear workflow with concrete steps
- No ambiguous instructions requiring user clarification

### 3. Clear Communication
- Description clearly states what agent does and when to use it
- Response format specified if agent produces output
- User knows what to expect

### 4. Appropriate Scope
- Agent focuses on specific, well-defined task
- Not too broad (Swiss Army knife)
- Not too narrow (single tool call)

### 5. Essential Rules Format
- If agent has essential rules, follow format:
  ```markdown
  ## Essential Rules
  - Rule 1
  - Rule 2
  ```
- Rules must be sourced from authoritative documents
- No orphaned rules (rules without source references)

### 6. Maven/Build Context
- For Maven/build agents: Use `target/` for temp files
- NEVER use `/tmp` (violates project context principle)
- Keep all generated artifacts in project structure

### 7. Permission Patterns
- All Bash commands requiring approval must be in permissions list
- No over-permissions (approved patterns not used)
- No stale patterns (outdated/redundant approvals)

### 8. No Absolute Paths
- No hardcoded paths like `/Users/`, `/home/`, `~/specific-project/`
- Use relative paths or environment variables
- Agent must be portable across systems

### 9. Architecture Compliance
- Self-contained (no external file references)
- No documentation-only noise
- Follows marketplace architecture rules

## YAML Frontmatter Standards

### Required Fields

```yaml
---
name: agent-name              # Unique identifier (lowercase, hyphens, max 64 chars)
description: Clear description # What agent does and when to use it (50-200 chars recommended, max 1024)
tools: [Read, Write, Edit, Bash, Grep, Glob, Task]  # Required tools
---
```

### Optional Fields

```yaml
model: haiku                  # Model to use (sonnet, opus, haiku)
color: blue                   # Color for UI display
```

### Common Mistakes

- ❌ Using `allowed-tools` instead of `tools` (agents use `tools`, skills use `allowed-tools`)
- ❌ Missing `---` delimiters
- ❌ Using tabs instead of spaces in YAML
- ❌ Empty or very short descriptions
- ❌ Descriptions exceeding 1024 characters
- ❌ Names with spaces or uppercase letters
- ❌ Listing tools not actually used in agent

## Tool Coverage Analysis

### Tool Fit Score Calculation

```
Tool Fit Score = (tools_used / tools_listed) * 100

- 90-100%: Excellent - Agent uses all tools it has
- 75-89%: Good - Minor over-permissions
- 60-74%: Fair - Some unused tools
- Below 60%: Poor - Significant over-permissions
```

### Required Tools by Task Type

**File Reading Tasks:**
- Read (required)
- Grep (recommended for search)
- Glob (recommended for discovery)

**File Modification Tasks:**
- Read (required - must read before editing)
- Edit or Write (required)
- Glob (recommended for discovery)

**Code Execution Tasks:**
- Bash (required)
- Read (recommended for verifying scripts)

**Multi-Step Orchestration:**
- Task (required to launch sub-agents)
- Read (recommended for context)

**Research/Analysis:**
- WebSearch or WebFetch (required)
- Read (recommended for analysis)

## Agent Complexity Scoring

**Low Complexity** (< 100 lines):
- Single focused task
- Linear workflow
- Minimal branching

**Medium Complexity** (100-300 lines):
- Multi-step workflow
- Some conditional logic
- Moderate branching

**High Complexity** (> 300 lines):
- Complex multi-phase workflow
- Significant conditional logic
- **Consider splitting into multiple agents**

## Content Quality Requirements

### No Duplication
- Avoid repeating information across sections
- Use cross-references instead of duplicating

### No Ambiguity
- Use specific, measurable criteria
- Avoid vague terms: "some", "many", "when appropriate"
- Replace with: "< 50 lines", ">= 80% coverage", "for all X"

### High Precision
- Clear, actionable instructions
- Specific examples
- Measurable success criteria

**Precision Score Calculation:**
```
Precision Score = 100 - (ambiguous_statements * 10)

- 90-100%: Excellent - Highly precise
- 75-89%: Good - Minor ambiguities
- 60-74%: Fair - Moderate ambiguities
- Below 60%: Poor - Too vague
```

## Essential Rules Synchronization

If agent has "Essential Rules" section:

1. **Format Requirement:**
   ```markdown
   ## Essential Rules
   - Rule 1 (from: source-document.md)
   - Rule 2 (from: source-document.md)
   ```

2. **Source Tracking:**
   - Each rule must reference source document
   - Use `(from: path/to/document.md)` suffix
   - Enables automatic synchronization

3. **Sync Status:**
   - ✅ **In Sync**: Rule matches source exactly
   - ⚠️ **Out of Date**: Source changed, rule needs update
   - ❌ **Orphaned**: Source not found or no source specified
   - ⚠️ **Old Sync**: Rule has outdated sync metadata

4. **Auto-Fix:**
   - Update out-of-date rules from source
   - Remove orphaned rules or add source attribution
   - Update sync metadata

## Permission Patterns Validation

Agents may include permission patterns for Bash commands:

```yaml
tools: [Bash(git:*), Bash(npm:*), Bash(mvn:*)]
```

### Validation Rules:

1. **Missing Approvals** (CRITICAL):
   - Agent uses Bash command not in permission list
   - Fix: Add pattern to tools list

2. **Over-Permissions** (WARNING):
   - Approved pattern not used by agent
   - Fix: Remove unused pattern

3. **Stale Patterns** (WARNING):
   - Outdated or redundant patterns
   - Fix: Update or consolidate

## Directory Structure Standards

```
agent-name.md                  # Single file agent (required)
```

Agents are always single files, not directories.

## Industry Best Practices Compliance

Checklist of industry standards:

- [ ] Single Responsibility - Agent does one thing well
- [ ] Clear Interface - Description and response format well-defined
- [ ] Error Handling - Agent handles failures gracefully
- [ ] Idempotency - Can be run multiple times safely
- [ ] Observable - Provides clear progress indicators
- [ ] Testable - Can be verified for correctness
- [ ] Maintainable - Clear structure, well-documented
- [ ] Portable - No hardcoded paths or system dependencies
- [ ] Secure - Appropriate permissions, no unnecessary tool access

**Compliance Score:**
```
Compliance Score = (practices_followed / 9) * 100

- 90-100%: Excellent
- 75-89%: Good
- 60-74%: Fair
- Below 60%: Poor
```

## Quality Thresholds

**Overall Agent Quality:**
- Tool Fit Score ≥ 90%
- Precision Score ≥ 90%
- Compliance Score ≥ 90%
- Zero critical issues
- Zero orphaned rules
- Zero absolute paths
- Zero permission violations

**Minimum Acceptable:**
- Tool Fit Score ≥ 75%
- Precision Score ≥ 75%
- Compliance Score ≥ 75%
- No critical structural issues
