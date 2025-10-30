# Self-Containment Validation

Procedures for validating that skills are self-contained with no external dependencies.

## Validation Workflow

### Step 1: Scan for External References

```bash
# Check for escape sequences (../../../../)
grep -n "\.\..*\.\..*\.\." skill/SKILL.md

# Check for absolute paths
grep -n "~/\|^/" skill/SKILL.md | grep -v "https://"

# Check for .adoc references (likely external)
grep -n "\.adoc" skill/SKILL.md
```

**Expected Result**: No matches for compliant skill

### Step 2: Extract and Verify Internal References

```bash
# Extract all Read: statements
grep "Read: standards/" skill/SKILL.md | awk '{print $2}'

# For each file, verify exists
for file in $(extracted_files); do
  if [ ! -f "skill/$file" ]; then
    echo "MISSING: $file"
  fi
done
```

**Expected Result**: All files exist

### Step 3: Categorize References Section

```bash
# Extract References section
sed -n '/^## References/,/^##/p' skill/SKILL.md

# Categorize each reference:
# - https:// → External URL (allowed)
# - Skill: → Skill dependency (allowed)
# - standards/ → Internal file (allowed)
# - ../../../../ → External file (VIOLATION)
```

## Scoring

See **scoring-criteria.md** for the complete Skill Self-Containment Score formula, deductions, and thresholds.

## Score Interpretation

- **90-100**: ✅ Excellent - Fully self-contained, marketplace ready
- **75-89**: ⚠️ Good - Minor external refs, easy to fix
- **60-74**: ⚠️ Fair - Moderate issues, need internalization
- **< 60**: ❌ Poor - Major violations, significant work needed

## Common Violations and Fixes

### Violation 1: External File in Workflow

**Detection**:
```
Line 19: Read: ../../../../standards/java/java-core.adoc
```

**Severity**: CRITICAL (-20 points)

**Fix**:
```bash
1. Copy file to skill:
   cp ../../../../standards/java/java-core.adoc skill/standards/java-core.md

2. Update SKILL.md line 19:
   Read: standards/java-core.md

3. Verify:
   test -f skill/standards/java-core.md
```

### Violation 2: External File in References (Documentation)

**Detection**:
```
Line 272: * Requirements Doc: ../../../../standards/requirements/requirements-document.adoc
```

**Severity**: WARNING (-10 points)

**Fix Option A - Internalize**:
```bash
cp ../../../../standards/requirements/requirements-document.adoc skill/standards/requirements-document.md
# Update reference to: standards/requirements-document.md
```

**Fix Option B - Remove** (if not actually used):
```
Remove line 272 entirely
```

**Fix Option C - Convert to URL** (if publicly available):
```
* Requirements Doc: https://example.com/requirements-guide.html
```

### Violation 3: Absolute Path

**Detection**:
```
Line 45: Read: ~/git/cui-llm-rules/standards/logging.adoc
```

**Severity**: CRITICAL (-20 points)

**Fix**:
```bash
1. Copy to skill:
   cp ~/git/cui-llm-rules/standards/logging.adoc skill/standards/logging.md

2. Update SKILL.md line 45:
   Read: standards/logging.md
```

### Violation 4: Missing Internal File

**Detection**:
```
SKILL.md line 23: Read: standards/missing-file.md
File does not exist: skill/standards/missing-file.md
```

**Severity**: WARNING (-10 points)

**Fix**:
```bash
# Create placeholder
cat > skill/standards/missing-file.md << 'PLACEHOLDER'
# Missing Standard - TODO

**Status**: Placeholder - needs content

**Purpose**: [Describe purpose]

## TODO
- [ ] Add actual content
- [ ] Define standards
- [ ] Provide examples
PLACEHOLDER
```

## Automated Validation Script

```bash
#!/bin/bash
skill_path="$1"
score=100

echo "Validating: $skill_path"

# Check 1: External file references
ext_refs=$(grep -c "\.\..*\.\..*\.\." "$skill_path/SKILL.md" 2>/dev/null || echo 0)
score=$((score - ext_refs * 20))
echo "External file refs: $ext_refs (-$((ext_refs * 20)) points)"

# Check 2: Absolute paths
abs_paths=$(grep -c "~/\|^/" "$skill_path/SKILL.md" 2>/dev/null | grep -v "https://" || echo 0)
score=$((score - abs_paths * 20))
echo "Absolute paths: $abs_paths (-$((abs_paths * 20)) points)"

# Check 3: Missing internal files
while read -r file; do
  if [ ! -f "$skill_path/$file" ]; then
    score=$((score - 10))
    echo "Missing file: $file (-10 points)"
  fi
done < <(grep "Read: standards/" "$skill_path/SKILL.md" | awk '{print $2}')

# Final score
if [ $score -lt 0 ]; then score=0; fi
echo "FINAL SCORE: $score/100"
```

## Integration with Diagnostic Commands

This validation is integrated into:

- **/cui-create-skill**: Proactive - prevents violations at creation time
- **/cui-diagnose-skills**: Reactive - detects violations in existing skills
- **/cui-diagnose-bundle**: Aggregates skill scores for bundle health

All commands invoke `Skill: cui-marketplace-architecture` to load these validation procedures.
