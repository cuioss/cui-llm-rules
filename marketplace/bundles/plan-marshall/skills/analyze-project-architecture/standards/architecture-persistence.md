# Architecture Persistence

Storage format for project architecture data with separation of raw and derived data.

## Storage

**Location**: `.plan/project-architecture/`

```
.plan/project-architecture/
├── derived-data.json  # Extension API output (deterministic)
└── llm-enriched.json  # LLM-enriched fields
```

**Benefits of separation:**
- Raw data regenerated independently (re-run discovery)
- Derived data updated without expensive re-discovery
- Clear provenance (tooling vs LLM analysis)
- No field duplication

## derived-data.json

Direct output from `discover_project_modules()`. See [build-project-structure.md](../../extension-api/standards/build-project-structure.md) for full specification.

### Structure

```json
{
  "project": {
    "name": "oauth-sheriff",
    "root": "/Users/dev/oauth-sheriff"
  },
  "modules": {
    "oauth-sheriff-core": {
      "name": "oauth-sheriff-core",
      "build_systems": ["maven"],
      "paths": {
        "module": "oauth-sheriff-core",
        "descriptor": "oauth-sheriff-core/pom.xml",
        "sources": ["oauth-sheriff-core/src/main/java"],
        "tests": ["oauth-sheriff-core/src/test/java"],
        "readme": "oauth-sheriff-core/README.adoc"
      },
      "metadata": {
        "artifact_id": "oauth-sheriff-core",
        "group_id": "de.cuioss.sheriff.oauth",
        "packaging": "jar",
        "description": "Core OAuth Sheriff functionality",
        "profiles": [...]
      },
      "packages": {
        "de.cuioss.sheriff.oauth.core": {
          "path": "...",
          "package_info": "..."
        }
      },
      "dependencies": ["de.cuioss:cui-java-tools:compile", ...],
      "stats": {"source_files": 45, "test_files": 38},
      "commands": {
        "module-tests": "python3 ...",
        "verify": "python3 ...",
        "quality-gate": "python3 ..."
      }
    }
  }
}
```

### Fields

| Field | Description |
|-------|-------------|
| `name` | Module name |
| `build_systems` | Array of build systems (e.g., `["maven"]`, `["maven", "npm"]`) |
| `paths` | Module paths (descriptor, sources, tests, readme) |
| `metadata` | Build-system specific metadata |
| `packages` | All packages with paths and package-info |
| `dependencies` | Full dependency list with scopes |
| `stats` | File counts |
| `commands` | Available build commands |

---

## llm-enriched.json

LLM-generated enrichments referencing modules by name.

### Structure

```json
{
  "project": {
    "description": "JWT validation library for Quarkus applications",
    "description_reasoning": "Derived from: root README.md first paragraph"
  },
  "modules": {
    "oauth-sheriff-core": {
      "responsibility": "Core JWT validation logic including claim extraction and signature verification",
      "responsibility_reasoning": "Derived from: README overview, ClaimValidator pattern",
      "purpose": "library",
      "purpose_reasoning": "packaging=jar, no runtime dependencies",
      "key_packages": {
        "de.cuioss.sheriff.oauth.core.pipeline": {
          "description": "JWT validation pipeline components",
          "components": ["ClaimValidator", "JwtPipeline", "ValidationResult"]
        }
      },
      "internal_dependencies": [],
      "key_dependencies": [
        "de.cuioss:cui-java-tools",
        "org.projectlombok:lombok"
      ],
      "key_dependencies_reasoning": "Core utilities and compile-time tooling",
      "proposed_skill_domains": [
        "pm-dev-java:java-core",
        "pm-dev-java:junit-core",
        "pm-dev-java:javadoc"
      ],
      "proposed_skill_domains_reasoning": "Plain Java library, no CDI/Quarkus runtime"
    }
  }
}
```

### Fields

| Field | Description |
|-------|-------------|
| `responsibility` | Human-readable module description (1-2 sentences) |
| `responsibility_reasoning` | Sources used for derivation |
| `purpose` | Module classification (see values below) |
| `purpose_reasoning` | Analysis rationale |
| `key_packages` | Important packages with descriptions and components |
| `internal_dependencies` | Dependencies on other project modules |
| `key_dependencies` | Important external dependencies |
| `key_dependencies_reasoning` | Filtering rationale |
| `proposed_skill_domains` | Applicable skill domains from configured set |
| `proposed_skill_domains_reasoning` | Selection rationale |

### Skill Domain Selection

The `proposed_skill_domains` field selects from configured skill domains based on:

| Signal | Skill Domain |
|--------|--------------|
| Quarkus dependencies | `pm-dev-java:java-cdi-quarkus` |
| CDI annotations | `pm-dev-java:java-cdi` |
| HTTP client usage | `pm-dev-java-cui:cui-testing-http` |
| npm build system | `pm-dev-frontend:cui-javascript` |
| Plain Java (no framework) | `pm-dev-java:java-core`, `pm-dev-java:junit-core` |

Only skills from configured domains are proposed. Query available domains via:
```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config skill-domains list
```

### Purpose Values

| Value | Description |
|-------|-------------|
| `library` | Reusable code, no runtime |
| `extension` | Framework plugin (Quarkus, NiFi) |
| `deployment` | Build-time processing |
| `runtime` | Application entry point |
| `parent` | Aggregator POM (packaging=pom at root) |
| `bom` | Bill of Materials |
| `integration-tests` | Integration test module |
| `benchmark` | Performance testing |

---

## Client API Mapping

The [client-api.md](client-api.md) merges both files for output:

| API Output | derived-data.json | llm-enriched.json |
|------------|-------------------|-------------------|
| `module` (default) | paths, commands | responsibility, purpose, key_packages, internal_dependencies, key_dependencies, proposed_skill_domains |
| `module --full` | + packages, dependencies | + reasoning fields |
| `info` | project.name, project.root | project.description |

---

## Field Summary

| Field | Source | Default Output | Full Output |
|-------|--------|----------------|-------------|
| `name` | derived | Yes | Yes |
| `build_systems` | derived | Yes | Yes |
| `paths` | derived | Yes | Yes |
| `metadata` | derived | Yes | Yes |
| `packages` | derived | No | Yes |
| `dependencies` | derived | No | Yes |
| `stats` | derived | Yes | Yes |
| `commands` | derived | Yes | Yes |
| `responsibility` | llm-enriched | Yes | Yes |
| `responsibility_reasoning` | llm-enriched | No | Yes |
| `purpose` | llm-enriched | Yes | Yes |
| `purpose_reasoning` | llm-enriched | No | Yes |
| `key_packages` | llm-enriched | Yes | Yes |
| `internal_dependencies` | llm-enriched | Yes | Yes |
| `key_dependencies` | llm-enriched | Yes | Yes |
| `key_dependencies_reasoning` | llm-enriched | No | Yes |
| `proposed_skill_domains` | llm-enriched | Yes | Yes |
| `proposed_skill_domains_reasoning` | llm-enriched | No | Yes |

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [build-project-structure.md](../../extension-api/standards/build-project-structure.md) | Raw data field specification |
| [client-api.md](client-api.md) | API for reading merged data |
| [client-view.md](client-view.md) | What consumers need |
