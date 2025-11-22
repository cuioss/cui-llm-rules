---
name: plugin-architecture
description: Architecture principles, skill patterns, and design guidance for building goal-based Claude Code marketplace components
allowed-tools:
  - Read
---

# Plugin Architecture Skill

Pure reference skill providing architecture principles, skill patterns, and design guidance for building goal-based Claude Code marketplace components.

## What This Skill Provides

**Architecture Foundation**: Core principles for building marketplace components that follow Claude Skills best practices and goal-based organization.

**Skill Patterns**: 10 implementation patterns for building different types of skills (automation, analysis, validation, etc.).

**Design Guidance**: Workflow-focused skill design, thin orchestrator commands, and proper resource organization.

## Pattern Type

**Pattern 10: Reference Library** - Pure reference skill with no execution logic. Load references on-demand based on current task.

## When to Use This Skill

Activate when:
- **Creating new marketplace components** - Agents, commands, skills, or bundles
- **Refactoring existing components** - Migrating to goal-based architecture
- **Reviewing component design** - Ensuring architecture compliance
- **Learning marketplace architecture** - Understanding principles and patterns

## Core Concepts

### Goal-Based Organization

**Principle**: Organize by WHAT users want to accomplish (goals), not by WHAT component operates on (types).

**User Goals**:
- **CREATE** - Create new marketplace components
- **DIAGNOSE** - Find and understand issues
- **FIX** - Fix identified issues
- **MAINTAIN** - Keep marketplace healthy
- **LEARN** - Understand architecture and patterns

### Progressive Disclosure

**Principle**: Minimize initial context load, load details on-demand.

**Levels**:
1. **Frontmatter** - Minimal metadata (~3 lines)
2. **SKILL.md** - Full instructions (~400-800 lines)
3. **References** - Detailed content (thousands of lines, loaded when needed)

### {baseDir} Pattern

**Principle**: All resource paths use `{baseDir}` for portability across installations.

**Examples**:
```
Read {baseDir}/references/core-principles.md
bash {baseDir}/scripts/analyzer.py
Load template: {baseDir}/assets/template.html
```

## Available References

Load references progressively based on current task. **Never load all references at once.**

### 1. Core Principles (NEW - Essential Foundation)
**File**: `references/core-principles.md`

**Load When**:
- Starting any marketplace component development
- Learning Claude Skills fundamentals
- Understanding {baseDir} pattern
- Reviewing progressive disclosure strategy

**Contents**:
- Skills as prompt modifiers
- {baseDir} pattern for portability
- Progressive disclosure strategy
- Resource organization (scripts/, references/, assets/)
- Tool permissions scoping
- Imperative language guidelines
- Scripts for deterministic logic
- Anti-patterns to avoid

**Load Command**:
```
Read {baseDir}/references/core-principles.md
```

### 2. Skill Patterns (NEW - Implementation Patterns)
**File**: `references/skill-patterns.md`

**Load When**:
- Designing a new skill
- Choosing implementation pattern
- Understanding skill composition
- Learning pattern combinations

**Contents**:
- Pattern 1: Script Automation
- Pattern 2: Read-Process-Write
- Pattern 3: Search-Analyze-Report
- Pattern 4: Command Chain Execution
- Pattern 5: Wizard-Style Workflow
- Pattern 6: Template-Based Generation
- Pattern 7: Iterative Refinement
- Pattern 8: Context Aggregation
- Pattern 9: Validation Pipeline
- Pattern 10: Reference Library
- Decision guide for choosing patterns
- Pattern combination strategies

**Load Command**:
```
Read {baseDir}/references/skill-patterns.md
```

### 3. Goal-Based Organization (NEW - Architecture Paradigm)
**File**: `references/goal-based-organization.md`

**Load When**:
- Understanding goal-based vs component-centric
- Migrating from component-centric architecture
- Designing goal-based commands
- Learning context optimization strategies

**Contents**:
- Goal-centric vs component-centric comparison
- User goals: CREATE, DIAGNOSE, FIX, MAINTAIN, LEARN
- Benefits of goal-based structure
- Migration from component-centric
- Progressive disclosure in action
- Context reduction strategies

**Load Command**:
```
Read {baseDir}/references/goal-based-organization.md
```

### 4. Architecture Rules (Core Requirements)
**File**: `references/architecture-rules.md`

**Load When**:
- Validating component compliance
- Understanding self-containment requirements
- Learning reference pattern rules
- Implementing progressive disclosure

**Contents**:
- Rule 1: Skills must be self-contained
- Rule 2: Components must use skills (not direct file access)
- Rule 3: Reference categorization (internal, external, skill)
- Rule 4: Progressive disclosure requirement
- Rule 5: Goal-based organization requirement
- {baseDir} pattern requirements
- Validation criteria

**Load Command**:
```
Read {baseDir}/references/architecture-rules.md
```

### 5. Skill Design (Workflow-Focused)
**File**: `references/skill-design.md`

