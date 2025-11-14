# Lessons Learned - Permission Management

Real-world insights and lessons from managing Claude Code permissions across multiple projects.

## Common Anti-Patterns

> For formal anti-pattern definitions and detection algorithms, see [permission-anti-patterns.md](../standards/permission-anti-patterns.md).

### Anti-Pattern 1: Permission Explosion

**What Happened:**
Project started with 5 permissions. After 3 months, had 50+ permissions with many duplicates and overlapping patterns.

**Root Cause:**
- Added permissions reactively without reviewing existing ones
- Never removed permissions when features were deprecated
- Multiple developers adding permissions without coordination

**Solution:**
- Regular quarterly permission audits
- Consolidate permissions before adding new ones
- Use broader patterns instead of many specific ones
- Document permission purpose in comments

**Example Fix:**
```
Before (12 permissions):
Bash(git:status)
Bash(git:log)
Bash(git:diff)
Bash(git:add)
Bash(git:commit)
Bash(git:push)
Bash(git:pull)
Bash(git:checkout)
Bash(git:branch)
Bash(git:merge)
Bash(git:rebase)
Bash(git:stash)

After (1 permission):
Bash(git:*)
```

### Anti-Pattern 2: Overly Specific File Paths

**What Happened:**
Settings had 20+ Read permissions for individual files in the same directory structure.

**Root Cause:**
- Added permission for each new file encountered
- Didn't realize glob patterns could cover multiple files
- Fear of being "too permissive"

**Solution:**
- Use directory-level glob patterns
- Balance security with maintainability
- Trust Claude Code's permission system

**Example Fix:**
```
Before (20+ permissions):
Read(//project/src/main/Component1.java)
Read(//project/src/main/Component2.java)
Read(//project/src/main/Component3.java)
...

After (1 permission):
Read(//project/src/**)
```

### Anti-Pattern 3: WebFetch Without Security Review

**What Happened:**
Added multiple WebFetch domains quickly without vetting, later discovered one was compromised.

**Root Cause:**
- Rushed to unblock development
- Assumed all documentation sites are trustworthy
- No security assessment process

**Solution:**
- Always check domain against web-security-standards
- Research domain history and reputation
- Document security assessment in commit message
- Remove domains when no longer needed

**Lesson:**
Even seemingly harmless documentation sites can be compromised. Always verify.

### Anti-Pattern 4: Mixing Absolute and Relative Paths

**What Happened:**
Read permissions mixed `//absolute/path/**` and `relative/path/**`, causing confusion about what was actually permitted.

**Root Cause:**
- Inconsistent permission addition
- Multiple developers with different understanding
- No standard documented

**Solution:**
- Establish path format convention (prefer absolute `//` paths)
- Document convention in project README
- Validate format during permission audits

**Example Standard:**
```
Always use absolute paths for project files:
✓ Read(//~/git/project/**)
✗ Read(project/**)

Use relative only for Claude-specific:
✓ Read(//.claude/**)
```

### Anti-Pattern 5: Never Removing Permissions

**What Happened:**
Settings file grew to 100+ permissions over a year. Many were for deprecated features or removed dependencies.

**Root Cause:**
- No process for permission removal
- Fear of breaking something by removing
- No tracking of why permissions were added

**Solution:**
- Document why each permission is needed
- Review and prune during regular audits
- Remove when feature/dependency removed
- Test after removal (permissions fail safely)

**Lesson:**
Permissions should be treated like dependencies - add intentionally, remove when unused.

## Best Practices from Experience

> For formal validation and architectural standards, see [permission-validation-standards.md](../standards/permission-validation-standards.md) and [permission-architecture.md](../standards/permission-architecture.md).

### Practice 1: Start Narrow, Expand as Needed

**Lesson:**
Start with specific permissions and broaden only when patterns emerge.

**Example:**
```
Day 1: Bash(mvn:test)
Week 1: Bash(mvn:clean), Bash(mvn:verify)
Month 1: Bash(mvn:*) [after seeing we use many mvn commands]
```

**Why This Works:**
- Understand actual usage before granting broad access
- Easier to broaden than narrow
- Documents actual needs over time

### Practice 2: Group Related Permissions

**Lesson:**
Organize permissions by purpose/feature for easier maintenance.

**Example:**
```json
// Git operations
{"tool": "Bash", "pattern": "git:*"},

// Maven build
{"tool": "Bash", "pattern": "./mvnw:*"},

// Project source (read-only)
{"tool": "Read", "pattern": "//~/git/project/**"},

// Claude configuration (read/write)
{"tool": "Read", "pattern": "//.claude/**"},
{"tool": "Write", "pattern": "//.claude/**"},
{"tool": "Edit", "pattern": "//.claude/**"}
```

