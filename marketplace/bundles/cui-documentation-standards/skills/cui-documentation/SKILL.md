---
name: cui-documentation
description: General documentation standards for README, AsciiDoc, and technical documentation with validation, formatting, link verification, and content review workflows
allowed-tools: Read, Edit, Write, Bash, Grep, Glob, Skill
---

# CUI Documentation Skill

Standards and workflows for writing clear, maintainable technical documentation in CUI projects.

**Note**: This skill covers general documentation. For code documentation, use:
- `cui-javadoc` for Java code documentation
- `cui-frontend-development/jsdoc-standards.md` for JavaScript documentation

## Available Workflows

This skill provides four specialized workflows:

| Workflow | Purpose | Script Used |
|----------|---------|-------------|
| **format-document** | Auto-fix AsciiDoc formatting issues | `asciidoc-formatter.sh` |
| **validate-format** | Validate AsciiDoc format compliance | `asciidoc-validator.sh` |
| **verify-links** | Verify links and cross-references | `verify-adoc-links.py` |
| **review-content** | Review content quality and tone | `review-content.py` |

## Workflow: format-document

Auto-fix common AsciiDoc formatting issues with safety features.

### What It Fixes

- Add blank lines before lists
- Convert deprecated `<<>>` syntax to `xref:`
- Fix header attributes
- Remove trailing whitespace

### Parameters

- `target` (required): File path or directory path
- `dry_run` (optional, default: true): Preview changes without modifying
- `fix_types` (optional, default: "all"): Types of fixes: "lists", "xref", "headers", "whitespace", "all"

### Steps

**Step 1: Load Documentation Standards**

Read standards/asciidoc-formatting.md

**Step 2: Discover Files**

If target is a file:
- Verify file exists and has `.adoc` extension

If target is a directory:
- Use Glob: `{directory}/*.adoc` (non-recursive)
- Filter out `target/` directories

**Step 3: Run Auto-Formatter**

Build command with options:
```bash
OPTIONS=""
if [dry_run == true]; then OPTIONS="$OPTIONS -n"; fi
if [fix_types != "all"]; then OPTIONS="$OPTIONS -t {fix_type}"; fi
```

Execute:
```bash
bash scripts/asciidoc-formatter.sh $OPTIONS {target} 2>&1
```

**Step 4: Parse Output**

Extract statistics:
- Files processed
- Files modified
- Issues fixed
- Fix details per file

**Step 5: Report Results**

**Dry-run mode (preview):**
```
Format Preview for {target}
Files that would be modified: {count}
Changes that would be applied: {list}
To apply: run with dry_run=false
```

**Apply mode:**
```
Format Fixes Applied to {target}
Files modified: {count}
Issues fixed: {count}
Changes applied: {list}
```

**Step 6: Validation (if changes applied)**

If dry_run=false, run validation to confirm:
```bash
bash scripts/asciidoc-validator.sh {target} 2>&1
```

---

## Workflow: validate-format

Validate AsciiDoc files for format compliance.

### What It Checks

- Section headers with blank lines
- Proper list formatting
- Blank lines before/after lists
- Code block formatting

### Parameters

- `target` (required): File path or directory path
- `apply_fixes` (optional, default: false): Apply automatic fixes

### Steps

**Step 1: Load Documentation Standards**

Read standards/asciidoc-formatting.md

**Step 2: Discover Files**

If target is a file:
- Verify file exists and has `.adoc` extension

If target is a directory:
- Use Glob: `{directory}/*.adoc` (non-recursive)

**Step 3: Run Format Validation**

Execute:
```bash
bash scripts/asciidoc-validator.sh {target} 2>&1
```

**Step 4: Parse Output**

Extract warnings matching `Line [0-9]+`:
- Categorize issues by type
- Track by file and line number

**Step 5: Apply Fixes (if requested)**

If apply_fixes=true:
- For each issue, read file context (±5 lines)
- Use Edit tool to fix the issue
- Track fixes applied

**Step 6: Re-Validate (if fixes applied)**

Re-run validator and compare:
- Before: {total_issues}
- After: {remaining_issues}
- Fixed: {fixed_count}

**Step 7: Generate Report**

```
## AsciiDoc Format Validation Complete

**Status**: ✅ PASS | ⚠️ WARNINGS | ❌ FAILURES

**Summary**: Validated {file_count} file(s)

**Metrics**:
- Files validated: {count}
- Format issues found: {count}
- Issues fixed: {count}
- Issues remaining: {count}

**Issues by Category**:
- Blank line after header: {count}
- Blank line before list: {count}
- Other format violations: {count}

**Details by File**:
### {file_1}
- Line {N}: {issue description}
- Status: ✅ Clean | ⚠️ Issues remaining
```

---

## Workflow: verify-links

Verify all links and cross-references in AsciiDoc files.

### What It Verifies

- Cross-reference file links (xref:)
- Internal anchor references (<<anchor>>)
- Link formats and syntax

### Parameters

- `target` (required): File path or directory path
- `fix_links` (optional, default: false): Fix broken links

### Steps

**Step 1: Load Documentation Standards**

Read standards/asciidoc-formatting.md

**Step 2: Discover Files**

If target is a file:
- Verify file exists and has `.adoc` extension

If target is a directory:
- Use Glob: `{directory}/*.adoc` (non-recursive)

**Step 3: Setup Report Directory**

```bash
mkdir -p target/asciidoc-link-verifier
```

**Step 4: Run Link Verification**

Execute:
```bash
python3 scripts/verify-adoc-links.py --file {file_path} --report target/asciidoc-link-verifier/links.md 2>&1
```

