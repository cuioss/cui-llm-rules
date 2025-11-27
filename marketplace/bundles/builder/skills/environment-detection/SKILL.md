---
name: environment-detection
description: Detect and cache build environment information for consistent workflow configuration
allowed-tools:
  - Read
  - Bash(python3:*)
---

# Environment Detection Skill

Central skill for querying the current build environment. Detects available build systems and caches results for consistent access across workflows.

## What This Skill Provides

- Detect available build systems (maven, gradle, npm)
- Determine default/primary build system
- Cache detection results in run-configuration
- Provide consistent environment info to all workflows

## When to Activate

Activate this skill when:
- Starting a new task that needs build system context
- Initializing plan configuration
- Any workflow needs to know available build tools
- Commands need to route to appropriate builders

## Cached Attributes

Stored in `.claude/run-configuration.json` under `build`:

| Attribute | Example | Description |
|-----------|---------|-------------|
| `build.available_systems` | `"maven,npm"` | Comma-separated list of detected systems |
| `build.default_system` | `"maven"` | Primary build system (highest priority) |

**Priority Order**: maven (1) > gradle (2) > npm (3)

---

## Workflow: Get Build Environment

**Pattern**: Command Chain Execution with Caching

Returns build environment info, using cached values when available.

### Step 1: Check Cache

Read from run-configuration:

```
Skill: cui-utilities:claude-run-configuration
Workflow: Read Configuration
Field: build
```

**If cached values exist** (both `available_systems` and `default_system` present):

```json
{
  "status": "cached",
  "available_systems": "maven,npm",
  "default_system": "maven"
}
```

→ Return cached values, skip to Step 4.

### Step 2: Detect Build Systems

If not cached, run detection:

```bash
python3 scripts/detect-build-systems.py --project-dir .
```

**Output:**
```json
{
  "status": "success",
  "available_systems": "maven,npm",
  "default_system": "maven",
  "detected": [
    {"name": "maven", "priority": 1, "technology": "java", "detected_by": "pom.xml"},
    {"name": "npm", "priority": 3, "technology": "javascript", "detected_by": "package.json"}
  ]
}
```

### Step 3: Cache Results

Store in run-configuration:

```
Skill: cui-utilities:claude-run-configuration
Workflow: Update Configuration
Field: build.available_systems
Value: "{available_systems}"

Skill: cui-utilities:claude-run-configuration
Workflow: Update Configuration
Field: build.default_system
Value: "{default_system}"
```

### Step 4: Return Environment

Return structured result:

```json
{
  "available_systems": "maven,npm",
  "default_system": "maven",
  "source": "cached|detected"
}
```

---

## Workflow: Refresh Build Environment

**Pattern**: Command Chain Execution

Force re-detection of build systems (bypasses cache).

### Step 1: Detect Build Systems

```bash
python3 scripts/detect-build-systems.py --project-dir .
```

### Step 2: Update Cache

```
Skill: cui-utilities:claude-run-configuration
Workflow: Update Configuration
Field: build.available_systems
Value: "{available_systems}"

Skill: cui-utilities:claude-run-configuration
Workflow: Update Configuration
Field: build.default_system
Value: "{default_system}"
```

### Step 3: Return Result

```json
{
  "available_systems": "maven,npm",
  "default_system": "maven",
  "source": "detected",
  "message": "Build environment refreshed"
}
```

---

## Workflow: Check Build System Available

**Pattern**: Simple Query

Check if a specific build system is available.

### Parameters

- **system** (required): Build system to check (maven, gradle, npm)

### Step 1: Get Environment

```
Skill: builder:environment-detection
Workflow: Get Build Environment
```

### Step 2: Check Availability

```python
available = result["available_systems"].split(",")
is_available = system in available
is_default = result["default_system"] == system
```

### Step 3: Return Result

```json
{
  "system": "maven",
  "available": true,
  "is_default": true
}
```

---

## Detection Logic

### Build File Detection

| System | Detection Files | Priority |
|--------|-----------------|----------|
| maven | `pom.xml` | 1 (highest) |
| gradle | `build.gradle`, `build.gradle.kts`, `settings.gradle`, `settings.gradle.kts` | 2 |
| npm | `package.json` | 3 |

### Priority Rules

- Lower number = higher priority
- Default system is the highest priority detected
- Multiple systems can coexist (e.g., Java backend + JS frontend)

### Example Scenarios

| Project Type | Detected | Default |
|--------------|----------|---------|
| Pure Maven | maven | maven |
| Pure npm | npm | npm |
| Maven + npm frontend | maven,npm | maven |
| Gradle + npm | gradle,npm | gradle |

---

## Run Configuration Schema

```json
{
  "build": {
    "available_systems": "maven,npm",
    "default_system": "maven"
  }
}
```

---

## Integration

### With Plan Init

```
# During plan initialization
Skill: builder:environment-detection
Workflow: Get Build Environment

# Use result for config.md
build_system = result["default_system"]
technology = derive_technology(build_system)
```

### With Build Commands

```
# Route to correct builder
Skill: builder:environment-detection
Workflow: Get Build Environment

if "maven" in result["available_systems"]:
    # Use /maven-build-and-fix
elif "gradle" in result["available_systems"]:
    # Use /gradle-build-and-fix
elif "npm" in result["available_systems"]:
    # Use /npm-build-and-fix
```

### With Task Workflow

```
# Determine technology for implementation
Skill: builder:environment-detection
Workflow: Get Build Environment

# Map to technology
technology_map = {
    "maven": "java",
    "gradle": "java",
    "npm": "javascript"
}
technology = technology_map.get(result["default_system"], "unknown")
```

---

## Scripts

| Script | Purpose |
|--------|---------|
| `detect-build-systems.py` | Scan project for build files |

Script characteristics:
- Uses Python stdlib only (json, argparse, pathlib)
- Outputs JSON to stdout
- Exit code 0 for success, 1 for errors
- Supports `--help` flag

---

## Related

- Skill: `cui-utilities:claude-run-configuration` - Cache storage
- Skill: `builder:builder-maven-rules` - Maven builds
- Skill: `builder:builder-gradle-rules` - Gradle builds
- Skill: `builder:builder-npm-rules` - npm builds
