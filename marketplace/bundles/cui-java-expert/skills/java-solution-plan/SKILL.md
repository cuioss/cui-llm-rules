---
name: java-solution-plan
description: Analyze Java codebase and decompose request into goals
allowed-tools: Read, Glob, Grep, Bash
---

# Java Goals Skill

**Role**: Domain analysis skill for Java implementation tasks. Transforms the request into a solution document by analyzing the codebase.

**Key Pattern**: Single solution document - goals are consolidated into `solution_outline.md` via `manage-plan-documents` skill.

## Operation: decompose

**Input**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |

**Process**:

### Step 0: Load Solution Outline Skill

Load the solution outline skill for structure and examples:

```
Skill: planning:manage-solution-outline
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
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  request read \
  --plan-id {plan_id}

# Read plan configuration
python3 .plan/execute-script.py planning:manage-config:manage-config read \
  --plan-id {plan_id}

# Read references (issue context if available)
python3 .plan/execute-script.py planning:manage-references:manage-references read \
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

Create a single solution document containing all goals. Each goal should be:
- **Independent**: Can be implemented without other goals completing first (when possible)
- **Testable**: Has clear completion criteria
- **Sized**: Reasonable scope (not too large, not too small)

Build a goals markdown section with numbered goals:

```markdown
### 1. {Goal Title}

{Java-specific technical goal description}

**Component**: {class|interface|module|config}
**Path**: `src/main/java/de/cuioss/...`
**Module**: {module name for multi-module projects}
**Dependencies**: {dependencies and integration points}
**Test Path**: `src/test/java/...`
**Standards**: {CDI, logging, etc.}

**Success Criteria:**
- {criterion 1}
- {criterion 2}

### 2. {Next Goal Title}
...
```

Write the solution document directly using Claude Code's Write tool to: `.plan/plans/{plan_id}/solution_outline.md`

Then validate the structure:

```bash
python3 .plan/execute-script.py planning:manage-plan-documents:manage-plan-document \
  solution validate \
  --plan-id {plan_id}
```

**Why direct Write?** Solution outlines contain ASCII diagrams and rich content that don't fit CLI parameter passing. The agent generates the full markdown document and writes it directly.

### Step 4: Record Issues as Lessons

On unexpected codebase state or ambiguity:

```bash
python3 .plan/execute-script.py planning:manage-lessons:manage-lesson add \
  --component-type skill \
  --component-name java-solution-plan \
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

goals_count: {number of goals in solution document}
lessons_recorded: {count}
```

---

## Goal Decomposition Patterns

| Request Pattern | Typical Goals |
|-----------------|---------------|
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
- Reference `cui-java-expert:cui-java-core` standards

### CDI Analysis
When task involves CDI:
- Check `beans.xml` configuration
- Identify scope annotations
- Reference `cui-java-expert:cui-java-cdi` standards

### Testing Analysis
When task involves testing:
- Check for `@EnabledIfReachable` patterns
- Identify generator requirements
- Reference `cui-java-expert:cui-java-unit-testing` standards

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

**Caller**: `cui-java-expert:java-solution-plan-agent`

**Scripts Used**:
- `planning:manage-plan-documents` - Create solution document
- `planning:manage-lessons` - Record lessons on issues

**Standards Referenced**:
- `cui-java-expert:cui-java-core` - Core Java patterns
- `cui-java-expert:cui-java-cdi` - CDI/Quarkus patterns
- `cui-java-expert:cui-java-unit-testing` - Testing standards
