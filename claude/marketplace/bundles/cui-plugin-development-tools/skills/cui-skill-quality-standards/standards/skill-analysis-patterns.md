# Skill Analysis Patterns

Common issues to look for when analyzing skills.

## Pattern 1: YAML Frontmatter Issues

**Problem:** Invalid YAML or missing required fields
**Example:** No `---` delimiters, missing `name` or `description`
**Fix:** Add proper frontmatter structure with required fields

## Pattern 2: Wrong Tool Field Name

**Problem:** Using `tools` instead of `allowed-tools`
**Example:** `tools: [Read, Write]` (WRONG - skills use `allowed-tools`, not `tools`)
**Fix:** Change `tools` to `allowed-tools` in YAML frontmatter

**Correct format:**
```yaml
---
name: skill-name
description: Brief description of what this skill does and when to use it
allowed-tools: [Read, Edit, Write, Bash, Grep, Glob]
---
```

## Pattern 3: Broken Standards References

**Problem:** References to non-existent standards files
**Example:** `Read: standards/missing-file.md`
**Fix:** Create missing file or remove reference

## Pattern 4: Absolute Paths

**Problem:** Hardcoded absolute paths to standards
**Example:** `Read: ~/git/cui-llm-rules/standards/file.md`
**Fix:** Convert to relative path: `Read: standards/file.md`

## Pattern 5: Missing Primary File

**Problem:** SKILL.md doesn't exist or has wrong case
**Example:** `skill.md` or `Skill.md` instead of `SKILL.md`
**Fix:** Rename file to proper case

## Pattern 6: Excessive Tool Access

**Problem:** Knowledge skill has Write/Edit/Bash access
**Example:** `tools: [Read, Write, Edit, Bash]` for documentation skill
**Fix:** Restrict to `tools: [Read, Grep, Glob]`

## Pattern 7: Unused Skills

**Problem:** Skill not referenced by any agents
**Example:** Skill exists but no agent uses it
**Fix:** Either reference from agents or consider removing

## Pattern 8: Missing Workflow

**Problem:** No clear usage instructions in SKILL.md
**Example:** Only frontmatter and standards list, no workflow section
**Fix:** Add "## Workflow" section with step-by-step instructions

## Pattern 9: Circular Dependencies

**Problem:** Skills reference each other in a loop
**Example:** skill-a references skill-b, skill-b references skill-a
**Fix:** Restructure skill relationships to be acyclic

## Pattern 10: Inconsistent Naming

**Problem:** Skill directory name doesn't match frontmatter `name`
**Example:** Directory: `cui-java-core`, YAML name: `CUI Java Standards`
**Fix:** Align naming (directory = kebab-case, YAML name = Title Case)

## Pattern 11: Harmful Content Duplication

**Problem:** Same content repeated across multiple standards files
**Example:** Logger declaration pattern in logging-standards.md, java-core-patterns.md, and testing-junit-core.md
**Fix:** Keep content in one authoritative file, add cross-references from others

## Pattern 12: Content Conflicts

**Problem:** Contradictory requirements in different standards
**Example:** One file says "always use X", another says "never use X"
**Fix:** Resolve conflict by clarifying contexts or unifying guidance

## Pattern 13: Ambiguous Requirements

**Problem:** Vague language that doesn't provide clear guidance
**Example:** "Methods should be reasonably short", "Use when appropriate"
**Fix:** Replace with specific criteria: "Methods < 50 lines (recommended)", "Use for all test data (mandatory)"

## Pattern 14: Content Gaps

**Problem:** Important topics missing from standards coverage
**Example:** Skill covers Java but no guidance on dependency injection
**Fix:** Add missing section or create new standards file for gap

## Pattern 15: Poor Integrated Score

**Problem:** Overall content quality below acceptable threshold (< 75/100)
**Example:** Multiple duplications, conflicts, ambiguities, and gaps
**Fix:** Systematic content review and refinement across all standards

## Pattern 16: Documentation-Only Noise

**Problem:** Content sections that provide zero information and can be safely removed

**Example:** "Related Documentation" section containing only broken `xref:` links to `.adoc` files that don't exist in skill directory

**Characteristics:**
- Sections titled "Related Documentation", "See Also", "References", etc.
- Contains ONLY external/broken references (no actual content)
- Format incompatibility (AsciiDoc `xref:` syntax in Markdown `.md` files)
- Referenced files don't exist in skill directory
- Links point outside skill (violates self-containment)

**Fix:** Remove entire section (zero information loss, improves signal-to-noise ratio)

**Example Fix:**
```
BEFORE (lines 10-15 in maven-integration.md):
== Related Documentation
* xref:project-structure.adoc[Project Structure Standards]
* xref:javascript-development-standards.adoc[JavaScript Standards]
* xref:linting-standards.adoc[Linting Standards]

AFTER:
(removed - these files don't exist in skill, provide no information)
```

## Pattern Detection Logic

When analyzing skills, check for these patterns in this order:

1. **Structural Issues First** (Patterns 1-5): These prevent skill from functioning
2. **Configuration Issues** (Patterns 6, 10): Affect security and maintainability
3. **Integration Issues** (Patterns 7, 9): Affect skill ecosystem
4. **Content Quality Issues** (Patterns 11-16): Affect AI consumption quality
5. **Documentation Issues** (Pattern 8, 16): Affect usability and signal-to-noise ratio

## Pattern Priority

- **CRITICAL**: Patterns 1, 3, 4, 5, 11, 12 - Must fix before use
- **WARNING**: Patterns 2, 6, 7, 13, 14, 16 - Should fix for quality
- **SUGGESTION**: Patterns 8, 9, 10, 15 - Nice to have improvements
