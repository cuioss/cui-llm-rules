# Project Standards and Technology Stack

## Purpose
Defines the core project standards, technology stack, and framework guidelines for CUI OSS projects.

## Related Commands
- `cp: maintenance java prepare`: Project preparation and setup
- `cp: maintenance java perform`: Core maintenance and updates
- `cp: maintenance java finalize`: Maintenance completion
- `cp: verify sonar`: Quality analysis

## Related Documentation
- maintenance/java.md: Java maintenance process
- core/standards/documentation-standards.md: Documentation standards
- core/standards/quality-standards.md: Quality standards
- core/standards/version-control-standards.md: Version control and commit standards
- cascade/verify-rules.md: Documentation verification

## Core Standards

### 1. Technology Stack

#### Java Platform
- Java 17 LTS or higher
- Jakarta EE compatible
- Maven-based build system
- CDI for dependency injection

#### Core Libraries
- cuioss libraries (preferred)
- cui-java-tools (standard utility)

#### Build Tools
- Maven wrapper (mvnw) required
- Maven plugins must be version-locked
- Standardized plugin configurations
- Parent POM inheritance

#### Testing Framework
- JUnit 5 for unit testing
- JaCoCo for code coverage

#### Quality Tools
- SonarCloud for code analysis
- OpenRewrite for code modernization

### 2. Build Configuration

#### Maven Wrapper Usage
1. Always use maven-wrapper (mvnw) when available
2. Run complete module build after each change
3. Create local commit after each successful build

#### Build Command Format
- Full build: `./mvnw clean verify`
- Module build: `./mvnw clean verify -rf :module-name`
- Test only: `./mvnw test`
- Install: `./mvnw clean install`

#### Build Optimization
1. During multi-module builds:
   - Use `-rf :module-name` to resume from specific module
   - Only build affected module and downstream dependencies
   - Example: `./mvnw clean verify -rf :module-name`

2. Build Sequence Rules:
   - Verify all tests pass before commit
   - Keep commits atomic and focused
   - Run up to 5 consecutive builds maximum without user interaction
   - For Javadoc builds, see core/standards/documentation-standards.md

### 3. Framework Guidelines

#### Dependency Management
1. Use managed dependencies via parent POM
2. Explicit versioning in dependency management
3. Regular dependency updates and audits
4. Security vulnerability monitoring
5. Prefer cuioss libraries
6. Use cui-java-tools as standard utility

#### Code Style
1. Follow Java coding conventions
2. Maintain consistent formatting
3. Apply clean code principles
4. Use consistent naming patterns
5. Follow package structure guidelines

#### Version Control
1. Git for source control
2. Feature branch workflow
3. Semantic versioning
4. Conventional commits
5. Pull request reviews

### 4. Documentation Standards

#### Project Documentation
1. README.adoc in project root
2. Module-specific documentation
3. API documentation (see core/standards/documentation-standards.md)
4. Build and deployment instructions

#### Change Documentation
1. Conventional commit messages
2. Pull request documentation
3. Migration guides when needed
4. Release notes for significant changes

### 5. Quality Standards

#### Code Quality
1. Sonar Requirements
   - Quality gates must pass
   - No critical issues
   - Technical debt managed
   - Security vulnerabilities must be addressed immediately
   - Regular security audits required

2. Test Coverage
   - Minimum 80% coverage
   - Critical paths covered
   - Integration test coverage required for all APIs
   - All tests passing
   - Regular integration test maintenance

3. Documentation Quality
   - Complete API documentation
   - Up-to-date project documentation
   - Clear usage examples
   - Maintained change history

## Success Criteria

### 1. Build and Test
- All builds successful
- Tests passing
- Coverage requirements met
- No critical issues pending

### 2. Documentation
- Documentation complete and current
- API documentation standards met
- Build instructions accurate
- Change history maintained

### 3. Quality Gates
- Sonar quality gates passed
- Test coverage thresholds met
- No critical issues
- Security requirements satisfied

## See Also
- core/standards/documentation-standards.md: Documentation standards
- core/standards/quality-standards.md: Quality and testing standards
- maintenance/documentation/progress-management.md: Progress and phase management
