---
name: plugin-create-agent
description: Guide users through creating a well-structured agent following architectural best practices
---

# Create Agent Command

Interactive wizard for creating well-structured Claude Code agents following marketplace architecture and best practices.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=plugin-create-agent update="[your improvement]"` with:
1. Improved questionnaire patterns for gathering agent requirements
2. Better validation strategies for architecture compliance
3. More effective agent file generation templates
4. Enhanced duplication detection across existing agents
5. Any lessons learned about agent creation workflows

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

**scope** - Where to create agent (marketplace/global/project, default: marketplace)

## WORKFLOW

### Step 1: Load Architecture Standards

```
Skill: cui-marketplace-architecture
```

### Step 2: Interactive Questionnaire

**A. Agent name** - kebab-case (e.g., `code-reviewer`, `test-runner`)
   - **Validation**: Must not be empty, must match kebab-case pattern
   - **Error**: If invalid: "Agent name must be kebab-case (lowercase-with-hyphens)" and retry

**B. Bundle selection** - List available bundles
   - **Validation**: Must select valid bundle from list
   - **Error**: If invalid selection: "Please select a bundle from the list" and retry

**C. Description** - One sentence describing agent purpose (<100 chars)
   - **Validation**: Must not be empty, must be ≤100 chars
   - **Error**: If invalid: "Description required (max 100 chars): {current_length}/100" and retry

**D. Agent type**:
1. Analysis agent (code review, diagnostics)
2. Execution agent (build, test, deploy)
3. Coordination agent (multi-step workflows)
4. Research agent (information gathering)
   - **Validation**: Must select 1-4
   - **Error**: If invalid: "Please select agent type (1-4)" and retry

### Step 3: Collect Capability Information

**A. What does this agent do?** (detailed capabilities)
   - **Validation**: Must not be empty
   - **Error**: If empty: "Agent capabilities description required" and retry

**B. Required tools** - Which tools does agent need?
- Read, Write, Edit, Glob, Grep, Bash, WebFetch, etc.
   - **Validation**: Must list at least one tool
   - **Error**: If none: "At least one tool required" and retry
   - **CRITICAL Validation - Task Tool**:
     - If user lists `Task` as a tool:
       ```
       ❌ ERROR: Agents CANNOT use the Task tool

       Platform Limitation: Task tool is unavailable to agents at runtime (Rule 6)
       - Agents are focused executors (do ONE task)
       - Commands orchestrate agents (delegate using Task)
       - Agent attempting Task delegation = guaranteed runtime failure

       Refactoring needed:
       - If agent needs to delegate: Create a COMMAND instead (commands can use Task)
       - If agent is focused: Remove Task from tools list

       Reference: architecture-rules.md Rule 6
       ```
       - Force user to either remove Task from list OR abort and create command instead
   - **CRITICAL Validation - Maven Calls**:
     - If user lists `Bash` as a tool AND agent name ≠ "maven-builder":
       ```
       ⚠️  WARNING: Maven Execution Pattern Check

       You selected Bash tool for an agent. Per Rule 7:
       - Agents CANNOT call Maven directly (Bash(./mvnw:*) is always a bug)
       - ONLY maven-builder agent may execute Maven
       - All other agents must return results to caller who orchestrates maven-builder

       Does this agent need to execute Maven commands?
       - [Y]es, it needs to run Maven → ❌ ERROR: Cannot proceed
         "Create maven-builder agent OR restructure as command that orchestrates maven-builder"
       - [N]o, it uses Bash for other purposes → ✅ Continue with Bash tool

       Reference: architecture-rules.md Rule 7
       ```
       - If user confirms Maven execution needed: abort with error
       - If user confirms non-Maven Bash usage: continue

   - **CRITICAL Validation - CONTINUOUS IMPROVEMENT RULE Pattern**:
     - After generating agent template, validate CONTINUOUS IMPROVEMENT RULE section:
       ```
       ⚠️  Pattern 22: Agent Self-Invocation Check

       Per Rule 6: Agents CANNOT invoke commands (SlashCommand tool unavailable at runtime)

       CONTINUOUS IMPROVEMENT RULE must instruct agent to:
       ✅ REPORT improvement findings to caller
       ✅ RETURN structured improvement suggestions
       ❌ NOT invoke /plugin-update-agent or any slash command directly

       Detection patterns (must NOT appear in agent):
       - "YOU MUST.*using /plugin-"
       - "invoke /plugin-"
       - "call /plugin-"
       - "SlashCommand: /plugin-"

       Correct pattern: Agent reports improvements, CALLER invokes command

       Reference: agent-analysis-patterns.md Pattern 22
       ```
     - This validation is applied post-generation in Step 5 to ensure template compliance

**C. When should this agent be used?** (trigger conditions)
   - **Validation**: Must provide use cases
   - **Error**: If empty: "Usage conditions required" and retry

**D. Expected inputs/outputs**
   - **Validation**: Must describe inputs and outputs
   - **Error**: If empty: "Input/output description required" and retry

### Step 4: Validate Architecture Compliance and Check Duplication

**A. Architecture validation** using cui-marketplace-architecture skill:
- Self-contained (no cross-agent dependencies)
- Proper tool fit (agent needs listed tools)
- Essential rules compliance

**B. Duplication detection:**
1. Use Glob to find all agents in target bundle
2. Use Grep to search for similar agent names or descriptions
3. **If duplicates found**:
   - Display: "⚠️ Similar agents found: {list agent names with descriptions}"
   - Prompt: "[C]ontinue anyway/[R]ename agent/[A]bort creation?"
   - Track in duplication_checks counter

**Error handling:**
- If Glob/Grep fails: Log warning, continue (increment validations_performed with note)

### Step 5: Generate Agent File

Create `{bundle}/agents/{agent-name}.md` with:

**A. YAML frontmatter**:
- name, description, model (optional), tools

**B. Agent purpose** section

**C. CONTINUOUS IMPROVEMENT RULE** section (REQUIRED):
```markdown
## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this agent and discover a more precise, better, or more efficient approach, **REPORT the improvement to your caller** with:
1. [Improvement area 1 specific to agent purpose]
2. [Improvement area 2 specific to agent purpose]
3. [Improvement area 3 specific to agent purpose]
4. [Improvement area 4 specific to agent purpose]
5. Any lessons learned about [agent domain] workflows

