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

## Package.json Configuration and Dependencies

**For complete package.json configuration, dependencies, Jest setup, Babel configuration, and dependency management, see `javascript-project-structure.md`.**

This file focuses on JavaScript coding standards (language features, modules, functions, complexity). All project structure, build configuration, and dependency management is documented in javascript-project-structure.md.

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
