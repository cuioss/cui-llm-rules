# Web Components Standards (Lit Framework)

## Purpose
Standards for developing web components using the Lit framework, including architecture patterns, CSS-in-JS practices, and component lifecycle management.

## Lit Framework Standards

### Framework Version Requirements
* **Lit**: Version 3.0.0 or later
* **Target**: Modern browsers with native Web Components support
* **Polyfills**: Not required for supported browser targets

### Import Standards
```javascript
import { html, css, LitElement } from 'lit';
import { devui } from 'devui';  // For DevUI integration when needed
```

### Component Base Class
All components must extend `LitElement`:

```javascript
export class ComponentName extends LitElement {
  // Component implementation
}
```

## Component Architecture Standards

### Component Class Structure
Components must follow this standardized structure:

```javascript
export class QwcComponentName extends LitElement {
  // 1. Static styles (CSS-in-JS)
  static styles = css`
    /* Component styles */
  `;

  // 2. Static properties definition
  static properties = {
    propertyName: { type: String },
    anotherProperty: { state: true },
  };

  // 3. Constructor (if needed)
  constructor() {
    super();
    // Initialize properties
  }

  // 4. Lifecycle methods
  connectedCallback() {
    super.connectedCallback();
    // Component connected to DOM
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    // Component removed from DOM
  }

  // 5. Event handlers (private methods)
  _handleEvent() {
    // Event handling logic
  }

  // 6. Public methods
  publicMethod() {
    // Public API
  }

  // 7. Render method (always last)
  render() {
    return html`
      <!-- Component template -->
    `;
  }
}
```

### Component Naming Standards
* **Class Names**: PascalCase with 'Qwc' prefix (e.g., `QwcJwtConfig`)
* **File Names**: kebab-case (e.g., `qwc-jwt-config.js`)
* **Custom Element Names**: kebab-case with project prefix (e.g., `qwc-jwt-config`)

### Component Registration
Components should be self-registering:

```javascript
// At the end of component file
customElements.define('qwc-component-name', QwcComponentName);
```

## Property and State Management

### Property Declaration Standards
```javascript
static properties = {
  // Public properties (reactive)
  title: { type: String },
  count: { type: Number },
  isActive: { type: Boolean },
  items: { type: Array },
  config: { type: Object },

  // Private state (internal reactive state)
  _loading: { state: true },
  _error: { state: true },
  _data: { state: true },
};
```

### Property Initialization
```javascript
constructor() {
  super();
  // Initialize all properties with default values
  this.title = '';
  this.count = 0;
  this.isActive = false;
  this.items = [];
  this.config = {};
  this._loading = false;
  this._error = null;
  this._data = null;
}
```

## CSS-in-JS Standards

