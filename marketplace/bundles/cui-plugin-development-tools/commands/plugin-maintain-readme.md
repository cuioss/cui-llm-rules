---
name: plugin-maintain-readme
description: Analyze and update all README files to reflect current marketplace state
---

# Maintain README Command

Comprehensive README maintenance for marketplace bundles and project root. Ensures all documented agents, commands, and skills are accurate, complete, and properly described.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover a more precise, better, or more efficient approach, **YOU MUST immediately update this file** using `/plugin-update-command command-name=plugin-maintain-readme update="[your improvement]"` with:
1. Better patterns for detecting README inconsistencies with actual components
2. Improved strategies for identifying missing or outdated documentation
3. More effective README update templates and formatting standards
4. Enhanced validation of component descriptions and completeness
5. Any lessons learned about documentation maintenance workflows

This ensures the command evolves and becomes more effective with each execution.

## PARAMETERS

None - Processes all bundles and project root automatically.

## TOOL USAGE REQUIREMENTS

```
Skill: cui-utilities:cui-diagnostic-patterns
```

✅ Use `Glob`, `Read`, `Edit`, `SlashCommand` (never Bash alternatives)

## WORKFLOW OVERVIEW

**This command has THREE phases:**

**PHASE 1: Discovery (Step 1)**
- Load complete marketplace inventory
- Identify all bundles, agents, commands, skills

**PHASE 2: Bundle README Maintenance (Steps 2-4)**
- For each bundle: Analyze bundle README.md
- Validate documented components match actual components
- Update completeness and correctness
- Fix descriptions and formatting

**PHASE 3: Project Root README (Steps 5-6)**
- Analyze project root README.adoc
- Update bundle listings and documentation
- Ensure project overview is accurate

## WORKFLOW INSTRUCTIONS

### Step 1: Initialize and Load Inventory

**Validate environment:**
- Verify marketplace directory exists using Glob
- If marketplace/bundles/ not found: Display error "Not in marketplace root directory" and abort

**Initialize statistics tracking:**
- `bundles_discovered`: Total bundles found
- `bundles_analyzed`: Bundles successfully analyzed
- `readmes_updated`: Count of README files modified
- `components_added`: Components added to documentation
- `components_removed`: Obsolete components removed
- `descriptions_updated`: Component descriptions corrected
- `failed_updates`: Updates that failed (with error details)

**Display:**
```
╔════════════════════════════════════════════════════════════╗
║          README Maintenance Starting                       ║
╚════════════════════════════════════════════════════════════╝

Loading marketplace inventory...
```

**Run plugin-inventory to discover all bundles:**
```
SlashCommand: /plugin-inventory --json --include-descriptions
```

Parse JSON output:
- Extract `bundles[]` array
- For each bundle: Extract name, path, agents[], commands[], skills[] with descriptions
- Track `bundles_discovered` count

**Error handling:**
- If SlashCommand fails: Display "Failed to load inventory: {error}" and abort
- If JSON parse fails: Display "Invalid inventory format" and abort

### Step 2: For Each Bundle, Analyze README.md

**For each bundle in inventory:**

#### 2.1: Read Bundle README.md

```
Read: {bundle.path}/README.md
```

