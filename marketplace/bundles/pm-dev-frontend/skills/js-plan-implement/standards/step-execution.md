# Step Execution Patterns

How to execute steps (file paths) for JavaScript-domain tasks.

## Step Types

Each step `title` is a file path. Determine operation type from:
1. Task description
2. File existence
3. Deliverable guidance

| File Exists | Task Intent | Operation |
|-------------|-------------|-----------|
| Yes | Update | Modify existing file |
| Yes | Replace | Overwrite file |
| No | Create | Create new file |
| Yes | Delete | Remove file |

## JavaScript File Structure

JavaScript files follow ES module conventions:

```javascript
/**
 * Module JSDoc.
 * @module module-name
 */

import { dependency } from './dependency.js';

/**
 * Function JSDoc.
 * @param {string} param - Parameter description
 * @returns {boolean} Return description
 */
export function functionName(param) {
    // implementation
}

export default class ClassName {
    // class implementation
}
```

## Modification Patterns

### Update Import Statements

```python
# Pattern: Add import
old: "import { dependency } from './dependency.js';"
new: "import { dependency } from './dependency.js';\nimport { newDep } from './new-dep.js';"
```

Use Edit tool with precise old/new strings.

### Update Function Implementation

```python
# Pattern: Replace function body
old: """export function functionName(param) {
    // old implementation
}"""

new: """export function functionName(param) {
    // new implementation
}"""
```

### Add New Export

```python
# Pattern: Add export at end of file
old: "// end of module"
new: """export function newFunction() {
    // implementation
}

// end of module"""
```

## Execution Flow Per Step

### 1. Read Current Content

```
Read: {step.title}
```

Parse the file to understand:
- Import statements
- Export structure
- Function/class definitions
- JSDoc comments

### 2. Plan Changes

Based on task description, identify:
- What functions to modify
- What imports to add
- What patterns to apply (from loaded skills)

### 3. Apply Changes

Use Edit tool for surgical changes:

```
Edit:
  file_path: {step.title}
  old_string: {exact text to replace}
  new_string: {replacement text}
```

**Prefer multiple small edits over one large write.**

### 4. Verify Changes

After editing, optionally verify:
- File still parses
- No syntax errors
- CUI patterns followed

## Common JavaScript Changes

### Implementation: Add Function

Steps:
1. Find appropriate location in module
2. Add function with JSDoc
3. Add export if needed
4. Follow CUI patterns from loaded skills

### Implementation: Update Web Component

Steps:
1. Find component class
2. Update render method or lifecycle
3. Update styles if needed
4. Follow CUI web component patterns

### Test: Add Test

Steps:
1. Find test file
2. Add describe/it blocks
3. Follow Jest patterns
4. Use proper assertions

### JSDoc: Update Documentation

Steps:
1. Find function/class JSDoc
2. Update description, params, returns
3. Follow CUI JSDoc standards

## Error Recovery

### Parse Error

If file cannot be parsed:
1. Log error with file path
2. Skip step
3. Mark step as failed
4. Continue to next step

### Edit Conflict

If old_string not found:
1. Read file again (may have changed)
2. Adjust old_string
3. Retry edit
4. If still fails, log and continue

### Lint Error

If changes break linting:
1. Log the issue
2. Attempt to fix
3. If still fails, mark step as failed
4. Continue to next step
