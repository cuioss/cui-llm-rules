# Menu Option: Configuration

Sub-menu for build systems and plan-types configuration.

---

## Configuration Submenu

```
AskUserQuestion:
  question: "What would you like to configure?"
  options:
    - label: "Build Systems"
      description: "Detect and configure Maven/Gradle/npm"
      value: "build"
    - label: "Plan-Types"
      description: "Add/remove plan-types, define custom types"
      value: "plan-types"
    - label: "Full Reconfigure"
      description: "Run first-run wizard again"
      value: "wizard"
    - label: "Back"
      description: "Return to main menu"
      value: "back"
```

## Routing

| Selection | Action |
|-----------|--------|
| build | Execute "Configuration: Build System" below |
| plan-types | Execute "Configuration: Plan-Types" below |
| wizard | Load and execute: `Read references/wizard-flow.md` |
| back | Return to Main Menu |

---

## Configuration: Build System

### Detect Build Systems

```bash
python3 .plan/execute-script.py pm-dev-builder:environment-detection:build-env detect
```

### Configure Build Mappings

| Detected | Skill | Verification Command |
|----------|-------|---------------------|
| Maven | `pm-dev-builder:builder-maven-rules` | `/pm-dev-builder:builder-build-and-fix` |
| Gradle | `pm-dev-builder:builder-gradle-rules` | `/pm-dev-builder:builder-build-and-fix` |
| npm | `pm-dev-builder:builder-npm-rules` | `/pm-dev-builder:builder-build-and-fix system=npm` |

### Update Verification Commands

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config plan-type-defaults set \
  --plan-type pm-workflow:plan-type-java \
  --verification-command "/pm-dev-builder:builder-build-and-fix"
```

---

## Configuration: Plan-Types

### Add/Remove Plan-Types

```
AskUserQuestion:
  question: "Which plan-types to toggle?"
  options:
    - label: "Add Java"
      value: "add-java"
    - label: "Add JavaScript"
      value: "add-javascript"
    - label: "Add Plugin"
      value: "add-plugin"
    - label: "Remove a type"
      value: "remove"
    - label: "Define Custom"
      value: "custom"
    - label: "Back"
      value: "back"
```

### Routing

| Selection | Action |
|-----------|--------|
| add-java | Configure Java plan-type |
| add-javascript | Configure JavaScript plan-type |
| add-plugin | Configure Plugin plan-type |
| remove | Show list of configured types to remove |
| custom | Load and execute: `Read references/plan-type-wizard.md` |
| back | Return to Configuration Submenu |

### Add Plan-Type

For each type, configure domain agents:

**Java**:
```bash
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config domain-agents set \
  --plan-type pm-workflow:plan-type-java \
  --solution-outline-agent pm-dev-java:java-solution-outline-agent \
  --task-plan-agent pm-dev-java:java-task-plan-agent
```

**JavaScript**:
```bash
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config domain-agents set \
  --plan-type pm-workflow:plan-type-javascript \
  --solution-outline-agent pm-dev-frontend:js-solution-outline-agent \
  --task-plan-agent pm-dev-frontend:js-task-plan-agent
```

**Plugin**:
```bash
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config domain-agents set \
  --plan-type pm-workflow:plan-type-plugin \
  --solution-outline-agent pm-plugin-development:plugin-solution-outline-agent \
  --task-plan-agent pm-plugin-development:plugin-task-plan-agent
```

### Update Domain Agent Mappings

```bash
python3 .plan/execute-script.py pm-workflow:manage-config:marshal-config domain-agents set \
  --plan-type {plan_type} \
  --solution-outline-agent {solution_outline_agent} \
  --task-plan-agent {task_plan_agent}
```

---

After any configuration completes, return to Main Menu.