**Load When**:
- Designing skill workflows
- Creating multi-workflow skills
- Understanding workflow parameters
- Learning skill composition patterns

**Contents**:
- Workflow-focused design principles
- Multi-workflow vs single-workflow skills
- Workflow parameter design
- Conditional workflow selection
- Workflow composition patterns
- Quality standards for workflows

**Load Command**:
```
Read {baseDir}/references/skill-design.md
```

### 6. Command Design (Thin Orchestrators)
**File**: `references/command-design.md`

**Load When**:
- Creating new commands
- Designing parameter parsing
- Routing to skill workflows
- Learning user interaction patterns

**Contents**:
- Thin orchestrator pattern
- Parameter parsing strategies
- Routing to skill workflows
- Goal-based command structure
- User interaction patterns
- Command quality standards

**Load Command**:
```
Read {baseDir}/references/command-design.md
```

### 7. Token Optimization (Context Management)
**File**: `references/token-optimization.md`

**Load When**:
- Optimizing context usage
- Designing batch processing
- Implementing large-scale workflows
- Reducing token consumption

**Contents**:
- Pre-loading shared content
- Batched processing strategies
- Streamlined output formats
- Context budgeting
- Progressive disclosure for token reduction
- Pattern 7 (Iterative Refinement) for large codebases

**Load Command**:
```
Read {baseDir}/references/token-optimization.md
```

### 8. Reference Patterns ({baseDir} Usage)
**File**: `references/reference-patterns.md`

**Load When**:
- Understanding allowed reference types
- Implementing {baseDir} pattern
- Validating reference compliance
- Testing portability

**Contents**:
- Pattern 1: {baseDir}/references/ for documentation
- Pattern 2: {baseDir}/scripts/ for automation
- Pattern 3: {baseDir}/assets/ for templates
- Pattern 4: External URLs (allowed)
- Pattern 5: Skill dependencies (Skill:)
- Portability testing guidance
- Prohibited patterns

**Load Command**:
```
Read {baseDir}/references/reference-patterns.md
```

### 9. Frontmatter Standards (Component Metadata)
**File**: `references/frontmatter-standards.md`

**Load When**:
- Creating component YAML frontmatter
- Validating frontmatter fields
- Understanding required vs optional fields

**Contents**:
- Required frontmatter fields
- Optional frontmatter fields
- Field format specifications
- Validation rules
- Examples for agents, commands, skills

**Load Command**:
```
Read {baseDir}/references/frontmatter-standards.md
```

### 10. Script Standards (Executable Automation)
**File**: `references/script-standards.md`

**Load When**:
- Creating new scripts (Python/Bash)
- Documenting scripts in SKILL.md
- Writing script tests
- Understanding stdlib-only requirements
- Implementing JSON output format

**Contents**:
- Script location (`{skill-dir}/scripts/`)
- Documentation requirements in SKILL.md
- Test file requirements and structure
- Help output requirements (`--help` flag)
- Stdlib-only requirement (Python/Bash)
- JSON output format
- Executable permissions and shebang
- Error handling patterns
- Common issues and fixes
- Script quality checklist

**Load Command**:
```
Read {baseDir}/references/script-standards.md
```

## Examples

### Example 1: Goal-Based Skill
**File**: `references/examples/goal-based-skill-example.md`

**Load When**:
- Learning goal-based skill structure
- Understanding workflow organization
- Seeing progressive disclosure in practice

**Shows**:
- plugin-diagnose skill structure
- 5 workflows for different diagnostic goals
- Progressive disclosure demonstration
- {baseDir} usage throughout
- Script contracts (JSON output)
- Reference loading patterns

**Load Command**:
```
Read {baseDir}/references/examples/goal-based-skill-example.md
```

### Example 2: Thin Orchestrator Command
**File**: `references/examples/workflow-command-example.md`

**Load When**:
- Learning command design patterns
- Understanding parameter parsing
- Seeing skill invocation in practice

**Shows**:
- diagnose command structure
- Parameter parsing logic
- Scope determination
- Skill invocation with workflow selection
- User interaction patterns

**Load Command**:
```
Read {baseDir}/references/examples/workflow-command-example.md
```

### Example 3: Pattern Usage
**File**: `references/examples/pattern-usage-examples.md`

**Load When**:
- Applying skill patterns to real scenarios
- Understanding pattern combinations
- Learning when to use which pattern

**Shows**:
- Each of 10 patterns applied to marketplace scenarios
- Pattern combinations (e.g., Pattern 5 + Pattern 6)
- When to use which pattern
- Anti-pattern examples

**Load Command**:
```
Read {baseDir}/references/examples/pattern-usage-examples.md
```

## Usage Workflow

### Step 1: Identify Your Goal

