---
name: cui-add-skill-knowledge
description: Add external knowledge document to a skill with duplication prevention
---

# Add Skill Knowledge

Integrates external knowledge documents into skills by creating isolated reference documents and preventing duplication across existing skill standards.

## PURPOSE

When you have valuable documentation (README files, external guides, technical specs) that should be available within a skill, this command:

1. Creates an isolated knowledge document in the skill's standards directory
2. References it from SKILL.md as on-demand loading
3. Scans all existing skill standards for duplicate content
4. Removes duplicates, keeping the new document as authoritative source

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** with:
1. Improved knowledge integration patterns or transformation techniques
2. Better methods for identifying semantic duplication
3. More effective strategies for cross-referencing and deduplication
4. Enhanced content organization and load-type selection guidelines
5. Improved integration report formats or validation checklist items
6. Any lessons learned about knowledge document creation and maintenance

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

**Required Parameters** (will prompt if missing):

- **target-skill**: Path to skill directory (e.g., `claude/marketplace/bundles/cui-java-expert/skills/cui-java-unit-testing`)
- **source-knowledge**: Path to source document (e.g., `/Users/oliver/git/cui-test-juli-logger/README.adoc`)

**Optional Parameters**:

- **knowledge-name**: Name for the knowledge document (default: derived from source filename)
- **load-type**: How to load knowledge (default: `on-demand`)
  - `on-demand`: Load only when explicitly requested
  - `conditional`: Load based on specific conditions
  - `always`: Load with other standards (use sparingly)

## WORKFLOW

### Step 1: Validate Input Parameters

**If target-skill not provided:**
```
Ask user: "Which skill should receive this knowledge? (provide path to skill directory)"
Example: claude/marketplace/bundles/cui-java-expert/skills/cui-java-unit-testing
```

**If source-knowledge not provided:**
```
Ask user: "What is the source of the knowledge? (provide path to document)"
Example: /Users/oliver/git/cui-test-juli-logger/README.adoc
```

**Validation:**
- Verify target-skill directory exists and contains SKILL.md
- Verify source-knowledge file exists and is readable
- Confirm target skill has `standards/` directory (create if missing)

### Step 2: Analyze Source Knowledge

**Read and analyze the source document:**

1. Read the complete source document
2. Identify key topics and content sections
3. Determine appropriate knowledge document name
4. Extract format (AsciiDoc, Markdown, etc.)

**Generate knowledge document name:**
- Use source filename as base (e.g., `README.adoc` → `juli-logger-reference.md`)
- Convert to kebab-case
- Ensure `.md` extension for consistency
- Prompt user to confirm or customize name

### Step 3: Create Isolated Knowledge Document

**Create new file:**
```
{target-skill}/standards/{knowledge-name}.md
```

**Document structure:**
```markdown
# {Title from Source}

> **Source**: {Original source path/URL}
> **Integration Date**: {Current date}
> **Load Type**: {on-demand/conditional/always}

{Content from source document, converted to Markdown if needed}
```

**Content transformation:**
- Convert AsciiDoc to Markdown if source is .adoc
- Preserve code examples exactly
- Maintain heading hierarchy
- Keep all technical details
- Add source attribution at top

### Step 4: Update SKILL.md

**Add reference to SKILL.md:**

For `on-demand` loading (default):
```markdown
### Step X: Load Additional Knowledge (Optional)

**When needed**: Load domain-specific knowledge on demand.

**{Knowledge Topic}** (load when needed):
```
Read: standards/{knowledge-name}.md
```

Use when: {Brief description of when to load this knowledge}
```

For `conditional` loading:
```markdown
### Step X: Load {Topic} Standards (Conditional)

**If** {condition}, load:
```
Read: standards/{knowledge-name}.md
```
```

For `always` loading:
```markdown
### Step X: Load Core Standards

```
Read: standards/{knowledge-name}.md
```
```

**Placement:**
- On-demand: Add after core standards loading section
- Conditional: Place where condition naturally occurs in workflow
- Always: Include in main standards loading section

### Step 5: Scan for Duplicate Content

**CRITICAL: Manual line-by-line review required**

**Scan all existing standards in the skill:**
```
Read all files in {target-skill}/standards/*.md
Read {target-skill}/SKILL.md
```

**For each existing file, manually compare:**

1. **Read source knowledge document completely**
2. **Read each existing standards file line by line**
3. **Identify duplicate content**:
   - Same concepts explained
   - Similar code examples
   - Redundant guidance
   - Overlapping sections

4. **Document findings**:
   ```
   File: {filename}
   Duplicate sections found:
   - Lines {X-Y}: {Description of duplicate content}
   - Lines {A-B}: {Description of duplicate content}
   ```

