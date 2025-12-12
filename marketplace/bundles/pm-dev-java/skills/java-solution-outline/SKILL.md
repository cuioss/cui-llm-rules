---
name: java-solution-outline
description: Analyze Java codebase and create solution outline with deliverables
allowed-tools: Read, Glob, Grep, Bash
---

# Java Solution Outline Skill

**Role**: Domain analysis skill for Java implementation tasks. Transforms the request into a solution document by analyzing the codebase.

**Key Pattern**: Single solution document - deliverables are consolidated into `solution_outline.md` via `manage-solution-outline` skill.

## Operation: decompose

**Input**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |

**Process**:

### Step 0: Load Solution Outline Skill

Load the solution outline skill for structure and examples:

```
Skill: pm-workflow:manage-solution-outline
```

This provides:
- Required document structure (Summary, Overview, Deliverables)
- ASCII diagram patterns for Java features
- Deliverable reference format
- Realistic examples

### Step 1: Load Request Context

Load plan context via manage-* scripts:

```bash
# Read original request description
python3 .plan/execute-script.py pm-workflow:manage-plan-documents:manage-plan-document \
  request read \
  --plan-id {plan_id}

# Read plan configuration
python3 .plan/execute-script.py pm-workflow:manage-config:manage-config read \
  --plan-id {plan_id}

# Read references (issue context if available)
python3 .plan/execute-script.py pm-workflow:manage-references:manage-references read \
  --plan-id {plan_id}
```

Parse the request to identify what needs to be accomplished.

### Step 2: Analyze Codebase

Parse request intent and explore affected Java components:

**Project Structure Detection**:
```bash
Glob **/pom.xml              # Maven multi-module
Glob **/build.gradle*        # Gradle
Glob settings.gradle*        # Gradle settings
```

**Component Exploration**:
```bash
Grep "class {ClassName}" --type java
Grep "interface {InterfaceName}" --type java
Glob src/main/java/**/*.java
Read {java-file-path}
```

**Identify**:
- Classes, interfaces, modules affected
- Package structure and placement
- Dependencies (CDI, external libs)
- Test requirements
- Complexity assessment

### Step 3: Create Solution Document

Create a single solution document containing all deliverables. Each deliverable should be:
- **Independent**: Can be implemented without other deliverables completing first (when possible)
- **Testable**: Has clear completion criteria
- **Sized**: Reasonable scope (not too large, not too small)

Build a deliverables markdown section with numbered deliverables and required metadata:

```markdown
### 1. {Deliverable Title}

**Metadata:**
- change_type: {create|modify|refactor}
- execution_mode: automated
- domain: {java|java-testing}
- suggested_skill: pm-dev-java:{java-implement|java-refactor|java-implement-tests}
- suggested_workflow: {implement|refactor|implement-tests}
- context_skills: []
- depends: none

{Java-specific technical deliverable description}

**Component**: {class|interface|module|config}
**Path**: `src/main/java/de/cuioss/...`
**Module**: {module name for multi-module projects}
**Dependencies**: {dependencies and integration points}
**Test Path**: `src/test/java/...`
**Standards**: {CDI, logging, etc.}

**Verification:**
- Command: `mvn test -pl {module}`
- Criteria: Build and tests pass

**Success Criteria:**
- {criterion 1}
- {criterion 2}

### 2. {Next Deliverable Title}
...
```

Write and validate the solution document using heredoc:

```bash
python3 .plan/execute-script.py pm-workflow:manage-solution-outline:manage-solution-outline \
  write \
  --plan-id {plan_id} \
  --validate <<'EOF'
# Solution Outline

## Summary
{one-line summary}

## Overview
{ASCII diagram showing component relationships}

## Deliverables

### 1. {Deliverable Title}
{content}
EOF
```

**Why heredoc?** Solution outlines contain ASCII diagrams and rich content that don't fit CLI parameter passing. The `--validate` flag is REQUIRED - it ensures structure validation on every write.

### Step 4: Record Issues as Lessons

On unexpected codebase state or ambiguity:

```bash
python3 .plan/execute-script.py plan-marshall:lessons-learned:manage-lesson add \
  --component-type skill \
  --component-name java-solution-outline \
  --category observation \
  --title "{issue summary}" \
  --detail "{context and resolution approach}"
```

### Step 5: Return Results

**Output**:
```toon
status: success
plan_id: {plan_id}
solution_created: true

deliverables_count: {number of deliverables in solution document}
lessons_recorded: {count}
```

---

## Skill and Workflow Mapping

When creating deliverables, use this mapping for `suggested_skill` and `suggested_workflow`:

