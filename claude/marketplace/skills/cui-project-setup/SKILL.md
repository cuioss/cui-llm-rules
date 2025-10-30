---
name: cui-project-setup
description: Project initialization and configuration standards for CUI projects
allowed-tools: [Read, Edit, Write, Bash, Glob]
---

# CUI Project Setup Skill

Standards for initializing and configuring new CUI projects including Maven setup, dependencies, structure, and configuration.

## Workflow

### Step 1: Load Project Setup Standards

**CRITICAL**: Load project setup standards for guidance.

```
Read: standards/new-project-guide.md
```

### Step 2: Analyze Project Requirements

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

### Step 3: Apply Project Setup Standards

**When to Execute**: During project initialization

**What to Apply**:

1. **Maven Project Structure**:
   - Standard directory layout (src/main/java, src/test/java)
   - Maven pom.xml with proper parent
   - Group ID: `de.cuioss` or `io.github.cuioss`
   - Follow semantic versioning
   - Include required build plugins

2. **Project Configuration**:
   - Configure Maven compiler (Java 17+)
   - Set up dependency management
   - Configure build plugins (surefire, failsafe, jacoco)
   - Set up quality plugins (spotbugs, checkstyle)
   - Configure frontend-maven-plugin (if applicable)

3. **Package Structure**:
   - Follow reverse domain naming
   - Logical package organization
   - Separation of concerns
   - Public API in root packages

4. **Initial Files**:
   - README.adoc with standard structure
   - LICENSE file
   - .gitignore for Java/Maven/Node
   - pom.xml with complete configuration
   - Basic test structure

5. **Quality Configuration**:
   - Maven pre-commit profile
   - JaCoCo coverage configuration
   - Spotbugs configuration
   - Checkstyle rules
   - Frontend quality tools (if applicable)

### Step 4: Verify Project Setup

**When to Execute**: After project initialization

**Quality Checks**:

1. **Build Verification**:
   - [ ] Clean build succeeds: `mvn clean install`
   - [ ] Pre-commit checks pass: `mvn -Ppre-commit clean verify`
   - [ ] All plugins configured correctly
   - [ ] Dependency resolution works

2. **Structure Verification**:
   - [ ] Standard directory layout
   - [ ] Package naming conventions followed
   - [ ] README.adoc present and complete
   - [ ] .gitignore configured
   - [ ] LICENSE file included

3. **Quality Tool Verification**:
   - [ ] JaCoCo configured
   - [ ] Spotbugs configured
   - [ ] Tests run successfully
   - [ ] Coverage thresholds set

4. **Frontend Verification** (if applicable):
   - [ ] package.json configured
   - [ ] Node.js version specified
   - [ ] npm scripts configured
   - [ ] Frontend tests configured

### Step 5: Document and Commit

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
- [x] Quality tools configured
- [x] Tests run successfully

## References

* New Project Guide: standards/new-project-guide.md
* CUI Parent POM: https://github.com/cuioss
* Maven Standards: https://maven.apache.org/guides/
