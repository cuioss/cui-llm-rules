# Claude Code Agent Architecture Principles

This document defines the architectural principles and design patterns for Claude Code agents.

**Audience**: Agent creators, agent users, tooling developers (agents-doctor)

**Status**: Living document - updated as architecture evolves

**Last Updated**: 2025-10-20

---

## Table of Contents

1. [Core Architectural Decisions](#core-architectural-decisions)
2. [Essential Rules Pattern](#essential-rules-pattern)
3. [Tool Fit Requirement](#tool-fit-requirement)
4. [Self-Contained Agents](#self-contained-agents)
5. [Lessons Learned vs Continuous Improvement](#lessons-learned-vs-continuous-improvement)
6. [Response Format Standards](#response-format-standards)
7. [Agent vs Command: When to Use Which](#agent-vs-command-when-to-use-which)
8. [Industry Best Practices for Agent Quality](#industry-best-practices-for-agent-quality)

---

## Core Architectural Decisions

### Decision 1: Agents Must Be Self-Contained

**Principle**: Agents should contain all necessary information to execute their task without external reads during execution.

**Rationale**:
- **Performance**: External file reads consume tokens and add latency
- **Autonomy**: Agent can operate independently of external state
- **Clarity**: Anyone reading agent file knows exactly what rules it follows
- **Reliability**: No broken references to moved/deleted files

**Implementation**: Use the Essential Rules Pattern (see below)

**Trade-off**: Duplication of standards across agents vs execution speed
- ✅ Accepted: Speed and autonomy outweigh duplication concerns
- ✅ Mitigation: Automated synchronization via agents-doctor

---

### Decision 2: Perfect Tool Fit Required

**Principle**: Agents must have exactly the tools they need - no more, no less.

**Goal**: Agent executes autonomously without requesting user approval for tool usage.

**Measurement**: Tool Fit Score = 100%

**Rationale**:
- **Autonomy**: User approval breaks agent flow
- **Security**: Minimal permission surface area
- **Clarity**: Tool list documents capabilities
- **Efficiency**: No unused tool overhead

**Enforcement**: agents-doctor verifies tool coverage and flags mismatches

---

### Decision 3: No Self-Modification for Agents

**Principle**: Agents report lessons learned but do not modify themselves.

**Distinction**:
- **Commands** (slash commands): CAN self-modify (continuous improvement pattern)
- **Agents**: CANNOT self-modify (lessons learned reporting pattern)

**Rationale**:
- Agents are invoked by system, not directly by user
- Agent modifications require restart to take effect
- Creates race conditions (agent modifies self while running)
- User should review and approve architectural changes

**Implementation**: Agents include "Lessons Learned Reporting" section in output

---

### Decision 4: Structured Response Format

**Principle**: All agents must produce structured, parseable output.

**Required Elements**:
1. **Status**: Success/Failure indicator
2. **Summary**: Brief description of work done
3. **Metrics**: Quantified results (files processed, issues found, etc.)
4. **Tool Usage Tracking**: Which tools were used and how many times
5. **Lessons Learned**: Insights for manual improvement (optional but recommended)

**Rationale**:
- Main process can parse and act on results
- Enables automation and chaining
- Provides visibility into agent behavior
- Facilitates debugging and improvement

---

## Essential Rules Pattern

### The Problem

Agents often need to follow standards from `~/git/cui-llm-rules/standards/`:
- Logging standards
- Documentation standards
- Code quality standards
- Error handling standards

**Traditional Approach** (used in commands):
```markdown
### Step 1: Read Standards

1. Read ~/git/cui-llm-rules/standards/logging/cui-logging-standards.adoc
2. Extract LogRecord pattern rules
3. Store in working memory
```

**Problems**:
- External file read consumes ~2,000 tokens
- Adds latency (I/O operation)
- Standards file may be large (100+ lines)
- Repeated reads across multiple agent invocations

### The Solution: Embed + Sync

**Embed essential rules directly in agent file**:
```markdown
## Essential Rules

### Logging Standards
Source: ~/git/cui-llm-rules/standards/logging/cui-logging-standards.adoc#logrecord-pattern
Last Synced: 2025-10-15

- All INFO/WARN/ERROR must use LogRecord constants
- Use %s for all string substitutions (never %d, %.2f, {})
- Exceptions must come first in parameter list
- LogRecord identifiers: INFO (001-099), WARN (100-199), ERROR (200-299)

### JavaDoc Standards
Source: ~/git/cui-llm-rules/standards/documentation/javadoc-standards.adoc#mandatory-javadoc
Last Synced: 2025-10-18

- All public classes must have JavaDoc
- All public methods must document @param, @return, @throws
- No missing JavaDoc warnings allowed
```

**Automated Synchronization**:
- `agents-doctor` verifies embedded rules match sources
- Detects: OUT_OF_DATE, ORPHANED, OLD_SYNC
- Offers auto-update from source

### Format Specification

```markdown
## Essential Rules

### {Domain} Standards
Source: {absolute_path}#{optional_section_anchor}
Last Synced: {YYYY-MM-DD}

{Embedded rules content - bullet points or prose}
```

**Required Fields**:
- **Domain**: Clear category (e.g., "Logging Standards", "JavaDoc Standards")
- **Source**: Absolute path to authoritative source file
- **Section Anchor**: Optional `#section-id` to reference specific part of source
- **Last Synced**: Date when rules were last synchronized with source

**Content Guidelines**:
- **Selective**: Only include rules relevant to agent's domain
- **Essential**: 10-30 lines per domain (not entire standard)
- **Curated**: Extract key rules, not every detail
- **Actionable**: Rules the agent will actually enforce

### Benefits

| Aspect | External Read | Embedded + Sync |
|--------|---------------|-----------------|
| Execution tokens | ~2,000 per read | ~0 (already in agent) |
| Performance | Slower (I/O) | Faster (inline) |
| Autonomy | Depends on external file | Self-contained |
| Clarity | References external docs | Clear what agent follows |
| Maintenance | Auto (always current) | Semi-auto (verify + sync) |

### Trade-offs

**Accepted**:
- ✅ Duplication across agents (acceptable for performance)
- ✅ Manual sync trigger (automated via agents-doctor)

**Mitigated**:
- ✅ Sync burden → Automated detection and update
- ✅ Drift risk → agents-doctor warns when out of sync

---

## Tool Fit Requirement

### Definition

**Tool Fit Score**: Percentage measuring how well configured tools match workflow needs.

```
Tool Fit Score = (Correctly Configured Tools / (Required Tools + Unnecessary Tools)) * 100
```

**Example**:
- Required tools (from workflow): Read, Edit, Write, Bash (4 tools)
- Configured tools (in frontmatter): Read, Edit, Bash, Grep (4 tools)
- Missing: Write (1 tool)
- Unnecessary: Grep (1 tool)
- Score: (3 / 6) * 100 = 50% (Poor fit)

### Ratings

- **100%**: Perfect fit - All required tools, no extras
- **90-99%**: Good fit - Minor issue (1 missing or 1 extra)
- **70-89%**: Fair fit - Multiple issues
- **<70%**: Poor fit - Needs fixing

### Goal: 100% Tool Fit

**Why Perfect Fit Matters**:

1. **Missing Tools → User Approval Required**
   ```
   Agent tries to use Write tool
   → Write not configured
   → Claude asks user for approval
   → Breaks autonomous execution
   ```

2. **Extra Tools → Security/Clarity Issues**
   ```
   Agent has Grep configured
   → Never uses it in workflow
   → Unnecessary permission surface
   → Misleading about capabilities
   ```

### Tool Coverage Analysis

agents-doctor performs comprehensive tool coverage analysis:

1. **Scan Workflow**: Extract all tool references
2. **Compare**: Required tools vs configured tools
3. **Categorize Issues**:
   - CRITICAL: Missing required tool
   - WARNING: Unnecessary configured tool
4. **Calculate Score**: Tool Fit percentage
5. **Offer Fixes**: Auto-update frontmatter

### Tool Dependencies

**Special Rules**:
- **Edit requires Read**: Edit tool must read file first in same context
  - If workflow uses Edit → Must configure both Read and Edit
- **Bash for git**: If workflow runs git commands → Must configure Bash
- **Write for creation**: If workflow creates files → Must configure Write

---

## Self-Contained Agents

### The Principle

**Self-contained**: Agent file contains everything needed for execution.

**Includes**:
- ✅ Frontmatter (name, description, tools, model, color)
- ✅ Task definition and goals
- ✅ Complete workflow instructions
- ✅ Essential rules (embedded standards)
- ✅ Response format template
- ✅ Tool usage tracking requirements
- ✅ Error handling logic

**Does NOT Include**:
- ❌ References to external files during execution
- ❌ "Read this standard and extract rules"
- ❌ Continuous improvement self-modification

### Benefits

**For Agent Execution**:
- Fast: No external I/O during execution
- Reliable: No broken references
- Clear: Everything visible in one file

**For Agent Users**:
- Transparent: Can read agent file to understand behavior
- Predictable: Agent behavior documented in file
- Debuggable: All logic in one place

**For Agent Creators**:
- Simple: No complex dependency management
- Testable: Can verify agent without external setup
- Maintainable: Single source of truth

### Implementation Checklist

When creating a new agent:

1. ✅ Define complete workflow inline
2. ✅ Embed essential rules (Essential Rules pattern)
3. ✅ Configure exact required tools (100% fit)
4. ✅ Include response format template
5. ✅ Add tool usage tracking
6. ✅ Add lessons learned reporting
7. ❌ No external reads during execution
8. ❌ No self-modification logic

---

## Lessons Learned vs Continuous Improvement

### The Distinction

| Aspect | Commands (Slash Commands) | Agents |
|--------|---------------------------|--------|
| **Invocation** | User types `/command` | System invokes via Task tool |
| **Self-Modification** | ✅ Allowed (Continuous Improvement) | ❌ Forbidden |
| **Learning Pattern** | Updates own file automatically | Reports to user for manual update |
| **Reason** | User directly controls | Agent runs in isolated context |

### Commands: Continuous Improvement Pattern

**Allowed for slash commands**:

```markdown
## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** with:
1. Improved validation patterns discovered
2. Better methods for verification
3. More efficient processing approaches
4. Lessons learned about edge cases

This ensures the command evolves with each execution.
```

**Why it works for commands**:
- User invokes command directly
- User sees file modification
- Changes take effect on next invocation
- User can review/revert changes

### Agents: Lessons Learned Reporting Pattern

**Required for agents**:

```markdown
## LESSONS LEARNED REPORTING

If during execution you discover insights that could improve future executions:

**When to report lessons learned:**
- New warning patterns that should be acceptable
- Better error analysis techniques
- More efficient fix strategies
- Edge cases not covered in current workflow
- Unexpected tool behavior

**Include in final report**:
- What was discovered
- Why it matters
- Suggested improvement for this agent
- Impact on future executions

**Purpose**: Allow users to manually improve this agent based on real execution experience, without agent self-modification.
```

**Why different for agents**:
- Agent invoked by system (not directly by user)
- Agent context is isolated (changes require restart)
- Self-modification creates race conditions
- Architectural changes should be user-reviewed

### Response Format

**Lessons Learned section in agent output**:

```markdown
**Lessons Learned** (for future improvement):
{if any insights discovered during execution:}
- Discovery: {what was discovered}
- Why it matters: {explanation}
- Suggested improvement: {what should change in this agent}
- Impact: {how this would help future executions}

{if no lessons learned: "None - execution followed expected patterns"}
```

**User workflow**:
1. Agent completes work
2. Agent reports lessons learned
3. User reviews suggestions
4. User manually updates agent file (if agrees)
5. User runs `agents` command to reload
6. Updated agent used in next invocation

---

## Response Format Standards

### Required Response Structure

All agents must produce structured output following this template:

```markdown
## {Agent Name} - {Task} Complete

**Status**: ✅ SUCCESS | ❌ FAILURE | ⚠️ PARTIAL

**Summary**:
{Brief 1-2 sentence description of work done}

**Metrics**:
- {Metric 1}: {count}
- {Metric 2}: {count}
- {Metric 3}: {count}

**Tool Usage**:
- Read: {count} invocations
- Edit: {count} invocations
- Write: {count} invocations
- Bash: {count} invocations
- {other tools if used}

**Lessons Learned** (for future improvement):
{if any insights discovered:}
- Discovery: {what was discovered}
- Why it matters: {explanation}
- Suggested improvement: {what should change}
- Impact: {how this would help}

{if no lessons learned: "None - execution followed expected patterns"}

**Details**:
{Detailed results, findings, changes made}
```

### Required Elements

1. **Status Indicator**: ✅ SUCCESS | ❌ FAILURE | ⚠️ PARTIAL
   - Must be parseable by main process
   - Clear success/failure determination

2. **Summary**: Brief overview
   - 1-2 sentences
   - High-level outcome

3. **Metrics**: Quantified results
   - Countable measures (files processed, issues found, etc.)
   - Enable trend analysis over time

4. **Tool Usage Tracking**: Every tool invocation recorded
   - Helps optimize tool configuration
   - Identifies inefficiencies
   - Feeds into Tool Fit Score calculation

5. **Lessons Learned**: Insights for improvement (optional but recommended)
   - Discovered patterns
   - Suggested changes
   - Impact assessment

### Benefits

**For Main Process**:
- Can parse and act on results
- Enables automation
- Facilitates chaining agents

**For Users**:
- Clear outcome visibility
- Quantified results
- Actionable improvement suggestions

**For Agent Developers**:
- Standard format to follow
- Consistent user experience
- Easier debugging

---

## Agent vs Command: When to Use Which

### Commands (Slash Commands)

**Location**: `.claude/commands/*.md` or `~/.claude/commands/*.md`

**Invocation**: User types `/command-name`

**Use When**:
- User needs direct control over execution
- Interactive decisions required throughout
- Complex multi-step workflows
- Learning/improving over time (continuous improvement)
- Processing large datasets (may require multiple sessions)

**Characteristics**:
- Can self-modify (continuous improvement)
- Direct user interaction
- May ask questions mid-execution
- Can span multiple sessions
- User sees full execution

**Examples**:
- `/docs-review` - Interactive document review with user decisions
- `/verify-project` - Build verification with user approvals
- `/slash-doctor` - Command analysis with fix approval

### Agents

**Location**: `.claude/agents/*.md` or `~/.claude/agents/*.md`

**Invocation**: System uses Task tool (not directly user-typed)

**Use When**:
- Task is well-defined and autonomous
- No user interaction needed during execution
- Single-session completion expected
- Faster execution preferred (self-contained)
- Result needs to be parseable by main process

**Characteristics**:
- Cannot self-modify (lessons learned instead)
- Minimal user interaction (decisions only, not approvals)
- Complete execution in one session
- Self-contained (embedded rules)
- Structured output format

**Examples**:
- `project-builder` - Autonomous build verification
- `documentation-analyzer` - Analyze docs without interaction
- `code-reviewer` - Review code and report findings

### Decision Matrix

| Criterion | Use Command | Use Agent |
|-----------|-------------|-----------|
| Execution time | Can be hours/days | < 30 minutes |
| User interaction | Frequent questions | Minimal (decisions only) |
| Learning pattern | Continuous improvement | Lessons learned reporting |
| Output format | Flexible | Structured, parseable |
| External reads | Acceptable | Avoid (use embedded rules) |
| Self-contained | Not required | Required |
| Invoked by | User directly | System (Task tool) |

---

## Industry Best Practices for Agent Quality

This section documents external best practices from industry research, Anthropic guidelines, and prompt engineering standards. These principles ensure agents are unambiguous, precise, sharp, and avoid common anti-patterns.

**Sources**:
- Anthropic Claude Prompt Engineering Documentation (2025)
- AI Agent Design Patterns research (2025)
- Prompt Engineering Best Practices (academic and industry sources)

**Last Reviewed**: 2025-10-20

### Principle 1: Clarity and Specificity

**Guideline**: Agent instructions must be clear, explicit, and specific. Ambiguity is the primary cause of poor LLM output.

**Best Practices**:

1. **Use Precise Language**
   - ✅ DO: "Run `./mvnw clean install` with timeout of 120000ms"
   - ❌ DON'T: "Build the project appropriately"

2. **Include Specific Details**
   - ✅ DO: "Generate 3-5 sentence summary in markdown format"
   - ❌ DON'T: "Provide a fairly short summary"

3. **Define Clear Scope**
   - ✅ DO: "Analyze all `.java` files in `src/main/java` excluding test files"
   - ❌ DON'T: "Analyze the codebase"

4. **Concrete Action Verbs**
   - ✅ DO: validate, transform, calculate, parse, extract, verify
   - ❌ DON'T: handle, manage, deal with, work with, process

**Source**: Anthropic Claude 4 Prompt Engineering Best Practices (2025)

### Principle 2: Avoid Ambiguous Language

**Anti-Pattern Detection**: Flag and eliminate vague phrases that have multiple interpretations.

**Common Ambiguity Anti-Patterns**:

| Vague Phrase | Problem | Specific Alternative |
|--------------|---------|---------------------|
| "if needed" | When is it needed? | "if error count > 0" |
| "appropriately" | What defines appropriate? | "using format: YYYY-MM-DD" |
| "handle errors" | Which errors? How? | "catch IOException, log, and retry once" |
| "ensure quality" | What are criteria? | "achieve 100% test coverage" |
| "fairly short" | How short? | "3-5 sentences" or "< 200 words" |
| "reasonable timeout" | What's reasonable? | "120 seconds" |

**Detection Rules for agents-doctor**:

When analyzing agent instructions, flag:
- Conditional phrases without criteria: "if necessary", "when appropriate", "as needed"
- Subjective modifiers: "appropriately", "reasonably", "fairly", "sufficiently"
- Generic action verbs: "handle", "manage", "deal with", "work with"
- Undefined scope: "relevant files", "important sections", "key points"
- Unmeasurable goals: "good quality", "better performance", "clean code"

**Source**: Prompt Engineering Anti-Patterns Research (2025)

### Principle 3: Eliminate Internal Duplication

**Guideline**: Each rule or instruction should appear once. Duplication causes confusion and maintenance burden.

**Detection Strategy**:

1. **Exact Duplicates**
   - Same instruction repeated in multiple steps
   - Same rule in different sections
   - Example: "Read file before editing" appears in Step 3, Step 7, and Critical Rules

2. **Semantic Duplicates**
   - Different wording, same meaning
   - Example: "Always use Read before Edit" vs "Edit requires prior Read"

3. **Redundant Clarifications**
   - Over-explanation of same concept
   - Example: Explaining the same workflow requirement 3 times

**Consolidation Pattern**:
- State rule ONCE in "CRITICAL RULES" section
- Reference it in workflow: "See CRITICAL RULES #3"
- Do not repeat verbatim

**Benefit**: Single source of truth, easier maintenance, less token usage

### Principle 4: Measurable Success Criteria

**Guideline**: All goals, conditions, and outcomes must be measurable or objectively verifiable.

**Best Practices**:

1. **Quantify Thresholds**
   - ✅ DO: "Retry up to 3 times"
   - ❌ DON'T: "Retry several times"

2. **Define Success Explicitly**
   - ✅ DO: "Success = exit code 0 and no ERROR lines in output"
   - ❌ DON'T: "Success = build completes successfully"

3. **Enumerate Conditions**
   - ✅ DO: "If status is one of: [FAILED, TIMEOUT, ERROR]"
   - ❌ DON'T: "If status indicates failure"

4. **Specify Formats**
   - ✅ DO: "Output as JSON with keys: {status, count, duration}"
   - ❌ DON'T: "Output as structured data"

**Source**: AI Agent Evaluation Best Practices (2025)

### Principle 5: Explicit Error Handling

**Guideline**: Every error condition must have a defined handling strategy. No implicit "handle appropriately" instructions.

**Required Error Specification**:

1. **Enumerate Error Types**
   ```markdown
   Error Handling:
   - FileNotFoundException: Log error, skip file, continue
   - TimeoutException: Retry once with 2x timeout, then fail
   - ParseException: Log details, mark file as invalid, continue
   - NetworkException: Retry 3 times with exponential backoff, then fail
   ```

2. **Define Retry Logic**
   - Max retry count (explicit number)
   - Retry conditions (which errors are retryable)
   - Backoff strategy (immediate, exponential, fixed delay)
   - Final action after retries exhausted

3. **Specify Failure Modes**
   - When to abort entire workflow
   - When to skip and continue
   - What to report in each failure mode

**Anti-Pattern**: Generic error handling
```markdown
❌ "Handle errors appropriately"
❌ "If errors occur, deal with them"
❌ "Ensure robust error handling"
```

**Source**: Agentic AI Design Patterns (AWS, Databricks, 2025)

### Principle 6: Chain-of-Thought and Structured Reasoning

**Guideline**: For complex tasks, explicitly instruct the agent to think step-by-step.

**Best Practices**:

1. **Explicit Thinking Steps**
   ```markdown
   Before executing Step 3, perform analysis:
   1. List all files to be processed
   2. Estimate token cost: <count> * 200 tokens
   3. Check if within budget (< 50,000 tokens)
   4. If over budget, partition into batches
   ```

2. **Decision Trees**
   ```markdown
   Decision Point:
   - If test count = 0: ERROR - no tests found
   - If test count < 5: WARNING - insufficient coverage
   - If test failures > 0: FAIL - fix failures first
   - If all pass: SUCCESS - proceed to next step
   ```

3. **Validation Checkpoints**
   ```markdown
   After Step 4, verify:
   ✅ All files processed (expected: 10, actual: ?)
   ✅ No errors in log (grep "ERROR")
   ✅ Output file exists and > 0 bytes
   If any check fails, abort and report.
   ```

**Source**: Anthropic Claude 4 Best Practices (2025) - Chain-of-thought reasoning

### Principle 7: Minimal Context, Maximum Signal

**Guideline**: Provide only essential information. Avoid verbose explanations or unnecessary context that dilutes key instructions.

**Context Engineering Principles**:

1. **Attention Budget Management**
   - Agent attention is finite (limited context window)
   - Every token competes for attention
   - Curate the smallest set of high-signal tokens

2. **Signal-to-Noise Ratio**
   - ✅ High signal: "Parse JSON with keys: [name, version, dependencies]"
   - ❌ Low signal: "JSON is a data format that uses key-value pairs. You should parse it carefully and extract the important information including things like the name field which represents..."

3. **Essential Rules Pattern**
   - Embed only essential subset of standards
   - 10-30 lines per domain (not 100+ lines)
   - Curate based on agent's actual enforcement needs

**Anti-Pattern**: Information overload
- Embedding entire standard documents
- Repeating same information in multiple sections
- Verbose explanations where concise instructions suffice

**Source**: Anthropic "Effective Context Engineering for AI Agents" (2025)

### Principle 8: Provide Examples

**Guideline**: For nuanced or stylistic requirements, show concrete examples rather than abstract descriptions.

**Best Practices**:

1. **Input-Output Examples**
   ```markdown
   Format transformation examples:

   Input: "2025-10-20T14:30:00Z"
   Output: "October 20, 2025 at 2:30 PM"

   Input: "2025-01-05T09:00:00Z"
   Output: "January 5, 2025 at 9:00 AM"
   ```

2. **Good vs Bad Examples**
   ```markdown
   ✅ GOOD: "Add logging for authentication failure"
   - Changes 1 specific thing
   - Clear scope (authentication only)
   - Actionable

   ❌ BAD: "Improve logging"
   - Vague scope (all logging?)
   - Undefined improvement
   - Not actionable
   ```

3. **Edge Case Examples**
   ```markdown
   Handle edge cases:
   - Empty file: Return {count: 0, status: "EMPTY"}
   - Binary file: Return {count: null, status: "BINARY"}
   - Access denied: Return {count: null, status: "DENIED"}
   ```

**Source**: Anthropic Prompt Engineering Guide (2025)

### Principle 9: Start Simple, Add Complexity Deliberately

**Guideline**: Begin with minimal workflow. Add complexity only when simpler solutions demonstrably fail.

**Agent Design Progression**:

1. **Level 0: Simple Prompt**
   - Single instruction
   - No tools
   - Direct response

2. **Level 1: Single-Step Agent**
   - One tool (e.g., Read)
   - Linear workflow
   - No decision branching

3. **Level 2: Multi-Step Agent**
   - Multiple tools (Read, Edit, Write)
   - Sequential workflow
   - Basic error handling

4. **Level 3: Branching Agent**
   - Decision points
   - Conditional logic
   - Retry mechanisms

5. **Level 4: Multi-Agent System**
   - Coordination between agents
   - Parallel execution
   - Complex state management

**Principle**: Only move to next level when current level cannot solve the problem.

**Source**: Anthropic "Building Effective Agents" (2025)

### Principle 10: Observability and Evaluation

**Guideline**: Agents must be measurable. Track performance, quality, and behavior.

**Required Metrics**:

1. **Performance Metrics**
   - Execution time (per step, total)
   - Token usage (input, output, total)
   - Tool invocations (count per tool)
   - Success/failure rate

2. **Quality Metrics**
   - Task completion rate
   - Accuracy (if measurable)
   - User approval required (should be 0)
   - Retries needed

3. **Behavior Tracking**
   - Which code paths executed
   - Decision points reached
   - Error conditions encountered

**Implementation**: Tool Usage Tracking + Metrics sections in response format

**Source**: AI Agent Observability Best Practices (2025)

### Quality Checklist for Agent Instructions

Use this checklist when creating or reviewing agents:

**Clarity & Specificity**:
- [ ] No vague language ("appropriately", "if needed", "handle")
- [ ] All thresholds quantified (numbers, not "several" or "many")
- [ ] Concrete action verbs (validate, calculate, not "manage", "deal with")
- [ ] Specific formats defined (JSON schema, markdown structure, etc.)

**Ambiguity Elimination**:
- [ ] All conditionals have explicit criteria ("if X > 5", not "if necessary")
- [ ] Decision points enumerate all options
- [ ] Scope clearly bounded ("files in src/main/java", not "relevant files")
- [ ] Success criteria measurable and objective

**Duplication Prevention**:
- [ ] Each rule stated once (in CRITICAL RULES or workflow, not both)
- [ ] No semantic duplication (same meaning, different words)
- [ ] No redundant clarifications

**Error Handling**:
- [ ] All error types enumerated
- [ ] Retry strategy explicit (count, backoff, conditions)
- [ ] Failure modes defined (abort vs continue)
- [ ] No generic "handle errors" instructions

**Measurability**:
- [ ] Success criteria are verifiable (exit code, output format, etc.)
- [ ] Thresholds have explicit numbers
- [ ] Conditions are boolean-evaluable
- [ ] Outcomes are observable

**Context Efficiency**:
- [ ] Essential Rules section: 10-30 lines per domain (not 100+)
- [ ] No verbose explanations where concise works
- [ ] High signal-to-noise ratio

**Examples Provided**:
- [ ] Complex formats shown with examples
- [ ] Edge cases illustrated
- [ ] Good vs bad examples for nuanced requirements

**Observability**:
- [ ] Tool usage tracking required
- [ ] Metrics defined and quantified
- [ ] Response format structured and parseable

### Common Anti-Patterns Summary

**Anti-Pattern 1: Vague Instructions**
```markdown
❌ "Process the files as needed"
✅ "Process all .java files in src/main/java, excluding files matching *Test.java"
```

**Anti-Pattern 2: Undefined Success**
```markdown
❌ "Build succeeds"
✅ "Build succeeds = exit code 0 AND no lines matching 'ERROR' in output"
```

**Anti-Pattern 3: Generic Error Handling**
```markdown
❌ "Handle exceptions appropriately"
✅ "Catch FileNotFoundException → log and skip file. Catch IOException → retry once, then fail."
```

**Anti-Pattern 4: Ambiguous Conditions**
```markdown
❌ "If the file is too large..."
✅ "If file size > 10MB..."
```

**Anti-Pattern 5: Unmeasurable Criteria**
```markdown
❌ "Ensure good code quality"
✅ "Ensure: 0 checkstyle violations, 0 SpotBugs errors, test coverage > 80%"
```

### References

**Primary Sources**:
1. **Anthropic Claude Prompt Engineering** - https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview (2025)
2. **Anthropic Building Effective Agents** - https://www.anthropic.com/research/building-effective-agents (2025)
3. **Anthropic Effective Context Engineering** - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents (2025)

**Industry Research**:
4. **AI Agent Design Patterns** - Databricks, AWS, MongoDB (2025)
5. **Agentic AI Architectures** - LangChain, LlamaIndex, Microsoft AutoGen (2025)
6. **Prompt Engineering Best Practices** - Academic and industry sources (2025)

**Additional Reading**:
7. **The 2025 Guide to AI Agent Workflows** - Vellum (2025)
8. **Zero to One: Learning Agentic Patterns** - Philipp Schmid (2025)
9. **Prompt Engineering Guide** - Lakera AI (2025)

---

## Enforcement and Tooling

### agents-doctor

**Tool**: `/agents-doctor` command

**Purpose**: Verify agents follow architectural principles

**Checks**:
1. ✅ Tool Fit Score = 100%
2. ✅ Essential Rules synchronized with sources
3. ✅ No self-modification references
4. ✅ Valid frontmatter
5. ✅ Structured response format
6. ✅ Tool usage tracking present
7. ✅ Lessons learned reporting (recommended)

**Usage**:
```bash
/agents-doctor global           # Check all global agents
/agents-doctor project-builder  # Check specific agent
/agents-doctor                  # Interactive mode
```

**Automated Fixes**:
- Updates tool configuration (adds missing, removes extra)
- Synchronizes Essential Rules from sources
- Adds missing response format sections

### Integration Points

**Pre-commit Hook** (recommended):
```bash
# Run agents-doctor before committing agent changes
/agents-doctor project
```

**CI/CD Pipeline** (recommended):
```bash
# Verify all agents in CI
/agents-doctor global
/agents-doctor project
```

**Regular Maintenance** (recommended):
```bash
# Weekly: Check for out-of-date Essential Rules
/agents-doctor global
```

---

## Migration Guide

### Converting Command to Agent

If you have a command that should be an agent:

**Step 1: Evaluate Suitability**
- Can it complete in < 30 minutes? ✅
- Can it be self-contained? ✅
- Does it need continuous improvement? ❌
- Does it need frequent user interaction? ❌

If all answers match, proceed with conversion.

**Step 2: Create Agent File**

Create `.claude/agents/agent-name.md`:

```markdown
---
name: agent-name
description: {Clear description with usage examples}
tools: {Comma-separated required tools only}
model: sonnet
color: green
---

{Agent content from command, adapted}
```

**Step 3: Embed Essential Rules**

Replace:
```markdown
### Step 1: Read Standards
1. Read /Users/.../standards/logging.adoc
```

With:
```markdown
## Essential Rules

### Logging Standards
Source: /Users/.../standards/logging.adoc#section
Last Synced: 2025-10-20

{Embedded essential rules}
```

**Step 4: Add Response Format**

Add structured response template (see Response Format Standards above)

**Step 5: Replace Continuous Improvement**

Remove:
```markdown
## CONTINUOUS IMPROVEMENT RULE
...self-modification logic...
```

Add:
```markdown
## LESSONS LEARNED REPORTING
...reporting logic...
```

**Step 6: Verify Tool Fit**

```bash
/agents-doctor agent-name
```

Fix any tool coverage issues until Tool Fit Score = 100%.

**Step 7: Test**

Invoke agent and verify:
- Executes without user approval
- Produces structured output
- Reports tool usage
- Reports lessons learned

---

## Reference Template: project-builder Agent

**Location**: `~/.claude/agents/project-builder.md`

**Status**: Fully compliant with all architectural principles (as of 2025-10-20)

### Why Use as Template

The `project-builder` agent is the **canonical reference implementation** of the agent architecture:

✅ **Perfect Tool Fit** (100%):
- Tools: Read, Edit, Write, Bash
- All required, none unnecessary
- Matches workflow exactly

✅ **Essential Rules Section**:
- Domain: JavaDoc Standards
- Source reference: Full path with Last Synced date
- Curated content: 25 lines of essential rules
- Relevant to agent's task

✅ **Structured Response Format**:
- Status indicator
- Metrics (iterations, issues fixed)
- Tool usage tracking
- Lessons learned reporting

✅ **No Self-Modification**:
- Uses Lessons Learned Reporting pattern
- No Continuous Improvement references

✅ **Complete Frontmatter**:
- Clear description with usage examples
- Correct tools configuration
- Proper model and color

### Template Structure

Use this structure when creating new agents:

```markdown
---
name: {agent-name}
description: {Clear description with usage examples}
tools: {Comma-separated required tools only - verify 100% fit}
model: sonnet
color: {green|blue|purple|...}
---

{Brief role description}

## YOUR TASK

{Clear task definition}

## ESSENTIAL RULES

### {Domain} Standards
Source: {/absolute/path/to/source.adoc}#{optional-section}
Last Synced: {YYYY-MM-DD}

{Curated essential rules - 10-30 lines}

## WORKFLOW (FOLLOW EXACTLY)

### Step 1: {Task}
{Detailed instructions}

### Step 2: {Task}
{Detailed instructions}

...

## CRITICAL RULES

{Non-negotiable constraints}

## TOOL USAGE TRACKING

{Requirement to track all tool invocations}

## LESSONS LEARNED REPORTING

{Report insights without self-modification}

## RESPONSE FORMAT

{Structured output template}
```

### Key Sections to Copy

When creating a new agent, copy these sections from project-builder:

1. **TOOL USAGE TRACKING**: Exact text
2. **LESSONS LEARNED REPORTING**: Exact text (adapt "When to report" list to your domain)
3. **RESPONSE FORMAT**: Adapt template to your metrics

### Verification Checklist

After creating new agent based on template:

1. ✅ Add Essential Rules with source reference
2. ✅ Configure only required tools
3. ✅ Include Tool Usage Tracking section
4. ✅ Include Lessons Learned Reporting section
5. ✅ Define structured Response Format
6. ✅ Run `/agents-doctor {agent-name}` to verify
7. ✅ Fix any issues until Tool Fit Score = 100%

---

## Future Considerations

### Potential Enhancements

1. **Agent Composition**: Agents invoking sub-agents
2. **Shared Essential Rules**: Common rules repository
3. **Version Control**: Track Essential Rules versions
4. **Performance Metrics**: Standard benchmarking
5. **Agent Registry**: Central catalog of available agents

### Open Questions

1. How to handle very large standards (>100 lines)?
   - Current: Curate essential subset
   - Future: Hierarchical embedding?

2. How to share Essential Rules across agents?
   - Current: Duplicate (acceptable)
   - Future: Shared rules with references?

3. How to version Essential Rules?
   - Current: Last Synced date
   - Future: Version numbers or checksums?

---

## References

- Agent Implementation: `.claude/agents/*.md`
- agents-doctor: `~/.claude/commands/agents-doctor.md`
- agents-doctor modules: `~/git/cui-llm-rules/claude/agents/agents-doctor/`
- Project Standards: `~/git/cui-llm-rules/standards/`
- Command Architecture: (Different pattern - continuous improvement allowed)

---

## Changelog

### 2025-10-20
- Initial architecture document created
- Defined Essential Rules pattern
- Established Tool Fit requirement
- Documented Lessons Learned vs Continuous Improvement distinction
- Created Response Format standards
- Updated project-builder agent as reference template
- Added Essential Rules section to project-builder
- Achieved 100% Tool Fit Score for project-builder
- Documented project-builder as canonical reference implementation
- Added Industry Best Practices for Agent Quality section:
  - 10 principles from Anthropic, industry research, and prompt engineering standards
  - Clarity, specificity, ambiguity avoidance, measurability, error handling
  - Comprehensive Quality Checklist for agent creation/review
  - Common anti-patterns with examples
  - References to authoritative sources (reviewed 2025-10-20)
