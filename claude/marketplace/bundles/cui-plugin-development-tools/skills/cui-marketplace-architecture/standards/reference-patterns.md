# Reference Patterns

Classification of allowed vs prohibited reference types in marketplace components.

## Allowed Patterns

### Pattern 1: Internal Standards (Skills Only)

**Format**:
```
Read: standards/filename.md
Read: standards/subdirectory/filename.md
```

**Rules**:
- Must start with `standards/`
- Must be relative path within skill directory
- File must exist in skill's standards/ directory
- No `../` sequences allowed
- Path separator is forward slash `/`

**Examples**:
```
✅ Read: standards/java-core-patterns.md
✅ Read: standards/testing/junit-patterns.md
✅ Read: standards/cdi/cdi-aspects.md
```

**Validation**:
```bash
# Extract all Read: statements
grep "Read: standards/" skill/SKILL.md

# Verify each file exists
for file in $(extracted_paths); do
  test -f "skill/$file" || echo "MISSING: $file"
done
```

### Pattern 2: External URLs

**Format**:
```
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
```
✅ * Java Spec: https://docs.oracle.com/javase/specs/
✅ * Maven Guide: https://maven.apache.org/guides/
✅ * CDI Spec: https://jakarta.ee/specifications/cdi/
✅ * Quarkus Guide: https://quarkus.io/guides/cdi
```

**Purpose**:
- Link to authoritative specifications
- Reference official documentation
- Point to framework guides
- Provide supplemental reading

### Pattern 3: Skill Dependencies

**Format**:
```
Skill: cui-skill-name
```

**Rules**:
- Must use `Skill:` prefix
- Must reference valid skill name
- Skill must exist (marketplace, bundle, or global)
- Used in agent/command workflows
- Used in skill dependencies

**Examples**:
```
✅ Skill: cui-java-core
✅ Skill: cui-java-unit-testing
✅ Skill: cui-javadoc
✅ Skill: cui-documentation
```

**Usage Contexts**:

In agents:
```yaml
---
tools: Read, Edit, Write, Skill
---

Step 1: Activate Standards
Skill: cui-java-core
```

In skills (conditional):
```
If project uses logging:
  Skill: cui-logging
