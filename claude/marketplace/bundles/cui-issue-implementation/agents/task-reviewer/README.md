# Issue Reviewer Agent

Reviews issues for implementation readiness by ensuring correctness, completeness, and lack of ambiguities.

## Purpose

This agent automates the issue review process by:
- Deeply analyzing issue requirements using ULTRATHINK reasoning
- Researching unclear aspects or requesting clarification
- Updating issue documentation to achieve 100% clarity
- Ensuring issues are consistent, correct, unambiguous, and complete
- Verifying all quality criteria before marking issue as implementation-ready

## Usage

```bash
# Review a GitHub issue
"Review issue #3"

# Review an issue from a file
"Review issue described within issue-4-plan.md"

# Review an issue from a directory
"Review issue described within /http-client"
```

## How It Works

1. **Load Information**: Retrieves issue from GitHub or files
2. **Deep Analysis**: Uses ULTRATHINK reasoning to understand requirements
3. **Research/Clarify**: Resolves unclear aspects via research or user questions
4. **Confidence Check**: Verifies 100% understanding before proceeding
5. **Review Documentation**: Identifies gaps between understanding and documentation
6. **Update Issue**: Applies changes to achieve clarity
7. **Quality Loop**: Iterates until all quality criteria pass
8. **AsciiDoc Review**: Optionally reviews technical documentation

## Quality Criteria

The agent ensures all issues meet these criteria:

1. **Consistency**: All sections align, no contradictions
2. **Correctness**: Technical details are accurate
3. **Unambiguous**: Every statement has single clear interpretation
4. **No duplication**: Each point stated once
5. **Complete**: All necessary information present
6. **Actionable**: Clear what needs to be implemented

## Examples

### Example 1: GitHub Issue Review

```
User: "Review issue #42"

Agent:
- Fetches issue via gh CLI
- Analyzes requirements using ULTRATHINK
- Identifies 3 ambiguities in acceptance criteria
- Asks user for clarification on edge cases
- Updates issue description with clarified requirements
- Adds explicit acceptance criteria
- Removes duplicated information
- Verifies all 6 quality criteria pass
- Returns detailed review report
```

### Example 2: File-Based Issue

```
User: "Review issue described within feature-plan.md"

Agent:
- Reads feature-plan.md
- Finds unclear technical approach
- Invokes research-best-practices agent for best practices
- Identifies missing error handling requirements
- Updates feature-plan.md with:
  - Clarified technical approach
  - Added error handling section
  - Explicit scope boundaries
- Loops Step 6-7 twice to achieve all criteria
- Returns review with 2 iterations
```

### Example 3: AsciiDoc Issue

```
User: "Review issue in ./specs/http-retry"

Agent:
- Scans directory for issue files
- Finds spec.adoc and requirements.md
- Analyzes both files
- Identifies inconsistency between spec and requirements
- Updates both files to align
- Detects .adoc files involved
- Invokes /review-technical-docs
- Incorporates technical review findings
- Returns comprehensive review
```

## Critical Rules

- **Documentation Only**: Agent reviews and updates documentation, NEVER writes code
- **100% Confidence**: Must achieve complete understanding before making updates
- **Edit Issue Description**: For GitHub issues, edits description (not comments)
- **Zero Ambiguity**: Every statement must have single clear interpretation
- **Quality Loop**: Iterates Step 6-7 until all criteria pass

## Notes

- Uses ULTRATHINK reasoning for deep analysis
- Can invoke research-best-practices agent for technical clarification
- Uses AskUserQuestion for business/design decisions
- Supports both GitHub issues and file-based issues
- Conditionally invokes /review-technical-docs for AsciiDoc files
- Tracks tool usage and reports lessons learned

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
