# Permission Validation Standards

Standards and patterns for validating and maintaining Claude Code permissions in settings files.

## Validation Criteria

### Format Validation

**Bash Command Patterns:**
```json
{
  "tool": "Bash",
  "pattern": "command:*"
}
```

**Requirements:**
- Must use specific command followed by `:*` wildcard
- Commands must be exact (e.g., `git:*`, not `git*` or `git:**`)
- One permission per command pattern
- No shell operators in pattern (&&, ||, ;, |)

**Read/Write/Edit File Patterns:**
```json
{
  "tool": "Read",
  "pattern": "//path/to/**"
}
```

**Requirements:**
- Must use `//` prefix for absolute paths
- Supports glob patterns (`**`, `*`)
- No redundant permissions (e.g., `//foo/**` makes `//foo/bar/**` redundant)
- Paths must be valid and exist

**Skill Patterns:**
```json
{
  "tool": "Skill",
  "pattern": "plugin:skill-name"
}
```

**Requirements:**
- Format: `plugin:skill-name` or `bundle:skill-name:*`
- Must reference existing skill in loaded plugins
- Use `:*` suffix for all skills in a bundle

**SlashCommand Patterns:**
```json
{
  "tool": "SlashCommand",
  "pattern": "/command-name:*"
}
```

**Requirements:**
- Must start with `/`
- Use `:*` suffix for parameterized commands
- Must reference existing command in loaded plugins

**WebFetch Patterns:**
```json
{
  "tool": "WebFetch",
  "pattern": "domain:example.com"
}
```

**Requirements:**
- Must use `domain:` prefix
- Domain only (no protocol, path, or port)
- Must pass security assessment (see web-security-standards skill)
- No wildcard domains (e.g., `domain:*.com` is invalid)

### Structural Validation

**No Duplicates:**
- Same tool + same pattern = duplicate (remove)
- Broader pattern makes specific pattern redundant:
  - `Bash(git:*)` makes `Bash(git:status)` redundant
  - `Read(//project/**)` makes `Read(//project/src/**)` redundant

**Proper Organization:**
- Group by tool type
- Order within tool type: specific before broad, alphabetical
- Consistent formatting and spacing

**Security Validation:**
- No overly permissive patterns without justification
- WebFetch domains must be vetted (see domain-security-assessment.md)
- File access patterns must be scoped appropriately
- Bash commands must be safe operations

## Common Validation Issues

### Issue 1: Duplicate Permissions

**Problem:**
```json
{"tool": "Bash", "pattern": "git:*"},
{"tool": "Bash", "pattern": "git:status"}
```

**Fix:** Remove the specific permission (second one) as it's covered by the wildcard.

### Issue 2: Incorrect Path Format

**Problem:**
```json
{"tool": "Read", "pattern": "/Users/oliver/project/**"}
```

**Fix:** Use `//` prefix for absolute paths:
```json
{"tool": "Read", "pattern": "//Users/oliver/project/**"}
```

### Issue 3: Malformed Bash Pattern

**Problem:**
```json
{"tool": "Bash", "pattern": "git*"}
{"tool": "Bash", "pattern": "git:**"}
```

**Fix:** Use correct format with colon:
```json
{"tool": "Bash", "pattern": "git:*"}
```

### Issue 4: Redundant Permissions

**Problem:**
```json
{"tool": "Read", "pattern": "//project/**"},
{"tool": "Read", "pattern": "//project/src/**"},
{"tool": "Read", "pattern": "//project/tests/**"}
```

**Fix:** Keep only the broadest pattern:
```json
{"tool": "Read", "pattern": "//project/**"}
```

### Issue 5: WebFetch with Protocol

**Problem:**
```json
{"tool": "WebFetch", "pattern": "domain:https://docs.example.com"}
```

**Fix:** Domain only, no protocol:
```json
{"tool": "WebFetch", "pattern": "domain:docs.example.com"}
```

### Issue 6: Skill Format Variations

**Problem:**
```json
{"tool": "Skill", "pattern": "my-skill"},
{"tool": "Skill", "pattern": "plugin/my-skill"},
{"tool": "Skill", "pattern": "bundle:my-bundle:my-skill"}
```

