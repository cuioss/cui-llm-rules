# Compliance Checking Module

**Purpose**: Verify agent follows industry standards from authoritative sources.

**Parent Command**: agents-doctor

**Reference**: Industry Best Practices for Agent Quality (from agents-architecture.md)

**Usage**: This module is read and executed by the main agents-doctor command. Do not use standalone.

---

## Analysis Workflow

### A. Check Against Quality Checklist

Verify agent against comprehensive checklist from architecture doc:

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

### B. Check for Common Anti-Patterns

Scan for specific anti-patterns from architecture doc:

1. **Anti-Pattern: Vague Instructions**
   - Pattern: "Process files as needed", "Handle appropriately"
   - Should be: Specific files, explicit handling

2. **Anti-Pattern: Undefined Success**
   - Pattern: "Build succeeds", "Tests pass"
   - Should be: "exit code = 0", "test_failures = 0"

3. **Anti-Pattern: Generic Error Handling**
   - Pattern: "Handle exceptions appropriately", "Deal with errors"
   - Should be: Enumerated error types with specific handling

4. **Anti-Pattern: Ambiguous Conditions**
   - Pattern: "If file is too large", "When necessary"
   - Should be: "If file_size > 10MB", "After every code change"

5. **Anti-Pattern: Unmeasurable Criteria**
   - Pattern: "Ensure good quality", "Better performance"
   - Should be: "0 violations", "latency < 100ms"

### C. Report Compliance

Display findings:
```
Industry Best Practices Compliance:

**Checklist Compliance**: 32/40 items (80%)

Failed Checks:
❌ Vague language present (8 instances)
❌ 3 thresholds not quantified
❌ 2 error types lack handling strategy
❌ Success criteria not fully measurable
❌ Essential Rules section: 45 lines (exceeds 30-line guideline)

**Anti-Pattern Detection**:
Found 5 anti-patterns:
1. Line 67: Vague instruction - "Process as needed"
2. Line 89: Undefined success - "Build completes successfully"
3. Line 112: Generic error handling - "Handle exceptions"
4. Line 145: Ambiguous condition - "If timeout is too long"
5. Line 178: Unmeasurable - "Ensure reasonable quality"

**Compliance Rating**: 80% (Good, but improvements needed)

Recommendations:
- Replace 8 vague phrases with specific alternatives
- Quantify 3 thresholds with explicit numbers
- Define handling for 2 error types
- Make success criteria objectively verifiable
- Trim Essential Rules to essential subset (30 lines max)
```

### D. Categorize Issues

- **WARNING**: Non-compliance with industry best practices
- Impact: Reduces agent quality, maintainability, and reliability
- Fix: Apply specific recommendations from compliance report

### E. Update Statistics

Track:
- `checklist_compliance_percent`: Percentage of passed checks
- `antipatterns_found`: Count of anti-patterns detected
- `compliance_issues`: Total non-compliance issues
- Add to total issues count

---

## Expected Output Format

```json
{
  "analysis": "compliance",
  "checklist": {
    "total_items": 40,
    "passed": 32,
    "failed": 8,
    "compliance_percent": 80
  },
  "antipatterns": [
    {
      "id": 1,
      "type": "vague_instruction",
      "line": 67,
      "text": "Process as needed",
      "should_be": "Process all .java files in src/main/java"
    },
    {
      "id": 2,
      "type": "undefined_success",
      "line": 89,
      "text": "Build completes successfully",
      "should_be": "exit code = 0 AND no ERROR lines in output"
    }
  ],
  "rating": "Good, but improvements needed",
  "recommendations": [
    "Replace 8 vague phrases with specific alternatives",
    "Quantify 3 thresholds with explicit numbers",
    "Define handling for 2 error types",
    "Make success criteria objectively verifiable",
    "Trim Essential Rules to essential subset (30 lines max)"
  ],
  "summary": {
    "compliance_percent": 80,
    "antipatterns_found": 5,
    "total_issues": 13
  }
}
```
