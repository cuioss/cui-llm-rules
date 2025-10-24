# CUI Frontend Development Skill

Frontend development standards for CUI projects including JavaScript, CSS, web components, and testing.

## Overview

The `cui-frontend-development` skill provides comprehensive frontend standards covering:

- **JavaScript Core**: ES2022+ syntax, vanilla JavaScript, module patterns, complexity limits
- **Project Structure**: package.json, Jest configuration, Babel setup, Node.js LTS
- **CSS Development**: Custom properties, Grid/Flexbox, Stylelint, PostCSS, BEM conventions
- **Web Components**: Lit framework, component structure, CSS-in-JS, lifecycle methods
- **JSDoc Standards**: Documentation for public APIs, types, parameters, examples
- **Cypress Testing**: E2E testing, custom commands, data-testid selectors, console monitoring

## When to Use This Skill

Use `cui-frontend-development` when:

- Writing JavaScript code for CUI web applications
- Developing CSS styles and layouts
- Creating Lit-based web components
- Documenting JavaScript APIs with JSDoc
- Writing Cypress E2E tests
- Setting up frontend project structure

## Prerequisites

**Required**:
- Node.js 20.12.2 LTS
- npm (latest version)
- Modern browser for testing

**Optional**:
- Lit framework (for web components)
- Cypress (for E2E testing)
- Jest (for unit testing)

## Standards Included

### 1. JavaScript Core (`javascript-core.md`)

**Always loaded** - Foundation for all JavaScript:

- ES2022+ syntax (const/let, arrow functions, destructuring, async/await)
- Vanilla JavaScript preference (avoid jQuery)
- Module imports/exports (ES6 modules)
- Variable declarations (const preferred, never var)
- Function patterns (arrow vs regular)
- Complexity limits (max 15 cyclomatic, max 20 statements)
- Error handling with try/catch
- Promises and async patterns

### 2. Project Structure (`javascript-project-structure.md`)

**Always loaded** - Project configuration:

- package.json structure and scripts
- Jest configuration and coverage thresholds
- Babel setup for test environment
- ESLint configuration
- Node.js version management (20.12.2 LTS)
- Directory structure conventions
- File naming patterns
- Dependency management

### 3. CSS Development (`css-development.md`)

**Load when**: Working with CSS

- CSS custom properties (variables)
- Modern layout (Grid and Flexbox)
- Stylelint configuration
- PostCSS plugins
- BEM naming conventions
- Responsive design patterns
- Mobile-first approach
- CSS architecture

### 4. Web Components (`web-components.md`)

**Load when**: Working with Lit/Web Components

- Component structure and naming
- Property and state management
- CSS-in-JS patterns with Lit
- Lifecycle methods
- Event handling and dispatching
- Shadow DOM usage
- Component composition
- Accessibility (ARIA)

### 5. JSDoc Standards (`jsdoc-standards.md`)

**Load when**: Writing or reviewing JSDoc

- JSDoc completeness for public APIs
- Parameter and return type documentation
- Example code in documentation
- ESLint JSDoc plugin configuration
- Type annotations
- Custom types definition

### 6. Cypress Testing (`cypress-testing.md`)

**Load when**: Working with E2E tests

- Test organization and naming
- Custom commands usage
- Selector strategy (data-testid preferred)
- Console error monitoring
- Test independence
- Before/after hooks
- Fixtures and test data

## Quick Start

### 1. Modern JavaScript

```javascript
// Use const/let, never var
const API_URL = 'https://api.example.com';
let counter = 0;

// Arrow functions
const fetchUser = async (userId) => {
    try {
        const response = await fetch(`${API_URL}/users/${userId}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Failed to fetch user:', error);
        throw error;
    }
};

// Destructuring
const {name, email} = user;
const [first, second, ...rest] = items;

// Template literals
console.log(`User ${name} has email ${email}`);
```

### 2. Lit Web Component

```javascript
import {LitElement, html, css} from 'lit';

export class UserCard extends LitElement {
    static styles = css`
        :host {
            display: block;
            padding: 1rem;
            border: 1px solid #ccc;
        }

        .user-card__name {
            font-size: 1.5rem;
            font-weight: bold;
        }
    `;

    static properties = {
        userName: {type: String},
        userEmail: {type: String}
    };

    constructor() {
        super();
        this.userName = '';
        this.userEmail = '';
    }

    render() {
        return html`
            <div class="user-card">
                <div class="user-card__name">${this.userName}</div>
                <div class="user-card__email">${this.userEmail}</div>
            </div>
        `;
    }
}

customElements.define('user-card', UserCard);
```

### 3. Modern CSS with Custom Properties

```css
:root {
    --color-primary: #007bff;
    --spacing-unit: 0.5rem;
    --border-radius: 4px;
}

.button {
    background-color: var(--color-primary);
    padding: calc(var(--spacing-unit) * 2);
    border-radius: var(--border-radius);
    display: flex;
    align-items: center;
    gap: var(--spacing-unit);
}

