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

## Command Resolution Logic

Extensions resolve which commands to include based on module characteristics. This section defines the resolution rules.

### Resolution Categories

Commands fall into three categories based on when they are included:

| Category | Commands | Condition |
|----------|----------|-----------|
| **Always** | `verify`, `install`, `quality-gate`, `package` | All modules (except pom-only modules get subset) |
| **Source-conditional** | `compile` | Only if `paths.sources` is non-empty |
| **Test-conditional** | `test-compile`, `module-tests` | Only if `paths.tests` is non-empty |
| **Profile-based** | `integration-tests`, `coverage`, `benchmark` | Only if corresponding profile detected |

### Resolution Rules

#### 1. Always-Available Commands

All modules receive these commands:
- `verify` - Full verification (compile + test + quality)
- `install` - Install to local repository
- `quality-gate` - Static analysis and linting
- `package` - Create deployable artifact

**Profile enhancement**: If a profile maps to a canonical command, enhance that command:
```
quality-gate + pre-commit profile → "clean verify -Ppre-commit"
verify + integration-tests profile → "clean verify -Pintegration-tests"
```

#### 2. Source-Conditional Commands

Only include if `stats.source_files > 0` or `paths.sources` is non-empty:
- `compile` - Compile production sources

#### 3. Test-Conditional Commands

Only include if `stats.test_files > 0` or `paths.tests` is non-empty:
- `test-compile` - Compile test sources
- `module-tests` - Run unit tests

**Rationale**: Modules without test sources should not have `module-tests` (avoids misleading "no tests to run" results).

#### 4. Profile-Based Commands

Only include if corresponding profile/configuration is detected:
- `integration-tests` - Requires integration test profile
- `coverage` - Requires coverage tooling (JaCoCo, Istanbul, etc.)
- `benchmark` - Requires benchmark configuration (JMH, etc.)

### Aggregator Modules (pom-only)

Modules with `metadata.packaging == "pom"` only receive:
- `quality-gate` - Can still run linting/formatting checks

They do **not** receive: `compile`, `test-compile`, `module-tests`, `verify`, `install`, `package`

### Resolution Flow

```
discover_modules():
    for each module:
        commands = {}

        # 1. Always-available (unless pom)
        if packaging != "pom":
            commands["verify"] = template.verify
            commands["install"] = template.install
            commands["package"] = template.package

        # 2. Always: quality-gate (all modules)
        commands["quality-gate"] = template.quality_gate

        # 3. Source-conditional
        if has_sources(module):
            commands["compile"] = template.compile

        # 4. Test-conditional
        if has_tests(module):
            commands["test-compile"] = template.test_compile
            commands["module-tests"] = template.module_tests

        # 5. Profile-based enhancements
        for profile in detected_profiles:
            canonical = classify_profile(profile.id)
            if canonical == "quality-gate":
                commands["quality-gate"] = enhance_with_profile(...)
            elif canonical in ["integration-tests", "coverage", "benchmark"]:
                commands[canonical] = build_profile_command(...)

        return {... "commands": commands}
```

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

Required commands depend on module type and content:

| Module Type | Required Commands |
|-------------|-------------------|
| **Standard module** (jar, war, etc.) | `quality-gate`, `verify` |
| **Standard module with tests** | `quality-gate`, `verify`, `module-tests` |
| **Aggregator module** (pom) | `quality-gate` only |

**Validation rules**:
- `quality-gate` - Required for all modules
- `verify` - Required for non-pom modules
- `module-tests` - Required only if `stats.test_files > 0`

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
