# Wait Pattern Specification

Synchronous polling utility for blocking until an async operation completes, inspired by the [Awaitility](http://www.awaitility.org/) JUnit library.

---

## Overview

The wait pattern provides a **synchronous blocking** mechanism that:
- Polls a condition until satisfied or timeout
- Returns immediately when condition is met (early return)
- Uses generous outer timeouts with configurable poll intervals
- Supports adaptive timeout learning from execution history

```
                    WAIT PATTERN FLOW

    ┌─────────────────────────────────────────────────────┐
    │                                                     │
    │   Caller (Skill/Script)                             │
    │   ┌───────────────────────────────────────────┐     │
    │   │  await_until(                             │     │
    │   │    condition = check_ci_status,           │     │
    │   │    timeout = 300s,                        │     │
    │   │    poll_interval = 30s                    │     │
    │   │  )                                        │     │
    │   └───────────────────────────────────────────┘     │
    │                       │                             │
    │                       ▼                             │
    │   ┌───────────────────────────────────────────┐     │
    │   │  Wait Utility (BLOCKS)                    │     │
    │   │                                           │     │
    │   │  ┌─────────────────────────────────────┐  │     │
    │   │  │ Poll Loop                           │  │     │
    │   │  │                                     │  │     │
    │   │  │  1. Call condition()                │  │     │
    │   │  │  2. If satisfied → RETURN SUCCESS   │  │     │
    │   │  │  3. If timeout → RETURN TIMEOUT     │  │     │
    │   │  │  4. Sleep(poll_interval)            │  │     │
    │   │  │  5. GOTO 1                          │  │     │
    │   │  │                                     │  │     │
    │   │  └─────────────────────────────────────┘  │     │
    │   └───────────────────────────────────────────┘     │
    │                       │                             │
    │                       ▼                             │
    │   ┌───────────────────────────────────────────┐     │
    │   │  Result: {status, duration, polls, data}  │     │
    │   └───────────────────────────────────────────┘     │
    │                                                     │
    └─────────────────────────────────────────────────────┘
```

---

## Design Principles

### 1. Synchronous Blocking

The wait utility **blocks the calling script** until:
- The condition is satisfied (success)
- The timeout is reached (timeout)
- An error occurs (failure)

This is intentional - the caller wants to wait for the operation to complete before proceeding.

### 2. Early Return

If the condition is satisfied on the first poll (or any subsequent poll), return immediately. Don't wait for the full timeout.

```
    Time ──────────────────────────────────────────────▶

    Timeout: 300s
    Poll interval: 30s

    ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
    │ 0s  │ 30s │ 60s │ 90s │120s │150s │180s │...  │
    └──┬──┴──┬──┴──┬──┴─────┴─────┴─────┴─────┴─────┘
       │     │     │
       ▼     ▼     ▼
    PENDING PENDING SUCCESS ← Returns here (60s)
                             Not at 300s timeout
```

### 3. Generous Outer Timeout

The caller should provide a **generous timeout** that allows for:
- Normal operation completion
- Network delays
- Queue times
- Retry scenarios

The inner poll interval handles the "check frequently" aspect.

### 4. Condition Function

The condition is a **callable** that returns:
- `True` / `"success"` - condition satisfied, return immediately
- `False` / `"pending"` - not yet satisfied, continue polling
- `"failure"` - permanent failure, stop polling and return error

---

## State Machine

```
                        WAIT STATE MACHINE

    ┌──────────────────────────────────────────────────────────┐
    │                                                          │
    │                    ┌─────────┐                           │
    │                    │  START  │                           │
    │                    └────┬────┘                           │
    │                         │                                │
    │                         ▼                                │
    │                  ┌──────────────┐                        │
    │          ┌───────│   POLLING    │◀──────────┐            │
    │          │       └──────┬───────┘           │            │
    │          │              │                   │            │
    │          │              ▼                   │            │
    │          │       ┌──────────────┐           │            │
    │          │       │    CHECK     │           │            │
    │          │       │  CONDITION   │           │            │
    │          │       └──────┬───────┘           │            │
    │          │              │                   │            │
    │          │     ┌────────┼────────┐          │            │
    │          │     │        │        │          │            │
    │          │     ▼        ▼        ▼          │            │
    │          │  SUCCESS  PENDING  FAILURE       │            │
    │          │     │        │        │          │            │
    │          │     │        │        │          │            │
    │          │     │        ▼        │          │            │
    │          │     │  ┌──────────┐   │          │            │
    │          │     │  │ TIMEOUT? │   │          │            │
    │          │     │  └────┬─────┘   │          │            │
    │          │     │    NO │ YES     │          │            │
    │          │     │       │  │      │          │            │
    │          │     │       │  │      │          │            │
    │          │     │  ┌────┘  │      │          │            │
    │          │     │  │       │      │          │            │
    │          │     │  │       ▼      │          │            │
    │          │     │  │   ┌───────┐  │          │            │
    │          │     │  │   │TIMEOUT│  │          │            │
    │          │     │  │   └───┬───┘  │          │            │
    │          │     │  │       │      │          │            │
    │          │     │  │       │      │          │            │
    │          │     │  │ SLEEP │      │          │            │
    │          │     │  └───────┼──────┘          │            │
    │          │     │          │                 │            │
    │          │     │          └─────────────────┘            │
    │          │     │                                         │
    │          │     ▼                                         │
    │          │  ┌───────┐                                    │
    │          │  │SUCCESS│                                    │
    │          │  └───────┘                                    │
    │          │                                               │
    │          ▼                                               │
    │       ┌───────┐                                          │
    │       │FAILURE│                                          │
    │       └───────┘                                          │
    │                                                          │
    └──────────────────────────────────────────────────────────┘
```

---

## API Design (Awaitility-Style)

### Python Script API

```python
from await_util import await_until, ConditionResult

# Basic usage
result = await_until(
    condition=lambda: check_ci_status(pr_number),
    timeout_seconds=300,
    poll_interval_seconds=30,
    description="CI checks to pass"
)

# With condition result object
def check_build_status():
    status = get_build_status()
    if status == "success":
        return ConditionResult.success(data={"build_id": 123})
    elif status == "failed":
        return ConditionResult.failure(error="Build failed")
    else:
        return ConditionResult.pending(message="Build in progress")

result = await_until(
    condition=check_build_status,
    timeout_seconds=600,
    poll_interval_seconds=60
)
```

### CLI Script API

The CLI provides two modes: **explicit** (manual timeout/interval) and **adaptive** (managed via run-config).

```bash
# ADAPTIVE MODE (recommended): timeout/interval managed internally via run-config
# The script fetches timeout from run-config and updates execution history after completion
python3 .plan/execute-script.py plan-marshall:script-executor:await-until poll \
    --check-cmd "python3 .plan/execute-script.py pm-ci-integration:ci-operations:ci-provider-api ci check-status --pr-number 123" \
    --success-field "status=success" \
    --failure-field "status=failure" \
    --command-key "ci:pr_checks"

# EXPLICIT MODE: manual timeout/interval (useful for one-off operations)
python3 .plan/execute-script.py plan-marshall:script-executor:await-until poll \
    --check-cmd "python3 .plan/execute-script.py pm-ci-integration:ci-operations:ci-provider-api ci check-status --pr-number 123" \
    --success-field "status=success" \
    --timeout 300 \
    --interval 30

# Wait for Sonar analysis completion
python3 .plan/execute-script.py plan-marshall:script-executor:await-until poll \
    --check-cmd "python3 .plan/execute-script.py pm-ci-integration:ci-operations:ci-provider-api sonar get-status --pr-number 123" \
    --success-field "qualityGate=OK" \
    --failure-field "qualityGate=ERROR" \
    --command-key "ci:sonar_analysis"
```

### Command-Key Naming Convention

The `--command-key` parameter identifies the operation in run-config for timeout learning:

| Key Pattern | Description | Example |
|-------------|-------------|---------|
| `ci:<operation>` | CI/CD operations | `ci:pr_checks`, `ci:sonar_analysis` |
| `build:<type>` | Build operations | `build:maven_verify`, `build:npm_test` |
| `deploy:<env>` | Deployment waits | `deploy:staging`, `deploy:production` |

The key is used to store/retrieve execution history in `run-configuration.json` under `commands.<key>`.

---

## Timeout Strategy

```
                    TIMEOUT HIERARCHY

    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │  Caller Script (e.g., plan-finalize)                    │
    │  ┌───────────────────────────────────────────────────┐  │
    │  │                                                   │  │
    │  │  GENEROUS OUTER TIMEOUT: 600s (10 min)            │  │
    │  │  ┌───────────────────────────────────────────┐    │  │
    │  │  │                                           │    │  │
    │  │  │  await_until(timeout=600s, interval=30s)  │    │  │
    │  │  │                                           │    │  │
    │  │  │  Poll 1 (0s)    → PENDING                 │    │  │
    │  │  │  Poll 2 (30s)   → PENDING                 │    │  │
    │  │  │  Poll 3 (60s)   → PENDING                 │    │  │
    │  │  │  Poll 4 (90s)   → SUCCESS ← Early return  │    │  │
    │  │  │                                           │    │  │
    │  │  │  Actual duration: 90s (not 600s)          │    │  │
    │  │  │                                           │    │  │
    │  │  └───────────────────────────────────────────┘    │  │
    │  │                                                   │  │
    │  └───────────────────────────────────────────────────┘  │
    │                                                         │
    └─────────────────────────────────────────────────────────┘

    Key insight:
    - Outer timeout = maximum wait (generous, accounts for edge cases)
    - Poll interval = how often to check (frequent, for early return)
    - Actual duration = when condition is satisfied (usually much less)
```

### Recommended Timeout Values

| Operation | Timeout | Poll Interval | Rationale |
|-----------|---------|---------------|-----------|
| PR checks | 300s | 30s | CI typically completes in 2-5 min |
| Full pipeline | 900s | 60s | Complex builds may take longer |
| Sonar analysis | 180s | 20s | Usually quick, but queued |
| PR merge | 60s | 10s | Fast operation, quick feedback |

---

## Adaptive Timeout Learning

The wait utility can learn from execution history to provide better timeout defaults.

```
                ADAPTIVE TIMEOUT LEARNING

    ┌────────────────────────────────────────────────────────┐
    │                                                        │
    │  Execution 1: PR Checks                                │
    │  ┌──────────────────────────────────────────────────┐  │
    │  │ Timeout: 300s                                    │  │
    │  │ Actual:  120s                                    │  │
    │  │ Status:  SUCCESS                                 │  │
    │  └──────────────────────────────────────────────────┘  │
    │                       │                                │
    │                       ▼                                │
    │  ┌──────────────────────────────────────────────────┐  │
    │  │ run-configuration.json                           │  │
    │  │ commands.ci:pr_checks.last_execution:            │  │
    │  │   duration_ms: 120000                            │  │
    │  │   status: SUCCESS                                │  │
    │  └──────────────────────────────────────────────────┘  │
    │                       │                                │
    │                       ▼                                │
    │  Execution 2: PR Checks                                │
    │  ┌──────────────────────────────────────────────────┐  │
    │  │ Adaptive timeout: 120s * 1.5 = 180s              │  │
    │  │ (with minimum of 60s, maximum of 600s)           │  │
    │  └──────────────────────────────────────────────────┘  │
    │                                                        │
    └────────────────────────────────────────────────────────┘
```

### Learning Algorithm

```python
def calculate_adaptive_timeout(command_key: str) -> int:
    """Calculate timeout based on execution history."""
    history = get_execution_history(command_key)

    if not history:
        return DEFAULT_TIMEOUT  # No history, use default

    last_duration = history.last_execution.duration_ms

    # Apply buffer factor (1.5x by default)
    adaptive_timeout = last_duration * BUFFER_FACTOR

    # Clamp to bounds
    return clamp(
        adaptive_timeout,
        minimum=MINIMUM_TIMEOUT,  # 60s
        maximum=MAXIMUM_TIMEOUT   # 600s
    )
```

---

## Integration with run-config

When `--command-key` is provided, the await-until script **internally manages** all timeout/interval configuration:

1. **Before polling**: Fetches timeout from run-config history (if available)
2. **After completion**: Updates run-config with execution result for learning

The caller does NOT need to manage run-config separately - it's all handled internally.

```
                CONFIG INTEGRATION (INTERNAL)

    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │  await-until.py --command-key "ci:pr_checks"            │
    │                                                         │
    │  ┌───────────────────────────────────────────────────┐  │
    │  │ 1. INTERNAL: Fetch timeout from run-config        │  │
    │  │    commands.ci:pr_checks.last_execution           │  │
    │  │    → Found: duration_ms=120000                    │  │
    │  │    → Adaptive timeout: 120000 * 1.5 = 180000ms    │  │
    │  └───────────────────────────────────────────────────┘  │
    │                         │                               │
    │                         ▼                               │
    │  ┌───────────────────────────────────────────────────┐  │
    │  │ 2. Execute poll loop with adaptive timeout        │  │
    │  │    timeout=180s, interval=30s (default)           │  │
    │  │    ... polling condition ...                      │  │
    │  │    Result: SUCCESS after 95s                      │  │
    │  └───────────────────────────────────────────────────┘  │
    │                         │                               │
    │                         ▼                               │
    │  ┌───────────────────────────────────────────────────┐  │
    │  │ 3. INTERNAL: Update run-config with result        │  │
    │  │    commands.ci:pr_checks.last_execution:          │  │
    │  │      date: "2025-01-15"                           │  │
    │  │      duration_ms: 95000                           │  │
    │  │      status: "SUCCESS"                            │  │
    │  └───────────────────────────────────────────────────┘  │
    │                         │                               │
    │                         ▼                               │
    │  ┌───────────────────────────────────────────────────┐  │
    │  │ 4. Output result (TOON format)                    │  │
    │  │    status=success, duration_ms=95000, ...         │  │
    │  └───────────────────────────────────────────────────┘  │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
```

### run-configuration.json Structure

```json
{
  "commands": {
    "ci:pr_checks": {
      "last_execution": {
        "date": "2025-01-15",
        "duration_ms": 95000,
        "status": "SUCCESS"
      }
    },
    "ci:sonar_analysis": {
      "last_execution": {
        "date": "2025-01-15",
        "duration_ms": 45000,
        "status": "SUCCESS"
      }
    }
  }
}
```

---

## Output Contract

Output uses TOON format (Tab-delimited Object Notation):

```
status	success
duration_ms	95000
polls	4
timeout_used_ms	180000
timeout_source	adaptive
command_key	ci:pr_checks
final_result.state	completed
final_result.conclusion	success
```

### Status Values

| Status | Description |
|--------|-------------|
| `success` | Condition satisfied within timeout |
| `timeout` | Timeout reached without condition being satisfied |
| `failure` | Permanent failure detected (check returned failure state) |

### Fields

| Field | Description |
|-------|-------------|
| `status` | Result status (success/timeout/failure) |
| `duration_ms` | Actual wait duration in milliseconds |
| `polls` | Number of condition checks performed |
| `timeout_used_ms` | Timeout value used (explicit or adaptive) |
| `timeout_source` | Source of timeout: `explicit`, `adaptive`, or `default` |
| `command_key` | The command key used (if adaptive mode) |
| `final_result.*` | Flattened fields from the last condition check |
| `error` | Error message (only present on failure) |

---

## Example: CI Wait Flow

```
                    CI WAIT EXAMPLE

    ┌─────────────────────────────────────────────────────────┐
    │                                                         │
    │  plan-finalize skill                                    │
    │  ┌───────────────────────────────────────────────────┐  │
    │  │ 1. Create PR                                      │  │
    │  │    gh pr create --title "..." --body "..."        │  │
    │  │    → PR 123 created                               │  │
    │  └───────────────────────────────────────────────────┘  │
    │                         │                               │
    │                         ▼                               │
    │  ┌───────────────────────────────────────────────────┐  │
    │  │ 2. Wait for CI                                    │  │
    │  │                                                   │  │
    │  │    await_until(                                   │  │
    │  │      condition=lambda: check_pr_status(123),      │  │
    │  │      timeout=300,                                 │  │
    │  │      interval=30                                  │  │
    │  │    )                                              │  │
    │  │                                                   │  │
    │  │    Poll 1 (0s):   "pending" - CI queued           │  │
    │  │    Poll 2 (30s):  "pending" - CI running          │  │
    │  │    Poll 3 (60s):  "pending" - CI running          │  │
    │  │    Poll 4 (90s):  "success" - CI passed! ✓        │  │
    │  │                                                   │  │
    │  │    → Returns immediately at 90s                   │  │
    │  └───────────────────────────────────────────────────┘  │
    │                         │                               │
    │                         ▼                               │
    │  ┌───────────────────────────────────────────────────┐  │
    │  │ 3. Continue with PR workflow                      │  │
    │  │    - Check for reviews                            │  │
    │  │    - Merge if approved                            │  │
    │  └───────────────────────────────────────────────────┘  │
    │                                                         │
    └─────────────────────────────────────────────────────────┘
```

---

## Implementation Tasks

See [pm-ci-integration.md](../../../../../.plan/refactor-plan-execution/plans/pm-ci-integration.md) Phase C:

- [x] **C1.1** This document (wait-pattern.md)
- [x] **C1.2** Create `scripts/await-until.py` - Synchronous wait with polling, internal run-config management
- [x] **C1.3** Update `SKILL.md` with wait pattern documentation as optional loading
- [x] **C1.4** Create tests for wait pattern
- [x] **C1.5** Update `run-config/references/run-config-format.md` - Document command-key storage format for adaptive timeouts
- [x] **C1.6** Run all tests: `python3 test/run-tests.py`
- [x] **C1.7** Update `.plan/refactor-plan-execution/` documents - Phase C tasks marked complete

> **Note**: No extensions to `run-config.py` are needed - the await-until.py script directly uses `json-file-operations` to read/update run-configuration.json internally.

> **Post-Implementation**: Remove this "Implementation Tasks" section once all tasks are complete - this specification should document the API, not track implementation progress.

---

## References

- [Awaitility](http://www.awaitility.org/) - Java DSL for synchronous testing
- [run-config SKILL.md](../../run-config/SKILL.md) - Execution history storage
