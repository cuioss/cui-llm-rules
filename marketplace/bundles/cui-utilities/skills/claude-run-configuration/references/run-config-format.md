# Run Configuration Format

JSON schema specification for `.claude/run-configuration.json`.

## Purpose

The run configuration file stores:
- Command execution history
- Lessons learned from command runs
- Acceptable warnings and skip lists
- Maven build configurations
- Agent architecture decisions

## Schema

```json
{
  "version": 1,
  "commands": {
    "<command-name>": {
      "last_execution": {
        "date": "2025-11-25",
        "status": "SUCCESS|FAILURE",
        "run_number": 1,
        "result": "Optional description"
      },
      "lessons_learned": ["Array of lessons"],
      "skipped_files": ["file1.txt"],
      "skipped_directories": ["dir/"],
      "acceptable_warnings": [],
      "user_approved_permissions": [],
      "changes_applied": {
        "global_added": [],
        "local_removed": [],
        "local_kept": []
      }
    }
  },
  "maven": {
    "<maven-command>": {
      "last_execution": {
        "duration_ms": 120000,
        "duration_human": "2 minutes",
        "last_updated": "2025-11-25"
      },
      "acceptable_warnings": [
        {
          "pattern": "[WARNING] ...",
          "category": "transitive_dependency|deprecation|other",
          "reason": "Why this is acceptable",
          "added": "2025-11-25"
        }
      ]
    }
  },
  "agent_decisions": {
    "<agent-name>": {
      "status": "keep-monolithic|refactored",
      "decision_date": "2025-10-30",
      "rationale": "Why this decision was made",
      "responsibilities": ["List of responsibilities"],
      "future_consideration": "Optional notes"
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
| agent_decisions | Agent architecture decisions |

---

## Commands Section

Each command entry can have:

| Field | Type | Description |
|-------|------|-------------|
| last_execution | object | Most recent execution details |
| lessons_learned | array | Accumulated lessons from executions |
| acceptable_warnings | array | Warning patterns to ignore |
| skipped_files | array | Files to skip in processing |
| skipped_directories | array | Directories to skip |
| user_approved_permissions | array | Permissions approved by user |
| changes_applied | object | Record of configuration changes |

### last_execution Fields

| Field | Type | Description |
|-------|------|-------------|
| date | string | ISO date of execution |
| status | string | SUCCESS or FAILURE |
| run_number | integer | Execution counter |
| result | string | Optional result description |

---

## Maven Section

Each maven command entry can have:

| Field | Type | Description |
|-------|------|-------------|
| last_execution | object | Build timing information |
| acceptable_warnings | array | Warning patterns to accept |

### Maven last_execution Fields

| Field | Type | Description |
|-------|------|-------------|
| duration_ms | integer | Build duration in milliseconds |
| duration_human | string | Human-readable duration |
| last_updated | string | Date of last update |

### Maven acceptable_warnings Entry

| Field | Type | Description |
|-------|------|-------------|
| pattern | string | Warning text pattern |
| category | string | transitive_dependency, deprecation, other |
| reason | string | Why this warning is acceptable |
| added | string | Date warning was accepted |

---

## Agent Decisions Section

Each agent decision entry can have:

| Field | Type | Description |
|-------|------|-------------|
| status | string | keep-monolithic or refactored |
| decision_date | string | When decision was made |
| rationale | string | Reasoning for decision |
| responsibilities | array | List of agent responsibilities |
| future_consideration | string | Optional notes for future |

---

## JSON Path Access

Use dot notation for field access:

| Path | Access |
|------|--------|
| `commands` | All commands |
| `commands.my-cmd` | Specific command |
| `commands.my-cmd.last_execution.date` | Execution date |
| `commands.my-cmd.lessons_learned[0]` | First lesson |
| `maven.build.acceptable_warnings` | Maven warnings |

---

## Example

```json
{
  "version": 1,
  "commands": {
    "setup-project-permissions": {
      "last_execution": {
        "date": "2025-11-25",
        "status": "SUCCESS",
        "run_number": 5
      },
      "lessons_learned": [
        "Always validate permissions before adding",
        "Check for duplicates in global settings"
      ]
    },
    "docs-technical-adoc-review": {
      "last_execution": {
        "date": "2025-11-24",
        "status": "SUCCESS",
        "run_number": 3
      },
      "skipped_files": ["CHANGELOG.adoc"],
      "acceptable_warnings": []
    }
  },
  "maven": {
    "build": {
      "last_execution": {
        "duration_ms": 45000,
        "duration_human": "45 seconds",
        "last_updated": "2025-11-25"
      }
    }
  }
}
```
