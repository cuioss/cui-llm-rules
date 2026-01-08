# First-Run Wizard Flow

Sequential structured setup for new projects. Execute steps in order.

---

## Step 1: Gitignore Setup

Configure `.gitignore` for `.plan/` directory with tracked file exceptions.

**BOOTSTRAP**: Use DIRECT Python call (no executor yet):

```bash
python3 ${PLUGIN_ROOT}/plan-marshall/skills/marshall-steward/scripts/gitignore-setup.py
```

**Output (TOON)**:
```toon
status	created
gitignore_path	/path/to/.gitignore
entries_added	3
```

**Tracked Files**:
- `.plan/marshal.json` - Project configuration
- `.plan/project-architecture/` - Project architecture data

| status | Meaning |
|--------|---------|
| `created` | New .gitignore created with planning entries |
| `updated` | Existing .gitignore updated with planning entries |
| `unchanged` | Planning entries already present |

**NOTE**: `execute-script.py` is NOT tracked because it contains local absolute paths and must be regenerated per-machine.

---

## Step 1b: Update Project Documentation

Check if project docs need `.plan/temp/` documentation:

**BOOTSTRAP**: Use DIRECT Python call (executor not yet available):

```bash
python3 ${PLUGIN_ROOT}/plan-marshall/skills/marshall-steward/scripts/determine-mode.py check-docs
```

**Output (TOON)**:
```toon
status	ok
files_needing_update	0
```

Or if updates needed:
```toon
status	needs_update
files_needing_update	2
missing	CLAUDE.md,agents.md
```

