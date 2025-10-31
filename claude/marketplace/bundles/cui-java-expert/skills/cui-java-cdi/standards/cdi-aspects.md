# CDI Aspects and Best Practices

## Purpose
This document defines CDI (Contexts and Dependency Injection) standards and best practices for Quarkus applications within CUI projects.

## References
* [CDI 2.0 Specification](https://docs.oracle.com/javaee/7/tutorial/cdi-basic.htm)
* [Quarkus CDI Guide](https://quarkus.io/guides/cdi)
* [Quarkus CDI Reference](https://quarkus.io/guides/cdi-reference)

## Constructor Injection in CDI

### Mandatory Standard: Use Constructor Injection

**REQUIRED**: Always use constructor injection instead of field injection in CDI beans.

For foundational constructor injection principles (immutability, testability, fail-fast behavior), see **cui-java-core** skill (invoked in SKILL.md Step 1).

This section focuses on **CDI-specific** constructor injection rules and patterns

## CDI Constructor Injection Rules

### Automatic @Inject Detection

**Important**: The `@Inject` annotation is **NOT required** for constructor injection in specific cases.

#### Single Constructor Rule

When a CDI bean has exactly **one constructor**, CDI automatically treats it as the injection point:

```java
@ApplicationScoped
public class OrderService {

    private final PaymentService paymentService;
    private final InventoryService inventoryService;

    // No @Inject needed - only one constructor
    public OrderService(PaymentService paymentService,
                       InventoryService inventoryService) {
        this.paymentService = paymentService;
        this.inventoryService = inventoryService;
    }
}
```

#### Multiple Constructors Rule

When a CDI bean has **multiple constructors**, you **MUST** explicitly mark the injection constructor with `@Inject`:

```java
@ApplicationScoped
public class ConfigurableService {

    private final DatabaseService databaseService;
    private final String configValue;

    // Default constructor
    public ConfigurableService() {
        this.databaseService = null;
        this.configValue = "default";
    }

    @Inject  // REQUIRED - multiple constructors exist
    public ConfigurableService(DatabaseService databaseService,
                              @ConfigProperty(name = "app.config") String configValue) {
        this.databaseService = databaseService;
        this.configValue = configValue;
    }
}
```

#### No-Args Constructor

If only a no-args constructor exists, CDI uses it automatically (no injection occurs):

```java
@ApplicationScoped
public class StatelessService {

    // CDI uses this automatically - no dependencies injected
    public StatelessService() {
        // Initialize without dependencies
    }
}
```

### Best Practices Summary

#### ✅ Recommended Patterns

1. **Single Constructor with Dependencies**
```java
@ApplicationScoped
public class BookingService {
    private final ReservationRepository repository;
    private final EmailService emailService;

    // Perfect - single constructor, no @Inject needed
    public BookingService(ReservationRepository repository, EmailService emailService) {
        this.repository = repository;
        this.emailService = emailService;
    }
}
```

2. **Final Fields for Immutability**
```java
private final UserService userService;  // ✅ Final field
private final AuditService auditService;  // ✅ Final field
```

3. **Constructor Parameter Validation**
```java
public PaymentService(PaymentGateway gateway, AuditLogger logger) {
    this.gateway = Objects.requireNonNull(gateway, "PaymentGateway cannot be null");
    this.logger = Objects.requireNonNull(logger, "AuditLogger cannot be null");
}
```

#### ❌ Anti-Patterns to Avoid

1. **Field Injection**
```java
@Inject
private UserService userService;  // ❌ Avoid field injection
```

2. **Setter Injection**
```java
@Inject
public void setUserService(UserService userService) {  // ❌ Avoid setter injection
    this.userService = userService;
}
```

3. **Multiple Constructors without @Inject**
```java
public ServiceClass() { }  // ❌ Ambiguous - CDI won't know which to use
public ServiceClass(Dependency dep) { }
```

## CDI Scopes and Lifecycle

### Common CDI Scopes

#### @ApplicationScoped
* Single instance per application
* Use for stateless services
* Most common scope for business logic

```java
@ApplicationScoped
public class UserService {
    // Singleton across application
}
```

#### @RequestScoped
* New instance per HTTP request
* Automatically disposed after request
* Use for request-specific data

```java
@RequestScoped
public class RequestContext {
    // New instance per HTTP request
}
```

#### @Singleton
* Single instance like @ApplicationScoped
* Eager initialization by default
* Use sparingly, prefer @ApplicationScoped

## Optional Dependencies

### Using Instance<T> for Optional Injection

When a dependency might not be available, use `Instance<T>`:

```java
@ApplicationScoped
public class NotificationService {

    private final EmailService emailService;
    private final SmsService smsService;  // May be null

    public NotificationService(EmailService emailService,
                             Instance<SmsService> smsServiceInstance) {
        this.emailService = emailService;
        this.smsService = smsServiceInstance.isResolvable() ?
                         smsServiceInstance.get() : null;
    }

    public void sendNotification(String message) {
        emailService.send(message);  // Always available

        if (smsService != null) {    // Optional
            smsService.send(message);
        }
    }
}
```

## CDI Producer Methods

### Producer Method Scopes and Null Returns

**CRITICAL**: CDI has strict rules about producer methods returning null based on their scope.

#### @Dependent Scope Producers (Allows null)

Use `@Dependent` scope when the producer method might return null:

```java
@ApplicationScoped
public class ServletObjectsProducer {

    @Produces
    @CuiServletObjects
    @Dependent  // ✅ REQUIRED for null returns
    public HttpServletRequest produceHttpServletRequest() {
        // Can safely return null outside REST context
        return getHttpServletRequest().orElse(null);
    }

    private Optional<HttpServletRequest> getHttpServletRequest() {
        ResteasyProviderFactory factory = ResteasyProviderFactory.getInstance();
        if (factory == null) {
            return Optional.empty();
        }
        return Optional.ofNullable(factory.getContextData(HttpServletRequest.class));
    }
}
```

#### Normal Scoped Producers (Cannot return null)

Normal scoped producers (`@RequestScoped`, `@SessionScoped`, etc.) **MUST NOT** return null:

```java
@ApplicationScoped
public class BadProducer {

    @Produces
    @RequestScoped  // ❌ ILLEGAL - will throw IllegalProductException
    public SomeService createService() {
        return null;  // ❌ CDI will throw exception at runtime
    }
}
```

**Error**: `jakarta.enterprise.inject.IllegalProductException: Normal scoped producer method may not return null`

#### Why This Restriction Exists

Normal scoped beans use CDI client proxies:
- Proxies require a target object to delegate method calls
- Null cannot be proxied - no object to delegate to
- CDI enforces this at runtime to prevent proxy failures

### Optional<T> in Producer Methods - NOT RECOMMENDED

**AVOID**: Returning `Optional<T>` from producer methods is not considered CDI best practice:

```java
@ApplicationScoped
public class NotRecommendedProducer {

    @Produces
    @RequestScoped
    public Optional<SomeService> createOptionalService() {  // ❌ Not recommended
        return Optional.ofNullable(someService);
    }
}
```

**Problems with Optional Producers:**
1. **Goes against CDI design philosophy** - CDI expects concrete bean instances
2. **Adds unnecessary complexity** - Consumers must handle Optional unwrapping
3. **Performance overhead** - Creates additional wrapper objects
4. **Type safety issues** - Makes injection points less clear

### Recommended Patterns for Optional Dependencies

#### 1. Use Instance<T> at Injection Points

```java
@ApplicationScoped
public class MyService {

    private final OptionalService optionalService;

    public MyService(Instance<OptionalService> optionalServiceInstance) {
        this.optionalService = optionalServiceInstance.isResolvable() ?
                              optionalServiceInstance.get() : null;
    }
}
```

#### 2. Use @Dependent Scope with Null Returns

```java
@Produces
@Dependent  // Allows null returns
public OptionalService createOptionalService() {
    return serviceAvailable() ? new OptionalService() : null;
}
```

#### 3. Use Null Object Pattern

```java
@Produces
@RequestScoped
public NotificationService createNotificationService() {
    return notificationEnabled ?
           new EmailNotificationService() :
           new NoOpNotificationService();  // Never null
}
```

#### 4. Use Conditional Bean Creation

```java
@ApplicationScoped
public class ConditionalProducer {

    @Produces
    @ConditionalOnProperty("feature.enabled")
    public FeatureService createFeatureService() {
        return new FeatureService();
    }
}
```

### Producer Method Best Practices

#### ✅ Recommended Patterns

1. **Use @Dependent for nullable producers**
```java
@Produces
@Dependent
public HttpServletRequest produceRequest() {
    return getRequest().orElse(null);  // ✅ Safe with @Dependent
}
```

2. **Use Internal Optional with concrete returns**
```java
@Produces
@RequestScoped
public DatabaseService createDatabaseService() {
    return getDatabaseService().orElse(new DefaultDatabaseService());
}

private Optional<DatabaseService> getDatabaseService() {
    // Internal logic with Optional for null safety
}
```

3. **Clear producer method names**
```java
@Produces
@Named("primary")
public PaymentGateway createPrimaryPaymentGateway() {
    return new StripePaymentGateway();
}
```

#### ❌ Anti-Patterns to Avoid

1. **Normal scoped producers returning null**
```java
@Produces
@RequestScoped
public SomeService createService() {
    return null;  // ❌ IllegalProductException
}
```

2. **Returning Optional from producers**
```java
@Produces
@RequestScoped
public Optional<SomeService> createOptionalService() {  // ❌ Not recommended
    return Optional.ofNullable(service);
}
```

3. **Producer methods without clear scope**
```java
@Produces
// ❌ Missing scope - defaults to @Dependent but unclear intent
public SomeService createService() {
    return new SomeService();
}
```

### Contract-Based Injection

**Preferred**: When dependencies are guaranteed by architectural contract, use direct injection:

```java
@ApplicationScoped
public class OrderProcessor {

    private final PaymentService paymentService;  // Guaranteed by contract

    // Contract ensures PaymentService is always available
    public OrderProcessor(PaymentService paymentService) {
        this.paymentService = paymentService;  // No null check needed
    }
}
```

## Error Handling and Troubleshooting

### Common CDI Injection Issues

#### Unsatisfied Dependencies
**Problem**: `UnsatisfiedResolutionException`
**Solution**: Ensure the dependency is a CDI bean with appropriate scope

#### Ambiguous Dependencies
**Problem**: `AmbiguousResolutionException`
**Solution**: Use qualifiers to distinguish between implementations

```java
@ApplicationScoped
public class PaymentService {

    public PaymentService(@Named("primary") PaymentGateway gateway) {
        // Uses specifically qualified implementation
    }
}
```

#### Circular Dependencies
**Problem**: `DeploymentException` due to circular references
**Solution**: Refactor architecture or use `Instance<T>` for lazy initialization

## Summary

### Key Rules

1. **Always use constructor injection** - never field or setter injection
2. **Single constructor doesn't need @Inject** - CDI detects automatically
3. **Multiple constructors require @Inject** - mark the injection constructor
4. **Make injected fields final** - ensures immutability
5. **Use Instance<T> for optional dependencies** - when beans might not exist
6. **Trust the contract** - no null checks for guaranteed dependencies

### Benefits

* **Type Safety**: Compile-time dependency validation
* **Testability**: Easy unit testing without CDI container
* **Performance**: No reflection overhead for dependency access
* **Maintainability**: Clear dependency relationships
* **Reliability**: Fail-fast behavior for missing dependencies
