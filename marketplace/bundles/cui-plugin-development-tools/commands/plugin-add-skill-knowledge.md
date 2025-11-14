---
name: plugin-add-skill-knowledge
description: Add external knowledge document to a skill with duplication prevention
---

# Add Skill Knowledge

Integrates external knowledge documents into skills by creating isolated reference documents and preventing duplication across existing skill standards.

## PURPOSE

When you have valuable documentation (README files, external guides, technical specs) that should be available within a skill, this command:

1. Creates an isolated knowledge document in the skill's standards directory
2. References it from SKILL.md as on-demand loading
3. Scans all existing skill standards marketplace-wide for duplicate content
4. Removes duplicates, keeping the new document as authoritative source

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=plugin-add-skill-knowledge update="[your improvement]"` with:
1. Improved knowledge integration patterns or transformation techniques
2. Better methods for identifying semantic duplication
3. More effective strategies for cross-referencing and deduplication
4. Enhanced content organization and load-type selection guidelines
5. Improved integration report formats or validation checklist items
6. Any lessons learned about knowledge document creation and maintenance

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

**Required Parameters** (will prompt if missing):

- **target-skill**: Path to skill directory (e.g., `marketplace/bundles/cui-java-expert/skills/cui-java-unit-testing`)
- **source-knowledge**: Path to source document (e.g., `/Users/oliver/git/cui-test-juli-logger/README.adoc`)

**Optional Parameters**:

- **knowledge-name**: Name for the knowledge document (default: derived from source filename)
- **load-type**: How to load knowledge - `on-demand` (default), `conditional`, or `always`

## WORKFLOW

### Step 1: Validate Input Parameters

**Prompt for missing parameters:**
- `target-skill`: "Which skill should receive this knowledge? (provide path to skill directory)"
- `source-knowledge`: "What is the source of the knowledge? (provide path to document)"

**Validation:**
- Verify target-skill directory exists and contains SKILL.md (abort if not found)
- Verify source-knowledge file exists and is readable (abort if not found)
- Confirm target skill has `standards/` directory (create if missing)
- Verify knowledge-name (if provided) is valid kebab-case with .md extension

### Step 2: Analyze Source Knowledge

1. Read the complete source document
2. Identify key topics and content sections
3. Generate knowledge document name from filename (convert to kebab-case with `.md` extension)
4. Prompt user to confirm or customize name

### Step 3: Create Isolated Knowledge Document

Create `{target-skill}/standards/{knowledge-name}.md` with:
- Source attribution header (source path, integration date, load type)
- Content from source document (convert AsciiDoc to Markdown if needed)
- Preserve all code examples and technical details exactly

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

**Placement:** Add reference based on load-type (on-demand: after core standards, conditional: where condition occurs, always: in main loading section)

### Step 5: Scan for Duplicate Content (Marketplace-Wide)

**CRITICAL: Scan ALL marketplace bundles for semantic duplication**

1. **Discover all marketplace standards files:**
   - Use Glob to find all `bundles/*/skills/*/standards/*.md` and `bundles/*/skills/*/SKILL.md`
   - Also scan bundle-level `bundles/*/standards/*.md` if they exist

2. **For each file, perform semantic comparison:**
   - Read source knowledge document completely
   - Read each existing standards file
   - Identify duplicate content: same concepts, similar examples, redundant guidance, overlapping sections
   - Document findings: `{skill-name}/{filename}: Lines {X-Y} - {description}`

3. **Track statistics:** files_scanned, duplicates_found, bundles_scanned, skills_scanned

**Error handling:** If marketplace path cannot be determined or files cannot be read, log error and continue with remaining files.

### Step 6: Remove Duplicates

**For each duplicate identified:**

1. **Prompt user for confirmation:** "Found duplicate content in {skill-name}/{filename} (lines {X-Y}: {topic}). Remove and add cross-reference? [Y/n/q]"
2. **If yes:** Remove duplicate section and add cross-reference to new knowledge document
3. **Verify:** Check section transitions and ensure document remains coherent
4. **Track:** Increment duplicates_removed counter

**Error handling:** If Edit tool fails, log error and continue with remaining duplicates.

### Step 7: Display Integration Report

Display summary with statistics:
- **Created:** `{knowledge-name}.md` ({line_count} lines)
- **Updated:** SKILL.md (added {load-type} reference)
- **Scanned:** {bundles_scanned} bundles, {skills_scanned} skills, {files_scanned} files
- **Duplicates found:** {duplicates_found}
- **Duplicates removed:** {duplicates_removed}
- **Skills modified:** {list of skills where duplicates were removed}
- **Authoritative source:** `{target-skill}/standards/{knowledge-name}.md`

### Step 8: Verify Skill Quality

Run `/plugin-diagnose-skills {skill-name}` to verify skill structure, references, and standards organization.

**Error handling:** If diagnosis fails, log error and display diagnostic output for review.

### Step 9: Verify Bundle Quality (If modifications span multiple skills)

**Decision logic:** If duplicates were removed from skills outside the target skill, run `/plugin-diagnose-bundle {bundle-name}` for each affected bundle.

**Error handling:** If diagnosis fails, log error and display diagnostic output for review.

## CRITICAL RULES

**Duplication Prevention:**
- New knowledge document is ALWAYS authoritative
- Scan ALL marketplace bundles (not just target bundle)
- Identify semantic duplication (conceptual overlap, not just text matching)
- Confirm all removals with user before modifying files

**Integration Quality:**
- Preserve source attribution in knowledge document
- Convert content to Markdown format
- Maintain all technical details exactly
- Use on-demand loading by default (load only when explicitly requested)

## USAGE EXAMPLES

### Example 1: Basic Usage

```bash
/plugin-add-skill-knowledge
# Will prompt for target-skill and source-knowledge
```

### Example 2: With Parameters

```bash
/plugin-add-skill-knowledge \
  target-skill=marketplace/bundles/cui-java-expert/skills/cui-java-unit-testing \
  source-knowledge=/Users/oliver/git/cui-test-juli-logger/README.adoc
```

### Example 3: Custom Knowledge Name

```bash
/plugin-add-skill-knowledge \
  target-skill=marketplace/bundles/cui-java-expert/skills/cui-java-cdi \
  source-knowledge=/path/to/quarkus-guide.md \
  knowledge-name=quarkus-advanced-patterns
```

### Example 4: Always-Load Knowledge

```bash
/plugin-add-skill-knowledge \
  target-skill=marketplace/skills/cui-frontend-development \
  source-knowledge=/path/to/web-components-spec.md \
  load-type=always
```

## TOOL USAGE

- **Glob**: Discover marketplace standards files (non-prompting)
- **Read**: Read source knowledge and existing standards files
- **Write**: Create new knowledge document
- **Edit**: Update SKILL.md and remove duplicates
- **SlashCommand**: Run `/plugin-diagnose-skills` and `/plugin-diagnose-bundle`

## STATISTICS TRACKING

Track throughout workflow:
- `files_scanned`: Total standards files reviewed
- `bundles_scanned`: Total bundles examined
- `skills_scanned`: Total skills examined
- `duplicates_found`: Duplicate sections identified
- `duplicates_removed`: Duplicate sections removed with user confirmation
- `skills_modified`: Skills where duplicates were removed

## RELATED

- `/plugin-diagnose-skills` - Validates skill structure and quality
- `/plugin-create-skill` - Creates new skills
