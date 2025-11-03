# New Project Guide

## Purpose
Standards for creating new CUI projects including requirements, specifications, and directory structure.

## Directory Structure Standards

Create the basic directory structure:

```
project-root/
├── doc/
│   ├── Requirements.adoc
│   ├── Specification.adoc
│   ├── LogMessages.adoc
│   └── specification/
│       ├── technical-components.adoc
│       ├── configuration.adoc
│       ├── error-handling.adoc
│       ├── testing.adoc
│       ├── security.adoc
│       ├── integration-patterns.adoc
│       └── internationalization.adoc
├── src/
│   ├── main/
│   │   ├── java/
│   │   └── resources/
│   └── test/
│       ├── java/
│       └── resources/
└── pom.xml
```

## Requirements and Specification Documentation

For complete guidance on requirements and specification documentation:

**See cui-requirements skill** (invoked in SKILL.md Step 1)

The cui-requirements skill provides:
- Requirement document structure and templates
- Specification document organization
- Requirement ID prefixes and numbering standards
- Planning document formats
- Traceability and backtracking link patterns

This skill focuses on the **technical project setup** (Maven configuration, directory structure, and build configuration).

## Maven Project Setup

### POM.xml Template

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
                             http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>de.cuioss</groupId>
        <artifactId>cui-java-parent</artifactId>
        <version>1.3.6</version>
        <relativePath/>
    </parent>

    <artifactId>project-name</artifactId>
    <name>Project Name</name>
    <version>1.0.0-SNAPSHOT</version>
    <description>Project description</description>
    <packaging>jar</packaging>

    <url>https://github.com/cuioss/project-name/</url>

    <scm>
        <url>https://github.com/cuioss/project-name/</url>
        <connection>scm:git:https://github.com/cuioss/project-name.git</connection>
        <developerConnection>scm:git:https://github.com/cuioss/project-name/</developerConnection>
        <tag>HEAD</tag>
    </scm>

    <issueManagement>
        <url>https://github.com/cuioss/project-name/issues</url>
        <system>GitHub Issues</system>
    </issueManagement>

    <properties>
        <maven.compiler.release>21</maven.compiler.release>
        <maven.jar.plugin.automatic.module.name>de.cuioss.project.name</maven.jar.plugin.automatic.module.name>
    </properties>

    <dependencies>
        <!-- Lombok -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
        </dependency>
        <!-- JSpecify -->
        <dependency>
            <groupId>org.jspecify</groupId>
            <artifactId>jspecify</artifactId>
        </dependency>
        <!-- Unit testing -->
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>de.cuioss.test</groupId>
            <artifactId>cui-test-generator</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
```

**Note:** The parent POM (`cui-java-parent`) handles all plugin configuration (compiler, surefire, failsafe, jacoco, etc.). Do not duplicate plugin configuration in project POMs.

## Package Structure

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

## Logging Requirements

When implementing logging in a new project:

1. Add a dedicated section for logging requirements in Requirements.adoc
2. Create a dedicated LogMessages.adoc file in the doc directory
3. Follow logging standards and implementation guides

## Initial Git Commit

```bash
git init
git add .
git commit -m "feat: Initial project setup

- Maven project structure
- Requirements and specification documents
- Standard configuration
- Initial documentation"
```

## Frontend Integration Setup

For projects with frontend components (JavaScript, CSS, web components):

### package.json Template

```json
{
  "name": "module-name",
  "version": "1.0.0",
  "description": "Module description",
  "scripts": {
    "lint": "eslint src/main/resources/META-INF/resources/javascript",
    "lint:fix": "eslint --fix src/main/resources/META-INF/resources/javascript",
    "format": "prettier --write src/main/resources/META-INF/resources",
    "test": "cypress run",
    "test:open": "cypress open"
  },
  "devDependencies": {
    "eslint": "^8.0.0",
    "prettier": "^3.0.0",
    "cypress": "^13.0.0"
  }
}
```

### Frontend Directory Structure

```
src/main/resources/META-INF/resources/
├── javascript/
│   └── modules/
│       └── module-name/
│           ├── components/
│           └── utils/
└── css/
    └── module-name.css
```

### Maven Integration

The `frontend-maven-plugin` integration is handled by cui-java-parent. Projects only need to:
1. Add `package.json` in project root
2. Define npm scripts for lint, format, test
3. Organize JavaScript/CSS in standard resource paths

For detailed Maven/JavaScript integration, see cui-frontend-development skill.

## .gitignore Template

```gitignore
# Maven
target/
pom.xml.tag
pom.xml.releaseBackup
pom.xml.versionsBackup
pom.xml.next
release.properties
dependency-reduced-pom.xml

# Node.js / Frontend
node_modules/
package-lock.json
.npm/
dist/

# IDE
.idea/
*.iml
.vscode/
.settings/
.project
.classpath

# OS
.DS_Store
Thumbs.db

# Test Reports
cypress/videos/
cypress/screenshots/
```

## README.adoc Template

```asciidoc
= Project Name

Description of the project purpose and functionality.

== Maven Coordinates

[source,xml]
----
<dependency>
    <groupId>de.cuioss</groupId>
    <artifactId>module-name</artifactId>
    <version>1.0.0</version>
</dependency>
----

== Features

* Feature 1
* Feature 2
* Feature 3

== Requirements

* Java 17+
* Maven 3.8+
* Node.js 20+ (if using frontend components)

== Building

[source,bash]
----
mvn clean install
----

== License

Apache License 2.0 - See LICENSE file
```

## Quality Checklist

- [ ] Directory structure complete
- [ ] Requirements.adoc created with proper prefix
- [ ] Specification.adoc created with backtracking links
- [ ] Individual specification documents created
- [ ] Maven pom.xml configured with parent POM and dependencies
- [ ] Package structure follows standards
- [ ] .gitignore configured (using template above)
- [ ] README.adoc present (using template above)
- [ ] LICENSE file included
- [ ] Parent POM properly referenced (cui-java-parent)
- [ ] Frontend setup complete (if applicable):
  - [ ] package.json configured
  - [ ] npm scripts defined
  - [ ] Frontend directory structure created
  - [ ] ESLint and Prettier configured
