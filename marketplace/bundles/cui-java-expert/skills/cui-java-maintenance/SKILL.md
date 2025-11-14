---
name: cui-java-maintenance
description: Standards for identifying, prioritizing, and verifying Java code maintenance and refactoring work
allowed-tools: [Read, Grep, Glob]
---

# CUI Java Maintenance Skill

Standards for systematic Java code maintenance including violation detection, prioritization frameworks, and compliance verification.

## Purpose

This skill provides comprehensive standards for:
- **Detecting** when code needs refactoring (trigger criteria)
- **Prioritizing** maintenance work (impact-based framework)
- **Verifying** standards compliance (comprehensive checklist)

## When to Use This Skill

Activate this skill when:

**Planning Maintenance Work:**
- Conducting code quality audits
- Planning refactoring sprints
- Identifying technical debt
- Analyzing codebases for violations

**During Refactoring:**
- Need trigger criteria for when to refactor
- Need prioritization guidance
- Verifying standards compliance after changes

**Code Reviews:**
- Assessing code quality systematically
- Identifying improvement opportunities
- Validating maintenance work completeness

## Workflow

### Step 1: Load Core Maintenance Standards

**Load all three standards files** (always loaded together):

```
Read: standards/refactoring-triggers.md
Read: standards/maintenance-prioritization.md
Read: standards/compliance-checklist.md
```

These standards work together as a complete maintenance framework:
1. **Triggers** - Identify WHAT needs fixing (detection criteria)
2. **Prioritization** - Decide WHEN to fix it (impact framework)
3. **Checklist** - Verify fixes are COMPLETE (compliance verification)

### Step 2: Apply Standards Based on Task

**For Code Analysis Tasks:**

1. Use refactoring-triggers.md to scan for violations:
   - Code organization issues
   - Method design problems
   - Null safety violations
   - Exception handling issues
   - Naming convention problems
   - Legacy code patterns
   - Unused code detection
   - Lombok integration opportunities
   - Documentation gaps

2. Document all findings with locations and descriptions

**For Prioritization Tasks:**

1. Use maintenance-prioritization.md to categorize findings:
   - HIGH: Critical violations (API contracts, security, fundamental design)
   - MEDIUM: Maintainability issues (method design, code cleanup, modernization)
   - LOW: Style and speculative optimizations

2. Consider contextual factors:
   - Impact scope
   - Technical debt interest
   - Team context
   - Risk assessment

3. Create prioritized work list

**For Verification Tasks:**

1. Use compliance-checklist.md to verify fixes:
   - Work through each checklist section
   - Mark compliant/non-compliant items
   - Address all non-compliant findings
   - Re-verify after fixes
   - Document intentional deviations

2. Execute build verification:
   - Quality build: `./mvnw -Ppre-commit clean verify -DskipTests`
   - Test suite: `./mvnw clean test`
   - Coverage: `./mvnw clean verify -Pcoverage`

### Step 3: Load Implementation Standards (Optional)

When implementing fixes, load relevant implementation skills:

**For code implementation:**
```
Skill: cui-java-core
```
Provides actual implementation patterns for:
- Core patterns and null safety
- Lombok usage
- Modern Java features
- Logging implementation

**For documentation work:**
```
Skill: cui-javadoc
```
Provides Javadoc standards and patterns.

**For testing work:**
```
Skill: cui-java-unit-testing
```
Provides testing standards and patterns.

**For CDI work:**
```
Skill: cui-java-cdi
```
Provides CDI aspects and container standards.

### Step 4: Report Findings

Provide structured output:

**For Analysis:**
```
Violations Found:
- HIGH Priority: [count] issues
  - [Category]: [specific violations]
- MEDIUM Priority: [count] issues
  - [Category]: [specific violations]
- LOW Priority: [count] issues
  - [Category]: [specific violations]

Recommended Actions:
1. Address HIGH priority items first
2. [Specific recommendations]
```

**For Verification:**
```
Compliance Verification Results:
✅ Package Organization: Compliant
✅ Class Design: Compliant
⚠️ Method Design: 3 issues found
⚠️ Null Safety: @NullMarked missing
✅ Exception Handling: Compliant
...

Next Steps:
- Fix identified non-compliant items
- Re-run verification
```

## Common Patterns and Examples

### Pattern 1: Code Quality Audit

```markdown
## Step 1: Load Maintenance Standards
Skill: cui-java-maintenance

## Step 2: Analyze Codebase
Use Grep/Glob to scan for violations based on trigger criteria:
- Search for catch(Exception e)
- Search for System.out.println
- Check for missing package-info.java
- Identify classes > 500 lines

## Step 3: Categorize and Prioritize
Apply prioritization framework:
- Security issues → HIGH
- API contract issues → HIGH
- Method design issues → MEDIUM
- Style issues → LOW

## Step 4: Create Action Plan
Generate prioritized list of fixes needed.
```

### Pattern 2: Refactoring Verification

