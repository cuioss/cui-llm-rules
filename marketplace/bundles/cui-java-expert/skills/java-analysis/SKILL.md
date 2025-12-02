---
name: java-analysis
description: Analyzes Java implementation tasks to identify components, test requirements, and dependencies. Implements planning:analysis-api contract.
allowed-tools: Read, Glob, Grep, Bash
---

# Java Analysis Skill

**Role**: Domain analysis skill for Java implementation tasks. Analyzes task requirements and codebase to identify Java components (classes, modules, packages) and their dependencies.

**Integration**: Called by `planning:plan-refine` during the refine phase for `implementation` plan types with Java projects.

**API Contract**: Load `planning:analysis-api` for full input/output specification.

```
Skill: planning:analysis-api
```

## Operation: analyze

**Contract**: See `planning:analysis-api` for full input/output specification.

### Domain-Specific Input

| Parameter | Description |
|-----------|-------------|
| `build_system` | Required: `maven` or `gradle` |

### Domain-Specific Output

**Component Types**: `class`, `interface`, `module`, `package`, `config`

**Domain-Specific Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `module` | string | Maven/Gradle module name |
| `test_required` | boolean | Whether unit tests are needed |
| `test_path` | string | Path to test file |

**Example Output**:
```yaml
analysis_result:
  status: "success"
  components:
    - name: "CacheConfig"
      type: "config"
      scope: "create"
      path: "src/main/java/de/cuioss/service/config/CacheConfig.java"
      module: "core-service"
      test_required: true
      test_path: "src/test/java/de/cuioss/service/config/CacheConfigTest.java"
      dependencies:
        - "spring-boot-starter-data-redis"
      complexity: "medium"
      notes: "Redis connection configuration"
```

## Analysis Process

### Step 1: Parse Task Intent

Extract from task description:
- Action verbs: implement, add, create, fix, refactor, update
- Component types: class, interface, service, repository, controller, config
- Target modules: Look for module names, package paths
- Features: Business logic keywords

### Step 2: Detect Project Structure

**Maven Multi-Module**:
```bash
Glob **/pom.xml
```

**Gradle Multi-Module**:
```bash
Glob **/build.gradle*
Glob settings.gradle*
```

**Package Structure**:
```bash
Glob src/main/java/**/*.java
```

### Step 3: Explore Affected Components

For each identified component:

**Classes/Interfaces**:
```bash
Grep "class {ClassName}" --type java
Grep "interface {InterfaceName}" --type java
Read {java-file-path}
```

**Packages**:
```bash
Glob src/main/java/{package-path}/**/*.java
```

**Configuration**:
```bash
Glob **/application.properties
Glob **/application.yml
Glob **/beans.xml
```

### Step 4: Identify Dependencies

For each component, analyze:
- **Import statements**: Direct dependencies
- **CDI injection**: `@Inject`, `@Produces`, `@Observes`
- **Spring annotations**: `@Autowired`, `@Component`, `@Service`
- **Module dependencies**: `pom.xml` or `build.gradle` dependencies
- **Cross-module**: References to other modules

### Step 5: Determine Test Requirements

| Component Type | Test Required | Test Type |
|---------------|---------------|-----------|
| Service class | Yes | Unit + Integration |
| Repository | Yes | Integration |
| Controller | Yes | Integration |
| DTO/Model | Conditional | Unit (if logic) |
| Config class | Conditional | Integration |
| Utility class | Yes | Unit |

### Step 6: Assess Complexity

| Factor | Low | Medium | High |
|--------|-----|--------|------|
| Files affected | 1-3 | 4-8 | 9+ |
| Cross-module | No | 1 module | 2+ modules |
| Breaking changes | None | Internal | Public API |
| Dependencies | 0-2 | 3-5 | 6+ |
| Test coverage needed | Unit only | Unit + Integration | Full suite |

### Step 7: Return Components

Return structured component list with all metadata for plan-type skill to generate tasks.

## Component Type Detection

| Indicator | Type |
|-----------|------|
| Ends with `Service`, `ServiceImpl` | class (service) |
| Ends with `Repository`, `Dao` | class (repository) |
| Ends with `Controller`, `Resource` | class (controller) |
| Ends with `Config`, `Configuration` | config |
| Interface definition | interface |
| Package path mentioned | package |
| `pom.xml`, `build.gradle` reference | module |

## Scope Detection

| Indicator | Scope |
|-----------|-------|
| "implement", "add", "create", "new" | create |
| "fix", "update", "modify", "change" | modify |
| "refactor", "reorganize", "migrate" | refactor |

## Example Analysis

**Task**: "Implement caching for UserService using Redis"

**Analysis Output**:
```yaml
components:
  - name: "CacheConfig"
    type: "config"
    scope: "create"
    module: "core-service"
    path: "src/main/java/de/cuioss/service/config/CacheConfig.java"
    test_required: true
    test_path: "src/test/java/de/cuioss/service/config/CacheConfigTest.java"
    dependencies:
      - "spring-boot-starter-data-redis"
    complexity: "medium"
    notes: "Redis connection configuration"

  - name: "UserService"
    type: "class"
    scope: "modify"
    module: "core-service"
    path: "src/main/java/de/cuioss/service/user/UserService.java"
    test_required: true
    test_path: "src/test/java/de/cuioss/service/user/UserServiceTest.java"
    dependencies:
      - "CacheConfig"
      - "UserRepository"
    complexity: "medium"
    notes: "Add @Cacheable annotations"

  - name: "pom.xml"
    type: "module"
    scope: "modify"
    module: "core-service"
    path: "core-service/pom.xml"
    test_required: false
    test_path: null
    dependencies: []
    complexity: "low"
    notes: "Add Redis dependency"
```

## Integration with Plan-Type Skills

After analysis completes, return components to `plan-refine`, which passes them to:

```
Skill: planning:plan-type-implementation
operation: generate-tasks
plan_id: {plan_id}
components: {components from analysis}
```

The plan-type skill then generates appropriate tasks (implement, test, verify) and writes them directly to plan.md.

## CUI-Specific Patterns

### Logging Analysis
When task involves logging:
- Check for `CuiLogger` usage
- Identify `LogRecord` requirements
- Flag for `cui-java-expert:cui-java-core` standards

### CDI Analysis
When task involves CDI:
- Check `beans.xml` configuration
- Identify scope annotations
- Flag for `cui-java-expert:cui-java-cdi` standards

### Testing Analysis
When task involves testing:
- Check for `@EnabledIfReachable` patterns
- Identify generator requirements
- Flag for `cui-java-expert:cui-java-unit-testing` standards

## Error Handling

### Class Not Found
If task references a class that doesn't exist:
- For "create" scope: Continue (expected)
- For "modify" scope: Warn and ask for clarification
- For "refactor" scope: Error and request correct path

### Module Not Found
If module doesn't exist in multi-module project:
- Check if task is to create the module
- Otherwise error with suggestion

### Ambiguous Component
If multiple classes match the name:
- List all matches with paths
- Ask user to select correct one

## Quality Checklist

- [x] Self-contained with relative paths
- [x] Returns structured components[] for plan generation
- [x] Identifies test requirements for each component
- [x] Assesses complexity for task planning
- [x] Handles Maven and Gradle projects
- [x] Respects CUI-specific patterns
