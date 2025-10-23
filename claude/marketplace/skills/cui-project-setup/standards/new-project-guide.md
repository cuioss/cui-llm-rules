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

## Requirement Prefix Standards

Determine the requirement prefix:

1. Choose a short, meaningful prefix (3-5 characters)
2. Recommended prefixes:
   - `NIFI-` for Apache NiFi related projects
   - `SEC-` for security-related projects
   - `API-` for API-related projects
   - `UI-` for user interface projects
   - `DB-` for database projects
   - `INT-` for integration projects
3. Custom prefixes should be relevant to the project domain

## Requirements Document Standards

### Requirements.adoc Template

```asciidoc
= Project Name Requirements
:toc:
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js

== Overview
This document outlines the requirements for Project Name, a component designed to...

== General Requirements

[#PREFIX-1]
=== PREFIX-1: Project Overview
* High-level requirement 1
* High-level requirement 2
* High-level requirement 3

[#PREFIX-2]
=== PREFIX-2: Core Functionality
* Core functionality requirement 1
* Core functionality requirement 2
* Core functionality requirement 3

[#PREFIX-2.1]
==== PREFIX-2.1: Sub-requirement
* Detailed requirement 1
* Detailed requirement 2
```

### Requirements Organization

Organize requirements into logical sections:

1. General Requirements
2. Functional Requirements
3. Non-Functional Requirements
4. Component-Specific Requirements

## Specification Document Standards

### Specification.adoc Template

```asciidoc
= Project Name Specification
:toc:
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js

== Overview
_See Requirement link:Requirements.adoc#PREFIX-1[PREFIX-1: Project Overview]_

This document provides the technical specification for implementing Project Name.
For functional requirements, see link:Requirements.adoc[Requirements Document].

== Document Structure
This specification is organized into the following documents:

* link:specification/technical-components.adoc[Technical Components] - Core implementation details
* link:specification/configuration.adoc[Configuration] - Configuration properties and UI
* link:specification/error-handling.adoc[Error Handling] - Error handling implementation
* link:specification/testing.adoc[Testing] - Unit and integration testing
* link:specification/security.adoc[Security] - Security considerations
* link:specification/integration-patterns.adoc[Integration Patterns] - Integration examples
* link:specification/internationalization.adoc[Internationalization] - i18n implementation
* link:LogMessages.adoc[Log Messages] - Logging standards and implementation
```

### Individual Specification Document Template

```asciidoc
= Project Name Technical Components
:toc:
:toclevels: 3
:toc-title: Table of Contents
:sectnums:
:source-highlighter: highlight.js

link:../Specification.adoc[Back to Main Specification]

== Core Components
_See Requirement link:../Requirements.adoc#PREFIX-2[PREFIX-2: Core Functionality]_

This section describes the core components of the Project Name implementation.

=== Component 1
_See Requirement link:../Requirements.adoc#PREFIX-2.1[PREFIX-2.1: Sub-requirement]_

The Component 1 is responsible for...

[source,java]
----
public class Component1 {
    // Implementation details
}
----
```

## Maintaining Traceability

1. Always ensure each specification section has a backtracking link to a requirement
2. When adding new requirements, update the corresponding specification documents
3. When updating specifications, ensure they remain aligned with requirements
4. Regularly review documentation to ensure consistency and completeness

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

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
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
