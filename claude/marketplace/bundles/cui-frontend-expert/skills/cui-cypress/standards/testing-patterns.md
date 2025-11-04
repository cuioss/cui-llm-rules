# Cypress Testing Patterns and Best Practices

Core testing patterns, best practices, and anti-patterns for reliable Cypress E2E tests.

## Core Testing Principles

### No Branching Logic in Tests

**MANDATORY:** Tests must never contain conditional logic that affects test flow or assertions.

**Prohibited:**
- `if/else` statements
- `switch` statements
- Ternary operators (`condition ? true : false`)
- Conditional assertion logic

**Rationale:**
- Tests should have deterministic, predictable paths
- Branching makes test outcomes unpredictable
- Conditional logic masks underlying test issues
- Makes debugging and maintenance difficult

**Examples:**

```javascript
// ❌ BAD - Branching logic in test
it('should handle login state', () => {
  cy.getSessionContext().then((context) => {
    if (context.isLoggedIn) {
      cy.verifyPageType('MAIN_CANVAS');
    } else {
      cy.verifyPageType('LOGIN');
    }
  });
});

// ✅ GOOD - Explicit assertions
it('should show login page when not authenticated', () => {
  cy.clearSession();
  cy.visit('/');

  cy.getSessionContext().then((context) => {
    expect(context.isLoggedIn).to.be.false;
    expect(context.pageType).to.equal('LOGIN');
  });
});

it('should show main canvas when authenticated', () => {
  cy.login('testuser', 'password');

  cy.getSessionContext().then((context) => {
    expect(context.isLoggedIn).to.be.true;
    expect(context.pageType).to.equal('MAIN_CANVAS');
  });
});
```

### Always Be Explicit

**MANDATORY:** Tests must use direct, unambiguous assertions.

**Principles:**
- Assert expected values explicitly
- Assert negative cases explicitly
- No ambiguous conditions
- Clear failure messages

**Examples:**

```javascript
// ❌ BAD - Ambiguous assertion
cy.getPageContext().then((context) => {
  expect(context.pageType).to.not.be.undefined;
});

// ✅ GOOD - Explicit value assertion
cy.getPageContext().then((context) => {
  expect(context.pageType).to.equal('LOGIN');
});

// ❌ BAD - Unclear expectation
cy.get('[data-testid="error"]').should('exist');

// ✅ GOOD - Explicit state verification
cy.get('[data-testid="login-error"]')
  .should('be.visible')
  .and('contain.text', 'Invalid credentials');
```

### Fail Fast Pattern

Tests should fail immediately on first error rather than continuing with invalid state.

**Implementation:**
- Use Cypress's default fail-fast behavior
- Chain assertions logically
- Verify prerequisites before proceeding
- Don't catch errors unless handling is meaningful

**Example:**

```javascript
// ✅ GOOD - Fails fast on any step
it('should complete user registration flow', () => {
  // Step 1: Navigate to registration
  cy.navigateToPage('/register', {
    expectedPageType: 'REGISTRATION',
    waitForReady: true
  });

  // Step 2: Fill form (fails if navigation failed)
  cy.get(TestConstants.SELECTORS.REGISTRATION.EMAIL_INPUT)
    .type('user@example.com');

  // Step 3: Submit (fails if form wasn't filled)
  cy.get(TestConstants.SELECTORS.REGISTRATION.SUBMIT_BUTTON).click();

  // Step 4: Verify success (fails if submission failed)
  cy.verifyPageType('REGISTRATION_SUCCESS');
});
```

## Session Management

### Clean State Guarantee

Use dedicated session management methods for reliable test isolation.

**Custom Commands:**

```javascript
/**
 * Clear all session data for clean test state
 */
Cypress.Commands.add('clearSession', () => {
  cy.clearCookies();
  cy.clearLocalStorage();
  cy.window().then((win) => {
    win.sessionStorage.clear();
  });
});

/**
 * Retrieve and validate existing session
 */
Cypress.Commands.add('retrieveSession', () => {
  cy.getCookies().should('have.length.gt', 0);
  cy.getSessionContext().then((context) => {
    expect(context.isLoggedIn).to.be.true;
  });
});
```

