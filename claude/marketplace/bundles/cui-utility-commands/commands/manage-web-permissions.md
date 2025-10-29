---
name: manage-web-permissions
description: Analyze and consolidate WebFetch domain permissions across projects with security research and validation
---

# Manage WebFetch Domains Command

Analyzes all WebFetch domain permissions across projects in ~/git/, consolidates safe and common domains to global settings, and maintains clean project-level configurations with security research and validation.

## CONTINUOUS IMPROVEMENT RULE

**CRITICAL:** Every time you execute this command and discover new patterns, security insights, or better approaches, **YOU MUST immediately update this file** with:
1. New security assessment patterns for domain categories
2. Improved reach analysis methods (frequency thresholds, cross-project usage)
3. Additional suspicious domain patterns or security red flags
4. Better domain categorization logic (CDN, documentation, tools, etc.)
5. Enhanced sorting and organization strategies
6. Any lessons learned about domain security or permission management

This ensures the command evolves and becomes more effective at managing WebFetch permissions with each execution.

## PARAMETERS

### Optional Parameters

**auto**
- Automatically apply safe consolidations without prompting
- Still prompts for security concerns or ambiguous decisions
- Skips confirmation for moving major/safe domains to global
- Example: `/manage-web-permissions auto`

**project=<path>**
- Analyze only a specific project instead of all projects
- Path must be under ~/git/
- Example: `/manage-web-permissions project=~/git/cui-llm-rules`

**dry-run**
- Preview changes without applying them
- Shows what would be moved/changed
- No modifications to settings files
- Example: `/manage-web-permissions dry-run`

## PARAMETER VALIDATION

**Step 1: Parse Parameters**

Extract parameters from command arguments:
```bash
# Check for flags
auto_mode=false
dry_run=false
specific_project=""

[[ "$args" =~ auto ]] && auto_mode=true
[[ "$args" =~ dry-run ]] && dry_run=true

# Check for project parameter
if [[ "$args" =~ project=([^ ]+) ]]; then
    specific_project="${BASH_REMATCH[1]}"
    # Remove quotes if present
    specific_project="${specific_project//\"/}"
    # Expand ~ to full path
    specific_project="${specific_project/#\~/$HOME}"
fi
```

**Step 2: Validate project Parameter (if provided)**

If `project` parameter is provided:
1. **Validate path exists:**
   - Must be a valid directory
   - Must be under ~/git/
   - If invalid, report error and exit

2. **Validate is git repository:**
   - Must contain .git directory
   - If not a git repo, report warning but continue

**Example validation:**
```
✅ Valid: project=~/git/cui-llm-rules
✅ Valid: project=/Users/oliver/git/OAuth-Sheriff
❌ Invalid: project=~/Documents/notes - Not under ~/git/
❌ Invalid: project=~/git/nonexistent - Directory doesn't exist
```

**Step 3: Validate Conflicting Parameters**

- `auto` and `dry-run` cannot be used together
- If conflicts found, report error and exit

## WORKFLOW INSTRUCTIONS

### Step 1: Read Global Settings and Extract Current WebFetch Domains

**Purpose:** Understand what domains are already globally approved before analyzing projects.

**A. Read global settings file**
```bash
global_settings="$HOME/.claude/settings.json"
if [ ! -f "$global_settings" ]; then
    echo "❌ ERROR: Global settings not found at $global_settings"
    exit 1
fi
```

**B. Parse global WebFetch permissions**
- Extract all `WebFetch(domain:*)` permissions from global allow list
- Store in `global_domains` array
- Note if `WebFetch(domain:*)` exists (universal web access)

**C. Display global WebFetch summary**
```
Global WebFetch Settings: ~/.claude/settings.json
Current domains approved globally: {count}

Universal Access: {Yes/No}
- WebFetch(domain:*) - All domains allowed
```

**D. If WebFetch(domain:*) exists globally**
```
⚠️  WARNING: Universal WebFetch Access Enabled

WebFetch(domain:*) in global settings allows ALL domains globally.
This means ALL project-level WebFetch domains are redundant.

Options:
1. Remove universal access, use specific domains only (RECOMMENDED)
2. Keep universal access, clean all project-level domains
3. Exit and review manually

Choice:
```

