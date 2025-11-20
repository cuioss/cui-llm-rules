# Categorization Patterns - Safe vs Risky Fixes

Defines the logic for categorizing issues into safe (auto-fixable) and risky (requires user judgment) categories.

## Core Principle

**Safe fixes** can be applied automatically without risk of breaking functionality or losing important information.

**Risky fixes** require human judgment because they involve:
- Decisions about what content to keep vs remove
- Understanding domain-specific context
- Potential for unintended consequences
- Changes to architectural structure

## Safe Fix Categories

These fixes can be auto-applied when `auto-fix=true`:

### 1. YAML Frontmatter Syntax Errors

**What qualifies:**
- Invalid YAML syntax (unclosed quotes, improper indentation)
- Missing required fields (can add with sensible defaults)
- Field name typos (e.g., `tools` → `allowed-tools`)
- Invalid field values that have clear correct alternatives

**Why safe:**
- YAML structure is well-defined with clear rules
- Required fields have standard default values
- Syntax errors have unambiguous fixes
- No content interpretation needed

**Fix approach:**
```
Edit: {component-file}
- Fix YAML syntax errors
- Add missing required fields with defaults:
  - description: "[Description needed]"
  - allowed-tools: []
- Correct field name typos
```

### 2. Formatting and Whitespace Normalization

**What qualifies:**
- Inconsistent indentation
- Missing blank lines before lists (AsciiDoc requirement)
- Trailing whitespace
- Incorrect heading hierarchy (h1 → h2 → h3)
- Line length normalization (within reason)

**Why safe:**
- Formatting changes don't affect meaning
- Whitespace normalization is mechanical
- Heading hierarchy has clear rules
- No content interpretation needed

**Fix approach:**
```
Edit: {component-file}
- Normalize whitespace and indentation
- Ensure blank lines before lists
- Fix heading hierarchy
- Remove trailing whitespace
```

### 3. Broken File References

**What qualifies:**
- References to files that don't exist
- Links to non-existent sections
- Import statements for missing modules

