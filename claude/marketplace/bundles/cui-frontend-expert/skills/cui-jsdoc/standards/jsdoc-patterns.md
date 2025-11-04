# JSDoc Documentation Patterns

## Purpose

Quick reference patterns for documenting functions, classes, modules, types, and web components.

## Function Patterns

### Simple Function

```javascript
/**
 * Calculates the total price including tax.
 *
 * @param {number} price - Base price before tax
 * @param {number} taxRate - Tax rate as decimal (e.g., 0.08)
 * @returns {number} Total price including tax
 * @throws {Error} When price or taxRate is negative
 * @example
 * const total = calculateTotalPrice(100, 0.08); // 108
 */
function calculateTotalPrice(price, taxRate) {
  // Implementation
}
```

### Async Function

```javascript
/**
 * Loads configuration from remote server.
 *
 * @async
 * @param {string} configUrl - Configuration endpoint URL
 * @param {Object} [options={}] - Request options
 * @param {number} [options.timeout=5000] - Timeout in milliseconds
 * @returns {Promise<Object>} Validated configuration
 * @throws {NetworkError} When fetch fails
 * @throws {ValidationError} When config is invalid
 * @example
 * const config = await loadConfig('https://api.example.com/config');
 */
async function loadConfig(configUrl, options = {}) {
  // Implementation
}
```

### Complex Function with Nested Parameters

```javascript
/**
 * Creates a new user session with JWT token.
 *
 * @param {Object} sessionData - Session configuration
 * @param {Object} sessionData.user - User information
 * @param {string} sessionData.user.id - User identifier
 * @param {string} sessionData.user.email - User email
 * @param {Object} sessionData.tokenConfig - Token configuration
 * @param {number} sessionData.tokenConfig.expiresIn - Expiration in seconds
 * @returns {Promise<string>} Generated JWT token
 * @throws {ValidationError} When required data is missing
 * @example
 * const token = await createSession({
 *   user: { id: 'user123', email: 'user@example.com' },
 *   tokenConfig: { expiresIn: 3600 }
 * });
 */
async function createSession(sessionData) {
  // Implementation
}
```

## Class Patterns

### Class Declaration

```javascript
/**
 * Manages JWT token validation and user authentication.
 *
 * Handles JWKS key rotation automatically and caches keys
 * for improved performance.
 *
 * @class JWTManager
 * @example
 * const manager = new JWTManager({
 *   issuer: 'https://auth.example.com',
 *   jwksUri: 'https://auth.example.com/.well-known/jwks.json'
 * });
 * const isValid = await manager.validateToken(token);
 */
class JWTManager {
  /**
   * Creates a new JWT manager instance.
   *
   * @param {Object} config - Configuration object
   * @param {string} config.issuer - JWT issuer URL
   * @param {string} config.jwksUri - JWKS endpoint URL
   * @param {number} [config.cacheTTL=3600] - Key cache TTL in seconds
   * @throws {ConfigError} When required config is missing
   */
  constructor(config) {
    // Implementation
  }

  /**
   * Validates a JWT token against configured issuer.
   *
   * @param {string} token - JWT token to validate
   * @returns {Promise<boolean>} True if token is valid
   * @throws {JWTError} When token is invalid
   * @example
   * const isValid = await manager.validateToken(token);
   */
  async validateToken(token) {
    // Implementation
  }
}
```

### Class with Inheritance

```javascript
/**
 * Extended JWT manager with refresh token support.
 *
 * @extends JWTManager
 * @example
 * const manager = new RefreshableJWTManager({
 *   issuer: 'https://auth.example.com',
 *   refreshEndpoint: 'https://auth.example.com/refresh'
 * });
 */
class RefreshableJWTManager extends JWTManager {
  /**
   * Validates token and auto-refreshes if near expiration.
   *
   * @override
   * @param {string} token - JWT token
   * @returns {Promise<boolean>} True if valid
   */
  async validateToken(token) {
    // Implementation
  }
}
```

## Module Patterns

### Module with File Overview

```javascript
/**
 * @fileoverview JWT validation utilities for Quarkus DevUI.
 *
 * Provides utilities for JWT token validation, user authentication,
 * and security configuration management.
 *
 * @module jwt-utils
 * @version 1.0.0
 * @author DevUI Team
 */

/**
 * Default JWT configuration.
 *
 * @constant {Object} DEFAULT_CONFIG
 * @property {number} maxAge - Maximum token age in seconds
 * @property {boolean} requireHttps - Require HTTPS for validation
 */
export const DEFAULT_CONFIG = {
  maxAge: 3600,
  requireHttps: true
};

/**
 * Validates JWT token and extracts user information.
 *
 * @param {string} token - JWT token to validate
 * @returns {Promise<Object>} Decoded token payload
 * @throws {JWTError} When token is invalid
 */
export async function validateJWT(token) {
  // Implementation
}
```

## Type Patterns

