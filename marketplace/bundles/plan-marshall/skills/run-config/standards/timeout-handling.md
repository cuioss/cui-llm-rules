# Timeout Handling Specification

Adaptive timeout management for command execution, enabling learned timeout values based on historical execution data.

---

## Overview

The timeout handling system provides:
- **Retrieval with defaults**: Get timeout for a command with fallback to default value
- **Safety margin**: Apply buffer to persisted values to account for variance
- **Adaptive learning**: Update timeouts weighted towards longer durations for reliability

```
                    TIMEOUT FLOW

    ┌─────────────────────────────────────────────────────┐
    │                                                     │
    │   GET TIMEOUT                                       │
    │   ┌───────────────────────────────────────────┐     │
    │   │  timeout get                              │     │
    │   │    --command "ci:pr_checks"               │     │
    │   │    --default 300                          │     │
    │   └───────────────────────────────────────────┘     │
    │                       │                             │
    │           ┌───────────┴───────────┐                 │
    │           │                       │                 │
    │           ▼                       ▼                 │
    │     No persisted            Has persisted          │
    │     value                   value (240s)           │
    │           │                       │                 │
    │           ▼                       ▼                 │
    │     Return default          Apply safety margin    │
    │     (300s)                  (240 * 1.25 = 300s)    │
    │                                                     │
    └─────────────────────────────────────────────────────┘


    ┌─────────────────────────────────────────────────────┐
    │                                                     │
    │   SET TIMEOUT                                       │
    │   ┌───────────────────────────────────────────┐     │
    │   │  timeout set                              │     │
    │   │    --command "ci:pr_checks"               │     │
    │   │    --duration 180                         │     │
    │   └───────────────────────────────────────────┘     │
    │                       │                             │
    │           ┌───────────┴───────────┐                 │
    │           │                       │                 │
    │           ▼                       ▼                 │
    │     No existing             Has existing           │
    │     value                   value (240s)           │
    │           │                       │                 │
    │           ▼                       ▼                 │
    │     Write directly          Weighted update        │
    │     (180s)                  80% towards higher     │
    │                             max(180,240)=240       │
    │                             0.2*180 + 0.8*240      │
    │                             = 228s                 │
    │                                                     │
    └─────────────────────────────────────────────────────┘
```

---

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `SAFETY_MARGIN` | 1.25 | Multiplier applied to persisted values on retrieval |
| `HIGHER_WEIGHT` | 0.80 | Weight given to higher value during update |

---

## API Design

### Get Timeout

Retrieve timeout for a command with default fallback. Returns plain number (seconds).

```bash
python3 .plan/execute-script.py plan-marshall:run-config:run-config timeout get \
  --command "ci:pr_checks" \
  --default 300
```

**Parameters**:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--command` | Yes | Command identifier (e.g., `ci:pr_checks`) |
| `--default` | Yes | Default timeout in seconds if no persisted value |

**Logic**:
1. Look up `commands.<command>.timeout_seconds` in run-configuration.json
2. If not found: return `--default` value
3. If found: return `persisted_value * SAFETY_MARGIN`

**Output**: Plain number (e.g., `300`)

### Set Timeout

Update timeout for a command with adaptive weighting.

```bash
python3 .plan/execute-script.py plan-marshall:run-config:run-config timeout set \
  --command "ci:pr_checks" \
  --duration 180
```

**Parameters**:

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--command` | Yes | Command identifier (e.g., `ci:pr_checks`) |
| `--duration` | Yes | Observed duration in seconds |

**Logic**:
1. Look up existing `commands.<command>.timeout_seconds`
2. If not found: write `--duration` directly
3. If found: compute weighted value favoring higher number
   - `higher = max(existing, new_duration)`
   - `lower = min(existing, new_duration)`
   - `result = HIGHER_WEIGHT * higher + (1 - HIGHER_WEIGHT) * lower`

**Output** (TOON format):
```
status	success
command	ci:pr_checks
timeout_seconds	228
previous_seconds	240
source	computed|initial
```

---

## Storage Format

Timeouts are stored in `run-configuration.json` under the command entry:

```json
{
  "version": 1,
  "commands": {
    "ci:pr_checks": {
      "timeout_seconds": 240,
      "last_execution": {
        "date": "2025-12-17",
        "duration_ms": 180000,
        "status": "SUCCESS"
      }
    }
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `timeout_seconds` | integer | Learned timeout value in seconds |

---

## Weighting Algorithm

The update algorithm is **biased towards higher values** to ensure reliability:

```python
def compute_weighted_timeout(existing: int, new_duration: int) -> int:
    """Compute weighted timeout favoring higher value."""
    HIGHER_WEIGHT = 0.80

    higher = max(existing, new_duration)
    lower = min(existing, new_duration)

    return int(HIGHER_WEIGHT * higher + (1 - HIGHER_WEIGHT) * lower)
```

**Examples**:

| Existing | New | Higher | Lower | Result |
|----------|-----|--------|-------|--------|
| 240 | 180 | 240 | 180 | 0.8×240 + 0.2×180 = 228 |
| 180 | 240 | 240 | 180 | 0.8×240 + 0.2×180 = 228 |
| 300 | 300 | 300 | 300 | 0.8×300 + 0.2×300 = 300 |
| 100 | 500 | 500 | 100 | 0.8×500 + 0.2×100 = 420 |

**Rationale**: Operations occasionally complete faster (network conditions, caching, etc.) but rarely exceed the worst-case time. Weighting towards higher values prevents premature timeouts.

---

## Integration with await-until

The timeout subcommand complements `await-until.py` from `script-executor`:

```bash
# Get learned timeout (or default) - outputs plain number
TIMEOUT=$(python3 .plan/execute-script.py plan-marshall:run-config:run-config timeout get \
  --command "ci:pr_checks" --default 300)

# Use in await-until
python3 .plan/execute-script.py plan-marshall:script-executor:await-until poll \
  --check-cmd "gh pr checks 123 --json state" \
  --success-field "status=success" \
  --timeout "$TIMEOUT" \
  --interval 30

# Record actual duration for learning
python3 .plan/execute-script.py plan-marshall:run-config:run-config timeout set \
  --command "ci:pr_checks" --duration 180
```

> **Note**: `await-until.py` has built-in adaptive timeout support via `--command-key`. This API provides an alternative for scripts that need explicit timeout control.

---

## References

- [run-config-format.md](../references/run-config-format.md) - Complete schema documentation
- [wait-pattern.md](../../script-executor/standards/wait-pattern.md) - Awaitility-style synchronous wait
