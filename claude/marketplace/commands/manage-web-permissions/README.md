# manage-web-permissions

Analyzes WebFetch domain permissions across all projects, consolidates safe domains to global settings, performs security research on unknown domains, and maintains clean permission configurations with enforced limits.

## Purpose

Automates WebFetch permission management by scanning all projects, categorizing domains by reach and safety, performing web-based security research, consolidating common/safe domains globally, and enforcing 30-domain global and 10-domain project limits.

## Usage

```bash
# Analyze all projects under ~/git/
/manage-web-permissions

# Auto-apply safe consolidations (still prompts for security)
/manage-web-permissions auto

# Analyze single project
/manage-web-permissions project=~/git/cui-llm-rules

# Preview changes without applying
/manage-web-permissions dry-run

# Combine parameters
/manage-web-permissions project=~/git/OAuth-Sheriff auto
```

## What It Does

The command performs comprehensive WebFetch permission optimization:

1. **Read Global Settings** - Extract current globally-approved domains
2. **Scan All Projects** - Discover WebFetch domains across ~/git/
3. **Load Decision History** - Read previous security research from ~/.claude/run-configuration.md
4. **Categorize Domains** - Organize by: ALREADY_GLOBAL, MAJOR_DOMAINS, HIGH_REACH, RESEARCHED, FLAGGED, UNKNOWN
5. **Clean Redundant** - Remove project domains already in global
6. **Consolidate Major** - Move known-safe domains (github.com, etc.) to global
7. **Research Unknown** - Use WebSearch to assess security of new domains
8. **Enforce Limits** - Keep global ≤30, projects ≤10
9. **Sort Alphabetically** - Maintain consistent organization
10. **Update History** - Record all decisions and research
11. **Generate Report** - Comprehensive summary with recommendations

## Key Features

- **Automated Security Research**: Uses WebSearch to research unknown domains with multiple queries
- **Domain Categorization**: Intelligent sorting into 7 categories based on reach and safety
- **Decision Persistence**: Stores research and decisions in ~/.claude/run-configuration.md
- **Major Domain Detection**: Recognizes ~20 major platforms (GitHub, Stack Overflow, etc.) as always-safe
- **Limit Enforcement**: Enforces 30 global / 10 per-project domain limits
- **Redundancy Cleanup**: Removes project domains when available globally
- **Security Flagging**: Tracks suspicious domains, always re-prompts
- **Reach Analysis**: Considers cross-project usage (3+ projects = high reach)
- **Comprehensive Reporting**: Detailed change summaries and next-step recommendations

## Parameters

### auto (Optional)
- **Format**: `auto` (flag)
- **Behavior**: Auto-apply safe consolidations without prompting
- **Note**: Still prompts for security concerns or ambiguous decisions
- **Use Case**: Faster processing when you trust major domain detection

### project (Optional)
- **Format**: `project=<path>`
- **Description**: Analyze only a specific project
- **Path Requirement**: Must be under ~/git/
- **Examples**:
  - `project=~/git/cui-llm-rules`
  - `project=/Users/oliver/git/OAuth-Sheriff`

### dry-run (Optional)
- **Format**: `dry-run` (flag)
- **Behavior**: Preview changes without applying them
- **Use Case**: Understand current state and proposed changes

## Domain Categories

### ALREADY_GLOBAL
- Domains already approved in global settings
- **Action**: Remove from project settings (redundant)

### MAJOR_DOMAINS
- Known safe platforms: github.com, stackoverflow.com, anthropic.com, docs.oracle.com, etc.
- **Action**: Move to global automatically (with confirmation unless auto-mode)
- **Count**: ~20 pre-approved major domains

### HIGH_REACH
- Used in 3+ projects but not yet researched
- **Action**: Perform security research, prompt user

### RESEARCHED_SAFE
- Previously researched and approved for global
- **Action**: Move to global without re-research

### RESEARCHED_LOCAL
- Previously researched, determined to be project-specific
- **Action**: Keep in original project only

### FLAGGED
- Previously flagged with security concerns
- **Action**: Always re-prompt user (never auto-approve)

### UNKNOWN
- New domains needing security research
- **Action**: Research and prompt user

## Security Research Process

For each HIGH_REACH or UNKNOWN domain:

1. **Execute Multiple WebSearch Queries**:
   - `"{domain}" security reputation review`
   - `"{domain}" trustworthy safe website`
   - `"{domain}" website information purpose`

2. **Analyze Results for Indicators**:
   - **Green Flags**: Official docs, major company, well-known service, positive reputation
   - **Red Flags**: Malware reports, phishing, suspicious activity, no information
   - **Neutral**: Small/niche service, regional, specific use case

3. **Generate Security Assessment**:
   - Website purpose description
   - Reputation (Trusted/Unknown/Suspicious)
   - Category (documentation/API/CDN/tools)
   - List of green/red flags

4. **Prompt User for Decision**:
   - Add to global (safe and useful)
   - Keep local (safe but project-specific)
   - Reject (remove from all)
   - Skip (decide later)

5. **Record Decision**: Store in ~/.claude/run-configuration.md for future runs

## Limit Enforcement

### Global Limit: 30 Domains

**If exceeded:**
- Display least-used domains (candidates for removal)
- Options: Auto-remove lowest usage / Manual selection / Keep all (not recommended)
- Remove domains until count ≤ 30