**Error handling:**
- If Read fails (file not found): Log "No README found for {bundle.name}"
- If Read fails (permission/other error): Log detailed error, skip this bundle
- Track bundles without README for reporting
- Continue with next bundle (don't abort entire process)

#### 2.2: Extract Documented Components

Parse README.md to identify documented components in sections for Agents, Commands, and Skills.

Extract:
- `documented_agents`: Agent names found in README
- `documented_commands`: Command names found in README
- `documented_skills`: Skill names found in README
- `documented_descriptions`: Component descriptions from README

**Track:** Components documented in README per bundle

#### 2.3: Compare with Actual Components

**From inventory (Step 1):**
- `actual_agents`: Agents discovered for this bundle
- `actual_commands`: Commands discovered for this bundle
- `actual_skills`: Skills discovered for this bundle

**Identify discrepancies:**
- `missing_components`: In actual but not documented
- `obsolete_components`: In documented but not actual
- `description_mismatches`: Components where README description differs from YAML frontmatter

**Track issues per bundle:**
```
Bundle: {bundle-name}
  Missing from README:
    Agents: {missing_agent_names}
    Commands: {missing_command_names}
    Skills: {missing_skill_names}
  Obsolete in README:
    Agents: {obsolete_agent_names}
    Commands: {obsolete_command_names}
    Skills: {obsolete_skill_names}
  Description mismatches: {count}
```

### Step 3: Update Bundle README.md

**For bundles with discrepancies found in Step 2:**

#### 3.1: Prepare README Updates

**Build updated component sections:**

For each component type (agents, commands, skills):
1. Use actual components from inventory
2. Sort alphabetically by name
3. Use descriptions from YAML frontmatter (from --include-descriptions)
4. Match existing README formatting style (list or table)

#### 3.2: Apply Updates Using Edit Tool

**Strategy:**
- Preserve README structure and non-component content
- Update only component listing sections
- Maintain existing formatting style (list vs table)

**For each component section:**
```
Edit:
  file_path: {bundle.path}/README.md
  old_string: {existing_section_content}
  new_string: {updated_section_content}
```

**Track updates:**
- Increment `components_added` for each new component
- Increment `components_removed` for each obsolete component
- Increment `descriptions_updated` for each corrected description
- Increment `readmes_updated` when bundle README modified

**Display progress:**
```
[UPDATE] {bundle-name}/README.md
  ✓ Added {count} missing components
  ✓ Removed {count} obsolete components
  ✓ Updated {count} descriptions
```

**Error handling:**
- If Edit fails (no match): Verify old_string exists in file, adjust and retry once
- If Edit fails (tool error): Log detailed error with bundle name and file path
- Track failed edit in `failed_updates` with: bundle name, error message, file path
- Continue with next bundle (don't abort entire process)
- Report all failed updates with details at end

### Step 4: Bundle Phase Summary

Display bundle maintenance results:

```
╔════════════════════════════════════════════════════════════╗
║          Bundle README Maintenance Complete                ║
╚════════════════════════════════════════════════════════════╝

Statistics:
- Bundles discovered: {bundles_discovered}
- Bundles analyzed: {bundles_analyzed}
- Bundle READMEs updated: {bundle_readmes_updated}
- Components added: {components_added}
- Components removed: {components_removed}
- Descriptions updated: {descriptions_updated}

{if bundle_readmes_updated > 0:
  "Updated Bundles:"
  {list updated bundle names}
}

{if failed_updates > 0:
  "⚠️ Failed Updates:"
  {list failed bundle names with errors}
}
```

**Continue to PHASE 3 (Project Root README)**

### Step 5: Analyze Project Root README.adoc

#### 5.1: Read Project README

```
Read: /Users/oliver/git/cui-llm-rules/README.adoc
```

**Error handling:**
- If Read fails (file not found): Display error "Project README.adoc not found at expected path", abort Phase 3
- If Read fails (permission/other error): Display detailed error message, abort Phase 3
- Phase 3 failure doesn't affect Phase 2 results (bundle READMEs already updated)

#### 5.2: Extract Documented Bundles

Parse README.adoc to identify documented bundles:

**Common patterns in project README:**
- Bundle listings with descriptions
- Links to bundle READMEs: `xref:marketplace/bundles/{bundle-name}/README.md[Bundle Name]`
- Bundle description sections

Extract:
- `documented_bundles`: Bundle names found in README
- `documented_bundle_descriptions`: Bundle descriptions from README

**Track:** Bundles documented in project README

#### 5.3: Compare with Actual Bundles

**From inventory (Step 1):**
- `actual_bundles`: All bundles discovered

**Identify discrepancies:**
- `missing_bundles`: Bundles not documented in project README
- `obsolete_bundles`: Documented but don't exist
- `description_updates`: Bundles where description should be refreshed

**Display findings:**
```
Project README.adoc:
  Missing bundles: {missing_bundle_names}
  Obsolete bundles: {obsolete_bundle_names}
  Total bundles: {actual_count} actual, {documented_count} documented
```

### Step 6: Update Project Root README.adoc

**If discrepancies found in Step 5:**

#### 6.1: Prepare README.adoc Updates

**Build updated bundle listings:**
1. Use all bundles from inventory
2. Sort alphabetically
3. Extract bundle purpose from bundle README.md
4. Format as AsciiDoc matching existing style

#### 6.2: Apply Updates Using Edit Tool

```
Edit:
  file_path: /Users/oliver/git/cui-llm-rules/README.adoc
  old_string: {existing_bundle_section}
  new_string: {updated_bundle_section}
```

**Track updates:**
- Increment `readmes_updated` if project README modified
- Track added/removed bundles

**Display:**
```
[UPDATE] Project README.adoc
  ✓ Added {count} missing bundles
  ✓ Removed {count} obsolete bundles
  ✓ Updated bundle listings
```

**Error handling:**
- If Edit fails (no match): Verify old_string exists in file, adjust and retry once
- If Edit fails (tool error): Log detailed error with file path and error message
- Track failed edit in `failed_updates` with: "project README", error message, file path
- Report failure clearly with full error details
- Continue to final summary (don't abort)

### Step 7: Display Final Summary

```
╔════════════════════════════════════════════════════════════╗
║          README Maintenance Summary                        ║
╚════════════════════════════════════════════════════════════╝

Results:
- Bundles processed: {bundles_analyzed}
- READMEs updated: {readmes_updated}
  - Bundle READMEs: {bundle_readme_count}
  - Project README: {project_readme_updated ? "✓" : "—"}

Component Updates:
- Components added: {components_added}
- Components removed: {components_removed}
- Descriptions corrected: {descriptions_updated}

Documentation Status: {✓ UP-TO-DATE | ⚠ PARTIAL | ✗ ERRORS}

{if readmes_updated > 0:
  "Files Modified:"
  {list all modified README paths}
}

{if failed_updates > 0:
  "⚠️ Failed Updates:"
  {list failures with error messages}

  "Next Steps:"
  1. Review error messages above
  2. Manually fix failed updates
  3. Re-run /plugin-maintain-readme to verify
}

{if readmes_updated == 0 && failed_updates == 0:
  "✅ All READMEs are already up-to-date!"
}
```

## CRITICAL RULES

**Discovery:**
- Use /plugin-inventory as source of truth for actual components
- Use --include-descriptions to get component descriptions from YAML frontmatter
- Never fabricate component names or descriptions

**Analysis:**
- Parse existing README structure to preserve formatting style
- Detect list vs table formatting and maintain consistency
- Identify all three component types: agents, commands, skills
- Compare documented vs actual for completeness

**Updates:**
- Preserve README structure and non-component sections
- Update only component listings, not general content
- Use YAML frontmatter descriptions as source of truth
- Maintain existing formatting conventions (markdown/asciidoc)
- Keep alphabetical ordering for readability

**Safety:**
- Git provides version control - no backup files needed
- Continue processing even if individual bundles fail
- Report all failures clearly at end
- Never skip project README phase

**Error Handling:**
- If inventory fails: Abort (can't proceed without discovery)
- If individual bundle README fails: Log warning, continue with next bundle
- If Edit fails: Log error, mark as failed, continue
- If project README read fails: Abort project phase (critical file)

**User Experience:**
- Clear progress indicators per bundle
- Statistics tracking throughout workflow
- Grouped results by phase (bundles vs project)
- Comprehensive before/after reporting

## STATISTICS TRACKING

Track throughout workflow:
- `bundles_discovered`: Count from plugin-inventory
- `bundles_analyzed`: Bundles successfully examined
- `readmes_updated`: Total README files modified
- `components_added`: Missing components added to READMEs
- `components_removed`: Obsolete components removed
- `descriptions_updated`: Incorrect descriptions corrected
- `failed_updates`: Edit operations that failed

Display all statistics in final summary.

## USAGE EXAMPLES

**Maintain all READMEs:**
```
/plugin-maintain-readme
```

Processes all bundle READMEs and project root README.adoc automatically.

## RELATED COMMANDS

- `/plugin-inventory` - Discovers all marketplace resources (used internally)
- `/plugin-diagnose-metadata` - Validates metadata consistency
- `/plugin-create-bundle` - Creates bundles with initial README
- `/doc-review-technical-docs` - Reviews documentation quality

## PURPOSE

**This command ensures README documentation accuracy:**
- Validates all bundle README.md files reflect actual components
- Updates component listings to match discovered agents/commands/skills
- Corrects component descriptions using YAML frontmatter as source
- Maintains project root README.adoc bundle listings
- Ensures documentation completeness and correctness across marketplace
