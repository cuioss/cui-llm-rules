# SonarCloud Verification

## Purpose
Verifies code quality through SonarCloud analysis and provides structured feedback.

## Related Commands
- `cp: verify sonar`: Quality analysis
- `cp: maintenance java perform`: Core maintenance
- `cp: maintenance java finalize`: Completion tasks

## Related Documentation
- core/standards/project-standards.md: Project standards and technology stack
- maintenance/documentation/javadoc.md: Documentation standards
- maintenance/java.md: Java maintenance process

## Access Configuration

### Repository Access
1. Get Current Branch:
   ```bash
   git rev-parse --abbrev-ref HEAD
   ```

2. Access Points:
   - Dashboard View:
     ```
     https://sonarcloud.io/dashboard?id=cuioss_<project-name>&branch=<branch-name>
     ```
   - Issues API:
     ```
     https://sonarcloud.io/api/issues/search?componentKeys=cuioss_<project-name>&branch=<branch-name>&resolved=false&sinceLeakPeriod=true
     ```

## Process Steps

1. Quality Gate Review
   - Check overall status
   - Review failing conditions
   - Note quality metric thresholds
   - Document gate configuration

2. Issue Analysis
   Review issues by:
   - Severity (MAJOR, MINOR, etc.)
   - Type (CODE_SMELL, BUG, VULNERABILITY)
   - Impact on quality metrics
   - Associated code locations
   - Rule references

3. Code Coverage Review
   - Overall coverage percentage
   - New code coverage
   - Uncovered lines
   - Critical areas lacking coverage
   - Test quality metrics

4. Security Assessment
   - Check for vulnerabilities
   - Review security hotspots
   - Assess security-related code smells
   - Verify dependency security

5. Documentation Update
   - Record findings
   - Document remediation steps
   - Note technical debt decisions
   - Update quality metrics

## Documentation Requirements

### Issue Documentation
1. File and line references must be precise
2. Include issue descriptions from SonarCloud
3. Note severity and impact levels
4. Document remediation steps
5. Reference specific SonarCloud rules

### Quality Metrics
1. Coverage percentages
2. Quality gate status
3. Issue counts by type
4. Technical debt metrics
5. Security assessment results

## Integration Points

### Review Schedule
1. Regular Review Points:
   - After major feature completion
   - Before creating pull requests
   - During code review process
   - Post-merge verification

2. Response Requirements:
   - Address all new issues promptly
   - Document intentional deviations
   - Track technical debt decisions
   - Update related documentation

## Success Criteria

1. Quality Analysis
   - All new issues identified
   - Impact assessed
   - Clear remediation paths
   - Documentation complete

2. Coverage Standards
   - Minimum coverage met
   - Critical paths covered
   - Test quality sufficient
   - No coverage regressions

3. Security Standards
   - No critical vulnerabilities
   - Security hotspots reviewed
   - Dependencies verified
   - Security best practices followed

## See Also
- core/standards/project-standards.md: Project standards and technology stack
- maintenance/documentation/javadoc.md: Documentation standards
- maintenance/java.md: Java maintenance process
