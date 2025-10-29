---
name: cui-create-agent
description: Guide users through creating a new well-structured agent following architectural best practices
---

# Agent Creation Wizard

Guide users through creating a new, well-structured agent following architectural best practices.

## SCOPE

**Repository-Specific Utility**: This command is designed for the `cui-llm-rules` repository and references repository-specific architecture documentation. It creates agents that follow CUI standards and patterns.

## CRITICAL: Reference Architecture

Before execution, always reference: `~/git/cui-llm-rules/claude/agents-architecture.md`

This ensures agents follow:
- Essential Rules Pattern
- Tool Fit Requirement (100%)
- Self-Contained Agents principle
- Lessons Learned Reporting (not Continuous Improvement)
- Industry Best Practices

## WORKFLOW INSTRUCTIONS

### Step 1: Display Welcome and Overview

Display:
```
╔════════════════════════════════════════════════════════════╗
║              Agent Creation Wizard                         ║
╔════════════════════════════════════════════════════════════╝
║
║ This wizard will guide you through creating a new agent
║ that follows architectural best practices.
║
║ You'll answer questions about:
║ - Agent location and basic info
║ - Task definition and invocation examples
║ - Required tools (Tool Fit: 100%)
║ - Essential rules to embed
║ - Workflow structure
║ - Response format and metrics
║ - Industry best practices compliance
║
║ Let's begin!
║
╚════════════════════════════════════════════════════════════

Ready to start? Enter 'y' to continue:
```

Wait for user acknowledgment (any input will proceed).

### Step 2: Read Architecture Principles

**CRITICAL**: Load agent architecture to ensure compliance.

1. Read: `~/git/cui-llm-rules/claude/agents-architecture.md`
2. Extract:
   - Best Practices for Well-Formed Agents
   - Essential Rules Pattern specification
   - Tool Fit Requirement (100%)
   - Lessons Learned Reporting pattern
   - Response Format standards
   - Industry Best Practices checklist

3. Store in working memory for validation during agent generation

### Step 3: Collect Basic Information

#### Question 3.1: Agent Location
```
[Question 1/10] Where should the agent be located?

1. Marketplace bundle (~/git/cui-llm-rules/claude/marketplace/bundles/)
   - Part of a shareable plugin bundle
   - Use for reusable, versioned agents
   - Examples: maven-project-builder, asciidoc-reviewer, task-executor

2. Project agent (.claude/agents/)
   - Available only in this project
   - Use for project-specific workflows
   - Examples: custom validators, project-specific analysis

Enter 1 or 2:
```

Store response as `location` (marketplace or project).

**If marketplace (option 1) selected, ask follow-up:**
```
Which bundle should contain this agent?

Existing bundles:
- cui-utility-commands (project utilities)
- cui-plugin-development-tools (plugin/command/agent creation)
- cui-pull-request-workflow (PR management)
- cui-issue-implementation (issue planning and implementation)
- cui-documentation-standards (documentation review)
- cui-project-quality-gates (build and quality checks)

Enter bundle name or "new" to create a new bundle:
```

Store response as `bundle_name`.

#### Question 3.2: Agent Name
```
[Question 2/10] What is the agent name?

- Use lowercase with hyphens (e.g., maven-project-builder, code-reviewer)
- Should be descriptive and concise
- Must be unique (not conflict with existing agents)
- Will be used as filename: {name}.md

Agent name:
```

Store response as `agent_name`.
Validate: No spaces, lowercase, hyphens only, doesn't already exist.

#### Question 3.3: Agent Purpose
```
[Question 3/10] What is the agent's primary purpose?

This is a brief, one-sentence description of what the agent does.
It appears in the frontmatter description field.

Example:
"Use this agent when the user needs to build and verify the entire project with quality checks."

Agent purpose:
```

Store response as `purpose`.

#### Question 3.4: When to Invoke

```
[Question 4/10] When should this agent be invoked?

Provide 2-3 specific examples of when the agent should be used.

These will appear in the frontmatter description and help users
understand when to invoke this agent vs. others.

Format each example as:
- User: "{user request}"
  Assistant: "{how assistant invokes agent}"

Example 1:
```

Collect 2-3 examples. Store in `invocation_examples` array.

### Step 4: Define Required Tools

#### Question 4.1: Analyze Workflow for Tool Requirements

```
[Question 5/10] Describe the agent's workflow

To determine required tools, describe what the agent will do:
- What files will it read?
- Will it modify or create files?
- Will it run shell commands (git, maven, etc.)?
- Will it search for patterns in files?
- Will it fetch web content?

Describe the workflow in detail:
```

