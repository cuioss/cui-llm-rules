# Architecture Analysis Output

What the `analyze-project-architecture` skill produces for consumers.

## Client View

The primary consumer is **solution-outline** during task planning.

```
+------------------------------------------------------------------+
|                        SOLUTION-OUTLINE                           |
|                                                                   |
|  "I need to add a new Validator for JWT claims"                   |
|                                                                   |
|  Questions I need answered:                                       |
|    • Which module handles validation?                             |
|    • What package should the Validator go in?                     |
|    • What naming convention to follow?                            |
|    • What existing patterns to match?                             |
|    • What test conventions apply?                                 |
+------------------------------------------------------------------+
                              |
                              | queries
                              v
+------------------------------------------------------------------+
|                   ARCHITECTURAL DOCUMENT                          |
|                                                                   |
|  Provides:                                                        |
|    • Module responsibilities (which module for what)              |
|    • Placement rules (where new code goes)                        |
|    • Conventions (naming, patterns, testing)                      |
|    • Module relationships (dependencies, layers)                  |
+------------------------------------------------------------------+
```

## What Solution-Outline Needs

| Question | Document Section |
|----------|------------------|
| "Which module handles X?" | Module responsibilities |
| "Where does new code go?" | Placement rules |
| "What patterns to follow?" | Conventions |
| "What to test and how?" | Test patterns |
| "What depends on what?" | Module relationships |

## Output Format

The architectural document is a **concise summary** loaded into LLM context.

```
+------------------------------------------------------------------+
|                    ARCHITECTURAL DOCUMENT                         |
+------------------------------------------------------------------+

  1. Project Overview
  ===================
  Brief description of what the project does.


  2. Module Responsibilities
  ==========================
  Module-by-module: what each one does, when to use it.

  +-------------------+------------------------------------------+
  | Module            | Responsibility                           |
  +-------------------+------------------------------------------+
  | oauth-sheriff-core| Core JWT validation logic                |
  | ...-deployment    | Quarkus build-time processing            |
  | ...-quarkus       | Quarkus runtime extension                |
  +-------------------+------------------------------------------+


  3. Placement Rules
  ==================
  Where to put new components by type.

  +-------------------+-------------------+------------------------+
  | Component Type    | Module            | Package                |
  +-------------------+-------------------+------------------------+
  | Validator         | oauth-sheriff-core| ...core.pipeline       |
  | BuildStep         | ...-deployment    | ...deployment          |
  | Producer (CDI)    | ...-quarkus       | ...quarkus.runtime     |
  +-------------------+-------------------+------------------------+


  4. Conventions
  ==============
  Naming patterns, code style, framework usage.

  • Validators: {Name}Validator.java
  • Tests: {Name}Test.java (mirror structure)
  • CDI: Constructor injection, @ApplicationScoped


  5. Module Relationships
  =======================
  Dependencies and layering.

  oauth-sheriff-core  <--  oauth-sheriff-quarkus
                      <--  oauth-sheriff-quarkus-deployment
```

## How It's Used

```
Task: "Add JWT issuer validation"
                |
                v
Solution-outline reads architectural document
                |
                v
Determines:
  • Module: oauth-sheriff-core (handles validation)
  • Package: de.cuioss.sheriff.oauth.core.pipeline
  • Pattern: IssuerValidator.java
  • Test: IssuerValidatorTest.java (mirror)
                |
                v
Creates deliverables with correct placement
```

## Information Sources

The architectural document is generated from:

| Source | Contributes |
|--------|-------------|
| `discover_project_modules()` | Module names, paths, build systems |
| Module READMEs | Responsibilities |
| package-info.java | Package purposes |
| Existing code patterns | Conventions |
| User input (questionnaire) | Placement rules |

See [documentation-sources.md](documentation-sources.md) for reading priorities.

## Related Documents

| Document | Purpose |
|----------|---------|
| [documentation-sources.md](documentation-sources.md) | Where to find information |
| [extension-api/architecture-overview.md](../../extension-api/standards/architecture-overview.md) | Module discovery details |
