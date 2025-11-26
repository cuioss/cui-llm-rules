# npm Build Execution Standards

Standards for executing npm/npx builds in CUI JavaScript projects.

## Command Construction

### npm vs npx Detection

Commands are automatically routed to either `npm` or `npx` based on the command:

**npx commands** (tools that should use npx):
- `playwright` - Playwright test runner
- `eslint` - ESLint linter
- `prettier` - Prettier formatter
- `stylelint` - StyleLint CSS linter
- `tsc` - TypeScript compiler
- `jest` - Jest test runner (when invoked directly)
- `vitest` - Vitest test runner (when invoked directly)

**npm commands** (npm scripts):
- `run <script>` - Execute package.json script
- `test` - Run test script
- `install` - Install dependencies
- `build` - Build production bundle
- Any other npm commands

**Examples:**
```bash
# These use npx automatically
playwright test
eslint src/
prettier --check src/

# These use npm
run test
run build
test
install
```

### Workspace Targeting

For monorepo projects with npm workspaces:

**Detection:**
1. Read root `package.json`
2. Check for `workspaces` array
3. Validate workspace name exists

**Usage:**
```bash
# Single workspace build
npm run test --workspace=e-2-e-playwright

# Multiple workspaces
npm run test --workspace=pkg1 --workspace=pkg2
```

**Workspace flag:**
- Only applies to `npm` commands (not `npx`)
- Must match workspace name in package.json
- Can be directory path or package name

### Environment Variables

Common environment variables for builds:

| Variable | Purpose | Example |
|----------|---------|---------|
| `NODE_ENV` | Execution environment | `NODE_ENV=test` |
| `CI` | CI/CD environment flag | `CI=true` |
| `PLAYWRIGHT_BASE_URL` | Playwright base URL | `PLAYWRIGHT_BASE_URL=http://localhost:3000` |
| `COVERAGE` | Enable coverage | `COVERAGE=true` |

**Usage:**
```bash
NODE_ENV=test CI=true npm run test
```

## Build Execution

### Log File Management

**Log file naming:**
```
target/npm-output-{YYYY-MM-DD-HHmmss}.log
```

**Pre-creation:**
- Create `target/` directory if not exists
- Create log file before execution
- Handles `clean` commands correctly

**Output capture:**
```bash
npm run test > target/npm-output-2025-11-26-143022.log 2>&1
```

**Benefits:**
- Timestamped for historical tracking
- Consistent with Maven structure (target/)
- All output (stdout + stderr) captured

### Timeout Management

**Default timeouts:**
- Standard builds: 120000ms (2 minutes)
- E2E/Playwright tests: 180000ms (3 minutes)
- Lint/format: 60000ms (1 minute)

**Timeout behavior:**
- Commands exceeding timeout return exit code 124
- Log file contains partial output up to timeout
- Build marked as FAILURE

**Custom timeouts:**
```bash
python3 execute-npm-build.py --command "run test:e2e" --timeout 300000
```

### Exit Code Interpretation

**Exit codes:**
- `0` - Success
- `1` - General failure (test failures, lint errors, compilation errors)
- `124` - Timeout
- Other non-zero - Command-specific errors

**Status determination:**
1. Check exit code
2. Parse log file for error patterns
3. Combine both for final status

## Output Parsing

### Error Categorization

**compilation_error:**
- `SyntaxError:`
- `TypeError:`
- `ReferenceError:`
- `error TS\d+:` (TypeScript)

**test_failure:**
- `✘` or `✖` (Jest/Vitest markers)
- `FAIL` messages
- `Expected.*to.*but.*received`
- `\d+ tests? failed`

**lint_error:**
- `eslint` messages
- `stylelint` messages
- `prettier` check failures
- ESLint format: `line:col error message rule-name`

**dependency_error:**
- `Cannot find module`
- `Module not found`
- `npm ERR! 404`
- `ERESOLVE` conflicts

**playwright_error:**
- `playwright` errors
- `page.goto: Timeout`
- `locator.click: Timeout`
- `selector.*not found`

**npm_error:**
- `npm ERR!` messages
- Package installation failures
- Registry errors

### File Location Extraction

**Supported patterns:**

1. **TypeScript/ESLint style:**
   ```
   src/components/Button.js:15:3
   ```

2. **Webpack style:**
   ```
   @ ./src/components/Button.js 15:3
   ```

3. **Jest style:**
   ```
   at Object.<anonymous> (src/utils/helper.js:42:10)
   ```

4. **Playwright style:**
   ```
   tests/login.spec.js:15:5
   ```

**Extracted data:**
- File path (relative to project root)
- Line number (1-indexed)
- Column number (1-indexed)

## Working Directory

### Default Behavior

Commands execute from project root by default.

### Custom Working Directory

For projects with nested frontend directories:

```bash
python3 execute-npm-build.py \
    --command "run test" \
    --working-dir frontend/
```

**Notes:**
- All relative paths resolve from working directory
- Log file still written to `target/` from project root
- Package.json read from working directory

## Best Practices

### Build Command Selection

**Test execution:**
- Use `run test` for package.json test script
- Use `run test:ci` for CI/CD environments
- Use `run test:coverage` for coverage generation

**Linting:**
- Use `run lint` for configured linters
- Use `npx eslint src/` for direct ESLint
- Use `run format:check` for Prettier validation

**Building:**
- Use `run build` for production builds
- Use `run dev` for development builds
- Use `run preview` for build preview

### Workspace Best Practices

**Single workspace:**
```bash
npm run test --workspace=e-2-e-playwright
```

**Multiple workspaces:**
```bash
npm run test --workspaces
```

**Specific script per workspace:**
```bash
npm run test --workspace=pkg1 --workspace=pkg2
```

### Environment Configuration

**Test environment:**
```bash
NODE_ENV=test CI=true npm run test
```

**Production build:**
```bash
NODE_ENV=production npm run build
```

**E2E tests:**
```bash
PLAYWRIGHT_BASE_URL=http://localhost:3000 npm run test:e2e
```

## Integration with Commands

### Command Usage Pattern

```
Skill: cui-frontend-expert:cui-npm-rules
Workflow: Execute npm Build
Parameters:
  command: run test
  workspace: e-2-e-playwright
  output_mode: structured
```

### Build Verification

Commands should verify builds:
1. Execute build via skill
2. Check structured output status
3. Route issues to appropriate fix commands
4. Iterate until clean

### Issue Routing

| Issue Type | Target Command |
|------------|----------------|
| compilation_error | `/js-implement-code` |
| test_failure | `/js-implement-tests` |
| lint_error | `/js-enforce-eslint` |
| dependency_error | Manual fix |
| playwright_error | `/js-implement-tests` |

## Related Standards

- **project-structure.md** - Project directory layouts and package.json
- **dependency-management.md** - npm dependency versioning and security
- **maven-integration.md** - Integration with Maven builds via frontend-maven-plugin
