# Error Handling Skill

This skill implements the **Reversed Hook Architecture** for detecting and handling errors in Claude Code tool output.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           REVERSED HOOK ARCHITECTURE                                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────┐    ┌─────────────────┐    ┌───────────────────────────────────────┐   │
│  │   Claude    │───▶│   Tool Call     │───▶│     PostToolUse Hook                  │   │
│  │   Code      │    │   (Task, Bash,  │    │     (error-detector.sh)               │   │
│  │             │    │   Skill, etc.)  │    │                                       │   │
│  └─────────────┘    └─────────────────┘    │  1. Receives tool output via stdin    │   │
│                                            │  2. Pattern matches for errors         │   │
│                                            │  3. If error: saves context, blocks    │   │
│                                            │  4. Instructs LLM to load skill        │   │
│                                            └──────────────┬────────────────────────┘   │
│                                                           │                             │
│                              ┌────────────────────────────┼────────────────────────┐   │
│                              │                            ▼                        │   │
│                              │    ┌─────────────────────────────────────────┐     │   │
│                              │    │     .plan/error-context.toon            │     │   │
│                              │    │                                         │     │   │
│                              │    │  timestamp: "2024-12-06T15:30:00"       │     │   │
│                              │    │  tool: "Task"                           │     │   │
│                              │    │  error:                                 │     │   │
│                              │    │    patterns_matched: "Unknown skill"    │     │   │
│                              │    │    blocking: true                       │     │   │
│                              │    │  raw_output: |                          │     │   │
│                              │    │    Error: Unknown skill: ...            │     │   │
│                              │    └─────────────────────────────────────────┘     │   │
│                              │                            │                        │   │
│                              │                            ▼                        │   │
│  ┌─────────────┐            │    ┌─────────────────────────────────────────┐     │   │
│  │   Claude    │◀───────────│────│  Error-Handling Skill (SKILL.md)        │     │   │
│  │   Code      │            │    │                                         │     │   │
│  │  (receives  │            │    │  1. Reads error context                 │     │   │
│  │  analysis)  │            │    │  2. Classifies error type               │     │   │
│  └─────────────┘            │    │  3. Loads analysis standard             │     │   │
│        │                    │    │  4. Performs root cause analysis        │     │   │
│        ▼                    │    │  5. Presents options to user            │     │   │
│  ┌─────────────┐            │    │  6. WAITS for user decision             │     │   │
│  │   User      │            │    │  7. Logs resolution to work-log         │     │   │
│  │  Decision   │            │    └─────────────────────────────────────────┘     │   │
│  └─────────────┘            │                                                     │   │
│                              │                    ERROR HANDLING                   │   │
│                              │                       DOMAIN                        │   │
│                              └─────────────────────────────────────────────────────┘   │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Why Reversed Architecture?

Traditional approach: Skill detects and handles errors internally.
**Problem**: Errors inside agent delegations (Task tool) are invisible to parent skills.

Reversed approach: Hook detects errors, skill provides analysis.
**Benefit**: Works across all tool calls, including nested agent delegations.

| Aspect | Traditional | Reversed |
|--------|-------------|----------|
| Error Detection | Skill reads output | Hook intercepts output |
| Visibility | Limited to direct calls | All tool output |
| Nested Errors | Invisible | Captured |
| Analysis | Simple (shell script) | Full LLM capabilities |
| User Interaction | None | Structured options |

## Components

### 1. Error Detector Hook (`scripts/error-detector.sh`)

A lightweight bash script that:
- Intercepts all tool output via PostToolUse hook
- Pattern matches for common error indicators
- Saves context to `.plan/error-context.toon`
- Instructs the LLM to load this skill

**Error Patterns Detected**:
- `status: error` - Structured error response
- `exit code [1-9]` - Non-zero exit codes
- `Unknown skill` - Skill resolution failures
- `skill not found` - Bundle resolution failures
- `not found` - Generic resource errors
- `failed` - Execution failures
- `exception` - Runtime exceptions

### 2. Error-Handling Skill (`SKILL.md`)

A skill that provides full LLM analysis capabilities:
- Reads and parses error context
- Classifies errors by type
- Loads appropriate analysis standards
- Presents structured analysis to user
- Waits for user decision
- Logs resolution to work-log

### 3. Analysis Standards (`standards/`)

This skill owns the analysis standards used by both error-handling and verification:

```
standards/
├── failure-analysis.md      # Script and tool failure analysis
├── resolution-analysis.md   # Path and reference resolution issues
└── workaround-detection.md  # Detecting and analyzing workarounds
```

## Installation

### Step 1: Configure Hook in Project Settings

Add to your `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "marketplace/bundles/cui-plugin-development-tools/skills/error-handling/scripts/error-detector.sh",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

### Step 2: Verify Hook is Executable

```bash
chmod +x marketplace/bundles/cui-plugin-development-tools/skills/error-handling/scripts/error-detector.sh
```

### Step 3: Verify Installation

Test the hook by triggering a known error:

```bash
# Test hook detection
echo "status: error" | marketplace/bundles/cui-plugin-development-tools/skills/error-handling/scripts/error-detector.sh
# Should output "ERROR DETECTED" message and exit with code 1

# Test pass-through
echo "status: success" | marketplace/bundles/cui-plugin-development-tools/skills/error-handling/scripts/error-detector.sh
# Should exit with code 0, no output
```

## Error Context Format (TOON)

The hook saves error context in TOON format (Token-Oriented Object Notation):

```toon
# Error Context
# Generated by error-detector hook

timestamp: "2024-12-06T15:30:00+01:00"
tool: "Task"
working_directory: "/Users/dev/project"

error:
  patterns_matched: "Unknown skill,not found"
  blocking: true

raw_output: |
  Error: Unknown skill: planning:invalid-skill
  The skill 'invalid-skill' was not found in bundle 'planning'
```

## Relationship with Verification Skill

This skill and the verification skill are **complementary**:

| Aspect | Error-Handling | Verification |
|--------|---------------|--------------|
| **Trigger** | Reactive (hook triggers) | Proactive (LLM self-monitors) |
| **Activation** | Automatic on error | Manual load |
| **Nested agents** | ✓ Can see | ✗ Cannot see |
| **Workarounds** | ✗ Cannot detect | ✓ Can detect |
| **Standards** | Owns standards | References this skill |

**When to use both**: Load verification for maximum coverage:
- Error-handling catches errors in nested agents via hooks
- Verification catches workarounds before they happen

## Integration with Other Skills

### Verification Skill

The verification skill (`cui-plugin-development-tools:verification`) provides:
- Proactive behavioral mode for manual QA workflows
- Workaround detection (catching when LLM is about to use alternative approaches)
- References this skill's `standards/` directory for analysis

### Manage-Log Skill

Uses `planning:manage-log` to record:
- Error occurrences
- User decisions
- Resolution outcomes

## Troubleshooting

### Hook Not Triggering

1. Verify hook configuration in `.claude/settings.json`
2. Ensure script is executable (`chmod +x`)
3. Check script path is correct (relative to project root)

### False Positives

If the hook triggers on non-error output containing error-like words:
1. Check the patterns in `error-detector.sh`
2. Consider adding exclusion patterns for known safe outputs
3. The hook uses case-insensitive matching

### Context File Not Created

1. Ensure `.plan/` directory exists
2. Check write permissions
3. Verify PROJECT_ROOT detection is finding the correct directory

## Testing

Run the integration tests:

```bash
python3 test/run-tests.py test/cui-plugin-development-tools/error-handling/
```
