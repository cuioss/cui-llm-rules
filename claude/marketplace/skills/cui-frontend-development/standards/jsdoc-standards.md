# JSDoc Documentation Standards

## Purpose
Comprehensive standards for JavaScript documentation using JSDoc to ensure consistent, maintainable, and professional code documentation across all CUI projects.

## JSDoc Integration Requirements

### ESLint Plugin Configuration
```json
{
  "devDependencies": {
    "eslint-plugin-jsdoc": "^46.8.0"
  }
}
```

```javascript
// .eslintrc.js
module.exports = {
  extends: [
    'plugin:jsdoc/recommended'
  ],
  plugins: ['jsdoc'],
  rules: {
    'jsdoc/require-description': 'error',
    'jsdoc/require-param-description': 'error',
    'jsdoc/require-returns-description': 'error',
    'jsdoc/require-example': 'warn'
  }
};
```

## Documentation Requirements

### Mandatory Documentation
The following MUST be documented with JSDoc:

* **All public functions and methods**
* **All classes and constructors**
* **All exported modules**
* **Complex algorithms or business logic**
* **Configuration objects and constants**
* **Event handlers and callbacks**

### Optional Documentation
The following MAY be documented based on complexity:

* **Private methods** (when complex or non-obvious)
* **Simple getter/setter methods**
* **Utility functions** (when purpose is clear from name)

## JSDoc Comment Structure

### Basic Format
```javascript
/**
 * Brief description of the function or class.
 *
 * Detailed description providing context, usage notes,
 * and any important implementation details.
 *
 * @param {type} paramName - Description of the parameter
 * @param {type} [optionalParam] - Description of optional parameter
 * @returns {type} Description of return value
 * @throws {Error} Description of when errors are thrown
 * @example
 * // Example usage
 * const result = functionName('example');
 *
 * @since 1.0.0
 * @author Developer Name
 */
```

### Required Tags
* `@param` - For all parameters
* `@returns` - For functions that return values
* `@throws` - For functions that can throw exceptions
* `@example` - At least one example for public APIs

### Optional but Recommended Tags
* `@since` - Version when added
* `@author` - Original author
* `@see` - References to related functions/classes
* `@deprecated` - For deprecated functionality
* `@todo` - For planned improvements

## Function Documentation Standards

### Simple Functions
```javascript
/**
 * Calculates the total price including tax.
 *
 * @param {number} price - The base price before tax
 * @param {number} taxRate - The tax rate as a decimal (e.g., 0.08 for 8%)
 * @returns {number} The total price including tax
 * @throws {Error} When price or taxRate is negative
 * @example
 * const total = calculateTotalPrice(100, 0.08);
 * console.log(total); // 108
 */
function calculateTotalPrice(price, taxRate) {
  if (price < 0 || taxRate < 0) {
    throw new Error('Price and tax rate must be non-negative');
  }
  return price * (1 + taxRate);
}
```

### Complex Functions
```javascript
/**
 * Validates a JWT token and extracts user information.
 *
 * This function performs comprehensive JWT validation including
 * signature verification, expiration checking, and issuer validation.
 *
 * @param {string} token - The JWT token to validate
 * @param {Object} options - Validation options
 * @param {string} options.issuer - Expected token issuer
 * @param {string} options.audience - Expected token audience
 * @param {boolean} [options.ignoreExpiration=false] - Skip expiration check
 * @returns {Promise<Object>} Promise resolving to decoded token payload
 * @returns {string} returns.sub - Subject (user ID)
 * @returns {string} returns.email - User email address
 * @returns {Array<string>} returns.roles - User roles
 * @throws {JWTError} When token is invalid or expired
 * @throws {NetworkError} When JWKS endpoint is unreachable
 * @example
 * const payload = await validateJWT(token, {
 *   issuer: 'https://auth.example.com',
 *   audience: 'my-app'
 * });
 * console.log(payload.sub); // User ID
 */
async function validateJWT(token, options) {
  // Implementation
}
```

### Arrow Functions
```javascript
/**
 * Filters an array of users by role.
 *
 * @param {Array<Object>} users - Array of user objects
 * @param {string} role - Role to filter by
 * @returns {Array<Object>} Filtered array of users
 * @example
 * const admins = filterUsersByRole(users, 'admin');
 */
const filterUsersByRole = (users, role) => {
  return users.filter(user => user.role === role);
};
```

## Class Documentation Standards

