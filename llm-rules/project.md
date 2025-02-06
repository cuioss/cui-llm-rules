# Project Configuration and Build Rules

## Purpose
Defines the core project configuration and build rules for CUI OSS projects.

## Related Commands
- `cp: maintenance java prepare`: Project preparation and initial setup
- `cp: maintenance java perform`: Core maintenance execution
- `cp: maintenance java finalize`: Maintenance completion

## Related Documentation
- maintenance/java.md: Java maintenance process
- maintenance/documentation/javadoc.md: Javadoc standards
- technologies.md: Technology standards
- cascade/verify-rules.md: Documentation verification

## Build Configuration

### Maven Wrapper Usage
1. Always use maven-wrapper (mvnw) when available
2. Run complete module build after each change
3. Create local commit after each successful build

### Build Optimization
1. During build and fix cycles in multi-module projects:
   - Use `-rf :module-name` to resume from specific module
   - Only build affected module and downstream dependencies
   - Example: `./mvnw clean verify -rf :module-name`

2. Build Command Format:
   - Full build: `./mvnw clean verify`
   - Module build: `./mvnw clean verify -rf :module-name`
   - Test only: `./mvnw test`
   - Install: `./mvnw clean install`

3. Build Sequence Rules:
   - Verify all tests pass before commit
   - Keep commits atomic and focused
   - Run up to 5 consecutive builds without user interaction
   - For Javadoc builds, see maintenance/documentation/javadoc.md

## Project Standards

### Technology Stack
1. Java Version: Java 17
2. Enterprise Framework: Jakarta EE
3. Dependency Injection: CDI
4. Core Libraries:
   - cuioss libraries (preferred)
   - cui-java-tools (standard utility)

### Documentation Requirements
1. README.adoc in project root
2. Module-specific documentation
3. For API documentation standards, see maintenance/documentation/javadoc.md
4. Build and deployment instructions

### Quality Standards
1. Sonar quality gates must pass
2. Test coverage requirements met
3. Documentation up to date
4. No critical issues pending

## Success Criteria
1. All builds successful
2. Tests passing
3. Documentation complete
4. Standards followed
5. Quality gates passed

## See Also
- technologies.md: Detailed technology standards
- maintenance/java.md: Java maintenance process
- maintenance/documentation/javadoc.md: Javadoc standards