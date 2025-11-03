---
name: cui-project-setup
description: Project initialization and configuration standards for CUI projects
allowed-tools: [Read, Edit, Write, Bash, Glob]
---

# CUI Project Setup Skill

Standards for initializing and configuring new CUI projects including Maven setup, dependencies, structure, and configuration.

## Workflow

### Step 1: Load Requirements Engineering Standards

**CRITICAL**: Load requirements and specification documentation standards first.

```
Skill: cui-requirements
```

This skill provides comprehensive guidance on:
- Requirements document structure and format
- Specification standards and organization
- Requirement ID prefixes and numbering
- Planning document templates

### Step 2: Load Project Setup Standards

**CRITICAL**: Load project setup standards for technical configuration.

```
Read: standards/new-project-guide.md
```

### Step 3: Analyze Project Requirements

**When to Execute**: Before starting project setup

**What to Analyze**:

1. **Project Type**:
   - Java library module
   - Quarkus application
   - Frontend module (JavaScript/CSS)
   - Maven parent/aggregator
   - Multi-module project

2. **Technology Stack**:
   - Java version (17+ required)
   - Quarkus version
   - Build tools (Maven)
   - Testing frameworks (JUnit 5, Jest)
   - Additional frameworks

3. **Dependencies**:
   - Core CUI dependencies
   - Third-party libraries
   - Testing dependencies
   - Build plugins

4. **Project Structure**:
   - Module organization
   - Package naming
   - Directory layout
   - Resource organization

### Step 4: Apply Project Setup Standards

**When to Execute**: During project initialization

**What to Apply**:

Apply project setup standards from `standards/new-project-guide.md`:
- Maven project structure and POM configuration
- Package structure and naming conventions
- Initial file templates (.gitignore, README.adoc, LICENSE)
- Frontend integration setup (if applicable)

**Note**: The parent POM (cui-java-parent) handles all plugin configuration. See new-project-guide.md for complete templates.

### Step 5: Verify Project Setup

**When to Execute**: After project initialization

**Quality Checks**:

1. **Build Verification**:
   - [ ] Clean build succeeds: `mvn clean install`
   - [ ] Pre-commit checks pass: `mvn -Ppre-commit clean verify`
   - [ ] Parent POM referenced correctly
   - [ ] Dependency resolution works

2. **Structure Verification**:
   - [ ] Standard directory layout
   - [ ] Package naming conventions followed
   - [ ] README.adoc present and complete
   - [ ] .gitignore configured
   - [ ] LICENSE file included

3. **Testing Verification**:
   - [ ] Tests run successfully

4. **Frontend Verification** (if applicable):
   - [ ] package.json configured
   - [ ] Node.js version specified
   - [ ] npm scripts configured
   - [ ] Frontend tests configured

### Step 6: Document and Commit

**When to Execute**: After verification passes

**Process**:
1. Initialize git repository
2. Stage all files
3. Create initial commit (see standards/new-project-guide.md for commit message template)

## Common Project Setup Patterns

Refer to `standards/new-project-guide.md` for detailed templates including:
- Maven POM structure and configuration
- Java package organization
- Git commit message format
- Frontend project setup guidelines

## Quality Verification

All project setup must pass:
- [x] Clean build succeeds
- [x] Pre-commit checks pass
- [x] Standard directory layout
- [x] README.adoc present
- [x] Parent POM referenced
- [x] Tests run successfully

## References

* New Project Guide: standards/new-project-guide.md
* CUI Parent POM: https://github.com/cuioss
* Maven Standards: https://maven.apache.org/guides/
