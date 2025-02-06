# Technology Stack and Framework Guidelines

## Purpose
Defines the standard technology stack and framework guidelines for CUI OSS projects.

## Related Commands
- `cp: maintenance java perform`: Technology stack updates
- `cp: maintenance java prepare`: Project setup
- `cp: verify sonar`: Quality analysis

## Related Documentation
- project.md: Project configuration
- maintenance/java.md: Java maintenance
- maintenance/sonar.md: Quality analysis

## Core Technologies

### Java Platform
- Java 17 LTS or higher
- Jakarta EE compatible
- Maven-based build system
- CDI for dependency injection

### Build Tools
- Maven wrapper (mvnw) required
- Maven plugins must be version-locked
- Standardized plugin configurations
- Parent POM inheritance

### Testing Framework
- JUnit 5 for unit testing
- JaCoCo for code coverage

### Quality Tools
- SonarCloud for code analysis
- OpenRewrite for code modernization

## Framework Guidelines

### Dependency Management
1. Use managed dependencies via parent POM
2. Explicit versioning in dependency management
3. Regular dependency updates and audits
4. Security vulnerability monitoring
5. Prefer cuioss libraries
6. Use cui-java-tools as standard utility

### Code Style
1. Follow Java coding conventions
2. Maintain consistent formatting
3. Apply clean code principles
4. Use consistent naming patterns
5. Follow package structure guidelines

### Documentation
1. API Documentation
   - See maintenance/documentation/javadoc.md for complete Javadoc standards
   - All public APIs must be documented according to standards

2. Project Documentation
   - README.adoc for project overview
   - Module-specific documentation
   - API documentation
   - Build instructions

3. Change Documentation
   - Conventional commit messages
   - Pull request documentation

### Version Control
1. Git for source control
2. Feature branch workflow
3. Semantic versioning
4. Conventional commits
5. Pull request reviews

## Quality Standards
1. Code Coverage
   - Minimum 80% coverage
   - Critical paths covered
   - Integration test coverage

2. Code Quality
   - Sonar quality gates passed
   - No critical issues
   - Technical debt managed
   - Security vulnerabilities addressed

3. Documentation Quality
   - Complete API documentation
   - Up-to-date project documentation
   - Clear usage examples
   - Maintained change history

## Success Criteria
1. All quality gates passed
2. Documentation complete
3. Tests passing
4. Coverage requirements met
5. No critical issues pending

## See Also
- project.md: Project configuration details
- maintenance/java.md: Java maintenance process
- maintenance/sonar.md: Quality analysis process