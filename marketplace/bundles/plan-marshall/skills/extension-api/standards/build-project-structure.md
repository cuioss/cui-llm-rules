# Project Structure Discovery API

Specification for project structure discovery in domain extensions.

## Purpose

Domain bundles that provide build capabilities expose a **unified discovery API** that:
- Discovers all project modules with complete metadata
- Extracts dependencies, packages, and source structure
- Detects hybrid modules (e.g., Maven+npm in same directory)
- Returns structured data for project analysis

## Discovery Contract

### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `project_root` | string | Yes | Absolute path to project root directory |

### Output (Per Extension)

Each extension returns modules it discovered with `technology` field:

```json
{
  "name": "oauth-sheriff-core",
  "technology": "maven",
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
    "parent": "de.cuioss.sheriff.oauth:oauth-sheriff"
  },
  "packages": {
    "de.cuioss.sheriff.oauth.core": {
      "path": "oauth-sheriff-core/src/main/java/de/cuioss/sheriff/oauth/core",
      "package_info": "oauth-sheriff-core/src/main/java/de/cuioss/sheriff/oauth/core/package-info.java"
    },
    "de.cuioss.sheriff.oauth.core.util": {
      "path": "oauth-sheriff-core/src/main/java/de/cuioss/sheriff/oauth/core/util"
    }
  },
  "dependencies": [
    "de.cuioss:cui-java-tools:compile",
    "org.projectlombok:lombok:compile",
    "org.junit.jupiter:junit-jupiter:test"
  ],
  "stats": {
    "source_files": 45,
    "test_files": 38
  }
}
```

### Output (Aggregated by Orchestrator)

For hybrid modules, the orchestrator merges results and uses `build_systems` array:

```json
{
  "name": "nifi-cuioss-ui",
  "build_systems": ["maven", "npm"],
  "paths": {
    "module": "nifi-cuioss-ui",
    "descriptors": ["nifi-cuioss-ui/pom.xml", "nifi-cuioss-ui/package.json"],
    "sources": ["nifi-cuioss-ui/src/main/java", "nifi-cuioss-ui/src/main/resources/dev-ui"],
    "tests": ["nifi-cuioss-ui/src/test/java"],
    "readme": "nifi-cuioss-ui/README.adoc"
  },
  "metadata": {
    "artifact_id": "nifi-cuioss-ui",
    "group_id": "de.cuioss.nifi",
    "packaging": "jar",
    "description": "NiFi UI components"
  },
  "packages": {
    "de.cuioss.nifi.ui": {
      "path": "nifi-cuioss-ui/src/main/java/de/cuioss/nifi/ui"
    }
  },
  "dependencies": [
    "de.cuioss:cui-java-tools:compile",
    "npm:lit:^3.0.0:compile"
  ],
  "stats": {
    "source_files": 24,
    "test_files": 12
  }
}
```

**Key distinction:**
- `technology` - single value, per extension result
- `build_systems` - aggregated list, created by orchestrator from multiple extensions

**Field types**:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Module name |
| `technology` | string | Build system (per-extension) |
| `build_systems` | string[] | Build systems (aggregated) |
| `paths.module` | string | Relative path from project root |
| `paths.descriptor` | string | Path to descriptor (per-extension) |
| `paths.descriptors` | string[] | Paths to descriptors (aggregated) |
| `paths.sources` | string[] | Source directories |
| `paths.tests` | string[] | Test directories |
| `paths.readme` | string | Path to README if exists |
| `metadata.*` | string \| null | Extracted metadata (snake_case) |
| `packages` | object | Package name → {path, package_info?} |
| `dependencies` | string[] | `groupId:artifactId:scope` |
| `stats` | object | `{source_files, test_files}` |

## Module Types

| Type | Build System | Indicators |
|------|--------------|------------|
| `jar` | Maven/Gradle | `<packaging>jar</packaging>` or default |
| `war` | Maven/Gradle | `<packaging>war</packaging>` |
| `pom` | Maven | `<packaging>pom</packaging>` (parent/BOM) |
| `quarkus` | Maven/Gradle | Quarkus dependencies present |
| `npm` | npm | `package.json` present |