Store response as `workflow_description`.

#### Question 4.2: Tool Analysis

Based on workflow_description, analyze required tools:

**Automatic Tool Detection**:
- Reads files → Needs: **Read**
- Edits files → Needs: **Read, Edit**
- Creates files → Needs: **Write** (may also need Read for templates)
- Runs commands (git, maven, etc.) → Needs: **Bash**
- Searches file content → Needs: **Grep**
- Finds files by pattern → Needs: **Glob**
- Fetches URLs → Needs: **WebFetch**
- Edits Jupyter notebooks → Needs: **NotebookEdit**

Display detected tools:
```
Tool Analysis:

Based on your workflow description, the agent will need:

✅ Read - For reading files
✅ Edit - For modifying files (requires Read)
✅ Bash - For running shell commands

IMPORTANT: Edit tool requires Read to be configured as well.

Proposed tools: Read, Edit, Bash

Is this correct?
1. Yes - Use these tools
2. No - Let me adjust the tool list

Enter 1 or 2:
```

If No:
```
Which tools should be added or removed?

Current: Read, Edit, Bash

Available tools:
- Read (read files)
- Edit (edit files - requires Read)
- Write (create new files)
- Bash (run shell commands)
- Grep (search content in files)
- Glob (find files by pattern)
- WebFetch (fetch web content)
- NotebookEdit (edit Jupyter notebooks)

Enter tools as comma-separated list (e.g., "Read, Write, Bash"):
```

Store final tool list in `required_tools`.

**Tool Fit Validation**:
- Verify Edit doesn't appear without Read
- Warn if tool list seems incomplete for described workflow
- Confirm 100% Tool Fit will be achieved

### Step 5: Essential Rules Definition

#### Question 5.1: Standards to Embed

```
[Question 6/10] Essential Rules

Agents should embed essential rules inline for fast, self-contained execution.

Does this agent need to enforce specific standards?

Examples:
- JavaDoc standards (all public methods documented)
- Logging standards (use LogRecord pattern)
- Code style standards (naming conventions, etc.)
- Error handling standards (specific exception types)

1. Yes - Specify standards to embed
2. No - No specific standards needed

Enter 1 or 2:
```

If yes, for EACH standard:
```
Standard #{n}:

Standard name (e.g., "JavaDoc Standards", "Logging Standards"):
```

```
Source file path (absolute path to authoritative source):
```

```
Section anchor (optional, e.g., "#logrecord-pattern"):
```

```
Key rules to embed (10-30 lines of essential rules from source):

Paste or describe the key rules that this agent must enforce:
```

```
Add another standard?
1. Yes
2. No

Enter 1 or 2:
```

Store in `essential_rules` array with:
- domain (standard name)
- source (full path + anchor)
- rules_content (the actual rules)

### Step 6: Response Format Definition

#### Question 6.1: Metrics and Tracking

```
[Question 7/10] Response Format - Metrics

What metrics should this agent track and report?

Examples from maven-project-builder:
- Iterations: Number of build cycles
- Issues found and fixed: Compilation errors, test failures, warnings
- Execution time: Duration of the build

What metrics are relevant for your agent?
(Describe what should be counted, measured, or tracked)

Metrics to track:
```

Store response as `metrics_description`.

Parse into individual metrics for response template.

#### Question 6.2: Tool Usage Tracking

```
[Question 8/10] Tool Usage Tracking

All agents must track tool usage.

This has been added automatically and will report:
- Read: {count} invocations
- Edit: {count} invocations
- {other tools}: {count} invocations

Confirm: OK to proceed with automatic tool usage tracking?
(Enter 'y' to continue)
```

### Step 7: Workflow Structure

#### Question 7.1: Detailed Workflow Steps

```
[Question 9/10] Detailed Workflow

Now let's structure the workflow you described earlier into concrete steps.

Your earlier description:
"{workflow_description}"

Please provide detailed steps with:
1. What the step does
2. What tools it uses
3. Success/failure conditions
4. Any loops or decision points

You can refine or expand your earlier description here:

Detailed workflow:
```

Store response as `detailed_workflow`.

**Automatic Step Structuring**:
- Parse detailed_workflow
- Extract distinct steps
- Number sequentially (Step 1, Step 2, etc.)
- Add substeps where needed (Step 4.1, 4.2, etc.)
- Identify decision points
- Mark loop points

### Step 8: Critical Constraints

#### Question 8.1: Critical Rules

