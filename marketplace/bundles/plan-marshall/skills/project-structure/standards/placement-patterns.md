# Placement Patterns

Guidance for defining and using component placement rules.

## Purpose

Placement rules define where new components should be created:
- Target module
- Package location
- File naming pattern
- Test file pattern

## Rule Structure

```toon
placement:
  component-type:
    module: target-module
    package: com.example.{feature}
    pattern: {Name}Component.java
    test_pattern: {Name}ComponentTest.java
    example: ExampleComponent.java
```

## Placeholder Conventions

### {feature}

Lowercase feature or subdomain name.

**Usage**: Package organization
**Examples**: `oauth`, `validation`, `transform`

**Applied**:
```
package: com.example.processors.{feature}
→ com.example.processors.oauth
```

### {Name}

PascalCase component name.

**Usage**: Class and file names
**Examples**: `OAuthToken`, `UserValidator`, `DataTransform`

**Applied**:
```
pattern: {Name}Processor.java
→ OAuthTokenProcessor.java
```

### {name}

camelCase or kebab-case name (context-dependent).

**Usage**: Test files, script names
**Examples**: `oauthToken`, `user-validator`

**Applied**:
```
pattern: {name}.spec.ts
→ oauth-token.spec.ts
```

## Common Patterns by Domain

### Java Patterns

```toon
placement:
  processor:
    module: my-processors
    package: com.example.processors.{feature}
    pattern: "{Name}Processor.java"
    test_pattern: "{Name}ProcessorTest.java"

  service:
    module: my-services
    package: com.example.services.{feature}
    pattern: "{Name}Service.java"
    test_pattern: "{Name}ServiceTest.java"

  controller:
    module: my-api
    package: com.example.api.{feature}
    pattern: "{Name}Controller.java"
    test_pattern: "{Name}ControllerTest.java"

  dto:
    module: my-api
    package: com.example.api.{feature}.dto
    pattern: "{Name}Dto.java"
```

### JavaScript Patterns

```toon
placement:
  component:
    module: frontend
    package: src/components/{feature}
    pattern: "{Name}.jsx"
    test_pattern: "{Name}.test.jsx"

  hook:
    module: frontend
    package: src/hooks
    pattern: "use{Name}.js"
    test_pattern: "use{Name}.test.js"

  service:
    module: frontend
    package: src/services
    pattern: "{name}Service.js"
    test_pattern: "{name}Service.test.js"
```

### Test Patterns

```toon
placement:
  unit_test:
    module: same-as-source
    package: same-as-source
    pattern: "{Name}Test.java"

  integration_test:
    module: integration-testing
    package: com.example.integration.{feature}
    pattern: "{Name}IT.java"

  e2e_test:
    module: e2e-testing
    package: tests/{feature}
    pattern: "{name}.spec.ts"
```

## NiFi-Specific Patterns

```toon
placement:
  processor:
    module: nifi-cuioss-processors
    package: de.cuioss.nifi.processors.{feature}
    pattern: "{Name}Processor.java"
    test_pattern: "{Name}ProcessorTest.java"
    example: OAuthTokenProcessor.java

  controller_service:
    module: nifi-cuioss-processors
    package: de.cuioss.nifi.controller.{feature}
    pattern: "{Name}Service.java"
    test_pattern: "{Name}ServiceTest.java"

  ui_component:
    module: nifi-cuioss-ui
    package: src/main/webapp/js/nf-{feature}
    pattern: "nf-{name}.js"
```

## Query Usage

### CLI Query

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  placement query --component-type processor
```

### Output

```toon
status: success
component_type: processor
module: nifi-cuioss-processors
package: de.cuioss.nifi.processors.{feature}
pattern: {Name}Processor.java
test_pattern: {Name}ProcessorTest.java
example: OAuthTokenProcessor.java
```

### In Solution Outline

When creating deliverables, query placement to determine:
1. Target module
2. Package for new files
3. Naming pattern to follow

## Setting Rules

### CLI Set

```bash
python3 .plan/execute-script.py plan-marshall:project-structure:manage_project_structure \
  placement set \
  --component-type processor \
  --module nifi-cuioss-processors \
  --package "de.cuioss.nifi.processors.{feature}" \
  --pattern "{Name}Processor.java" \
  --test-pattern "{Name}ProcessorTest.java" \
  --example "OAuthTokenProcessor.java"
```

## Best Practices

1. **One rule per component type**: Clear, unambiguous placement
2. **Include test patterns**: Ensure tests follow same organization
3. **Provide examples**: Real file names help understanding
4. **Use consistent placeholders**: Same placeholder meaning across rules
5. **Document special cases**: Note exceptions in module tips

## Fallback Behavior

When no placement rule exists:
1. Use module's primary package from `key_packages`
2. Follow general naming conventions from `conventions.naming`
3. Ask user if ambiguous

## Related Documents

- `standards/toon-format.md` - Complete TOON schema
- `standards/layer-definitions.md` - Layer semantics
