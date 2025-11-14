# Skill Usage Patterns

How agents and commands should properly use skills for standards access.

## Correct Pattern

### Agent with Skill Usage

```yaml
---
name: code-reviewer-agent
description: Reviews code for standards compliance
tools: Read, Edit, Write, Bash, Skill
---

# Code Reviewer Agent

## Step 1: Activate Required Skills

**CRITICAL**: Load standards before reviewing code.

```
Skill: cui-java-core
Skill: cui-javadoc
```

Skills load comprehensive standards into context.

## Step 2: Review Code

Apply patterns from loaded skills:
- Java core patterns (from cui-java-core)
- JavaDoc standards (from cui-javadoc)
- Null safety rules (from cui-java-core)

## Step 3: Report Violations

[Use loaded standards to identify violations]
```

**Key Elements**:
1. `Skill` in tools list
2. `Skill:` invocations in workflow
3. No direct file references
4. Skills loaded before use

## Detection Algorithm

### Step 1: Determine if Agent Uses Standards

```bash
# Look for standards-related keywords
if grep -qi "standard\|pattern\|guideline\|best practice\|compliance" agent.md; then
  echo "Agent uses standards - verify Skill usage"
else
  echo "Agent doesn't use standards - N/A"
fi
```

### Step 2: Verify Skill Usage (if applicable)

```bash
# Check for Skill in tools
if grep -q "tools:.*Skill" agent.md; then
  echo "✅ Has Skill in tools"
else
  echo "❌ Missing Skill in tools"
fi

# Check for Skill invocations
if grep -q "^Skill:" agent.md; then
  echo "✅ Invokes skills in workflow"
else
  echo "❌ No skill invocations found"
fi

# Check for direct file references (bad)
if grep -q "Read: ~/\|Read: \.\./\.\./\.\." agent.md; then
  echo "❌ Direct file references found"
fi
```

## Scoring

See **scoring-criteria.md** for the complete Agent Skill Usage Score formula, deductions, and thresholds.

## Common Patterns

### Pattern 1: Java Development Agent

```yaml
tools: Read, Edit, Write, Bash, Skill
```

```
Step 1: Activate Java Standards
Skill: cui-java-core
Skill: cui-java-unit-testing

Step 2: Implement Feature
[Use standards from skills]
```

**Skills Loaded**:
- cui-java-core → Java patterns, null safety, Lombok, logging
- cui-java-unit-testing → JUnit 5, generators, value object testing

### Pattern 2: Documentation Agent

```yaml
tools: Read, Edit, Bash, Glob, Skill
```

```
Step 1: Load Documentation Standards
Skill: cui-documentation

Step 2: Review Documentation
[Apply standards from skill]
```

**Skills Loaded**:
- cui-documentation → AsciiDoc, README, technical docs

### Pattern 3: Multi-Skill Agent

```yaml
tools: Read, Edit, Write, Bash, Skill
```

```
Step 0: Activate Required Skills

IF implementing Java code:
  Skill: cui-java-core
  Skill: cui-java-unit-testing
  Skill: cui-javadoc

Step 1: Analyze Task
[...]

Step 2: Implement
[Use standards from all loaded skills]
```

**Conditional Loading**: Agent adapts based on context

### Pattern 4: Simple Utility Agent (No Skills)

```yaml
tools: Read, Edit, Write, Bash
```

```
Step 1: Perform Utility Task
[No standards needed - simple utility]
```

**Valid Pattern**: Not all agents need skills (utilities, simple tasks)

## Violation Patterns

### Violation 1: Direct File Reference

❌ **INCORRECT**:
```
Step 1: Load Standards
Read: ~/git/cui-llm-rules/standards/java-core.adoc
```

✅ **CORRECT**:
```
Step 1: Activate Standards
Skill: cui-java-core
```

**Why Wrong**:
- Hard-codes file path
- Breaks when file moves
- Bypasses skill logic
- Not portable

### Violation 2: Missing Skill in Tools

❌ **INCORRECT**:
```yaml
tools: Read, Edit, Write
```
```
Skill: cui-java-core  ← ERROR: Skill not in tools
```

✅ **CORRECT**:
```yaml
tools: Read, Edit, Write, Skill
```
```
Skill: cui-java-core  ← OK
```

### Violation 3: Skill in Tools but Unused

❌ **INCORRECT**:
```yaml
tools: Read, Edit, Write, Skill
```
```
[No Skill: invocations anywhere in workflow]
```

✅ **CORRECT**:
```yaml
tools: Read, Edit, Write, Skill
```
```
Step 1: Activate Standards
Skill: cui-java-core
```

**Or remove Skill from tools if not needed**

## Fix Recommendations

### Fix 1: Add Skill to Tools

**Before**:
```yaml
tools: Read, Edit, Write
```

**After**:
```yaml
tools: Read, Edit, Write, Skill
```

### Fix 2: Replace Direct Reference with Skill

**Before**:
```
Read: ~/git/cui-llm-rules/standards/java-core.adoc
```

**After**:
```
Skill: cui-java-core
```

**Steps**:
1. Identify which skill contains the content
2. Add Skill to tools if missing
3. Replace Read: with Skill: invocation
4. Remove direct file reference

### Fix 3: Remove Unused Skill from Tools

**Before**:
```yaml
tools: Read, Edit, Write, Skill
```
(but no Skill: invocations)

**After**:
```yaml
tools: Read, Edit, Write
```

**When to Apply**: Agent doesn't actually use skills

## Integration with Tool Fit Score

The skill usage pattern affects the agent's Tool Fit score:

```
Tool Fit Score includes:
- Tool coverage: Are all tools in list used?
- Tool necessity: Are all used tools in list?
- Skill usage (if applicable): Is Skill used correctly?

IF agent uses standards:
  Deduct from Tool Fit if:
  - Missing Skill in tools: -15 points
  - Direct file refs instead of Skill: -20 points
  - Skill in tools but unused: -5 points
```

## Diagnostic Integration

This pattern validation is integrated into:

- **/plugin-diagnose-agents**: Checks skill usage for each agent
- **/plugin-diagnose-bundle**: Aggregates agent scores
- **/plugin-create-agent**: Guides proper skill usage at creation

All commands invoke `Skill: cui-marketplace-architecture` to load these usage patterns.
