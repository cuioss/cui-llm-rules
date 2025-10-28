# CUI Skills Quick Reference

Fast lookup guide for choosing the right skill for your task.

## Quick Skill Selector

### "I'm writing Java code..."

| Task | Skill | Quality |
|------|-------|---------|
| Core Java classes, patterns, logging | [cui-java-core](cui-java-core/) | 99/100 ⭐⭐ |
| Unit tests, generators, mocking | [cui-java-unit-testing](cui-java-unit-testing/) | 98/100 ⭐ |
| JavaDoc documentation | [cui-javadoc](cui-javadoc/) | 98/100 ⭐ |
| CDI/Quarkus, dependency injection | [cui-java-cdi](cui-java-cdi/) | 97/100 ⭐ |

### "I'm writing frontend code..."

| Task | Skill | Quality |
|------|-------|---------|
| JavaScript, CSS, web components, Cypress | [cui-frontend-development](cui-frontend-development/) | 97/100 ⭐ |

### "I'm writing documentation..."

| Task | Skill | Quality |
|------|-------|---------|
| README, AsciiDoc, technical docs | [cui-documentation](cui-documentation/) | 98/100 ⭐ |
| Java API documentation | [cui-javadoc](cui-javadoc/) | 98/100 ⭐ |

### "I'm starting a new project..."

| Task | Skill | Quality |
|------|-------|---------|
| Maven setup, project structure | [cui-project-setup](cui-project-setup/) | 98/100 ⭐ |
| Requirements, specifications | [cui-requirements](cui-requirements/) | 97/100 ⭐ |

---

## Skill Cheat Sheet

### cui-java-core (99/100)

**Use for**: All Java development

**Key Rules**:
- Constructor injection ONLY (no field injection)
- @NullMarked in package-info.java
- Never @Nullable for returns (use Optional)
- CuiLogger (not SLF4J)
- Records for simple data carriers
- @Builder for 3+ parameters
- DSL-style nested constants
- Methods < 50 lines (100 max)

**Typical workflow**:
1. Add @NullMarked to package
2. Use CuiLogger
3. Apply Lombok patterns
4. Use modern Java features
5. Run: `./mvnw clean verify`

---

### cui-java-unit-testing (98/100)

**Use for**: Writing Java tests

**Key Rules**:
- @EnableGeneratorController (mandatory)
- Generators.* for ALL test data
- AAA pattern (Arrange-Act-Assert)
- Meaningful assertion messages (20-60 chars)
- NO Mockito/Hamcrest/PowerMock
- 80% coverage minimum
- NEVER commit @GeneratorSeed

**Typical workflow**:
1. Add @EnableGeneratorController
2. Use Generators.* for data
3. Follow AAA pattern
4. Run: `./mvnw clean verify -Pcoverage`

---

### cui-javadoc (98/100)

**Use for**: Java documentation

**Key Rules**:
- Document all public/protected APIs
- Start with clear purpose (what and why)
- Avoid stating the obvious
- Standard tag order: @param, @return, @throws, @see, @since
- Use {@code} for inline code
- Include working examples
- Close all HTML tags

**Typical workflow**:
1. Document class purpose
2. Document all public methods
3. Add code examples
4. Run: `mvn javadoc:javadoc`

---

### cui-java-cdi (97/100)

**Use for**: CDI/Quarkus development

**Key Rules**:
- Constructor injection ONLY
- Injected fields must be final
- @ApplicationScoped for stateless
- @Dependent for producers that may return null
- @RegisterForReflection for native
- Non-root container users
- Health checks in Dockerfile

**Typical workflow**:
1. Use constructor injection
2. Select proper scope
3. Write @QuarkusTest
4. Run: `./mvnw clean verify`

---

### cui-frontend-development (97/100)

**Use for**: JavaScript/CSS development

**Key Rules**:
- ES2022+ syntax only
- const/let (never var)
- Vanilla JavaScript (no jQuery)
- Lit for web components
- data-testid for Cypress selectors
- CSS custom properties
- Max 15 cyclomatic complexity
- Node 20.12.2 LTS

**Typical workflow**:
1. Write ES2022+ JavaScript
2. Use Lit for components
3. Style with modern CSS
4. Test with Cypress
5. Run: `npm test && npm run lint`

