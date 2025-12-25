---
name: plan-marshall-plugin
description: CUI Java supplement manifest for plan-marshall workflow integration
allowed-tools: Read
---

# Plan Marshall Plugin - CUI Java Supplement

Supplement manifest skill providing CUI-specific Java patterns to the Java domain.

## Purpose

Declares CUI-specific supplements for the Java domain including:
- Target domain (java)
- Additional skills for logging, testing, and HTTP
- Profile-based skill organization

## Configuration

All configuration is in `extension.py` which implements the Extension API:
- `get_domain_supplements()` - Supplement metadata for the target domain

## Integration

This extension is discovered by:
- `skill-domains get-available` - Lists available supplements
- `skill-domains configure --supplements` - Merges supplement skills into target domain
- `marshall-steward` wizard - Supplement selection after domain selection
