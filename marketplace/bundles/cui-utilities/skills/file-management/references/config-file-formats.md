# Configuration File Formats

JSON schema specifications for `.claude/` configuration files.

## run-configuration.json

Command configurations and execution history.

### Schema

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

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| version | integer | Schema version (currently 1) |
| commands | object | Command-specific configurations |

### Optional Sections

| Section | Purpose |
|---------|---------|
| maven | Maven build configurations |
| agent_decisions | Agent architecture decisions |

---

## scripts.local.json

Script path registry for script-runner skill.

### Schema

```json
{
  "version": 1,
  "scripts": {
    "<bundle:skill/scripts/name>": {
      "absolute": "/absolute/path/to/script.py",
      "type": "python|shell"
    }
  },
  "permissions": [
    "Bash(python3 /path/to/script.py:*)"
  ]
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| version | integer | Schema version |
| scripts | object | Script path mappings |
| permissions | array | Generated permission strings |

### Script Entry Format

Each script entry must have:
- `absolute`: Full filesystem path
- `type`: Script type (python, shell)

---

## settings.local.json

Project-specific Claude Code permissions.

### Schema

```json
{
  "allow": [
    "Bash(./mvnw:*)",
    "Skill(bundle:skill)",
    "WebFetch(domain:example.com)"
  ],
  "deny": [
    "Bash(rm -rf:*)"
  ],
  "ask": [
    "Bash(git push:*)"
  ]
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| allow | array | Auto-approved operations |
| deny | array | Blocked operations |
| ask | array | Operations requiring confirmation |

All fields are optional. Empty object is valid.

---

## JSON Path Notation

Use dot notation for field access:

| Path | Access |
|------|--------|
| `commands` | Top-level field |
| `commands.my-cmd` | Nested object |
| `commands.my-cmd.last_execution.date` | Deep nested |
| `commands.list[0]` | Array index |
| `commands.list[-1]` | Last array element |

### Special Characters

- Keys with dots/special chars: `commands."my.special.key"`
- Array indices: `[0]`, `[-1]`
