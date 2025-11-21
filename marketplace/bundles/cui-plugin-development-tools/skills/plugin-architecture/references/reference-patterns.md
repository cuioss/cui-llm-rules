# Reference Patterns

Classification of allowed vs prohibited reference types in marketplace components, emphasizing the `{baseDir}` pattern for portability.

## The {baseDir} Pattern

**Critical Principle**: All resource paths in skills must use `{baseDir}` for portability across installation contexts.

**Why {baseDir}**:
- Skills installed in different locations (global, project, bundle)
- `{baseDir}` resolves to skill's installation directory at runtime
- Makes skills portable and distributable

**Resolves To**:
- Global: `~/.claude/skills/my-skill/`
- Project: `.claude/skills/my-skill/`
- Bundle: `marketplace/bundles/{bundle}/skills/my-skill/`

## Pattern 1: Internal References ({baseDir}/references/)

**Purpose**: Documentation and knowledge loaded on-demand.

**Format**:
```markdown
Read {baseDir}/references/filename.md
Read {baseDir}/references/subdirectory/filename.md
```

**Rules**:
- Must use `{baseDir}` prefix
- Must be relative path within references/ directory
- File must exist in skill's references/ directory
- No `../` sequences allowed
- Path separator is forward slash `/`

**Examples**:
```markdown
✅ Read {baseDir}/references/quality-standards.md
✅ Read {baseDir}/references/testing/junit-patterns.md
✅ Read {baseDir}/references/cdi/cdi-aspects.md
✅ Read {baseDir}/references/examples/good-example.md
```

**Prohibited**:
```markdown
❌ Read: references/file.md                    # Missing {baseDir}
❌ Read: standards/file.md                     # Old pattern (use references/)
❌ Read: ../../../../other-skill/file.md       # Escape sequences
❌ Read: ~/git/cui-llm-rules/standards/file.md # Absolute path
```

**Validation**:
```bash
# Extract all Read: statements
grep "Read {baseDir}/references/" skill/SKILL.md

# Verify each file exists
for file in $(extracted_paths); do
  # Remove {baseDir}/ prefix and check existence
  test -f "skill/${file#\{baseDir\}/}" || echo "MISSING: $file"
done
```

## Pattern 2: Script Execution ({baseDir}/scripts/)

**Purpose**: Executable automation scripts (Python, Bash) for deterministic logic.

**Format**:
```markdown
bash {baseDir}/scripts/script-name.sh {args}
python {baseDir}/scripts/script-name.py {args}
python3 {baseDir}/scripts/script-name.py {args}
```

**Rules**:
- Must use `{baseDir}` prefix
- Scripts must exist in skill's scripts/ directory
- Use `bash`, `python`, or `python3` command
- Pass arguments as needed

**Examples**:
```markdown
✅ bash {baseDir}/scripts/analyzer.sh {input_file}
✅ python3 {baseDir}/scripts/validate.py {component_path}
✅ bash {baseDir}/scripts/generate-report.sh {findings_json}
```

**Prohibited**:
```markdown
❌ bash ./scripts/analyzer.sh                  # Missing {baseDir}
❌ bash scripts/analyzer.sh                    # Missing {baseDir}
❌ python ~/project/scripts/analyzer.py        # Absolute path
❌ ./scripts/analyzer.sh                       # Relative execution
```

**Script Output**:
- Scripts should output structured data (JSON) for Claude to interpret
- Scripts should return exit code 0 for success, non-zero for failure
- Output to stdout, errors to stderr

## Pattern 3: Asset Templates ({baseDir}/assets/)

**Purpose**: Templates and binary files used as input to scripts or for generation.

**Format**:
```markdown
Load template: {baseDir}/assets/template-name.ext
Read {baseDir}/assets/config-example.json
```

**Rules**:
- Must use `{baseDir}` prefix
- Assets must exist in skill's assets/ directory
- Typically used with "Load template:" or similar context
- Can be any file type (templates, configs, images)

