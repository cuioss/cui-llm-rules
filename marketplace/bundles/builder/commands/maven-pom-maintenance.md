---
name: maven-pom-maintenance
description: Orchestrate POM maintenance workflows for dependency management, BOM optimization, and quality verification
---

# POM Maintenance Command

Orchestrates POM maintenance by routing to appropriate skill workflows based on user intent.

## PARAMETERS

| Parameter | Default | Description |
|-----------|---------|-------------|
| `action` | `analyze` | Workflow: `analyze`, `optimize`, `openrewrite`, `wrapper`, `verify` |
| `module` | (none) | Specific module to target |
| `auto_fix` | `true` | Auto-fix safe issues (optimize action) |

## WORKFLOW

### Step 1: Parse Parameters and Determine Action

Extract action from user input. Map common phrases:
- "analyze", "check", "audit" → `analyze`
- "fix", "optimize", "consolidate" → `optimize`
- "rewrite", "cleanup" → `openrewrite`
- "update wrapper", "maven version" → `wrapper`
- "verify", "validate", "quality" → `verify`

### Step 2: Delegate to Skill Workflow

```
Skill: builder:builder-pom-maintenance
Workflow: {action}
Parameters: module, auto_fix (as applicable)
```

**Action routing:**

| Action | Skill Workflow | Purpose |
|--------|----------------|---------|
| `analyze` | Analyze POM Issues | Identify dependency/BOM/scope issues |
| `optimize` | Optimize Dependencies | Apply fixes from analysis |
| `openrewrite` | Run OpenRewrite Cleanup | Execute POM cleanup recipes |
| `wrapper` | Update Maven Wrapper | Update to latest Maven version |
| `verify` | Verify POM Quality | Run quality gate checks |

### Step 3: Report Results

**For analyze:**
```
POM ANALYSIS

Unused dependencies: {n}
Undeclared dependencies: {n}
Hardcoded versions: {n}
BOM violations: {n}
Scope issues: {n}

Run `/maven-pom-maintenance action=optimize` to fix safe issues
```

**For optimize:**
```
POM OPTIMIZATION

Fixed: {n} issues
Requires confirmation: {n} issues
Skipped: {n} issues

Run `/maven-pom-maintenance action=verify` to validate
```

**For openrewrite:**
```
OPENREWRITE CLEANUP

Files modified: {n}
Recipes applied: [...]
Build status: {SUCCESS|FAILURE}
```

**For wrapper:**
```
MAVEN WRAPPER UPDATE

Previous: {version}
Current: {version}
Build status: {SUCCESS|FAILURE}
```

**For verify:**
```
POM QUALITY REPORT

Build: {PASS|FAIL}
Dependency analysis: {PASS|FAIL}
Enforcer: {PASS|FAIL}
OpenRewrite: {PASS|FAIL}
Overall: {PASS|FAIL}
```

## TYPICAL WORKFLOW

Full POM maintenance sequence:

1. `/maven-pom-maintenance action=wrapper` - Update Maven first
2. `/maven-pom-maintenance action=openrewrite` - Run automated cleanup
3. `/maven-pom-maintenance action=analyze` - Identify remaining issues
4. `/maven-pom-maintenance action=optimize` - Fix identified issues
5. `/maven-pom-maintenance action=verify` - Validate quality

## CRITICAL RULES

- NEVER execute `./mvnw` directly - use skill workflows
- All POM standards in builder-pom-maintenance skill
- This command only orchestrates: parse → delegate → report
- Dependency version updates handled by Dependabot (not this command)

## RELATED

- Skill: `builder:builder-pom-maintenance` - POM maintenance workflows
- Skill: `builder:builder-maven-rules` - Maven build execution
- Command: `/maven-build-and-fix` - Build error fixing
