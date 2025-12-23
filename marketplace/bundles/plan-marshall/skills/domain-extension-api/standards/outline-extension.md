# Outline Extension Contract

Contract for domain-specific outline extension skills.

## Purpose

Outline extensions provide domain-specific guidance during solution outline generation. They help Claude understand how to structure deliverables for a specific technology domain.

## Registration

Register an outline extension in the domain manifest:

```json
{
  "extensions": {
    "outline": "pm-dev-java:java-outline-ext"
  }
}
```

## Required Structure

### Frontmatter

The extension skill MUST include:

```yaml
---
name: {domain}-outline-ext
description: Outline extension for {Domain} deliverables
implements: plan-marshall:domain-extension-api/outline-extension
---
```

### Required Sections

| Section | Required | Purpose |
|---------|----------|---------|
| `## Deliverable Patterns` | Yes | How to structure deliverables |
| `## Domain Detection` | No | How to detect domain relevance |
| `## Codebase Analysis` | No | Domain-specific analysis guidance |

## Section Content

### Deliverable Patterns (Required)

Describe how deliverables should be structured for this domain:

```markdown
## Deliverable Patterns

### Component Deliverables
For new components (services, controllers, utilities):
- One deliverable per component
- Include interface + implementation if applicable
- Group related tests with implementation

### Refactoring Deliverables
For refactoring tasks:
- One deliverable per refactoring type
- Include all affected files in scope
- Consider backward compatibility
```

### Domain Detection (Optional)

Describe how to detect when this domain applies:

```markdown
## Domain Detection

This domain applies when:
- Project contains `pom.xml` or `build.gradle`
- Source files have `.java` extension
- Package structure follows Java conventions
```

### Codebase Analysis (Optional)

Describe domain-specific analysis techniques:

```markdown
## Codebase Analysis

When analyzing Java codebases:
- Identify framework (Spring, Quarkus, Jakarta EE)
- Check dependency injection patterns
- Analyze test framework (JUnit 5, TestNG)
- Review build system configuration
```

## Validation

Validation checks:

1. **Frontmatter**: `implements` field references this contract
2. **Required section**: `## Deliverable Patterns` exists
3. **Section content**: Required section is not empty

## Example

```markdown
---
name: java-outline-ext
description: Outline extension for Java deliverables
implements: plan-marshall:domain-extension-api/outline-extension
---

# Java Outline Extension

## Deliverable Patterns

### Service Components
- Service interface + implementation as single deliverable
- Include unit tests for the service
- Consider integration tests separately

### Entity/Model Deliverables
- Entity class + repository as single deliverable
- Include validation annotations
- Group related DTOs

## Domain Detection

Applies when:
- `pom.xml` or `build.gradle` present
- `.java` files in `src/main/java`

## Codebase Analysis

Check for:
- Framework: Look for `@SpringBootApplication`, `@QuarkusMain`
- DI: Constructor injection vs field injection
- Testing: JUnit 5 annotations
```

## Integration

During solution outline generation:

1. Load domain outline extension if configured
2. Apply deliverable patterns when structuring work
3. Use domain detection to confirm applicability
4. Apply codebase analysis guidance