## Hybrid Module Detection

Modules may use multiple build systems simultaneously (e.g., Maven for backend, npm for frontend in same directory).

**Detection**: A module is hybrid when multiple descriptor files exist:
- `pom.xml` + `package.json` → Maven + npm hybrid
- `build.gradle` + `package.json` → Gradle + npm hybrid

**Merging**: See [orchestrator-integration.md](../../analyze-project-architecture/standards/orchestrator-integration.md) for merge rules.

## Extension Implementation

Extensions implement `discover_modules()` in their `extension.py`:

```python
from extension_base import ExtensionBase

class Extension(ExtensionBase):
    def discover_modules(self, project_root: str) -> list:
        """Discover all modules with complete metadata."""
        modules = []

        # Parse build descriptor (pom.xml, package.json, etc.)
        # Extract metadata, dependencies, packages
        # Detect source/test directories
        # Count files, check for readme

        return modules
```

### Build-System-Specific Discovery

| Build System | Descriptor | Metadata Source | Dependency Source |
|--------------|------------|-----------------|-------------------|
| Maven | `pom.xml` | `<name>`, `<description>`, `<groupId>`, `<artifactId>` | `<dependencies>` |
| Gradle | `build.gradle` | `description`, `group`, `version` | External execution required |
| npm | `package.json` | `name`, `description`, `version` | `dependencies`, `devDependencies` |

**Dependency format**: `groupId:artifactId:scope`
- Maven: `org.projectlombok:lombok:compile`
- npm: `npm:lit:^3.0.0:compile` (prefixed with `npm:`)

### Package Discovery

**Java packages** (object keyed by package name):
```json
"packages": {
  "de.cuioss.tools": {
    "path": "core/src/main/java/de/cuioss/tools",
    "package_info": "core/src/main/java/de/cuioss/tools/package-info.java"
  },
  "de.cuioss.tools.util": {
    "path": "core/src/main/java/de/cuioss/tools/util"
  }
}
```
- Include `package_info` path if `package-info.java` exists, omit otherwise
- All paths are project-relative

**npm packages** (directory-based or exports-defined):
```json
"packages": {
  "components": {
    "path": "my-lib/src/components"
  },
  "hooks": {
    "path": "my-lib/src/hooks"
  },
  "utils": {
    "path": "my-lib/src/utils",
    "exports": "./utils"
  }
}
```
- Discover from `package.json` [subpath exports](https://nodejs.org/api/packages.html) field
- Fall back to top-level directories under `src/` or `lib/`
- Include `exports` path if defined in package.json exports field
- All paths are project-relative

## Orchestrator Integration

The `project-structure` skill orchestrates discovery across all extensions, merges hybrid modules, and persists results.

See [orchestrator-integration.md](../../analyze-project-architecture/standards/orchestrator-integration.md) for:
- Orchestrator flow and extension discovery
- Hybrid module merging algorithm
- Output location (`.plan/raw-project-data.json`)
- CLI interface

## Compliance

Extensions providing module discovery must:

- [ ] Implement `discover_modules()` returning list of module dicts
- [ ] Return empty list (not None) when no modules found
- [ ] Use `technology` field (single value per extension)
- [ ] Use `paths` object with `module`, `descriptor`, `sources`, `tests`, `readme`
- [ ] Use snake_case for metadata fields (`artifact_id`, `group_id`)
- [ ] Use `packages` as object keyed by package name
- [ ] Use dependency format `groupId:artifactId:scope`
- [ ] All paths project-relative (not absolute)

## Known Limitations

1. **Nested modules**: Deeply nested modules (e.g., `parent/child/grandchild`) require recursive discovery
2. **Gradle dependencies**: Require Gradle execution (not parsed from `build.gradle`)
3. **Dynamic configuration**: Build-time-only values not discoverable from static analysis

## Related Specifications

- [orchestrator-integration.md](../../analyze-project-architecture/standards/orchestrator-integration.md) - Orchestrator flow and merging
- [extension-contract.md](extension-contract.md) - Extension API contract
- [build-execution.md](build-execution.md) - Build command execution
- [canonical-commands.md](canonical-commands.md) - Command vocabulary
