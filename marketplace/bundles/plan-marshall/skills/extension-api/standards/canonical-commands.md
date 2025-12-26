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
| `performance` | test | No | Performance/benchmark tests |
| `quality-gate` | quality | **Yes** | Static analysis, linting, formatting checks |
| `verify` | verify | **Yes** | Full verification (compile + test + quality) |
| `install` | deploy | No | Install artifact to local repository |
| `package` | deploy | No | Create deployable artifact |

## Applicability by Module Type

Commands are filtered based on module type:

| Module Type | Applicable Commands |
|-------------|---------------------|
| `jar` | All except install only for library modules |
| `war` | All web application commands |
| `quarkus` | All including native build support |
| `pom` | Only `install`, `quality-gate` |
| `npm` | `module-tests`, `quality-gate`, `verify`, `package`, `lint`, `e2e-tests` |

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

## Required Commands

Testable modules (jar, war, quarkus, npm) **must** have these commands configured:
- `module-tests` - Run unit tests
- `quality-gate` - Run static analysis and linting
- `verify` - Full verification

Use `build_env validate-required --module <name>` to check compliance.

## Phase Descriptions

| Phase | Purpose |
|-------|---------|
| **build** | Compile source code |
| **test** | Execute tests |
| **quality** | Static analysis, formatting |
| **verify** | Complete validation |
| **deploy** | Create/install artifacts |

## Extension-Specific Commands

Extensions may define additional commands beyond the canonical set:

| Extension | Additional Commands |
|-----------|---------------------|
| npm | `lint`, `lint-fix`, `e2e-tests` |

These are not part of the canonical vocabulary but are valid within their build system scope.
