# Plugin-Doctor Dependency Analysis

Visual analysis of call relationships and dependencies for `/plugin-doctor` command.

## Master Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           /plugin-doctor COMMAND                                │
│                      (plugin-doctor.md - Thin Wrapper)                          │
└───────────────────────────────────┬─────────────────────────────────────────────┘
                                    │
                                    │ Skill: pm-plugins:plugin-doctor
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           PLUGIN-DOCTOR SKILL                                   │
│                              (SKILL.md)                                         │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                    WORKFLOW DECISION TREE                               │   │
│  │                                                                         │   │
│  │   scope=agents ─────────────► Workflow 1: doctor-agents                 │   │
│  │   scope=commands ───────────► Workflow 2: doctor-commands               │   │
│  │   scope=skills ─────────────► Workflow 3: doctor-skills                 │   │
│  │   scope=metadata ───────────► Workflow 4: doctor-metadata               │   │
│  │   scope=scripts ────────────► Workflow 5: doctor-scripts                │   │
│  │   scope=skill-content ──────► Workflow 6: doctor-skill-content          │   │
│  │   scope=marketplace ────────► ALL 5 workflows sequentially              │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Workflow 1: doctor-agents

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         WORKFLOW 1: doctor-agents                               │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
     ┌──────────────────────────────┼──────────────────────────────┐
     │                              │                              │
     ▼                              ▼                              ▼
┌─────────────┐            ┌─────────────────┐           ┌─────────────────────┐
│  PHASE 1    │            │    PHASE 2      │           │      PHASE 3        │
│   LOAD      │            │    DISCOVER     │           │      ANALYZE        │
└──────┬──────┘            └────────┬────────┘           └──────────┬──────────┘
       │                            │                               │
       ▼                            ▼                               ▼
┌──────────────────┐       ┌────────────────────┐        ┌─────────────────────┐
│ SKILLS:          │       │ marketplace scope: │        │ SCRIPTS (via        │
│                  │       │   Skill: market-   │        │ script-runner):     │
│ • cui-diagnostic-│       │   place-inventory  │        │                     │
│   patterns       │       │                    │        │ • analyze-markdown- │
│ • plugin-        │       │ global/project:    │        │   file.sh           │
│   architecture   │       │   Glob *.md        │        │ • analyze-tool-     │
│                  │       │                    │        │   coverage.sh       │
│ REFERENCES:      │       └────────────────────┘        │ • validate-         │
│                  │                                     │   references.py     │
│ • agents-guide.md│                                     │                     │
│ • fix-catalog.md │                                     └──────────┬──────────┘
└──────────────────┘                                                │
                                                                    ▼
                                    ┌───────────────────────────────────────────┐
                                    │              VALIDATION RULES             │
                                    │                                           │
                                    │  • Tool fit score >= 70%                  │
                                    │  • Rule 6: NO Task tool                   │
                                    │  • Rule 7: NO Maven (except maven-builder)│
                                    │  • Pattern 22: lessons-learned skill      │
                                    │  • Bloat: NORMAL<300, CRITICAL>800        │
                                    └───────────────────────────────────────────┘
                                                        │
     ┌──────────────────────────────────────────────────┴──────────────────────┐
     │                              │                                          │
     ▼                              ▼                                          ▼
┌─────────────┐            ┌─────────────────┐                      ┌──────────────┐
│  PHASE 4    │            │    PHASE 5      │                      │   PHASE 6    │
│ CATEGORIZE  │            │  APPLY FIXES    │                      │   VERIFY     │
└──────┬──────┘            └────────┬────────┘                      └──────┬───────┘
       │                            │                                      │
       ▼                            ▼                                      ▼