For directories:
```bash
python3 scripts/verify-adoc-links.py --directory {directory} --report target/asciidoc-link-verifier/links.md 2>&1
```

**Step 5: Parse Report**

Read `target/asciidoc-link-verifier/links.md` and extract:
- Broken file links
- Broken anchors
- Format violations

**Step 6: Manual Verification (CRITICAL)**

For each "broken" link reported:
1. Extract target path
2. Resolve absolute path: `realpath {relative_target_path}`
3. Verify with Read tool
4. If file EXISTS but script reported broken: Report false positive
5. If file NOT FOUND: Confirm broken

**Step 7: Fix Internal Anchors (if approved)**

For missing anchors:
1. Search for matching section header
2. Add anchor ID: `[#anchor-id]` before header
3. Use Edit tool

**Step 8: Generate Report**

```
## AsciiDoc Link Verification Complete

**Status**: ✅ PASS | ⚠️ WARNINGS | ❌ FAILURES

**Summary**: Verified links in {file_count} file(s)

**Metrics**:
- Files verified: {count}
- Broken file links: {count}
- Broken anchors: {count}
- Issues fixed: {count}

**Details by File**:
### {file_1}
- Line {N}: xref to {target} - {status}
- Line {N}: anchor <<{id}>> - {status}
```

---

## Workflow: review-content

Review AsciiDoc content for quality: correctness, clarity, tone, style, and completeness.

### What It Reviews

- **Correctness**: Factual claims, RFC citations, verifiable statements
- **Clarity**: Concise, unambiguous, clear explanations
- **Tone & Style**: Professional, technical, no marketing language
- **Consistency**: Terminology, formatting patterns
- **Completeness**: No missing sections, TODOs, or gaps

### Parameters

- `target` (required): File path or directory path
- `apply_fixes` (optional, default: false): Apply content fixes

### Steps

**Step 1: Load Documentation Standards**

Read standards/tone-and-style.md
Read standards/documentation-core.md

**Step 2: Discover Files**

If target is a file:
- Verify file exists and has `.adoc` extension

If target is a directory:
- Use Glob: `{directory}/*.adoc` (non-recursive)

**Step 3: Run Content Analysis**

Execute:
```bash
python3 scripts/review-content.py --file {file_path} 2>&1
```

For directories:
```bash
python3 scripts/review-content.py --directory {directory} 2>&1
```

**Step 4: Parse JSON Output**

Script returns structured JSON:
```json
{
  "status": "success",
  "data": {
    "files_analyzed": N,
    "average_quality_score": N,
    "issues": [
      {
        "file": "path",
        "line": N,
        "type": "tone|correctness|completeness",
        "severity": "critical|high|medium|low",
        "message": "description"
      }
    ]
  }
}
```

**Step 5: Apply Deep Analysis**

For each issue from script, apply Claude judgment:
- Is the marketing language truly promotional or factual?
- Can claims be verified from context?
- Are TODOs appropriate (e.g., in development docs)?

**Step 6: Categorize by Priority**

**Priority 1 - CRITICAL:**
- Unverified factual claims
- Marketing/promotional language
- Transitional markers in specification docs

**Priority 2 - HIGH:**
- Clarity problems
- Tone issues
- Consistency violations

**Priority 3 - MEDIUM:**
- Minor wording improvements

**Step 7: Apply Fixes (if requested)**

If apply_fixes=true:
- For Priority 1 and 2 issues
- Read file context
- Use Edit tool for fixes
- Ask user before major changes

**Step 8: Generate Report**

```
## AsciiDoc Content Review Complete

**Status**: ✅ PASS | ⚠️ WARNINGS | ❌ FAILURES

**Summary**: Reviewed {file_count} file(s)

**Quality Score**: {average_score}/100

**Metrics**:
- Files reviewed: {count}
- Tone issues: {count}
- Correctness issues: {count}
- Completeness issues: {count}

**Issues by Priority**:
- CRITICAL: {count}
- HIGH: {count}
- MEDIUM: {count}

**Details by File**:
### {file_1}

**Tone Issues:**
- Line {N}: {description}
  - Current: "{text}"
  - Suggested: "{improved}"

**Correctness Issues:**
- Line {N}: {description}

**Completeness Issues:**
- Line {N}: {description}
```

---

## Standards References

All documentation standards are in the `standards/` directory:

| Reference | Purpose | When to Load |
|-----------|---------|--------------|
| `documentation-core.md` | Core documentation principles | Always |
| `asciidoc-formatting.md` | AsciiDoc format rules | Format/validation workflows |
| `tone-and-style.md` | Tone and style requirements | Content review workflow |
| `readme-structure.md` | README structure patterns | README files |
| `organization-standards.md` | Document organization | Structure reviews |

## Script Reference

All scripts are in the `scripts/` directory:

| Script | Purpose | Output |
|--------|---------|--------|
| `asciidoc-formatter.sh` | Auto-fix formatting | Console output |
| `asciidoc-validator.sh` | Validate format | Console output |
| `verify-adoc-links.py` | Verify links | Markdown report |
| `review-content.py` | Content quality | JSON |
| `documentation-stats.sh` | Statistics | Multiple formats |

## Usage from Commands

Commands invoke this skill and its workflows:

```markdown
# In command file
Skill: cui-documentation-standards:cui-documentation

# Then specify workflow
Execute workflow: format-document
Parameters:
  target: "standards/"
  dry_run: true
```

## Quality Verification Checklist

All documentation must pass:

- [ ] Professional, neutral tone (no marketing language)
- [ ] Proper AsciiDoc formatting
- [ ] Complete code examples
- [ ] Verified references
- [ ] Consistent terminology
- [ ] Documents only existing features
- [ ] All links valid