---

### cui-documentation (98/100)

**Use for**: README, AsciiDoc, docs

**Key Rules**:
- Professional, neutral tone
- NO marketing language
- Blank lines before ALL lists (AsciiDoc)
- Code examples from unit tests
- Document only existing features
- Use linking (not duplication)
- Technical precision

**Typical workflow**:
1. Write clear overview
2. Add working examples
3. Document configuration
4. Add best practices
5. Verify rendering

---

### cui-project-setup (98/100)

**Use for**: New project initialization

**Key Rules**:
- Java 17+ required
- Maven standard layout
- cui-parent or cui-bom
- Semantic versioning
- 80% coverage threshold
- Pre-commit profile
- Security-hardened containers

**Typical workflow**:
1. Create Maven structure
2. Add package-info.java
3. Configure plugins
4. Add quality tools
5. Run: `mvn clean install`

---

### cui-requirements (97/100)

**Use for**: Requirements, specifications

**Key Rules**:
- SMART criteria (Specific, Measurable, Achievable, Relevant, Time-bound)
- MUST/SHOULD/MAY categories
- Given/When/Then acceptance criteria
- Non-functional requirements
- Testable requirements

**Typical workflow**:
1. Write MUST/SHOULD/MAY requirements
2. Add non-functional requirements
3. Define acceptance criteria
4. Review with stakeholders

---

## Common Skill Combinations

### New Java Library
```yaml
skills:
  - cui-project-setup       # Initialize
  - cui-java-core           # Develop
  - cui-java-unit-testing   # Test
  - cui-javadoc             # Document
  - cui-documentation       # README
```

### Quarkus Application
```yaml
skills:
  - cui-project-setup
  - cui-java-core
  - cui-java-cdi            # CDI/Quarkus
  - cui-java-unit-testing
```

### Full-Stack Web App
```yaml
skills:
  - cui-java-core           # Backend
  - cui-java-cdi
  - cui-frontend-development # Frontend
  - cui-java-unit-testing
  - cui-documentation
```

### Documentation Project
```yaml
skills:
  - cui-documentation       # General docs
  - cui-javadoc             # Java docs
  - cui-requirements        # Requirements
```

---

## Quick Troubleshooting

### Build Fails
1. Check Java version: `java -version` (17+ required)
2. Verify Maven: `mvn -version`
3. Clean build: `./mvnw clean install`
4. Check logs for specific errors

### Tests Fail
1. Verify @EnableGeneratorController present
2. Check all test data uses Generators.*
3. No @GeneratorSeed committed
4. Run: `./mvnw clean test`

### Coverage Too Low
1. Target: 80% line and branch
2. Run: `./mvnw clean verify -Pcoverage`
3. Check uncovered paths
4. Add missing tests

### JavaDoc Errors
1. Check all public APIs documented
2. Verify HTML tags closed
3. Fix broken {@link} references
4. Run: `mvn javadoc:javadoc`

### CDI Issues
1. Use constructor injection (not field)
2. Make injected fields final
3. Check scope annotations
4. Verify @QuarkusTest setup

### Frontend Issues
1. Check Node version: `node -v` (20.12.2 LTS)
2. Use const/let (never var)
3. Run linters: `npm run lint`
4. Check Cypress selectors (use data-testid)

---

## Quality Verification

### Run Quality Checks

```bash
# Verify single skill
/diagnose-skills cui-java-core

# Verify all skills
/diagnose-skills global

# Pre-commit checks
./mvnw clean verify -Ppre-commit,coverage
```

### Quality Thresholds

| Score | Quality | Action |
|-------|---------|--------|
| 90-100 | Excellent ⭐ | Production ready |
| 75-89 | Good | Minor improvements |
| 60-74 | Fair | Moderate work needed |
| < 60 | Poor | Major rework required |

**Current Average**: 97.75/100 ⭐

---

## Getting Help

1. **Skill README** - Detailed documentation
2. **SKILL.md** - AI workflow instructions
3. **Standards files** - Detailed requirements
4. **Quality checker** - `/diagnose-skills`
5. **Repository issues** - Report problems

---

**Quick Tip**: Most Java development needs `cui-java-core` + `cui-java-unit-testing` + `cui-javadoc`

**Last Updated**: 2025-10-24