**Fix:** Use consistent plugin format:
```json
{"tool": "Skill", "pattern": "plugin:my-skill"}
```
Or bundle wildcard:
```json
{"tool": "Skill", "pattern": "bundle:my-bundle:*"}
```

## Validation Process

### Step 1: Format Check
```
For each permission:
1. Verify tool field is valid Claude Code tool
2. Verify pattern matches required format for tool type
3. Check for syntax errors (missing colons, incorrect prefixes)
4. Validate paths exist (for Read/Write/Edit)
```

### Step 2: Duplication Check
```
1. Group permissions by tool
2. Sort by pattern specificity (broad to specific)
3. Identify exact duplicates (same tool + pattern)
4. Identify redundant permissions (specific covered by broad)
5. Mark duplicates/redundancies for removal
```

### Step 3: Security Check
```
1. For WebFetch: validate each domain against security standards
2. For Bash: verify commands are safe operations
3. For file access: ensure appropriate scope
4. Flag overly permissive patterns for review
```

### Step 4: Organization Check
```
1. Verify permissions grouped by tool
2. Check alphabetical ordering within tool groups
3. Validate consistent formatting
4. Ensure no mixing of permission types
```

### Step 5: Reference Check
```
1. For Skills: verify skill exists in loaded plugins
2. For SlashCommands: verify command exists
3. For file paths: check paths are valid
4. Flag broken references
```

## Permission Scoping Best Practices

### File Access Scoping

**Too Broad (Avoid):**
```json
{"tool": "Read", "pattern": "//**"}
```

**Appropriately Scoped:**
```json
{"tool": "Read", "pattern": "//~/git/project/**"},
{"tool": "Read", "pattern": "//.claude/**"}
```

### Bash Command Scoping

**Too Broad (Avoid):**
```json
{"tool": "Bash", "pattern": "**"}
```

**Appropriately Scoped:**
```json
{"tool": "Bash", "pattern": "git:*"},
{"tool": "Bash", "pattern": "npm:*"},
{"tool": "Bash", "pattern": "ls:*"}
```

### WebFetch Scoping

**Never Use (Invalid):**
```json
{"tool": "WebFetch", "pattern": "domain:*"}
```

**Appropriately Scoped:**
```json
{"tool": "WebFetch", "pattern": "domain:docs.anthropic.com"},
{"tool": "WebFetch", "pattern": "domain:api.github.com"}
```

## Automated Validation Rules

### Rule 1: Pattern Format
- `Bash`: Must match `^[a-zA-Z0-9_-]+:\*$`
- `Read/Write/Edit`: Must start with `//` or be relative path
- `Skill`: Must match `^(plugin|bundle):[a-zA-Z0-9_-]+(:[a-zA-Z0-9_-]+)?(\*)?$`
- `SlashCommand`: Must match `^/[a-zA-Z0-9_-]+(:\*)?$`
- `WebFetch`: Must match `^domain:[a-zA-Z0-9.-]+\.[a-z]{2,}$`

### Rule 2: Duplication Detection
```
For tool T and patterns P1, P2:
  If P1 == P2: Duplicate (remove P2)
  If P1 is glob and P2 matches P1: Redundant (remove P2)
```

### Rule 3: Security Requirements
```
For WebFetch permissions:
  - Domain must pass security assessment
  - Domain must have legitimate use case
  - Domain must be documented with purpose
```

### Rule 4: Path Validation
```
For file access permissions:
  - Path must exist or be valid glob pattern
  - No circular or symbolic link issues
  - Appropriate scope for use case
```

## Maintenance Procedures

### Regular Audits
- Review permissions quarterly
- Remove unused permissions
- Update patterns as project structure changes
- Validate security of approved domains

### Change Management
- Document reason when adding new permission
- Review before committing to version control
- Test that permission is necessary
- Remove when feature/need is removed

### Documentation Requirements
- Comment complex or non-obvious permissions
- Group related permissions with headers
- Document why broad patterns are necessary
- Link to security assessments for WebFetch domains
