# Module Graph Format

Output format for the `architecture graph` command. Returns the complete internal module dependency graph in a single call.

## Purpose

Provides a complete view of internal module dependencies for:
- Ordering deliverables in multi-module tasks
- Identifying dependency chains
- Detecting circular dependencies
- Planning parallel execution

## Output Format (TOON)

```toon
status: success

graph:
  node_count: 4
  edge_count: 3

nodes[4]{name,purpose,layer}:
oauth-sheriff-parent,parent,0
oauth-sheriff-core,library,1
oauth-sheriff-quarkus,extension,2
oauth-sheriff-quarkus-deployment,deployment,2

edges[3]{from,to}:
oauth-sheriff-quarkus,oauth-sheriff-core
oauth-sheriff-quarkus-deployment,oauth-sheriff-core
oauth-sheriff-quarkus-deployment,oauth-sheriff-quarkus

layers[3]{layer,modules}:
0,[oauth-sheriff-parent]
1,[oauth-sheriff-core]
2,[oauth-sheriff-quarkus,oauth-sheriff-quarkus-deployment]

roots[1]:
  - oauth-sheriff-parent
  - oauth-sheriff-core

leaves[2]:
  - oauth-sheriff-quarkus
  - oauth-sheriff-quarkus-deployment
```

## Field Definitions

### Graph Summary

| Field | Type | Description |
|-------|------|-------------|
| `node_count` | int | Total number of modules |
| `edge_count` | int | Total number of dependency edges |

### Nodes Table

| Column | Description |
|--------|-------------|
| `name` | Module name |
| `purpose` | Module purpose (library, extension, deployment, parent, test) |
| `layer` | Topological layer (0 = no dependencies, higher = more dependencies) |

### Edges Table

| Column | Description |
|--------|-------------|
| `from` | Dependent module (has the dependency) |
| `to` | Dependency module (is depended upon) |

Direction: `from` depends on `to` (A→B means A requires B)

### Layers

Modules grouped by topological depth:
- **Layer 0**: Modules with no internal dependencies (roots)
- **Layer N**: Modules that only depend on layers < N

Use layers to determine execution order: execute layer 0 first, then layer 1, etc.

### Roots and Leaves

| Field | Description |
|-------|-------------|
| `roots` | Modules with no internal dependencies (can start immediately) |
| `leaves` | Modules that nothing depends on (end of dependency chains) |

## Use Cases

### Ordering Deliverables

When creating multi-module deliverables, use layer information:

```
Deliverable 1: oauth-sheriff-core (layer 1) - execute first
Deliverable 2: oauth-sheriff-quarkus (layer 2) - depends on 1
Deliverable 3: oauth-sheriff-quarkus-deployment (layer 2) - depends on 1
```

Deliverables in the same layer can execute in parallel if no other dependencies exist.

### Detecting Circular Dependencies

If the graph cannot be layered (topological sort fails):

```toon
status: error
error: circular_dependency
cycle[3]:
  - module-a
  - module-b
  - module-a
message: Circular dependency detected between modules
```

## Empty Graph

For single-module projects or projects with no internal dependencies:

```toon
status: success

graph:
  node_count: 1
  edge_count: 0

nodes[1]{name,purpose,layer}:
my-module,library,0

edges[0]{from,to}:

layers[1]{layer,modules}:
0,[my-module]

roots[1]:
  - my-module

leaves[1]:
  - my-module
```

## Error Handling

### Data Not Found

```toon
status: error
error: data_not_found
path: .plan/project-architecture/derived-data.json
message: Run 'architecture discover' first
```

## Related Documents

- [client-api.md](client-api.md) - Full command reference
- [architecture-persistence.md](architecture-persistence.md) - Data storage schema
