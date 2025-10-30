---
name: cui-fix-intellij-diagnostics
description: Retrieve and fix IDE diagnostics automatically, suppressing only when no reasonable fix is available
---

# Fix IntelliJ Diagnostics Command

Retrieves diagnostics from IntelliJ IDE via MCP, analyzes issues, applies fixes, and handles unfixable issues through suppression.

## PARAMETERS

**file** - Specific file to check (optional, checks all open files if not provided)

**push** - Auto-push after fixes (optional flag)

## CRITICAL: File Must Be Active in IDE

IntelliJ MCP server ONLY works on currently active/focused file. If file not active, getDiagnostics will timeout (~60-120 seconds).

**Workflow**: Manually click file in IntelliJ → Call this command

## WORKFLOW

### Step 1: Get Diagnostics from IDE

**A. If file parameter provided**: Open file in IDE, get diagnostics for that file

**B. If no parameter**: Get diagnostics for all open files

Use MCP ide tool:
```
mcp__ide__getDiagnostics uri="file:///{absolute_path}"
```

### Step 2: Categorize Issues

Group by:
- Errors vs Warnings
- Fixable vs Unfixable
- By file (if multiple)

### Step 3: Attempt Fixes

For each diagnostic:

**A. Analyze issue** - Understand problem and possible solutions

**B. Determine if fixable**:
- Code issues → Fix code
- Import issues → Add imports
- Type issues → Fix types
- Style issues → Fix formatting

**C. Apply fix** using Edit tool

### Step 4: Re-verify Build

```
Task:
  subagent_type: maven-project-builder
  description: Verify fixes
  prompt: Run maven build and verify no errors
```

### Step 5: Handle Unfixable Issues

For issues that cannot be reasonably fixed:

**A. Determine suppression approach** based on tool:
- IntelliJ: `//noinspection {InspectionName}`
- SpotBugs: `@SuppressFBWarnings`
- Checkstyle: `// CHECKSTYLE:OFF`
- PMD: `// NOPMD`
- SonarQube: `@SuppressWarnings("java:S####")`
- ErrorProne: `@SuppressWarnings("ErrorProneName")`

**B. Add suppression comment** with justification

### Step 6: Re-check Diagnostics

Call getDiagnostics again to verify issues resolved.

### Step 7: Build and Commit

**A. Final build verification**

**B. Commit changes** (if push parameter):
```
Task:
  subagent_type: commit-changes
  description: Commit diagnostic fixes
  prompt: Commit fixes with message describing issues resolved
```

### Step 8: Display Report

```
╔════════════════════════════════════════════════════════════╗
║          Diagnostic Fix Report                             ║
╚════════════════════════════════════════════════════════════╝

Files analyzed: {count}
Issues found: {count}
Issues fixed: {count}
Issues suppressed: {count}
Remaining issues: {count}

Build status: {SUCCESS/FAILURE}
Committed: {yes/no}
```

## CRITICAL RULES

**MCP Constraints:**
- File must be active in IDE
- Timeout ~60-120 seconds if file not active
- Use mcp__ide__getDiagnostics tool

**Fix Priority:**
1. Try reasonable fix first
2. Only suppress if no reasonable fix
3. Always add justification for suppression

**Build Verification:**
- Must verify build after fixes
- Re-check diagnostics after fixes
- Ensure no new issues introduced

**Suppression:**
- Use appropriate tool-specific syntax
- Add comment explaining why suppressed
- Document in commit message

## USAGE EXAMPLES

**Check all open files:**
```
/cui-fix-intellij-diagnostics
```

**Check specific file:**
```
/cui-fix-intellij-diagnostics file=src/main/java/Foo.java
```

**Auto-push:**
```
/cui-fix-intellij-diagnostics file=Foo.java push
```

## ARCHITECTURE

Uses:
- MCP jetbrains server (getDiagnostics)
- maven-project-builder agent (build verification)
- commit-changes agent (git operations)

## RELATED

- maven-project-builder agent
- commit-changes agent
- MCP jetbrains server documentation
