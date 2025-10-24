# CUI Project Setup Skill

Project initialization and configuration standards for CUI projects.

## Overview

The `cui-project-setup` skill provides standards for:

- Maven project structure and configuration
- Project initialization and scaffolding
- Dependency management
- Build plugin configuration
- Quality tool setup (Spotbugs, Checkstyle, JaCoCo)
- Frontend integration (frontend-maven-plugin)
- Multi-module project organization

## When to Use This Skill

Use `cui-project-setup` when:

- Initializing a new CUI project
- Setting up Maven configuration
- Configuring build plugins
- Establishing project structure
- Setting up quality tools and coverage
- Creating multi-module projects
- Integrating frontend and backend builds

## Prerequisites

**Required**:
- Java 17 or later
- Maven 3.8+
- Git for version control

**Optional**:
- Node.js 20.12.2 LTS (for frontend modules)
- Docker (for containerized applications)

## Standards Included

### New Project Guide (`new-project-guide.md`)

**Always loaded** - Complete project setup guide:

**Maven Configuration**:
- Standard directory layout (src/main/java, src/test/java, src/main/resources)
- pom.xml with proper parent (cui-parent or cui-bom)
- Group ID: `de.cuioss` or `io.github.cuioss`
- Semantic versioning (MAJOR.MINOR.PATCH)
- Required build plugins configuration

**Project Structure**:
- Reverse domain naming for packages
- Logical package organization by feature
- Separation of concerns
- Public API in root packages
- Implementation details in subpackages

**Initial Files**:
- README.adoc with standard structure
- LICENSE file (Apache 2.0)
- .gitignore for Java/Maven/Node
- pom.xml with complete configuration
- package-info.java files with @NullMarked

**Build Plugins**:
- maven-compiler-plugin (Java 17+)
- maven-surefire-plugin (unit tests)
- maven-failsafe-plugin (integration tests)
- jacoco-maven-plugin (code coverage)
- spotbugs-maven-plugin (static analysis)
- maven-checkstyle-plugin (code style)
- frontend-maven-plugin (if frontend)

**Quality Configuration**:
- Maven pre-commit profile
- JaCoCo coverage thresholds (80% line/branch)
- Spotbugs configuration
- Checkstyle rules
- Frontend quality tools (ESLint, Stylelint)

**Multi-Module Setup**:
- Parent POM configuration
- Module aggregation
- Dependency management section
- Shared plugin configuration
- Module dependencies

## Quick Start

### 1. Basic Maven Project

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

    <groupId>de.cuioss.portal</groupId>
    <artifactId>portal-authentication</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>jar</packaging>

    <name>CUI Portal Authentication</name>
    <description>Authentication module for CUI Portal</description>

    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <!-- CUI dependencies -->
        <dependency>
            <groupId>de.cuioss</groupId>
            <artifactId>cui-java-tools</artifactId>
        </dependency>

        <!-- JSpecify for null safety -->
        <dependency>
            <groupId>org.jspecify</groupId>
            <artifactId>jspecify</artifactId>
        </dependency>

        <!-- Lombok -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <scope>provided</scope>
        </dependency>

        <!-- Testing -->
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

    <build>
        <plugins>
            <!-- Compiler -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
            </plugin>

            <!-- Unit tests -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
            </plugin>

            <!-- Integration tests -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-failsafe-plugin</artifactId>
            </plugin>

            <!-- Code coverage -->
            <plugin>
                <groupId>org.jacoco</groupId>
                <artifactId>jacoco-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>

    <profiles>
        <!-- Coverage profile -->
        <profile>
            <id>coverage</id>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.jacoco</groupId>
                        <artifactId>jacoco-maven-plugin</artifactId>
                        <executions>
                            <execution>
                                <id>check</id>
                                <goals>
                                    <goal>check</goal>
                                </goals>
                                <configuration>
                                    <rules>
                                        <rule>
                                            <element>BUNDLE</element>
                                            <limits>
                                                <limit>
                                                    <counter>LINE</counter>
                                                    <value>COVEREDRATIO</value>
                                                    <minimum>0.80</minimum>
                                                </limit>
                                                <limit>
                                                    <counter>BRANCH</counter>
                                                    <value>COVEREDRATIO</value>
                                                    <minimum>0.80</minimum>
                                                </limit>
                                            </limits>
                                        </rule>
                                    </rules>
                                </configuration>
                            </execution>
                        </executions>
                    </plugin>
                </plugins>
            </build>
        </profile>

        <!-- Pre-commit profile -->
        <profile>
            <id>pre-commit</id>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-checkstyle-plugin</artifactId>
                    </plugin>
                    <plugin>
                        <groupId>com.github.spotbugs</groupId>
                        <artifactId>spotbugs-maven-plugin</artifactId>
                    </plugin>
                </plugins>
            </build>
        </profile>
    </profiles>
