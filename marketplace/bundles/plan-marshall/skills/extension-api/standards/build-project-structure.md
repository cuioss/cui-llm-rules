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
    "parent": "de.cuioss.sheriff.oauth:oauth-sheriff",
    "profiles": [
      {"id": "pre-commit", "canonical": "quality-gate", "activation": {"type": "command-line"}},
      {"id": "integration-tests", "canonical": "integration-tests", "activation": {"type": "command-line"}}
    ]
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
  },
  "commands": {
    "module-tests": "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run --targets \"clean test\" --module oauth-sheriff-core",
    "quality-gate": "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run --targets \"clean verify -Ppre-commit\" --module oauth-sheriff-core",
    "verify": "python3 .plan/execute-script.py pm-dev-java:plan-marshall-plugin:maven run --targets \"clean verify\" --module oauth-sheriff-core"
  }
}
```

### Output (Aggregated by Orchestrator)

See [orchestrator-integration.md](../../analyze-project-architecture/standards/orchestrator-integration.md) for:
- Complete aggregated output structure including `commands`
- Hybrid module merging algorithm
- Command resolution flow
- Output location (`.plan/raw-project-data.json`)

**Key distinctions:**
- `technology` - single value, per extension result
- `build_systems` - aggregated list, created by orchestrator from multiple extensions

**Field types (per-extension)**:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Module name |
| `technology` | string | Build system (per-extension) |
| `paths.module` | string | Relative path from project root |
| `paths.descriptor` | string | Path to descriptor |
| `paths.sources` | string[] | Source directories |
| `paths.tests` | string[] | Test directories |
| `paths.readme` | string | Path to README if exists |
| `metadata.*` | string \| null | Extracted metadata (snake_case) |
| `metadata.profiles` | array \| null | Build-system-specific profiles (Maven only) |
| `packages` | object | Package name → {path, package_info?} |
| `dependencies` | string[] | `groupId:artifactId:scope` |
| `stats` | object | `{source_files, test_files}` |
| `commands` | object | Canonical command name → resolved command string |

## Packaging Types

The `metadata.packaging` field stores build-system-specific packaging information:

**Maven/Gradle** (`metadata.packaging`):

| Value | Description |
|-------|-------------|
| `jar` | Standard Java library (default if not specified) |
| `war` | Web application archive |
| `pom` | Parent/BOM module (no compiled code) |

**npm**: No packaging field (npm modules are always packages).

**Framework detection** (e.g., Quarkus) is inferred from dependencies, not stored as packaging type.

## Hybrid Module Detection

Modules may use multiple build systems simultaneously (e.g., Maven for backend, npm for frontend in same directory).

**Detection**: A module is hybrid when multiple descriptor files exist:
- `pom.xml` + `package.json` → Maven + npm hybrid
- `build.gradle` + `package.json` → Gradle + npm hybrid

**Merging**: See [orchestrator-integration.md](../../analyze-project-architecture/standards/orchestrator-integration.md) for merge rules.

## Extension Implementation

Extensions use **build tool commands** to extract information rather than parsing files directly. Let the tool do its job.

### Maven Discovery

```bash
# List all modules
./mvnw -q help:evaluate -Dexpression=project.modules -DforceStdout

# Get module metadata
./mvnw -q help:evaluate -Dexpression=project.artifactId -DforceStdout
./mvnw -q help:evaluate -Dexpression=project.groupId -DforceStdout
./mvnw -q help:evaluate -Dexpression=project.packaging -DforceStdout
./mvnw -q help:evaluate -Dexpression=project.description -DforceStdout

# List dependencies
./mvnw -q dependency:list -DoutputAbsoluteArtifactFilename=false -DincludeScope=compile

# List profiles
./mvnw -q help:all-profiles
```

### Gradle Discovery

```bash
# List all projects
./gradlew projects -q

# Get project properties
./gradlew properties -q --project-dir module-name

# List dependencies
./gradlew dependencies -q --configuration compileClasspath
```

### npm Discovery

```bash
# Get package metadata (reads package.json)
npm pkg get name version description

# List dependencies
npm ls --json --depth=0

# List scripts
npm pkg get scripts
```

### Implementation Pattern

Extensions use `direct_command.execute_direct()` for all command execution, reading output from the log file:

```python
from pathlib import Path
from extension_base import ExtensionBase
from direct_command import execute_direct

class Extension(ExtensionBase):
    def discover_modules(self, project_root: str) -> list:
        """Discover modules using build tool commands."""
        modules = []

        # Run Maven command to list modules
        result = execute_direct(
            args="help:evaluate -Dexpression=project.modules -DforceStdout",
            command_key="maven:discover-modules",
            project_dir=project_root
        )

        if result["status"] == "success":
            # Read output from log file
            log_content = Path(result["log_file"]).read_text()
            module_names = self._parse_module_list(log_content)
            for name in module_names:
                modules.append(self._build_module_dict(name, project_root))

        return modules
```

See [build-execution.md](build-execution.md) for the complete `execute_direct` API.

### Build-System-Specific Discovery

| Build System | Metadata Command | Dependency Command |
|--------------|------------------|-------------------|
| Maven | `mvnw help:evaluate -Dexpression=...` | `mvnw dependency:list` |
| Gradle | `gradlew properties` | `gradlew dependencies` |
| npm | `npm pkg get name description` | `npm ls --json` |

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
- [ ] Include `metadata.profiles` for build-system-specific profiles (Maven)
- [ ] Use `packages` as object keyed by package name
- [ ] Use dependency format `groupId:artifactId:scope`
- [ ] Include `commands` with resolved canonical command strings
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
