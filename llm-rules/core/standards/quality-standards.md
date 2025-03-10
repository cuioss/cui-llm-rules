# Quality Standards and Testing Framework

## Purpose
Defines comprehensive quality standards, testing framework guidelines, and quality verification processes for CUI OSS projects.

## Related Commands
- `cp: verify sonar`: Quality analysis
- `cp: maintenance java perform`: Core maintenance
- `cp: maintenance java finalize`: Completion tasks

## Related Documentation
- [Project Standards](project-standards.md): Project standards and technology stack
- [Documentation Standards](documentation-standards.md): Documentation standards
- [Java Maintenance](../../maintenance/java.md): Java maintenance process

## Core Testing Standards

### 1. Test Structure and Organization
- Follow AAA pattern (Arrange-Act-Assert)
- One logical assertion per test
- Clear test naming convention
- Descriptive test documentation
- Independent test execution
- Clean test environment
- Predictable test data
- Use documentation tags for code examples (see [Documentation Tags](#documentation-tags))

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
   - Leverage parameterized tests (see [Parameterized Tests Best Practices](#parameterized-tests-best-practices))
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

### 1. Quality Analysis Tools
- SonarCloud for static code analysis (see [SonarCloud Integration](../../maintenance/sonar.md))
- JUnit for unit testing
- Mutation testing for test quality
- Regular code reviews
- Continuous integration checks

### 2. Quality Metrics
- Code coverage
- Code duplication
- Complexity metrics
- Issue density
- Technical debt ratio

### 3. Best Practices

#### Test Quality
- Regular test review
- Mutation testing
- Test failure analysis
- DRY in test utilities
- Clear test documentation
- Consistent patterns

### 4. Parameterized Tests Best Practices

- **Minimum Test Cases**: Parameterized tests should have at least 3 test cases to justify the overhead
  - For fewer than 3 test cases, use direct test methods instead
  - Convert existing parameterized tests with fewer than 3 cases to direct methods

- **Method Source Organization**:
  - Use descriptive method names for test case providers
  - Group related test cases together
  - Document each test case's purpose in the provider method
  - Return `Stream<Arguments>` with clear parameter descriptions

- **Test Case Naming**:
  - Use the `name` parameter in `@ParameterizedTest` for descriptive test names
  - Include parameter values in the name template where appropriate
  - Example: `@ParameterizedTest(name = "{0}: {1} should result in {2}")`

- **Test Case Documentation**:
  - Document the purpose of each test case in the provider method
  - Include edge cases and boundary conditions
  - Explain the relationship between inputs and expected outputs

- **Maintenance Considerations**:
  - Regularly review parameterized tests for relevance
  - Avoid excessive parameterization that obscures test intent
  - Balance between coverage and maintainability

### 5. Documentation Tags

- **Code Example Tags**:
  - Use asciidoc tag comments to mark code examples in source files
  - Format: `// tag::example-name[]` and `// end::example-name[]`
  - Choose descriptive tag names that indicate the example's purpose

- **Documentation Integration**:
  - Include tagged code in documentation using asciidoc includes
  - Format: `include::path/to/file.java[tags=example-name]`
  - Place includes within appropriate code blocks: `[source,java]`

- **Benefits**:
  - Examples stay synchronized with actual code
  - Documentation automatically updates when code changes
  - Reduces duplication and maintenance burden
  - Makes documentation more robust and reliable

- **Best Practices**:
  - Keep tagged sections focused and concise
  - Use meaningful tag names that describe the example's purpose
  - Document the existence of tags in class/method Javadoc
  - Review tags during code reviews to ensure documentation relevance

#### Performance
- Fast test execution
- Efficient resource usage
- Parallel test execution where possible
- Regular performance monitoring

#### Review Process
Regular Review Points:
- After major feature completion
- Before creating pull requests
- During code review process
- Post-merge verification

#### Documentation
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
- [Project Standards](project-standards.md): Project standards and technology stack
- [Documentation Standards](documentation-standards.md): Documentation standards
- [Java Maintenance](../../maintenance/java.md): Java maintenance process
- [SonarCloud Integration](../../maintenance/sonar.md): SonarCloud configuration and usage
