# Cypress E2E Testing Standards

## Purpose
Comprehensive standards for Cypress End-to-End (E2E) testing that extend the base CUI JavaScript standards with framework-specific adaptations for test automation scenarios.

## Framework-Specific Adaptations

### Code Complexity Accommodations
Cypress E2E tests require different complexity thresholds due to the nature of end-to-end test scenarios.

#### Function Length Limits
```javascript
"max-lines-per-function": ["error", {
  "max": 200,           // Increased from 50 for test scenarios
  "skipBlankLines": true,
  "skipComments": true
}]
```

#### Cyclomatic Complexity
```javascript
"complexity": ["error", {
  "max": 25  // Increased from 10 for complex test scenarios
}]
```

### ESLint Configuration for Cypress

```javascript
// eslint.config.js - Cypress-specific configuration
export default [
  {
    files: ["cypress/**/*.js"],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
        cy: "readonly",
        Cypress: "readonly"
      }
    },
    plugins: {
      cypress,
      jsdoc,
      sonarjs,
      security,
      unicorn
    },
    rules: {
      // Cypress-specific rules
      "cypress/no-unnecessary-waiting": "warn",
      "cypress/unsafe-to-chain-command": "off",
      "cypress/no-assigning-return-values": "error",

      // Adapted complexity rules
      "max-lines-per-function": ["error", { "max": 200 }],
      "complexity": ["error", { "max": 25 }],

      // JSDoc requirements
      "jsdoc/require-description": "error",
      "jsdoc/require-param-description": "error",
      "jsdoc/require-returns-description": "error"
    }
  }
];
```

## Console Error Management

### Zero-Error Policy
Cypress tests must actively monitor and validate browser console output to maintain application quality.

### Allowed Warnings System
Implement a centralized system for managing acceptable console warnings from third-party libraries:

```javascript
// cypress/support/console-monitoring.js
const allowedWarnings = [
  'DevTools failed to load source map',
  'Synchronous XMLHttpRequest on the main thread is deprecated'
];

Cypress.on('window:before:load', (win) => {
  win.consoleErrors = [];
  win.consoleWarnings = [];

  // Override console methods to track messages
  const originalError = win.console.error;
  win.console.error = (...args) => {
    originalError(...args);
    win.consoleErrors.push(args.join(' '));
  };

  const originalWarn = win.console.warn;
  win.console.warn = (...args) => {
    originalWarn(...args);
    const message = args.join(' ');
    if (!allowedWarnings.some(allowed => message.includes(allowed))) {
      win.consoleWarnings.push(message);
    }
  };
});
```

## Constants Organization

### Centralized Test Constants
Organize test data and selectors in a hierarchical structure:

```javascript
// cypress/constants/test-constants.js
export const TestConstants = {
  SELECTORS: {
    LOGIN: {
      USERNAME_INPUT: '[data-testid="username-input"]',
      PASSWORD_INPUT: '[data-testid="password-input"]',
      SUBMIT_BUTTON: '[data-testid="login-submit"]'
    },
    NAVIGATION: {
      MENU_TOGGLE: '[data-testid="menu-toggle"]',
      USER_MENU: '[data-testid="user-menu"]'
    }
  },
  TIMEOUTS: {
    DEFAULT: 10000,
    API_CALL: 30000,
    PAGE_LOAD: 15000
  },
  TEST_DATA: {
    VALID_USER: {
      username: 'testuser',
      password: 'testpass'
    }
  }
};
```

## Test Organization Standards

### File Structure
```
cypress/
├── e2e/
│   ├── auth/
│   │   ├── login.cy.js
│   │   └── logout.cy.js
│   ├── dashboard/
│   │   └── dashboard.cy.js
│   └── admin/
│       └── user-management.cy.js
├── support/
│   ├── commands.js
│   ├── e2e.js
│   └── console-monitoring.js
├── fixtures/
│   ├── users.json
│   └── config.json
└── constants/
    └── test-constants.js
```

### Test File Naming
* **Test files**: `feature-name.cy.js`
* **Test suites**: Group related tests in directories
* **Helper files**: Descriptive names without `.cy.js` suffix

## Custom Commands

