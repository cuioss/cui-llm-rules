# Quality Standards and Testing Framework

## Purpose
Defines comprehensive quality standards, testing framework guidelines, and quality verification processes for CUI OSS projects.

## Related Commands
- `cp: verify sonar`: Quality analysis
- `cp: maintenance java perform`: Core maintenance
- `cp: maintenance java finalize`: Completion tasks

## Related Documentation
- core/standards/project-standards.md: Project standards and technology stack
- core/standards/documentation-standards.md: Documentation standards
- maintenance/java.md: Java maintenance process

## Core Testing Standards

### 1. Test Structure and Organization
- Follow AAA pattern (Arrange-Act-Assert)
- One logical assertion per test
- Clear test naming convention
- Descriptive test documentation
- Independent test execution
- Clean test environment
- Predictable test data

### 2. Coverage Requirements
- Minimum 80% line coverage
- Critical paths must have 100% coverage
- All public APIs must be tested
- Edge cases must be covered
- No coverage regressions allowed
- Regular coverage review

### 3. Testing Tools and Frameworks

#### Required Frameworks
1. JUnit 5
   - Use `@DisplayName` for readable test names
   - Leverage parameterized tests
   - Apply proper test lifecycle annotations

#### CUI Testing Utilities
1. cui-test-generator
   - Use for generating test data
   - Follow builder patterns
   - Document generator configurations

2. cui-test-value-objects
   - Leverage for value object testing
   - Follow equality testing guidelines
   - Include serialization tests

3. cui-jsf-test-basic
   - Use for JSF component testing
   - Follow component test patterns
   - Include lifecycle tests

### 4. Test Categories

#### Unit Tests
- Test single units in isolation
- Mock all dependencies
- Fast execution
- High maintainability

#### Integration Tests
- Test component interactions
- Minimal mocking
- Cover critical paths
- Include error scenarios
- Regular maintenance required

#### System Tests
- End-to-end scenarios
- Real dependencies where possible
- Cover main user flows
- Include performance criteria

## Quality Verification

### 1. SonarCloud Integration

#### Access Configuration
1. Dashboard Access:
   ```
   https://sonarcloud.io/dashboard?id=cuioss_<project-name>&branch=<branch-name>
   ```
2. Issues API:
   ```
   https://sonarcloud.io/api/issues/search?componentKeys=cuioss_<project-name>&branch=<branch-name>&resolved=false&sinceLeakPeriod=true
   ```

#### Quality Gate Review
- Check overall status
- Review failing conditions
- Note quality metric thresholds
- Document gate configuration

### 2. Issue Management

#### Issue Analysis
Review issues by:
- Severity (MAJOR, MINOR, etc.)
- Type (CODE_SMELL, BUG, VULNERABILITY)
- Impact on quality metrics
- Associated code locations
- Rule references

#### Issue Documentation
- File and line references must be precise
- Include issue descriptions from SonarCloud
- Note severity and impact levels
- Document remediation steps
- Reference specific SonarCloud rules

### 3. Security Standards

#### Security Assessment
- Check for vulnerabilities
- Review security hotspots
- Assess security-related code smells
- Verify dependency security
- No critical vulnerabilities allowed
- Security best practices followed

#### Security Documentation
- Document security findings
- Track vulnerability remediation
- Record security decisions
- Update security metrics

## Best Practices

### 1. Test Quality
- Regular test review
- Mutation testing
- Test failure analysis
- DRY in test utilities
- Clear test documentation
- Consistent patterns

### 2. Performance
- Fast test execution
- Efficient resource usage
- Parallel test execution where possible
- Regular performance monitoring

### 3. Review Process
Regular Review Points:
- After major feature completion
- Before creating pull requests
- During code review process
- Post-merge verification

### 4. Documentation
- Record quality findings
- Document remediation steps
- Note technical debt decisions
- Update quality metrics
- Track coverage changes

## Success Criteria

### 1. Test Coverage
- All coverage requirements met
- Critical paths fully covered
- Test quality sufficient
- No coverage regressions

### 2. Quality Analysis
- All quality gates passed
- New issues addressed
- Impact assessed
- Clear remediation paths
- Documentation complete

### 3. Security
- No critical vulnerabilities
- Security hotspots reviewed
- Dependencies verified
- Security standards met

## See Also
- core/standards/project-standards.md: Project standards and technology stack
- core/standards/documentation-standards.md: Documentation standards
- maintenance/java.md: Java maintenance process
