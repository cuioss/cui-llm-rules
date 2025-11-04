# ESLint Build Integration

## Purpose

This document defines integration requirements for ESLint in build pipelines, CI/CD processes, Maven configuration, and development workflows for consistent code quality enforcement across CUI projects.

## NPM Scripts Integration

### Required Package.json Scripts

All projects must include these essential linting scripts:

```json
{
  "scripts": {
    "lint:js": "eslint src/**/*.js",
    "lint:js:fix": "eslint --fix src/**/*.js",
    "lint": "npm run lint:js",
    "lint:fix": "npm run lint:js:fix"
  }
}
```

### With StyleLint Integration

For projects using CSS-in-JS (Lit components):

```json
{
  "scripts": {
    "lint:js": "eslint src/**/*.js",
    "lint:js:fix": "eslint --fix src/**/*.js",
    "lint:style": "stylelint src/**/*.js",
    "lint:style:fix": "stylelint --fix src/**/*.js",
    "lint": "npm run lint:js && npm run lint:style",
    "lint:fix": "npm run lint:js:fix && npm run lint:style:fix"
  }
}
```

### Additional Useful Scripts

Recommended additional linting scripts:

```json
{
  "scripts": {
    "lint:check": "npm run lint",
    "lint:report": "eslint src/**/*.js --format html --output-file target/eslint-report.html",
    "lint:ci": "eslint src/**/*.js --max-warnings 0",
    "validate": "npm run lint && npm run format:check"
  }
}
```

## Maven Integration

### Frontend Maven Plugin Configuration

Integrate ESLint into Maven build process using frontend-maven-plugin:

```xml
<plugin>
  <groupId>com.github.eirslett</groupId>
  <artifactId>frontend-maven-plugin</artifactId>
  <version>${frontend-maven-plugin.version}</version>
  <executions>
    <!-- Install Node and npm -->
    <execution>
      <id>install-node-and-npm</id>
      <goals>
        <goal>install-node-and-npm</goal>
      </goals>
      <phase>initialize</phase>
    </execution>

    <!-- Install npm dependencies -->
    <execution>
      <id>npm-install</id>
      <goals>
        <goal>npm</goal>
      </goals>
      <phase>initialize</phase>
      <configuration>
        <arguments>install</arguments>
      </configuration>
    </execution>

    <!-- Run ESLint with auto-fix -->
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

### Build Phase Selection

**initialize phase**: Install Node.js, npm, and dependencies

**verify phase**: Run linting with auto-fix (recommended)
- Occurs after test phase
- Allows automatic fixing of linting issues
- Non-breaking for development workflow

**validate phase**: Run linting without auto-fix (not recommended)
- Occurs before compilation
- Breaks build on linting errors
- Can be disruptive to development workflow

### Maven Build Lifecycle

Typical build lifecycle with linting:

1. **initialize**: Install Node.js and npm
2. **generate-resources**: Copy frontend resources
3. **compile**: Compile Java code
4. **test**: Run tests
5. **verify**: Run lint:fix to automatically fix and validate JavaScript
6. **package**: Package application

## CI/CD Integration

### Continuous Integration Requirements

Linting must be integrated into CI/CD pipeline:

```yaml
# GitHub Actions example
name: CI

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - run: npm run lint:check
```

### Quality Gates

Establish quality gates for successful builds:

1. **No ESLint errors**: All error-level violations must be fixed
2. **Minimize warnings**: Address warnings or document exceptions
3. **Security rules pass**: All security rules must pass
4. **Complexity thresholds**: Functions meet complexity limits

### Pre-commit Hooks

Recommended pre-commit hook setup using Husky:

```json
{
  "devDependencies": {
    "husky": "^8.0.0",
    "lint-staged": "^13.0.0"
  },
  "lint-staged": {
    "*.js": [
      "eslint --fix",
      "prettier --write"
    ]
  }
}
```

```bash
# .husky/pre-commit
npm run lint:fix
```

## Error Handling Standards

### Severity Level Guidelines

**Error Severity**: Build-breaking issues that must be fixed
- Security vulnerabilities
- Syntax errors
- Clear standards violations
- Critical code quality issues

**Warning Severity**: Issues that should be addressed
- Complexity warnings
- Documentation gaps
- Performance concerns
- Maintainability issues

**Off Severity**: Explicitly disabled rules
- Conflicts with other tools (Prettier)
- Framework-specific exceptions
- Test environment relaxations

### Common Fix Strategies

**Automatic Fixes**:
```bash
# Fix all auto-fixable issues
npm run lint:fix

# Fix specific file
npx eslint --fix src/main/resources/components/example.js

# Fix and report
npm run lint:fix && npm run lint:check
```

**Manual Review**:
- Complex rule violations requiring code refactoring
- Security issues requiring architectural changes
- Complexity reductions requiring function extraction
- Documentation requirements needing human input

### Error Reporting

Generate detailed error reports:

```bash
# HTML report for review
npm run lint:report

# JSON report for tooling
npx eslint src/**/*.js --format json --output-file target/eslint-report.json

