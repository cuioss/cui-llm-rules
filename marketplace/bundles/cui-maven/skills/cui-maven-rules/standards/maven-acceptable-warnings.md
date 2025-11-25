# Acceptable Warnings Standards

## Purpose

This document defines standards for managing acceptable warnings in Maven builds. Some warnings are infrastructure-related and cannot be fixed in project code. These can be documented as "acceptable" to avoid repeated manual review.

## Warning Classification

### Infrastructure Warnings (Can Be Acceptable)

Warnings that originate from external factors beyond project control:

1. **Transitive Dependency Conflicts**
   - Version conflicts from dependencies of dependencies
   - Cannot be resolved without changing external library versions
   - Example: `[WARNING] Conflicting dependency: org.slf4j:slf4j-api versions 1.7.x vs 2.0.x`

2. **Plugin Compatibility Warnings**
   - Plugin warnings for configurations locked by parent POM
   - Cannot change without affecting entire project hierarchy
   - Example: `[WARNING] Parameter 'skip' is deprecated for plugin X`

3. **Platform-Specific Warnings**
   - Warnings related to OS, JVM version, or hardware
   - Not addressable in project code
   - Example: `[WARNING] Signal handling not available on this platform`

### Fixable Warnings (NEVER Acceptable)

These warnings MUST be fixed and NEVER added to acceptable list:

1. **JavaDoc Warnings** - ALWAYS FIX
   - Missing @param, @return tags
   - Invalid references
   - Syntax errors

2. **Compilation Warnings** - ALWAYS FIX
   - Unchecked casts
   - Raw type usage
   - Unused variables

3. **Deprecation Warnings** - ALWAYS FIX (unless external)
   - Usage of deprecated APIs
   - Only acceptable if from external dependency with no alternative

4. **Code Quality Warnings** - ALWAYS FIX
   - Static analysis warnings
   - Potential null pointer issues
   - Resource leak warnings

## Configuration File Format

Acceptable warnings are stored in `.claude/run-configuration.json`:

```json
{
  "version": 1,
  "maven": {
    "acceptable_warnings": {
      "transitive_dependency": [
        "Overriding managed version 2.0.0 for slf4j-api"
      ],
      "plugin_compatibility": [
        "Parameter 'session' is deprecated"
      ],
      "platform_specific": []
    }
  }
}
```

### JSON Path Access

To read acceptable warnings:
```
Path: maven.acceptable_warnings
Categories: transitive_dependency, plugin_compatibility, platform_specific
```

Use the `cui-utilities:claude-run-configuration` skill to validate and the `cui-utilities:json-file-operations` skill to manage entries.

## Adding Acceptable Warnings

### Validation Requirements

Before adding a warning to acceptable list:

1. **Verify it's infrastructure-related**
   - Cannot be fixed by changing project code
   - Originates from external dependency or configuration

2. **Confirm it's NOT a fixable category**
   - Not JavaDoc (ALWAYS fix)
   - Not compilation (ALWAYS fix)
   - Not deprecation from project code (ALWAYS fix)

3. **Document the reason**
   - Explain why warning cannot be fixed
   - Reference external constraint

### Add Workflow

Use the `cui-utilities:json-file-operations` skill:

```bash
python3 scripts/manage-json-file.py add-entry \
    .claude/run-configuration.json \
    --field "maven.acceptable_warnings.transitive_dependency" \
    --value '"Overriding managed version 2.0.0 for slf4j-api"'
```

## Removing Acceptable Warnings

Remove warnings from acceptable list when:
- Root cause is resolved (dependency updated, plugin changed)
- Warning no longer appears in build output
- Workaround becomes available

### Remove Workflow

Use the `cui-utilities:json-file-operations` skill:

```bash
python3 scripts/manage-json-file.py remove-entry \
    .claude/run-configuration.json \
    --field "maven.acceptable_warnings.transitive_dependency" \
    --value '"Overriding managed version 2.0.0 for slf4j-api"'
```

## Pattern Matching

Warnings in build output are matched against acceptable list:

1. **Exact Match**: Pattern matches warning exactly
2. **Prefix Match**: Pattern matches start of warning
3. **Contains Match**: Warning contains pattern substring

Example patterns:
```
# Exact match
[WARNING] Using platform encoding

# Prefix match
[WARNING] Overriding managed version

# Contains match
deprecated for plugin
```

## Build Integration

During build verification:

1. Parse all `[WARNING]` lines from output
2. For each warning, check against acceptable list
3. If matched, skip (acceptable warning)
4. If NOT matched:
   - Check if fixable category → FIX IT
   - If infrastructure → ASK USER to add to acceptable

## JavaDoc Warning Handling

**CRITICAL**: JavaDoc warnings are NEVER acceptable.

If a JavaDoc warning is presented for acceptance:
1. REFUSE to add it
2. Explain that JavaDoc warnings must be fixed
3. Suggest running `/java-fix-javadoc`

```
⚠️ JavaDoc warnings cannot be added to acceptable list.
   These must be fixed using /java-fix-javadoc command.
```

## Maintenance

### Periodic Review

Review acceptable warnings list periodically:
- When upgrading dependencies
- When updating parent POM
- When changing Maven plugins

### Cleanup

Remove stale entries:
- Warnings that no longer appear
- Warnings from removed dependencies
- Warnings fixed by updates

## See Also

- [Maven Build Execution Standards](maven-build-execution.md) - Build workflow
- [OpenRewrite Handling Standards](maven-openrewrite-handling.md) - Marker handling
