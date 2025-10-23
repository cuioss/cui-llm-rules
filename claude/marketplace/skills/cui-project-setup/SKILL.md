---
name: cui-project-setup
description: Project initialization and configuration standards for CUI projects
tools: [Read, Edit, Write, Bash, Glob]
---

# CUI Project Setup Skill

Standards for initializing and configuring new CUI projects including Maven setup, dependencies, structure, and configuration.

## Workflow

### Step 1: Load Project Setup Standards

**CRITICAL**: Load project setup standards for guidance.

```
Read: ../../standards/requirements/new-project-guide.adoc
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

**Initial Commit**:
```bash
git init
git add .
git commit -m "feat: Initial project setup

- Maven project structure
- Standard configuration
- Quality tools configured
- Initial documentation

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Common Project Setup Patterns

### Maven POM Structure
```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                             http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>de.cuioss</groupId>
        <artifactId>cui-parent</artifactId>
        <version>1.0.0</version>
    </parent>

    <groupId>de.cuioss</groupId>
    <artifactId>project-name</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <name>Project Name</name>

    <properties>
        <java.version>17</java.version>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
    </properties>

    <dependencies>
        <!-- Dependencies here -->
    </dependencies>

    <build>
        <plugins>
            <!-- Build plugins here -->
        </plugins>
    </build>
</project>
```

### Package Structure
```
src/main/java/
└── de/cuioss/projectname/
    ├── core/           # Core functionality
    ├── model/          # Data models
    ├── service/        # Business logic
    └── util/           # Utilities

src/test/java/
└── de/cuioss/projectname/
    ├── core/
    ├── model/
    ├── service/
    └── util/
```

## Quality Verification

All project setup must pass:
- [x] Clean build succeeds
- [x] Pre-commit checks pass
- [x] Standard directory layout
- [x] README.adoc present
- [x] Quality tools configured
- [x] Tests run successfully

## References

* New Project Guide: ../../standards/requirements/new-project-guide.adoc
* CUI Parent POM: https://github.com/cuioss
* Maven Standards: https://maven.apache.org/guides/
