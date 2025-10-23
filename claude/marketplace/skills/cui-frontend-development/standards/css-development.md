# CSS Development Standards

## Purpose
Comprehensive standards for CSS development including modern CSS3+ features, PostCSS configuration, linting, formatting, and design system patterns for CUI projects.

## Modern CSS Standards

### CSS Version Support
* **Target**: CSS3+ with modern features
* **Browser Support**: Last 2 versions, > 0.5% usage
* **Custom Properties**: Full support for CSS variables
* **Layout**: CSS Grid, Flexbox, Container Queries

### CSS Best Practices
* Use CSS custom properties (variables) for design tokens
* Prefer modern layout techniques (Grid, Flexbox)
* Minimize specificity and avoid !important
* Use BEM or similar naming convention
* Mobile-first responsive design

## Package.json CSS Scripts

### Required CSS Scripts
```json
{
  "scripts": {
    "build:css": "postcss src/**/*.css --dir target/classes/META-INF/resources/css",
    "build:css:dev": "postcss src/**/*.css --dir target/classes/META-INF/resources/css --watch",
    "build:css:min": "postcss src/**/*.css --dir target/classes/META-INF/resources/css --env production",
    "lint:css": "stylelint \"src/**/*.css\"",
    "lint:css:fix": "stylelint \"src/**/*.css\" --fix",
    "format:css": "prettier --write \"src/**/*.css\"",
    "format:css:check": "prettier --check \"src/**/*.css\"",
    "test:css": "npm run lint:css && npm run format:css:check",
    "clean": "rimraf target/classes/META-INF/resources/css"
  }
}
```

## CSS Dependencies

### Required CSS Dependencies
```json
{
  "devDependencies": {
    "postcss": "latest",
    "postcss-cli": "latest",
    "autoprefixer": "latest",
    "postcss-preset-env": "latest",
    "postcss-import": "latest",
    "postcss-nested": "latest",
    "postcss-custom-properties": "latest",
    "stylelint": "latest",
    "stylelint-config-standard": "latest",
    "stylelint-config-prettier": "latest",
    "stylelint-order": "latest",
    "prettier": "latest",
    "csso": "latest",
    "purgecss": "latest",
    "postcss-csso": "latest"
  }
}
```

## PostCSS Configuration

### Required PostCSS Setup
Create `postcss.config.js` in project root:

```javascript
module.exports = (ctx) => ({
  plugins: {
    'postcss-import': {},
    'postcss-nested': {},
    'postcss-custom-properties': {
      preserve: true,
      fallback: true
    },
    'postcss-preset-env': {
      stage: 1,
      features: {
        'custom-properties': false,
        'nesting-rules': false
      }
    },
    'autoprefixer': {
      grid: 'autoplace'
    },
    'csso': ctx.env === 'production' ? {} : false,
    'postcss-reporter': {
      clearReportedMessages: true
    }
  }
});
```

### Environment-Specific Configuration
```javascript
module.exports = (ctx) => {
  const isDev = ctx.env !== 'production';

  return {
    plugins: {
      'postcss-import': {},
      'postcss-nested': {},
      'postcss-custom-properties': {
        preserve: isDev,
        fallback: !isDev
      },
      'postcss-preset-env': {
        stage: isDev ? 0 : 1,
        autoprefixer: { grid: 'autoplace' }
      },
      'csso': !isDev ? { comments: false } : false
    }
  };
};
```

## Stylelint Configuration

### Required Stylelint Setup
Create `.stylelintrc.js`:

```javascript
module.exports = {
  extends: [
    'stylelint-config-standard',
    'stylelint-config-prettier'
  ],
  plugins: [
    'stylelint-order'
  ],
  rules: {
    'order/properties-alphabetical-order': true,
    'color-hex-length': 'short',
    'color-named': 'never',
    'declaration-no-important': true,
    'max-nesting-depth': 3,
    'selector-max-specificity': '0,3,0',
    'selector-class-pattern': '^[a-z][a-z0-9]*(-[a-z0-9]+)*$'
  }
};
```

## CSS Design System

