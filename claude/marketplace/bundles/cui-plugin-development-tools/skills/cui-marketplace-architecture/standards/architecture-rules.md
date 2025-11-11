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
- ✅ Commands CAN invoke other Commands (Layer 3 → Layer 3) via SlashCommand
- ✅ Commands CAN invoke Agents (Layer 3 → Layer 2) via Task
- ✅ Commands CAN invoke Skills (Layer 3 → Layer 1) via Skill
- ✅ Agents CAN invoke Skills (Layer 2 → Layer 1) via Skill
- ✅ Skills MAY reference other Skills (Layer 1 → Layer 1) via Skill

**Prohibited**:
- ❌ Skills CANNOT invoke Agents (Layer 1 → Layer 2) - breaks abstraction
- ❌ Skills CANNOT invoke Commands (Layer 1 → Layer 3) - breaks abstraction
- ❌ Agents CANNOT invoke Commands (Layer 2 → Layer 3) - SlashCommand unavailable
- ❌ Agents CANNOT invoke other Agents (Layer 2 → Layer 2) - Task tool unavailable at runtime

**Note**: The agent delegation constraint (agents cannot invoke other agents or commands) is a platform limitation, not a design choice. See Rule 6 for details.

## Rule 6: Agent Delegation Constraints

Agents CANNOT delegate to other agents or commands due to platform limitations.

**Platform Constraint**: The Claude Code platform intentionally restricts the Task tool from being available to sub-agents at runtime to prevent infinite nesting and control resource consumption. Similarly, the SlashCommand tool is unavailable to agents.

**Critical Rules**:
- ✅ Commands CAN invoke other commands (via SlashCommand tool)
- ✅ Commands CAN invoke agents (via Task tool)
- ❌ Agents CANNOT invoke other agents (Task tool unavailable at runtime)
- ❌ Agents CANNOT invoke commands (SlashCommand tool unavailable)
- ✅ Agents CAN use all other tools (Read, Write, Edit, Bash, Grep, Glob, Skill, etc.)
- 📋 Flow is unidirectional: command → command OR command → agent (NEVER agent → *)

**Agent Design Requirements**:
- Agents must be **focused executors** (do ONE specific task)
- NO verification workflows in agents (commands handle verification)
- NO commit/push logic in agents (commands handle commits)
- NO orchestration in agents (commands orchestrate)
- Return structured results to caller for decision making

**Command Design Requirements**:
- Commands orchestrate workflows (agent → verify → iterate)
- Commands delegate to other commands for complex operations
- Commands handle all verification and commit logic
- Commands make control flow decisions based on agent results

**Examples**:

✅ CORRECT - Focused Agent:
```yaml
---
name: java-code-implementer
tools: Read, Write, Edit, Grep, Glob, Skill
---

Step 1: Load Standards
Skill: cui-java-core

Step 2: Implement Code Changes
[Implementation logic]

Step 3: Return Result
Return structured result to caller (NO verification, NO commit)
```

✅ CORRECT - Orchestrating Command:
```markdown
---
name: java-implement-code
---

Step 1: Delegate Implementation
Task(java-code-implementer)

Step 2: Verify Implementation
Task(maven-builder)

Step 3: Analyze and Iterate
If errors: repeat Step 1-2 with fixes

Step 4: Return Result
Return success/failure to caller
```

❌ INCORRECT - Agent Attempting Orchestration:
```yaml
---
name: bad-agent
tools: Read, Write, Edit, Task  # Task in tools list
---

Step 1: Implement Changes
[Implementation logic]

Step 2: Verify Changes
Task(maven-builder)  # ❌ FAILS - Task unavailable at runtime

Step 3: Commit Changes
Task(commit-changes)  # ❌ FAILS - Task unavailable at runtime
```

**Detection**:
- Task tool in agent frontmatter tools list = potential violation
- Task(...) calls in agent workflow = guaranteed runtime failure
- Bash(./mvnw:*) in agent = anti-pattern (see Rule 7)

**Reference**: See `claude/architectural-issues/agent-nesting-limitation.md` for technical details and evidence sources

## Rule 7: Maven Execution Principle

Agents NEVER call Maven directly - commands orchestrate maven-builder agent for all build operations.

**Rationale**: Centralizing Maven execution in a dedicated agent (`maven-builder`) ensures consistent build configuration, output capture, error handling, and performance tracking across all workflows. Direct Maven calls bypass this centralization and duplicate logic.

