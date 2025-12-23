# Domain Extension Architecture

This document describes the plugin extension architecture for bundle-declared domain capabilities.

## Design Goals

1. **Bundle Self-Description**: Bundles declare their own domain capabilities
2. **Automatic Discovery**: Installed bundles are automatically discoverable
3. **Contract Enforcement**: Extension contracts are validated at registration
4. **Decentralized Configuration**: No hardcoded templates - all config lives in bundles
5. **Clean Architecture**: No legacy fallbacks or compatibility layers

## Architecture Overview

```
DOMAIN BUNDLE (pm-dev-java)
├── .claude-plugin/
│   └── plugin.json          # Claude Code component manifest (existing)
├── skills/
│   ├── plan-marshall-plugin/  # Fixed name for domain manifest
│   │   ├── SKILL.md           # Minimal skill definition
│   │   └── plugin.json        # Domain capability manifest
│   ├── java-core/           # Core domain skill
│   ├── java-outline-ext/    # Outline extension (optional)
│   └── java-triage/         # Triage extension (optional)
└── ...

SUPPLEMENT BUNDLE (pm-dev-java-cui)
├── .claude-plugin/
│   └── plugin.json          # Claude Code component manifest (existing)
└── skills/
    ├── plan-marshall-plugin/  # Fixed name for supplement manifest
    │   ├── SKILL.md           # Minimal skill definition
    │   └── plugin.json        # Supplement manifest (targets java domain)
    ├── cui-logging/         # Supplementary skill
    └── cui-testing/         # Supplementary skill

CENTRAL CONTRACT (plan-marshall)
└── skills/domain-extension-api/
    ├── SKILL.md             # Central contract definitions
    ├── scripts/
    │   ├── discover_domains.py  # Scan for domains AND supplements
    │   └── validate_manifest.py # Validate domain OR supplement manifest
    └── standards/
        ├── domain-schema.md         # Domain manifest schema
        ├── supplements-schema.md    # Supplement manifest schema
        ├── outline-extension.md     # Outline extension contract
        ├── triage-extension.md      # Triage extension contract
        └── profile-contract.md      # Profile structure contract

RUNTIME (marshal.json)
└── skill_domains: {...}     # Assembled from domains + merged supplements
```

## Manifest Types

### Domain Manifest

A domain manifest declares a new domain with profiles and optional extensions.

**Location**: `{bundle}/skills/plan-marshall-plugin/plugin.json`

**Schema**: `domain-manifest-v1.json`

**Example**:
```json
{
  "$schema": "https://raw.githubusercontent.com/cuioss/cui-llm-rules/main/marketplace/bundles/plan-marshall/skills/domain-extension-api/schemas/domain-manifest-v1.json",
  "domain": {
    "key": "java",
    "name": "Java Development",
    "description": "Java code patterns, CDI, JUnit testing, Maven/Gradle builds"
  },
  "extensions": {
    "outline": "pm-dev-java:java-outline-ext",
    "triage": "pm-dev-java:java-triage"
  },
  "profiles": {
    "core": {
      "defaults": ["pm-dev-java:java-core"],
      "optionals": ["pm-dev-java:java-null-safety", "pm-dev-java:java-lombok"]
    },
    "implementation": {
      "defaults": [],
      "optionals": ["pm-dev-java:java-cdi", "pm-dev-java:java-maintenance"]
    },
    "testing": {
      "defaults": ["pm-dev-java:junit-core"],
      "optionals": ["pm-dev-java:junit-integration"]
    },
    "quality": {
      "defaults": ["pm-dev-java:javadoc"],
      "optionals": []
    }
  }
}
```

### Supplement Manifest

A supplement manifest adds skills to an existing domain's profiles.

**Location**: `{bundle}/skills/plan-marshall-plugin/plugin.json`

**Schema**: `domain-supplements-v1.json`

**Example**:
```json
{
  "$schema": "https://raw.githubusercontent.com/cuioss/cui-llm-rules/main/marketplace/bundles/plan-marshall/skills/domain-extension-api/schemas/domain-supplements-v1.json",
  "supplements": {
    "domain": "java",
    "description": "CUI-specific Java patterns for logging, testing, and HTTP",
    "skills": {
      "core": {
        "defaults": [],
        "optionals": ["pm-dev-java-cui:cui-logging"]
      },
      "implementation": {
        "defaults": [],
        "optionals": ["pm-dev-java-cui:cui-http"]
      },
      "testing": {
        "defaults": [],
        "optionals": ["pm-dev-java-cui:cui-testing", "pm-dev-java-cui:cui-testing-http"]
      }
    }
  }
}
```

## Discovery Flow

1. Scan plugin directories for bundles with `skills/plan-marshall-plugin/plugin.json`
2. Read manifest and detect type (`domain` vs `supplements` field)
3. Collect domains and supplements separately
4. Return structured output with both lists

## Validation Flow

### At Bundle Install

1. Check for `skills/plan-marshall-plugin/plugin.json`
2. Detect manifest type from content
3. Validate against appropriate schema
4. Check referenced skills exist
5. For domains: validate extension skills have required sections

## Runtime Merging

When configuring domains with supplements:

1. Read domain manifest profiles
2. Read supplement manifest skills
3. Merge supplement skills into domain profiles (as optionals)
4. Write merged config to marshal.json

**Example result**:
```json
{
  "java": {
    "core": {
      "defaults": ["pm-dev-java:java-core"],
      "optionals": ["pm-dev-java:java-null-safety", "pm-dev-java-cui:cui-logging"]
    },
    "testing": {
      "defaults": ["pm-dev-java:junit-core"],
      "optionals": ["pm-dev-java:junit-integration", "pm-dev-java-cui:cui-testing"]
    }
  }
}
```

## Design Decisions

### Version Compatibility

Version is encoded in the `$schema` URL (e.g., `domain-manifest-v1.json`). Validation extracts and checks the version from the schema reference.

### Multi-Domain Bundles

No multi-domain bundles. One bundle = one domain. Supplementary bundles use a different manifest type.

### Domain Inheritance

No inheritance. Use composition instead. Domains do not extend other domains.

### Optional Extensions

Extensions are not required. If present, they can be minimal stubs. A domain can omit `extensions` entirely.

## Benefits

| Aspect | Before | After |
|--------|--------|-------|
| Add new domain | Modify central file | Add `skills/plan-marshall-plugin/` to bundle |
| Bundle isolation | No | Yes - all config in bundle |
| Automatic discovery | No | Yes - scan for `plan-marshall-plugin` skill |
| Contract validation | No | Yes - validate at install |
| Extension validation | No | Yes - check required sections |
| Central hardcoding | `config_defaults.py` | Eliminated |

## Breaking Changes

- `DOMAIN_TEMPLATES` in `config_defaults.py` is deleted
- Bundles without `skills/plan-marshall-plugin/` are not discoverable as domains
- No fallback or compatibility layer
