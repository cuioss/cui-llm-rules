---
name: plan-marshall
description: Project configuration wizard for planning system
allowed-tools: Read, Bash, Skill, AskUserQuestion
---

# /plan-marshall

Project configuration wizard for the planning system.

## Usage

```
/plan-marshall           # Interactive menu or first-run wizard
/plan-marshall --wizard  # Force first-run wizard
```

## Banner

Display this banner on command start (output as single code block):

```
╔═══════════════════════════════════════════════════════════════════════╗
║                                 :                                     ║
║                               .;:;.                                   ║
║                              :;:::;:                                  ║
║          ...             .;:::::::::;.              ...               ║
║          .::;:::::::::::::;:::::::::;:::::::::::::;::.                ║
║               :;:::::::::::::::::::::::::::::::;:                     ║
║                .;:::::::::::::::::::::::::::::;.                      ║
║                                                                       ║
║                        █▀█ █   █▀█ █▄ █                               ║
║                        █▀▀ █▄▄ █▀█ █ ▀█                               ║
║                  █▀▄▀█ █▀█ █▀█ █▀ █ █ █▀█ █   █                       ║
║                  █ ▀ █ █▀█ █▀▄ ▄█ █▀█ █▀█ █▄▄ █▄▄                     ║
║                                                                       ║
║                .;:::::::::::::::::::::::::::::;.                      ║
║               :;:::::::::::::::::::::::::::::::;:                     ║
║          .::;:::::::::::::;:::::::::;:::::::::::::;::.                ║
║         ...              .;:::::::::;.              ...               ║
║                              :;:::;:                                  ║
║                               .;:;.                                   ║
║                                 :                          by KIDICAP ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## Execution

### Step 1: Determine Mode

Run the mode detection script (handles missing executor):

```bash
python3 marketplace/bundles/plan-marshall/skills/plan-marshall/scripts/determine-mode.py mode
```

If `--wizard` flag was provided, skip to wizard mode regardless of output.

### Step 2: Route Based on Output

| mode | reason | Action |
|------|--------|--------|
| `wizard` | `executor_missing` | Read skill, start at "First-Run Wizard" Step 1 |
| `wizard` | `marshal_missing` | Read skill, start at "First-Run Wizard" Step 2 |
| `menu` | `both_exist` | Read skill, go to "Interactive Menu" |

### Step 3: Execute Skill

Read and follow the skill instructions:

```
Read: marketplace/bundles/plan-marshall/skills/plan-marshall/SKILL.md
```

Execute the section identified in Step 2. Follow all steps exactly as documented.