If `status` is `needs_update`, add to each listed file's appropriate section:
```
- Use `.plan/temp/` for ALL temporary files (covered by `Write(.plan/**)` permission - avoids permission prompts)
```

---

## Step 1c: Ensure Executor Permission

Add the executor permission to project-local settings so script execution doesn't prompt:

**BOOTSTRAP**: Use DIRECT Python call (no executor yet):

```bash
python3 ${PLUGIN_ROOT}/plan-marshall/skills/permission-fix/scripts/permission-fix.py ensure \
  --permissions "Bash(python3 .plan/execute-script.py *)" \
  --target project
```

**Output (TOON)**:
```toon
status	added
permission	Bash(python3 .plan/execute-script.py *)
target	project
settings_file	/path/to/.claude/settings.local.json
```

| status | Meaning |
|--------|---------|
| `added` | Permission added to project settings |
| `exists` | Permission already present |

This ensures script execution works without prompting, independent of global settings.

---

## Step 2: Generate Executor

**BOOTSTRAP**: Use DIRECT Python call with glob (executor doesn't exist yet):

```bash
python3 ${PLUGIN_ROOT}/plan-marshall/skills/script-executor/scripts/generate-executor.py generate
```

**Output (TOON)**:
```toon
status	scripts_discovered	executor_generated	logs_cleaned
success	109	.plan/execute-script.py	0
```

The script auto-detects the plugin cache location and generates `.plan/execute-script.py` with all script mappings embedded.

**Verify syntax**:
```bash
python3 -m py_compile .plan/execute-script.py && echo "Executor syntax OK"
```

**Ensure executor permission** (prevents permission prompts when using executor):
```bash
python3 ${PLUGIN_ROOT}/plan-marshall/skills/permission-fix/scripts/permission-fix.py ensure \
  --permissions "Bash(python3 .plan/execute-script.py *)" \
  --target project
```

**Output**: "Executor ready with N script mappings"

**NOTE**: From this point on, all script calls use: `python3 .plan/execute-script.py {notation} ...`

---

## Step 3: Discover Project Architecture (Source of Truth)

Discover modules directly from filesystem via extension API. This creates `derived-data.json` which is the single source of truth for module information.

**No marshal.json dependency** - works even before marshal.json exists.

```bash
python3 .plan/execute-script.py plan-marshall:analyze-project-architecture:architecture discover --force
```

**Output (TOON)**:
```toon
status	success
modules_discovered	10
output_file	.plan/project-architecture/derived-data.json
```

This creates `.plan/project-architecture/derived-data.json` with:
- All modules with paths, build_systems, packaging
- Per-module details (packages, dependencies, source/test counts)
- Documentation paths (README locations)
- Build commands

**Verification** - Display discovered modules:
```
Modules discovered: 10
  - bom (pom, maven)
  - oauth-sheriff-core (jar, maven)
  - oauth-sheriff-quarkus-parent (pom, maven)
  - oauth-sheriff-quarkus (jar, maven) [parent: oauth-sheriff-quarkus-parent]
  - oauth-sheriff-quarkus-deployment (jar, maven+npm) [parent: oauth-sheriff-quarkus-parent]
  ...
```

**Hybrid modules** are detected automatically when both pom.xml and package.json exist.

---

## Step 4: Initialize Marshal.json

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config init
```

**Output**: "Created .plan/marshal.json with defaults"

**Note**: marshal.json no longer contains module detection data - only configuration. Module list comes from raw-project-data.json.

---

## Step 4b: Apply Extension Defaults

Apply project-specific configuration defaults from domain extensions. Each extension's `config_defaults()` callback is invoked to set domain-specific values in `run-configuration.json`.

```bash
python3 .plan/execute-script.py plan-marshall:extension-api:extension apply-config-defaults
```

**Output (TOON)**:
```toon
status	success
extensions_called	3
extensions_skipped	2
errors_count	0
```

| Field | Description |
|-------|-------------|
| `extensions_called` | Extensions that provided config_defaults() |
| `extensions_skipped` | Extensions without config_defaults() implementation |
| `errors_count` | Failures during callback execution |

**Contract**: Extensions use write-once semantics - they only set defaults if keys don't already exist in `run-configuration.json`. User-defined values are never overwritten.

**Example defaults set by extensions**:
- Profile mappings (e.g., `itest` → `skip`)
- Coverage profiles to exclude
- Build-specific timeout defaults

See `standards/config-callback.md` in `extension-api` skill for the callback contract.

---

## Step 5: Configure Build Commands

Build commands are stored in `module_config` section of marshal.json, separate from module detection data.

### Step 5a: Detect Available Profiles

Query for Maven/Gradle profiles that can be mapped to canonical commands:

```bash
python3 .plan/execute-script.py plan-marshall:extension-api:build_env detect-profiles
```

**Output (TOON)**:
```toon
status: success
modules_with_profiles: 2

profiles[5]{module,id,canonical,activation_type}:
default	pre-commit	quality-gate	command-line
default	coverage	coverage	command-line
oauth-sheriff-core	integration-tests	integration-tests	command-line
oauth-sheriff-core	coverage	coverage	command-line
oauth-sheriff-core	benchmark	performance	command-line
```

Display profile summary:
```
Profiles detected: 5
  - default: pre-commit → quality-gate, coverage → coverage
  - oauth-sheriff-core: integration-tests, coverage, benchmark → performance
```

### Step 5b: User Command Selection

**Tiered approach** to handle projects of all sizes:

#### Tier 1: Setup Mode Selection

```yaml
AskUserQuestion:
  question: "How do you want to configure module commands?"
  header: "Setup Mode"
  options:
    - label: "Auto-detect (Recommended)"
      description: "Use smart defaults based on module types and detected profiles"
    - label: "Customize per module"
      description: "Select commands for each module individually"
    - label: "Minimal"
      description: "Only required commands (module-tests, quality-gate, verify)"
  multiSelect: false
```

**Routing:**

| Selection | Action |
|-----------|--------|
| Auto-detect | Go to Tier 2 (if profiles detected) or directly to Step 5c |
| Customize | Go to Tier 3 (per-module selection) |
| Minimal | Go to Step 5c with `--minimal` flag |

---

#### Tier 2: Profile Confirmation (Auto-detect path)

Only shown if profiles were detected:

```yaml
AskUserQuestion:
  question: "Detected specialized profiles in 2 modules. Include them?"
  header: "Profiles"
  multiSelect: true
  options:
    - label: "oauth-sheriff-core: integration-tests"
      description: "Integration tests (mvn verify -Pintegration-tests)"
    - label: "oauth-sheriff-core: coverage"
      description: "JaCoCo coverage (mvn verify -Pcoverage)"
    - label: "oauth-sheriff-core: benchmark → performance"
      description: "JMH benchmarks (mvn verify -Pbenchmark)"
    - label: "default: coverage"
      description: "Coverage reporting (mvn verify -Pcoverage)"
```

Selected profiles are passed to `persist` command. Proceed to Step 5c.

---

#### Tier 3: Per-Module Selection (Customize path)

For each module with available commands, present multi-select:

```yaml
AskUserQuestion:
  question: "Select commands for module 'oauth-sheriff-core':"
  header: "Commands"
  multiSelect: true
  options:
    - label: "module-tests (Required)"
      description: "Unit tests (mvn clean test)"
    - label: "quality-gate (Required)"
      description: "Quality checks (mvn verify -Ppre-commit)"
    - label: "verify (Required)"
      description: "Full verification (mvn clean verify)"
    - label: "integration-tests [DETECTED]"
      description: "Integration tests (mvn verify -Pintegration-tests)"
    - label: "coverage [DETECTED]"
      description: "Test coverage (mvn verify -Pcoverage)"
    - label: "performance [DETECTED]"
      description: "JMH benchmarks (mvn verify -Pbenchmark)"
    - label: "install"
      description: "Install to local repo (mvn clean install)"
```

Repeat for each module. Proceed to Step 5c with collected selections.

---

### Step 5c: Generate and Persist Commands

Based on user selection, generate and persist commands:

```bash
# Auto-detect mode (with optional profile filter)
python3 .plan/execute-script.py plan-marshall:extension-api:build_env persist

# Minimal mode
python3 .plan/execute-script.py plan-marshall:extension-api:build_env persist --minimal

# With specific profiles selected (from Tier 2)
python3 .plan/execute-script.py plan-marshall:extension-api:build_env persist \
  --include-profiles "oauth-sheriff-core:integration-tests,oauth-sheriff-core:coverage"
```

**Output (TOON)**:
```toon
status: success
build_systems: maven,npm
modules_updated: 3
commands_generated: 18

modules[3]{name,path,type,commands_count}:
default	.	pom	4
oauth-sheriff-core	oauth-sheriff-core	jar	8
oauth-sheriff-ui	oauth-sheriff-ui	npm	6
```

Display to user:
```
Build Systems: Maven, npm
Modules configured: 3
  - default (pom, 4 commands)
  - oauth-sheriff-core (jar, 8 commands)
  - oauth-sheriff-ui (npm, 6 commands)
```

### Step 5c-2: Resolve Unmapped Profiles

If `build_env persist` reports unmapped profiles, resolve them interactively:

**Check output for unmapped profiles**:
```toon
unmapped_profiles[3]{module,profile_id}:
default	jfr
benchmark-core	analyze-jfr
benchmark-core	quick

hint: Use 'run_config profile-mapping set ...' to resolve
```

**For each unique unmapped profile**, ask user to classify:

```yaml
AskUserQuestion:
  question: "Profile 'jfr' detected but can't be auto-classified. What is it?"
  header: "Profile"
  options:
    - label: "Skip (internal/unused)"
      description: "Exclude from command generation"
    - label: "Integration tests"
      description: "Integration or E2E test execution"
    - label: "Coverage"
      description: "Code coverage analysis"
    - label: "Performance"
      description: "Benchmark or performance testing"
  multiSelect: false
```

**Map user selection to canonical**:

| Selection | Canonical |
|-----------|-----------|
| Skip | `skip` |
| Integration tests | `integration-tests` |
| Coverage | `coverage` |
| Performance | `performance` |
| Quality gate | `quality-gate` |

**Save decision to run-config**:

```bash
python3 .plan/execute-script.py plan-marshall:run-config:run_config profile-mapping set \
  --profile-id jfr --canonical skip
```

**Batch mode** - If multiple profiles share same classification:

```bash
python3 .plan/execute-script.py plan-marshall:run-config:run_config profile-mapping batch-set \
  --mappings-json '{"jfr": "skip", "analyze-jfr": "skip", "quick": "skip"}'
```

**Re-run persist** after all mappings are saved:

```bash
python3 .plan/execute-script.py plan-marshall:extension-api:build_env persist
```

This ensures marshal.json contains only resolved commands with no diagnostic artifacts.

### Step 5c-3: Infer Module Domains

Auto-populate module domains from build_systems:

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  modules infer-domains
```

**Output (TOON)**:
```toon
status: success
updated_count: 3
updated:
  - module: oauth-sheriff-core
    domains: java
    from_build_systems: maven
  - module: oauth-sheriff-ui
    domains: javascript
    from_build_systems: npm
  - module: default
    domains: java
    from_build_systems: maven
skipped_count: 0
```

**Domain Inference Mapping:**

| Build System | Inferred Domain |
|--------------|-----------------|
| maven | java |
| gradle | java |
| npm | javascript |

Hybrid modules with multiple build systems (e.g., Maven + npm) get both domains: `["java", "javascript"]`.

---

### Canonical Command Names

Commands use a fixed vocabulary for programmatic lookup by plan execution agents:

| Canonical | Required | Description |
|-----------|----------|-------------|
| `module-tests` | **Yes** | Unit tests for the module |
| `quality-gate` | **Yes** | Pre-commit checks (lint, format, static analysis) |
| `verify` | **Yes** | Full build verification |
| `integration-tests` | No | Integration/E2E tests |
| `coverage` | No | Test coverage reports |
| `performance` | No | Benchmark/performance tests |
| `install` | No | Install to local repository |
| `package` | No | Create distributable package |

### Hybrid Module Support

Modules with multiple build systems (e.g., Maven + npm) get nested command format:

```json
{
  "module-tests": {
    "maven": "python3 .plan/execute-script.py ... --goals \"clean test\"",
    "npm": "python3 .plan/execute-script.py ... --command \"run test\""
  }
}
```

Use `lookup --build-system maven` or `lookup --build-system npm` to get specific command.

---

### Step 6: Skill Domain Configuration

Configure skill domains using bundle discovery. Domains are auto-discovered from installed bundles.

**Step 6a: Discover available domains**

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains get-available
```

**Output (JSON)**:
```json
{
  "status": "success",
  "discovered_domains": [
    {
      "key": "java",
      "bundle": "pm-dev-java",
      "name": "Java Development",
      "description": "Java code patterns, CDI, JUnit testing, Maven/Gradle builds",
      "applicable": true
    },
    {
      "key": "java-cui",
      "bundle": "pm-dev-java-cui",
      "name": "CUI Java Development",
      "description": "CUI-specific Java patterns for logging, testing, and HTTP",
      "applicable": true
    },
    {
      "key": "javascript",
      "bundle": "pm-dev-frontend",
      "name": "JavaScript Development",
      "description": "Modern JavaScript, ESLint, Jest testing, npm builds",
      "applicable": false
    },
    {
      "key": "plan-marshall-plugin-dev",
      "bundle": "pm-plugin-development",
      "name": "Plugin Development",
      "description": "Claude Code marketplace component development",
      "applicable": false
    },
    {
      "key": "requirements",
      "bundle": "pm-requirements",
      "name": "Requirements Engineering",
      "description": "User stories, acceptance criteria, specifications",
      "applicable": false
    }
  ]
}
```

The `applicable` flag indicates whether the domain's extension detected this project type (via `is_applicable()`).

**Step 6b: Auto-configure detected domains**

All domains with `applicable: true` are automatically configured without user interaction:

```
Detected domains (auto-configured):
- java (pm-dev-java)
- java-cui (pm-dev-java-cui)
- requirements (pm-requirements)
```

**Step 6c: User selection for optional domains**

Present non-applicable domains for optional selection. **Note: AskUserQuestion supports max 4 options.**

```yaml
AskUserQuestion:
  question: "Enable additional skill domains?"
  header: "Optional Domains"
  multiSelect: true
  options:
    # Show up to 4 non-applicable domains
    - label: "JavaScript Development"
      description: "Modern JS, ESLint, Jest (pm-dev-frontend)"
    - label: "Plugin Development"
      description: "Claude Code marketplace (pm-plugin-development)"
    - label: "Documentation"
      description: "AsciiDoc, ADRs (pm-documents)"
    # If more than 4 available, show most relevant 4
```

If more than 4 optional domains exist, prioritize by relevance or show multiple questions.

**Selection Rule**:
1. Auto-configure all `applicable: true` domains
2. Ask about optional domains (max 4 per question)
3. To add more domains later: `skill-domains configure --domains "domain1,domain2"`

**Step 6d: Configure selected domains**

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config \
  skill-domains configure --domains "java,java-cui,javascript"
```

**Output (TOON)**:
```toon
status: success
system_domain: configured
domains_configured: 3
domains: java,java-cui,javascript
```

This populates `skill_domains` in marshal.json with:
- `system` domain (always) with workflow_skills for 5 phases
- Each selected domain with nested structure from bundle manifest:
  - `workflow_skill_extensions` (outline, triage)
  - `core` (defaults + optionals)
  - Profile blocks (implementation, testing, quality)

---

## Step 7: Verify Skill Domain Configuration

Skill domains configure which implementation skills are loaded during plan execution. The 5-phase model uses:
- **System domain**: Contains workflow_skills (init, outline, plan, execute, finalize)
- **Technical domains**: Profile-based skills and workflow_skill_extensions

```bash
python3 .plan/execute-script.py plan-marshall:plan-marshall-config:plan-marshall-config skill-domains list
```

**Expected output**: Shows configured domains:
```json
{
  "system": {
    "workflow_skills": {
      "init": "pm-workflow:plan-init",
      "outline": "pm-workflow:solution-outline",
      "plan": "pm-workflow:task-plan",
      "execute": "pm-workflow:task-execute",
      "finalize": "pm-workflow:plan-finalize"
    }
  },
  "java": {
    "workflow_skill_extensions": {
      "outline": "pm-dev-java:java-outline-ext",
      "triage": "pm-dev-java:java-triage"
    },
    "core": {...},
    "architecture": {...},
    "implementation": {...},
    "testing": {...},
    "quality": {...}
  }
}
```

**Note**: Workflow skills are resolved from system domain. Domain-specific behavior is provided via workflow_skill_extensions (outline, triage).

---

## Step 8: Project Structure Analysis

Generate project structure knowledge for solution outline support.

**Prerequisites**: Step 3 created `.plan/raw-project-data.json` with all module information.

### Step 8a: LLM Architectural Analysis

Invoke the analysis skill to read raw data and generate meaningful structure:

```
Skill: plan-marshall:analyze-project-architecture
```

The LLM analysis reads discovered data, samples documentation and source code, then enriches with:
- Semantic module responsibilities (not just names)
- Module purpose classification (library, extension, runtime, etc.)
- 2-4 key packages per module with descriptions
- Proposed skill domains
- Implementation tips and insights

**Output**: `.plan/project-architecture/llm-enriched.json` with rich, meaningful content

### Step 8b: User Refinement (Optional)

Display generated structure and offer refinement:

```yaml
AskUserQuestion:
  question: "Review analyzed structure. Refine any module details?"
  header: "Structure"
  options:
    - label: "Accept analysis"
      description: "Use LLM-generated structure as-is"
    - label: "Refine responsibilities"
      description: "Adjust module descriptions manually"
  multiSelect: false
```

If user chooses "Refine responsibilities", for each module with uncertain analysis:

```yaml
AskUserQuestion:
  question: "Confirm 'oauth-sheriff-core' responsibility:"
  header: "Module"
  options:
    - label: "Validates OAuth access tokens against security policies"
      description: "LLM-suggested based on code analysis"
    - label: "Core business logic"
      description: "Generic description"
  multiSelect: false
```

Update with user input:
```bash
python3 .plan/execute-script.py plan-marshall:analyze-project-architecture:architecture \
  enrich module --name oauth-sheriff-core --responsibility "Core OAuth token validation and refresh logic"
```

### Step 8c: Verify Structure

```bash
python3 .plan/execute-script.py plan-marshall:analyze-project-architecture:architecture info
```

Verify that all modules have responsibilities and key packages. Missing fields indicate areas needing attention.

---

## Step 9: Detect CI Provider

Detect CI provider and verify tools:

```bash
python3 .plan/execute-script.py plan-marshall:ci-operations:ci_health status
```

Display detection result to user. If tool not authenticated, warn:
- "GitHub detected but 'gh' not authenticated. Run 'gh auth login' for CI operations."
- "GitLab detected but 'glab' not authenticated. Run 'glab auth login' for CI operations."

Persist CI configuration to marshal.json:
```bash
python3 .plan/execute-script.py plan-marshall:ci-operations:ci_health persist
```

**Output**: CI configuration persisted to marshal.json with detected provider and authenticated tools.

---

## Step 10: Permission Setup

```
AskUserQuestion:
  question: "Configure permissions now?"
  options:
    - label: "Yes"
      description: "Set up global and project permissions"
      value: "yes"
    - label: "Later"
      description: "Skip permission setup for now"
      value: "no"
```

If yes:
```bash
python3 .plan/execute-script.py plan-marshall:permission-fix:permission-fix apply-fixes --scope project
```

---

## Step 11: Summary

Output final summary:

```toon
status: success
operation: wizard_complete

gitignore: configured
executor:
  path: .plan/execute-script.py
  script_count: 45
marshal:
  path: .plan/marshal.json
project_architecture:
  path: .plan/project-architecture/
  modules_count: 3
build_systems:
  - maven
  - npm
modules:
  count: 3
  commands_generated: 15
skill_domains:
  - java
  - javascript
  - plugin

next_steps:
  - Run /plan-manage to create a new plan
  - Use /marshall-steward for maintenance tasks
```

After summary output, wizard is complete. Exit skill execution.