┌────────────────┐         ┌─────────────────────┐               ┌─────────────────┐
│ SAFE (auto):   │         │ Safe: Edit tool     │               │ SCRIPTS:        │
│ • Missing      │         │ (NO prompt)         │               │                 │
│   frontmatter  │         │                     │               │ • verify-fix.sh │
│ • Invalid YAML │         │ Risky: AskUser-     │               │                 │
│ • Unused tools │         │ Question first      │               │ REFERENCES:     │
│                │         │                     │               │                 │
│ RISKY (prompt):│         │ SCRIPTS:            │               │ • reporting-    │
│ • Rule 6       │         │ • apply-fix.py      │               │   templates.md  │
│ • Rule 7       │         │                     │               │                 │
│ • Pattern 22   │         └─────────────────────┘               └─────────────────┘
│ • Bloat >500   │
└────────────────┘
```

---

## Workflow 2: doctor-commands

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        WORKFLOW 2: doctor-commands                              │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
     ┌──────────────────────────────┼──────────────────────────────┐
     │                              │                              │
     ▼                              ▼                              ▼
┌─────────────┐            ┌─────────────────┐           ┌─────────────────────┐
│  PHASE 1    │            │    PHASE 2      │           │      PHASE 3        │
│   LOAD      │            │    DISCOVER     │           │      ANALYZE        │
└──────┬──────┘            └────────┬────────┘           └──────────┬──────────┘
       │                            │                               │
       ▼                            ▼                               ▼
┌──────────────────┐       ┌────────────────────┐        ┌─────────────────────┐
│ SKILLS:          │       │ (same as agents)   │        │ SCRIPTS:            │
│                  │       │                    │        │                     │
│ • cui-diagnostic-│       │ Skill: market-     │        │ • analyze-markdown- │
│   patterns       │       │ place-inventory    │        │   file.sh           │
│ • plugin-        │       │                    │        │ • validate-         │
│   architecture   │       │     OR             │        │   references.py     │
│                  │       │                    │        │                     │
│ REFERENCES:      │       │ Glob *.md          │        │ (NO tool-coverage   │
│                  │       │                    │        │  for commands)      │
│ • commands-      │       └────────────────────┘        └──────────┬──────────┘
│   guide.md       │                                                │
│ • fix-catalog.md │                                                ▼
└──────────────────┘                             ┌───────────────────────────────┐
                                                 │       VALIDATION RULES        │
                                                 │                               │
                                                 │  RULE 0 - THIN WRAPPER:       │
                                                 │  • IDEAL: <100 lines          │
                                                 │  • ACCEPTABLE: 100-150        │
                                                 │  • BLOATED: 150-200           │
                                                 │  • CRITICAL: >200 lines       │
                                                 │                               │
                                                 │  • MUST delegate to skills    │
                                                 │  • NO step-by-step logic      │
                                                 │  • NO for loops               │
                                                 │  • Check invoked skills for   │
                                                 │    foundation skill loading   │
                                                 └───────────────────────────────┘
                                                             │
     ┌───────────────────────────────────────────────────────┴─────────────────────┐
     │                              │                                              │
     ▼                              ▼                                              ▼
┌─────────────┐            ┌─────────────────┐                          ┌──────────────┐
│  PHASE 4    │            │    PHASE 5      │                          │   PHASE 6    │
│ CATEGORIZE  │            │  APPLY FIXES    │                          │   VERIFY     │
└──────┬──────┘            └────────┬────────┘                          └──────┬───────┘
       │                            │                                          │
       ▼                            ▼                                          ▼
┌────────────────┐         ┌─────────────────────┐                   ┌─────────────────┐
│ SAFE (auto):   │         │ Safe: Edit tool     │                   │ (same as        │
│ • Header case  │         │ (NO prompt)         │                   │  agents)        │
│   (## Workflow │         │                     │                   │                 │
│   → ## WORKFLOW│         │ Auto-fix patterns:  │                   │ • verify-fix.sh │
│ • Missing      │         │ • Section headers   │                   │ • reporting-    │
│   CONTINUOUS   │         │ • CONTINUOUS        │                   │   templates.md  │
│   IMPROVEMENT  │         │   IMPROVEMENT       │                   │                 │
│ • Legacy CIR   │         │                     │                   └─────────────────┘
│                │         │ Risky: Report only  │
│ RISKY (report):│         │ (manual refactor)   │
│ • Rule 0       │         │                     │
│   violations   │         └─────────────────────┘
│   (>200 lines) │
└────────────────┘
```

---

## Workflow 3: doctor-skills

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         WORKFLOW 3: doctor-skills                               │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
     ┌──────────────────────────────┼──────────────────────────────┐
     │                              │                              │
     ▼                              ▼                              ▼
