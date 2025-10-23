---
name: cui-frontend-development
description: Frontend development standards for CUI projects including JavaScript, CSS, web components, JSDoc, and Cypress testing
tools: [Read, Edit, Write, Bash, Grep, Glob]
---

# CUI Frontend Development Skill

Standards and patterns for frontend development in CUI projects. This skill provides comprehensive guidance on JavaScript, CSS, web components, project structure, documentation, and end-to-end testing.

## Workflow

### Step 1: Load Applicable Frontend Standards

**CRITICAL**: Load current frontend standards to use as enforcement criteria.

1. **Always load foundational standards**:
   ```
   Read: standards/javascript-core.md
   Read: standards/javascript-project-structure.md
   ```
   These provide core JavaScript patterns and project configuration always needed for development.

2. **Conditional loading based on context**:

   - If working with CSS:
     ```
     Read: standards/css-development.md
     ```

   - If working with Lit/Web Components:
     ```
     Read: standards/web-components.md
     ```

   - If writing or reviewing JSDoc documentation:
     ```
     Read: standards/jsdoc-standards.md
     ```

   - If working with Cypress E2E tests:
     ```
     Read: standards/cypress-testing.md
     ```

3. **Extract key requirements from all loaded standards**

4. **Store in working memory** for use during task execution

### Step 2: Analyze Existing Frontend Code

**When to Execute**: After loading standards

**What to Analyze**:

1. **JavaScript Code Patterns**:
   - Verify ES2022+ syntax usage
   - Check vanilla JavaScript preference (avoid jQuery)
   - Validate module imports and exports
   - Review variable declarations (const/let, never var)
   - Check function patterns (arrow vs regular functions)
   - Verify complexity limits (max 15 cyclomatic, max 20 statements)

2. **Project Structure**:
   - Review package.json scripts and dependencies
   - Verify Jest configuration and coverage thresholds
   - Check Babel setup for test environment
   - Validate Node.js version (20.12.2 LTS)
   - Review directory structure and file naming

3. **CSS Patterns** (if CSS context):
   - Check for CSS custom properties usage
   - Verify modern layout techniques (Grid/Flexbox)
   - Review Stylelint and PostCSS configuration
   - Check BEM naming conventions
   - Validate responsive design patterns

4. **Web Components** (if Lit context):
   - Review component structure and naming
   - Check property and state management
   - Verify CSS-in-JS patterns
   - Validate lifecycle method usage
   - Review event handling patterns

5. **Documentation** (if JSDoc context):
   - Check JSDoc completeness for public APIs
   - Verify parameter and return type documentation
   - Review example code in documentation
   - Validate ESLint JSDoc plugin configuration

6. **E2E Tests** (if Cypress context):
   - Review test organization and naming
   - Check custom commands usage
   - Verify selector strategy (data-testid preferred)
   - Review console error monitoring
   - Validate test independence

### Step 3: Apply Frontend Standards to Development Task

**When to Execute**: During implementation or code review

**What to Apply**:

1. **JavaScript Core Standards**:
   - Use ES modules with named exports
   - Apply const by default, let for reassignment
   - Use arrow functions for utilities, regular for methods
   - Implement proper destructuring patterns
   - Apply function complexity limits
   - Let async errors bubble naturally

2. **Project Configuration**:
   - Ensure package.json has required scripts
   - Configure Jest with proper coverage thresholds (80%)
   - Set up Babel for test environment
   - Include all necessary dependencies
   - Configure Maven integration properly

3. **CSS Standards** (if CSS context):
   - Use CSS custom properties for design tokens
   - Implement modern layout patterns
   - Configure PostCSS with required plugins
   - Set up Stylelint with proper rules
   - Apply BEM naming convention

4. **Web Component Standards** (if Lit context):
   - Follow component structure order
   - Use static properties for reactive properties
   - Implement CSS-in-JS with css tagged templates
   - Apply proper lifecycle methods
   - Use event dispatching patterns

5. **JSDoc Standards** (if documentation context):
   - Document all public functions and classes
   - Include @param, @returns, @throws tags
   - Provide @example for public APIs
   - Use proper type annotations
   - Configure ESLint JSDoc plugin

6. **Cypress Standards** (if E2E testing context):
   - Organize tests by feature in directories
   - Use custom commands for common operations
   - Implement console error monitoring
   - Apply proper selector strategy
   - Configure appropriate complexity limits

### Step 4: Verify Implementation Quality

**When to Execute**: After applying standards

**Quality Checks**:

1. **JavaScript Verification**:
   - [ ] ES2022+ features used appropriately
   - [ ] Vanilla JavaScript preferred over libraries
   - [ ] Const/let used correctly, no var
   - [ ] Function complexity within limits
   - [ ] Proper async error handling
   - [ ] All imports use ES module syntax

2. **Project Configuration Verification**:
   - [ ] package.json has all required scripts
   - [ ] Jest configured with 80% coverage thresholds
   - [ ] All dependencies at latest secure versions
   - [ ] package-lock.json committed
   - [ ] Maven integration configured