| Change Type | Component Type | Skill | Workflow |
|-------------|----------------|-------|----------|
| create | class/interface | pm-dev-java:java-implement | implement |
| create | test | pm-dev-java:java-implement-tests | implement-tests |
| modify | any | pm-dev-java:java-implement | implement |
| refactor | any | pm-dev-java:java-refactor | refactor |
| fix | build error | pm-dev-java:java-fix-build | fix-build |
| fix | test failure | pm-dev-java:java-fix-tests | fix-tests |

### Domain Selection

| Content Type | Domain |
|--------------|--------|
| Production code (`src/main/java`) | `java` |
| Test code (`src/test/java`) | `java-testing` |
| Mixed (prod + tests in same deliverable) | Split into separate deliverables |

### Context Skills Guidance

| Situation | Add to context_skills |
|-----------|----------------------|
| Uses CDI/injection | `pm-dev-java:cui-java-cdi` |
| Quarkus-specific | `pm-dev-java:cui-java-cdi` |
| Complex refactoring | `pm-dev-java:cui-java-maintenance` |

---

## Deliverable Decomposition Patterns

| Request Pattern | Typical Deliverables |
|-----------------|----------------------|
| "Add caching to service" | 1. Add cache dependency 2. Create cache config 3. Add @Cacheable annotations 4. Add cache tests |
| "Implement new endpoint" | 1. Create DTO classes 2. Create controller 3. Add service method 4. Add integration tests |
| "Refactor to interface" | 1. Extract interface 2. Update implementations 3. Update injection points 4. Update tests |

---

## Component Types

| Type | Indicators | Example |
|------|------------|---------|
| `class` | Service, ServiceImpl, Repository, Controller | UserService.java |
| `interface` | Interface definition | AuthenticationProvider.java |
| `module` | pom.xml, build.gradle reference | core-service module |
| `config` | Config, Configuration suffix | CacheConfig.java |
| `package` | Package path mentioned | de.cuioss.service.auth |

---

## Scope Detection

| Indicator | Scope |
|-----------|-------|
| "implement", "add", "create", "new" | create |
| "fix", "update", "modify", "change" | modify |
| "refactor", "reorganize", "migrate" | refactor |

---

## Complexity Assessment

| Factor | Low | Medium | High |
|--------|-----|--------|------|
| Files affected | 1-3 | 4-8 | 9+ |
| Cross-module | No | 1 module | 2+ modules |
| Breaking changes | None | Internal | Public API |
| Dependencies | 0-2 | 3-5 | 6+ |
| Test coverage needed | Unit only | Unit + Integration | Full suite |

---

## Test Requirements

| Component Type | Test Required | Test Type |
|---------------|---------------|-----------|
| Service class | Yes | Unit + Integration |
| Repository | Yes | Integration |
| Controller | Yes | Integration |
| DTO/Model | Conditional | Unit (if logic) |
| Config class | Conditional | Integration |
| Utility class | Yes | Unit |

---

## CUI-Specific Patterns

### Logging Analysis
When task involves logging:
- Check for `CuiLogger` usage
- Identify `LogRecord` requirements
- Reference `pm-dev-java:cui-java-core` standards

### CDI Analysis
When task involves CDI:
- Check `beans.xml` configuration
- Identify scope annotations
- Reference `pm-dev-java:cui-java-cdi` standards

### Testing Analysis
When task involves testing:
- Check for `@EnabledIfReachable` patterns
- Identify generator requirements
- Reference `pm-dev-java:cui-java-unit-testing` standards

---

## Error Handling

### Component Not Found

| Scope | Action |
|-------|--------|
| `create` | Continue (expected - component doesn't exist yet) |
| `modify` | Warn and ask for clarification |
| `refactor` | Error and request correct path |

### Module Not Found

If module doesn't exist in multi-module project:
- Check if task is to create the module
- Otherwise error with suggestion

### Ambiguous Component

If multiple classes match the name:
- List all matches with paths
- Ask user to select correct one

---

## Integration

**Caller**: `pm-dev-java:java-solution-outline-agent`

**Script Notations** (use EXACTLY as shown):
- `pm-workflow:manage-solution-outline:manage-solution-outline` - Write and validate solution document (write --validate, read, list-deliverables)
- `pm-workflow:manage-plan-documents:manage-plan-document` - Request operations (request read)
- `pm-workflow:manage-config:manage-config` - Plan config (read)
- `pm-workflow:manage-references:manage-references` - Plan references (read)
- `plan-marshall:lessons-learned:manage-lesson` - Record lessons on issues (add)

**Standards Referenced**:
- `pm-dev-java:cui-java-core` - Core Java patterns
- `pm-dev-java:cui-java-cdi` - CDI/Quarkus patterns
- `pm-dev-java:cui-java-unit-testing` - Testing standards