**Why safe:**
- File existence is binary (exists or doesn't)
- Broken references cause errors, removal is safe
- Can comment out rather than delete for traceability

**Fix approach:**
```
Edit: {component-file}
- Remove or comment out references to non-existent files
- Add comment: "<!-- Reference removed: file not found -->"
- Update import statements to remove missing dependencies
```

### 4. Obsolete Content (Commands Only)

**What qualifies:**
- Deprecated tool usage patterns
- Outdated parameter names
- Legacy workflow steps that have been superseded

**Why safe (for commands):**
- Command documentation should reflect current tool capabilities
- Deprecated patterns are documented elsewhere
- Clear markers indicate obsolescence

**Fix approach:**
```
Edit: {command-file}
- Remove sections marked with DEPRECATED or OBSOLETE
- Add comment explaining removal if needed
```

## Risky Fix Categories

These fixes ALWAYS require user confirmation:

### 1. Duplication Consolidation

**What qualifies:**
- Content appearing in multiple locations
- Decision needed: which version to keep, which to merge
- Potential for different contexts requiring different wording

**Why risky:**
- Requires judgment about which version is authoritative
- May lose context-specific explanations
- Different audiences may need different explanations
- Cross-references may break

**User decision needed:**
- Which version to keep as canonical source?
- Should other locations cross-reference or be fully removed?
- Is the duplication actually harmful or contextually appropriate?

### 2. Integration Issues

**What qualifies:**
- Orphaned files (exist but not referenced)
- Workflow disconnection (steps reference missing components)
- Missing cross-references between related files

**Why risky:**
- Files may be intentionally unreferenced (work in progress, examples)
- Removing orphaned files may lose valuable content
- Adding cross-references requires understanding relationships
- May indicate architectural issues needing broader fixes

**User decision needed:**
- Should orphaned files be deleted or integrated?
- Should missing steps be added or references removed?
- Is the disconnection intentional or an error?

### 3. Reference Problems

**What qualifies:**
- Ambiguous cross-references
- Circular reference patterns
- References to external resources that may change
- Unclear link text

**Why risky:**
- Requires understanding of what should be referenced
- May need to create new sections/files
- External references need validation
- Breaking circular references may require restructuring

**User decision needed:**
- How to resolve circular references?
- Should new sections be created or references removed?
- Are external references still valid and appropriate?

### 4. Zero-Information Content

**What qualifies:**
- Generic statements without actionable guidance
- Vague requirements without examples
- Placeholder sections with minimal content

**Why risky:**
- Content may have context we don't understand
- "Obvious" information may be valuable to some users
- Removing content requires domain expertise
- May be work-in-progress rather than final state

**User decision needed:**
- Is this truly zero-information or contextually valuable?
- Should section be removed or enhanced?
- Is this a placeholder for future content?

### 5. Conflicting Guidance

**What qualifies:**
- Different files provide contradictory recommendations
- Multiple approaches described without clear guidance
- Standards that contradict best practices

**Why risky:**
- Requires domain expertise to determine correct approach
- May need to update multiple files
- Context may matter (both approaches valid in different scenarios)
- May indicate architectural documentation issues

**User decision needed:**
- Which guidance is correct?
- Should contradictions be resolved or contextualized?
- Do different contexts justify different approaches?

### 6. Architectural Changes (Agents/Commands)

**What qualifies:**
- Bloat requiring extraction to skill
- Tool access pattern violations
- Self-invocation patterns (Pattern 22 violations)
- Missing architectural compliance

**Why risky:**
- Requires creating new components (skills)
- May affect multiple commands/agents
- Breaking changes to interfaces
- Requires testing across multiple use cases

**User decision needed:**
- Should bloated content be extracted or compressed?
- How to restructure to fix architectural violations?
- What new components need to be created?

## NEVER "Simplify" - Functional UI Elements

**CRITICAL**: These patterns are NOT over-specification and must NEVER be "simplified":

### Bracketed Keyboard Shortcuts

**What they are:**
- User prompts with brackets indicating hotkeys: `"[R]etry/[A]bort"`
- Options with bracketed letters: `"[F]ix/[S]uppress/[S]kip"`
- Interactive choice indicators: `"[Y]es/[N]o/[C]ancel"`

**Why they must be preserved:**
- Brackets indicate which key to press for each option
- Removing brackets removes functional UI guidance
- This is **user interface design**, not redundancy
- Users need to know that pressing "R" selects "Retry"

**Examples:**

| ❌ WRONG "Simplification" | ✅ CORRECT (Preserve) |
|--------------------------|----------------------|
| Prompt: "Retry/Abort" | Prompt: "[R]etry/[A]bort" |
| Options: "Fix/Suppress/Skip" | Options: "[F]ix/[S]uppress/[S]kip" |
| "Continue or Stop" | "[C]ontinue/[S]top" |

**Detection pattern:**
- If line contains prompt/option pattern `"[A-Z][a-z]+/[A-Z][a-z]+"` with brackets
- This is **functional UI**, NOT bloat

### Other Functional Patterns to Preserve

- ASCII box borders used for visual separation in terminal output
- Emoji indicators for status (✅, ❌, ⚠️) used for quick visual scanning
- Indentation patterns that indicate hierarchy or grouping
- Code formatting examples showing exact syntax

## Categorization Algorithm

For each issue found:

1. **Check if issue is functional UI element (see NEVER Simplify above)**
   - If yes: Categorize as NOT AN ISSUE
   - If no: Continue to step 2

2. **Check if issue type is in safe category list**
   - If yes: Categorize as SAFE
   - If no: Continue to step 3

3. **Check if issue involves any of:**
   - Content judgment (what to keep/remove)
   - Domain expertise
   - Structural changes
   - Multiple components
   - User decision

   If yes: Categorize as RISKY

4. **Default**: When in doubt, categorize as RISKY
   - Better to prompt unnecessarily than break something

## Tracking Structure

Track categorization results using the JSON structures defined in **tracking-patterns.md**. See that file for the complete categorization tracking schema.

## Component-Specific Variations

Different component types may have additional safe/risky categories:

**Skills:**
- Safe: Standards file formatting
- Risky: Cross-skill duplication

**Agents:**
- Safe: Tool declaration fixes
- Risky: Architectural pattern violations (Pattern 22)

**Commands:**
- Safe: Obsolete content removal
- Risky: Bloat extraction to skills

Each diagnosis command defines its specific categories while following the core safe vs risky principles above.
