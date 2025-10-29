---
name: build-and-verify
description: Execute comprehensive project verification by running Maven build and optionally committing changes
---

# Verify Project Command

Execute a comprehensive project verification workflow by delegating to specialized agents:
- **maven-project-builder** agent: Runs Maven build, analyzes output, fixes all issues
- **commit-changes** agent: Commits and pushes changes (if requested)

## PARAMETERS

- **push** (optional): When provided, automatically commits all changes with a descriptive message and pushes to remote repository after successful verification

## WORKFLOW INSTRUCTIONS

### Step 1: Parse Parameters

1. Check if the user provided "push" as a parameter
2. Store this as a boolean flag for later use

### Step 2: Invoke maven-project-builder Agent

1. Use the Task tool to invoke the `maven-project-builder` agent
2. Set `subagent_type: "maven-project-builder"`
3. Provide a clear prompt:
   ```
   Execute comprehensive project verification by running ./mvnw -Ppre-commit clean install.
   Analyze all output, fix all errors and warnings, and track execution time in .claude/run-configuration.md.
   ```
4. Wait for the agent to complete
5. The agent will handle:
   - Reading configuration from .claude/run-configuration.md
   - Executing Maven build with proper timeout
   - Analyzing all errors, warnings, JavaDoc issues, and OpenRewrite markers
   - Fixing all issues and repeating until clean
   - Updating execution duration if changed >10%

**SUCCESS CRITERIA**: Agent reports "✅ SUCCESS" status with clean build

**FAILURE HANDLING**: If agent reports failure, display the error report to the user and stop (do not proceed to commit/push)

### Step 3: Commit and Push (Optional)

**Decision Point:**
- If "push" parameter was NOT provided → Skip to final report
- If "push" parameter was provided → Continue

**Execution:**

1. Use the Task tool to invoke the `commit-changes` agent
2. Set `subagent_type: "commit-changes"`
3. Provide a clear prompt:
   ```
   Commit all changes from project verification and push to remote repository.
   Analyze the changes to create an appropriate commit message following Git Commit Standards.
   Include both code fixes and any .claude/run-configuration.md updates in the commit.
   After committing, push the changes to the remote repository.
   ```
4. Wait for the agent to complete
5. The agent will handle:
   - Checking for uncommitted changes
   - Cleaning any build artifacts
   - Creating a commit with proper Git Commit Standards format
   - Pushing to remote repository
   - Reporting commit hash and push status

**SUCCESS CRITERIA**: Agent reports "✅ SUCCESS" with commit created and pushed

**FAILURE HANDLING**: If agent reports failure, display the error to the user

### Step 4: Display Summary Report

After all agents complete, provide a consolidated summary to the user:

```
## /build-and-verify Complete

**Verification Status**: {status from maven-project-builder agent}
**Commit/Push Status**: {status from commit-changes agent, or "N/A - not requested"}

**Project Verification Summary**:
{Key metrics from maven-project-builder agent report}

{If push was performed:}
**Commit Details**:
{Key details from commit-changes agent report}
```

## CRITICAL RULES

- **ALWAYS invoke maven-project-builder agent** - never duplicate its verification logic
- **ALWAYS wait for agents to complete** - do not proceed until agent reports back
- **ONLY invoke commit-changes if push parameter provided** - respect user intent
- **NEVER implement verification logic directly** - delegate to maven-project-builder agent
- **NEVER implement commit/push logic directly** - delegate to commit-changes agent
- **ALWAYS display agent reports** - show user what each agent accomplished

## Agent Delegation Benefits

- **No duplication**: Single source of truth for verification logic (maven-project-builder)
- **No duplication**: Single source of truth for commit/push logic (commit-changes)
- **Maintainability**: Updates to verification or commit logic only need to be made in one place
- **Reusability**: Other commands can use the same agents
- **Consistency**: All verification follows the same standards regardless of invocation method

## Usage

### Basic Usage
Simply invoke: `/build-and-verify`

No arguments needed. The command will automatically delegate to the maven-project-builder agent.

### Usage with Push
Invoke with push parameter: `/build-and-verify push`

When the `push` parameter is provided, the command will:
- Delegate to maven-project-builder agent for complete verification
- Delegate to commit-changes agent to commit and push all changes

This is useful for automated workflows or when you want to immediately persist verification fixes.
