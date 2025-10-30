---
name: cui-manage-web-permissions
description: Analyze and consolidate WebFetch domain permissions across projects with security research and validation
---

# Manage Web Permissions Command

Analyzes WebFetch domains across global and project settings, researches domains for security, consolidates permissions, and provides recommendations.

## PARAMETERS

**scope** - Which settings to analyze (global/local/both, default: both)

## WORKFLOW

### Step 1: Load Web Security Standards

```
Skill: web-security-standards
```

Loads trusted domains, security assessment patterns, and research methodology.

### Step 2: Collect All WebFetch Permissions

**A. Read global settings** (`~/.claude/settings.json`)

**B. Read local settings** (`./.claude/settings.local.json`)

**C. Extract all WebFetch permissions** from both sources

**D. Categorize domains**:
- Universal (domain:*)
- Major domains (from trusted-domains standards)
- High-reach domains (github.com, stackoverflow.com, etc.)
- Project-specific domains
- Unknown domains (need research)

### Step 3: Detect Duplicate and Redundant Permissions

**A. Check for domain:*** - If present globally, all specific domains are redundant

**B. Find exact duplicates** across global and local

**C. Identify redundant patterns**:
- Subdomain when parent domain approved
- Multiple entries for same domain

### Step 4: Research Unknown Domains

For each unknown domain:

**A. Web research** using WebSearch or WebFetch:
```
WebSearch: "domain-name.com reputation security"
WebFetch: https://domain-name.com (check if accessible)
```

**B. Assess security** using standards from web-security-standards skill:
- Check against red flags
- Evaluate purpose and trustworthiness
- Categorize risk level (LOW/MEDIUM/HIGH)

**C. Determine categorization**:
- MAJOR_DOMAINS - Documentation, official sites
- HIGH_REACH - Popular developer resources
- PROJECT_SPECIFIC - Project dependencies
- SUSPICIOUS - Security concerns
- UNKNOWN - Unable to assess

### Step 5: Generate Consolidation Recommendations

**A. If domain:* exists globally**:
```
✅ Universal web access enabled
Recommendation: Remove all specific domains (redundant)
- Remove {count} specific domains from global
- Remove {count} specific domains from local
```

**B. If no domain:***:
```
Recommendations by Category:

MAJOR_DOMAINS ({count}):
→ Move to global settings (docs.oracle.com, maven.apache.org, ...)

HIGH_REACH ({count}):
→ Move to global settings (github.com, stackoverflow.com, ...)

PROJECT_SPECIFIC ({count}):
→ Keep in local settings

SUSPICIOUS ({count}):
→ Review for removal: {list with reasons}
```

### Step 6: Display Analysis Report

```
╔════════════════════════════════════════════════════════════╗
║          WebFetch Permission Analysis                      ║
╚════════════════════════════════════════════════════════════╝

Global Settings:
- WebFetch permissions: {count}
- Universal access (domain:*): {yes/no}

Local Settings:
- WebFetch permissions: {count}

Total Unique Domains: {count}

By Category:
- Major domains: {count}
- High-reach domains: {count}
- Project-specific: {count}
- Suspicious: {count}
- Unknown: {count}

Duplicates Found: {count}
Redundant (if domain:* exists): {count}

Recommendations:
{detailed recommendations}
```

### Step 7: Apply Recommendations (Optional)

Prompt user:
```
Apply recommended changes? [Y/n/r]
Y - Apply all recommendations
n - Skip (display only)
r - Review each change
```

If yes:
- Update global settings
- Update local settings
- Remove duplicates and redundant permissions
- Consolidate domains per recommendations

### Step 8: Report Results

Display summary of changes made and final state.

## CRITICAL RULES

**Security:**
- Always research unknown domains before approval
- Flag suspicious domains for review
- Check against red flags from standards

**Consolidation:**
- If domain:* exists, remove all specific domains
- Move major/high-reach domains to global
- Keep project-specific domains in local
- Remove duplicates

**User Control:**
- Never auto-remove without user approval
- Provide clear rationale for recommendations
- Allow review mode for granular control

## USAGE EXAMPLES

**Analyze all settings:**
```
/cui-manage-web-permissions
```

**Analyze global only:**
```
/cui-manage-web-permissions scope=global
```

**Analyze local only:**
```
/cui-manage-web-permissions scope=local
```

## ARCHITECTURE

This command:
- Uses web-security-standards skill for domain knowledge
- Performs web research for unknown domains
- Provides consolidation recommendations
- Optionally applies changes

## STANDARDS

References:
- web-security-standards skill (trusted domains, security patterns)
- Permission architecture standards (global vs local)

## RELATED

- `/cui-setup-project-permissions` - Manages all permission types
- `web-security-standards` skill - Domain security knowledge