### Custom Type Definition

```javascript
/**
 * User profile information.
 *
 * @typedef {Object} UserProfile
 * @property {string} id - Unique user identifier
 * @property {string} email - User email address
 * @property {Array<string>} roles - Assigned user roles
 * @property {boolean} active - Whether account is active
 */

/**
 * Validates a user profile.
 *
 * @param {UserProfile} profile - User profile to validate
 * @returns {boolean} True if profile is valid
 */
function validateProfile(profile) {
  // Implementation
}
```

### Function Type (Callback)

```javascript
/**
 * Progress callback function.
 *
 * @callback ProgressCallback
 * @param {number} completed - Number of completed items
 * @param {number} total - Total number of items
 * @returns {void}
 */

/**
 * Processes items with progress callback.
 *
 * @param {Array<Object>} items - Items to process
 * @param {ProgressCallback} onProgress - Progress callback
 * @returns {Promise<Array>} Processed items
 */
async function processItems(items, onProgress) {
  // Implementation
}
```

### Union and Literal Types

```javascript
/**
 * User role type.
 *
 * @typedef {('admin'|'user'|'guest')} UserRole
 */

/**
 * API response that can be success or error.
 *
 * @typedef {SuccessResponse|ErrorResponse} ApiResponse
 */

/**
 * Updates user role.
 *
 * @param {string} userId - User identifier
 * @param {UserRole} role - New role
 * @returns {Promise<void>}
 */
async function updateRole(userId, role) {
  // Implementation
}
```

## Web Component Patterns

### Lit Component

```javascript
/**
 * JWT Configuration component for Quarkus DevUI.
 *
 * Provides an interactive interface for viewing and managing
 * JWT validation configuration.
 *
 * @customElement qwc-jwt-config
 * @extends {LitElement}
 * @example
 * <qwc-jwt-config
 *   issuer="https://auth.example.com"
 *   audience="my-app">
 * </qwc-jwt-config>
 *
 * @fires config-changed - When configuration is updated
 * @fires validation-error - When validation fails
 *
 * @cssproperty --jwt-primary-color - Primary theme color
 * @cssproperty --jwt-error-color - Error message color
 */
class QwcJwtConfig extends LitElement {
  static get properties() {
    return {
      /**
       * JWT issuer URL for validation.
       *
       * @type {string}
       * @attribute issuer
       */
      issuer: { type: String },

      /**
       * Expected token audience.
       *
       * @type {string}
       * @attribute audience
       */
      audience: { type: String }
    };
  }

  /**
   * Validates the current configuration.
   *
   * @returns {Promise<ValidationResult>} Validation results
   * @fires config-validated - When validation succeeds
   * @example
   * await component.validateConfiguration();
   */
  async validateConfiguration() {
    // Implementation
  }
}

/**
 * Configuration validated event.
 *
 * @event QwcJwtConfig#config-validated
 * @type {CustomEvent}
 * @property {Object} detail - Event detail
 * @property {boolean} detail.valid - Whether config is valid
 */
```

## Documentation Quality

### Good Example

```javascript
/**
 * Authenticates user credentials against identity provider.
 *
 * Performs credential validation and returns authentication result
 * with user profile and JWT token. Failed authentication throws
 * specific error types for different failure scenarios.
 *
 * @param {string} username - User's login name (email format)
 * @param {string} password - User's password (min 8 chars)
 * @returns {Promise<Object>} Authentication result with user and token
 * @throws {ValidationError} When credentials format is invalid
 * @throws {AuthenticationError} When credentials are incorrect
 * @throws {AccountLockedError} When account is locked
 * @throws {NetworkError} When identity provider is unreachable
 * @example
 * try {
 *   const result = await authenticate('user@example.com', 'password123');
 *   console.log('User:', result.user.email);
 * } catch (error) {
 *   if (error instanceof AuthenticationError) {
 *     console.error('Invalid credentials');
 *   }
 * }
 */
async function authenticate(username, password) {
  // Implementation
}
```

### Bad Example (Avoid)

```javascript
/**
 * Authenticates user.
 *
 * @param {string} user - The user
 * @param {string} pass - The password
 * @returns {Object} The result
 */
async function authenticate(user, pass) {
  // Implementation
}
```

**Problems:**
- Vague description ("Authenticates user" - what does it do?)
- Parameter names don't match function signature
- No error documentation
- No examples
- Missing type details (Promise)
- Unclear return value description

## Quick Reference

### Required for All Public Functions
- Brief description
- @param for each parameter (type + description)
- @returns for non-void returns
- @throws for all possible errors
- @example for complex functions

### Required for Classes
- @class tag
- Class-level description
- Constructor documentation
- Public method documentation

### Required for Modules
- @fileoverview
- @module tag
- Export documentation

### Optional but Recommended
- @since for version tracking
- @author for team/developer
- @see for cross-references
- @deprecated for deprecated code
