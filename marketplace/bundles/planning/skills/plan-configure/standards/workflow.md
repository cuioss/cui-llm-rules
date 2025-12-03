# Plan Configure Workflow Standards

Detailed standards for requirements analysis, clarifying questions, and validation.

## Requirements Analysis

### Extraction Guidelines

When analyzing task.md, extract requirements based on:

1. **Explicit Goals**: Direct statements of what needs to be done
2. **Acceptance Criteria**: Any "must", "should", "needs to" statements
3. **Implied Needs**: Supporting functionality needed for main goal
4. **Non-Functional Requirements**: Performance, security, compatibility

### Requirement Quality Criteria

Each requirement must:
- Have a clear, actionable title (verb + noun)
- Include sufficient detail in body for implementation
- Be independently verifiable
- Map to one or few acceptance criteria

**Good**: "Implement user authentication with JWT tokens"
**Bad**: "Make login work"

---

## Clarifying Question Patterns

### When to Ask

Ask questions when:
- Scope cannot be determined from task.md
- Technology stack is ambiguous
- Multiple valid approaches exist
- Breaking changes are possible

### Question Format

Always use options-based questions:

```
AskUserQuestion:
  question: "{clear question}"
  options:
    - label: "{short label}"
      description: "{clarifying details}"
```

### Standard Questions

#### Scope Uncertainty

```
AskUserQuestion:
  question: "What is the scope of this change?"
  options:
    - label: "Small fix"
      description: "Single file or function, minimal risk"
    - label: "Medium change"
      description: "Few related files, moderate testing needed"
    - label: "Large feature"
      description: "Multiple components, comprehensive testing"
```

#### Technology Uncertainty

```
AskUserQuestion:
  question: "What is the primary technology for this task?"
  options:
    - label: "Java"
      description: "Java code with Maven or Gradle build"
    - label: "JavaScript"
      description: "JavaScript/TypeScript with npm"
    - label: "Plugin Development"
      description: "Claude Code plugin (skill, agent, command)"
    - label: "Generic"
      description: "Documentation, config, or mixed"
```

#### Breaking Changes

```
AskUserQuestion:
  question: "Will this introduce breaking changes?"
  options:
    - label: "No - backward compatible"
      description: "Existing behavior preserved"
    - label: "Yes - breaking changes"
      description: "API changes, removed features, or behavioral changes"
```

#### Testing Requirements

```
AskUserQuestion:
  question: "What level of testing is needed?"
  options:
    - label: "Unit tests only"
      description: "Cover new/changed code"
    - label: "Unit + integration"
      description: "Verify component interactions"
    - label: "Full test suite"
      description: "Comprehensive coverage required"
```

---

## Plan Type Detection

### Detection Logic

```
IF task mentions plugin, skill, command, agent:
  plan_type = "plugin-development"

ELIF task mentions Java, Maven, Gradle, pom.xml, .java:
  plan_type = "java"

ELIF task mentions JavaScript, npm, package.json, .js, .ts:
  plan_type = "javascript"

ELIF simple task (docs, config, small fix):
  plan_type = "generic"

ELSE:
  ASK user to choose technology
```

### Technology Indicators

| Plan Type | File Indicators | Keyword Indicators |
|-----------|-----------------|-------------------|
| java | pom.xml, build.gradle, *.java | Maven, Gradle, JUnit, CDI |
| javascript | package.json, *.js, *.ts | npm, Jest, ESLint |
| plugin-development | SKILL.md, plugin.json | skill, agent, command, bundle |
| generic | *.md, *.adoc, config files | documentation, README |

---

## Validation Criteria

### Pre-Configuration Validation

Before creating config:
- [ ] task.md exists and has content
- [ ] At least one requirement created
- [ ] Plan type determined (detected or specified)

### Post-Configuration Validation

After configuration:
- [ ] config.toon created with valid plan_type
- [ ] requirements/ directory exists with at least one REQ file
- [ ] status.toon updated with phase transition

### Requirements Validation

For each requirement:
- [ ] Has non-empty title
- [ ] Has non-empty body
- [ ] Status is "pending"
- [ ] Number is sequential

---

## Error Recovery

### Missing task.md

```toon
status: error
plan_id: {plan_id}
error: missing_task_md
message: task.md not found in plan directory
recovery: Run plan-init-agent first to create task.md
```

### Invalid Plan Type

```toon
status: error
plan_id: {plan_id}
error: invalid_plan_type
message: Plan type '{type}' not recognized
valid_types:
  - java
  - javascript
  - plugin-development
  - generic
```

### Script Failure

On any script failure:
1. Log error context
2. Record lesson-learned
3. Return partial status if possible
4. Suggest recovery action
