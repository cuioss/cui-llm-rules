# Marketplace Architecture Rules

Core architectural principles for Claude Code marketplace components.

## Rule 1: Skills Must Be Self-Contained

All skills must contain ALL content within their own directory structure.

**Rationale**: Skills may be distributed independently, installed globally, or bundled. External dependencies break portability and marketplace distribution.

**Requirements**:
- All standards content in `skill-name/standards/` subdirectory
- All `Read:` statements in SKILL.md point to internal files only
- No references escaping skill directory (`../../../`)
- No absolute paths (`~/git/cui-llm-rules/`)
- External references only via URLs or `Skill:` invocations

**Examples**:

✅ CORRECT:
```
Read: standards/java-core-patterns.md
Read: standards/logging-standards.md
Skill: cui-java-unit-testing
```

❌ INCORRECT:
```
Read: ../../../../standards/java/java-core.adoc
Read: ~/git/cui-llm-rules/standards/logging.adoc
```

**Validation**: See `self-containment-validation.md` for comprehensive validation commands

**Impact of Violation**:
- Skill cannot be distributed independently
- Breaks when skill installed outside cui-llm-rules repo
- Fails in global skill installation
- Breaks marketplace distribution

## Rule 2: Agents Must Use Skills

Agents requiring standards must invoke Skills via the Skill tool, not read files directly.

**Rationale**: Skills provide curated, versioned standards with conditional loading logic. Direct file access bypasses skill workflow, breaks abstraction layer, and couples agents to file structure.

**Requirements**:
- Include `Skill` in agent's tools list
- Invoke `Skill: cui-skill-name` in agent workflow
- No direct `Read:` of standards files from main repo
- Let skill handle conditional loading and standards selection

**Examples**:

✅ CORRECT:
```yaml
---
name: code-reviewer
tools: Read, Edit, Write, Skill
---

Step 1: Activate Required Standards
Skill: cui-java-core
Skill: cui-javadoc

Step 2: Review Code
Apply standards loaded from skills
```

❌ INCORRECT:
```
Step 1: Load Standards
Read: ~/git/cui-llm-rules/standards/java-core.adoc
Read: ~/git/cui-llm-rules/standards/javadoc.adoc
```

**Impact of Violation**:
- Bypasses skill conditional loading logic
- Hard-codes file paths in agent
- Breaks when standards reorganized
- Loses skill versioning benefits

## Rule 3: Reference Categorization

Only specific reference types allowed in skills and agents.

**Allowed References**:

1. **Internal files** (skills only):
   ```
   Read: standards/file.md
   ```
   - Must be relative path within skill directory
   - File must exist in skill's standards/
   - No `../` sequences

2. **External URLs** (all components):
   ```
   * Java Spec: https://docs.oracle.com/javase/specs/
   * Maven Guide: https://maven.apache.org/guides/
   ```
   - Must start with `https://` or `http://`
   - Publicly accessible documentation
   - Typically in ## References section

3. **Skill dependencies** (all components):
   ```
   Skill: cui-java-core
   Skill: cui-logging
   ```
   - Must use `Skill:` prefix
   - Must reference valid skill name
   - Skill must exist (marketplace, bundle, or global)

**Prohibited References**:

1. **Escape sequences**:
   ```
   ❌ Read: ../../../../standards/java/java-core.adoc
   ❌ * Guide: ../../../standards/requirements/guide.adoc
   ```
   - Breaks portability
   - Assumes specific directory structure
   - Fails when distributed

2. **Absolute paths**:
   ```
   ❌ Read: ~/git/cui-llm-rules/standards/java-core.adoc
   ❌ Source: /Users/oliver/git/cui-llm-rules/standards/logging.adoc
   ```
   - Machine-specific
   - User-specific
   - Not portable

3. **Cross-skill file access**:
   ```
   ❌ Read: ../cui-other-skill/standards/file.md
   ```
   - Should use `Skill: cui-other-skill` instead
   - Breaks skill encapsulation

## Rule 4: Bundle Architecture

Bundles must maintain clean architecture across all components.

**Requirements**:
- All skills in bundle are self-contained
- All agents in bundle use Skills properly (not direct refs)
- No inter-bundle file references
- Only external URLs for non-skill references
- Bundle follows functional cohesion principles

**Bundle Cohesion Principles**:
- Components serve common functional goal
- Components work together in workflow
- High coupling within bundle (components change together)
- Low coupling between bundles (independent evolution)

**Examples**:

✅ GOOD BUNDLE (cui-workflow):
- commit-changes (agent) → git commit utility for workflow
- task-executor (agent) → executes implementation tasks
- pr-quality-fixer (agent) → fixes quality issues
- High cohesion: all agents work together in development cycle

✅ GOOD BUNDLE (cui-utility-commands):
- research-best-practices (agent) → standalone research utility
- cui-diagnostic-patterns (skill) → self-contained diagnostic standards
- cui-setup-project-permissions (command) → standalone utility

✅ GOOD BUNDLE (cui-documentation-standards):
- asciidoc-reviewer (agent) → uses Skill: cui-documentation
- cui-documentation (skill) → self-contained
- cui-review-technical-docs (command) → orchestrates agent

❌ BAD BUNDLE:
- agent references ../../../../standards/external.adoc
- skill references files outside skill directory
- agent reads standards directly instead of using skill

**Validation**:
- Scan all skills for self-containment
- Scan all agents for skill usage
- Calculate bundle architecture score
- Report violations by component

## Rule 5: Component Organization

Components must be organized following the three-layer architecture.

**Layer 1: Skills** (Knowledge + Standards)
- Self-contained bundles with SKILL.md + standards/
- Read-only tools recommended (Read, Grep, Glob)
- Progressive loading via conditional logic
- May reference other skills

**Layer 2: Agents** (Task Executors)
- Autonomous task execution
- Invoke skills for standards
- Use Read, Edit, Write, Bash for implementation
- Embed essential rules for performance (optional)

**Layer 3: Commands** (User Utilities)
- User-invoked via /command-name
- Orchestrate agents and workflows
- Verification and diagnostic tools
- May invoke skills directly or via agents

**Cross-Layer Communication**:
- Agents invoke Skills (Layer 2 → Layer 1)
- Commands invoke Agents (Layer 3 → Layer 2)
- Commands invoke Skills (Layer 3 → Layer 1)
- Skills may reference Skills (Layer 1 → Layer 1)

**Prohibited**:
- Skills invoking Agents (Layer 1 should not → Layer 2)
- Agents invoking Commands (Layer 2 should not → Layer 3)

## Enforcement

These rules are enforced through:
- `/cui-create-skill` - Proactive prevention at creation
- `/cui-diagnose-skills` - Reactive detection in existing skills
- `/cui-diagnose-agents` - Check agent skill usage patterns
- `/cui-diagnose-bundle` - Overall bundle compliance

All diagnostic commands invoke this skill to apply consistent validation rules.
