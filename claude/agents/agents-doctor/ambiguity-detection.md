# Ambiguity Detection Module

**Purpose**: Flag vague, ambiguous language that could have multiple interpretations.

**Parent Command**: agents-doctor

**Reference**: Industry Best Practices for Agent Quality (from agents-architecture.md)

**Usage**: This module is read and executed by the main agents-doctor command. Do not use standalone.

---

## Analysis Workflow

### A. Scan for Vague Phrases

Search agent instructions for ambiguous language:

| Pattern | Examples | Why Ambiguous |
|---------|----------|---------------|
| "if needed" | "Run tests if needed" | When is it needed? |
| "appropriately" | "Handle errors appropriately" | What defines appropriate? |
| "reasonably" | "Reasonable timeout" | What's reasonable? |
| "fairly" | "Fairly short description" | How short? |
| "sufficiently" | "Sufficiently detailed" | How detailed? |
| "as necessary" | "Retry as necessary" | When necessary? |
| "when appropriate" | "Use cache when appropriate" | When is it appropriate? |

### B. Detect Generic Action Verbs

Flag vague verbs that lack specificity:
- ❌ "handle", "manage", "deal with", "work with", "process"
- ✅ "validate", "transform", "calculate", "parse", "extract", "verify"

Examples:
- "Handle errors" → Ambiguous (which errors? how?)
- "Manage files" → Ambiguous (create? delete? move?)
- "Process data" → Ambiguous (transform? validate? store?)

### C. Identify Undefined Scope

Flag scope without boundaries:
- "relevant files" → Which files are relevant?
- "important sections" → What makes a section important?
- "key points" → Which points are key?
- "necessary information" → What information is necessary?

### D. Find Unmeasurable Goals

Flag goals without objective criteria:
- "good quality" → What defines good?
- "better performance" → Better by how much?
- "clean code" → What are cleanliness criteria?
- "sufficient coverage" → What percentage is sufficient?

### E. Report Ambiguities

Display findings:
```
Ambiguity Detection:

❌ AMBIGUOUS: Line 67: "Run tests if necessary"
   Problem: "necessary" is undefined
   Impact: Agent doesn't know when to run tests
   Fix: "Run tests after every code modification"

❌ AMBIGUOUS: Line 103: "Handle timeouts appropriately"
   Problem: "appropriately" is subjective
   Impact: Unclear handling strategy
   Fix: "On timeout: retry once with 2x duration, then fail"

❌ VAGUE VERB: Line 145: "Manage error conditions"
   Problem: "manage" is non-specific
   Impact: Unclear what action to take
   Fix: "Catch IOException → log and continue. Catch TimeoutException → retry once."

❌ UNDEFINED SCOPE: Line 178: "Process relevant files"
   Problem: "relevant" is not defined
   Impact: Agent must guess which files
   Fix: "Process all .java files in src/main/java, excluding *Test.java"

⚠️ UNMEASURABLE: Line 200: "Ensure good code quality"
   Problem: "good" has no criteria
   Impact: Cannot verify success
   Fix: "Ensure: 0 checkstyle errors, 0 PMD warnings, coverage > 80%"

Summary:
- Ambiguous conditionals: {count}
- Generic verbs: {count}
- Undefined scope: {count}
- Unmeasurable goals: {count}
- Total ambiguity issues: {count}
```

### F. Categorize Issues

- **CRITICAL**: Ambiguous instructions that block agent execution
- **WARNING**: Vague language that reduces precision
- Impact: Agent makes wrong assumptions, user approval needed
- Fix: Replace with specific, measurable instructions

### G. Update Statistics

Track:
- `ambiguity_issues`: Count of ambiguity problems found
- Add to total issues count

---

## Expected Output Format

```json
{
  "analysis": "ambiguity",
  "issues": [
    {
      "type": "AMBIGUOUS_CONDITIONAL",
      "line": 67,
      "text": "Run tests if necessary",
      "problem": "necessary is undefined",
      "impact": "Agent doesn't know when to run tests",
      "fix": "Run tests after every code modification",
      "severity": "CRITICAL"
    },
    {
      "type": "VAGUE_VERB",
      "line": 145,
      "text": "Manage error conditions",
      "problem": "manage is non-specific",
      "impact": "Unclear what action to take",
      "fix": "Catch IOException → log and continue. Catch TimeoutException → retry once.",
      "severity": "WARNING"
    }
  ],
  "summary": {
    "ambiguous_conditionals": 3,
    "generic_verbs": 2,
    "undefined_scope": 1,
    "unmeasurable_goals": 2,
    "total": 8
  }
}
```