```

## Prohibited Patterns

### Pattern 1: Escape Sequences

**Format**:
```
❌ Read: ../../../../standards/java/java-core.adoc
❌ * Guide: ../../../standards/requirements/guide.adoc
❌ Read: ../../doc/architecture.adoc
```

**Why Prohibited**:
- Breaks portability (assumes specific directory structure)
- Fails when skill distributed independently
- Fails in global skill installation (~/.claude/skills/)
- Breaks marketplace distribution
- Couples component to repository layout

**Impact**:
```
When skill installed globally:
~/.claude/skills/cui-java-core/
  SKILL.md contains: Read: ../../../../standards/java-core.adoc
  Resolves to: ~/.claude/standards/java-core.adoc (DOESN'T EXIST)
  Result: SKILL FAILS TO LOAD
```

**Fix**:
- Copy file to skill/standards/
- Convert reference to: `Read: standards/java-core.md`
- Or convert to `Skill:` dependency if content in another skill

### Pattern 2: Absolute Paths

**Format**:
```
❌ Read: ~/git/cui-llm-rules/standards/java-core.adoc
❌ Source: /Users/oliver/git/cui-llm-rules/standards/logging.adoc
❌ Read: /home/user/project/standards/file.adoc
```

**Why Prohibited**:
- User-specific paths
- Machine-specific paths
- Not portable across environments
- Fails for other users/machines
- Breaks CI/CD environments

**Impact**:
```
Different users have different paths:
User A: ~/git/cui-llm-rules/
User B: ~/projects/cui-llm-rules/
User C: /opt/cui-llm-rules/

Hardcoded path only works for one user.
```

**Fix**:
- Internalize content to skill/standards/
- Use relative paths within skill
- Or use Skill: dependency

### Pattern 3: Cross-Skill File Access

**Format**:
```
❌ Read: ../cui-other-skill/standards/file.md
❌ Read: ../../bundles/other-bundle/skills/cui-skill/standards/file.md
```

**Why Prohibited**:
- Breaks skill encapsulation
- Creates hidden dependencies
- Skills may be distributed separately
- Bypasses skill workflow logic
- Couples skills together tightly

**Correct Pattern**:
```
✅ Skill: cui-other-skill
```

**Rationale**:
- Skill invocation is explicit dependency
- Skill handles its own internal loading
- Skills can version independently
- Dependency is documented and visible

### Pattern 4: Direct Repository References in Agents

**Format**:
```
❌ Read: ~/git/cui-llm-rules/standards/java-core.adoc
❌ Read: ../../../../standards/java/patterns.adoc
```

**Why Prohibited**:
- Bypasses skill abstraction
- Hard-codes file structure in agent
- Breaks when standards reorganized
- Loses skill versioning benefits
- Couples agent to repository layout

**Correct Pattern**:
```
✅ Skill: cui-java-core
```

**Benefits**:
- Skill manages file structure internally
- Skill handles conditional loading
- Standards can reorganize without breaking agent
- Agent depends on skill interface, not implementation

### Pattern 5: .adoc References in Marketplace

**Format**:
```
❌ Read: ../../../../standards/requirements/requirements-document.adoc
❌ * Guide: ../../doc/plugin-architecture.adoc
```

**Why Prohibited in Marketplace**:
- .adoc files typically in main repository
- Not distributed with marketplace bundles
- Marketplace uses .md for consistency
- .adoc → .md conversion needed for distribution

**Fix Strategy**:
1. Copy .adoc file to skill/standards/
2. Convert to .md format (or keep .adoc if needed)
3. Update reference to internal path
4. Or replace with external URL if publicly available

## Detection Patterns

### Scan for Violations

**Check 1: Escape Sequences**
```bash
grep -n "\.\..*\.\..*\.\." skill/SKILL.md
# Any match is violation
```

**Check 2: Absolute Paths**
```bash
grep -n "~/\|^/" skill/SKILL.md
# Filter out URLs starting with https://
grep -n "~/\|^/" skill/SKILL.md | grep -v "https://"
```

**Check 3: External .adoc**
```bash
grep -n "\.adoc" skill/SKILL.md
# Verify these are NOT external file references
# URLs ending in .adoc are OK
```

**Check 4: Cross-Skill Access**
```bash
grep -n "\.\./cui-" skill/SKILL.md
# Any match is likely cross-skill file access
```

## Fix Strategies

### Fix 1: Internalize Content

**Before**:
```
Read: ../../../../standards/java/java-core.adoc
```

**After**:
```
1. Copy file: cp ../../../../standards/java/java-core.adoc skill/standards/java-core.md
2. Update reference: Read: standards/java-core.md
3. Verify: test -f skill/standards/java-core.md
```

### Fix 2: Convert to Skill Dependency

**Before**:
```
Read: ../../../../standards/logging/logging-core.adoc
```

**After (if content in another skill)**:
```
Skill: cui-logging
```

**Verification**:
```
1. Verify cui-logging skill exists
2. Verify skill contains logging-core standards
3. Add Skill to allowed-tools if needed
```

### Fix 3: Convert to External URL

**Before**:
```
* Java Spec: ../../../../standards/java/spec.adoc
```

**After (if available online)**:
```
* Java Spec: https://docs.oracle.com/javase/specs/
```

**When to Use**:
- Reference is documentation-only (not loaded)
- Content available at authoritative URL
- No need to load into skill context

### Fix 4: Remove Reference

**Before**:
```
* Old Doc: ../../../../standards/deprecated/old-doc.adoc
```

**After**:
```
(remove line entirely)
```

**When to Use**:
- Reference is dead/deprecated
- Not used in workflow
- Documentation-only reference
- Content no longer relevant

## Validation Checklist

For each skill:
- [ ] All `Read: standards/` references have matching files
- [ ] No `../../../../` escape sequences
- [ ] No absolute paths (`~/`, `/`)
- [ ] No cross-skill file access (`../cui-other-skill/`)
- [ ] External URLs use `https://` format
- [ ] Skill dependencies use `Skill:` format
- [ ] All references categorized correctly

For each agent:
- [ ] No direct standards file references
- [ ] Uses `Skill:` invocations if needs standards
- [ ] Has `Skill` in tools list if invoking skills
- [ ] No repository file paths

Self-containment verified when:
- ✅ All checks pass
- ✅ Score: 100/100
- ✅ Ready for marketplace distribution