┌─────────────┐            ┌─────────────────┐           ┌─────────────────────┐
│  PHASE 1    │            │    PHASE 2      │           │      PHASE 3        │
│   LOAD      │            │    DISCOVER     │           │      ANALYZE        │
└──────┬──────┘            └────────┬────────┘           └──────────┬──────────┘
       │                            │                               │
       ▼                            ▼                               ▼
┌──────────────────┐       ┌────────────────────┐        ┌─────────────────────┐
│ SKILLS:          │       │ Skill: market-     │        │ SCRIPTS:            │
│                  │       │ place-inventory    │        │                     │
│ • cui-diagnostic-│       │                    │        │ • analyze-skill-    │
│   patterns       │       │                    │        │   structure.sh      │
│ • plugin-        │       │                    │        │ • analyze-markdown- │
│   architecture   │       │                    │        │   file.sh           │
│                  │       │                    │        │ • validate-         │
│ REFERENCES:      │       │                    │        │   references.py     │
│                  │       │                    │        │                     │
│ • skills-guide.md│       └────────────────────┘        └──────────┬──────────┘
│ • fix-catalog.md │                                                │
└──────────────────┘                                                ▼
                                                 ┌───────────────────────────────┐
                                                 │       VALIDATION RULES        │
                                                 │                               │
                                                 │  • Structure score >= 70      │
                                                 │  • Progressive disclosure     │
                                                 │  • Relative path usage        │
                                                 │  • No missing referenced files│
                                                 │  • No unreferenced files      │
                                                 │  • Bloat: NORMAL<400,         │
                                                 │           CRITICAL>1200       │
                                                 │                               │
                                                 │  FOUNDATION SKILL CHECK:      │
                                                 │  ┌───────────────────────────┐│
                                                 │  │ MUST load:                ││
                                                 │  │ • plugin-architecture     ││
                                                 │  │ • cui-diagnostic-patterns ││
                                                 │  │                           ││
                                                 │  │ EXEMPT:                   ││
                                                 │  │ • plugin-architecture     ││
                                                 │  │   (is itself)             ││
                                                 │  │ • marketplace-inventory   ││
                                                 │  │   (Pattern 1 only)        ││
                                                 │  │ • Read-only skills        ││
                                                 │  └───────────────────────────┘│
                                                 └───────────────────────────────┘
                                                             │
     ┌───────────────────────────────────────────────────────┴─────────────────────┐
     │                              │                                              │
     ▼                              ▼                                              ▼
┌─────────────┐            ┌─────────────────┐                          ┌──────────────┐
│  PHASE 4    │            │    PHASE 5      │                          │   PHASE 6    │
│ CATEGORIZE  │            │  APPLY FIXES    │                          │   VERIFY     │
└──────┬──────┘            └────────┬────────┘                          └──────┬───────┘
       │                            │                                          │
       ▼                            ▼                                          ▼
┌────────────────┐         ┌─────────────────────┐                   ┌─────────────────┐
│ SAFE (auto):   │         │ Safe: Edit tool     │                   │ (same pattern)  │
│ • Missing      │         │                     │                   │                 │
│   frontmatter  │         │ Auto-fix:           │                   │ • verify-fix.sh │
│ • Unused tools │         │ Add Step 0 for      │                   │ • reporting-    │
│ • Invalid YAML │         │ foundation skills   │                   │   templates.md  │
│ • MISSING      │         │                     │                   │                 │
│   foundation   │         │ ┌─────────────────┐ │                   └─────────────────┘
│   skills       │         │ │#### Step 0: Load│ │
│                │         │ │Foundation Skills│ │
│ RISKY:         │         │ │```              │ │
│ • (none        │         │ │Skill: plugin-   │ │
│   specific)    │         │ │  architecture   │ │
│                │         │ │Skill: cui-diag- │ │
└────────────────┘         │ │  nostic-patterns│ │
                           │ │```              │ │
                           │ └─────────────────┘ │
                           └─────────────────────┘