### Static Styles Definition
```javascript
static styles = css`
  :host {
    display: block;
    padding: var(--spacing-md, 1rem);
  }

  .container {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm, 0.5rem);
  }

  .button {
    padding: var(--spacing-sm, 0.5rem) var(--spacing-md, 1rem);
    background-color: var(--color-primary, #007bff);
    color: white;
    border: none;
    border-radius: var(--border-radius, 0.25rem);
    cursor: pointer;
  }

  .button:hover {
    opacity: 0.9;
  }
`;
```

### CSS Custom Properties
```javascript
static styles = css`
  :host {
    /* Component-specific variables */
    --component-bg: var(--bg-primary, #ffffff);
    --component-text: var(--text-primary, #212529);
  }

  .component-root {
    background-color: var(--component-bg);
    color: var(--component-text);
  }
`;
```

## Template Rendering

### HTML Template Standards
```javascript
render() {
  return html`
    <div class="container">
      <h2>${this.title}</h2>

      ${this._renderContent()}

      <button
        class="action-button"
        @click=${this._handleButtonClick}
        ?disabled=${this._loading}
      >
        ${this._loading ? 'Loading...' : 'Submit'}
      </button>
    </div>
  `;
}

_renderContent() {
  if (this._error) {
    return html`<div class="error">${this._error}</div>`;
  }

  if (this._loading) {
    return html`<div class="loading">Loading...</div>`;
  }

  return html`<div class="content">${this._data}</div>`;
}
```

### Conditional Rendering
```javascript
// Boolean attributes
html`<button ?disabled=${this.isDisabled}>Click</button>`;

// Conditional content
html`
  ${this.showError ? html`<div class="error">${this.errorMessage}</div>` : ''}
`;

// List rendering
html`
  <ul>
    ${this.items.map(item => html`
      <li>${item.name}</li>
    `)}
  </ul>
`;
```

## Event Handling

### Event Binding
```javascript
render() {
  return html`
    <button @click=${this._handleClick}>Click Me</button>
    <input @input=${this._handleInput} @change=${this._handleChange} />
    <form @submit=${this._handleSubmit}>
      <input type="text" />
      <button type="submit">Submit</button>
    </form>
  `;
}

_handleClick(event) {
  console.log('Button clicked', event);
}

_handleInput(event) {
  this.value = event.target.value;
}

_handleSubmit(event) {
  event.preventDefault();
  // Handle form submission
}
```

### Custom Events
```javascript
_dispatchCustomEvent(detail) {
  this.dispatchEvent(new CustomEvent('custom-event', {
    detail,
    bubbles: true,
    composed: true
  }));
}

// Usage in render
_handleAction() {
  this._dispatchCustomEvent({ action: 'completed', data: this._data });
}
```

## Lifecycle Methods

### Component Lifecycle
```javascript
// Called when element is added to DOM
connectedCallback() {
  super.connectedCallback();
  this._fetchInitialData();
  window.addEventListener('resize', this._handleResize);
}

// Called when element is removed from DOM
disconnectedCallback() {
  super.disconnectedCallback();
  window.removeEventListener('resize', this._handleResize);
}

// Called after first render
firstUpdated(changedProperties) {
  super.firstUpdated(changedProperties);
  // Access rendered DOM elements
  const button = this.shadowRoot.querySelector('.primary-button');
}

// Called after every render
updated(changedProperties) {
  super.updated(changedProperties);

  if (changedProperties.has('config')) {
    this._processConfigChange();
  }
}
```

## Async Data Loading

### Data Fetching Pattern
```javascript
async connectedCallback() {
  super.connectedCallback();
  await this._loadData();
}

async _loadData() {
  try {
    this._loading = true;
    this._error = null;

    const response = await fetch('/api/data');

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    this._data = await response.json();
  } catch (error) {
    this._error = error.message;
  } finally {
    this._loading = false;
  }
}
```

## Component Testing

### Testing with Jest and Lit Mocks
```javascript
import { QwcComponentName } from './qwc-component-name.js';

describe('QwcComponentName', () => {
  let component;
  let container;

  beforeEach(() => {
    container = document.createElement('div');
    document.body.appendChild(container);

    component = new QwcComponentName();
    container.appendChild(component);
  });

  afterEach(() => {
    document.body.removeChild(container);
  });

  test('should render component', () => {
    expect(component).toBeDefined();
    expect(component.shadowRoot).not.toBeNull();
  });

  test('should handle property changes', async () => {
    component.title = 'New Title';
    await component.updateComplete;

    const heading = component.shadowRoot.querySelector('h2');
    expect(heading.textContent).toBe('New Title');
  });

  test('should handle events', async () => {
    const button = component.shadowRoot.querySelector('.action-button');
    const spy = jest.spyOn(component, '_handleButtonClick');

    button.click();

    expect(spy).toHaveBeenCalled();
  });
});
```

## Best Practices

### Performance Optimization
* Use `shouldUpdate()` to prevent unnecessary renders
* Implement lazy loading for heavy components
* Use `static` methods where possible
* Minimize property changes

### Accessibility
* Use semantic HTML in templates
* Include ARIA attributes where needed
* Ensure keyboard navigation works
* Test with screen readers

### Code Organization
* Keep render methods focused
* Extract complex logic to helper methods
* Use private methods (prefixed with `_`) for internal logic
* Document public API with JSDoc

## References

* [Lit Documentation](https://lit.dev/)
* [Web Components Standards](https://developer.mozilla.org/en-US/docs/Web/Web_Components)
* [Custom Elements Specification](https://html.spec.whatwg.org/multipage/custom-elements.html)
