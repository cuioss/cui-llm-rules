# Permission Anti-Patterns

## Suspicious Permission Patterns

### System Temp Directories
- `Read(//tmp/**)`, `Write(//tmp/**)`
- `Read(//private/tmp/**)`
- Any permission accessing `/tmp` or `/private/tmp`

### Critical System Directories
- `/dev/**` - Device files (disks, terminals, CPU)
- `/sys/**` - System information
- `/proc/**` - Process information
- `/etc/**` - System configuration
- `/boot/**` - Boot files
- `/root/**` - Root user home

### Overly Broad Wildcards
- `Read(//Users/**)` - All user files
- `Read(//\*\*)` - Entire filesystem
- `Bash(*)` - All commands

### Dangerous Commands
- `Bash(rm:*)` without specific path
- `Bash(sudo:*)`
- `Bash(chmod:*)`
- `Bash(dd:*)`

### Malformed Patterns
- Absolute paths without user-relative format (`/Users/oliver/` instead of `~/`)
- Missing wildcards where needed
- Empty patterns

### Redundant Patterns
- Specific pattern covered by broader pattern
- Example: `Read(//~/git/project/src/**)` when `Read(//~/git/project/**)` exists
- Local permissions duplicating global permissions

## Detection Strategies

Check each permission against:
1. System directory patterns
2. Dangerous command patterns
3. Overly broad wildcards
4. Path format issues
5. Redundancy with existing permissions

## Security Risk Assessment

**HIGH RISK:**
- System directory access
- Dangerous commands without restrictions
- Overly broad wildcards

**MEDIUM RISK:**
- Temp directory access
- Redundant permissions (maintenance risk)

**LOW RISK:**
- Path format issues (usability, not security)