### Custom Properties (CSS Variables)
```css
:root {
  /* Colors */
  --color-primary: #007bff;
  --color-secondary: #6c757d;
  --color-success: #28a745;
  --color-danger: #dc3545;
  --color-warning: #ffc107;
  --color-info: #17a2b8;

  /* Typography */
  --font-family-base: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-size-base: 1rem;
  --font-size-sm: 0.875rem;
  --font-size-lg: 1.25rem;
  --line-height-base: 1.5;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Borders */
  --border-radius: 0.25rem;
  --border-width: 1px;
  --border-color: #dee2e6;

  /* Shadows */
  --shadow-sm: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  --shadow-md: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
  --shadow-lg: 0 1rem 3rem rgba(0, 0, 0, 0.175);

  /* Transitions */
  --transition-base: all 0.2s ease-in-out;
  --transition-fast: all 0.1s ease-in-out;
  --transition-slow: all 0.3s ease-in-out;
}
```

### Dark Mode Support
```css
:root {
  --bg-primary: #ffffff;
  --text-primary: #212529;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #212529;
    --text-primary: #f8f9fa;
  }
}

[data-theme="dark"] {
  --bg-primary: #212529;
  --text-primary: #f8f9fa;
}
```

## CSS Layout Patterns

### CSS Grid
```css
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-md);
}

.grid-sidebar {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: var(--spacing-lg);
}
```

### Flexbox
```css
.flex-container {
  display: flex;
  gap: var(--spacing-md);
  align-items: center;
}

.flex-column {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}
```

### Container Queries
```css
.card {
  container-type: inline-size;
  container-name: card;
}

@container card (min-width: 400px) {
  .card-content {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
}
```

## CSS Naming Conventions

### BEM Methodology
```css
/* Block */
.button {
  display: inline-block;
  padding: var(--spacing-sm) var(--spacing-md);
}

/* Element */
.button__icon {
  margin-right: var(--spacing-xs);
}

/* Modifier */
.button--primary {
  background-color: var(--color-primary);
  color: white;
}

.button--large {
  padding: var(--spacing-md) var(--spacing-lg);
  font-size: var(--font-size-lg);
}
```

### Component Structure
```css
/* Component base */
.component-name {
  /* Layout properties */
  display: flex;
  flex-direction: column;

  /* Box model */
  margin: var(--spacing-md);
  padding: var(--spacing-md);

  /* Visual properties */
  background-color: var(--bg-primary);
  border: var(--border-width) solid var(--border-color);
  border-radius: var(--border-radius);

  /* Typography */
  font-family: var(--font-family-base);
  color: var(--text-primary);
}
```

## CSS Performance

### Performance Best Practices
* Minimize specificity (prefer classes over IDs)
* Avoid deep nesting (max 3 levels)
* Use CSS containment for isolated components
* Leverage CSS Grid/Flexbox instead of floats
* Minimize use of expensive properties (box-shadow, filter)

### CSS Containment
```css
.component {
  contain: layout style paint;
}

.isolated-section {
  contain: content;
}
```

## CSS Accessibility

### Accessible Patterns
```css
/* Focus visibility */
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* Skip to main content */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  z-index: 100;
}

.skip-link:focus {
  top: 0;
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* High contrast mode */
@media (prefers-contrast: high) {
  :root {
    --border-width: 2px;
  }
}
```

## Responsive Design

### Mobile-First Approach
```css
/* Mobile first (default) */
.container {
  width: 100%;
  padding: var(--spacing-sm);
}

/* Tablet */
@media (min-width: 768px) {
  .container {
    padding: var(--spacing-md);
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--spacing-lg);
  }
}
```

## Development Workflow

### CSS Development Cycle
1. Write CSS following modern standards
2. Run `npm run format:css` to format
3. Run `npm run lint:css:fix` to fix linting issues
4. Test responsive behavior
5. Run `npm run test:css` before committing

### Build Process
* Development: `npm run build:css:dev` (watch mode)
* Production: `npm run build:css:min` (minified)

## References

* [MDN CSS Documentation](https://developer.mozilla.org/en-US/docs/Web/CSS)
* [CSS Grid Guide](https://css-tricks.com/snippets/css/complete-guide-grid/)
* [Flexbox Guide](https://css-tricks.com/snippets/css/a-guide-to-flexbox/)
* [PostCSS Documentation](https://postcss.org/)
* [Stylelint Documentation](https://stylelint.io/)