# Console output with colors
npm run lint:js
```

## Performance Optimization

### Caching

Enable ESLint caching for faster subsequent runs:

```json
{
  "scripts": {
    "lint:js": "eslint --cache src/**/*.js",
    "lint:js:fix": "eslint --cache --fix src/**/*.js"
  }
}
```

Add cache file to .gitignore:

```
# .gitignore
.eslintcache
```

### Parallel Execution

For large codebases, consider parallel execution:

```json
{
  "scripts": {
    "lint:parallel": "npm-run-all --parallel lint:js lint:style"
  },
  "devDependencies": {
    "npm-run-all": "^4.1.5"
  }
}
```

### Incremental Linting

Lint only changed files in CI:

```bash
# Git-based incremental linting
git diff --name-only --diff-filter=ACM origin/main | grep '.js$' | xargs eslint --fix
```

### File Exclusions

Exclude unnecessary files from linting:

```javascript
// eslint.config.js
export default [
  {
    ignores: [
      '**/node_modules/**',
      '**/target/**',
      '**/dist/**',
      '**/*.min.js',
      '**/vendor/**'
    ]
  },
  // ... configuration
];
```

## Development Workflow Integration

### IDE Integration

**Visual Studio Code**: Install ESLint extension
```json
// .vscode/settings.json
{
  "eslint.validate": ["javascript"],
  "eslint.format.enable": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

**IntelliJ IDEA**: Enable ESLint in settings
- Preferences → Languages & Frameworks → JavaScript → Code Quality Tools → ESLint
- Check "Automatic ESLint configuration"
- Check "Run eslint --fix on save"

### Watch Mode

Run linting in watch mode during development:

```json
{
  "scripts": {
    "lint:watch": "nodemon --watch src --ext js --exec npm run lint:fix"
  },
  "devDependencies": {
    "nodemon": "^2.0.20"
  }
}
```

### Editor Configuration

Consistent editor settings across team:

```
# .editorconfig
root = true

[*.js]
indent_style = space
indent_size = 2
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true
```

## Troubleshooting

### Common Build Issues

**Issue: "Cannot find module 'eslint'"**

Cause: ESLint not installed or npm install not run

Solution:
```bash
npm install
# or
mvn clean install
```

**Issue: "Parsing error: Cannot use import statement outside a module"**

Cause: Missing `"type": "module"` in package.json

Solution:
```json
{
  "type": "module"
}
```

**Issue: "Configuration file not found"**

Cause: Missing eslint.config.js or wrong filename

Solution:
- Ensure file is named `eslint.config.js` (not .eslintrc.js)
- File must be in project root directory

**Issue: "Plugin not found"**

Cause: Plugin not installed or incorrect import

Solution:
```bash
npm install --save-dev eslint-plugin-jsdoc
```
```javascript
import jsdoc from 'eslint-plugin-jsdoc';
```

**Issue: "Maximum call stack size exceeded"**

Cause: Circular dependency in ESLint configuration or project files

Solution:
- Check for circular imports in JavaScript files
- Verify ESLint configuration doesn't have circular extends
- Use `--debug` flag to identify circular dependency

### Maven Build Issues

**Issue: Maven build fails with linting errors**

Cause: ESLint errors blocking build in verify phase

Solution:
- Run `npm run lint:fix` locally to fix issues
- Commit fixed files
- Alternatively, temporarily disable lint in Maven for urgent fixes (not recommended)

**Issue: Maven doesn't find npm scripts**

Cause: package.json scripts not defined or npm not installed

Solution:
- Verify scripts exist in package.json
- Ensure frontend-maven-plugin install-node-and-npm executed
- Check Maven execution order in pom.xml

**Issue: Linting takes too long in Maven build**

Cause: Large number of files or no caching

Solution:
- Enable ESLint caching in npm scripts
- Exclude unnecessary directories (node_modules, target)
- Consider incremental linting in CI

## Best Practices

1. **Run lint:fix in verify phase** - Automatic fixing during build
2. **Enable caching** - Faster subsequent lint runs
3. **Integrate with CI/CD** - Enforce quality gates
4. **Use pre-commit hooks** - Catch issues before commit
5. **Configure IDE integration** - Real-time feedback during development
6. **Generate reports** - Track linting metrics over time
7. **Exclude build artifacts** - Don't lint generated or vendored files
8. **Document exceptions** - Comment any unusual configuration
9. **Run incrementally in CI** - Lint only changed files
10. **Monitor performance** - Optimize linting for large codebases

## Integration Checklist

- [ ] ESLint v9 installed with all required plugins
- [ ] package.json includes lint:js and lint:fix scripts
- [ ] Maven pom.xml includes frontend-maven-plugin configuration
- [ ] Lint execution configured in verify phase
- [ ] .eslintcache added to .gitignore
- [ ] IDE ESLint extension installed and configured
- [ ] Pre-commit hooks configured (optional but recommended)
- [ ] CI/CD pipeline includes linting step
- [ ] Quality gates defined and enforced
- [ ] Documentation updated with linting procedures
