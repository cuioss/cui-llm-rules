# Skill Loading Pattern

The pm-workflow bundle uses a two-tier skill loading pattern for domain-agnostic execution.

---

## Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                      TWO-TIER SKILL LOADING                                 │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                                                                      │  │
│  │   TIER 1: SYSTEM SKILLS                                              │  │
│  │   ═════════════════════                                              │  │
│  │   • Loaded by agent (Step 0)                                         │  │
│  │   • Source: skill_domains.system.defaults                            │  │
│  │   • Example: plan-marshall:general-development-rules                 │  │
│  │   • Applies to ALL tasks regardless of domain                        │  │
│  │                                                                      │  │
│  │   ─────────────────────────────────────────────────────────────────  │  │
│  │                                                                      │  │
│  │   TIER 2: DOMAIN SKILLS                                              │  │
│  │   ══════════════════════                                             │  │
│  │   • Loaded from task.skills                                          │  │
│  │   • Source: module.proposed_skill_domains (from architecture)        │  │
│  │   • Example: pm-dev-java:java-core, pm-dev-java:java-cdi             │  │
│  │   • Selected during solution-outline, propagated through tasks       │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Skill Origin Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                      SKILL ORIGIN FLOW                                      │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                                                                      │  │
│  │  analyze-project-architecture                                        │  │
│  │  ════════════════════════════                                        │  │
│  │                                                                      │  │
│  │  Each module has proposed_skill_domains:                             │  │
│  │                                                                      │  │
│  │  modules:                                                            │  │
│  │    oauth-sheriff-core:                                               │  │
│  │      responsibility: "JWT validation logic"                          │  │
│  │      proposed_skill_domains: [java]                                  │  │
│  │                                                                      │  │
│  │    oauth-sheriff-quarkus:                                            │  │
│  │      responsibility: "Quarkus CDI integration"                       │  │
│  │      proposed_skill_domains: [java, java-cdi-quarkus]                │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                              │                                              │
│                              ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                                                                      │  │
│  │  solution-outline (OUTLINE phase)                                    │  │
│  │  ════════════════════════════════                                    │  │
│  │                                                                      │  │
│  │  1. Query architecture for modules                                   │  │
│  │  2. Select module for each deliverable                               │  │
│  │  3. Module brings proposed_skill_domains                             │  │
│  │                                                                      │  │
│  │  Deliverable output:                                                 │  │
│  │  ───────────────────                                                 │  │
│  │  ### 1. Add IssuerValidator class                                    │  │
│  │  **Module**: oauth-sheriff-core                                      │  │
│  │  **Domain**: java                                                    │  │
│  │  **Skills**: [java-core, java-cdi] ← from module context             │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                              │                                              │
│                              ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                                                                      │  │
│  │  task-plan (PLAN phase)                                              │  │
│  │  ══════════════════════                                              │  │
│  │                                                                      │  │
│  │  Propagates skills from deliverable to task:                         │  │
│  │                                                                      │  │
│  │  TASK-001.toon:                                                      │  │
│  │    deliverables: [1]                                                 │  │
│  │    module: oauth-sheriff-core                                        │  │
│  │    domain: java                                                      │  │
│  │    profile: implementation                                           │  │
│  │    skills:                                                           │  │
│  │      - pm-dev-java:java-core      ← inherited from deliverable       │  │
│  │      - pm-dev-java:java-cdi       ← inherited from deliverable       │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                              │                                              │
│                              ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                                                                      │  │
│  │  task-execute-agent (EXECUTE phase)                                  │  │
│  │  ══════════════════════════════════                                  │  │
│  │                                                                      │  │
│  │  Loads skills from task.skills array (no resolution needed)          │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Insight**: Skills are associated with modules in architecture data. Module selection during outline phase determines which skills apply. No separate resolution API call needed.

---