3. **CSS Verification** (if CSS context):
   - [ ] CSS custom properties used
   - [ ] Modern layout techniques applied
   - [ ] Stylelint passes without errors
   - [ ] Proper naming convention followed
   - [ ] Responsive design implemented

4. **Web Component Verification** (if Lit context):
   - [ ] Component structure follows standards
   - [ ] Properties properly declared
   - [ ] CSS-in-JS correctly implemented
   - [ ] Lifecycle methods used appropriately
   - [ ] Events dispatched correctly

5. **JSDoc Verification** (if documentation context):
   - [ ] All public APIs documented
   - [ ] Required tags present
   - [ ] Examples provided
   - [ ] Types properly annotated
   - [ ] ESLint JSDoc rules pass

6. **Cypress Verification** (if E2E testing context):
   - [ ] Tests organized properly
   - [ ] Custom commands used
   - [ ] Console errors monitored
   - [ ] Proper selectors used
   - [ ] Tests are independent

7. **Build and Test**:
   ```bash
   # Install dependencies
   npm install

   # Format code
   npm run format

   # Fix linting issues
   npm run lint:fix

   # Run tests
   npm run test

   # Quality verification
   npm run quality

   # Maven build (if Maven project)
   ./mvnw clean install
   ```

8. **Security Verification**:
   ```bash
   # Check for vulnerabilities
   npm audit

   # Fix vulnerabilities
   npm audit fix
   ```

### Step 5: Document Changes and Commit

**When to Execute**: After verification passes

**Documentation Updates**:
- Update README if project structure changed
- Document any special configuration requirements
- Note any deviations from standards with rationale
- Update package.json version if appropriate

**Commit Standards**:
- Follow standard commit message format
- Reference related issues or tasks
- Include test results if applicable
- Add co-authored-by line for Claude Code

## Common Frontend Patterns

### Modern JavaScript Pattern
```javascript
// ES modules with named exports
export const fetchUserData = async (userId) => {
  const response = await fetch(`/api/users/${userId}`);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }

  return await response.json();
};

// Destructuring and modern syntax
const { name, email, preferences = {} } = user;
const [first, second, ...rest] = items;
```

### CSS Custom Properties Pattern
```css
:root {
  --color-primary: #007bff;
  --spacing-md: 1rem;
  --border-radius: 0.25rem;
}

.component {
  padding: var(--spacing-md);
  background-color: var(--color-primary);
  border-radius: var(--border-radius);
}
```

### Lit Component Pattern
```javascript
export class QwcUserProfile extends LitElement {
  static styles = css`
    :host { display: block; }
  `;

  static properties = {
    userId: { type: String },
    _userData: { state: true },
  };

  constructor() {
    super();
    this.userId = '';
    this._userData = null;
  }

  async connectedCallback() {
    super.connectedCallback();
    await this._loadUserData();
  }

  render() {
    return html`
      <div class="profile">
        ${this._renderUserInfo()}
      </div>
    `;
  }
}

customElements.define('qwc-user-profile', QwcUserProfile);
```

## Error Prevention

### Common JavaScript Issues

1. **UndefinedBehavior**: Using var instead of const/let
2. **ComplexityExceeded**: Functions exceeding 15 cyclomatic complexity
3. **MissingErrorHandling**: Async functions without error handling
4. **DeprecatedSyntax**: Using jQuery/legacy libraries instead of vanilla JavaScript

### Common Configuration Issues

1. **MissingCoverage**: Jest not configured or coverage < 80%
2. **SecurityVulnerabilities**: Outdated dependencies with known issues
3. **MissingBabel**: Tests failing without Babel configuration
4. **WrongNodeVersion**: Using Node.js version other than 20.12.2 LTS

### Common CSS Issues

1. **HighSpecificity**: Using IDs or !important unnecessarily
2. **DeepNesting**: CSS nesting exceeding 3 levels
3. **MissingVariables**: Hardcoded values instead of custom properties
4. **LegacyLayout**: Using floats instead of Grid/Flexbox

### Common Lit Issues

1. **IncorrectStructure**: Component structure not following standards
2. **MissingProperties**: Properties not declared in static properties
3. **WrongLifecycle**: Incorrect lifecycle method usage
4. **ImproperStyling**: Not using css tagged templates for styles

## Quality Verification

All changes must pass:
- [x] ES2022+ JavaScript syntax
- [x] Vanilla JavaScript preference
- [x] Const/let, no var
- [x] Function complexity limits
- [x] Jest tests with 80% coverage
- [x] ESLint passes
- [x] Prettier formatting
- [x] npm audit clean
- [x] Context-specific standards (CSS/Lit/JSDoc/Cypress)

## References

* ECMAScript Specification: https://tc39.es/ecma262/
* MDN JavaScript Guide: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide
* Jest Testing Framework: https://jestjs.io/
* Lit Framework: https://lit.dev/
* PostCSS: https://postcss.org/
* Cypress: https://docs.cypress.io/
* JSDoc: https://jsdoc.app/