**Usage Patterns:**

```javascript
// For tests requiring clean state
describe('Authentication Tests', () => {
  beforeEach(() => {
    cy.clearSession();
  });

  it('should show login form for unauthenticated user', () => {
    cy.visit('/');
    cy.verifyPageType('LOGIN');
  });
});

// For tests that can reuse sessions
describe('Dashboard Tests', () => {
  before(() => {
    cy.clearSession();
    cy.login('testuser', 'password');
  });

  beforeEach(() => {
    cy.retrieveSession();
    cy.visit('/dashboard');
  });

  it('should display user data', () => {
    cy.get(TestConstants.SELECTORS.DASHBOARD.USER_TABLE)
      .should('be.visible');
  });
});
```

### Session Context Verification

Always verify session context after authentication operations.

**Pattern:**

```javascript
/**
 * Get current session context
 * @returns {Object} Session context with authentication state
 */
Cypress.Commands.add('getSessionContext', () => {
  return cy.window().then((win) => {
    return win.sessionContext || {
      isLoggedIn: false,
      pageType: 'UNKNOWN',
      user: null
    };
  });
});

// Usage
it('should authenticate user successfully', () => {
  cy.login('testuser', 'password');

  cy.getSessionContext().then((context) => {
    expect(context.isLoggedIn).to.be.true;
    expect(context.user).to.not.be.null;
    expect(context.pageType).to.equal('MAIN_CANVAS');
  });
});
```

## Navigation Patterns

### Use Navigation Helpers

**MANDATORY:** Use navigation helpers instead of direct `cy.visit()` or `cy.url()` checks.

**Custom Navigation Command:**

```javascript
/**
 * Navigate to page with comprehensive verification
 * @param {string} path - URL path to navigate to
 * @param {Object} options - Navigation options
 * @param {string} options.expectedPageType - Expected page type after navigation
 * @param {boolean} options.waitForReady - Whether to wait for page ready state
 * @param {number} options.timeout - Custom timeout in milliseconds
 */
Cypress.Commands.add('navigateToPage', (path, options = {}) => {
  const {
    expectedPageType,
    waitForReady = true,
    timeout = TestConstants.TIMEOUTS.PAGE_LOAD
  } = options;

  cy.visit(path, { timeout });

  if (waitForReady) {
    cy.waitForPageReady({ timeout });
  }

  if (expectedPageType) {
    cy.verifyPageType(expectedPageType);
  }
});

/**
 * Wait for page to reach ready state
 * @param {Object} options - Wait options
 * @param {number} options.timeout - Custom timeout
 */
Cypress.Commands.add('waitForPageReady', (options = {}) => {
  const { timeout = TestConstants.TIMEOUTS.PAGE_LOAD } = options;

  cy.window({ timeout }).should((win) => {
    expect(win.document.readyState).to.equal('complete');
  });
});
```

**Usage:**

```javascript
// ✅ GOOD - Using navigation helper
it('should navigate to dashboard', () => {
  cy.navigateToPage('/dashboard', {
    expectedPageType: 'DASHBOARD',
    waitForReady: true,
    timeout: 20000
  });

  cy.get(TestConstants.SELECTORS.DASHBOARD.USER_TABLE)
    .should('be.visible');
});

// ❌ BAD - Direct navigation without verification
it('should navigate to dashboard', () => {
  cy.visit('/dashboard');
  cy.url().should('include', '/dashboard');
  cy.get('[data-testid="user-table"]').should('be.visible');
});
```

### Page Type Verification

Use page type detection for robust navigation verification.

**Implementation:**

```javascript
/**
 * Verify current page type matches expected
 * @param {string} expectedType - Expected page type constant
 */
Cypress.Commands.add('verifyPageType', (expectedType) => {
  cy.getPageContext({ timeout: TestConstants.TIMEOUTS.PAGE_LOAD })
    .then((context) => {
      expect(context.pageType).to.equal(expectedType);
    });
});

/**
 * Get current page context including type and state
 */
Cypress.Commands.add('getPageContext', (options = {}) => {
  const { timeout = TestConstants.TIMEOUTS.DEFAULT } = options;

  return cy.window({ timeout }).then((win) => {
    return win.pageContext || {
      pageType: 'UNKNOWN',
      isReady: false
    };
  });
});
```