### Project Limit: 10 Domains

**If exceeded:**
- Display project-specific domains
- Options: Keep top 10 / Move some to global / Manual selection / Keep all
- Document over-limit exceptions in .claude/run-configuration.md

## Decision History Persistence

### Global History: ~/.claude/run-configuration.md

Stores:
- Domains approved for global use (with reason and date)
- Domains kept local (with reason and date)
- Domains flagged with security concerns
- Last execution summary (date, counts)
- Domain limit status

### Project History: {project}/.claude/run-configuration.md

Stores:
- Local domains kept (project-specific)
- Rationale for each domain
- Last update timestamp

**Benefits**:
- No repeated security research
- Respects previous decisions
- Tracks domain evolution over time
- Documents security assessments

## Major Domain List (Always Safe)

Pre-approved without research:

- `github.com`, `raw.githubusercontent.com` - GitHub
- `gitlab.com` - GitLab
- `bitbucket.org` - Bitbucket
- `stackoverflow.com`, `*.stackexchange.com` - Stack Exchange
- `anthropic.com` - Anthropic
- `openai.com` - OpenAI
- `medium.com` - Medium
- `docs.oracle.com` - Oracle Java Docs
- `docs.microsoft.com` - Microsoft Docs
- `developer.mozilla.org` - MDN
- `w3.org` - W3C
- `npmjs.com` - npm
- `pypi.org` - PyPI
- `maven.apache.org` - Maven Central
- `quarkus.io` - Quarkus
- `spring.io` - Spring
- `wikipedia.org`, `wikimedia.org` - Wikipedia

## Security Red Flags

Be cautious of domains with:
- No HTTPS support
- Newly registered (may be malicious)
- Suspicious TLD (.xyz, .click, .top often problematic)
- No clear purpose (unknown/obscure)
- Malware reports in security databases
- Phishing reports (known scams)
- No online presence (can't verify legitimacy)

## Reach Threshold Guidelines

- **3+ projects**: Consider for global (research required)
- **2 projects**: Usually keep local unless major domain
- **1 project**: Always keep local (project-specific)

## Sorting Pattern

Within settings files:

1. **WebFetch Group Order**: After SlashCommand, Task, before Write
2. **Within WebFetch**:
   - Universal access first: `WebFetch(domain:*)`
   - Then alphabetically by domain name

Example:
```json
"WebFetch(domain:anthropic.com)",
"WebFetch(domain:docs.oracle.com)",
"WebFetch(domain:github.com)",
"WebFetch(domain:medium.com)",
"WebFetch(domain:raw.githubusercontent.com)",
"WebFetch(domain:stackoverflow.com)"
```

## Expected Duration

- **Small setup** (5-10 domains, 3-5 projects): 5-10 minutes
  - Scanning: 1-2 min
  - Research: 2-5 min (1 min per unknown domain)
  - Consolidation: 1-2 min

- **Medium setup** (15-25 domains, 10-15 projects): 15-30 minutes
  - Scanning: 2-3 min
  - Research: 10-20 min (5-10 unknown domains)
  - Consolidation: 3-5 min

- **Large setup** (30+ domains, 20+ projects): 30-60 minutes
  - Scanning: 3-5 min
  - Research: 20-40 min (10-20 unknown domains)
  - Limit enforcement: 5-10 min
  - Consolidation: 5-10 min

## Integration

Use this command:
- After setting up multiple projects with WebFetch needs
- Periodically to maintain clean permission configurations
- When global settings approaching 30-domain limit
- After discovering new domains that might be useful globally
- When projects have redundant domain permissions

Often used with:
- `/setup-project-permissions` - Comprehensive permission management
- Manual review of ~/.claude/settings.json and settings.local.json

## Example Output

```
╔════════════════════════════════════════════════════════════╗
║          WebFetch Domain Management Summary                ║
╔════════════════════════════════════════════════════════════╝

Projects Analyzed: 15
Unique Domains Found: 42

Global Settings Changes:
+ Added 8 domains to global
- Removed 0 redundant domains

Project Settings Changes:
- Cleaned 23 redundant domains from 12 projects
- Moved 8 domains to global
- Removed 2 rejected domains

Domain Research:
✅ 8 domains researched and approved
⚠️  2 domains flagged with security concerns
📋 5 domains kept local (project-specific)

Final Domain Counts:
- Global: 18/30 domains
- Projects over limit: 0 projects

╚════════════════════════════════════════════════════════════

Project: cui-llm-rules
Location: ~/git/cui-llm-rules

Changes:
- Removed: github.com (now in global)
- Removed: docs.oracle.com (now in global)
+ Kept: project-specific-api.com (project-specific)

Final: 3 WebFetch domains

---

✅ Updated global settings and 12 projects
✅ Updated decision history
- Global: ~/.claude/run-configuration.md
- Projects: 12 .claude/run-configuration.md files

All domain permissions are now optimized and secure! ✅
```

## Notes

- **Security research is mandatory** for unknown domains
- **User always has final say** on security concerns
- **Automatic consolidation** for major/known domains (with confirmation)
- **Limits prevent sprawl** (30 global, 10 per project)
- **History tracking prevents redundant research**
- **Handles universal access** (`WebFetch(domain:*)`) gracefully
- **Respects dry-run mode** - no file modifications in preview
- **Preserves JSON formatting** - 2-space indentation maintained

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