```markdown
## Step 1: Load Maintenance Standards
Skill: cui-java-maintenance

## Step 2: Apply Compliance Checklist
Work through checklist for modified classes:
- Package organization ✅
- Class design ✅
- Method design ⚠️ (2 methods > 50 lines)
- Null safety ✅
- Logging ✅

## Step 3: Fix Non-Compliant Items
Extract long methods to comply with standards.

## Step 4: Re-Verify
Run through checklist again and verify build passes.
```

### Pattern 3: Module-by-Module Maintenance

```markdown
## Step 1: Load Maintenance Standards
Skill: cui-java-maintenance

## Step 2: For Each Module
1. Apply trigger criteria to identify violations
2. Prioritize using framework
3. Implement fixes using cui-java-core
4. Verify using compliance checklist
5. Commit module changes

## Step 3: Final Verification
Verify all modules pass build and tests.
```

## Integration with Commands

This skill is designed to be used by:

**`/cui-java-refactor-code` command:**
- Loads this skill for detection, prioritization, and verification
- Orchestrates systematic refactoring workflow
- Uses trigger criteria to identify issues
- Uses prioritization to order work
- Uses checklist to verify completeness

**Other maintenance commands:**
- Any command performing code quality work
- Automated refactoring commands
- Code review automation

## Relationship with Other Skills

### Complementary Skills

**cui-java-core** - Implementation standards:
- This skill identifies WHAT needs fixing
- cui-java-core provides HOW to implement fixes

**cui-javadoc** - Documentation standards:
- This skill detects documentation gaps
- cui-javadoc provides documentation patterns

**cui-java-unit-testing** - Testing standards:
- This skill identifies testing needs
- cui-java-unit-testing provides testing patterns

**cui-java-cdi** - CDI standards:
- This skill detects CDI violations
- cui-java-cdi provides CDI patterns

### Clear Separation of Concerns

**This skill (cui-java-maintenance):**
- ✅ Detection criteria (WHEN to refactor)
- ✅ Prioritization framework (WHAT order)
- ✅ Verification checklist (HOW to verify)
- ❌ Implementation patterns (see cui-java-core)
- ❌ Workflow orchestration (see /cui-java-refactor-code command)

**Implementation skills (cui-java-core, etc.):**
- ✅ Implementation patterns (HOW to implement)
- ✅ Code examples and templates
- ✅ Best practices for writing code
- ❌ Detection criteria
- ❌ Prioritization decisions

## Standards Organization

```
standards/
├── refactoring-triggers.md          # Detection criteria
├── maintenance-prioritization.md    # Priority framework
└── compliance-checklist.md          # Verification checklist
```

**Design principles:**
- Self-contained standards (no external references except URLs)
- Markdown format for compatibility
- Practical examples included
- Clear decision guidance
- Agent-friendly structure

## Quality Verification

Before completing maintenance work:

1. [ ] All trigger criteria have been checked
2. [ ] Violations prioritized using framework
3. [ ] High priority items addressed
4. [ ] Compliance checklist completed
5. [ ] Build verification passed
6. [ ] Tests passing with adequate coverage
7. [ ] Static analysis (SonarQube) passing
8. [ ] Deviations documented with rationale

## Example Usage

### In a Command

```markdown
---
name: my-maintenance-command
---

## Step 1: Load Maintenance Standards

```
Skill: cui-java-maintenance
```

This loads refactoring triggers, prioritization framework, and compliance checklist.

## Step 2: Analyze Code

Apply trigger criteria from refactoring-triggers.md to identify violations.

## Step 3: Prioritize Work

Use maintenance-prioritization.md to order fixes by impact.

## Step 4: Implement Fixes

For implementation patterns, load cui-java-core or other implementation skills.

## Step 5: Verify Compliance

Use compliance-checklist.md to verify all standards met.
```

### In an Agent

```markdown
## Maintenance Analysis Agent

### Step 1: Load Standards
```
Read: standards/refactoring-triggers.md
```

### Step 2: Scan Codebase
Apply trigger criteria to identify all violations.

### Step 3: Apply Prioritization
Use prioritization framework to categorize findings.

### Step 4: Report Results
Return structured analysis with prioritized action items.
```

## Error Handling

If issues arise during maintenance:

1. **Build failures**: Use maven-builder agent to diagnose and fix
2. **Test failures**: Review test output and fix broken tests
3. **Coverage regressions**: Add tests for uncovered code paths
4. **Static analysis issues**: Address SonarQube findings systematically
5. **Ambiguous violations**: Ask user for guidance on priority

## References

**Internal Standards:**
- standards/refactoring-triggers.md - Detection criteria
- standards/maintenance-prioritization.md - Priority framework
- standards/compliance-checklist.md - Verification checklist

**Related Skills:**
- cui-java-core - Core implementation patterns
- cui-javadoc - Documentation standards
- cui-java-unit-testing - Testing standards
- cui-java-cdi - CDI standards

**Related Commands:**
- /cui-java-refactor-code - Systematic refactoring workflow
- /cui-maven-build-and-fix - Build verification and fixes
