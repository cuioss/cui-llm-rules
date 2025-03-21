# DSL-Style Nested Constants Pattern

> **Note:** This document has been migrated to the standards directory. Please refer to the [DSL-Style Constants Pattern](/standards/java/dsl-style-constants.adoc) for the current version.

## Migration Notice
The detailed DSL-Style Nested Constants Pattern guide has been migrated to the standards directory in AsciiDoc format. Please refer to the following documents for the current standards:

- [DSL-Style Constants Pattern](/standards/java/dsl-style-constants.adoc)
- [Java Standards](/standards/java/README.adoc)
- [Logging Implementation Guide](/standards/logging/implementation-guide.adoc)

## Key Characteristics

1. Hierarchical Organization: Constants are organized in nested static classes, each representing a dimension or category
2. Type Safety: Each level in the hierarchy is a proper type, enabling IDE support and compile-time checks
3. Discoverable API: The structure guides users through available options via IDE auto-completion
4. Immutable: All elements are final and preferably immutable
5. Self-Documenting: The hierarchy itself documents the relationship between constants

## Implementation Guidelines

1. Use @UtilityClass for all levels to prevent instantiation
2. Make all classes and constants public static final
3. Use meaningful names for each level that represent the dimension they categorize
4. Consider using interfaces to define common behavior across similar categories

## Example Structure

```java
@UtilityClass
public final class ModuleConstants {
    @UtilityClass
    public static final class CATEGORY_A {
        @UtilityClass
        public static final class TYPE_1 {
            public static final Item CONSTANT_1 = ...;
        }
    }
}
```

## Usage Example

```java
// Instead of:
ModuleConstants.CONSTANT_1

// Use:
ModuleConstants.CATEGORY_A.TYPE_1.CONSTANT_1
```

## Common Use Cases

1. Logging Systems: Organizing messages by module, level, and component
2. Configuration: Grouping settings by feature, environment, and type
3. Error Codes: Categorizing by module, severity, and subsystem
4. Resource Bundles: Organizing by language, region, and resource type

## Benefits

1. Improved Code Organization: Clear structure for related constants
2. Better Maintainability: Easy to add new categories without changing existing code
3. Enhanced Developer Experience: IDE auto-completion guides developers
4. Type Safety: Compile-time verification of constant usage
5. Documentation: Structure itself documents relationships

## Best Practices

1. Keep hierarchy depth reasonable (3-4 levels maximum)
2. Use consistent naming conventions across all levels
3. Document the purpose of each category level
4. Consider using enums for the lowest level when appropriate
5. Maintain consistent ordering within each level
