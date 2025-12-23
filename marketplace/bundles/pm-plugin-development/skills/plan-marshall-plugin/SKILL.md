---
name: plan-marshall-plugin
description: Plugin development domain manifest for plan-marshall workflow integration
allowed-tools: Read
---

# Plan Marshall Plugin - Plugin Development Domain

Domain manifest skill providing plugin development capabilities to plan-marshall workflows.

## Purpose

Declares the plugin-dev domain configuration including:
- Domain identity (key: plugin-dev)
- Workflow extensions (outline, triage)
- Profile-based skill organization (core, implementation, testing, quality)

## Configuration

All configuration is in `plugin.json`. This skill is automatically discovered by the `domain-extension-api` discovery mechanism.

## Integration

This manifest is read by:
- `skill-domains get-available` - Lists available domains
- `skill-domains configure` - Applies domain configuration to marshal.json
- `marshall-steward` wizard - Domain selection during project setup
