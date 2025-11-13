---
name: plugin-create-bundle
description: Create a new marketplace bundle with proper structure, plugin.json, and documentation
---

# Create Bundle Command

Creates a new marketplace bundle with proper directory structure, plugin.json configuration, and documentation following marketplace architecture standards.

## PARAMETERS

**scope** - Where to create bundle (marketplace/global/project, default: marketplace)

## WORKFLOW

### Step 1: Validate Parameters and Environment

Parse scope parameter and determine target directory.

### Step 2: Interactive Questionnaire

**A. Bundle name** - kebab-case (e.g., `java-development-standards`)

**B. Display name** - Human-readable (e.g., "Java Development Standards")

**C. Description** - One sentence describing bundle purpose

**D. Version** - Semantic version (default: 1.0.0)

**E. Author** - Bundle author name

**F. Bundle type** - Select from:
1. Standards bundle (provides development standards)
2. Tool bundle (provides commands/agents)
3. Mixed bundle (standards + tools)

**G. Initial components** - Ask which to create:
- Skills? (y/n) - If yes, how many initially?
- Commands? (y/n) - If yes, how many initially?
- Agents? (y/n) - If yes, how many initially?

### Step 3: Create Bundle Structure

**A. Create directory structure**:
```
{scope}/bundles/{bundle-name}/
{scope}/bundles/{bundle-name}/skills/
{scope}/bundles/{bundle-name}/commands/
{scope}/bundles/{bundle-name}/agents/
```

**B. Generate plugin.json** with:
- name, display_name, description, version, author
- components array (empty initially)
- marketplace metadata

**C. Generate README.md** with:
- Bundle overview and purpose
- What this bundle provides
- Components list (initially empty)
- Installation instructions
- Usage examples
- Integration notes
- Contributing guidelines

Trust AI to generate appropriate README structure - no need for 290-line template.

**D. Create component READMEs** if requested:
- skills/README.md - Skills overview
- commands/README.md - Commands overview
- agents/README.md - Agents overview

Trust AI to generate appropriate component README structure.

### Step 4: Create Initial Components (if requested)

For each component type user requested:

**Skills**: Redirect to `/plugin-create-skill scope={scope} bundle={bundle-name}`

**Commands**: Redirect to `/plugin-create-command scope={scope} bundle={bundle-name}`

**Agents**: Redirect to `/plugin-create-agent scope={scope} bundle={bundle-name}`

### Step 5: Update plugin.json with Created Components

After components created, update plugin.json components array with created items.

### Step 6: Display Summary

Show:
- Bundle created at: {path}
- Components created: {count} skills, {count} commands, {count} agents
- Next steps:
  - Populate component files
  - Add more components: Use /cui-create-{skill|command|agent}
  - Test bundle
  - Run bundle diagnosis

### Step 7: Run Bundle Diagnosis

Execute:
```
SlashCommand: /plugin-diagnose-bundle bundle-name={bundle-name}
```

Review results and offer to fix any issues found.

## CRITICAL RULES

**Structure:**
- Follow marketplace bundle architecture
- Use kebab-case for bundle names
- Include all three component directories (even if empty initially)
- plugin.json must be valid JSON with required fields

**Documentation:**
- Bundle README explains overall purpose
- Component READMEs explain component category
- Trust AI to generate appropriate content - avoid templates

**Component Creation:**
- Delegate to specialized creation commands
- Update plugin.json after components created
- Maintain consistency across bundle

**Quality:**
- Always run diagnosis after creation
- Address any issues found
- Verify plugin.json validity

## USAGE EXAMPLES

**Create marketplace bundle:**
```
/plugin-create-bundle
```

**Create global bundle:**
```
/plugin-create-bundle scope=global
```

**Create project bundle:**
```
/plugin-create-bundle scope=project
```

## ARCHITECTURE

This command:
- Creates minimal bundle structure
- Delegates component creation to specialized commands
- Generates concise documentation (no embedded templates)
- Validates structure via /plugin-diagnose-bundle
- Trusts AI to format content appropriately

## CONTINUOUS IMPROVEMENT RULE

**This command should be improved using**: `/plugin-update-command plugin-create-bundle`

**Improvement areas**:
- Enhanced questionnaire flow with better default suggestions
- Improved plugin.json validation and schema enforcement
- Better component dependency detection and ordering
- Enhanced README generation based on bundle type patterns
- Expanded integration testing after bundle creation

## STANDARDS

Follows:
- Claude Code marketplace architecture
- Bundle structure conventions
- plugin.json schema
- Component organization standards

## RELATED

- `/plugin-create-skill` - Create skills within bundle
- `/plugin-create-command` - Create commands within bundle
- `/plugin-create-agent` - Create agents within bundle
- `/plugin-diagnose-bundle` - Validate bundle structure
- `cui-marketplace-architecture` skill - Architecture rules

## IMPORTANT NOTES

**plugin.json Structure:**
```json
{
  "name": "bundle-name",
  "display_name": "Display Name",
  "description": "Bundle description",
  "version": "1.0.0",
  "author": "Author Name",
  "components": []
}
```

**Marketplace Conventions:**
- Bundle names use kebab-case
- Component directories: skills/, commands/, agents/
- Each component has README.md
- plugin.json at bundle root
- Bundle README.md provides overview

**README Generation:**
Generate appropriate README content based on bundle type and purpose. No need for extensive templates - trust AI to create professional, clear documentation.