Determine what you're trying to accomplish:
- **Creating component** → Load core-principles.md, skill-patterns.md
- **Understanding architecture** → Load goal-based-organization.md, architecture-rules.md
- **Designing skill** → Load skill-design.md, skill-patterns.md
- **Designing command** → Load command-design.md
- **Optimizing context** → Load token-optimization.md
- **Validating compliance** → Load architecture-rules.md, reference-patterns.md

### Step 2: Load Relevant References

**Never load all references** - Load only what's needed for current task.

**Example**:
```
# Creating a new skill
Read {baseDir}/references/core-principles.md
Read {baseDir}/references/skill-patterns.md
Read {baseDir}/references/skill-design.md
```

### Step 3: Apply Principles

Follow the guidance in loaded references:
- Use {baseDir} for all resource paths
- Implement progressive disclosure
- Choose appropriate skill pattern
- Follow architecture rules
- Optimize token usage

### Step 4: Validate Compliance

Ensure component follows architecture requirements:
- Self-contained (no external file references)
- Uses {baseDir} pattern
- Implements progressive disclosure
- Follows chosen skill pattern
- Meets quality standards

## Integration with Other Skills

### Plugin-Create Skill
When creating components, this skill provides:
- Architecture principles for templates
- Frontmatter standards
- Validation rules

### Plugin-Diagnose Skill
When analyzing components, this skill provides:
- Quality standards for validation
- Architecture rules for compliance checking
- Reference patterns for validation

### Plugin-Fix Skill
When fixing components, this skill provides:
- Architecture rules for fix guidance
- Reference patterns for corrections
- Compliance criteria

## Quick Reference Guide

### When to Load What

**Starting any work**:
```
Read {baseDir}/references/core-principles.md
```

**Creating skill**:
```
Read {baseDir}/references/skill-patterns.md
Read {baseDir}/references/skill-design.md
```

**Creating command**:
```
Read {baseDir}/references/command-design.md
```

**Understanding architecture**:
```
Read {baseDir}/references/goal-based-organization.md
Read {baseDir}/references/architecture-rules.md
```

**Optimizing performance**:
```
Read {baseDir}/references/token-optimization.md
```

**Validating compliance**:
```
Read {baseDir}/references/architecture-rules.md
Read {baseDir}/references/reference-patterns.md
```

**Creating scripts**:
```
Read {baseDir}/references/script-standards.md
```

**Learning by example**:
```
Read {baseDir}/references/examples/goal-based-skill-example.md
Read {baseDir}/references/examples/workflow-command-example.md
```

## Key Principles Summary

### 1. Goal-Based Organization
Organize by user goals (CREATE, DIAGNOSE, FIX, MAINTAIN, LEARN), not component types.

### 2. Progressive Disclosure
Minimize upfront information, load details on-demand.

### 3. {baseDir} Pattern
Always use `{baseDir}` for resource paths - never hardcode paths.

### 4. Self-Containment
Skills contain all content within their directory structure.

### 5. Pattern-Driven Design
Choose from 10 patterns based on skill purpose and complexity.

### 6. Workflow-Focused
Skills provide workflows, not monolithic operations.

### 7. Thin Orchestrators
Commands parse parameters and route to skill workflows.

### 8. Token Optimization
Pre-load shared content, use batching, streamline output.

### 9. Quality Standards
Follow architecture rules, validate compliance.

### 10. Composition
Build complex capabilities from simple, focused skills.

## Quality Verification

Components using this skill should demonstrate:
- [ ] Self-contained (no external file references)
- [ ] {baseDir} pattern used throughout
- [ ] Progressive disclosure implemented
- [ ] Appropriate skill pattern chosen
- [ ] Goal-based organization followed
- [ ] Architecture rules compliance
- [ ] Token optimization applied
- [ ] Quality standards met

## References

### Source Materials
- Claude Skills Deep Dive: https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/
- Claude Code Plugin Documentation: https://docs.claude.com/en/docs/claude-code/plugins

### Related Skills
- cui-utilities:cui-general-development-rules - Core development principles
- cui-utilities:cui-diagnostic-patterns - Tool usage patterns

### Internal References (Load On-Demand)
All references are in `references/` directory:
- core-principles.md
- skill-patterns.md
- goal-based-organization.md
- architecture-rules.md
- skill-design.md
- command-design.md
- token-optimization.md
- reference-patterns.md
- frontmatter-standards.md
- script-standards.md
- examples/goal-based-skill-example.md
- examples/workflow-command-example.md
- examples/pattern-usage-examples.md

---

## Non-Prompting Requirements

This skill is designed to run without user prompts. Required permissions:

**File Operations:**
- `Read({baseDir}/references/**)` - Read reference documentation

**Ensuring Non-Prompting:**
- All file reads use `{baseDir}/references/` which resolves to skill's mounted path
- Pure reference skill with no writes or executions
- Only the Read tool is used (no prompting scenarios)

---

*This is a Pattern 10 (Reference Library) skill - pure documentation with no execution logic. All content is loaded progressively based on current needs.*
