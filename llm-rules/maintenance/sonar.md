# SonarCloud Verification

## Command: cp: verify sonar

### Purpose
Verifies code quality through SonarCloud analysis and provides structured feedback.

### Process Steps

1. Access Setup
   a. Get Current Branch:
   ```bash
   git rev-parse --abbrev-ref HEAD
   ```
   
   b. Access Points:
   - Dashboard View:
     ```
     https://sonarcloud.io/dashboard?id=cuioss_<project-name>&branch=<branch-name>
     ```
   - Issues API:
     ```
     https://sonarcloud.io/api/issues/search?componentKeys=cuioss_<project-name>&branch=<branch-name>&resolved=false&sinceLeakPeriod=true
     ```

2. Quality Gate Review
   - Check overall status
   - Review failing conditions
   - Note quality metric thresholds

3. Issue Analysis
   Review issues by:
   - Severity (MAJOR, MINOR, etc.)
   - Type (CODE_SMELL, BUG, VULNERABILITY)
   - Impact on quality metrics
   - Associated code locations
   - Rule references

4. Code Coverage Review
   - Overall coverage percentage
   - New code coverage
   - Uncovered lines
   - Critical areas lacking coverage

5. Security Assessment
   - Check for vulnerabilities
   - Review security hotspots
   - Assess security-related code smells

### Documentation Requirements
1. File and line references must be precise
2. Include issue descriptions from SonarCloud
3. Note severity and impact levels
4. Document remediation steps
5. Reference specific SonarCloud rules

### Integration Points
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

### Success Criteria
1. All new issues identified
2. Impact on code quality assessed
3. Clear remediation paths provided
4. Findings properly documented
5. Integration with existing quality processes complete