Based on user choice:
- **Option 1**: Remove `WebFetch(domain:*)` from global, proceed with analysis
- **Option 2**: Skip domain analysis, just clean all project domains
- **Option 3**: Exit command

### Step 2: Discover All Projects and Scan for WebFetch Domains

**A. Find all git repositories under ~/git/**

```bash
if [ -n "$specific_project" ]; then
    projects=("$specific_project")
else
    projects=($(find ~/git -maxdepth 2 -type d -name .git -exec dirname {} \;))
fi

echo "Found {count} projects to analyze"
```

**B. For each project, extract WebFetch domains**

For each project:
1. Check if `.claude/settings.local.json` exists
2. If exists, parse WebFetch permissions from allow list
3. Store in `project_domains` map: `project_path -> [domains]`
4. Track domain frequency across projects in `domain_usage_count` map

**C. Display discovery summary**
```
Project Scan Results:
- Total projects found: {count}
- Projects with settings.local.json: {count}
- Projects with WebFetch domains: {count}
- Unique domains discovered: {count}

Domain Usage Analysis:
Top domains by frequency:
1. github.com - Used in {n} projects
2. anthropic.com - Used in {n} projects
3. medium.com - Used in {n} projects
...
```

### Step 3: Read Domain Decision History

**Purpose:** Load previous security research and user decisions to avoid re-analyzing.

**A. Check if ~/.claude/run-configuration.md exists in HOME directory**
```bash
if [ -f ~/.claude/run-configuration.md ]; then
    # File exists, proceed to read
else
    # File doesn't exist, initialize empty history
fi
```

**B. Search for manage-web-permissions section**

Look for section:
```markdown
## manage-web-permissions

### Domain Security Research History

Domains researched and approved for global use:
- github.com - Major code hosting, widely trusted (2025-01-15)
- stackoverflow.com - Major Q&A site, widely trusted (2025-01-15)

Domains researched and kept local (low reach):
- example-api.com - Project-specific API, 1 project only (2025-01-15)

Domains flagged with security concerns:
- suspicious-cdn.xyz - User rejected, keep asking (2025-01-15)
```

**C. Parse domain history**
- Extract approved-global domains (skip research for these)
- Extract kept-local domains (skip research for these)
- Extract flagged domains (always prompt user for these)
- Store in respective arrays

### Step 4: Categorize Domains for Processing

**Purpose:** Organize domains into processing categories based on current state and usage.

**A. For each unique domain discovered, determine category:**

```
Categories:
1. ALREADY_GLOBAL - Already in global settings
2. MAJOR_DOMAIN - Known major/safe domain (github.com, anthropic.com, etc.)
3. HIGH_REACH - Used in 3+ projects, not yet researched
4. RESEARCHED_SAFE - Previously researched and approved for global
5. RESEARCHED_LOCAL - Previously researched and kept local
6. FLAGGED - Previously flagged with security concerns
7. UNKNOWN - Needs security research
```

**B. Define major domain patterns**

Major domains that are always safe:
```
- github.com, raw.githubusercontent.com - Code hosting
- stackoverflow.com, ux.stackexchange.com - Q&A sites
- anthropic.com, openai.com - AI providers
- medium.com - Publishing platform
- docs.oracle.com, docs.microsoft.com - Official documentation
- developer.mozilla.org, w3.org - Web standards
- npmjs.com, pypi.org, maven.apache.org - Package repositories
- wikipedia.org, wikimedia.org - Knowledge bases
```

**C. Categorize and report**
```
Domain Categorization:

ALREADY_GLOBAL ({count}):
- domain:* (universal access)

MAJOR_DOMAINS ({count}) - Safe to add globally:
1. github.com - Used in {n} projects, code hosting
2. anthropic.com - Used in {n} projects, AI provider

HIGH_REACH ({count}) - Need research:
1. example-api.com - Used in {n} projects
2. custom-cdn.net - Used in {n} projects

RESEARCHED_SAFE ({count}) - Previously approved:
1. trusted-docs.io - Previously researched (2025-01-15)

RESEARCHED_LOCAL ({count}) - Low reach, keep local:
1. project-specific-api.com - 1 project only

FLAGGED ({count}) - Security concerns:
1. suspicious-domain.xyz - User rejected previously

UNKNOWN ({count}) - Need research:
1. new-domain.com - Used in {n} projects
```

### Step 5: Process ALREADY_GLOBAL Domains

**Purpose:** Clean up project-level domains that are redundant.

**A. For each domain in ALREADY_GLOBAL category:**
1. Find all projects using this domain
2. Mark for removal from project settings
3. Track cleanup actions

**B. Report redundant domains**
```
Redundant Project-Level Domains ({count}):

These domains are already globally approved and will be removed from projects:

github.com:
- ~/git/cui-llm-rules/.claude/settings.local.json
- ~/git/OAuth-Sheriff/.claude/settings.local.json
- ~/git/project-3/.claude/settings.local.json

Total: {n} domains across {m} projects marked for cleanup
```

**C. If dry-run:**
- Display what would be removed
- Skip to next step

**D. If auto-mode or user confirms:**
- Remove redundant domains from each project's settings.local.json
- Report: `✅ Cleaned {count} redundant domains from {n} projects`

### Step 6: Process MAJOR_DOMAINS

**Purpose:** Move known-safe high-usage domains to global settings.

**A. Display major domains found**
```
Major Domains Found ({count}):

Safe, widely-trusted domains used across projects:

1. github.com
   - Usage: {n} projects
   - Category: Code hosting platform
   - Security: Widely trusted, major tech company
   - Action: Move to global settings

2. stackoverflow.com
   - Usage: {n} projects
   - Category: Developer Q&A
   - Security: Widely trusted, Stack Exchange network
   - Action: Move to global settings
```

**B. If auto-mode:**
- Automatically add all major domains to global
- Remove from all project settings
- Report: `✅ Added {count} major domains to global, cleaned from projects`

**C. If NOT auto-mode:**
```
Add all {count} major domains to global settings?
These are widely-trusted domains used across multiple projects.

1. Yes - Add all to global (RECOMMENDED)
2. Review each domain individually
3. Skip - Keep as-is

Choice:
```

- If Yes: Add all to global, clean projects
- If Review: Prompt for each domain individually
- If Skip: Continue to next step

### Step 7: Research and Process HIGH_REACH and UNKNOWN Domains

**Purpose:** Perform security research on domains that need evaluation.

**A. Combine HIGH_REACH and UNKNOWN domains**
- Create list of domains needing research
- Sort by usage count (highest first)

**B. For each domain requiring research:**

```
Researching Domain {n}/{total}: {domain}
Usage: {count} projects
First seen: {project-name}

Performing security research...
```

**C. Execute web research using WebSearch**

Research queries:
1. `"{domain}" security reputation review`
2. `"{domain}" trustworthy safe website`
3. `"{domain}" website information purpose`

Analyze results for:
- **Green flags**: Official documentation, major company, well-known service, positive reputation
- **Red flags**: Malware reports, phishing, suspicious activity, no information found
- **Neutral**: Small/niche service, regional, specific use case

**D. Assess security based on research**

```
Research Results for {domain}:

Website Purpose: {description from research}
Reputation: {Trusted/Unknown/Suspicious}
Category: {documentation/API/CDN/tools/etc}

Security Assessment:
✅ Green Flags:
- Official documentation site for {technology}
- Operated by {reputable organization}
- Widely referenced in technical community

⚠️  Red Flags:
- {any security concerns found}
- {any suspicious patterns}

Recommendation: {APPROVE_GLOBAL/KEEP_LOCAL/REJECT}
```

**E. Prompt user for decision**

```
Domain: {domain}
Usage: {count} projects
Security: {assessment summary}

What should we do with this domain?

1. Add to global - Safe and useful across projects
2. Keep local - Safe but project-specific
3. Reject - Remove from all projects
4. Skip - Decide later

Choice:
```

**F. Handle security concerns**

If red flags or suspicious patterns detected:
```
⚠️  SECURITY CONCERN: {domain}

Issues found:
- {red flag 1}
- {red flag 2}

This domain requires your review before proceeding.
Research summary: {summary}

Approve this domain?
1. Yes - I trust this domain
2. No - Remove from all projects
3. Review manually - Skip for now

Choice:
```

**CRITICAL:** ALWAYS prompt user when security concerns detected, even in auto-mode.

**G. Apply decision**

Based on user choice:
- **Add to global**: Add to global settings, remove from projects, record in history
- **Keep local**: Remove from other projects (keep in original project only), record in history
- **Reject**: Remove from all projects, record as flagged in history
- **Skip**: No action, do not record in history (will re-prompt next run)

### Step 8: Process Remaining Domains

**A. Handle RESEARCHED_SAFE domains**
- Add to global settings if not already there
- Remove from project settings
- No prompts needed (already researched)

**B. Handle RESEARCHED_LOCAL domains**
- Keep in their respective projects
- No changes needed
- Report: `ℹ️  {count} domains kept local (previously assessed)`

**C. Handle FLAGGED domains**
- Always prompt user for each flagged domain
- Show previous flag reason
- Allow user to re-assess or keep flagged

### Step 9: Enforce Domain Limits

**Purpose:** Ensure project and global domain counts stay within limits.

**A. Check global domain count**

```bash
global_domain_count=$(count domains in global allow list)

if [ "$global_domain_count" -gt 30 ]; then
    echo "⚠️  Global domain count exceeds limit: $global_domain_count/30"
fi
```

**B. If global exceeds 30 domains:**

```
Global Domain Limit Exceeded: {count}/30

Least useful domains (candidates for removal):
1. {domain} - Used in {n} projects (lowest usage)
2. {domain} - Used in {n} projects
...

Options:
1. Auto-remove lowest usage domains to reach limit
2. Manually select domains to remove
3. Keep all (not recommended - over limit)

Choice:
```

Based on choice:
- **Auto-remove**: Remove domains with lowest cross-project usage until count ≤ 30
- **Manual**: Prompt for each candidate domain
- **Keep all**: Warn user but proceed

**C. For each project, check domain count**

```bash
for project in "${!project_domains[@]}"; do
    domain_count=$(count WebFetch domains in project)
    if [ "$domain_count" -gt 10 ]; then
        echo "⚠️  Project domain limit exceeded: $project ($domain_count/10)"
    fi
done
```

**D. If project exceeds 10 domains:**

```
Project Domain Limit Exceeded: {project}
Current domains: {count}/10

Project-specific domains:
1. {domain} - {description if available}
2. {domain}
...

Options:
1. Keep top 10 most relevant (remove others)
2. Move some to global if widely useful
3. Manually select domains to keep
4. Keep all (not recommended - over limit)

Choice:
```

Based on choice:
- **Keep top 10**: Keep most relevant/used, remove rest
- **Move to global**: Prompt which domains to move to global
- **Manual**: Prompt for each domain
- **Keep all**: Warn user but proceed

**E. Document over-limit decisions**

Update .claude/run-configuration.md for this project:
```markdown
### Domain Limit Status

Note: This project has {count} WebFetch domains (limit: 10)
Domains kept despite limit (user approved):
- {domain} - {reason}
- {domain} - {reason}
```

### Step 10: Sort All Domain Lists

**Purpose:** Maintain consistent, alphabetical organization.

**A. Sort global domains**

Sorting pattern (following setup-project-permissions):
1. Universal access first: `WebFetch(domain:*)`
2. Then alphabetically by domain name

```
WebFetch(domain:*)
WebFetch(domain:anthropic.com)
WebFetch(domain:docs.oracle.com)
WebFetch(domain:github.com)
WebFetch(domain:medium.com)
WebFetch(domain:raw.githubusercontent.com)
WebFetch(domain:stackoverflow.com)
...
```

**B. Sort each project's domains**

Same pattern:
1. Universal access if exists (should be removed though)
2. Alphabetically by domain name

**C. Sort within full permission list**

Within each settings file, maintain this order:
1. Bash(...) commands
2. Edit(...) permissions
3. Read(...) permissions
4. Skill(...) permissions
5. SlashCommand(...) permissions
6. Task(...) permissions
7. WebFetch(...) permissions
8. WebSearch
9. Write(...) permissions

### Step 11: Apply All Changes

**Purpose:** Write all updates to settings files.

**A. Display comprehensive change summary**

```
╔════════════════════════════════════════════════════════════╗
║          WebFetch Domain Management Summary                ║
╔════════════════════════════════════════════════════════════╝

Projects Analyzed: {count}
Unique Domains Found: {count}

Global Settings Changes:
+ Added {count} domains to global
- Removed {count} redundant domains

Project Settings Changes:
- Cleaned {count} redundant domains from {n} projects
- Moved {count} domains to global
- Removed {count} rejected domains

Domain Research:
✅ {count} domains researched and approved
⚠️  {count} domains flagged with security concerns
📋 {count} domains kept local (project-specific)

Final Domain Counts:
- Global: {count}/30 domains
- Projects over limit: {count} projects

╚════════════════════════════════════════════════════════════
```

**B. Show detailed changes per project**

For each project with changes:
```
Project: {project-name}
Location: {path}

Changes:
- Removed: {domain} (now in global)
- Removed: {domain} (now in global)
+ Kept: {domain} (project-specific)

Final: {count} WebFetch domains
```

**C. If dry-run:**
```
🔍 DRY RUN MODE - No changes applied

The above changes would be applied to:
- Global: ~/.claude/settings.json
- Projects: {count} settings.local.json files

To apply these changes, run without dry-run flag.
```
- Exit without modifying files

**D. If NOT dry-run:**
- Write updated global settings.json
- Write updated settings.local.json for each changed project
- Preserve JSON formatting (2-space indent)
- Report: `✅ Updated global settings and {count} projects`

### Step 12: Update Decision History

**Purpose:** Record all decisions for future runs.

**A. Update .claude/run-configuration.md in HOME directory**

Location: `~/.claude/run-configuration.md`

**B. Create or update manage-web-permissions section**

```markdown
## manage-web-permissions

### Last Execution

- Date: {timestamp}
- Projects analyzed: {count}
- Domains processed: {count}
- Domains moved to global: {count}
- Domains kept local: {count}
- Domains rejected: {count}

### Domain Security Research History

Domains researched and approved for global use:
- {domain} - {reason} ({date})
- {domain} - {reason} ({date})

Domains researched and kept local (low reach):
- {domain} - {reason} ({date})
- {domain} - {reason} ({date})

Domains flagged with security concerns:
- {domain} - {issue} ({date})
- {domain} - {issue} ({date})

### Domain Limits Status

Global domains: {count}/30
Projects over limit (10): {count}

Projects requiring attention:
- {project} - {count} domains
```

**C. For each project, update its .claude/run-configuration.md**

Add or update section:
```markdown
## manage-web-permissions

### WebFetch Domains for This Project

Local domains kept (project-specific):
- {domain} - {reason}
- {domain} - {reason}

Note: {count} domains are available globally
Last updated: {timestamp}
```

**D. Report update**
```
✅ Updated decision history
- Global: ~/.claude/run-configuration.md
- Projects: {count} .claude/run-configuration.md files
```

### Step 13: Generate Final Report

**A. Display comprehensive final report**

```
╔════════════════════════════════════════════════════════════╗
║          WebFetch Domain Management Complete               ║
╔════════════════════════════════════════════════════════════╝

Global Settings: ~/.claude/settings.json
- Total WebFetch domains: {count}/30
- Added this run: {count}
- Domains available to all projects: ✅

Project Settings:
- Projects cleaned: {count}
- Redundant domains removed: {count}
- Projects within limits: {count}/{total}
- Projects over limit: {count}

Security Research:
- Domains researched: {count}
- Approved for global: {count}
- Kept local: {count}
- Rejected/removed: {count}
- Security concerns flagged: {count}

Next Steps:
{if projects over limit}
⚠️  {count} projects exceed 10-domain limit
    Review these projects and consider:
    - Moving common domains to global
    - Removing unused domains
    - Documenting why specific domains are needed
{endif}

{if global near limit}
⚠️  Global settings at {count}/30 domains
    Consider removing rarely-used domains if adding more
{endif}

All domain permissions are now optimized and secure! ✅

╚════════════════════════════════════════════════════════════
```

**B. Suggest next actions**

If issues found:
```
Recommended Actions:

1. Review projects over domain limit:
   {list projects}

2. Consider these domains for global promotion:
   {list candidates with high usage}

3. Remove rarely-used domains from global:
   {list domains with low usage}

Run /manage-web-permissions again after making changes.
```

## CRITICAL RULES

### Security Rules

- **NEVER add domains to global without security research** - Always research unknown domains
- **ALWAYS prompt user for security concerns** - Even in auto-mode, security requires user approval
- **NEVER trust domain without verification** - Use WebSearch to validate safety
- **ALWAYS document security research** - Record findings for future reference
- **FLAG suspicious domains** - Track domains with security concerns separately
- **VALIDATE domain patterns** - Ensure domains follow valid format (no wildcards in domain names)

### Research Rules

- **USE comprehensive web search** - Multiple queries for thorough research
- **ANALYZE results critically** - Look for both green and red flags
- **DOCUMENT findings** - Store research summary with decisions
- **RESPECT user decisions** - Don't re-prompt for previously decided domains
- **RE-PROMPT flagged domains** - Always ask about previously rejected domains

### Data Integrity Rules

- **NEVER lose existing permissions** - Only remove with user approval or redundancy
- **PRESERVE JSON formatting** - Use 2-space indentation
- **VALIDATE JSON structure** - Before and after all changes
- **BACKUP mentally** - Know original state before modifications
- **ATOMIC changes** - All changes succeed or none apply

### Limit Enforcement Rules

- **ENFORCE 30 global domain limit** - Remove least useful if exceeded
- **ENFORCE 10 project domain limit** - Prompt user for cleanup if exceeded
- **DOCUMENT limit exceptions** - If user keeps over-limit, record reason
- **SUGGEST optimizations** - Help user stay within limits

### User Experience Rules

- **SHOW clear progress** - Report each step of analysis
- **EXPLAIN security findings** - Help user understand risks
- **PROVIDE recommendations** - Guide user to best practices
- **RESPECT decisions** - Don't re-prompt for recorded choices
- **CLEAR prompts** - Number choices, explain consequences

## USAGE EXAMPLES

### Analyze All Projects
```
/manage-web-permissions
```
- Scans all projects under ~/git/
- Researches unknown domains
- Prompts for each decision
- Consolidates to global where appropriate
- Cleans up project settings
- Enforces limits

### Auto-Mode (Safe Consolidation)
```
/manage-web-permissions auto
```
- Automatically moves major domains to global
- Automatically cleans redundant project domains
- Still prompts for security concerns
- Faster for known-safe domains

### Single Project Analysis
```
/manage-web-permissions project=~/git/cui-llm-rules
```
- Analyzes only specified project
- Compares against global settings
- Suggests consolidation opportunities
- Updates only that project

### Preview Mode
```
/manage-web-permissions dry-run
```
- Shows what would be changed
- Performs security research
- No modifications applied
- Useful for understanding current state

### Combined Parameters
```
/manage-web-permissions project=~/git/OAuth-Sheriff auto
```
- Analyzes single project
- Auto-applies safe changes
- Still prompts for security concerns

## IMPORTANT NOTES

### Domain Research Sources

When researching domains:
1. **Official documentation sites** - Immediate green flag
2. **Major tech companies** - Generally trusted
3. **Well-known services** - Check reputation carefully
4. **CDN providers** - Verify legitimacy
5. **Unknown domains** - Require thorough research

### Major Domain List

Always safe to add globally (no research needed):
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

### Security Red Flags

Be cautious of domains with:
- **No HTTPS support** - Security risk
- **Newly registered** - May be malicious
- **Suspicious TLD** - `.xyz`, `.click`, `.top` often problematic
- **No clear purpose** - Unknown/obscure sites
- **Malware reports** - Found in security databases
- **Phishing reports** - Known for scams
- **No online presence** - Can't verify legitimacy

### Reach Threshold

Guidelines for global vs local:
- **3+ projects**: Consider for global (research required)
- **2 projects**: Usually keep local unless major domain
- **1 project**: Always keep local, project-specific

### Sorting Pattern

Follow setup-project-permissions ordering:
1. Group all WebFetch together
2. Universal access (`domain:*`) first
3. Then alphabetically by domain
4. Within full allow list, WebFetch comes after SlashCommand and Task

### State Persistence

Decision history stored in:
- **Global**: `~/.claude/run-configuration.md` (shared across projects)
- **Per-project**: `.claude/run-configuration.md` (project-specific notes)

Benefits:
- No repeated security research
- Respects previous decisions
- Tracks domain evolution over time
- Documents security assessments

## LESSONS LEARNED

### 2025-01-27: Initial Implementation

**Design Decisions:**
- Security research is mandatory for unknown domains
- User always has final say on security concerns
- Automatic consolidation for major/known domains
- Limits prevent permission sprawl
- History tracking prevents redundant research

**Validation:**
- Must handle `WebFetch(domain:*)` universal access gracefully
- Need clear categorization for efficient processing
- Security research must be thorough but not blocking
- Limits should be enforced but with user override capability