**Usage:**

```javascript
it('should redirect to login after logout', () => {
  cy.login('testuser', 'password');
  cy.verifyPageType('MAIN_CANVAS');

  cy.logout();
  cy.verifyPageType('LOGIN');

  cy.getPageContext().then((context) => {
    expect(context.pageType).to.equal('LOGIN');
    expect(context.isReady).to.be.true;
  });
});
```

## Error Handling

### No Silent Failures

Tests must explicitly validate all expected outcomes.

**Checklist:**
- ✅ Assert successful navigation
- ✅ Verify authentication state
- ✅ Validate page readiness
- ✅ Check for console errors
- ✅ Confirm expected elements exist
- ✅ Validate data loaded correctly

**Example:**

```javascript
it('R-AUTH-001: Should authenticate valid user', () => {
  // Navigate and verify
  cy.navigateToPage('/login', {
    expectedPageType: 'LOGIN',
    waitForReady: true
  });

  // Authenticate
  cy.login('validuser', 'password');

  // Verify authentication state
  cy.getSessionContext().then((context) => {
    expect(context.isLoggedIn).to.be.true;
    expect(context.user).to.not.be.null;
  });

  // Verify navigation to authenticated page
  cy.verifyPageType('MAIN_CANVAS');

  // Verify no console errors
  cy.window().then((win) => {
    expect(win.consoleErrors).to.have.length(0);
  });
});
```

### Timeout Configuration

Use appropriate timeouts for different operation types.

**Timeout Constants:**

```javascript
export const TestConstants = {
  TIMEOUTS: {
    DEFAULT: 10000,           // Standard operations
    API_CALL: 30000,          // API requests
    PAGE_LOAD: 15000,         // Page navigation
    AUTHENTICATION: 45000,    // Login/logout operations
    ELEMENT_INTERACTION: 15000 // User interactions
  }
};
```

**Usage:**

```javascript
// Navigation with custom timeout
cy.navigateToPage('/slow-page', {
  expectedPageType: 'SLOW_PAGE',
  timeout: TestConstants.TIMEOUTS.PAGE_LOAD
});

// API call with appropriate timeout
cy.request({
  url: '/api/users',
  timeout: TestConstants.TIMEOUTS.API_CALL
}).then((response) => {
  expect(response.status).to.equal(200);
});

// Element with extended timeout
cy.get(TestConstants.SELECTORS.SLOW_ELEMENT, {
  timeout: TestConstants.TIMEOUTS.ELEMENT_INTERACTION
}).should('be.visible');
```

## Code Organization

### Self-Sufficient Tests

Each test must be independently executable.

**Requirements:**
- Clear session state if needed
- Establish required authentication
- Verify initial conditions
- Don't depend on other tests
- Don't rely on execution order

**Example:**

```javascript
describe('User Management', () => {
  // Each test is self-sufficient

  it('R-USER-001: Should create new user', () => {
    // Clear state
    cy.clearSession();

    // Authenticate
    cy.login('admin', 'password');

    // Verify prerequisites
    cy.verifyPageType('MAIN_CANVAS');

    // Execute test
    cy.navigateToPage('/admin/users');
    cy.get(TestConstants.SELECTORS.USER.ADD_BUTTON).click();
    // ... rest of test
  });

  it('R-USER-002: Should edit existing user', () => {
    // Completely independent - doesn't rely on previous test
    cy.clearSession();
    cy.login('admin', 'password');
    cy.navigateToPage('/admin/users');
    // ... rest of test
  });
});
```

### Descriptive Test Names

Use descriptive, action-based test names with requirement traceability.

**Pattern:** `R-{FEATURE}-{NUMBER}: Should {specific expected behavior}`

**Examples:**