```

---

## Workflow 4: doctor-metadata

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        WORKFLOW 4: doctor-metadata                              │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
     ┌──────────────────────────────┼──────────────────────────────┐
     │                              │                              │
     ▼                              ▼                              ▼
┌─────────────┐            ┌─────────────────┐           ┌─────────────────────┐
│  PHASE 1    │            │    PHASE 2      │           │      PHASE 3        │
│   LOAD      │            │    DISCOVER     │           │      ANALYZE        │
└──────┬──────┘            └────────┬────────┘           └──────────┬──────────┘
       │                            │                               │
       ▼                            ▼                               ▼
┌──────────────────┐       ┌────────────────────┐        ┌─────────────────────┐
│ SKILLS:          │       │ Glob:              │        │ LLM ANALYSIS:       │
│                  │       │                    │        │                     │
│ • cui-diagnostic-│       │ **/plugin.json     │        │ • Verify JSON syntax│
│   patterns       │       │                    │        │ • Check required    │
│                  │       │ path: marketplace/ │        │   fields (name,     │
│ (NO plugin-      │       │       bundles      │        │   version, desc)    │
│  architecture)   │       │                    │        │ • Validate arrays   │
│                  │       │                    │        │   (commands, skills,│
│ REFERENCES:      │       │                    │        │   agents)           │
│                  │       │                    │        │ • Cross-check files │
│ • metadata-      │       │                    │        │   vs declarations   │
│   guide.md       │       │                    │        │                     │
│ • fix-catalog.md │       └────────────────────┘        └──────────┬──────────┘
└──────────────────┘                                                │
                                                                    ▼
                                    ┌───────────────────────────────────────────┐
                                    │              VALIDATION RULES             │
                                    │                                           │
                                    │  • JSON syntax valid                      │
                                    │  • Required: name, version, description   │
                                    │  • Declared files MUST exist              │
                                    │  • Existing files SHOULD be declared      │
                                    │                                           │
                                    └───────────────────────────────────────────┘
                                                        │
     ┌──────────────────────────────────────────────────┴──────────────────────┐
     │                              │                                          │
     ▼                              ▼                                          ▼
┌─────────────┐            ┌─────────────────┐                      ┌──────────────┐
│  PHASE 4    │            │    PHASE 5      │                      │   PHASE 6    │
│ CATEGORIZE  │            │  APPLY FIXES    │                      │   VERIFY     │
└──────┬──────┘            └────────┬────────┘                      └──────┬───────┘
       │                            │                                      │
       ▼                            ▼                                      ▼
┌────────────────┐         ┌─────────────────────┐               ┌─────────────────┐
│ SAFE (auto):   │         │ Edit tool           │               │ (same pattern)  │
│ • Missing      │         │ (JSON modifications)│               │                 │
│   required     │         │                     │               │ • verify-fix.sh │
│   fields       │         │                     │               │ • reporting-    │
│ • Extra entries│         │                     │               │   templates.md  │
│   (files gone) │         │                     │               │                 │
│ • Missing      │         │                     │               └─────────────────┘
│   entries      │         │                     │
│   (files exist)│         │                     │
│                │         │                     │
│ RISKY:         │         │                     │
│ • (none)       │         │                     │
└────────────────┘         └─────────────────────┘
```

---

## Workflow 5: doctor-scripts

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         WORKFLOW 5: doctor-scripts                              │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
     ┌──────────────────────────────┼──────────────────────────────┐
     │                              │                              │
     ▼                              ▼                              ▼
┌─────────────┐            ┌─────────────────┐           ┌─────────────────────┐
│  PHASE 1    │            │    PHASE 2      │           │      PHASE 3        │
│   LOAD      │            │    DISCOVER     │           │      ANALYZE        │
└──────┬──────┘            └────────┬────────┘           └──────────┬──────────┘
       │                            │                               │
       ▼                            ▼                               ▼
