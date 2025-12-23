---
name: plan-marshall-plugin
description: Requirements domain manifest for plan-marshall workflow integration
allowed-tools: Read
---

# Plan Marshall Plugin - Requirements Domain

Domain manifest skill providing requirements engineering capabilities to plan-marshall workflows.

## Purpose

Declares the requirements domain configuration including:
- Domain identity (key: requirements)
- Profile-based skill organization (core, implementation, testing, quality)

## Configuration

All configuration is in `plugin.json`. This skill is automatically discovered by the `domain-extension-api` discovery mechanism.

## Integration

This manifest is read by:
- `skill-domains get-available` - Lists available domains
- `skill-domains configure` - Applies domain configuration to marshal.json
- `marshall-steward` wizard - Domain selection during project setup
