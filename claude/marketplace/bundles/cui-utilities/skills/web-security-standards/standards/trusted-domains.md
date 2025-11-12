# Trusted Domains

Pre-approved domains for WebFetch operations that have passed comprehensive security assessment and meet CUI trust criteria.

## Purpose

This document provides a curated list of domains that are pre-approved for WebFetch operations in CUI projects. These domains have been evaluated against security criteria defined in [domain-security-assessment.md](domain-security-assessment.md) and deemed safe for automated web fetching operations.

**When to use this list:**
- Before requesting WebFetch permissions for a domain, check if it's already trusted
- When reviewing pull requests that add WebFetch permissions
- During security audits of project permissions

**When additional review is needed:**
- If the specific URL path on a trusted domain seems suspicious
- If the trusted domain has been compromised (check security news)
- If fetching sensitive or dynamic content (API endpoints, user data)

## Selection Criteria

Domains on this list meet ALL of the following criteria:

1. **Security**
   - Valid HTTPS with up-to-date SSL certificate
   - No history of malware, phishing, or security incidents
   - Not listed on security blocklists (URLhaus, PhishTank, Google Safe Browsing)
   - Implements security headers (HSTS, CSP)

2. **Reputation**
   - Established presence (domain age >1 year for non-major companies)
   - Verifiable ownership by reputable organization
   - Positive community reputation
   - Professional web presence with clear purpose

3. **Relevance**
   - Provides documentation, tools, or resources relevant to software development
   - Commonly used by development community
   - Maintains stable, reliable content

4. **Maintenance**
   - Active updates and maintenance
   - Responsive to security issues
   - Clear content governance

For detailed security assessment methodology, see [domain-security-assessment.md](domain-security-assessment.md).

## Trust Level Taxonomy

For complete trust level definitions and decision framework, see **[domain-security-assessment.md](domain-security-assessment.md)** section "Trust Levels".

Domains in this list are classified using a 4-level taxonomy:
- **Fully Trusted**: Official documentation, major tech companies, established foundations
- **Generally Trusted**: Popular resources requiring verification before use
- **Review Required**: Case-by-case assessment needed (see domain-security-assessment.md)
- **High Scrutiny**: Thorough review required (see domain-security-assessment.md)

## Trusted Domains List

### Major Documentation Sites

Official documentation for widely-used technologies and frameworks:

- **docs.anthropic.com** - Claude AI documentation
  - Purpose: Claude API, Claude Code documentation
  - Trust Level: Fully Trusted (First-party documentation)

- **docs.github.com** - GitHub documentation
  - Purpose: Git, GitHub Actions, API documentation
  - Trust Level: Fully Trusted (Major tech company)

- **docs.oracle.com** - Oracle Java documentation
  - Purpose: Java API documentation, Java SE/EE specs
  - Trust Level: Fully Trusted (Official Java documentation)

- **docs.spring.io** - Spring Framework documentation
  - Purpose: Spring Boot, Spring Framework docs
  - Trust Level: Fully Trusted (Official framework documentation)

- **maven.apache.org** - Apache Maven
  - Purpose: Maven documentation, plugin repository
  - Trust Level: Fully Trusted (Apache Foundation)

- **quarkus.io** - Quarkus Framework
  - Purpose: Quarkus documentation and guides
  - Trust Level: Fully Trusted (Red Hat/Open Source)

- **junit.org** - JUnit Testing Framework
  - Purpose: JUnit 5 documentation
  - Trust Level: Fully Trusted (Established testing framework)

### Development Communities

Platforms for developer knowledge sharing:

- **github.com** - Code hosting and collaboration
  - Purpose: Repository browsing, issue tracking, releases
  - Trust Level: Fully Trusted (Major platform)
  - Note: Verify specific repository authenticity

- **stackoverflow.com** - Developer Q&A
  - Purpose: Programming questions and answers
  - Trust Level: Fully Trusted (Stack Exchange network)

- **medium.com** - Technical articles and tutorials
  - Purpose: Developer blogs, technical articles
  - Trust Level: Generally Trusted
  - Note: Verify author reputation for critical information

- **dev.to** - Developer community platform
  - Purpose: Developer articles, tutorials, discussions
  - Trust Level: Generally Trusted
  - Note: Community-contributed content, verify accuracy

## Usage Guidelines

### For Developers

When adding WebFetch permissions to a project:

1. **Check this list first** - If domain is listed, reference this document in PR description
2. **If not listed** - Perform security assessment using [domain-security-assessment.md](domain-security-assessment.md)
3. **Document justification** - Explain why domain access is needed
4. **Use specific paths** - Prefer specific path patterns over domain wildcards when possible

### For Code Reviewers

When reviewing WebFetch permission requests:

1. **Verify against trusted list** - Trusted domains should be approved quickly
2. **For new domains** - Ensure proper security assessment was performed
3. **Check for alternatives** - Can a trusted domain be used instead?
4. **Validate scope** - Ensure permissions are as narrow as possible

## Maintenance Procedures

### Adding New Domains

To add a domain to this trusted list:

1. **Perform comprehensive assessment** using [domain-security-assessment.md](domain-security-assessment.md)
2. **Document findings** including:
   - Security verification results (SSL, blocklists, reputation)
   - Ownership and organizational details
   - Relevance to development workflows
   - Trust level designation
3. **Submit PR** with domain addition and assessment documentation
4. **Require security review** - Changes to this list need approval from security stakeholders

### Reviewing Existing Domains

Periodically review trusted domains (recommended: quarterly):

1. **Check for security incidents** - Search for "[domain] security breach" or "[domain] compromised"
2. **Verify SSL certificate** - Ensure valid and up-to-date
3. **Review blocklist status** - Check Google Safe Browsing, VirusTotal
4. **Assess continued relevance** - Is domain still actively maintained and used?
5. **Remove or downgrade** if domain no longer meets criteria

### Reporting Issues

If you discover a security issue with a trusted domain:

1. **Immediately notify security team** - Don't wait for scheduled review
2. **Document the issue** - Include evidence and impact assessment
3. **Submit PR to remove or downgrade** domain from trusted list
4. **Update affected projects** - Review projects using the domain

## Risk Mitigation

Even for trusted domains, implement defense-in-depth:

1. **Validate responses** - Check content type, size, format before processing
2. **Sanitize content** - Don't blindly execute or render fetched content
3. **Handle errors gracefully** - Don't expose internal details in error messages
4. **Log access** - Monitor WebFetch usage for anomalies
5. **Rate limit** - Implement reasonable rate limits to prevent abuse

## Related Standards

- [domain-security-assessment.md](domain-security-assessment.md) - Comprehensive security assessment methodology
- See permission-management standards in the cui-utilities bundle for WebFetch permission validation patterns