**The Rule**:
- ❌ Agents calling `Bash(./mvnw:*)` = ALWAYS A BUG (except maven-builder)
- ✅ Commands orchestrate `Task(maven-builder)` for build/verify operations
- ✅ maven-builder agent is the ONLY agent allowed `Bash(./mvnw:*)` calls

**EXCEPTION**: The `maven-builder` agent IS allowed to use `Bash(./mvnw:*)` because it is the central build execution agent. All other agents must delegate to maven-builder instead.

**Why This Matters**:
- **Consistency**: All builds use same configuration, flags, and environment
- **Output Capture**: maven-builder captures output to timestamped files
- **Performance Tracking**: maven-builder tracks build times and metrics
- **Error Handling**: maven-builder provides structured error results
- **Reusability**: Build logic in one place, used by all commands
- **Testability**: Test build logic once, not in every agent

**Requirements**:

**For Agents** (except maven-builder):
- NO `Bash(./mvnw:*)` calls
- NO `Bash(mvn:*)` calls
- NO direct build execution
- Return results to caller who orchestrates verification

**For Commands**:
- Orchestrate `Task(maven-builder)` for builds
- Pass structured parameters to maven-builder
- Analyze maven-builder's structured results
- Make decisions based on build outcomes

**Examples**:

✅ CORRECT - Command Orchestrating Build:
```markdown
---
name: java-implement-code
---

Step 1: Implement Changes
Task(java-code-implementer)

Step 2: Verify with Maven
Task(maven-builder, goals="clean compile test")

Step 3: Analyze Results
If build failed: iterate with fixes
If build succeeded: return success
```

✅ CORRECT - maven-builder Agent (EXCEPTION):
```yaml
---
name: maven-builder
tools: Bash, Read, Write
---

Step 1: Execute Maven Build
Bash(./mvnw clean verify)  # ✅ ALLOWED - this is the central build agent

Step 2: Capture Output
Write output to target/build-output-{timestamp}.log

Step 3: Parse Results
Extract errors, warnings, test results

Step 4: Return Structured Results
{status, output_file, issues: [{type, file, line, message}]}
```

❌ INCORRECT - Agent Calling Maven Directly:
```yaml
---
name: java-code-implementer
tools: Read, Write, Edit, Bash
---

Step 1: Implement Changes
[Implementation logic]

Step 2: Verify Compilation
Bash(./mvnw clean compile)  # ❌ BUG - should delegate to maven-builder

Step 3: Check Tests
Bash(./mvnw test)  # ❌ BUG - should delegate to maven-builder
```

❌ INCORRECT - Agent with Bash(./mvnw:*) in Workflow:
```yaml
---
name: task-executor
tools: Read, Edit, Write, Bash
---

Step 1: Execute Task
[Task execution logic]

Step 2: Build Project
Bash(./mvnw clean verify)  # ❌ BUG - bypasses maven-builder
```

**Detection**:
- Grep agent files for `Bash(./mvnw` or `Bash(mvn ` patterns
- Exclude maven-builder agent from violation detection
- Flag any other agent with Maven execution as bug

**Impact of Violation**:
- Duplicate build configuration across agents
- Inconsistent error handling
- No centralized output capture
- Performance metrics not tracked
- Harder to maintain and test build logic

## Rule 8: Three-Layer Command Pattern

For batch operations on collections, use the three-layer pattern: Batch Command → Self-Contained Command → Focused Agents.

**Rationale**: Given the constraint that agents cannot delegate (Rule 6), batch processing requires command orchestration. The three-layer pattern provides clean separation between collection iteration, single-item orchestration, and focused execution.

**The Pattern**:

**Layer 1: Batch Command** (Collection/Iteration)
- Collects items (files, issues, tasks, etc.)
- Iterates over collection
- Delegates each item to Layer 2 command via `SlashCommand`
- Aggregates results from all items
- Reports summary statistics

**Layer 2: Self-Contained Command** (Single-Item Orchestration)
- Handles ONE item end-to-end
- Orchestrates Layer 3 agents for execution
- Orchestrates verification agents (e.g., maven-builder)
- Analyzes results and iterates if needed
- Returns structured result to Layer 1
- Can be invoked directly by users OR by Layer 1

**Layer 3: Focused Agents** (Execution Only)
- Does ONE specific task (no orchestration)
- NO Task tool delegation
- NO verification (returns results to Layer 2)
- NO commit/push logic
- Uses Read, Write, Edit, Bash, Grep, Glob, Skill tools only

