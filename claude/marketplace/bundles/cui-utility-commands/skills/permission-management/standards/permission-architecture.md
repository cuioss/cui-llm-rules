# Permission Architecture

## Global vs Local Separation

**Global Permissions** (`~/.claude/settings.json`):
- Apply to ALL projects universally
- `Read(//~/git/**)` - Universal read access to all git repositories
- All CUI marketplace skills
- `WebFetch(domain:*)` - Universal web access
- All common Bash commands (git, mvn, grep, find, etc.)

**Local Permissions** (`.claude/settings.local.json`):
- Project-specific ONLY
- `Edit(//~/git/{current-project}/**)` - Project editing
- `Write(//~/git/{current-project}/**)` - Project file creation
- `Bash(~/git/{current-project}/scripts/**)` - Project scripts (if applicable)
- **Typically 2-3 permissions per project**

**Key Principle:** Local settings should ONLY contain project-specific Write/Edit permissions. All Read permissions for git repos are globally covered.

## Universal Access Pattern

As of 2025-10-27:
- `Read(//~/git/**)` provides universal git access (covers all repos)
- All CUI skills available globally (9 marketplace skills)
- `WebFetch(domain:*)` covers all domains globally
- No duplication needed in local settings

## Permission Categorization

**Should be Global:**
- Common developer tools (Bash commands)
- Universal read access patterns
- Shared skills and standards
- Common documentation domains

**Should be Local:**
- Project-specific Edit/Write permissions
- Project-specific script execution
- Project-specific tool configurations
