---
name: plan-marshall
description: Project configuration wizard for planning system
allowed-tools: Skill, AskUserQuestion
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
║                                 :                                     ║
╚═══════════════════════════════════════════════════════════════════════╝
```

## Execution

Load and execute the plan-marshall skill:

```
Skill: planning:plan-marshall
```

The skill handles all interactive flows and operations:
- First-run wizard for new projects
- Interactive menu for returning users
- Executor generation and maintenance
- Permission configuration
- Build system detection
- Plan-type management
