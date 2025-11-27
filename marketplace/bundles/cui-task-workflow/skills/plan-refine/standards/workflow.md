# Plan Refine Workflow

## Phase Overview

The refine phase analyzes requirements and produces detailed implementation tasks:

```
Plan from Init Phase
        │
        ▼
┌─────────────────────────────────────────────────────┐
│ REFINE PHASE                                        │
│                                                     │
│   1. Read context (plan, config, issue)             │
│   2. Analyze requirements → components              │
│   3. Plan implementation tasks                      │
│   4. Identify documentation needs                   │
│   5. Generate implementation-requirements.md        │
│   6. Transition to implement phase                  │
└─────────────────────────────────────────────────────┘
        │
        ▼
    Implement Phase
```

## Operations Summary

| Operation | Description | Output |
|-----------|-------------|--------|
| **analyze** | Break down requirements into components | Component list with relationships |
| **plan-tasks** | Create detailed implementation tasks | Tasks with acceptance criteria |
| **identify-docs** | Determine documentation needs | ADR and interface references |

## Component Analysis

Analyze requirements to identify:
1. Functional components (features, APIs, services)
2. Technical boundaries (modules, packages, layers)
3. Dependencies between components
4. Complexity estimates (low/medium/high)

## Task Planning

For each component:
1. Create implementation task(s)
2. Add technology-specific checklist items
3. Define acceptance criteria from requirements
4. Add standard quality checklist items

Order tasks based on:
- Component dependencies
- Build order requirements
- Test isolation needs

## Technology-Specific Standards

### For Java Tasks

**Standard Checklist Items**:
```markdown
- [ ] Follow CUI Java coding standards
- [ ] Add JavaDoc to public methods
- [ ] Implement unit tests (JUnit 5)
- [ ] Verify build via `maven-builder` agent
- [ ] Check coverage ≥80%
```

**Delegation**: `cui-java-expert:java-implement-agent`

### For JavaScript Tasks

**Standard Checklist Items**:
```markdown
- [ ] Follow CUI JavaScript standards
- [ ] Add JSDoc to exported functions
- [ ] Implement unit tests (Jest)
- [ ] Verify build via `npm-builder` agent
- [ ] Check coverage ≥80%
```

**Delegation**: `cui-frontend-expert`

### For Mixed Tasks

**Standard Checklist Items**:
```markdown
- [ ] Follow technology-appropriate standards
- [ ] Add documentation per language
- [ ] Implement tests for both stacks
- [ ] Run both Maven and npm builds
```

## Documentation Identification

### ADR Triggers
- Architectural decisions (technology choices, patterns)
- Security considerations
- Integration approaches
- Performance trade-offs

### Interface Triggers
- New APIs (REST, GraphQL, etc.)
- Service interfaces
- External integrations
- Contract definitions

## Quality Gates

**Before Implement Phase**:
- [ ] All tasks have clear goals
- [ ] All tasks have acceptance criteria
- [ ] Dependencies correctly mapped
- [ ] Documentation references complete

**Per Task**:
- Test coverage: ≥80%
- Build status: passing
- Documentation: complete