┌──────────────────┐       ┌────────────────────┐        ┌─────────────────────┐
│ SKILLS:          │       │ Glob:              │        │ LLM + SCRIPT        │
│                  │       │                    │        │ ANALYSIS:           │
│ • cui-diagnostic-│       │ scripts/*.{sh,py}  │        │                     │
│   patterns       │       │                    │        │ • Verify SKILL.md   │
│ • plugin-        │       │ path: marketplace/ │        │   documentation     │
│   architecture   │       │       bundles/*/   │        │ • Check test file   │
│                  │       │       skills       │        │   exists            │
│ REFERENCES:      │       │                    │        │ • Verify --help     │
│                  │       │                    │        │   output            │
│ • plugin-        │       │                    │        │ • Check stdlib-only │
│   architecture:  │       │                    │        │   compliance        │
│   script-        │       │                    │        │                     │
│   standards.md   │       │                    │        │                     │
│ • fix-catalog.md │       └────────────────────┘        └──────────┬──────────┘
└──────────────────┘                                                │
       │                                                            ▼
       │                            ┌───────────────────────────────────────────┐
       │                            │              VALIDATION RULES             │
       │                            │                                           │
       │                            │  FROM script-standards.md:                │
       │                            │  • Documented in SKILL.md                 │
       │                            │  • Has corresponding test file            │
       │                            │  • Supports --help flag                   │
       │                            │  • stdlib-only (no pip/npm)               │
       │                            │  • Executable permissions                 │
       │                            │  • JSON output format                     │
       │                            │                                           │
       └──────────────────────────► │  NOTE: References EXTERNAL skill:         │
                                    │  plugin-architecture:script-standards.md  │
                                    └───────────────────────────────────────────┘
                                                        │
     ┌──────────────────────────────────────────────────┴──────────────────────┐
     │                              │                                          │
     ▼                              ▼                                          ▼
┌─────────────┐            ┌─────────────────┐                      ┌──────────────┐
│  PHASE 4    │            │    PHASE 5      │                      │   PHASE 6    │
│ CATEGORIZE  │            │  APPLY FIXES    │                      │   VERIFY     │
└──────┬──────┘            └────────┬────────┘                      └──────┬───────┘
       │                            │                                      │
       ▼                            ▼                                      ▼
┌────────────────┐         ┌─────────────────────┐               ┌─────────────────┐
│ (Script-       │         │ (Script-specific    │               │ (same pattern)  │
│  specific      │         │  fixes)             │               │                 │
│  checks)       │         │                     │               │ • verify-fix.sh │
│                │         │                     │               │ • reporting-    │
└────────────────┘         └─────────────────────┘               │   templates.md  │
                                                                 └─────────────────┘
