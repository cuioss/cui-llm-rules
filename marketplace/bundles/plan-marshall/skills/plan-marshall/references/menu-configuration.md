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
    - label: "Skill Domains"
      description: "Configure implementation skills per domain"
      value: "skill-domains"
    - label: "Modules"
      description: "Configure project modules"
      value: "modules"
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
| skill-domains | Execute "Configuration: Skill Domains" below |
| modules | Execute "Configuration: Modules" below |
| wizard | Load and execute: `Read references/wizard-flow.md` |
| back | Return to Main Menu |

---

## Configuration: Build System

### Detect Build Systems

```bash
python3 .plan/execute-script.py pm-dev-builder:environment-detection:build-env detect
```

### Auto-Configure Detected Systems

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config build-systems detect
```

This detects build systems from project files and adds them with default commands.

### Build System Mappings

| Detected | Skill | Verification Command |
|----------|-------|---------------------|
| Maven | `pm-dev-builder:builder-maven-rules` | `/pm-dev-builder:builder-build-and-fix` |
| Gradle | `pm-dev-builder:builder-gradle-rules` | `/pm-dev-builder:builder-build-and-fix` |
| npm | `pm-dev-builder:builder-npm-rules` | `/pm-dev-builder:builder-build-and-fix system=npm` |

### View Configured Build Systems

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config build-systems list
```

### Add/Remove Build System

```bash
# Add Gradle with defaults
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config build-systems add --system gradle

# Remove unused build system
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config build-systems remove --system gradle
```

---

## Configuration: Skill Domains

Skill domains configure which implementation skills are loaded for different code types.

### Detect Domains

Auto-detect skill domains from project files (pom.xml → java, package.json → javascript):

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config skill-domains detect
```

This populates the nested `skill_domains` structure with workflow_skills, core, implementation, and testing blocks.

### List Domains

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config skill-domains list
```

### View Domain Configuration

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config skill-domains get --domain java
```

### Resolve Domain Skills (for task planning)

Aggregate core + profile skills with descriptions for LLM skill selection:

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config resolve-domain-skills \
  --domain java --profile implementation
```

### Update Domain Skills

```bash
# Add JavaDoc to Java defaults
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config skill-domains set \
  --domain java \
  --defaults "pm-dev-java:java-core,pm-dev-java:javadoc"
```

---

## Configuration: Modules

Modules define project structure with domain and build system mappings.

### Detect Modules

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config modules detect
```

### List Modules

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config modules list
```

### Add Module

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config modules add \
  --module my-module \
  --path path/to/module \
  --domains "java,java-testing" \
  --build-systems "maven"
```

---

## Thin Agent Architecture

The pm-workflow bundle uses thin agents that load domain-specific skills dynamically:

| Agent | Purpose | Skill Source |
|-------|---------|--------------|
| `plan-init-agent` | Initialize plan, detect domains | System skills only |
| `solution-outline-agent` | Create deliverables | `config.workflow_skills.{domain}.solution_outline` |
| `task-plan-agent` | Create tasks from deliverables | `config.workflow_skills.{domain}.task_plan` |
| `task-execute-agent` | Execute single task | `config.workflow_skills.{domain}.{profile}` + `task.skills` |

Domain skill mappings are configured in `skill_domains` within marshal.json and written to plan's config.toon during init.

---

After any configuration completes, return to Main Menu.
