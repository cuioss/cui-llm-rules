---
name: plan-marshall-plugin
description: Java domain manifest for plan-marshall workflow integration
allowed-tools: Read
---

# Plan Marshall Plugin - Java Domain

Domain manifest skill providing Java development capabilities to plan-marshall workflows.

## Purpose

Declares the Java domain configuration including:
- Domain identity (key: java)
- Workflow extensions (outline, triage)
- Profile-based skill organization (core, implementation, testing, quality)

## Configuration

All configuration is in `extension.py` which implements the Extension API:
- `get_skill_domains()` - Domain metadata with profiles
- `provides_triage()` - Triage skill reference or None
- `provides_outline()` - Outline skill reference or None

## Integration

This extension is discovered by:
- `skill-domains get-available` - Lists available domains
- `skill-domains configure` - Applies domain configuration to marshal.json
- `marshall-steward` wizard - Domain selection during project setup
