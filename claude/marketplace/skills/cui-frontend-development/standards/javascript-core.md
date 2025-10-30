# JavaScript Core Standards

## Purpose
Comprehensive standards for modern JavaScript development including ES2022+ patterns, package configuration, dependencies, Jest testing, and best practices for CUI projects.

## Modern JavaScript Standards

### ECMAScript Version Support
* **Target**: ES2022 (ES13) and later features
* **Browser Support**: Modern browsers with native ES modules
* **Node.js**: Version 20.12.2 LTS or later
* **Transpilation**: Babel for test environments only

### Critical Rule: Vanilla JavaScript Preference
**The preferred way is to use vanilla JavaScript where possible: fetch instead of ajax. If it is not too complex to implement without jQuery/cash, always resort to vanilla JS.**

This rule ensures:
* Better performance by avoiding unnecessary library overhead
* Reduced bundle sizes and faster load times
* Native browser API usage for modern features
* Elimination of legacy dependencies

Examples:
```javascript
// ✅ Preferred: Vanilla JavaScript fetch
const response = await fetch('/api/data');
const data = await response.json();

// ❌ Avoid: jQuery ajax
$.ajax({
  url: '/api/data',
  success: (data) => { /* ... */ }
});

// ✅ Preferred: Native DOM manipulation
document.querySelector('.button').addEventListener('click', handleClick);

// ❌ Avoid: jQuery DOM manipulation
$('.button').on('click', handleClick);
```

## Module System Standards

### ES Modules
Use ES modules exclusively:

```javascript
// Named exports (preferred)
export const utilityFunction = () => {
  // Implementation
};

export class ComponentClass {
  // Implementation
}

// Default exports (when appropriate)
export default class MainComponent {
  // Implementation
}
```

### Import Patterns
```javascript
// Framework imports first
import { html, css, LitElement } from 'lit';

// Third-party imports
import { customElement, property } from 'lit/decorators.js';

// Local imports (relative paths)
import { validateInput } from '../utilities/validation.js';
import { API_ENDPOINTS } from '../config/constants.js';
```

## Variable and Function Standards

### Variable Declaration
```javascript
// Preferred: const for immutable bindings
const apiEndpoint = 'https://api.example.com';
const userConfig = { timeout: 5000 };

// Use let for reassignment
let currentUser = null;
let retryCount = 0;

// Never use var
```

### Function Declaration Patterns
```javascript
// Arrow functions for utilities and callbacks
const processData = (data) => {
  return data.map(item => item.value);
};

// Regular functions for methods and constructors
class DataProcessor {
  processItems(items) {
    return items.filter(item => this.isValid(item));
  }
}

// Async functions - let errors bubble up naturally
const fetchUserData = async (userId) => {
  const response = await fetch(`/api/users/${userId}`);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return await response.json();
};
```

### Destructuring Standards
```javascript
// Object destructuring
const { name, email, preferences = {} } = user;

// Array destructuring
const [first, second, ...rest] = items;

// Function parameter destructuring
const createUser = ({ name, email, role = 'user' }) => {
  return { id: generateId(), name, email, role };
};
```

## Function Organization and Complexity

### Complexity Limits
* **Cyclomatic Complexity**: Maximum 15 branches per function
* **Statement Count**: Maximum 20 statements per function
* **Parameter Count**: Maximum 5 parameters per function
* **Nesting Depth**: Maximum 3 levels of conditional/loop nesting

### Refactoring Strategies
```javascript
// ❌ Complex monolithic function
function processUserData(user) {
  if (!user) return null;
  if (user.isActive) {
    if (user.hasPermission('admin')) {
      // complex logic
    }
  }
  // many more statements
}

// ✅ Refactored with helper functions
function processUserData(user) {
  if (!user) return null;
  return user.isActive ? processActiveUser(user) : null;
}

function processActiveUser(user) {
  return user.hasPermission('admin') ? processAdmin(user) : processRegularUser(user);
}
```

## Package.json Configuration

For complete package.json organization and structure standards, see `javascript-project-structure.md` in this skill.

### Required Structure Example
```json
{
  "name": "project-name",
  "version": "1.0.0-SNAPSHOT",
  "description": "Brief project description",
  "private": true,
  "scripts": {
    "build": "webpack --mode production",
    "build:dev": "webpack --mode development",
    "test": "jest",
    "test:ci-strict": "jest --ci --coverage --watchAll=false --passWithNoTests --coverageThreshold='{\"global\":{\"branches\":80,\"functions\":80,\"lines\":80,\"statements\":80}}'",
    "lint": "npm run lint:js",
    "lint:js": "eslint src/**/*.js",
    "lint:js:fix": "eslint --fix src/**/*.js",
    "lint:fix": "npm run lint:js:fix",
    "format": "prettier --write \"src/**/*.js\"",
    "format:check": "prettier --check \"src/**/*.js\"",
    "quality": "npm run lint && npm run format:check",
    "quality:fix": "npm run lint:fix && npm run format",
    "clean": "rimraf target/classes/META-INF/resources target/dist"
  }
}
```

