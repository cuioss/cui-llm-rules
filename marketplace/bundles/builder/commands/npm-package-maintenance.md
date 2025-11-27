---
name: npm-package-maintenance
description: Orchestrate package.json maintenance for dependency auditing, updates, and verification
---

# npm Package Maintenance Command

Orchestrates package.json maintenance by routing to skill workflows based on user intent.

## PARAMETERS

| Parameter | Default | Description |
|-----------|---------|-------------|
| `action` | `analyze` | Workflow: `analyze`, `audit`, `update`, `verify` |
| `workspace` | (none) | Specific workspace to target |
| `auto_fix` | `false` | Auto-fix audit issues where safe |

## WORKFLOW

### Step 1: Parse Parameters and Determine Action

Extract action from user input. Map common phrases:
- "analyze", "check", "status" → `analyze`
- "audit", "security", "vulnerabilities" → `audit`
- "update", "upgrade", "outdated" → `update`
- "verify", "validate", "test" → `verify`

### Step 2: Delegate to Skill Workflow

```
Skill: builder:builder-npm-rules
Workflow: {action}
Parameters: workspace, auto_fix (as applicable)
```

**Action routing:**

| Action | Purpose |
|--------|---------|
| `analyze` | Check outdated packages, audit summary |
| `audit` | Run security audit, optionally fix |
| `update` | Update packages to latest compatible versions |
| `verify` | Run build and tests to validate state |

### Step 3: Execute Action

**For analyze:**
```bash
npm outdated
npm audit --audit-level=moderate
```

**For audit:**
```bash
npm audit
# If auto_fix=true:
npm audit fix
```

**For update:**
```bash
npm update
npm install
```

**For verify:**
```
Skill: builder:builder-npm-rules
Workflow: Execute npm Build
Parameters: command="run test", workspace
```

### Step 4: Report Results

**For analyze:**
```
PACKAGE ANALYSIS

Outdated packages: {n}
Security vulnerabilities: {n} (high: {n}, moderate: {n}, low: {n})
Lock file status: {synced|outdated}

Run `/npm-package-maintenance action=audit auto_fix=true` to fix vulnerabilities
```

**For audit:**
```
SECURITY AUDIT

Vulnerabilities found: {n}
Fixed: {n} (if auto_fix)
Manual review required: {n}

Run `/npm-package-maintenance action=verify` to validate
```

**For update:**
```
PACKAGE UPDATE

Updated: {n} packages
Lock file: regenerated

Run `/npm-package-maintenance action=verify` to validate
```

**For verify:**
```
VERIFICATION REPORT

Build: {PASS|FAIL}
Tests: {PASS|FAIL}
Overall: {PASS|FAIL}
```

## TYPICAL WORKFLOW

Full package maintenance sequence:

1. `/npm-package-maintenance action=analyze` - Check current state
2. `/npm-package-maintenance action=audit auto_fix=true` - Fix security issues
3. `/npm-package-maintenance action=update` - Update dependencies
4. `/npm-package-maintenance action=verify` - Validate everything works

## CRITICAL RULES

- NEVER execute `npm` directly for complex operations - use skill workflows
- All npm standards in builder-npm-rules skill
- This command only orchestrates: parse → delegate → report
- Major version updates should be reviewed manually

## RELATED

- Skill: `builder:builder-npm-rules` - npm build execution
- Skill: `cui-frontend-expert:cui-javascript-project` - Project structure
- Command: `/npm-build-and-fix` - Build error fixing