**Why This Works:**
- Easy to review related permissions together
- Clear what each group enables
- Simplifies removal of feature-specific permissions

### Practice 3: Document Permission Purpose

**Lesson:**
Add comments explaining why non-obvious permissions exist.

**Example:**
```json
// Legacy: Direct AsciiDoc script access (prefer using asciidoc-link-verifier agent instead)
{"tool": "Bash", "pattern": "python3 ~/git/cui-llm-rules/scripts/verify-adoc-links.py:*"},

// Required for custom build wrapper script
{"tool": "Bash", "pattern": "~/git/project/scripts/build-wrapper.sh:*"}
```

**Why This Works:**
- Future you/others understand the purpose
- Easier to identify when permission is no longer needed
- Documents unusual or project-specific patterns

### Practice 4: Prefer Bundle Wildcards for Skills

**Lesson:**
Use `bundle:name:*` instead of individual skill permissions when using multiple skills from one bundle.

**Example:**
```
Before (5 permissions):
Skill(cui-java-skills:cui-java-core)
Skill(cui-java-skills:cui-java-cdi)
Skill(cui-java-skills:cui-java-unit-testing)
Skill(cui-java-skills:cui-javadoc)
Skill(cui-java-skills:cui-frontend-development)

After (1 permission):
Skill(cui-java-skills:*)
```

**Why This Works:**
- Simpler maintenance
- Automatically includes new skills from bundle
- Reduces permission count

### Practice 5: Regular Permission Audits

**Lesson:**
Schedule quarterly reviews to clean up permissions.

**Audit Checklist:**
```
□ Remove duplicate permissions
□ Consolidate specific permissions into broader patterns
□ Remove permissions for deprecated features
□ Verify WebFetch domains are still needed and trusted
□ Update file path patterns if project structure changed
□ Check for unused Bash command permissions
□ Validate all custom script paths still exist
```

**Why This Works:**
- Prevents permission bloat
- Keeps settings file maintainable
- Identifies security issues (compromised domains, deprecated tools)

## Security Lessons

### Lesson 1: Domain Compromise is Real

**Experience:**
Approved WebFetch for a popular tutorial site. Six months later, site was compromised and serving malware.

**What We Learned:**
- Even established sites can be compromised
- Monitor security news for approved domains
- Have process for emergency domain removal
- Consider domain necessity vs. convenience

**New Practice:**
- Re-assess WebFetch domains quarterly
- Subscribe to security advisories for critical domains
- Remove domains immediately upon compromise reports

### Lesson 2: Script Paths Can Be Dangerous

**Experience:**
Allowed `Bash(scripts/**:*)` thinking it was scoped to project scripts. User had a `~/scripts/` directory that became accessible.

**What We Learned:**
- Relative paths can match unexpected locations
- Always use absolute paths for script permissions
- Test permission scope before committing

**New Practice:**
```
Never:  Bash(scripts/**:*)
Always: Bash(~/git/project/scripts/**:*)
```

### Lesson 3: Wildcard Bash Can Be Too Broad

**Experience:**
Granted `Bash(*:*)` to "make everything work". Later realized this allowed any command execution.

**What We Learned:**
- Understand what wildcards grant
- Prefer specific commands even if longer list
- Only use broad patterns for truly safe tools

**New Practice:**
```
Safe broad patterns:
✓ Bash(git:*)
✓ Bash(ls:*)
✓ Bash(cat:*)

Review carefully:
⚠ Bash(npm:*)   [can install packages]
⚠ Bash(docker:*) [can run containers]

Never:
✗ Bash(*:*)     [any command]
```

## Project-Specific Insights

### Multi-Repository Projects

**Challenge:**
Project spread across 5 Git repositories required Read access to all.

**Solution:**
```json
{"tool": "Read", "pattern": "//~/git/project-main/**"},
{"tool": "Read", "pattern": "//~/git/project-api/**"},
{"tool": "Read", "pattern": "//~/git/project-ui/**"},
{"tool": "Read", "pattern": "//~/git/project-docs/**"},
{"tool": "Read", "pattern": "//~/git/project-tests/**"}
```

**Alternative Considered:**
```json
{"tool": "Read", "pattern": "//~/git/project-*/**"}
```

**Why Not Used:**
Glob at repository level could match unintended directories like `project-archive` or `project-temp`.

**Lesson:**
Be explicit with multi-repo patterns; security over convenience.