```

---

## Workflow 6: doctor-skill-content

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      WORKFLOW 6: doctor-skill-content                           │
│                       (Cross-File Content Analysis)                             │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              6-PHASE WORKFLOW                                   │
│                                                                                 │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌──────────┐   ┌────────┐   ┌──────┐│
│  │ PHASE 1 │──►│ PHASE 2 │──►│ PHASE 3 │──►│ PHASE 4  │──►│ PHASE 5│──►│PHASE6││
│  │Inventory│   │Classify │   │ Analyze │   │Reorganize│   │ Verify │   │Report││
│  │ (SCRIPT)│   │  (LLM)  │   │(HYBRID) │   │(LLM+Bash)│   │(SCRIPT)│   │(LLM) ││
│  └─────────┘   └─────────┘   └─────────┘   └──────────┘   └────────┘   └──────┘│
└─────────────────────────────────────────────────────────────────────────────────┘
                                    │
     ┌──────────────────────────────┼──────────────────────────────┐
     │                              │                              │
     ▼                              ▼                              ▼
┌─────────────┐            ┌─────────────────┐           ┌─────────────────────┐
│  PHASE 1    │            │    PHASE 2      │           │      PHASE 3        │
│ INVENTORY   │            │    CLASSIFY     │           │      ANALYZE        │
│  (SCRIPT)   │            │     (LLM)       │           │     (HYBRID)        │
└──────┬──────┘            └────────┬────────┘           └──────────┬──────────┘
       │                            │                               │
       ▼                            ▼                               ▼
┌──────────────────┐       ┌────────────────────┐        ┌─────────────────────┐
│ LOAD:            │       │ For each .md file: │        │ Step 3a: SCRIPT     │
│                  │       │                    │        │ ┌───────────────────┐
│ SKILLS:          │       │ • Read content     │        │ │analyze-cross-file-│
│ • cui-diagnostic-│       │ • Apply criteria   │        │ │content.py         │
│   patterns       │       │   from content-    │        │ │                   │
│ • plugin-        │       │   classification-  │        │ │Detects:           │
│   architecture   │       │   guide.md         │        │ │• exact_duplicates │
│                  │       │ • Determine:       │        │ │• similarity_cands │
│ REFERENCES:      │       │   - reference      │        │ │• extraction_cands │
│ • content-       │       │   - workflow       │        │ │• terminology vars │
│   classification-│       │   - template       │        │ └───────────────────┘
│   guide.md       │       │   - mixed          │        │                     │
│ • content-       │       │ • Record:          │        │ Step 3b: LLM        │
│   quality-       │       │   - confidence     │        │ ┌───────────────────┐
│   guide.md       │       │   - needs_move     │        │ │Semantic analysis: │
│                  │       │   - needs_split    │        │ │• true_duplicate   │
│ SCRIPT:          │       │                    │        │ │• similar_concept  │
│ • scan-skill-    │       │ OUTPUT:            │        │ │• false_positive   │
│   inventory.sh   │       │ Classification for │        │ │                   │
│                  │       │ each file          │        │ │Recommend:         │
│ OUTPUT:          │       │                    │        │ │• consolidate      │
│ • directories    │       │                    │        │ │• cross_reference  │
│ • files          │       │                    │        │ │• keep_both        │
│ • line_counts    │       │                    │        │ └───────────────────┘
│ • extensions     │       │                    │        │                     │
└──────────────────┘       └────────────────────┘        │ Step 3c: LLM        │
                                                         │ Single-file quality │
                                                         │ • completeness      │
                                                         │ • contradictions    │
                                                         │                     │
                                                         │ Step 3d: SCRIPT     │
                                                         │ ┌───────────────────┐
                                                         │ │verify-cross-file- │
                                                         │ │findings.py        │
                                                         │ │                   │
                                                         │ │Rejects unverified │
                                                         │ │LLM claims         │
                                                         │ └───────────────────┘
                                                         └─────────────────────┘
                                                                    │
     ┌──────────────────────────────────────────────────────────────┴──────────┐
     │                              │                                          │
     ▼                              ▼                                          ▼
┌─────────────────┐        ┌─────────────────┐                      ┌──────────────────┐
│    PHASE 4      │        │    PHASE 5      │                      │     PHASE 6      │
│  REORGANIZE     │        │     VERIFY      │                      │     REPORT       │
│  (LLM + Bash)   │        │    (SCRIPT)     │                      │      (LLM)       │
└────────┬────────┘        └────────┬────────┘                      └────────┬─────────┘
         │                          │                                        │
         ▼                          ▼                                        ▼
┌─────────────────────┐   ┌─────────────────────┐               ┌──────────────────────┐
│ SAFE (auto):        │   │ SCRIPT:             │               │ Generate report:     │
│ • Move file to      │   │ • validate-         │               │                      │
│   correct dir       │   │   references.py     │               │ • Summary metrics    │
│ • Rename redundant  │   │                     │               │ • File classification│
│   suffix            │   │ Verify:             │               │   table              │
│                     │   │ • Internal xrefs    │               │ • Quality analysis   │
│ RISKY (prompt):     │   │   valid             │               │ • Reorganizations    │
│ • Split mixed file  │   │ • SKILL.md refs     │               │ • Link verification  │
│ • Delete duplicate  │   │   point to files    │               │ • Recommendations    │
│ • Merge similar     │   │                     │               │                      │
│                     │   └─────────────────────┘               └──────────────────────┘
│ After moves:        │
│ • Grep old paths    │
│ • Update refs       │
└─────────────────────┘
```

---

