# Architecture Compliance Scoring

Quantifiable metrics for marketplace architecture compliance.

## Skill Self-Containment Score

**Base Score**: 100 points

**Deductions**:
- External file reference in workflow (`Read: ../../../../`): **-20 points each**
- External file reference in documentation only: **-10 points each**
- Absolute path reference (`~/` or `/`): **-20 points each**
- Missing internal file (referenced but doesn't exist): **-10 points each**
- Cross-skill file access (`../other-skill/`): **-15 points each**

**Formula**:
```
score = 100
score -= (workflow_external_refs × 20)
score -= (doc_external_refs × 10)
score -= (absolute_paths × 20)
score -= (missing_files × 10)
score -= (cross_skill_access × 15)
score = max(0, score)  # minimum 0
```

**Thresholds**:
- **90-100**: ✅ Excellent - Fully self-contained
- **75-89**: ⚠️ Good - Minor external references
- **60-74**: ⚠️ Fair - Moderate violations
- **< 60**: ❌ Poor - Major violations

**Example Calculation**:
```
Skill has:
- 2 external file refs in workflow
- 1 absolute path
- 0 missing files

Score = 100 - (2 × 20) - (1 × 20) = 100 - 40 - 20 = 40/100 (Poor)
```

## Agent Skill Usage Score

**Applicability**: Only for agents that use standards

**Detection**:
```bash
# Agent uses standards if mentions:
grep -qi "standard\|pattern\|guideline\|best practice" agent.md
```

**Base Score**: 100 points (if applicable)

**Deductions**:
- Missing `Skill` in tools list: **-30 points**
- No `Skill:` invocations in workflow: **-30 points**
- Direct file reference (each): **-20 points**
- `Skill` in tools but never used: **-10 points**

**Formula**:
```
IF agent_uses_standards:
  score = 100
  if "Skill" not in tools: score -= 30
  if no_skill_invocations: score -= 30
  score -= (direct_file_refs × 20)
  if skill_in_tools_but_unused: score -= 10
  score = max(0, score)
ELSE:
  score = N/A  # Simple utility agent
```

**Thresholds** (if applicable):
- **90-100**: ✅ Excellent - Proper skill usage
- **75-89**: ⚠️ Good - Minor issues
- **60-74**: ⚠️ Fair - Some violations
- **< 60**: ❌ Poor - Major violations
- **N/A**: ℹ️ Simple utility (doesn't use standards)

**Example Calculation**:
```
Agent references "standards" but:
- Missing Skill in tools: -30
- No Skill: invocations: -30
- 1 direct file ref: -20

Score = 100 - 30 - 30 - 20 = 20/100 (Poor)
```

## Command Skill Usage Score

**Similar to Agent Scoring**:
- Commands that orchestrate workflows may invoke skills
- Commands that do diagnostics often invoke skills
- Scoring identical to agent skill usage score

## Bundle Architecture Score

**Components**:
- Skills in bundle (self-containment scores)
- Agents in bundle (skill usage scores)
- Commands in bundle (skill usage scores)

**Formula**:
```
skill_avg = sum(skill_scores) / count(skills)
agent_avg = sum(agent_scores) / count(agents)  # skip N/A scores
command_avg = sum(command_scores) / count(commands)  # skip N/A scores

bundle_score = (skill_avg × 0.6) + (agent_avg × 0.3) + (command_avg × 0.1)
```

**Weights Rationale**:
- Skills: 60% (most critical - must be self-contained for distribution)
- Agents: 30% (important - proper patterns matter)
- Commands: 10% (least critical - often utilities)

**Thresholds**:
- **90-100**: ✅ Excellent - Marketplace ready
- **75-89**: ⚠️ Good - Minor improvements needed
- **60-74**: ⚠️ Fair - Moderate work required
- **< 60**: ❌ Poor - Significant issues

**Example Calculation**:
```
Bundle has:
- 2 skills: 100/100, 80/100 → avg = 90
- 3 agents: 100/100, 90/100, N/A → avg = 95
- 1 command: 100/100 → avg = 100

bundle_score = (90 × 0.6) + (95 × 0.3) + (100 × 0.1)
             = 54 + 28.5 + 10
             = 92.5/100 (Excellent)
```

## Marketplace Overall Score

**Formula**:
```
marketplace_score = sum(bundle_scores) / count(bundles)
```

**Interpretation**:
- **90-100**: ✅ Marketplace ready for distribution
- **75-89**: ⚠️ Some bundles need work
- **60-74**: ⚠️ Moderate marketplace issues
- **< 60**: ❌ Not ready for marketplace

## Score Reporting Format

### Individual Component Report

```
Component: cui-java-core (skill)
Self-Containment Score: 95/100 ⭐⭐⭐⭐⭐ Excellent

Deductions:
- 1 documentation external ref (-5 points)

Status: ✅ Marketplace ready
```

### Bundle Report

```
Bundle: cui-maven
Architecture Score: 92/100 ⭐⭐⭐⭐⭐ Excellent

Skills (1):
- cui-maven-rules: 100/100
Average: 100/100

Agents (2):
- maven-project-builder: 95/100
- maven-builder: 90/100
Average: 92.5/100

Commands (1):
- cui-build-and-verify: 90/100
Average: 90/100

Weighted Score: (100 × 0.6) + (92.5 × 0.3) + (90 × 0.1) = 92/100

Status: ✅ Marketplace ready
```

### Marketplace Report

```
Marketplace Overall: 88/100 ⭐⭐⭐⭐ Good

Bundle Scores:
- cui-maven: 92/100
- cui-documentation-standards: 90/100
- cui-plugin-development-tools: 88/100
- cui-pull-request-workflow: 87/100
- cui-issue-implementation: 85/100
- cui-utility-commands: 85/100
- cui-java-expert: 90/100

Average: 88.1/100

Status: ⚠️ Minor improvements recommended
```

## Score Improvement Priorities

### Priority 1: Fix Critical Violations (< 60)

Components with critical violations:
1. Identify external file references
2. Internalize content to standards/
3. Re-score to verify improvement

**Impact**: Largest score improvement

### Priority 2: Fix Bundle Issues (60-74)

Bundles with fair scores:
1. Fix skill self-containment
2. Fix agent skill usage patterns
3. Re-score bundle

**Impact**: Moderate improvement

### Priority 3: Polish Excellence (75-89)

Good components:
1. Fix minor documentation refs
2. Remove unused tools
3. Clean up edge cases

**Impact**: Small improvement to reach excellent

## Integration Points

Scoring used in:

- **/cui-diagnose-skills**: Calculate skill self-containment score
- **/cui-diagnose-agents**: Calculate agent skill usage score
- **/cui-diagnose-bundle**: Calculate bundle architecture score
- **Marketplace dashboard**: Overall marketplace health

All commands invoke `Skill: cui-marketplace-architecture` to load consistent scoring criteria.