### Maven Wrapper vs. System Maven

**Challenge:**
Some projects use `./mvnw`, others use system `mvn`. Needed both patterns.

**Solution:**
```json
{"tool": "Bash", "pattern": "./mvnw:*"},
{"tool": "Bash", "pattern": "mvn:*"}
```

**Lesson:**
Don't assume tool consistency across projects. Support both wrapper and system versions.

### Custom Script Permissions

**Challenge:**
Project had custom validation scripts that Claude needed to run.

**Solution (Preferred - Marketplace Bundle):**
```json
// Documentation scripts via marketplace bundle agents
// Use specialized agents instead of direct script permissions
```

Agents available:
- `asciidoc-format-validator` - Format validation
- `asciidoc-auto-formatter` - Auto-fix formatting
- `asciidoc-link-verifier` - Link verification

Agents have built-in access to scripts at:
`./.claude/skills/cui-documentation/scripts/`

**Alternative Solution (Direct Script Access):**
```json
// Legacy script paths (backward compatibility)
{"tool": "Bash", "pattern": "~/git/cui-llm-rules/scripts/asciidoc-validator.sh:*"},
{"tool": "Bash", "pattern": "python3 ~/git/cui-llm-rules/scripts/verify-adoc-links.py:*"}
```

**Lesson:**
- Prefer marketplace bundle agents over direct script permissions
- Agents provide better integration with standards and workflows
- Use absolute paths for custom scripts when direct access needed
- Document why custom scripts need permissions
- Consider migrating scripts to marketplace bundles for reusability

### Bundle Development Workflow

**Challenge:**
Developing Claude Code marketplace bundles required access to multiple bundle directories.

**Solution:**
```json
{"tool": "Read", "pattern": "//~/git/cui-llm-rules/**"},
{"tool": "Write", "pattern": "//~/git/cui-llm-rules/**"},
{"tool": "Edit", "pattern": "//~/git/cui-llm-rules/**"}
```

**Lesson:**
Bundle development needs broad access to bundle structure. This is appropriate for development, would be scoped tighter for production use.

## Migration Lessons

### Migrating from Global to Project-Specific

**Experience:**
Started with all permissions in global `~/.claude/settings.json`, later moved to project-specific.

**Process:**
1. Identify project-specific vs. truly global permissions
2. Create `.claude/settings.json` in project
3. Move project permissions to project file
4. Keep only common utilities in global

**Result:**
```
Global (~/.claude/settings.json):
- Common tools: git, ls, cat, echo
- Generic utilities: npm, python, docker
- Universal skills: diagnostic-patterns

Project (.claude/settings.json):
- Project file paths
- Project-specific scripts
- Project-specific commands/skills
- Domain-specific WebFetch permissions
```

**Lesson:**
Project-specific permissions belong in project settings. Global should only have truly universal permissions.

### Consolidating Duplicate Patterns Across Projects

**Experience:**
Five projects all had similar but slightly different permission sets.

**Solution:**
- Created standard permission template
- Identified common patterns (git, maven, npm)
- Documented in project setup guide
- New projects start with template

**Template:**
```json
{
  "allowedTools": [
    // Version control
    {"tool": "Bash", "pattern": "git:*"},

    // Build tools
    {"tool": "Bash", "pattern": "./mvnw:*"},
    {"tool": "Bash", "pattern": "npm:*"},

    // File operations
    {"tool": "Bash", "pattern": "ls:*"},
    {"tool": "Bash", "pattern": "cat:*"},

    // Project access (customize path)
    {"tool": "Read", "pattern": "//~/git/PROJECT_NAME/**"},

    // Claude config
    {"tool": "Read", "pattern": "//.claude/**"},
    {"tool": "Write", "pattern": "//.claude/**"},
    {"tool": "Edit", "pattern": "//.claude/**"}
  ]
}
```

**Lesson:**
Standardize common patterns across projects to reduce setup time and ensure consistency.

## Key Takeaways

1. **Start specific, expand when justified** - Easier to add than remove
2. **Audit regularly** - Quarterly reviews prevent bloat
3. **Document non-obvious permissions** - Future you will thank you
4. **Consolidate before adding** - Check if existing permission could be broadened
5. **Security is not optional** - Especially for WebFetch domains
6. **Use absolute paths** - Prevents unexpected matches
7. **Group related permissions** - Improves maintainability
8. **Template common patterns** - Standardize across projects
9. **Remove unused permissions** - Treat like dependencies
10. **Test permission changes** - Fail-safe system makes testing easy