**When to Use This Pattern**:
- Processing multiple files (e.g., review all .adoc files)
- Handling multiple issues (e.g., fix all Sonar issues)
- Implementing multiple subtasks (e.g., complex feature breakdown)
- Any operation on a collection where each item needs same processing

**Examples**:

✅ CORRECT - Three-Layer Documentation Review:
```markdown
# Layer 1: Batch Command
/review-technical-docs
  ├─> Glob for all *.adoc files
  ├─> For each file:
  │    └─> SlashCommand(/review-single-asciidoc file.adoc)
  └─> Aggregate validation results

# Layer 2: Self-Contained Command
/review-single-asciidoc <file>
  ├─> Task(asciidoc-format-validator)  # Layer 3
  ├─> Task(asciidoc-link-verifier)     # Layer 3
  ├─> Task(asciidoc-content-reviewer)  # Layer 3
  └─> Return combined validation result

# Layer 3: Focused Agents
asciidoc-format-validator: validates format only
asciidoc-link-verifier: verifies links only
asciidoc-content-reviewer: reviews content only
```

✅ CORRECT - Three-Layer Java Implementation:
```markdown
# Layer 1: Batch Command (if multiple implementations)
/cui-java-task-manager
  ├─> Parse task into implementation list
  ├─> For each implementation:
  │    └─> SlashCommand(/java-implement-code class-task)
  └─> Aggregate implementation results

# Layer 2: Self-Contained Command
/java-implement-code <task>
  ├─> Task(java-code-implementer)  # Layer 3: just implements
  ├─> Task(maven-builder)          # Layer 3: just verifies
  ├─> Analyze build output
  ├─> If errors: repeat until clean
  └─> Return implementation result

# Layer 3: Focused Agents
java-code-implementer: implements code only (NO verification)
maven-builder: builds/verifies only (NO implementation)
```

❌ INCORRECT - Agent Attempting Batch Processing:
```yaml
---
name: bad-batch-agent
tools: Read, Write, Edit, Task, Glob
---

Step 1: Find All Files
Glob *.adoc files

Step 2: Process Each File
For each file:
  Task(validator-agent, file)  # ❌ FAILS - Task unavailable

Step 3: Aggregate Results
[Aggregation logic]
```

❌ INCORRECT - Flat Command Without Layers:
```markdown
/review-technical-docs
  ├─> Glob *.adoc files
  └─> For each file:
       ├─> Task(format-validator)
       ├─> Task(link-verifier)
       ├─> Task(content-reviewer)
       └─> Aggregate
```
**Why Wrong**: No Layer 2 means Layer 1 duplicates orchestration logic for each file. No reusability - users can't invoke single-file review directly.

**Benefits of Three-Layer Pattern**:
- **Reusability**: Layer 2 commands work standalone (users can invoke directly)
- **Testability**: Test each layer independently
- **Maintainability**: Changes to single-item logic in one place
- **Scalability**: Handles 1 or 1000 items with same pattern
- **Composability**: Layer 2 commands can be used by multiple Layer 1 commands

**Alternative Patterns**:
- **Single Operation**: Use Layer 2 pattern only (self-contained command + agents)
- **Smart Orchestration**: Use Fetch + Triage + Delegate for heterogeneous items (see migration-plan.md Pattern 3)

**Reference**: See `claude/architectural-issues/migration-plan.md` for comprehensive pattern descriptions and workflow examples

## Rule 9: Knowledge vs. Workflow Separation

Code examples, patterns, and teaching material belong in Skills (Layer 1), not in Agents or Commands (Layers 2-3).

**Rationale**: Skills are the knowledge layer containing standards, patterns, and examples. Agents/commands are the execution layer containing workflow logic. Embedding code examples in agents duplicates knowledge, violates DRY principle, and prevents independent skill updates.

**The Principle**:
- **Skills (Layer 1)** = KNOWLEDGE: standards, patterns, code examples, best practices, teaching material
- **Commands (Layer 2)** = ORCHESTRATION: coordination logic, iteration, decision flow
- **Agents (Layer 3)** = WORKFLOW: step-by-step execution logic, tool usage patterns

**Requirements**:

**For Skills**:
- ✅ Include comprehensive code examples
- ✅ Provide pattern demonstrations
- ✅ Show before/after comparisons
- ✅ Include anti-pattern examples
- ✅ Provide complete reference implementations

**For Agents/Commands**:
- ✅ Reference skill patterns by name
- ✅ Reference skill standards sections
- ✅ Load skills via `Skill: skill-name`
- ❌ DO NOT embed code examples
- ❌ DO NOT duplicate teaching material
- ⚠️ EXCEPTION: Output format examples (what agent writes to files)