```
[Question 10/10] Critical Rules and Constraints

What are the absolute constraints and critical rules for this agent?

CRITICAL CONSTRAINTS (What must NEVER happen):
- NEVER operations that would cause issues
- MUST NOT states that are invalid
- Absolute limitations

Examples:
- NEVER skip error fixes
- NEVER modify files without reading first
- MUST NOT proceed if tests fail

Your critical constraints:
```

Store response as `critical_constraints`.

### Step 9: Generate Agent Structure

Based on collected information, generate agent file with proper structure:

**1. Frontmatter (YAML)**
```markdown
---
name: {agent_name}
description: {purpose}\n\nExamples:\n{invocation_examples formatted}
tools: {required_tools comma-separated}
model: sonnet
color: green
---
```

**2. Agent Role Description**
```markdown
You are a {agent_name} agent that {purpose}.

## YOUR TASK

{Expanded task description based on purpose and workflow}
```

**3. Essential Rules Section** (if essential_rules provided)
```markdown
## ESSENTIAL RULES

{for each in essential_rules}
### {domain}
Source: {source}
Last Synced: {today's date}

{rules_content}
{end for}
```

**4. Workflow Instructions**
```markdown
## WORKFLOW (FOLLOW EXACTLY)

{Convert detailed_workflow into numbered steps}

### Step 1: {Step description}
{Step instructions}

### Step 2: {Step description}
{Step instructions}

...
```

**5. Critical Rules Section**
```markdown
## CRITICAL RULES

{critical_constraints formatted as bullet points}
- **Tool Coverage**: All tools in frontmatter must be used (100% Tool Fit)
- **Self-Contained**: All rules embedded inline, no external reads during execution
- **Lessons Learned**: Report discoveries, do not self-modify
```

**6. Tool Usage Tracking Section**
```markdown
## TOOL USAGE TRACKING

**CRITICAL**: Track and report all tools used during execution.

- Record each tool invocation: {list from required_tools}
- Count total invocations per tool
- Include in final report
```

**7. Lessons Learned Reporting Section**
```markdown
## LESSONS LEARNED REPORTING

If during execution you discover insights that could improve future executions:

**When to report lessons learned:**
- New patterns discovered
- Better approaches found
- Edge cases encountered
- Unexpected tool behavior
- Workflow improvements identified

**Include in final report**:
- Discovery: {what was discovered}
- Why it matters: {explanation}
- Suggested improvement: {what should change in this agent}
- Impact: {how this would help future executions}

**Purpose**: Allow users to manually improve this agent based on real execution experience, without agent self-modification.
```

**8. Response Format Section**
```markdown
## RESPONSE FORMAT

After completing all work, return findings in this format:

\```
## {Agent Name} - {Task} Complete

**Status**: ✅ SUCCESS | ❌ FAILURE | ⚠️ PARTIAL

**Summary**:
{Brief 1-2 sentence description of work done}

**Metrics**:
{Generate from metrics_description}
- {Metric 1}: {count}
- {Metric 2}: {count}

**Tool Usage**:
{Generate from required_tools}
- {Tool 1}: {count} invocations
- {Tool 2}: {count} invocations

**Lessons Learned** (for future improvement):
{if any insights discovered:}
- Discovery: {what was discovered}
- Why it matters: {explanation}
- Suggested improvement: {what should change}
- Impact: {how this would help}

{if no lessons learned: "None - execution followed expected patterns"}

**Details**:
{Detailed results, findings, changes made}
\```
```

**File Generation:**

1. Determine full path:
   - If marketplace: `~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/agents/{agent_name}.md`
   - If project: `.claude/agents/{agent_name}.md`

2. If marketplace and bundle doesn't exist:
   - Create bundle directory structure: `~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/`
   - Create subdirectories: `commands/`, `agents/`, `skills/`
   - Create `.claude-plugin/plugin.json` with minimal structure (see bundling-architecture.adoc)
   - Create bundle README.md

3. Generate content with all sections above (MUST start with YAML frontmatter)

4. Write file using Write tool

5. Verify frontmatter is present and valid

### Step 10: Display Creation Summary

```
╔════════════════════════════════════════════════════════════╗
║          Agent Created Successfully!                       ║
╔════════════════════════════════════════════════════════════╝

Agent: {agent_name}
Location: {full_path}
Length: {line_count} lines

Configuration:
- Tools: {required_tools}
- Tool Fit: 100% (all required tools configured)
- Essential Rules: {count} standard(s) embedded
- Response Format: Structured with {metric_count} metrics
- Lessons Learned: Reporting enabled

Compliance:
✅ Self-contained (no external reads during execution)
✅ Structured response format
✅ Tool usage tracking
✅ Lessons learned reporting (not self-modifying)
✅ Essential rules embedded inline

Next Steps:
1. Review the generated agent at: {full_path}
2. Running /diagnose-agents to verify agent structure...

╚════════════════════════════════════════════════════════════
```