Return structured improvement suggestion in your analysis result:
```
IMPROVEMENT OPPORTUNITY DETECTED

Area: [specific area]
Current limitation: [what doesn't work well]
Suggested enhancement: [specific improvement]
Expected impact: [benefit of change]
```

The caller can then invoke `/plugin-update-agent agent-name={agent-name}` based on your report.

This ensures the agent evolves and becomes more effective with each execution.
```

**D. Workflow** section (numbered steps)

**E. Tool usage** section

**F. Critical rules** section

Trust AI to generate appropriate structure from collected information and populate CONTINUOUS IMPROVEMENT RULE with 3-5 improvement areas relevant to the agent's specific purpose.

**Error handling:**
- **If Write fails**: Display "Failed to create agent file: {error}" and prompt "[R]etry/[A]bort"
- **If directory doesn't exist**: Create directories first, then retry Write
- Track successful creation in files_created counter

### Step 6: Cleanup and Display Summary

**Cleanup:**
- No temporary files created (all state in memory)
- No cleanup required

**Display summary:**
```
╔════════════════════════════════════════════════════════════╗
║          Agent Created Successfully                        ║
╚════════════════════════════════════════════════════════════╝

Agent: {agent-name}
Location: {file-path}
Bundle: {bundle-name}
Type: {agent-type}

Statistics:
- Questions answered: {questions_answered}
- Validations performed: {validations_performed}
- Duplication checks: {duplication_checks}
- Files created: {files_created}

Next steps:
1. Review agent file: {file-path}
2. Run diagnosis: /plugin-diagnose-agents agent-name={agent-name}
3. Test agent functionality
```

### Step 7: Run Agent Diagnosis

```
SlashCommand: /cui-plugin-development-tools:plugin-diagnose-agents agent-name={agent-name}
```

**Error handling:**
- **If diagnosis fails**: Display warning but don't abort (agent was already created)

## STATISTICS TRACKING

Track throughout workflow:
- `questions_answered`: Count of questionnaire responses collected
- `validations_performed`: Count of validation checks executed
- `files_created`: Count of agent files successfully created
- `duplication_checks`: Count of duplication detection runs

Display all statistics in final summary.

## CRITICAL RULES

**Architecture:**
- Agents must be self-contained
- List ALL required tools in frontmatter
- **NEVER include Task tool (Rule 6)** - Agents cannot delegate, guaranteed runtime failure
- **NEVER allow Maven calls in non-maven-builder agents (Rule 7)** - Bypasses centralized build execution
- Follow essential rules from marketplace architecture

**Structure:**
- Valid YAML frontmatter required
- Clear numbered workflow
- Tool usage documented
- Critical rules defined

**Tool Fit:**
- Only list tools agent actually uses
- Verify tool fit score >80%
- No over-tooling

**Validation:**
- ALL questionnaire responses must be validated
- Clear error messages for invalid inputs
- Retry on validation failures
- Check for duplicate agents before creation

**Error Handling:**
- Prompt user on file operation failures
- Allow retry/abort decisions
- Track all validations and checks

## USAGE EXAMPLES

**Create marketplace agent:**
```
/plugin-create-agent
```

**Create in specific scope:**
```
/plugin-create-agent scope=global
```

## RELATED

- `/plugin-diagnose-agents` - Validates agent
- `/plugin-update-agent` - Update existing agents
- `cui-marketplace-architecture` skill - Architecture rules
