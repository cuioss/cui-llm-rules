---
name: domain-extension-api
description: Central contract definitions for domain extensions and supplements. Provides validation and discovery.
allowed-tools: Read, Bash
---

# Domain Extension API

Central contract skill for domain and supplement registration and validation.

## What This Skill Provides

1. Define domain manifest schema (plugin.json with `domain` field)
2. Define supplement manifest schema (plugin.json with `supplements` field)
3. Define extension contracts (outline, triage)
4. Provide validation scripts
5. Support automatic domain and supplement discovery

## When to Activate This Skill

Activate when:
- Validating domain bundle manifests
- Validating supplement bundle manifests
- Discovering installed domains
- Checking extension contract compliance

---

## Workflow: Discover Domains and Supplements

**Pattern**: Script Automation

Scan installed bundles for domain and supplement manifests.

### Discovery

```bash
python3 .plan/execute-script.py plan-marshall:domain-extension-api:discover_domains discover
```

**Output**:
```toon
status: success
domains_found: 3
supplements_found: 1

domains[3]{key,name,bundle,has_outline,has_triage}:
java	Java Development	pm-dev-java	true	true
javascript	JavaScript Development	pm-dev-frontend	true	true
plan-marshall-plugin-dev	Plugin Development	pm-plugin-development	true	true

supplements[1]{domain,bundle,description}:
java	pm-dev-java-cui	CUI-specific Java patterns for logging, testing, and HTTP
```

---

## Workflow: Validate Manifest

**Pattern**: Script Automation

Validate a bundle's domain or supplement manifest.

### Validate Domain Bundle

```bash
python3 .plan/execute-script.py plan-marshall:domain-extension-api:validate_manifest validate \
  --bundle pm-dev-java
```

**Output**:
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

### Validate Supplement Bundle

```bash
python3 .plan/execute-script.py plan-marshall:domain-extension-api:validate_manifest validate \
  --bundle pm-dev-java-cui
```

**Output**:
```toon
status: success
type: supplement
target_domain: java
schema_version: v1
validation:
  manifest: valid
  profiles:
    core: valid
    implementation: valid
    testing: valid
  skills_exist: true
```

---

## Validation Checks

### Domain Validation

| Check | Description |
|-------|-------------|
| Schema compliance | plugin.json matches domain schema |
| Schema version | Version extracted from `$schema` URL is supported |
| Extension existence | Referenced extension skills exist (if declared) |
| Extension sections | Extension skills have required sections (if declared) |
| Profile structure | Profiles have defaults/optionals arrays |
| Skill references | All referenced skills exist in bundle |

### Supplement Validation

| Check | Description |
|-------|-------------|
| Schema compliance | plugin.json matches supplement schema |
| Schema version | Version extracted from `$schema` URL is supported |
| Target domain | Domain key is valid |
| Profile names | Only valid profiles (core, implementation, testing, quality) |
| Skill references | All referenced skills exist in bundle |

---

## Scripts

| Script | Notation | Purpose |
|--------|----------|---------|
| discover_domains | `plan-marshall:domain-extension-api:discover_domains` | Scan for domains and supplements |
| validate_manifest | `plan-marshall:domain-extension-api:validate_manifest` | Validate domain or supplement manifest |

Script characteristics:
- Uses Python stdlib only (json, argparse, pathlib)
- Outputs TOON to stdout
- Exit code 0 for success, 1 for errors
- Supports `--help` flag

---

## Standards

| Document | Purpose |
|----------|---------|
| domain-schema.md | Human-readable domain manifest schema |
| supplements-schema.md | Human-readable supplement manifest schema |
| outline-extension.md | Outline extension contract |
| triage-extension.md | Triage extension contract |
| profile-contract.md | Profile structure contract |

---

## Schemas

| File | Purpose |
|------|---------|
| schemas/domain-manifest-v1.json | JSON Schema for domain manifests |
| schemas/domain-supplements-v1.json | JSON Schema for supplement manifests |

Schema URLs:
- `https://raw.githubusercontent.com/cuioss/cui-llm-rules/main/marketplace/bundles/plan-marshall/skills/domain-extension-api/schemas/domain-manifest-v1.json`
- `https://raw.githubusercontent.com/cuioss/cui-llm-rules/main/marketplace/bundles/plan-marshall/skills/domain-extension-api/schemas/domain-supplements-v1.json`

---

## References

| Document | Purpose |
|----------|---------|
| references/architecture.md | Architecture overview and design principles |

---

## Error Handling

Standard error conditions:

```toon
status: error
error: Bundle not found: pm-dev-unknown
```

```toon
status: error
error: No plan-marshall-plugin skill found in bundle: pm-dev-java
```

```toon
status: error
error: Invalid schema version: v99 (supported: v1)
```