**DO NOT use automated tools like grep or diff:**
- This requires semantic understanding
- Must identify conceptual duplication, not just text matching
- Requires judgment about what constitutes harmful vs contextual duplication

### Step 6: Remove Duplicates

**For each duplicate identified:**

1. **Confirm duplication** with user:
   ```
   Found duplicate content in {filename} (lines {X-Y}):
   - Topic: {Description}
   - Action: Remove and reference new knowledge document

   Proceed with removal? (yes/no)
   ```

2. **Remove duplicate section** from existing file

3. **Add cross-reference** to new knowledge document:
   ```markdown
   For {topic}, see [{knowledge-name}]({knowledge-name}.md).
   ```

4. **Verify removal** doesn't break document flow:
   - Check section transitions
   - Update table of contents if present
   - Ensure remaining content is coherent

### Step 7: Generate Integration Report

**Create summary report:**

```markdown
## Knowledge Integration Report

**Skill**: {skill-name}
**Source**: {source-knowledge}
**Knowledge Document**: standards/{knowledge-name}.md
**Integration Type**: {load-type}

### Changes Made

1. **Created**: standards/{knowledge-name}.md ({line-count} lines)
2. **Updated**: SKILL.md (added {load-type} reference)

### Duplicates Removed

{For each file with duplicates removed}:
- **{filename}**:
  - Removed lines {X-Y}: {description}
  - Removed lines {A-B}: {description}
  - Added cross-reference to {knowledge-name}.md

### Files Scanned (No Duplicates Found)

{List files scanned that had no duplicates}

### Authoritative Source

The new document `standards/{knowledge-name}.md` is now the authoritative source for:
- {Topic 1}
- {Topic 2}
- {Topic 3}

All other standards files now reference this document for these topics.
```

## CRITICAL RULES

**Duplication Prevention:**
- New knowledge document is ALWAYS authoritative
- Remove ALL duplicates from existing files
- Manual review is REQUIRED (no automated deduplication)
- Must identify semantic duplication, not just text matching

**Integration Quality:**
- Source attribution must be preserved
- Content must be transformed to Markdown format
- Original technical details must be maintained exactly
- Integration type (on-demand/conditional/always) guides SKILL.md update

**Manual Review Process:**
- Read source knowledge completely first
- Read each existing file line by line
- Document all duplicates found before removing
- Confirm removals with user
- Verify coherence after removal

**Default Behavior:**
- Load type: `on-demand` (only when explicitly requested)
- Format: Markdown (.md)
- Placement: After core standards in SKILL.md
- Duplication: Remove from existing, keep in new

## USAGE EXAMPLES

### Example 1: Basic Usage

```bash
/cui-add-skill-knowledge
# Will prompt for target-skill and source-knowledge
```

### Example 2: With Parameters

```bash
/cui-add-skill-knowledge \
  target-skill=claude/marketplace/bundles/cui-java-expert/skills/cui-java-unit-testing \
  source-knowledge=/Users/oliver/git/cui-test-juli-logger/README.adoc
```

### Example 3: Custom Knowledge Name

```bash
/cui-add-skill-knowledge \
  target-skill=claude/marketplace/bundles/cui-java-expert/skills/cui-java-cdi \
  source-knowledge=/path/to/quarkus-guide.md \
  knowledge-name=quarkus-advanced-patterns
```

### Example 4: Always-Load Knowledge

```bash
/cui-add-skill-knowledge \
  target-skill=claude/marketplace/skills/cui-frontend-development \
  source-knowledge=/path/to/web-components-spec.md \
  load-type=always
```

## EXAMPLE INTEGRATION

**Before** (SKILL.md):
```markdown
### Step 1: Load Core Standards

```
Read: standards/testing-junit-core.md
Read: standards/testing-generators.md
```
```

**After** (SKILL.md with on-demand knowledge):
```markdown
### Step 1: Load Core Standards

```
Read: standards/testing-junit-core.md
Read: standards/testing-generators.md
```

### Step 2: Load Additional Knowledge (Optional)

**JUnit Logger Testing** (load when needed):
```
Read: standards/juli-logger-reference.md
```

Use when: Testing applications that use java.util.logging (JUL) or need to assert log output in tests.
```

## VALIDATION

After integration, verify:

- [ ] Knowledge document created in standards/
- [ ] Source attribution present in knowledge document
- [ ] SKILL.md updated with appropriate load type
- [ ] All existing standards files scanned manually
- [ ] All duplicates identified and documented
- [ ] Duplicates removed with user confirmation
- [ ] Cross-references added where duplicates removed
- [ ] Integration report generated
- [ ] No broken references in existing files
- [ ] Knowledge document is authoritative source

## RELATED

- `/cui-diagnose-skills` - Validates skill structure and quality
- `/cui-create-skill` - Creates new skills
- Skill quality standards - Standards for skill structure and content