### Class Definition
```javascript
/**
 * Manages user authentication and session handling.
 *
 * This class provides methods for user login, logout, token refresh,
 * and session validation. It integrates with the backend authentication
 * API and manages local storage of authentication tokens.
 *
 * @class
 * @example
 * const authManager = new AuthManager({
 *   apiUrl: 'https://api.example.com',
 *   tokenRefreshInterval: 300000
 * });
 *
 * await authManager.login('username', 'password');
 */
class AuthManager {
  /**
   * Creates an instance of AuthManager.
   *
   * @param {Object} config - Configuration options
   * @param {string} config.apiUrl - Base URL for authentication API
   * @param {number} [config.tokenRefreshInterval=300000] - Token refresh interval in ms
   */
  constructor(config) {
    this.apiUrl = config.apiUrl;
    this.tokenRefreshInterval = config.tokenRefreshInterval || 300000;
  }

  /**
   * Authenticates a user with username and password.
   *
   * @param {string} username - User's username
   * @param {string} password - User's password
   * @returns {Promise<Object>} Authentication result with user info and token
   * @throws {AuthError} When authentication fails
   * @example
   * const result = await authManager.login('john.doe', 'secretpass');
   * console.log(result.user.email);
   */
  async login(username, password) {
    // Implementation
  }
}
```

## Type Documentation

### Complex Types
```javascript
/**
 * @typedef {Object} UserProfile
 * @property {string} id - Unique user identifier
 * @property {string} email - User's email address
 * @property {string} name - User's full name
 * @property {Array<string>} roles - Array of assigned roles
 * @property {Object} preferences - User preferences
 * @property {string} preferences.theme - UI theme preference
 * @property {string} preferences.language - Language preference
 * @property {Date} createdAt - Account creation date
 * @property {Date} lastLogin - Last login timestamp
 */

/**
 * Fetches a user profile from the API.
 *
 * @param {string} userId - User ID to fetch
 * @returns {Promise<UserProfile>} User profile object
 * @example
 * const profile = await fetchUserProfile('user-123');
 */
async function fetchUserProfile(userId) {
  // Implementation
}
```

### Callback Documentation
```javascript
/**
 * @callback ValidationCallback
 * @param {Object} result - Validation result
 * @param {boolean} result.valid - Whether validation passed
 * @param {Array<string>} result.errors - Array of error messages
 * @returns {void}
 */

/**
 * Validates form data with a callback.
 *
 * @param {Object} formData - Form data to validate
 * @param {ValidationCallback} callback - Callback function
 * @example
 * validateForm(data, (result) => {
 *   if (result.valid) {
 *     console.log('Valid!');
 *   } else {
 *     console.error(result.errors);
 *   }
 * });
 */
function validateForm(formData, callback) {
  // Implementation
}
```

## Module Documentation

### Module-Level Documentation
```javascript
/**
 * @module utils/validation
 * @description
 * Provides validation utilities for user input, form data,
 * and API responses.
 *
 * @requires module:utils/errors
 * @requires module:config/constants
 *
 * @example
 * import { validateEmail, validatePassword } from './utils/validation.js';
 *
 * if (validateEmail(email)) {
 *   // Email is valid
 * }
 */

/**
 * Validates an email address format.
 *
 * @function
 * @param {string} email - Email address to validate
 * @returns {boolean} True if email format is valid
 * @example
 * validateEmail('user@example.com'); // true
 * validateEmail('invalid-email'); // false
 */
export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};
```

## Constant Documentation

### Configuration Objects
```javascript
/**
 * API endpoint configuration.
 *
 * @constant {Object}
 * @property {string} BASE_URL - Base API URL
 * @property {Object} ENDPOINTS - API endpoint paths
 * @property {string} ENDPOINTS.USERS - Users endpoint
 * @property {string} ENDPOINTS.AUTH - Authentication endpoint
 * @property {number} TIMEOUT - Default request timeout in ms
 */
export const API_CONFIG = {
  BASE_URL: 'https://api.example.com',
  ENDPOINTS: {
    USERS: '/users',
    AUTH: '/auth'
  },
  TIMEOUT: 30000
};
```

## Best Practices

### Documentation Style
* Write in present tense
* Be concise but complete
* Include examples for public APIs
* Document error conditions
* Use proper grammar and punctuation

### Type Annotations
* Always specify parameter types
* Document optional parameters with `[]`
* Use TypeScript-style syntax for complex types
* Document return types accurately

### Examples
* Provide realistic examples
* Show common use cases
* Include error handling examples
* Keep examples concise

## References

* [JSDoc Documentation](https://jsdoc.app/)
* [ESLint JSDoc Plugin](https://github.com/gajus/eslint-plugin-jsdoc)