**Acceptable Agent/Command Content**:
1. **Output format examples** (showing what agent writes):
   ```java
   /**
    * Design Decision: Returns Optional rather than throwing...
    * @param input the user input
    * @return Optional containing result
    */
   ```
   ✅ ACCEPTABLE - Shows format of JavaDoc/JSDoc agent will write

2. **Return message format** (showing agent response structure):
   ```
   IMPLEMENTATION COMPLETE
   Files Modified: 3
   Standards Applied: ✅
   ```
   ✅ ACCEPTABLE - Shows agent's return message structure

3. **Workflow references** (pointing to skill content):
   ```
   Reference patterns from loaded `cui-java-unit-testing` skill:
   - AAA pattern from testing standards
   - Generator usage patterns
   - Exception testing with assertThrows()
   ```
   ✅ CORRECT - References skill, doesn't duplicate content

**Prohibited Agent/Command Content**:
1. **Teaching code examples** (showing how to write code):
   ```java
   // Example implementation:
   class UserValidator {
       public boolean validate(String email) {
           return email.matches("...");
       }
   }
   ```
   ❌ PROHIBITED - Teaching material belongs in skill

2. **Pattern demonstrations** (showing technique):
   ```javascript
   // Example test with AAA pattern:
   test('should validate email', () => {
       // Arrange
       const validator = new Validator();
       // Act
       const result = validator.validate(email);
       // Assert
       expect(result).toBe(true);
   });
   ```
   ❌ PROHIBITED - Pattern teaching belongs in skill

**Examples**:

✅ CORRECT - Agent References Skill:
```yaml
---
name: java-junit-implementer
tools: Read, Write, Edit, Skill
---

Step 2: Load Testing Standards
Skill: cui-java-unit-testing

Step 4: Implement Tests
Reference patterns from loaded skill:
- AAA pattern from testing standards
- Generator usage (@EnableGeneratorController, Generators API)
- Exception testing with assertThrows()

All test implementation examples in skill standards.
```

✅ CORRECT - Skill Contains Examples:
```markdown
# cui-java-unit-testing Skill

## Test Implementation Patterns

### AAA Pattern Example
```java
@Test
void shouldValidateEmail() {
    // Arrange
    String email = Generators.emailAddress().next();
    UserValidator validator = new UserValidator();

    // Act
    boolean result = validator.validateEmail(email);

    // Assert
    assertTrue(result);
}
```
```

❌ INCORRECT - Agent Embeds Example:
```yaml
---
name: javascript-test-implementer
---

Step 4: Implement Tests

Example test implementation:
```javascript
import { validateEmail } from '../validator';

describe('Email Validator', () => {
  test('should validate correct email', () => {
    // Arrange
    const email = 'user@example.com';
    // Act
    const result = validateEmail(email);
    // Assert
    expect(result).toBe(true);
  });
});
```
```
**Why Wrong**: Code example duplicates skill content. Should reference skill instead.

**Benefits of Separation**:
- **Single Source of Truth**: Examples maintained in one place (skill)
- **Independent Updates**: Skills can be updated without touching agents
- **Reusability**: Multiple agents reference same skill examples
- **Consistency**: All agents use same patterns from skill
- **DRY Principle**: No duplication of teaching material
- **Smaller Agents**: Agents contain workflow only, not knowledge

**Migration Pattern**:
When fixing agents with embedded examples:
1. Read embedded example from agent
2. Check if skill already has this pattern (avoid duplication)
3. If not in skill: add to skill's standards/
4. Replace agent's embedded example with skill reference
5. Verify agent loads skill with `Skill:` invocation

**Detection**:
- Search agents for code blocks: ` ```java`, ` ```javascript`, ` ```typescript`
- Categorize each code block:
  - Teaching example? → Move to skill
  - Output format? → Keep in agent
  - Pattern demonstration? → Move to skill
- Verify corresponding skill has comprehensive examples

**Related Rules**:
- See Rule 2: Agents Must Use Skills (for skill invocation patterns)
- See Rule 5: Component Organization (for layer responsibilities)

## Enforcement

These rules are enforced through:
- `/cui-create-skill` - Proactive prevention at creation
- `/cui-diagnose-skills` - Reactive detection in existing skills
- `/cui-diagnose-agents` - Check agent skill usage patterns
- `/cui-diagnose-bundle` - Overall bundle compliance

All diagnostic commands invoke this skill to apply consistent validation rules.
