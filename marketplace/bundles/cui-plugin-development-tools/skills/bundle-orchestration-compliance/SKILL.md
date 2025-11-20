---
name: bundle-orchestration-compliance
description: Bundle-by-bundle orchestration compliance patterns - mandatory completion checklists, anti-skip protections, post-fix verification requirements, and adherence rules for all diagnose commands
requirements:
  - Skill
standards:
  - mandatory-completion-checklist.md
  - anti-skip-protections.md
  - post-fix-verification.md
  - bundle-processing-rules.md
---

# Bundle Orchestration Compliance Skill

Provides mandatory compliance patterns for bundle-by-bundle orchestration workflows used in all diagnose commands (agents/commands/skills).

## What This Skill Provides

### Compliance Patterns
- **Mandatory Completion Checklist** - 10-item checklist before proceeding to next bundle
- **Anti-Skip Protections** - Warnings against skipping workflow steps (5e-5i)
- **Post-Fix Verification** - Git status verification after fixes applied
- **Bundle Processing Rules** - Sequential processing requirements and stop points

### Problem This Solves

**Without these patterns, diagnose commands can:**
- Skip critical workflow steps (analysis → fix → verify)
- Process partial subsets of components instead of complete bundles
- Accept agent "fix" claims without verifying actual file changes
- Jump to summary without completing fix workflows
- Produce incomplete/invalid diagnosis results

**With these patterns, diagnose commands must:**
- Complete all steps for one bundle before proceeding
- Validate all components in bundle (not partial)
- Verify fixes with git status (not just agent reports)
- Follow explicit stop points and completion checks

## When to Activate This Skill

**MANDATORY for all diagnose commands:**
- `/plugin-diagnose-commands` - Must enforce bundle-by-bundle compliance
- `/plugin-diagnose-agents` - Must enforce bundle-by-bundle compliance
- `/plugin-diagnose-skills` - Must enforce bundle-by-bundle compliance

**When to load:**
- At workflow start (Step 1) along with other diagnostic patterns
- Before Step 5 (bundle processing) to ensure rules are available
- When updating diagnose commands to add compliance checks

## Workflow

### Step 1: Load Compliance Patterns

**At the start of any bundle-by-bundle workflow:**

```
Skill: cui-plugin-development-tools:bundle-orchestration-compliance
```

This loads all compliance patterns that must be followed during bundle processing.

### Step 2: Read Specific Patterns

Based on workflow context, read relevant standards:

**Always read:**
```
Read: standards/bundle-processing-rules.md
```

**When implementing bundle processing loop (Step 5):**
```
Read: standards/mandatory-completion-checklist.md
Read: standards/anti-skip-protections.md
```

**When implementing fix workflow:**
```
Read: standards/post-fix-verification.md
```

### Step 3: Apply Compliance Patterns

**During bundle processing:**

1. **Before starting bundle loop:** Display bundle-processing-rules requirements
2. **At step transitions:** Check anti-skip protections
3. **After fixes applied:** Execute post-fix verification with git status
4. **Before next bundle:** Verify mandatory-completion-checklist

### Step 4: Enforce Compliance

**Enforcement mechanisms:**

1. **Explicit warnings** - Display consequences of skipping steps
2. **Stop points** - Clear indicators of when to pause vs continue
3. **Verification gates** - Must verify before proceeding
4. **Checklists** - Must check all items before advancing

## Standards Organization

All compliance patterns are in `standards/` directory:

- `bundle-processing-rules.md` - Core sequential processing requirements
- `mandatory-completion-checklist.md` - 10-item checklist before next bundle
- `anti-skip-protections.md` - Warnings and consequences for skipping steps
- `post-fix-verification.md` - Git status verification after fixes

## Tool Access

This skill requires:
- **Read** - To load compliance standards
- **Bash** - For git status verification in post-fix verification

## Usage Pattern

When this skill is activated, diagnose commands:

1. **Load patterns at workflow start** (Step 1)
2. **Reference patterns at critical points**:
   - "Follow bundle-processing-rules from bundle-orchestration-compliance"
   - "Apply mandatory-completion-checklist before proceeding"
   - "Execute post-fix-verification after fixes applied"
3. **Display warnings** from anti-skip-protections
4. **Verify compliance** using git status and checklists

## Integration with Diagnose Commands

### All Bundle-by-Bundle Diagnose Commands

**Required activation:**
```markdown
### Step 1: Load Diagnostic Patterns

Skill: cui-utilities:cui-diagnostic-patterns
Skill: cui-plugin-development-tools:cui-marketplace-architecture
Skill: cui-plugin-development-tools:bundle-orchestration-compliance  # ← MANDATORY
```

**Then reference throughout workflow:**
- Step 5 header: Reference bundle-processing-rules
- Step 5b: Reference anti-skip-protections for reference validation
- Steps 5e-5i: Reference anti-skip-protections for fix workflow
- After fixes: Execute post-fix-verification
- Step 5j: Apply mandatory-completion-checklist

### Benefits

Commands benefit by:
- Not duplicating compliance patterns across three commands
- Getting updated enforcement automatically
- Following consistent standards across agents/commands/skills diagnosis
- Preventing workflow violations that produce invalid results
- Ensuring all bundles are fully processed before summary

## Quality Standards

- Compliance patterns must be enforceable (actionable checks)
- Warnings must explain consequences of violations
- Checklists must cover all required steps
- Verification must use observable evidence (git status)
- Stop points must be explicit and unambiguous

## Related Skills

- `cui-marketplace-orchestration-patterns` - General orchestration architecture
- `cui-fix-workflow` - Fix categorization and application patterns
- `cui-diagnostic-patterns` - Non-prompting tool usage patterns

## Related Commands

- `/plugin-diagnose-commands` - Uses this skill for compliance enforcement
- `/plugin-diagnose-agents` - Uses this skill for compliance enforcement
- `/plugin-diagnose-skills` - Uses this skill for compliance enforcement

## Maintenance Notes

This skill provides the authoritative compliance patterns for:
- Bundle-by-bundle sequential processing
- Mandatory completion verification
- Anti-skip enforcement
- Post-fix verification

When compliance requirements change, update files in `standards/` directory and all diagnose commands automatically benefit.

## Version

Version: 1.0.0 (Initial release)

Part of: cui-plugin-development-tools bundle

---

*This skill ensures bundle-by-bundle workflows complete all required steps and verify actual fixes before proceeding.*