## Execute Phase Skill Loading

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                  EXECUTE PHASE SKILL LOADING                                │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                                                                      │  │
│  │   task-execute-agent                                                 │  │
│  │   ═══════════════════                                                │  │
│  │                                                                      │  │
│  │   ┌────────────────────────────────────────────────────────────┐    │  │
│  │   │  Step 0: Load System Skills (Tier 1)                       │    │  │
│  │   │                                                            │    │  │
│  │   │  Skill: plan-marshall:general-development-rules            │    │  │
│  │   │                                                            │    │  │
│  │   │  • Always loaded                                           │    │  │
│  │   │  • Agent's skills: field in frontmatter                    │    │  │
│  │   │  • NOT visible in task.skills                              │    │  │
│  │   └────────────────────────────────────────────────────────────┘    │  │
│  │                              │                                       │  │
│  │                              ▼                                       │  │
│  │   ┌────────────────────────────────────────────────────────────┐    │  │
│  │   │  Step 1: Read Task                                         │    │  │
│  │   │                                                            │    │  │
│  │   │  manage-tasks get --plan-id X --task-number 1              │    │  │
│  │   │  → module: oauth-sheriff-core                              │    │  │
│  │   │  → domain: java                                            │    │  │
│  │   │  → profile: implementation                                 │    │  │
│  │   │  → skills: [pm-dev-java:java-core, pm-dev-java:java-cdi]   │    │  │
│  │   └────────────────────────────────────────────────────────────┘    │  │
│  │                              │                                       │  │
│  │                              ▼                                       │  │
│  │   ┌────────────────────────────────────────────────────────────┐    │  │
│  │   │  Step 2: Load Domain Skills (Tier 2)                       │    │  │
│  │   │                                                            │    │  │
│  │   │  For each skill in task.skills:                            │    │  │
│  │   │    Skill: pm-dev-java:java-core                            │    │  │
│  │   │    Skill: pm-dev-java:java-cdi                             │    │  │
│  │   │                                                            │    │  │
│  │   │  • Loaded AFTER system skills                              │    │  │
│  │   │  • Already resolved during outline/plan phases             │    │  │
│  │   │  • Listed explicitly in task                               │    │  │
│  │   └────────────────────────────────────────────────────────────┘    │  │
│  │                              │                                       │  │
│  │                              ▼                                       │  │
│  │   ┌────────────────────────────────────────────────────────────┐    │  │
│  │   │  Step 3: Load Workflow Skill                               │    │  │
│  │   │                                                            │    │  │
│  │   │  Based on task.profile:                                    │    │  │
│  │   │    implementation → pm-workflow:task-implementation        │    │  │
│  │   │    testing → pm-workflow:task-testing                      │    │  │
│  │   │                                                            │    │  │
│  │   │  • Determines HOW to execute                               │    │  │
│  │   │  • Applies domain skill patterns                           │    │  │
│  │   └────────────────────────────────────────────────────────────┘    │  │
│  │                              │                                       │  │
│  │                              ▼                                       │  │
│  │   ┌────────────────────────────────────────────────────────────┐    │  │
│  │   │  Step 4: Execute                                           │    │  │
│  │   │                                                            │    │  │
│  │   │  • Implements changes using domain patterns                │    │  │
│  │   │  • Runs verification                                       │    │  │
│  │   │  • Tracks file changes                                     │    │  │
│  │   └────────────────────────────────────────────────────────────┘    │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Skill Type Summary

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                       SKILL TYPE SUMMARY                                    │
│                                                                             │
│  ┌───────────────┬────────────────────┬──────────────────────────────────┐ │
│  │ TYPE          │ SOURCE             │ PURPOSE                          │ │
│  ├───────────────┼────────────────────┼──────────────────────────────────┤ │
│  │               │                    │                                  │ │
│  │ SYSTEM        │ Agent frontmatter  │ General rules                    │ │
│  │ (Tier 1)      │ Always first       │ Apply to all tasks               │ │
│  │               │                    │ NOT in task.skills               │ │
│  │               │                    │                                  │ │
│  ├───────────────┼────────────────────┼──────────────────────────────────┤ │
│  │               │                    │                                  │ │
│  │ DOMAIN        │ Architecture →     │ Domain knowledge                 │ │
│  │ (Tier 2)      │ Module →           │ Patterns, conventions            │ │
│  │               │ Deliverable →      │ Listed in task.skills            │ │
│  │               │ Task               │                                  │ │
│  │               │                    │                                  │ │
│  ├───────────────┼────────────────────┼──────────────────────────────────┤ │
│  │               │                    │                                  │ │
│  │ WORKFLOW      │ task.profile       │ HOW to execute                   │ │
│  │               │ (impl/testing)     │ Workflow logic                   │ │
│  │               │                    │ Calls manage-* scripts           │ │
│  │               │                    │                                  │ │
│  ├───────────────┼────────────────────┼──────────────────────────────────┤ │
│  │               │                    │                                  │ │
│  │ EXTENSION     │ config.toon.domains│ Domain-specific additions        │ │
│  │               │ Finalize phase     │ Triage extensions                │ │
│  │               │                    │                                  │ │
│  └───────────────┴────────────────────┴──────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Extensions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                          EXTENSIONS                                         │
│                                                                             │
│  Extensions add domain-specific knowledge without replacing workflow skills │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                                                                      │  │
│  │  EXTENSION TYPES:                                                    │  │
│  │                                                                      │  │
│  │  ┌──────────────┬─────────┬────────────────────────────────────────┐│  │
│  │  │ TYPE         │ PHASE   │ PURPOSE                                ││  │
│  │  ├──────────────┼─────────┼────────────────────────────────────────┤│  │
│  │  │ outline      │ outline │ Domain detection, deliverable patterns ││  │
│  │  │ triage       │ finalize│ Finding decision-making (fix/suppress) ││  │
│  │  └──────────────┴─────────┴────────────────────────────────────────┘│  │
│  │                                                                      │  │
│  │  RESOLUTION:                                                         │  │
│  │                                                                      │  │
│  │  python3 .plan/execute-script.py                                     │  │
│  │    plan-marshall:plan-marshall-config:plan-marshall-config           │  │
│  │    resolve-workflow-skill-extension                                  │  │
│  │    --domain java                                                     │  │
│  │    --type triage                                                     │  │
│  │                                                                      │  │
│  │  → pm-dev-java:java-triage                                           │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [agents.md](agents.md) | Agent skill loading steps |
| [phases.md](phases.md) | When each skill type is used |
| `plan-marshall:analyze-project-architecture` | Source of module.proposed_skill_domains |
| `pm-workflow:solution-outline` | Where module/skills are selected |
| `pm-workflow:plan-wf-skill-api` | Contract definitions |