**Examples**:
```markdown
✅ Load template: {baseDir}/assets/template.html
✅ Read {baseDir}/assets/config-example.json
✅ Use template: {baseDir}/assets/templates/basic.txt
✅ Load image: {baseDir}/assets/diagram.png
```

**Prohibited**:
```markdown
❌ Load template: ./assets/template.html      # Missing {baseDir}
❌ Use: ~/git/project/assets/template.html    # Absolute path
❌ Load: ../other-skill/assets/template.html  # Cross-skill access
```

## Pattern 4: External URLs

**Purpose**: Link to authoritative specifications and official documentation.

**Format**:
```markdown
* Description: https://external-site.com/path
* Description: http://external-site.com/path
```

**Rules**:
- Must start with `https://` or `http://`
- Must be publicly accessible
- Typically in ## References section
- Not loaded via `Read:` statement
- Used for supplemental documentation

**Examples**:
```markdown
✅ * Java Spec: https://docs.oracle.com/javase/specs/
✅ * Maven Guide: https://maven.apache.org/guides/
✅ * CDI Spec: https://jakarta.ee/specifications/cdi/
✅ * Quarkus Guide: https://quarkus.io/guides/cdi
✅ * Claude Skills Deep Dive: https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/
```

**Purpose**:
- Link to authoritative specifications
- Reference official documentation
- Point to framework guides
- Provide supplemental reading

## Pattern 5: Skill Dependencies

**Purpose**: Invoke other skills for their knowledge and capabilities.

**Format**:
```markdown
Skill: cui-skill-name
Skill: bundle-name:skill-name  # For bundled skills
```

**Rules**:
- Must use `Skill:` prefix
- Must reference valid skill name
- Skill must exist (marketplace, bundle, or global)
- Used in workflows to load standards

**Examples**:
```markdown
✅ Skill: cui-java-core
✅ Skill: cui-java-unit-testing
✅ Skill: cui-javadoc
✅ Skill: cui-utilities:cui-diagnostic-patterns
✅ Skill: cui-plugin-development-tools:plugin-architecture
```

**Usage Contexts**:

In skill workflows:
```markdown
## Step 1: Load Prerequisites

Skill: cui-java-core
Skill: cui-javadoc

## Step 2: Apply Standards

Apply standards loaded from skills in Step 1
```

In command workflows:
```markdown
## Step 1: Load Architecture Principles

Skill: cui-plugin-development-tools:plugin-architecture

## Step 2: Create Component

Follow architecture rules from loaded skill
```

**Prohibited**:
```markdown
❌ Read {baseDir}/../other-skill/SKILL.md     # Direct file access
❌ bash {baseDir}/../other-skill/scripts/*.sh # Cross-skill script
```

## Prohibited Patterns

### ❌ Escape Sequences
**Problem**: Breaks portability, assumes specific directory structure.

```markdown
❌ Read: ../../../../standards/java/java-core.adoc
❌ bash ../../scripts/analyzer.sh
❌ * Guide: ../../../standards/requirements/guide.adoc
```

**Why Wrong**:
- Assumes specific directory depth
- Breaks when skill installed elsewhere
- Fails in distribution

**Fix**: Use appropriate pattern (Skill: for other skills, {baseDir} for own resources).

### ❌ Absolute Paths
**Problem**: Machine-specific, user-specific, not portable.

```markdown
❌ Read: ~/git/cui-llm-rules/standards/java-core.adoc
❌ bash /Users/oliver/scripts/analyzer.sh
❌ Source: /opt/project/standards/logging.adoc
```

**Why Wrong**:
- User-specific home directory
- Machine-specific file system
- Not portable across installations

**Fix**: Use {baseDir} pattern or Skill: invocation.

### ❌ Missing {baseDir}
**Problem**: Relative paths work in development but break in distribution.

