# Refactoring Triggers and Detection Criteria

Standards for identifying when to apply refactoring actions in Java codebases.

## Purpose

This document defines WHEN to apply specific refactoring patterns by identifying code violations and triggering conditions. It provides systematic detection criteria for standards violations.

## Standards Violation Detection

This section defines when and how to identify violations of Java coding standards and what actions to take for each violation type.

### When to Refactor Code Organization

**Triggers for Action**: Apply code organization refactoring when:

**Package Structure Violations**: Non-standard package names or layer-based organization detected
- **Action Required**: Restructure to feature-based packages per Package Structure Standards
- **Standards Reference**: Package organization follows feature-based structure (not layer-based like controller/service/repository)

**Class Structure Violations**: Single Responsibility Principle violations or inappropriate access modifiers
- **Action Required**: Split classes or adjust access modifiers per Class Structure Standards
- **Detection**: Classes with multiple unrelated responsibilities, god classes, classes mixing concerns

**Large Classes**: Classes exceeding reasonable size limits
- **Action Required**: Extract functionality into focused classes following SRP
- **Detection**: Classes > 500 lines, classes with too many methods, classes handling multiple domains

### When to Refactor Method Design

**Triggers for Action**: Apply method design refactoring when:

**Long Methods**: Methods significantly exceeding 50 lines (guideline)
- **Action Required**: Extract methods per Method Design Standards
- **Guideline**: Prefer methods under 50 lines for better readability and maintainability
- **Detection**: Methods with multiple levels of nesting, methods doing multiple things
- **Note**: 50 lines is a guideline, not a hard rule - focus on keeping methods focused on a single responsibility

**High Cyclomatic Complexity**: Methods with complexity >15 (SonarQube default)
- **Action Required**: Simplify logic and extract sub-methods
- **Detection**: Use static analysis tools, count decision points (if, for, while, case, &&, ||)

**Too Many Parameters**: Methods with 3+ parameters without parameter objects
- **Action Required**: Create parameter objects per Parameter Objects Standards
- **Exception**: Only when parameters represent cohesive concepts
- **Detection**: Methods with long parameter lists, methods with similar parameter groups

**Command-Query Separation Violations**: Methods that both query and modify state
- **Action Required**: Separate into command and query methods per Method Design Standards
- **Detection**: Methods that return values AND modify state, getters with side effects

### When to Fix Null Safety Violations

**Triggers for Action**: Apply null safety fixes when:

**Missing @NonNull Annotations**: Public API methods lack null safety documentation
- **Action Required**: Add annotations per @NonNull Annotations Standards
- **Implementation**: Ensure methods guarantee non-null returns per Implementation Requirements
- **Detection**: Public methods without @NonNull annotations, package-info.java missing @NullMarked

**Inconsistent API Contracts**: Mix of nullable returns and Optional usage
- **Action Required**: Choose consistent pattern per API Return Type Guidelines
- **Standards**: Use @NonNull for guaranteed results, Optional<T> for potential absence
- **Detection**: Some methods return null, others return Optional for same scenarios

**Manual Enforcement Gaps**: @NonNull methods that can return null
- **Action Required**: Fix implementations to guarantee non-null returns
- **Testing**: Add tests per Implementation Requirements
- **Detection**: Methods annotated @NonNull but with code paths returning null

### When to Fix Naming Convention Violations

**Triggers for Action**: Apply naming fixes when:

**Poor Naming Practices**: Unclear abbreviations or non-descriptive names detected
- **Action Required**: Apply naming improvements per Naming Conventions Standards
- **Focus**: Use meaningful and descriptive names following Java standards
- **Detection**: Single-letter variables (except loop counters), unclear abbreviations, generic names like "data", "info", "manager"

### When to Fix Exception Handling Issues

**Triggers for Action**: Apply exception handling fixes when:

**Generic Exception Catching**: `catch (Exception e)` or `catch (RuntimeException e)` detected
- **Action Required**: Use specific exceptions per Exception Handling Standards
- **Detection**: Catch blocks for generic Exception or RuntimeException types

**Missing Error Messages**: Exceptions without meaningful messages
- **Action Required**: Add descriptive error messages per standards
- **Detection**: `throw new Exception()` without message, generic messages like "Error"

