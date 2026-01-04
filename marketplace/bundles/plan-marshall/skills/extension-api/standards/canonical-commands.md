# Canonical Command Vocabulary

Defines the standard command names that extensions implement via `get_command_mappings()`.

## Purpose

Canonical commands provide a **build-system-agnostic vocabulary** for common development operations. Extensions map these canonical names to build-system-specific invocations.

## Canonical Commands

| Canonical Name | Phase | Required | Description |
|----------------|-------|----------|-------------|
| `compile` | build | No | Compile production sources only |
| `test-compile` | build | No | Compile production and test sources |
| `module-tests` | test | **Yes** | Unit tests for the module |
| `integration-tests` | test | No | Integration tests (containers, external services) |
| `coverage` | test | No | Test execution with coverage measurement |
| `benchmark` | test | No | Performance/benchmark tests |
| `quality-gate` | quality | **Yes** | Static analysis, linting, formatting checks |
| `verify` | verify | **Yes** | Full verification (compile + test + quality) |
| `install` | deploy | No | Install artifact to local repository |
| `package` | deploy | No | Create deployable artifact |

## Command Applicability

Extensions determine which commands apply based on their own detection logic. The canonical vocabulary defines **what** commands mean, not **when** they apply.

### Applicability Factors

Extensions consider these factors when determining command applicability:

| Factor | Examples | Responsibility |
|--------|----------|----------------|
| **Build system** | Maven, Gradle, npm | Extension detection |
| **Packaging type** | jar, war, pom, bundle | Metadata from `discover_modules()` |
| **Framework** | Quarkus, Spring, React | Extension-specific detection |
| **Project structure** | Has tests, has sources | File system inspection |

### General Guidelines

| Command | Applies When |
|---------|--------------|
| `compile`, `test-compile` | Module has compilable sources |
| `module-tests` | All modules (no-op if no test sources) |
| `integration-tests` | Module has integration test configuration |
| `coverage` | Coverage tooling configured |
| `benchmark` | Benchmark configuration present |
| `quality-gate` | All modules (linting, static analysis) |
| `verify` | All modules |
| `install` | Artifact can be published to local repository |
| `package` | Artifact can be packaged for deployment |

### Extension Implementation

Extensions return resolved `commands` in `discover_modules()`, built from `get_command_mappings()` templates:

```python
def get_command_mappings(self) -> dict:
    # Template mappings with {module} placeholder
    return {
        "maven": {
            CMD_MODULE_TESTS: f'{base} --targets "clean test"{{module}}',
            CMD_VERIFY: f'{base} --targets "clean verify"{{module}}',
            CMD_QUALITY_GATE: f'{base} --targets "clean verify"{{module}}',
        }
    }

def discover_modules(self, project_root: str) -> list:
    # Extensions resolve commands and return them per module
    return [{
        "metadata": {"packaging": "jar", "profiles": [...]},
        "commands": {
            "module-tests": "python3 ... --module my-module",
            "verify": "python3 ... --module my-module",
            "quality-gate": "python3 ... -Ppre-commit --module my-module"
        },
        ...
    }]
```

## Implementation in Extensions

Extensions provide mappings via `get_command_mappings()`:

```python
def get_command_mappings() -> dict:
    """Return canonical -> script invocation template."""
    base = "python3 .plan/execute-script.py bundle:skill:script run"
    return {
        "maven": {
            "module-tests": f'{base} --targets "clean test"{{module}}',
            "quality-gate": f'{base} --targets "clean verify -Ppre-commit"{{module}}',
            "verify": f'{base} --targets "clean verify"{{module}}',
        }
    }
```

### Template Placeholders

| Placeholder | Resolution |
|-------------|------------|
| `{module}` | Replaced with ` --module <name>` or empty string |

**Note**: The replacement includes a leading space to maintain proper command syntax. Templates like `"clean test"{module}` produce `clean test --module foo` (with space) or `clean test` (no trailing space).

## Required Commands

Modules with source code **must** have these commands configured:
- `module-tests` - Run unit tests
- `quality-gate` - Run static analysis and linting
- `verify` - Full verification

All three are required regardless of whether test sources exist. If a module has no tests, `module-tests` executes as a no-op (succeeds immediately).

Parent/aggregator modules (packaging=pom) only require `quality-gate`.

The orchestrator validates that required commands exist in the `commands` field returned by `discover_modules()`.

## Phase Descriptions

| Phase | Purpose |
|-------|---------|
| **build** | Compile source code |
| **test** | Execute tests |
| **quality** | Static analysis, formatting |
| **verify** | Complete validation |
| **deploy** | Create/install artifacts |

## Extension-Specific Commands

Extensions may define additional commands beyond the canonical set. These are valid within their build system scope but are not part of the canonical vocabulary.

Extensions document their additional commands in their own skill documentation.

## Related Specifications

- [extension-contract.md](extension-contract.md) - Extension API contract
- [build-execution.md](build-execution.md) - Build command execution
- [build-project-structure.md](build-project-structure.md) - Module discovery and metadata
