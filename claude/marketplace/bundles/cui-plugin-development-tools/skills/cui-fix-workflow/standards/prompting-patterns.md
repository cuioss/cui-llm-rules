# Prompting Patterns - User Confirmation for Risky Fixes

Defines the standard AskUserQuestion structure for presenting risky fixes to users for approval.

## Core Principle

Users must be given **clear, actionable information** to make informed decisions about risky fixes:
- What will be changed
- Why the change is needed
- What the impact will be
- Where the change will occur

## Standard Prompting Structure

### When to Prompt

**ALWAYS prompt** when risky fixes exist, regardless of `auto-fix` setting.

**Never prompt** for safe fixes when `auto-fix=true` (they're applied automatically).

### AskUserQuestion Pattern

Use this exact structure for consistency across all diagnosis commands:

```
AskUserQuestion:
  questions: [
    {
      question: "Apply fixes for {Category} issues?",
      header: "{Category}",
      multiSelect: true,
      options: [
        {
          label: "Fix: {specific-issue-1}",
          description: "Component: {name}. Impact: {what-changes}. Location: {file}:{line}"
        },
        {
          label: "Fix: {specific-issue-2}",
          description: "Component: {name}. Impact: {what-changes}. Location: {file}:{line}"
        },
        ...,
        {
          label: "Skip all {category} fixes",
          description: "Continue without fixing this category"
        }
      ]
    }
  ]
```

## Grouping Strategy

Group risky fixes into logical categories for better user experience:

### Standard Categories

1. **Duplication Issues** - Content found in multiple places
2. **Integration Issues** - Orphaned files, workflow disconnection
3. **Reference Problems** - Broken references, unclear cross-references
4. **Zero-Information Content** - Generic statements without actionable guidance
5. **Conflicting Guidance** - Contradictory recommendations
6. **Architectural Issues** - Pattern violations, bloat, structural problems

### Category Selection Rules

- Maximum 3-4 categories per prompt (avoid overwhelming user)
- Group related issues together
- Put most common/important categories first
- Always include "Skip all" option per category

## Option Formatting

Each fix option should follow this format:

### Label Format

```
"Fix: {brief-description-of-issue}"
```

**Examples:**
- "Fix: Duplicate content in two files"
- "Fix: Orphaned file not referenced anywhere"
- "Fix: Circular reference between sections"
- "Fix: Bloated command with 800 lines"

**Guidelines:**
- Keep labels under 60 characters
- Be specific enough to identify the issue
- Use action verbs (Fix, Remove, Consolidate, Extract)

### Description Format

```
"Component: {name}. Impact: {what-changes}. Location: {file}:{line}"
```

**Examples:**
- "Skill: cui-java-core. Impact: Removes duplicate example from java-modern-features.md. Location: standards/java-modern-features.md:104"
- "Agent: diagnose-skill. Impact: Extracts 200-line workflow to separate skill. Location: diagnose-skill.md:450-650"
- "Command: plugin-diagnose-agents. Impact: Fixes circular reference by removing self-invocation. Location: plugin-diagnose-agents.md:234"

**Guidelines:**
- Component: Name of the skill/agent/command being fixed
- Impact: Clear statement of what will change (1 sentence)
- Location: File path and line number(s) for the change

## User Selection Processing

### Pattern for Processing Selections

```markdown
**Process user selections:**

For each question category:
  For each option in user's answers:
    If option is specific fix:
      - Apply fix using Edit tool
      - Increment risky_fixes_applied counter
      - Add to applied_fixes list

    If option is "Skip all {category}":
      - Skip entire category
      - Increment risky_fixes_skipped by category count
      - Add to skipped_categories list

  For each fix NOT selected by user:
    - Skip fix
    - Increment risky_fixes_skipped counter
    - Add to skipped_fixes list
```

### Handling Multiple Categories

When prompting for multiple categories:

1. **Single AskUserQuestion call** with multiple questions array items
2. **Each category gets own question** in the array
3. **Process all responses** in a single pass
4. **Report results** grouped by category

**Example:**

```
AskUserQuestion:
  questions: [
    {
      question: "Apply fixes for Duplication issues?",
      header: "Duplication",
      multiSelect: true,
      options: [...]
    },
    {
      question: "Apply fixes for Integration issues?",
      header: "Integration",
      multiSelect: true,
      options: [...]
    },
    {
      question: "Apply fixes for Reference issues?",
      header: "References",
      multiSelect: true,
      options: [...]
    }
  ]
```

## Tracking Structure

Track prompting and user responses:

```json
{
  "risky_fixes_prompted": {count},
  "risky_fixes_applied": {count},
  "risky_fixes_skipped": {count},
  "fixes_by_category": {
    "duplication": {
      "prompted": {count},
      "applied": {count},
      "skipped": {count}
    },
    "integration": {
      "prompted": {count},
      "applied": {count},
      "skipped": {count}
    },
    "references": {
      "prompted": {count},
      "applied": {count},
      "skipped": {count}
    }
  },
  "applied_fixes": [
    {
      "category": "duplication",
      "issue": "Duplicate content in two files",
      "component": "cui-java-core",
      "location": "standards/java-modern-features.md:104"
    }
  ],
  "skipped_fixes": [
    {
      "category": "integration",
      "issue": "Orphaned file not referenced",
      "component": "cui-css",
      "location": "examples/legacy-example.md"
    }
  ],
  "skipped_categories": ["references"]
}
```

## Error Handling

If user selection fails or is unclear:

1. **No selections made**: Treat as "skip all" and continue
2. **Invalid selections**: Re-prompt with clarification
3. **Timeout**: Default to skipping all risky fixes

## Reporting After Prompting

After processing user selections, report results:

```
Risky Fix Results:
- Fixes applied: {risky_fixes_applied}
- Fixes skipped: {risky_fixes_skipped}

By Category:
- Duplication: {applied}/{prompted} applied
- Integration: {applied}/{prompted} applied
- References: {skipped} skipped (category skipped)
```

## Component-Specific Customization

Each diagnosis command defines:
- **Category names** relevant to that component type
- **Fix descriptions** specific to component issues
- **Impact statements** appropriate for component changes

The prompting structure and user selection processing remain consistent across all commands.

## Quality Standards

- Labels must be under 60 characters
- Descriptions must include Component, Impact, and Location
- Categories must have "Skip all" option
- Maximum 3-4 categories per prompt
- Tracking must record all prompted, applied, and skipped fixes
