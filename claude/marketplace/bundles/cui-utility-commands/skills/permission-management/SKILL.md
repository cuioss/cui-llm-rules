---
name: permission-management
description: Permission validation, architecture patterns, anti-patterns, and best practices for Claude Code settings management
allowed-tools:
  - Read
  - Grep
---

# Permission Management Skill

Comprehensive permission management patterns for Claude Code settings, including validation, architecture, security anti-patterns, and lessons learned from production usage.

## What This Skill Provides

### Permission Validation Standards
- Syntax validation patterns for all permission types
- Path format validation rules
- Duplicate detection algorithms
- Permission categorization logic

### Architecture Patterns
- Global vs Local permission separation
- Universal git access patterns
- Project-specific permission patterns
- Skill and tool permission organization

### Security Anti-Patterns
- Suspicious permission detection patterns
- Critical system directory checks
- Dangerous command patterns
- Overly broad wildcard detection

### Historical Lessons
- Production issues discovered and resolved
- Architecture evolution and rationale
- Best practices established over time

## When to Activate This Skill

Activate when:
- Building permission management commands
- Validating permission syntax
- Detecting security anti-patterns
- Understanding global/local architecture
- Implementing permission doctor commands

## Workflow

### Step 1: Load Permission Standards

```
Read: standards/permission-validation-standards.md
Read: standards/permission-architecture.md
Read: standards/permission-anti-patterns.md
```

### Step 2: Apply Standards

Use loaded standards for:
- Permission syntax validation
- Global/local categorization
- Anti-pattern detection
- Security checks

### Step 3: Reference Best Practices

```
Read: best-practices/lessons-learned.md
```

Apply lessons learned to avoid known pitfalls.

## Standards Organization

- `standards/permission-validation-standards.md` - Validation patterns, syntax rules, categorization
- `standards/permission-architecture.md` - Global/Local separation, universal access patterns
- `standards/permission-anti-patterns.md` - Security patterns, suspicious permission detection
- `best-practices/lessons-learned.md` - Historical issues, evolution, established practices

## Integration

Commands using this skill:
- `cui-setup-project-permissions` - Main permission management command
- Doctor commands validating permission requirements
- Security audit commands

## Version

Version: 1.0.0 (Initial extraction from cui-setup-project-permissions)

Part of: cui-utility-commands bundle
