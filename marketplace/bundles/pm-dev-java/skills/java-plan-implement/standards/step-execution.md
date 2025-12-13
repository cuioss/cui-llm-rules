# Step Execution Patterns

How to execute steps (file paths) for Java-domain tasks.

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

## Java File Structure

Java files follow standard package and class conventions:

```java
package com.example.module;

import java.util.List;

/**
 * Class JavaDoc.
 */
public class ClassName {
    // Fields
    // Constructors
    // Methods
}
```

## Modification Patterns

### Update Import Statements

```python
# Pattern: Add import
old: "import java.util.List;"
new: "import java.util.List;\nimport java.util.Optional;"
```

Use Edit tool with precise old/new strings.

### Update Method Implementation

```python
# Pattern: Replace method body
old: """public void methodName() {
    // old implementation
}"""

new: """public void methodName() {
    // new implementation
}"""
```

### Add New Method

```python
# Pattern: Add method before class closing brace
old: "}\n// end of class"
new: """    public void newMethod() {
        // implementation
    }
}
// end of class"""
```

## Execution Flow Per Step

### 1. Read Current Content

```
Read: {step.title}
```

Parse the file to understand:
- Package declaration
- Import statements
- Class structure
- Existing methods

### 2. Plan Changes

Based on task description, identify:
- What methods to modify
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
- File still compiles
- No syntax errors
- CUI patterns followed

## Common Java Changes

### Implementation: Add Field

Steps:
1. Find field declaration section
2. Add new field with proper annotations
3. Add getter/setter if needed (Lombok may handle)

### Implementation: Add Method

Steps:
1. Find appropriate location in class
2. Add method with JavaDoc
3. Follow CUI patterns from loaded skills

### Test: Add Test Method

Steps:
1. Find test class
2. Add @Test annotated method
3. Follow JUnit 5 patterns
4. Use generators if applicable

### JavaDoc: Update Documentation

Steps:
1. Find class/method JavaDoc
2. Update description, params, returns
3. Follow CUI JavaDoc standards

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

### Compilation Error

If changes break compilation:
1. Log the issue
2. Attempt to fix
3. If still fails, mark step as failed
4. Continue to next step