**Inappropriate Exception Types**: Wrong exception types for the situation
- **Action Required**: Use checked exceptions for recoverable conditions, unchecked for programming errors
- **Detection**: RuntimeException for recoverable conditions, checked exceptions for programming errors

**Catch and Rethrow Anti-Pattern**: Catching and throwing the same or very similar exception
- **Action Required**: Remove unnecessary catch blocks or add meaningful context per Exception Handling Standards
- **Detection**: Catch blocks that immediately rethrow same exception type

### When to Adopt Modern Java Features

**Triggers for Action**: Apply modern Java feature adoption when:

**Legacy Switch Statements**: Classic switch statements with breaks detected
- **Action Required**: Convert to switch expressions per Switch Expressions Standards
- **Detection**: Switch statements with break keywords, fall-through cases

**Verbose Object Creation**: Manual data classes without records
- **Action Required**: Replace with records per Records Standards
- **Detection**: Classes with only fields, constructor, getters, equals, hashCode, toString

**Manual Stream Operations**: Imperative loops that could use streams
- **Action Required**: Simplify with streams per Stream Processing Standards
- **Detection**: Loops with filters, maps, or accumulations that could be replaced with streams
- **Exception**: Simple loops where streams would reduce readability

### When to Remove Unused Code

**Triggers for Action**: Apply unused code removal when:

**Unused Private Elements**: Private fields, methods, or variables never accessed
- **Action Required**: Remove after verification per detection strategy below
- **Safety Check**: Ensure no framework dependencies or reflection usage
- **Detection**: Use IDE warnings, static analysis tools

**Dead Code Detection**: Code that is never executed or called
- **Action Required**: Request user approval before removal
- **Process**: Follow user consultation protocol below
- **Detection**: Unreachable code, methods never called

#### Detection Strategy

1. Use IDE warnings and inspections to identify unused elements
2. Leverage static analysis tools (SonarQube, SpotBugs)
3. Manual code review for systematic identification
4. Build tool analysis with Maven/Gradle plugins

#### User Consultation Protocol

When unused methods are detected, MUST:

1. Document all findings with locations and signatures
2. Categorize by visibility (private, package-private, protected, public)
3. Ask user for guidance with context and potential impact
4. Wait for explicit approval before removing any methods
5. Remove approved unused code in focused commits

#### Special Considerations

Do NOT remove when:

- Framework dependencies may require "unused" methods (Spring, JPA, etc.)
- Methods may be called via reflection
- Private fields required for serialization frameworks
- Code prepared for upcoming features
- Public/protected methods needed for backward compatibility

### When to Apply Lombok Integration

**Triggers for Action**: Apply Lombok integration when:

**Inheritance Anti-Patterns**: Classes extending when they should delegate
- **Action Required**: Replace with composition and `@Delegate` per Lombok Standards
- **Detection**: Deep inheritance hierarchies, classes extending just to reuse utility methods

**Manual Builder Patterns**: Verbose builder implementations detected
- **Action Required**: Replace with `@Builder` per Lombok Standards
- **Detection**: Manual builder classes with fluent APIs, builder classes with many setters

**Boilerplate Immutable Objects**: Manual equals/hashCode/toString implementations
- **Action Required**: Replace with `@Value` per Lombok Standards
- **Detection**: Classes with manual implementations of equals, hashCode, toString for simple data carriers

### When to Enforce Documentation Standards

**Triggers for Action**: Apply documentation fixes when:

**Missing Javadoc**: Public APIs without proper documentation
- **Action Required**: Add documentation per Javadoc Standards
- **Detection**: Public classes/methods without Javadoc, missing @param/@return tags

**Outdated Documentation**: Comments not reflecting current code behavior
- **Action Required**: Update documentation to match refactored code
- **Detection**: Comments mentioning non-existent parameters, outdated behavior descriptions

**Redundant Comments**: Comments explaining obvious code
- **Action Required**: Remove unnecessary comments, add meaningful ones for complex logic
- **Detection**: Comments that just repeat method name, obvious comments like "// increment i"

## Related Standards
- maintenance-prioritization.md - How to prioritize violations
- compliance-checklist.md - How to verify fixes are complete