## Complete Dependency Map

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SKILL DEPENDENCIES                             │
└─────────────────────────────────────────────────────────────────────────────────┘

     ┌──────────────────────────────────────────────────────────────────────┐
     │                     FOUNDATION SKILLS (REQUIRED)                     │
     │                                                                      │
     │  ┌─────────────────────────────┐  ┌─────────────────────────────┐   │
     │  │ cui-utilities:              │  │ cui-plugin-development-     │   │
     │  │ cui-diagnostic-patterns     │  │ tools:plugin-architecture   │   │
     │  │                             │  │                             │   │
     │  │ Provides:                   │  │ Provides:                   │   │
     │  │ • Non-prompting tool        │  │ • Architecture principles   │   │
     │  │   usage patterns            │  │ • Skill patterns            │   │
     │  │ • Glob/Read/Grep over       │  │ • Design guidance           │   │
     │  │   Bash commands             │  │ • Script standards          │   │
     │  └─────────────────────────────┘  └─────────────────────────────┘   │
     │                                                                      │
     │  Used by: ALL 6 workflows (Phase 1 - Load Prerequisites)            │
     └──────────────────────────────────────────────────────────────────────┘

     ┌──────────────────────────────────────────────────────────────────────┐
     │                     DISCOVERY SKILL (CONDITIONAL)                    │
     │                                                                      │
     │  ┌─────────────────────────────────────────────────────────────────┐ │
     │  │ cui-plugin-development-tools:marketplace-inventory             │ │
     │  │                                                                 │ │
     │  │ Provides: Component discovery for marketplace scope            │ │
     │  │ Used by: Workflows 1-3, 5 (when scope=marketplace)             │ │
     │  └─────────────────────────────────────────────────────────────────┘ │
     └──────────────────────────────────────────────────────────────────────┘

     ┌──────────────────────────────────────────────────────────────────────┐
     │                     SCRIPT RESOLUTION (REQUIRED)                     │
     │                                                                      │
     │  ┌─────────────────────────────────────────────────────────────────┐ │
     │  │ cui-utilities:script-runner                                    │ │
     │  │                                                                 │ │
     │  │ Provides: Portable script path resolution                      │ │
     │  │ Resolves: bundle:skill/scripts/name → absolute path            │ │
     │  │ Used by: ALL workflows that execute scripts                    │ │
     │  └─────────────────────────────────────────────────────────────────┘ │
     └──────────────────────────────────────────────────────────────────────┘

     ┌──────────────────────────────────────────────────────────────────────┐
     │                     LESSONS LEARNED (OPTIONAL)                       │
     │                                                                      │
     │  ┌─────────────────────────────────────────────────────────────────┐ │
     │  │ cui-utilities:claude-lessons-learned                           │ │
     │  │                                                                 │ │
     │  │ Provides: Record discoveries during execution                  │ │
     │  │ Used by: CONTINUOUS IMPROVEMENT RULE (all commands)            │ │
     │  └─────────────────────────────────────────────────────────────────┘ │
     └──────────────────────────────────────────────────────────────────────┘
```

---

## Scripts Dependency Matrix

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            SCRIPTS BY WORKFLOW                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

             │ W1    │ W2    │ W3    │ W4    │ W5    │ W6
             │agents │ cmds  │skills │ meta  │scripts│content
─────────────┼───────┼───────┼───────┼───────┼───────┼────────
analyze-     │  ●    │  ●    │  ●    │       │       │
markdown-    │       │       │       │       │       │
file.sh      │       │       │       │       │       │
─────────────┼───────┼───────┼───────┼───────┼───────┼────────
analyze-tool-│  ●    │       │       │       │       │
coverage.sh  │       │       │       │       │       │
─────────────┼───────┼───────┼───────┼───────┼───────┼────────
analyze-     │       │       │  ●    │       │       │
skill-       │       │       │       │       │       │
structure.sh │       │       │       │       │       │
─────────────┼───────┼───────┼───────┼───────┼───────┼────────
validate-    │  ●    │  ●    │  ●    │       │       │  ●
references.py│       │       │       │       │       │
─────────────┼───────┼───────┼───────┼───────┼───────┼────────
scan-skill-  │       │       │       │       │       │  ●
inventory.sh │       │       │       │       │       │
─────────────┼───────┼───────┼───────┼───────┼───────┼────────
analyze-     │       │       │       │       │       │  ●
cross-file-  │       │       │       │       │       │
content.py   │       │       │       │       │       │
─────────────┼───────┼───────┼───────┼───────┼───────┼────────
verify-cross-│       │       │       │       │       │  ●
file-        │       │       │       │       │       │
findings.py  │       │       │       │       │       │
─────────────┼───────┼───────┼───────┼───────┼───────┼────────
apply-fix.py │  ●    │  ●    │  ●    │  ●    │  ●    │
─────────────┼───────┼───────┼───────┼───────┼───────┼────────
verify-fix.sh│  ●    │  ●    │  ●    │  ●    │  ●    │
─────────────┼───────┼───────┼───────┼───────┼───────┼────────
categorize-  │  ○    │  ○    │  ○    │  ○    │  ○    │
fixes.py     │       │       │       │       │       │
─────────────┼───────┼───────┼───────┼───────┼───────┼────────
extract-     │  ○    │  ○    │  ○    │  ○    │  ○    │
fixable-     │       │       │       │       │       │
issues.py    │       │       │       │       │       │

● = Used in workflow
○ = Available but optional
```

