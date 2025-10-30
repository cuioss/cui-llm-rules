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
- Initial documentation
```

## Quality Checklist

- [ ] Directory structure complete
- [ ] Requirements.adoc created with proper prefix
- [ ] Specification.adoc created with backtracking links
- [ ] Individual specification documents created
- [ ] Maven pom.xml configured
- [ ] Package structure follows standards
- [ ] .gitignore configured
- [ ] README.adoc present
- [ ] LICENSE file included
