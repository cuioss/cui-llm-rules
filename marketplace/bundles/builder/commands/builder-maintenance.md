---
name: builder-maintenance
description: Orchestrate dependency/package maintenance workflows (auto-detects build system)
---

# Builder Maintenance Command

Unified maintenance command that auto-detects or accepts build system specification.

## PARAMETERS

| Parameter | Default | Description |
|-----------|---------|-------------|
| `system` | (auto-detect) | Build system: `maven`, `gradle`, `npm` |
| `action` | `analyze` | Action to perform (system-specific) |
| `module` | (none) | Maven module / Gradle project / npm workspace |
| `auto_fix` | varies | Auto-fix safe issues |

**Actions by system:**

| System | Actions |
|--------|---------|
| maven | `analyze`, `optimize`, `openrewrite`, `wrapper`, `verify` |
| gradle | `analyze`, `optimize`, `catalog`, `wrapper`, `verify` |
| npm | `analyze`, `audit`, `update`, `verify` |

## WORKFLOW

### Step 1: Determine Build System

**If `system` parameter provided:** Use specified system.

**If `system` not provided:** Auto-detect:

```
Skill: builder:environment-detection
Workflow: Get Build Environment
```

Use `default_system` from result.

**If no system detected:** Report error and exit.

### Step 2: Parse Action

Map common phrases to actions:

| Phrase | Action |
|--------|--------|
| "analyze", "check", "status" | `analyze` |
| "fix", "optimize" | `optimize` |
| "audit", "security" | `audit` (npm) |
| "update", "upgrade" | `update` (npm) / `wrapper` (maven/gradle) |
| "catalog" | `catalog` (gradle) |
| "rewrite", "cleanup" | `openrewrite` (maven) |
| "verify", "validate" | `verify` |

### Step 3: Delegate to System-Specific Skill

**Maven:**
```
Skill: builder:builder-pom-maintenance
Workflow: {action}
Parameters: module, auto_fix
```

**Gradle:**
```
Skill: builder:builder-gradle-dependencies
Workflow: {action}
Parameters: project={module}, auto_fix
```

**npm:**
```
Skill: builder:builder-npm-rules
Workflow: {action}
Parameters: workspace={module}, auto_fix
```

### Step 4: Report Results

**For analyze:**
```
DEPENDENCY ANALYSIS ({system})

Issues found: {n}
- Unused dependencies: {n}
- Outdated: {n}
- Security: {n}

Run `/builder-maintenance action=optimize` to fix safe issues
```

**For optimize/audit/update:**
```
MAINTENANCE COMPLETE ({system})

Fixed: {n} issues
Manual review required: {n}

Run `/builder-maintenance action=verify` to validate
```

**For verify:**
```
VERIFICATION REPORT ({system})

Build: {PASS|FAIL}
Tests: {PASS|FAIL}
Overall: {PASS|FAIL}
```

## TYPICAL WORKFLOWS

**Maven:**
```bash
/builder-maintenance system=maven action=wrapper
/builder-maintenance system=maven action=openrewrite
/builder-maintenance system=maven action=analyze
/builder-maintenance system=maven action=optimize
/builder-maintenance system=maven action=verify
```

**Gradle:**
```bash
/builder-maintenance system=gradle action=wrapper
/builder-maintenance system=gradle action=analyze
/builder-maintenance system=gradle action=catalog
/builder-maintenance system=gradle action=verify
```

**npm:**
```bash
/builder-maintenance system=npm action=analyze
/builder-maintenance system=npm action=audit auto_fix=true
/builder-maintenance system=npm action=update
/builder-maintenance system=npm action=verify
```

## EXAMPLE USAGE

```bash
# Auto-detect and analyze
/builder-maintenance

# Explicit system
/builder-maintenance system=maven action=optimize
/builder-maintenance system=gradle action=catalog
/builder-maintenance system=npm action=audit

# With module targeting
/builder-maintenance module=api action=analyze
/builder-maintenance system=gradle module=":core" action=verify

# Auto-fix enabled
/builder-maintenance action=optimize auto_fix=true
```

## CRITICAL RULES

- NEVER execute build tools directly - use skill workflows
- System parameter takes precedence over auto-detection
- This command only orchestrates: detect -> parse -> delegate -> report
- Major version updates should be reviewed manually

## RELATED

- Skill: `builder:environment-detection` - Build system auto-detection
- Skill: `builder:builder-pom-maintenance` - Maven POM maintenance
- Skill: `builder:builder-gradle-dependencies` - Gradle dependency management
- Skill: `builder:builder-npm-rules` - npm package maintenance
- Command: `/builder-build-and-fix` - Build error fixing