## JavaScript Dependencies

### Required Development Dependencies
```json
{
  "devDependencies": {
    "jest": "latest",
    "jest-environment-jsdom": "latest",
    "@testing-library/jest-dom": "latest",
    "eslint": "latest",
    "eslint-config-airbnb-base": "latest",
    "eslint-config-prettier": "latest",
    "eslint-plugin-import": "latest",
    "eslint-plugin-jest": "latest",
    "eslint-plugin-jsdoc": "latest",
    "eslint-plugin-prettier": "latest",
    "eslint-plugin-unicorn": "latest",
    "eslint-plugin-security": "latest",
    "eslint-plugin-promise": "latest",
    "prettier": "latest",
    "webpack": "latest",
    "webpack-cli": "latest",
    "terser": "latest",
    "rimraf": "latest",
    "@babel/core": "latest",
    "@babel/preset-env": "latest",
    "babel-jest": "latest",
    "core-js": "latest"
  }
}
```

## Jest Configuration

### Required Jest Setup
```json
"jest": {
  "testEnvironment": "jest-environment-jsdom",
  "testMatch": ["**/src/test/js/**/*.test.js"],
  "transform": {
    "^.+\\.js$": "babel-jest"
  },
  "transformIgnorePatterns": [
    "node_modules/(?!(lit|@lit)/)"
  ],
  "collectCoverageFrom": [
    "src/main/resources/static/js/**/*.js",
    "!**/*.min.js",
    "!**/*.bundle.js"
  ],
  "coverageThreshold": {
    "global": {
      "branches": 80,
      "functions": 80,
      "lines": 80,
      "statements": 80
    }
  },
  "coverageReporters": ["text", "lcov", "html"],
  "coverageDirectory": "target/coverage"
}
```

### Babel Configuration
```json
"babel": {
  "presets": [
    ["@babel/preset-env", {
      "modules": "auto",
      "targets": {
        "browsers": ["last 2 versions", "not dead", "> 0.5%"]
      },
      "useBuiltIns": "usage",
      "corejs": "3.32"
    }]
  ],
  "plugins": [
    "@babel/plugin-transform-class-properties",
    "@babel/plugin-transform-private-methods",
    "@babel/plugin-transform-optional-chaining",
    "@babel/plugin-transform-nullish-coalescing-operator"
  ]
}
```

## Dependency Management

### Update Process
When adding, removing, or updating dependencies:

1. **Security Assessment First**: Run `npm audit` before changes
2. **Update to Latest Secure Versions**: Use most recent stable versions
3. **Post-Change Verification**:
   - Run `npm install` and review warnings
   - Execute `npm audit` to verify no new vulnerabilities
   - Test all functionality
4. **Fix Security Issues**: Run `npm audit fix` for automatic fixes
5. **Document Unfixable Issues**: Document any unresolvable warnings

### Version Management
* Always use most recent working versions
* Use exact versions for critical dependencies
* Always commit `package-lock.json`
* **Mandatory security auditing** with `npm audit`

## Error Handling Patterns

### Async Error Handling
```javascript
// Let errors bubble up naturally
const fetchUserData = async (userId) => {
  const response = await fetch(`/api/users/${userId}`);

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }

  return await response.json();
};

// Transform errors meaningfully when caught
const fetchUserDataWithContext = async (userId) => {
  try {
    return await fetchUserData(userId);
  } catch (error) {
    // Only catch to add meaningful context
    throw new Error(`Failed to fetch user data for ID ${userId}: ${error.message}`, {
      cause: error,
      userId
    });
  }
};
```

### Promise Utilities
```javascript
// Timeout wrapper
const withTimeout = (promise, timeoutMs) => {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Operation timed out')), timeoutMs)
    )
  ]);
};

// Retry logic
const retry = async (fn, maxRetries = 3, delay = 1000) => {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries) throw error;
      await new Promise(resolve => setTimeout(resolve, delay * attempt));
    }
  }
};
```

## Development Workflow

### Development Environment Setup
1. Install Node.js 20.12.2 LTS
2. Clone project repository
3. Run `npm install` to install dependencies
4. Verify setup with `npm run test`
5. Configure IDE for JavaScript development

### Development Cycle
1. Write JavaScript code following standards
2. Run `npm run format` to format code
3. Run `npm run lint:fix` to fix linting issues
4. Run `npm run test` to verify functionality
5. Run `npm run quality` before committing

## References

* [ECMAScript 2022 Specification](https://tc39.es/ecma262/)
* [MDN JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
* [Jest Testing Framework](https://jestjs.io/)
* [ESLint Documentation](https://eslint.org/)
