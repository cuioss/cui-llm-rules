# Content Quality Guide

Quality analysis dimensions for LLM-based content review in skill subdirectories.

## Purpose

Provides criteria for Claude to analyze content quality across four dimensions: completeness, duplication, consistency, and contradictions.

## Analysis Dimensions

| Dimension | Question | Impact |
|-----------|----------|--------|
| Completeness | Is anything missing? | Gaps in documentation |
| Duplication | Is content repeated? | Maintenance burden |
| Consistency | Is terminology uniform? | Confusion |
| Contradictions | Do files conflict? | Incorrect behavior |

---

## Dimension 1: Completeness Analysis

### What to Check

**Incomplete Sections**:
- TODO markers: `TODO`, `TBD`, `FIXME`, `XXX`
- Placeholder text: `Lorem ipsum`, `[description]`, `...`
- Empty sections: Headers with no content below
- Stub sections: Single-sentence explanations for complex topics

**Missing Examples**:
- Rules without code examples
- Concepts without usage demonstrations
- Edge cases mentioned but not shown

**Missing Context**:
- References to external concepts without explanation
- Assumed knowledge not documented
- Missing "when to use" guidance

### Output Format

```
Completeness Issues:
  File: {path}
  - Section "{section_name}": {issue_description}
  - Line {N}: TODO marker found: "{text}"
  - Missing: {what's missing}
  Score: {0-100}
```

### Scoring

| Score | Meaning |
|-------|---------|
| 90-100 | Complete - all sections filled, examples present |
| 70-89 | Minor gaps - 1-2 small missing items |
| 50-69 | Moderate gaps - missing sections or examples |
| 0-49 | Incomplete - significant content missing |

---

## Dimension 2: Duplication Analysis

### What to Check

**Exact Duplication**:
- Identical paragraphs across files
- Copy-pasted sections
- Same examples in multiple locations

**Semantic Duplication**:
- Same concept explained differently
- Overlapping guidance with different wording
- Multiple files covering same topic

**Near-Duplication**:
- 80%+ similar sections
- Slight variations of same content
- Outdated copies of updated content

### Detection Approach

1. Compare section headers across files
2. Compare paragraph content (fuzzy matching)
3. Identify shared concepts/terminology
4. Check for same examples used multiple places

### Output Format

```
Duplication Found:
  Source: {file1}:{lines}
  Target: {file2}:{lines}
  Similarity: {percentage}%
  Type: {exact|semantic|near}
  Recommendation: {consolidate|cross-reference|delete duplicate}
```

### Resolution Strategies

| Type | Action |
|------|--------|
| Exact | Delete duplicate, add cross-reference |
| Semantic | Consolidate into authoritative location |
| Near | Review for outdated content, merge |

---

## Dimension 3: Consistency Analysis

### What to Check

**Terminology Consistency**:
- Same concept with different names
- Abbreviations vs full terms
- Capitalization variations

**Common Inconsistencies**:
- "cross-reference" vs "xref" vs "internal link"
- "workflow" vs "process" vs "procedure"
- "must" vs "should" vs "may" (RFC 2119)

**Formatting Consistency**:
- Header level usage
- List style (bullet vs numbered)
- Code block formatting

**Style Consistency**:
- Imperative vs declarative tone
- "You should..." vs "Must..." vs "Use..."
- Active vs passive voice

### Output Format

```
Consistency Issues:
  Category: terminology
  Term variations:
    - "{term1}" used in: {file1}, {file2}
    - "{term2}" used in: {file3}, {file4}
  Recommendation: Standardize on "{preferred_term}"
```

### Terminology Standardization

For detected inconsistencies, recommend standard term:

| Variations Found | Recommended Standard |
|------------------|---------------------|
| cross-reference, xref, internal link | "cross-reference" (prose), "xref:" (syntax) |
| workflow, process, procedure | "workflow" (in skills), "procedure" (in docs) |
| must, should, may | Follow RFC 2119 strictly |

---

## Dimension 4: Contradiction Analysis

### What to Check

**Direct Contradictions**:
- Conflicting rules (e.g., different line limits)
- Opposite recommendations
- Mutually exclusive requirements

**Implicit Contradictions**:
- Examples that violate stated rules
- Exceptions that undermine main guidance
- "Always X" in one file, "Never X" in another

**Version Drift**:
- Old guidance not updated when rules changed
- Legacy examples with deprecated patterns

### Detection Approach

1. Extract all rules/requirements from files
2. Compare rule statements for conflicts
3. Check examples against stated rules
4. Verify cross-references are current

### Output Format

```
Contradiction Found:
  File 1: {path1}
    Line {N}: "{statement1}"
  File 2: {path2}
    Line {N}: "{statement2}"
  Nature: {direct|implicit|version_drift}
  Resolution: {recommendation}
```

### Resolution Strategies

| Type | Action |
|------|--------|
| Direct | Determine authoritative source, update other |
| Implicit | Fix examples to match rules |
| Version Drift | Update legacy content |

---

## Aggregate Quality Score

Combine dimension scores:

```
Quality Score = (Completeness + (100 - Duplication) + Consistency + (100 - Contradictions)) / 4
```

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | Excellent | Minor improvements only |
| 70-89 | Good | Address identified issues |
| 50-69 | Fair | Significant work needed |
| 0-49 | Poor | Major refactoring required |

---

## Quality Report Format

```markdown
# Content Quality Analysis

**Skill**: {skill_name}
**Files Analyzed**: {count}
**Overall Score**: {score}/100

## Completeness (Score: {X}/100)

{findings}

## Duplication (Score: {X}/100)

{findings}

## Consistency (Score: {X}/100)

{findings}

## Contradictions (Score: {X}/100)

{findings}

## Recommendations

### High Priority
1. {action}

### Medium Priority
1. {action}

### Low Priority
1. {action}
```

---

## Integration with doctor-skill-content Workflow

This guide is loaded in **Phase 3: Analyze Content Quality**.

```
Read references/content-quality-guide.md
Read ALL skill content files
Apply analysis dimensions
Generate quality report
```

The LLM applies these criteria to all discovered content files and produces findings for each dimension.
