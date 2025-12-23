# Plan-Marshall Plugin Validation Guide

Validation rules for skills named `plan-marshall-plugin` that contain domain or supplement manifests.

## When to Use This Guide

Load this reference when doctoring a skill where:
- `name` in frontmatter equals `plan-marshall-plugin`
- The skill contains a `plugin.json` file with `domain` or `supplements` field

## Manifest Types

| Type | Schema Field | Purpose |
|------|--------------|---------|
| Domain | `domain` | Declares a new domain with profiles and extensions |
| Supplement | `supplements` | Adds skills to an existing domain's profiles |

## Validation Script

Use the domain-extension-api validation script:

```bash
python3 .plan/execute-script.py plan-marshall:domain-extension-api:validate_manifest validate \
  --bundle {bundle_name}
```

**Note**: Extract bundle name from the skill path: `marketplace/bundles/{bundle}/skills/plan-marshall-plugin`

## Domain Manifest Validation

### Required Checks

| Check | Description | Fix Type |
|-------|-------------|----------|
| `$schema` present | Must reference domain-manifest-v1.json | Safe |
| `domain.key` present | Domain identifier (kebab-case) | Safe |
| `domain.name` present | Human-readable name | Safe |
| `profiles.core` present | Core profile is required | Safe |
| Profile structure | Each profile has `defaults` and `optionals` arrays | Safe |
| Skill reference format | All refs match `bundle:skill` pattern | Safe |

### Extension Checks (Optional)

| Check | Description | Fix Type |
|-------|-------------|----------|
| `extensions.outline` exists | If declared, skill must exist | Risky |
| `extensions.triage` exists | If declared, skill must exist | Risky |
| Extension implements contract | Must have required sections | Risky |

### Profile Names

Valid profile names:
- `core` (required)
- `implementation` (optional)
- `testing` (optional)
- `quality` (optional)

Any other profile name is invalid.

## Supplement Manifest Validation

### Required Checks

| Check | Description | Fix Type |
|-------|-------------|----------|
| `$schema` present | Must reference domain-supplements-v1.json | Safe |
| `supplements.domain` present | Target domain key | Safe |
| `supplements.skills` present | Profile-to-skills mapping | Safe |
| Profile names valid | Only core/implementation/testing/quality | Safe |
| Skill reference format | All refs match `bundle:skill` pattern | Safe |
| Skills exist | Referenced skills must exist in bundle | Risky |

## Validation Output

### Success Output

```toon
status: success
type: domain
domain: java
schema_version: v1
validation:
  manifest: valid
  extensions:
    outline: valid (pm-dev-java:java-outline-ext exists)
    triage: valid (pm-dev-java:java-triage exists)
  profiles:
    core: valid
    implementation: valid
    testing: valid
    quality: valid
```

### Error Output

```toon
status: error
type: domain
domain: java
schema_version: v1
validation:
  manifest: invalid
  profiles:
    core: missing
errors:
  - Missing required profile: 'core'
```

## Fix Patterns

### Safe Fixes

**Add missing `$schema`**:
```json
{
  "$schema": "https://raw.githubusercontent.com/cuioss/cui-llm-rules/main/marketplace/bundles/plan-marshall/skills/domain-extension-api/schemas/domain-manifest-v1.json",
  ...
}
```

**Fix profile structure** (add missing arrays):
```json
{
  "profiles": {
    "core": {
      "defaults": [],
      "optionals": []
    }
  }
}
```

### Risky Fixes

**Missing extension skill**: Cannot auto-fix. Requires either:
1. Creating the extension skill
2. Removing the extension reference

**Invalid skill reference**: Cannot auto-fix. Requires manual review of:
1. Skill existence
2. Bundle correctness
3. Skill name spelling

## Integration with doctor-skills Workflow

When `skill-name` matches `plan-marshall-plugin`:

1. **Standard analysis** (Step 3):
   - Run `analyze.py structure` on skill directory
   - Run `analyze.py markdown` on SKILL.md
   - Run `validate.py references` on SKILL.md

2. **Additional manifest validation** (Step 3c):
   ```bash
   # Extract bundle from path
   BUNDLE=$(echo "{skill_path}" | sed 's|.*bundles/\([^/]*\)/.*|\1|')

   # Run manifest validation
   python3 .plan/execute-script.py plan-marshall:domain-extension-api:validate_manifest validate \
     --bundle ${BUNDLE}
   ```

3. **Report findings**:
   - Include manifest validation status in output
   - Categorize issues as safe/risky
   - Apply safe fixes automatically
   - Prompt for risky fixes

## Example Workflow

```markdown
### Step 3c: Validate Manifest (plan-marshall-plugin only)

If skill name is `plan-marshall-plugin`:

1. Extract bundle name from skill path
2. Run manifest validation script
3. Parse validation output
4. Add findings to issue list
5. Categorize as safe/risky based on fix type table
```