```javascript
// ✅ GOOD - Descriptive with requirement ID
it('R-AUTH-001: Should reject invalid credentials with error message', () => {});
it('R-DASH-015: Should display paginated user list sorted by name', () => {});
it('R-ADMIN-003: Should update system configuration and show success notification', () => {});

// ❌ BAD - Vague or unclear
it('should work', () => {});
it('test login', () => {});
it('users', () => {});
```

## Modern Cypress Patterns

### Use cy.session()

Leverage Cypress session caching for faster test execution.

**Implementation:**

```javascript
/**
 * Login with session caching
 * @param {string} username - User login name
 * @param {string} password - User password
 */
Cypress.Commands.add('login', (username, password) => {
  cy.session([username, password], () => {
    cy.visit('/login');
    cy.get(TestConstants.SELECTORS.LOGIN.USERNAME_INPUT).type(username);
    cy.get(TestConstants.SELECTORS.LOGIN.PASSWORD_INPUT).type(password);
    cy.get(TestConstants.SELECTORS.LOGIN.SUBMIT_BUTTON).click();
    cy.url().should('not.include', '/login');
  }, {
    validate() {
      cy.getSessionContext().then((context) => {
        expect(context.isLoggedIn).to.be.true;
      });
    }
  });
});
```

**Benefits:**
- Automatic session caching across tests
- Faster test execution by reusing valid sessions
- Built-in session validation
- Improved test reliability

### Anti-Patterns to Avoid

**Prohibited Practices:**

```javascript
// ❌ BAD - Fixed timeout waits
cy.wait(1000);
cy.get('[data-testid="element"]');

// ✅ GOOD - Wait for specific condition
cy.get('[data-testid="element"]', {
  timeout: TestConstants.TIMEOUTS.DEFAULT
}).should('be.visible');

// ❌ BAD - Element existence checks in test logic
cy.get('[data-testid="optional"]').then(($el) => {
  if ($el.length > 0) {
    cy.wrap($el).click();
  }
});

// ✅ GOOD - Explicit test cases
it('should click optional element when present', () => {
  cy.get('[data-testid="optional"]').should('exist').click();
});

// ❌ BAD - Manual session clearing
cy.clearCookies();
cy.clearLocalStorage();

// ✅ GOOD - Use session management commands
cy.clearSession();

// ❌ BAD - Direct URL manipulation
cy.url().then((url) => {
  const newUrl = url.replace('/old', '/new');
  cy.visit(newUrl);
});

// ✅ GOOD - Use navigation helpers
cy.navigateToPage('/new', { expectedPageType: 'NEW_PAGE' });
```

## Performance Optimization

### Session Reuse Strategy

**Pattern:**

```javascript
describe('Dashboard Features', () => {
  // Login once for all tests in suite
  before(() => {
    cy.clearSession();
    cy.login('testuser', 'password');
  });

  // Validate session before each test
  beforeEach(() => {
    cy.retrieveSession();
    cy.visit('/dashboard');
  });

  // Individual tests run faster with cached session
  it('R-DASH-001: Should display user summary', () => {
    cy.get(TestConstants.SELECTORS.DASHBOARD.SUMMARY)
      .should('be.visible');
  });

  it('R-DASH-002: Should show recent activity', () => {
    cy.get(TestConstants.SELECTORS.DASHBOARD.ACTIVITY)
      .should('be.visible');
  });
});
```

### Parallel Execution Compatibility

Structure tests for parallel execution:
- No shared state between tests
- Independent data setup/teardown
- Unique test data identifiers
- No hardcoded timing dependencies

## Maintenance Guidelines

**Regular Maintenance Tasks:**
- Update navigation helpers when application routes change
- Verify tests don't depend on execution order
- Validate test reliability in CI/CD environment
- Review and update timeout values based on performance
- Keep custom commands synchronized with application changes

**Code Review Checklist:**
- ✅ No branching logic in tests
- ✅ Explicit assertions used throughout
- ✅ Navigation helpers used instead of direct cy.visit()
- ✅ Session management via custom commands
- ✅ Appropriate timeouts configured
- ✅ Tests are self-sufficient
- ✅ Descriptive test names with requirement IDs
- ✅ No anti-patterns present
