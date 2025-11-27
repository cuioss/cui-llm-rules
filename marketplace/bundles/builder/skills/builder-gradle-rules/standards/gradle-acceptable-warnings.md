# Gradle Acceptable Warnings

Standards for classifying and managing acceptable build warnings in Gradle projects.

## Warning Classification

### Infrastructure Warnings (Can Be Acceptable)

Warnings from build infrastructure that may be accepted:

#### Dependency Resolution Warnings

```
Could not resolve all files for configuration
Duplicate class found in modules
```

**When Acceptable**:
- Transitive dependency conflicts with known-good resolution
- Test scope duplicates with no runtime impact
- Known library incompatibilities with workarounds

#### Plugin Compatibility Warnings

```
Task 'xxx' is deprecated and will be removed
Configuration 'compile' is deprecated
```

**When Acceptable**:
- Waiting for plugin update
- Using deprecated API intentionally for compatibility
- Third-party plugin not yet updated

#### Platform-Specific Warnings

```
Unable to detect Kotlin version
File encoding not explicitly set
```

**When Acceptable**:
- CI environment differences
- Development vs. production configuration

### Fixable Warnings (NEVER Acceptable)

These warnings must always be fixed:

#### JavaDoc Warnings

```
warning: no @param for 'name'
warning: no @return
warning: missing @throws
```

**Always Fix**: Documentation must be complete

#### Compilation Errors

```
error: cannot find symbol
error: incompatible types
```

**Always Fix**: Code must compile cleanly

#### Deprecation Warnings (Internal Code)

```
[deprecation] method() is deprecated
```

**Always Fix**: Use modern alternatives
**Exception**: External library deprecations may be acceptable if no alternative exists

#### Unchecked Warnings

```
[unchecked] unchecked conversion
```

**Always Fix**: Add proper generics or explicit suppression with comment

## Configuration Access

### Reading Acceptable Patterns

```
Skill: cui-utilities:claude-run-configuration
Workflow: Read Configuration
Field: gradle.acceptable_warnings
```

### Configuration Structure

```json
{
  "gradle": {
    "acceptable_warnings": {
      "dependency_resolution": [
        "Could not resolve all files for configuration ':compileClasspath'"
      ],
      "plugin_compatibility": [
        "The compile configuration has been deprecated"
      ],
      "platform_specific": [
        "Unable to initialize native filesystem"
      ]
    }
  }
}
```

## Adding Acceptable Warnings

### Workflow

1. **Identify Warning**: Capture exact warning message
2. **Verify Criteria**: Ensure it's truly infrastructure-related
3. **Document Reason**: Why this warning is acceptable
4. **Add Pattern**: Update configuration

### Add Pattern Command

```
Skill: cui-utilities:claude-run-configuration
Workflow: Update Configuration
Action: add-entry
Field: gradle.acceptable_warnings.dependency_resolution
Value: "Could not resolve artifact com.example:legacy:1.0"
```

## Removing Acceptable Warnings

When a warning is fixed or no longer needed:

```
Skill: cui-utilities:claude-run-configuration
Workflow: Update Configuration
Action: remove-entry
Field: gradle.acceptable_warnings.dependency_resolution
Value: "Could not resolve artifact com.example:legacy:1.0"
```

## Infrastructure Warning Criteria

A warning can be marked as acceptable if ALL of these are true:

1. **Not Code Quality**: Warning is not about code quality
2. **Infrastructure Related**: Warning comes from build tool, not application code
3. **No Direct Fix**: No straightforward code change resolves it
4. **Known Issue**: The cause is understood and documented
5. **No Runtime Impact**: Warning doesn't indicate runtime issues

## Build Integration Workflow

### Pre-Build Check

1. Execute build
2. Parse warnings
3. Load acceptable patterns
4. Categorize warnings:
   - `acceptable`: Match patterns, skip
   - `fixable`: Always-fix types, require action
   - `unknown`: Present to user

### Warning Categorization Script

```bash
python3 scripts/check-acceptable-warnings.py \
    --warnings '{issues_json}' \
    --acceptable-warnings '{patterns_json}'
```

### Exit Code Interpretation

- `0`: No fixable or unknown warnings (build clean)
- `1`: Fixable or unknown warnings exist (action needed)

## Pattern Matching

### Exact Match

```json
"Could not resolve com.example:lib:1.0"
```

### Prefix Match

```json
"Could not resolve com.example:*"
```

### Contains Match

```json
"*deprecated*"
```

### Regex Match

```json
"^Configuration '\\w+' is deprecated"
```

## Review Process

### Quarterly Review

1. List all acceptable patterns
2. Check if issues are still present
3. Remove obsolete patterns
4. Update documentation

### New Warning Approval

Before adding a new acceptable warning:
1. Team review recommended
2. Document in project notes
3. Create tracking issue if temporary
