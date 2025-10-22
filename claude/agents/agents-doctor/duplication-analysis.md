# Duplication Analysis Module

**Purpose**: Detect and report duplicated instructions, rules, or content within the agent file.

**Parent Command**: agents-doctor

**Usage**: This module is read and executed by the main agents-doctor command. Do not use standalone.

---

## Analysis Workflow

### A. Scan for Exact Duplicates

1. Parse all sections of the agent file
2. Extract individual instructions/rules (by sentence or paragraph)
3. Hash each instruction
4. Identify exact matches across different sections

### B. Detect Semantic Duplicates

Look for instructions with different wording but same meaning:
- "Always use Read before Edit" vs "Edit requires prior Read"
- "Run tests after changes" vs "After making changes, execute tests"
- "Log errors to file" vs "Write error messages to log file"

### C. Find Redundant Clarifications

Identify over-explanation of the same concept:
- Same rule appears in CRITICAL RULES and repeated in workflow steps
- Same requirement stated multiple times with different emphasis
- Same example shown in multiple locations

### D. Report Duplications

Display findings:
```
Internal Duplication Analysis:

❌ EXACT DUPLICATE: "Always use Read before Edit"
   Locations:
   - Line 45: Step 3 instructions
   - Line 123: CRITICAL RULES #7
   - Line 200: Step 5 reminder
   Recommendation: State once in CRITICAL RULES, reference in workflow

⚠️ SEMANTIC DUPLICATE: Same concept, different wording
   - Line 67: "Run tests after making code changes"
   - Line 102: "After modifying code, execute the test suite"
   Recommendation: Consolidate into single statement

⚠️ REDUNDANT: Tool usage rule repeated 3 times
   - Lines 78, 145, 223 all explain when to use Bash tool
   Recommendation: Define once, reference elsewhere

Summary:
- Exact duplicates: {count}
- Semantic duplicates: {count}
- Redundant clarifications: {count}
- Total duplication issues: {count}
```

### E. Categorize Issues

- **WARNING**: Duplication increases maintenance burden and token usage
- Impact: Confusion when rules conflict, harder to update
- Fix: Consolidate into single authoritative statement

### F. Update Statistics

Track:
- `duplication_issues`: Count of duplication problems found
- Add to total issues count

---

## Expected Output Format

```json
{
  "analysis": "duplication",
  "issues": [
    {
      "type": "EXACT_DUPLICATE",
      "content": "Always use Read before Edit",
      "locations": [45, 123, 200],
      "recommendation": "State once in CRITICAL RULES, reference in workflow"
    },
    {
      "type": "SEMANTIC_DUPLICATE",
      "instances": [
        {"line": 67, "text": "Run tests after making code changes"},
        {"line": 102, "text": "After modifying code, execute the test suite"}
      ],
      "recommendation": "Consolidate into single statement"
    }
  ],
  "summary": {
    "exact_duplicates": 3,
    "semantic_duplicates": 2,
    "redundant_clarifications": 1,
    "total": 6
  }
}
```
