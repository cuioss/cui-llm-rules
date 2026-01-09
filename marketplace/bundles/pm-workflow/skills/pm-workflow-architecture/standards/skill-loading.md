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
│  │   • Source: Determined during task-plan (resolve-domain-skills)      │  │
│  │   • Example: pm-dev-java:java-core, pm-dev-java:java-cdi             │  │
│  │   • Specific to task's domain and profile                            │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Skill Resolution Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                     SKILL RESOLUTION FLOW                                   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                                                                      │  │
│  │  marshal.json                                                        │  │
│  │  ════════════                                                        │  │
│  │                                                                      │  │
│  │  skill_domains:                                                      │  │
│  │    system:                                                           │  │
│  │      defaults:                                                       │  │
│  │        - plan-marshall:general-development-rules                     │  │
│  │                                                                      │  │
│  │    java:                                                             │  │
│  │      defaults:                                                       │  │
│  │        - pm-dev-java:java-core                                       │  │
│  │      optionals:                                                      │  │
│  │        - pm-dev-java:java-cdi                                        │  │
│  │        - pm-dev-java:java-lombok                                     │  │
│  │      workflow_skills:                                                │  │
│  │        implementation: pm-workflow:task-implementation               │  │
│  │        testing: pm-workflow:task-testing                             │  │
│  │        outline: pm-workflow:solution-outline                         │  │
│  │                                                                      │  │
│  │    javascript:                                                       │  │
│  │      defaults:                                                       │  │
│  │        - pm-dev-frontend:cui-javascript                              │  │
│  │      optionals:                                                      │  │
│  │        - pm-dev-frontend:cui-javascript-unit-testing                 │  │
│  │      workflow_skills:                                                │  │
│  │        implementation: pm-workflow:task-implementation               │  │
│  │        testing: pm-workflow:task-testing                             │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Resolution Commands

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                      RESOLUTION COMMANDS                                    │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                                                                      │  │
│  │  RESOLVE WORKFLOW SKILL (by phase)                                   │  │
│  │  ═════════════════════════════════                                   │  │
│  │                                                                      │  │
│  │  python3 .plan/execute-script.py                                     │  │
│  │    plan-marshall:plan-marshall-config:plan-marshall-config           │  │
│  │    resolve-workflow-skill                                            │  │
│  │    --domain java                                                     │  │
│  │    --phase implementation                                            │  │
│  │                                                                      │  │
│  │  → pm-workflow:task-implementation                                   │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                                                                      │  │
│  │  RESOLVE DOMAIN SKILLS (for task)                                    │  │
│  │  ════════════════════════════════                                    │  │
│  │                                                                      │  │
│  │  python3 .plan/execute-script.py                                     │  │
│  │    plan-marshall:plan-marshall-config:plan-marshall-config           │  │
│  │    resolve-domain-skills                                             │  │
│  │    --domain java                                                     │  │
│  │    --profile implementation                                          │  │
│  │                                                                      │  │
│  │  OUTPUT:                                                             │  │
│  │  ───────                                                             │  │
│  │  domain: java                                                        │  │
│  │  profile: implementation                                             │  │
│  │                                                                      │  │
│  │  defaults:                                                           │  │
│  │    pm-dev-java:java-core: Java patterns, CUI conventions...          │  │
│  │                                                                      │  │
│  │  optionals:                                                          │  │
│  │    pm-dev-java:java-cdi: CDI patterns (@ApplicationScoped...)        │  │
│  │    pm-dev-java:java-lombok: Lombok annotations (@Builder...)         │  │
│  │    pm-dev-java:java-null-safety: JSpecify annotations...             │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

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
│  │   │  • Determined during task-plan phase                       │    │  │
│  │   │  • Listed explicitly in task                               │    │  │
│  │   └────────────────────────────────────────────────────────────┘    │  │
│  │                              │                                       │  │
│  │                              ▼                                       │  │
│  │   ┌────────────────────────────────────────────────────────────┐    │  │
│  │   │  Step 3: Resolve Workflow Skill                            │    │  │
│  │   │                                                            │    │  │
│  │   │  resolve-workflow-skill --domain java --phase impl         │    │  │
│  │   │  → pm-workflow:task-implementation                         │    │  │
│  │   │                                                            │    │  │
│  │   │  • Determines HOW to execute                               │    │  │
│  │   │  • NOT a loadable tier (defines workflow)                  │    │  │
│  │   └────────────────────────────────────────────────────────────┘    │  │
│  │                              │                                       │  │
│  │                              ▼                                       │  │
│  │   ┌────────────────────────────────────────────────────────────┐    │  │
│  │   │  Step 4: Execute Workflow Skill                            │    │  │
│  │   │                                                            │    │  │
│  │   │  Skill: pm-workflow:task-implementation                    │    │  │
│  │   │                                                            │    │  │
│  │   │  • Applies domain skill patterns                           │    │  │
│  │   │  • Implements changes                                      │    │  │
│  │   │  • Runs verification                                       │    │  │
│  │   └────────────────────────────────────────────────────────────┘    │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Plan Phase Skill Selection

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                   PLAN PHASE SKILL SELECTION                                │
│                                                                             │
│  During task-plan, domain skills are selected for each task:                │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                                                                      │  │
│  │  task-plan-agent                                                     │  │
│  │  ═══════════════                                                     │  │
│  │                                                                      │  │
│  │  For each deliverable:                                               │  │
│  │                                                                      │  │
│  │  ┌────────────────────────────────────────────────────────────────┐ │  │
│  │  │                                                                │ │  │
│  │  │  1. Read deliverable metadata                                  │ │  │
│  │  │     → domain: java                                             │ │  │
│  │  │     → profile: implementation                                  │ │  │
│  │  │                                                                │ │  │
│  │  │  2. Resolve domain skills                                      │ │  │
│  │  │     resolve-domain-skills --domain java --profile impl         │ │  │
│  │  │                                                                │ │  │
│  │  │  3. Review output                                              │ │  │
│  │  │     ─────────────────────────────────────────────────────────  │ │  │
│  │  │     defaults:                                                  │ │  │
│  │  │       pm-dev-java:java-core: Java patterns...                  │ │  │
│  │  │                                                                │ │  │
│  │  │     optionals:                                                 │ │  │
│  │  │       pm-dev-java:java-cdi: CDI patterns...   ← SELECT if      │ │  │
│  │  │       pm-dev-java:java-lombok: Lombok...        task uses      │ │  │
│  │  │       pm-dev-java:java-null-safety: JSpecify... these          │ │  │
│  │  │                                                                │ │  │
│  │  │  4. Select skills                                              │ │  │
│  │  │     • ALL defaults automatically included                      │ │  │
│  │  │     • Review optionals based on task content                   │ │  │
│  │  │     • LLM decides which optionals apply                        │ │  │
│  │  │                                                                │ │  │
│  │  │  5. Write to task                                              │ │  │
│  │  │     skills:                                                    │ │  │
│  │  │       - pm-dev-java:java-core                                  │ │  │
│  │  │       - pm-dev-java:java-cdi     ← selected optional           │ │  │
│  │  │                                                                │ │  │
│  │  └────────────────────────────────────────────────────────────────┘ │  │
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
│  │ TYPE          │ WHEN LOADED        │ PURPOSE                          │ │
│  ├───────────────┼────────────────────┼──────────────────────────────────┤ │
│  │               │                    │                                  │ │
│  │ SYSTEM        │ Step 0 (agent)     │ General rules                    │ │
│  │ (Tier 1)      │ Always first       │ Apply to all tasks               │ │
│  │               │                    │ NOT in task.skills               │ │
│  │               │                    │                                  │ │
│  ├───────────────┼────────────────────┼──────────────────────────────────┤ │
│  │               │                    │                                  │ │
│  │ DOMAIN        │ Step 2 (agent)     │ Domain knowledge                 │ │
│  │ (Tier 2)      │ From task.skills   │ Patterns, conventions            │ │
│  │               │                    │ Listed in task                   │ │
│  │               │                    │                                  │ │
│  ├───────────────┼────────────────────┼──────────────────────────────────┤ │
│  │               │                    │                                  │ │
│  │ WORKFLOW      │ Step 3/4           │ HOW to execute                   │ │
│  │               │ Resolved from      │ Workflow logic                   │ │
│  │               │ marshal.json       │ Calls manage-* scripts           │ │
│  │               │                    │                                  │ │
│  ├───────────────┼────────────────────┼──────────────────────────────────┤ │
│  │               │                    │                                  │ │
│  │ EXTENSION     │ By workflow skill  │ Domain-specific additions        │ │
│  │               │ When needed        │ Triage, outline extensions       │ │
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
| `pm-workflow:plan-wf-skill-api` | Contract definitions |
| `plan-marshall:plan-marshall-config` | Resolution commands |
