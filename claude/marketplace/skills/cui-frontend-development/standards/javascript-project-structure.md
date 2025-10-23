# JavaScript Project Structure Standards

## Purpose
Standards for JavaScript project structure, package.json configuration, and Maven integration for consistent development environments across CUI projects.

## Directory Structure Standards

### Standard Maven Projects
```
project-root/
├── package.json
├── .prettierrc.js
├── .eslintrc.js
├── src/
│   ├── main/resources/static/js/   # JavaScript source files
│   └── test/js/                    # JavaScript tests
└── target/                         # Build output
```

### Quarkus DevUI Projects
```
project-root/
├── package.json
├── .prettierrc.js
├── .eslintrc.js
├── src/
│   ├── main/resources/dev-ui/      # DevUI components
│   └── test/js/                    # Component tests with Lit mocks
└── target/
```

### NiFi Extension Projects
```
project-root/
├── package.json
├── webpack.config.js
├── src/
│   ├── main/webapp/js/             # NiFi UI components
│   └── test/js/                    # Tests with NiFi mocks
└── target/                         # WAR output
```

## File Naming Conventions
* **JavaScript files**: `kebab-case.js` (e.g., `user-service.js`, `api-client.js`)
* **Test files**: `kebab-case.test.js` (e.g., `user-service.test.js`)
* **Mock files**: `kebab-case.js` (e.g., `api-client-mock.js`)
* **Setup files**: `descriptive-name.js` (e.g., `jest.setup-dom.js`)
* **Component files**:
  - Quarkus DevUI: `qwc-component-name.js` (e.g., `qwc-jwt-config.js`)
  - General components: `component-name.js` (e.g., `user-profile.js`)

## Package.json Core Scripts

### Technology-Agnostic Scripts (Required)
All frontend projects must include:

```json
{
  "scripts": {
    "lint": "npm run lint:js",
    "lint:fix": "npm run lint:js:fix",
    "format": "npm run format:js",
    "format:check": "npm run format:js:check",
    "quality": "npm run lint && npm run format:check",
    "quality:fix": "npm run lint:fix && npm run format",
    "clean": "rimraf target/classes/META-INF/resources target/dist"
  }
}
```

### Build Scripts (Optional)
Projects generating minified or bundled assets:

```json
{
  "scripts": {
    "build": "webpack --mode production",
    "build:dev": "webpack --mode development",
    "build:watch": "webpack --mode development --watch"
  }
}
```

## Node.js Version Requirements
* **Minimum**: Node.js 20.12.2 LTS
* **npm**: 10.5.0 or compatible
* **Lock Files**: Always commit `package-lock.json`

## Environment Configuration

### Git Ignore Requirements
```gitignore
# Node.js runtime directories
node_modules/
target/node/

# npm cache and logs
.npm/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Coverage and build outputs
target/coverage/
dist/
build/
```

### Development Environment
* All developers must use the same Node.js and npm versions
* Local development should mirror CI/CD environment
* Environment variables must be documented

## Maven Integration Standards

### Frontend Maven Plugin Configuration
```xml
<plugin>
  <groupId>com.github.eirslett</groupId>
  <artifactId>frontend-maven-plugin</artifactId>
  <version>1.15.1</version>
  <configuration>
    <nodeVersion>v20.12.2</nodeVersion>
    <npmVersion>10.5.0</npmVersion>
    <installDirectory>target</installDirectory>
  </configuration>
  <executions>
    <execution>
      <id>install-node-and-npm</id>
      <goals>
        <goal>install-node-and-npm</goal>
      </goals>
    </execution>
    <execution>
      <id>npm-install</id>
      <goals>
        <goal>npm</goal>
      </goals>
      <configuration>
        <arguments>install</arguments>
      </configuration>
    </execution>
    <execution>
      <id>npm-format-check</id>
      <goals>
        <goal>npm</goal>
      </goals>
      <phase>compile</phase>
      <configuration>
        <arguments>run format:check</arguments>
      </configuration>
    </execution>
    <execution>
      <id>npm-test</id>
      <goals>
        <goal>npm</goal>
      </goals>
      <phase>test</phase>
      <configuration>
        <arguments>run test:ci-strict</arguments>
      </configuration>
    </execution>
    <execution>
      <id>npm-lint-fix</id>
      <goals>
        <goal>npm</goal>
      </goals>
      <phase>verify</phase>
      <configuration>
        <arguments>run lint:fix</arguments>
      </configuration>
    </execution>
  </executions>
</plugin>
```

### Maven Phase Integration
JavaScript tooling integrated into these Maven phases:

* **validate**: Node.js and npm installation
* **compile**: Format checking and dependency installation
* **test**: JavaScript unit tests with coverage
* **verify**: Linting with automatic fixes

### Sonar Integration
```xml
<properties>
  <!-- JavaScript coverage reporting -->
  <sonar.javascript.lcov.reportPaths>target/coverage/lcov.info</sonar.javascript.lcov.reportPaths>
  <sonar.coverage.exclusions>**/*.test.js,**/test/**/*,**/mocks/**/*</sonar.coverage.exclusions>
  <sonar.javascript.file.suffixes>.js</sonar.javascript.file.suffixes>
</properties>
```

## Dependency Management

### Update Process
When adding, removing, or updating dependencies:

1. **Security Assessment First**: Run `npm audit` before changes
2. **Update to Latest Versions**: Use most recent stable versions unless compatibility issues
3. **Check All Warnings**: After `npm install`, review all warning messages
4. **Fix Warnings**: Attempt to resolve through:
   - Updating peer dependencies
   - Adjusting package versions
   - Reviewing deprecation notices
5. **Document Unfixable Warnings**: Any warnings that cannot be resolved must be documented with:
   - The specific warning message
   - Reason why it cannot be fixed
   - Expected resolution timeline

### Version Management
* Always ensure the most recent working versions
* Use exact versions for critical dependencies
* Allow patch-level updates for development tools
* Regular security auditing with `npm audit`
* Document any peer dependency requirements

## Build Environment
* Frontend-maven-plugin ensures consistent Node.js installation
* Build must be reproducible across different machines
* All builds must pass formatting, linting, and testing requirements

## Quality Assurance

### Package.json Validation
Ensure the following elements are present:

- [ ] Required scripts are defined
- [ ] All necessary dependencies are included
- [ ] Version numbers are appropriate
- [ ] Jest configuration is complete (if JavaScript project)
- [ ] Coverage thresholds are set appropriately
- [ ] Build scripts exclude generated files from quality checks

### Dependency Security
* Run `npm audit` regularly
* Update dependencies to latest secure versions
* Document any security exceptions with justification
* Use `npm ci` in CI/CD environments for reproducible builds

## References

* [npm Documentation](https://docs.npmjs.com/)
* [frontend-maven-plugin](https://github.com/eirslett/frontend-maven-plugin)
* [Maven Documentation](https://maven.apache.org/)