/* Grid layout */
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-unit);
}
```

### 4. JSDoc Documentation

```javascript
/**
 * Validates user credentials and returns authentication token.
 *
 * @param {string} username - The username to authenticate
 * @param {string} password - The user password
 * @returns {Promise<{token: string, expiresAt: number}>} Authentication token with expiration
 * @throws {AuthenticationError} If credentials are invalid
 * @example
 * const auth = await authenticateUser('john', 'secret123');
 * console.log('Token:', auth.token);
 */
async function authenticateUser(username, password) {
    // Implementation
}
```

### 5. Cypress E2E Test

```javascript
describe('User Login', () => {
    beforeEach(() => {
        cy.visit('/login');
    });

    it('should login successfully with valid credentials', () => {
        // Use data-testid selectors
        cy.get('[data-testid="username-input"]').type('john@example.com');
        cy.get('[data-testid="password-input"]').type('password123');
        cy.get('[data-testid="login-button"]').click();

        // Verify redirect
        cy.url().should('include', '/dashboard');
        cy.get('[data-testid="welcome-message"]')
            .should('contain', 'Welcome');
    });

    it('should display error with invalid credentials', () => {
        cy.get('[data-testid="username-input"]').type('invalid@example.com');
        cy.get('[data-testid="password-input"]').type('wrongpass');
        cy.get('[data-testid="login-button"]').click();

        cy.get('[data-testid="error-message"]')
            .should('be.visible')
            .and('contain', 'Invalid credentials');
    });
});
```

## Integration with Other Skills

**Recommended skill combinations**:

```yaml
# Complete web application
skills:
  - cui-frontend-development  # Frontend standards (this skill)
  - cui-java-core             # Backend Java development
  - cui-documentation         # README and docs

# Frontend-only project
skills:
  - cui-frontend-development  # All frontend standards
  - cui-project-setup         # Project initialization
```

## Common Development Tasks

### Create New Web Component

1. Define component class extending LitElement
2. Add static styles with CSS-in-JS
3. Define properties with decorators
4. Implement render() method
5. Register with customElements.define()
6. Add JSDoc documentation
7. Write Cypress tests

### Style with Modern CSS

1. Use CSS custom properties for theming
2. Apply Grid or Flexbox for layout
3. Follow BEM naming conventions
4. Ensure mobile-first responsive design
5. Run Stylelint: `npm run lint:css`
6. Verify in multiple browsers

### Write JavaScript Module

1. Use ES2022+ syntax
2. Export functions/classes as modules
3. Add JSDoc documentation
4. Keep complexity low (max 15 cyclomatic)
5. Write Jest unit tests
6. Run ESLint: `npm run lint`

### Add E2E Test

1. Create test file in cypress/e2e/
2. Use data-testid for selectors
3. Test user workflows end-to-end
4. Verify console errors
5. Ensure test independence
6. Run: `npm run cypress:run`

## Prohibited Practices

**DO NOT**:
- Use `var` for variables (use const/let)
- Use jQuery (use vanilla JavaScript)
- Skip JSDoc for public APIs
- Use ID or class selectors in Cypress (use data-testid)
- Exceed complexity limits (15 cyclomatic, 20 statements)
- Inline styles (use CSS-in-JS or external CSS)
- Mix concerns in components

## Verification Checklist

After applying this skill:

**JavaScript**:
- [ ] ES2022+ syntax used throughout
- [ ] No var declarations (const/let only)
- [ ] Complexity limits respected
- [ ] Error handling present
- [ ] Modules properly imported/exported

**Project Structure**:
- [ ] package.json configured
- [ ] Jest tests configured
- [ ] ESLint passing: `npm run lint`
- [ ] Tests passing: `npm test`

**CSS** (if applicable):
- [ ] Custom properties used
- [ ] Modern layout (Grid/Flexbox)
- [ ] BEM naming followed
- [ ] Stylelint passing: `npm run lint:css`
- [ ] Responsive design verified

**Web Components** (if applicable):
- [ ] Lit patterns followed
- [ ] Properties defined correctly
- [ ] CSS-in-JS used
- [ ] Events dispatched properly
- [ ] Accessibility considered

**Documentation**:
- [ ] JSDoc complete for public APIs
- [ ] Examples provided
- [ ] Types documented

**E2E Tests** (if applicable):
- [ ] data-testid selectors used
- [ ] Tests independent
- [ ] Console errors monitored
- [ ] Cypress tests passing: `npm run cypress:run`

## Quality Standards

This skill enforces:

- **Modern JavaScript**: ES2022+ syntax only
- **Vanilla preference**: Avoid heavyweight frameworks
- **Code quality**: Complexity and statement limits
- **Documentation**: Complete JSDoc for APIs
- **Testing**: Comprehensive E2E coverage
- **Maintainability**: Clear structure and organization

## Examples

See standards files for comprehensive examples including:

- Modern JavaScript patterns
- Lit web component structures
- CSS Grid and Flexbox layouts
- JSDoc templates
- Cypress test patterns
- Project configuration files

## Support

For issues or questions:

1. Review detailed standards in `standards/` directory
2. Check Node.js version (20.12.2 LTS required)
3. Verify package.json configuration
4. Run linters and fix issues
5. Consult Lit and Cypress documentation

## License

Part of the CUI LLM Rules documentation system for CUI OSS projects.
