# Layer Definitions

Architectural layer semantics and dependency constraints for project modules.

## Layer Values

| Layer | Description | Typical Modules |
|-------|-------------|-----------------|
| `extension` | Plugin/extension code, core functionality | processors, plugins, extensions |
| `presentation` | UI components, web interfaces | ui, frontend, webapp |
| `service` | Business logic | service, core, domain |
| `api` | Public API definitions | api, client, sdk |
| `packaging` | Build artifacts, assembly | nar, assembly, dist |
| `testing` | Test modules | integration-testing, e2e, test |

## Layer Descriptions

### extension

Core functionality implemented as plugins or extensions.

**Characteristics**:
- Implements framework extension points
- Self-contained functionality
- No direct dependency on presentation
- May depend on api layer

**Examples**:
- NiFi processors
- Quarkus extensions
- Plugin implementations

### presentation

User interface and web components.

**Characteristics**:
- User-facing code
- May depend on extension and service layers
- No testing code dependencies

**Examples**:
- Angular/React components
- Web UI modules
- Frontend applications

### service

Business logic and domain services.

**Characteristics**:
- Core business rules
- Domain-specific logic
- May depend on api layer only

**Examples**:
- Service implementations
- Domain logic modules
- Core business modules

### api

Public API definitions and contracts.

**Characteristics**:
- Interface definitions
- DTOs and contracts
- No implementation details
- Minimal dependencies

**Examples**:
- API modules
- Client libraries
- SDK interfaces

### packaging

Build artifacts and distribution packaging.

**Characteristics**:
- No source code (assembly only)
- Bundles other modules
- Creates deployable artifacts

**Examples**:
- NAR bundles
- Assembly modules
- Distribution packages

### testing

Test modules including integration and end-to-end tests.

**Characteristics**:
- Can depend on any layer
- Not depended on by other layers
- Test-scoped dependencies

**Examples**:
- Integration test modules
- E2E test suites
- Performance test modules

## Default Layer Constraints

```toon
layer_rules:
  presentation:
    allowed:
      - extension
      - service
      - api
    forbidden:
      - testing
      - packaging

  extension:
    allowed:
      - api
      - service
    forbidden:
      - presentation
      - testing

  service:
    allowed:
      - api
    forbidden:
      - presentation
      - testing
      - packaging

  api:
    allowed: []
    forbidden:
      - presentation
      - testing
      - packaging
      - service

  packaging:
    allowed:
      - extension
      - presentation
      - service
    forbidden:
      - testing

  testing:
    allowed:
      - packaging
      - extension
      - presentation
      - service
      - api
    forbidden: []
```

## Layer Inference Rules

When generating structure from marshal.json, layers are inferred from module names:

| Pattern | Inferred Layer |
|---------|----------------|
| `*-ui`, `*-frontend`, `*-web`, `*webapp*` | presentation |
| `*-api` | api |
| `*-service`, `*-core` | service |
| `*test*`, `integration*`, `e2e*`, `e-2-e*` | testing |
| `*-nar`, `*-assembly`, `*-dist`, `*-package` | packaging |
| (default) | extension |

## Constraint Violations

When a dependency violates layer constraints:

1. **Forbidden dependency**: Direct violation of `forbidden` list
   - Example: `extension` depending on `presentation`
   - Action: Refactor to remove dependency

2. **Missing allowed**: Dependency not in `allowed` list
   - May indicate architectural issue
   - Action: Evaluate if constraint should be relaxed

## Customization

Projects may customize layer constraints in `project-structure.toon`:

```toon
dependencies:
  layer_rules:
    extension:
      allowed:
        - api
        - service
        - presentation  # Custom: allow presentation dependency
      forbidden:
        - testing
```

Document the reason for constraint relaxation in module insights.

## Related Documents

- `standards/toon-format.md` - Complete TOON schema
- `standards/placement-patterns.md` - Placement by layer
