# Run Configuration Format

JSON schema specification for `.claude/run-configuration.json`.

## Purpose

The run configuration file stores:
- Command execution history
- Acceptable warnings and skip lists
- Maven build configurations

> **Note**: Lessons learned are stored separately in `.claude/lessons-learned/`. See the `claude-lessons-learned` skill.

## Schema

```json
{
  "version": 1,
  "commands": {
    "<command-name>": {
      "last_execution": {
        "date": "2025-11-25",
        "status": "SUCCESS|FAILURE"
      },
      "skipped_files": ["file1.txt"],
      "skipped_directories": ["dir/"],
      "acceptable_warnings": [],
      "user_approved_permissions": []
    }
  },
  "maven": {
    "acceptable_warnings": {
      "transitive_dependency": [],
      "plugin_compatibility": [],
      "platform_specific": []
    }
  }
}
```

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| version | integer | Schema version (currently 1) |
| commands | object | Command-specific configurations |

## Optional Sections

| Section | Purpose |
|---------|---------|
| maven | Maven build configurations |

---

## Commands Section

Each command entry can have:

| Field | Type | Description |
|-------|------|-------------|
| last_execution | object | Most recent execution details |
| acceptable_warnings | array | Warning patterns to ignore |
| skipped_files | array | Files to skip in processing |
| skipped_directories | array | Directories to skip |
| user_approved_permissions | array | Permissions approved by user |

### last_execution Fields

| Field | Type | Description |
|-------|------|-------------|
| date | string | ISO date of execution |
| status | string | SUCCESS or FAILURE |

---

## Maven Section

Maven acceptable warnings configuration.

| Field | Type | Description |
|-------|------|-------------|
| acceptable_warnings | object | Warning patterns by category |

### acceptable_warnings Categories

| Category | Description |
|----------|-------------|
| transitive_dependency | Dependency-related warnings |
| plugin_compatibility | Plugin compatibility warnings |
| platform_specific | Platform-specific warnings |

---

## JSON Path Access

Use dot notation for field access:

| Path | Access |
|------|--------|
| `commands` | All commands |
| `commands.my-cmd` | Specific command |
| `commands.my-cmd.last_execution.date` | Execution date |
| `commands.my-cmd.skipped_files[0]` | First skipped file |
| `maven.acceptable_warnings` | Maven warnings |

---

## Example

```json
{
  "version": 1,
  "commands": {
    "setup-project-permissions": {
      "last_execution": {
        "date": "2025-11-25",
        "status": "SUCCESS"
      },
      "user_approved_permissions": []
    },
    "docs-technical-adoc-review": {
      "last_execution": {
        "date": "2025-11-24",
        "status": "SUCCESS"
      },
      "skipped_files": ["CHANGELOG.adoc"],
      "skipped_directories": ["target/", "node_modules/"],
      "acceptable_warnings": []
    }
  },
  "maven": {
    "acceptable_warnings": {
      "transitive_dependency": [],
      "plugin_compatibility": [],
      "platform_specific": []
    }
  }
}
```