```markdown
❌ Read: references/file.md
❌ bash ./scripts/analyzer.sh
❌ bash scripts/analyzer.sh
❌ Load: assets/template.html
```

**Why Wrong**:
- Works in development (current directory)
- Breaks when skill installed elsewhere
- Not explicitly portable

**Fix**: Always use {baseDir} prefix.

### ❌ Cross-Skill File Access
**Problem**: Breaks skill encapsulation, couples skills together.

```markdown
❌ Read {baseDir}/../cui-other-skill/references/file.md
❌ bash {baseDir}/../other-skill/scripts/script.sh
```

**Why Wrong**:
- Bypasses skill interface
- Couples implementations
- Breaks when other skill reorganized
- Not validated by skill system

**Fix**: Use `Skill: other-skill` to invoke skill properly.

## Portability Testing

### Test in Different Contexts

**1. Global Installation**:
```bash
cp -r my-skill ~/.claude/skills/
# Test that {baseDir} resolves to ~/.claude/skills/my-skill/
```

**2. Project Installation**:
```bash
cp -r my-skill .claude/skills/
# Test that {baseDir} resolves to .claude/skills/my-skill/
```

**3. Bundle Installation**:
```bash
# Skill already in bundle
# Test that {baseDir} resolves to marketplace/bundles/{bundle}/skills/my-skill/
```

### Validation Checklist

- [ ] All `Read:` statements use {baseDir} pattern
- [ ] All script executions use {baseDir} pattern
- [ ] All asset references use {baseDir} pattern
- [ ] No `../` escape sequences found
- [ ] No absolute paths found
- [ ] No hardcoded paths found
- [ ] Skill works when installed globally
- [ ] Skill works when installed in project
- [ ] Skill works when bundled

### Automated Validation

```bash
# Check for prohibited patterns
grep -r "Read: \.\." skill/              # Escape sequences
grep -r "bash \.\." skill/               # Escape sequences
grep -r "Read: ~" skill/                 # Absolute paths
grep -r "Read: /" skill/ | grep -v http # Absolute paths (exclude URLs)

# Check for missing {baseDir}
grep -r "Read: references/" skill/       # Should use {baseDir}/references/
grep -r "bash ./scripts/" skill/         # Should use {baseDir}/scripts/
grep -r "bash scripts/" skill/           # Should use {baseDir}/scripts/
```

## Reference Summary

**Pattern 1**: `Read {baseDir}/references/file.md` - On-demand documentation
**Pattern 2**: `bash {baseDir}/scripts/script.sh` - Executable automation
**Pattern 3**: `Load {baseDir}/assets/template.html` - Templates and binaries
**Pattern 4**: `* URL: https://example.com` - External documentation
**Pattern 5**: `Skill: skill-name` - Other skill invocation

**Key Principle**: Always use `{baseDir}` for all internal resources to ensure portability.

## Examples

### Complete Skill with All Patterns

```markdown
---
name: example-skill
description: Example using all reference patterns
allowed-tools: [Read, Bash, Skill]
---

# Example Skill

## Step 1: Load Prerequisites

Skill: cui-utilities:cui-general-development-rules  # Pattern 5

## Step 2: Load Reference Documentation

Read {baseDir}/references/core-principles.md        # Pattern 1
Read {baseDir}/references/examples/example-1.md     # Pattern 1

## Step 3: Execute Analysis Script

bash {baseDir}/scripts/analyzer.sh {input_file}     # Pattern 2

## Step 4: Generate Output

Load template: {baseDir}/assets/report-template.md  # Pattern 3
Fill template with analysis results
Write output to {output_file}

## References

* Official Spec: https://example.com/spec           # Pattern 4
* Framework Guide: https://example.com/guide         # Pattern 4
```

## Related References

- Core Principles: {baseDir}/references/core-principles.md
- Architecture Rules: {baseDir}/references/architecture-rules.md
- Skill Design: {baseDir}/references/skill-design.md
