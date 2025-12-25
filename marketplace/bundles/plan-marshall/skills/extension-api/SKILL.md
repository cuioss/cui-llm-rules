---
name: extension-api
description: Contract specification for bundle extension.py files that integrate with plan-marshall workflows
allowed-tools: Read
---

# Extension API Skill

Defines the contract for `extension.py` files that domain bundles implement to integrate with plan-marshall workflows.

## Purpose

Provides a single reference for all Extension API functions:
- Required functions all bundles must implement
- Domain functions (one required per bundle type)
- Optional workflow extension functions

## When to Reference This Skill

Reference when:
- Creating a new `extension.py` for a domain bundle
- Validating extension implementations
- Understanding how bundles integrate with plan-marshall

## Skill Structure

```
extension-api/
├── SKILL.md                     # This file (contract overview)
└── standards/
    └── extension-contract.md    # All function signatures and contracts
```

## Quick Reference

### Required Functions (All Bundles)

| Function | Purpose |
|----------|---------|
| `is_applicable(project_root: str) -> bool` | Detect if bundle applies to project |
| `provides_build_systems() -> list` | Return build system keys (or `[]`) |
| `get_command_mappings() -> dict` | Return command templates (or `{}`) |

### Domain Functions (One Required)

| Function | Use Case |
|----------|----------|
| `get_skill_domains() -> dict` | Primary domain bundles (pm-dev-java, pm-dev-frontend) |
| `get_domain_supplements() -> dict` | Supplement bundles extending a parent domain |

### Optional Functions

| Function | Purpose |
|----------|---------|
| `provides_triage() -> str \| None` | Return triage skill reference |
| `provides_outline() -> str \| None` | Return outline skill reference |

## Integration Points

- **build_env.py** - Discovers extensions via `is_applicable()`, `provides_build_systems()`, `get_command_mappings()`
- **cmd_skill_domains.py** - Loads domain metadata via `get_skill_domains()`, `get_domain_supplements()`
- **cmd_extension.py** - Validates extension implementations

## References

- `standards/extension-contract.md` - Complete function signatures and contracts
- `plan-marshall:build-operations` - Build system integration using extensions