### Defining Custom Commands
```javascript
// cypress/support/commands.js

/**
 * Custom command to log in a user.
 *
 * @param {string} username - Username for login
 * @param {string} password - Password for login
 * @example
 * cy.login('testuser', 'testpass');
 */
Cypress.Commands.add('login', (username, password) => {
  cy.visit('/login');
  cy.get(TestConstants.SELECTORS.LOGIN.USERNAME_INPUT).type(username);
  cy.get(TestConstants.SELECTORS.LOGIN.PASSWORD_INPUT).type(password);
  cy.get(TestConstants.SELECTORS.LOGIN.SUBMIT_BUTTON).click();
  cy.url().should('not.include', '/login');
});

/**
 * Custom command to check for console errors.
 *
 * @example
 * cy.checkConsoleErrors();
 */
Cypress.Commands.add('checkConsoleErrors', () => {
  cy.window().then((win) => {
    expect(win.consoleErrors || []).to.be.empty;
  });
});
```

## Test Writing Standards

### Test Structure
```javascript
describe('User Authentication', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  it('should successfully log in with valid credentials', () => {
    // Arrange
    const { username, password } = TestConstants.TEST_DATA.VALID_USER;

    // Act
    cy.get(TestConstants.SELECTORS.LOGIN.USERNAME_INPUT).type(username);
    cy.get(TestConstants.SELECTORS.LOGIN.PASSWORD_INPUT).type(password);
    cy.get(TestConstants.SELECTORS.LOGIN.SUBMIT_BUTTON).click();

    // Assert
    cy.url().should('include', '/dashboard');
    cy.get('[data-testid="user-menu"]').should('be.visible');
    cy.checkConsoleErrors();
  });

  it('should show error message with invalid credentials', () => {
    // Arrange
    const invalidCredentials = { username: 'invalid', password: 'wrong' };

    // Act
    cy.get(TestConstants.SELECTORS.LOGIN.USERNAME_INPUT).type(invalidCredentials.username);
    cy.get(TestConstants.SELECTORS.LOGIN.PASSWORD_INPUT).type(invalidCredentials.password);
    cy.get(TestConstants.SELECTORS.LOGIN.SUBMIT_BUTTON).click();

    // Assert
    cy.get('[data-testid="error-message"]').should('be.visible');
    cy.url().should('include', '/login');
  });
});
```

### Async Operations
```javascript
it('should load user data after login', () => {
  cy.login('testuser', 'testpass');

  // Wait for API call to complete
  cy.intercept('GET', '/api/user/profile').as('getUserProfile');
  cy.wait('@getUserProfile');

  // Verify data is loaded
  cy.get('[data-testid="user-name"]').should('not.be.empty');
  cy.get('[data-testid="user-email"]').should('contain', '@');
});
```

### Network Stubbing
```javascript
it('should handle API errors gracefully', () => {
  // Stub API to return error
  cy.intercept('GET', '/api/user/profile', {
    statusCode: 500,
    body: { error: 'Internal Server Error' }
  }).as('getUserProfileError');

  cy.login('testuser', 'testpass');
  cy.wait('@getUserProfileError');

  // Verify error handling
  cy.get('[data-testid="error-banner"]')
    .should('be.visible')
    .and('contain', 'Failed to load user profile');
});
```

## Best Practices

### Selector Strategy
* **Prefer**: `data-testid` attributes for test selectors
* **Avoid**: Class names, IDs, or element types
* **Example**: `[data-testid="submit-button"]` instead of `.btn-primary`

### Wait Strategies
* Use `cy.intercept()` and `cy.wait()` for API calls
* Use `.should()` assertions for element state
* Avoid `cy.wait(timeout)` with arbitrary timeouts
* Set appropriate timeouts in TestConstants

### Test Independence
* Each test should be independent
* Use `beforeEach()` for common setup
* Clean up state in `afterEach()` if needed
* Don't rely on test execution order

### Error Handling
* Always check for console errors at end of tests
* Use `cy.checkConsoleErrors()` custom command
* Verify error states and messages
* Test both success and failure scenarios

## Configuration

### Cypress Configuration
```javascript
// cypress.config.js
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:8080',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 30000,
    responseTimeout: 30000,
    setupNodeEvents(on, config) {
      // Implement node event listeners here
    },
  },
});
```

### Environment Variables
```javascript
// cypress.env.json
{
  "apiUrl": "http://localhost:8080/api",
  "testUser": {
    "username": "testuser",
    "password": "testpass"
  }
}
```

## Continuous Integration

### CI Script Configuration
```json
{
  "scripts": {
    "cypress:run": "cypress run",
    "cypress:open": "cypress open",
    "cypress:ci": "cypress run --browser chrome --headless"
  }
}
```

### CI/CD Integration
```bash
# Run Cypress tests in CI
npm run cypress:ci
```

## References

* [Cypress Documentation](https://docs.cypress.io/)
* [Cypress Best Practices](https://docs.cypress.io/guides/references/best-practices)
* [Testing Library Principles](https://testing-library.com/docs/guiding-principles/)