### Step 11: Auto-Verify with Agents Doctor

1. Automatically invoke `/diagnose-agents {agent_name}`
2. Wait for diagnose-agents to complete analysis
3. Display results

```
Agents Doctor Analysis Results:

Tool Fit Score: {score}% ({rating})
- {analysis of tool coverage}

Essential Rules: {rules_verified} verified
- {sync status}

Internal Quality:
- Duplication issues: {count}
- Ambiguity issues: {count}
- Precision score: {percentage}%
- Compliance score: {percentage}%

Total Issues: {count}
- Critical: {critical_count}
- Warnings: {warning_count}
- Suggestions: {suggestion_count}

{if issues found}
Would you like diagnose-agents to fix these issues now?
1. Yes - Fix automatically
2. No - I'll review manually later

Enter 1 or 2:
{end if}
```

If issues exist and user chooses Yes, diagnose-agents continues in fix mode.

### Step 12: Final Completion

```
╔════════════════════════════════════════════════════════════╗
║          Setup Complete!                                   ║
╔════════════════════════════════════════════════════════════╝

Your new agent is ready: {agent_name}

The agent follows architectural best practices:
✅ YAML frontmatter for agent discovery
✅ 100% Tool Fit (all required tools configured)
✅ Self-contained (Essential Rules embedded)
✅ Structured response format
✅ Tool usage tracking
✅ Lessons learned reporting
✅ Industry best practices compliance
✅ Verified by diagnose-agents

The agent will be invoked automatically by Claude Code when appropriate.

Happy coding! 🚀

╚════════════════════════════════════════════════════════════
```

## CRITICAL RULES

- **READ ARCHITECTURE DOCUMENT** at Step 2 - ensures compliance with patterns
- **ALWAYS include YAML frontmatter** as the FIRST element in the file (required for agent discovery)
- **ALWAYS collect ALL information** before generating the agent
- **NEVER skip tool fit analysis** - 100% is required
- **ALWAYS embed Essential Rules** inline - no external reads during execution
- **NEVER include Continuous Improvement Rule** - agents use Lessons Learned Reporting
- **ALWAYS include response format template** - structured output is required
- **ALWAYS include tool usage tracking** - visibility into agent behavior
- **ALWAYS run diagnose-agents** after creation to verify quality
- **DEFAULT to marketplace bundles** unless explicitly project-specific
- **VERIFY frontmatter syntax** is valid YAML with name, description, tools, model, and color fields
- **APPLY industry best practices** from architecture document
- **ENSURE self-contained agents** - no external file reads during execution

## VALIDATION RULES

Before writing the agent file:

1. **Name Validation:**
   - Lowercase only
   - Hyphens for spaces
   - No special characters
   - Unique (doesn't exist)
   - Descriptive and concise

2. **Tool Fit Validation:**
   - All tools required by workflow are configured
   - No unnecessary tools configured
   - Edit requires Read to be present
   - 100% Tool Fit Score achievable

3. **Essential Rules Validation:**
   - Each rule set has source reference
   - Each rule set has Last Synced date
   - Content is 10-30 lines per domain (essential subset)
   - Curated for agent's specific needs

4. **Structure Validation:**
   - Valid YAML frontmatter
   - All required sections present
   - Proper markdown formatting
   - Response format template included
   - Tool usage tracking included
   - Lessons learned reporting included
   - No Continuous Improvement Rule present

5. **Industry Best Practices Validation:**
   - No vague language ("appropriately", "if needed")
   - All thresholds quantified
   - Concrete action verbs
   - Clear success criteria
   - Explicit error handling
   - Measurable outcomes

## REFERENCE: Agents Architecture

This command implements the patterns defined in:
`~/git/cui-llm-rules/claude/agents-architecture.md`

Key patterns applied:
- **Essential Rules Pattern**: Embed + sync for performance
- **Tool Fit Requirement**: 100% match between tools and workflow
- **Self-Contained Agents**: No external reads during execution
- **Lessons Learned Reporting**: Agents don't self-modify
- **Response Format Standards**: Structured, parseable output
- **Industry Best Practices**: Clarity, precision, measurability

## USAGE

Simply invoke: `/create-agent`

The wizard will guide you through all questions and generate a compliant agent.