---

## References Dependency Matrix

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          REFERENCES BY WORKFLOW                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

                      │ W1    │ W2    │ W3    │ W4    │ W5    │ W6
                      │agents │ cmds  │skills │ meta  │scripts│content
──────────────────────┼───────┼───────┼───────┼───────┼───────┼────────
agents-guide.md       │  ●    │       │       │       │       │
──────────────────────┼───────┼───────┼───────┼───────┼───────┼────────
commands-guide.md     │       │  ●    │       │       │       │
──────────────────────┼───────┼───────┼───────┼───────┼───────┼────────
skills-guide.md       │       │       │  ●    │       │       │
──────────────────────┼───────┼───────┼───────┼───────┼───────┼────────
metadata-guide.md     │       │       │       │  ●    │       │
──────────────────────┼───────┼───────┼───────┼───────┼───────┼────────
plugin-architecture:  │       │       │       │       │  ●    │
script-standards.md   │       │       │       │       │       │
──────────────────────┼───────┼───────┼───────┼───────┼───────┼────────
content-             │       │       │       │       │       │  ●
classification-      │       │       │       │       │       │
guide.md             │       │       │       │       │       │
──────────────────────┼───────┼───────┼───────┼───────┼───────┼────────
content-quality-     │       │       │       │       │       │  ●
guide.md             │       │       │       │       │       │
──────────────────────┼───────┼───────┼───────┼───────┼───────┼────────
fix-catalog.md       │  ●    │  ●    │  ●    │  ●    │  ●    │
──────────────────────┼───────┼───────┼───────┼───────┼───────┼────────
safe-fixes-guide.md  │  ○    │  ○    │  ○    │  ○    │  ○    │
──────────────────────┼───────┼───────┼───────┼───────┼───────┼────────
risky-fixes-guide.md │  ○    │  ○    │  ○    │  ○    │  ○    │
──────────────────────┼───────┼───────┼───────┼───────┼───────┼────────
verification-guide.md│  ○    │  ○    │  ○    │  ○    │  ○    │
──────────────────────┼───────┼───────┼───────┼───────┼───────┼────────
reporting-           │  ●    │  ●    │  ●    │  ●    │  ●    │  ●
templates.md         │       │       │       │       │       │

● = Required for workflow
○ = Available for reference
```

---

## Context Usage Summary

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       PROGRESSIVE DISCLOSURE ANALYSIS                           │
└─────────────────────────────────────────────────────────────────────────────────┘

Without Progressive Disclosure (load ALL):
┌─────────────────────────────────────────┐
│ SKILL.md                    ~900 lines  │
│ agents-guide.md             ~500 lines  │
│ commands-guide.md           ~500 lines  │
│ skills-guide.md             ~850 lines  │
│ metadata-guide.md           ~400 lines  │
│ fix-catalog.md              ~300 lines  │
│ content-classification.md   ~200 lines  │
│ content-quality.md          ~200 lines  │
│ reporting-templates.md      ~100 lines  │
│ safe-fixes-guide.md         ~200 lines  │
│ risky-fixes-guide.md        ~200 lines  │
│ verification-guide.md       ~200 lines  │
├─────────────────────────────────────────┤
│ TOTAL                      ~4,550 lines │
└─────────────────────────────────────────┘

With Progressive Disclosure (per workflow):
┌─────────────────────────────────────────┐
│ Workflow 1 (agents):                    │
│   SKILL.md              ~900 lines      │
│   agents-guide.md       ~500 lines      │
│   fix-catalog.md        ~300 lines      │
│   TOTAL                ~1,700 lines     │
├─────────────────────────────────────────┤
│ Workflow 6 (skill-content):             │
│   SKILL.md              ~900 lines      │
│   content-class.md      ~200 lines      │
│   content-quality.md    ~200 lines      │
│   TOTAL                ~1,300 lines     │
└─────────────────────────────────────────┘

                    ┌────────────────────────┐
                    │  SAVINGS: ~65-70%      │
                    │  per workflow          │
                    └────────────────────────┘
```