</project>
```

### 2. Directory Structure

```
project-name/
├── pom.xml
├── README.adoc
├── LICENSE
├── .gitignore
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── de/cuioss/portal/authentication/
│   │   │       ├── package-info.java        # @NullMarked
│   │   │       ├── TokenValidator.java
│   │   │       └── TokenLogMessages.java
│   │   └── resources/
│   │       └── application.properties
│   └── test/
│       ├── java/
│       │   └── de/cuioss/portal/authentication/
│       │       └── TokenValidatorTest.java
│       └── resources/
│           └── test-application.properties
└── target/                                  # Git-ignored
```

### 3. package-info.java Template

```java
/**
 * JWT token validation and authentication services.
 *
 * <p>All types in this package are non-null by default due to {@code @NullMarked}.
 * Use {@code @Nullable} to explicitly mark nullable types.
 *
 * @see de.cuioss.portal.authentication.TokenValidator
 */
@NullMarked
package de.cuioss.portal.authentication;

import org.jspecify.annotations.NullMarked;
```

### 4. .gitignore Template

```gitignore
# Maven
target/
pom.xml.tag
pom.xml.releaseBackup
pom.xml.versionsBackup
pom.xml.next
release.properties
dependency-reduced-pom.xml
buildNumber.properties

# IDE
.idea/
*.iml
.vscode/
.settings/
.project
.classpath

# Node (if frontend)
node_modules/
npm-debug.log
yarn-error.log

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

### 5. Multi-Module Project

```xml
<!-- Parent POM -->
<project>
    <modelVersion>4.0.0</modelVersion>

    <groupId>de.cuioss.portal</groupId>
    <artifactId>portal-parent</artifactId>
    <version>1.0.0-SNAPSHOT</version>
    <packaging>pom</packaging>

    <modules>
        <module>portal-core</module>
        <module>portal-authentication</module>
        <module>portal-ui</module>
    </modules>

    <dependencyManagement>
        <dependencies>
            <!-- Internal modules -->
            <dependency>
                <groupId>de.cuioss.portal</groupId>
                <artifactId>portal-core</artifactId>
                <version>${project.version}</version>
            </dependency>
        </dependencies>
    </dependencyManagement>
</project>
```

## Integration with Other Skills

**Recommended skill combinations**:

```yaml
# New project setup
skills:
  - cui-project-setup     # Project initialization (this skill)
  - cui-java-core         # Java development standards
  - cui-documentation     # README and docs

# Complete project
skills:
  - cui-project-setup
  - cui-java-core
  - cui-java-unit-testing
  - cui-javadoc
  - cui-documentation
```

## Common Setup Tasks

### Initialize New Java Library

1. Create directory structure
2. Create pom.xml with cui-parent
3. Set up package structure
4. Create package-info.java with @NullMarked
5. Add .gitignore
6. Create README.adoc
7. Add LICENSE file
8. Initialize Git repository
9. Verify build: `mvn clean install`

### Add Frontend Module

1. Create frontend module directory
2. Configure frontend-maven-plugin in pom.xml
3. Create package.json
4. Set up Node.js version (20.12.2 LTS)
5. Configure Jest and ESLint
6. Add frontend sources
7. Verify: `mvn clean install`

### Set Up Quality Tools

1. Add jacoco-maven-plugin
2. Configure coverage thresholds (80%)
3. Add spotbugs-maven-plugin
4. Add maven-checkstyle-plugin
5. Create pre-commit profile
6. Verify: `mvn clean verify -Ppre-commit,coverage`

### Create Multi-Module Project

1. Create parent POM with modules
2. Set up dependencyManagement
3. Create module directories
4. Configure inter-module dependencies
5. Verify: `mvn clean install`

## Verification Checklist

After project setup:

**Project Structure**:
- [ ] Standard directory layout
- [ ] package-info.java with @NullMarked
- [ ] README.adoc present
- [ ] LICENSE file present
- [ ] .gitignore configured

**Maven Configuration**:
- [ ] pom.xml complete
- [ ] Java 17+ configured
- [ ] Dependencies declared
- [ ] Build plugins configured
- [ ] Profiles set up

**Build Verification**:
- [ ] Clean build succeeds: `mvn clean install`
- [ ] Tests pass: `mvn clean test`
- [ ] Coverage profile works: `mvn clean verify -Pcoverage`
- [ ] Pre-commit passes: `mvn clean verify -Ppre-commit`

**Quality Tools**:
- [ ] JaCoCo configured (80% threshold)
- [ ] Spotbugs configured
- [ ] Checkstyle configured
- [ ] All checks passing

## Quality Standards

This skill enforces:

- **Standard structure**: Maven conventions
- **Java 17+**: Modern Java version
- **Semantic versioning**: MAJOR.MINOR.PATCH
- **Quality gates**: 80% coverage minimum
- **Consistent naming**: Reverse domain packages
- **Complete configuration**: All required plugins

## Examples

See `standards/new-project-guide.md` for comprehensive examples including:

- Complete pom.xml templates
- Multi-module project structures
- Frontend integration configuration
- Quality tool setup
- CI/CD integration
- Quarkus project setup

## Support

For issues or questions:

1. Review `standards/new-project-guide.md`
2. Check Maven documentation
3. Verify Java version (17+ required)
4. Consult CUI parent POM
5. Review existing CUI projects for patterns

## License

Part of the CUI LLM Rules documentation system for CUI OSS projects.
