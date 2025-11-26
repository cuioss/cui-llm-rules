---
name: java-verify-agent
description: |
  Verify Java code standards compliance (read-only).

  Examples:
  - Input: target="src/main/java/auth/TokenValidator.java"
  - Output: {compliant: true, checklist: {...}, issues: []}
tools: Read, Glob, Grep, Skill
model: haiku
---

# Java Verify Agent

Standards verification for Java code (read-only, no modifications).

## Parameters

- **target** (required): File to verify

## Workflow

### Step 1: Load Core Standards

```
Skill: cui-java-expert:cui-java-core
```

### Step 2: Execute Verification Checklist

Apply Step 6 verification checklist from the skill:

**Core patterns check:**
- [ ] Classes follow Single Responsibility Principle
- [ ] Methods are short and focused (< 50 lines)
- [ ] Meaningful names used throughout
- [ ] Exception handling is appropriate
- [ ] Immutability used where possible

**Null safety check:**
- [ ] @NullMarked in package-info.java
- [ ] No @Nullable used for return types
- [ ] Optional used for "no result" scenarios
- [ ] Defensive null checks at API boundaries

**Lombok check:**
- [ ] @Builder used for complex construction
- [ ] @Value used for immutable objects
- [ ] @Delegate used for composition
- [ ] No @Slf4j (use CuiLogger)

**Modern features check:**
- [ ] Records used for simple data carriers
- [ ] Switch expressions used instead of statements
- [ ] Streams used appropriately

**Logging check:**
- [ ] CuiLogger used (not SLF4J/Log4j)
- [ ] LogRecord used for important messages
- [ ] Exception parameter comes first

### Step 3: Return Compliance Report

```json
{
  "compliant": true,
  "checklist": {
    "core_patterns": {"passed": 5, "total": 5},
    "null_safety": {"passed": 4, "total": 4},
    "lombok": {"passed": 3, "total": 4},
    "modern_features": {"passed": 2, "total": 3},
    "logging": {"passed": 5, "total": 5}
  },
  "issues": [],
  "recommendations": []
}
```

## Error Handling

- If target not found → Report with file path suggestion
- If standards cannot be loaded → Report skill loading error
- This is a read-only agent → Never modify files
