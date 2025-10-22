# Precision Analysis Module

**Purpose**: Measure instruction specificity and calculate precision score.

**Parent Command**: agents-doctor

**Reference**: Industry Best Practices for Agent Quality (from agents-architecture.md)

**Usage**: This module is read and executed by the main agents-doctor command. Do not use standalone.

---

## Analysis Workflow

### A. Instruction Specificity Check

For each instruction in workflow, verify:

1. **Verb Specificity**
   - ✅ Concrete verbs: validate, calculate, parse, transform
   - ❌ Vague verbs: handle, manage, process, deal with

2. **Parameter Specificity**
   - ✅ Bounded: "timeout: 120 seconds", "retry: 3 times"
   - ❌ Unbounded: "reasonable timeout", "several retries"

3. **Condition Specificity**
   - ✅ Explicit: "if error_count > 0", "if file_size > 10MB"
   - ❌ Implicit: "if needed", "when appropriate"

4. **Format Specificity**
   - ✅ Defined: "JSON with keys: {status, count}", "YYYY-MM-DD format"
   - ❌ Undefined: "structured output", "appropriate format"

### B. Measurability Check

For each success criterion, error condition, and threshold:

1. **Success Criteria**
   - ✅ Measurable: "exit code = 0", "test_failures = 0"
   - ❌ Subjective: "build succeeds", "tests pass"

2. **Error Conditions**
   - ✅ Enumerated: "FileNotFoundException OR IOException"
   - ❌ Generic: "exceptions", "errors"

3. **Thresholds**
   - ✅ Explicit numbers: "timeout: 120000ms", "max_size: 10MB"
   - ❌ Vague quantities: "long timeout", "large files"

### C. Calculate Precision Score

```
Total Instructions: {count}
Specific Instructions: {count}
Vague Instructions: {count}

Precision Score = (Specific / Total) * 100

Example:
- Total: 20 instructions
- Specific: 15
- Vague: 5
Score: (15 / 20) * 100 = 75%
```

### D. Precision Ratings

- **90-100%**: Excellent - Highly precise instructions
- **75-89%**: Good - Mostly precise with minor vagueness
- **60-74%**: Fair - Significant vagueness present
- **<60%**: Poor - Instructions lack precision

### E. Report Precision Analysis

Display findings:
```
Precision Analysis:

**Instruction Specificity**: 15/20 (75%)

Issues Found:
❌ Line 45: "Handle errors" - Generic verb
❌ Line 67: "Reasonable timeout" - Unbounded parameter
❌ Line 89: "When necessary" - Implicit condition
❌ Line 112: "Appropriate format" - Undefined format
❌ Line 156: "Good quality" - Unmeasurable criterion

**Measurability**: 8/10 criteria measurable (80%)

Issues Found:
⚠️ Line 78: Success = "build completes" (not measurable)
⚠️ Line 134: "Several retries" (quantity not specified)

**Precision Score**: 73% (Fair)

Recommendation: Tighten language in lines: 45, 67, 89, 112, 156
Replace vague terms with specific, measurable alternatives.
```

### F. Categorize Issues

- **WARNING**: Low precision score reduces agent effectiveness
- Impact: Agent interpretation varies, inconsistent behavior
- Fix: Replace vague language with specific, measurable terms

### G. Update Statistics

Track:
- `precision_score`: Percentage (0-100)
- `precision_issues`: Count of imprecise instructions
- Add to total issues count

---

## Expected Output Format

```json
{
  "analysis": "precision",
  "specificity": {
    "total_instructions": 20,
    "specific_instructions": 15,
    "vague_instructions": 5,
    "percentage": 75
  },
  "measurability": {
    "total_criteria": 10,
    "measurable": 8,
    "subjective": 2,
    "percentage": 80
  },
  "precision_score": 73,
  "rating": "Fair",
  "issues": [
    {
      "line": 45,
      "text": "Handle errors",
      "category": "generic_verb",
      "severity": "WARNING"
    },
    {
      "line": 67,
      "text": "Reasonable timeout",
      "category": "unbounded_parameter",
      "severity": "WARNING"
    }
  ],
  "summary": {
    "precision_score": 73,
    "rating": "Fair",
    "total_issues": 7,
    "recommendations": "Tighten language in lines: 45, 67, 89, 112, 156. Replace vague terms with specific, measurable alternatives."
  }
}
```
