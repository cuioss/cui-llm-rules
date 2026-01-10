# Core Concept: Architecture-Driven Workflow

The solution-outline workflow uses pre-computed architecture data to make intelligent module and package placement decisions.

---

## Architecture-Driven Workflow

```
+-----------------------------------------------------------------------------+
|                          ARCHITECTURE-DRIVEN WORKFLOW                        |
+-----------------------------------------------------------------------------+
|                                                                              |
|  TASK: {task description}                                                   |
|                                                                              |
|  Step 1: Query Architecture                                                 |
|  ════════════════════════════                                               |
|                                                                              |
|  architecture info → Project overview                                       |
|  architecture modules → [{module-1}, {module-2}, ...]                       |
|                                                                              |
|  Step 2: Match Task to Modules                                              |
|  ══════════════════════════════                                             |
|                                                                              |
|  For each module:                                                           |
|    architecture module --name {module}                                      |
|                                                                              |
|  Compare task keywords against:                                             |
|    • responsibility: "{from architecture}" ← MATCH?                         |
|    • key_packages: "{from architecture}" ← MATCH?                           |
|    • purpose: {library|application|extension} ← appropriate?                |
|                                                                              |
|  Result: {selected module} is the target module                             |
|                                                                              |
|  Step 3: Determine Package Placement                                        |
|  ════════════════════════════════════                                       |
|                                                                              |
|  key_packages:                                                              |
|    {package}:                                                               |
|      description: "{from architecture}"                                     |
|      components: [{existing components}]                                    |
|                                                                              |
|  Decision: New {component} goes in {package}                                |
|                                                                              |
|  Step 4: Create Deliverable with Justified Placement                        |
|  ════════════════════════════════════════════════════                       |
|                                                                              |
|  ### {N}. {Deliverable Title}                                               |
|                                                                              |
|  **Module**: {module} ({reasoning})                                         |
|  **Package**: {package}                                                     |
|  **Rationale**: {placement reasoning}                                       |
|                                                                              |
+-----------------------------------------------------------------------------+
```

---

## Key Insight

Module and package matching is **semantic analysis** that requires LLM reasoning. Scripts provide DATA, the LLM provides REASONING.

| Layer | Responsibility |
|-------|----------------|
| **Data Layer** (Scripts) | Structured, queryable module/package information |
| **Reasoning Layer** (LLM) | Semantic matching, selection, justification |

---

## Design Principles

| Principle | Rationale |
|-----------|-----------|
| Scripts provide DATA | Structured, queryable module/package information |
| LLM provides REASONING | Semantic matching, selection, justification |
| Reasoning is documented | Selection rationale captured in deliverables |
| No script-based matching | Task-to-module matching is inherently semantic |
| Simple/Complex split | Reuse simple workflow as building block |
| Decompose before select | Cross-module tasks need structure first |

---

## Benefits

1. **Pre-computed data**: Architecture analysis runs once, reused across multiple tasks
2. **Consistent placement**: Same module/package selection logic for all deliverables
3. **Documented reasoning**: Selection rationale captured in deliverables
4. **Reduced exploration**: No need to re-scan codebase for each task
5. **Skills inheritance**: Skills come from module selection, not runtime resolution

---

## Success Criteria

After implementation:

1. **Workflow selection works correctly**
   - Simple tasks → direct module/package selection
   - Complex tasks → decomposition first, then selection per sub-task

2. **Solution outlines include module context**
   - Every deliverable has module/package with reasoning
   - Placement matches existing patterns in key_packages

3. **Architecture data is used first**
   - Codebase exploration happens AFTER architecture query
   - Module selection reasoning references responsibility/purpose

4. **Cross-module tasks are decomposed correctly**
   - Sub-tasks are module-scoped
   - Dependencies use `internal_dependencies` data
   - `depends` field reflects actual module dependencies

5. **Simple workflow is reused**
   - Complex workflow calls simple workflow per sub-task
   - No duplication of module/package selection logic
