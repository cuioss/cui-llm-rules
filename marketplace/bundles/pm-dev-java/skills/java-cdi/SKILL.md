---
name: java-cdi
description: Core CDI patterns including constructor injection, scopes, producers, and container configuration
allowed-tools: [Read, Edit, Write, Bash, Grep, Glob]
---

# Java CDI Skill

Core CDI (Contexts and Dependency Injection) standards applicable to any CDI container. This skill covers dependency injection patterns, scopes, and container configuration.

## Prerequisites

This skill applies to Jakarta CDI projects:
- `jakarta.inject:jakarta.inject-api`
- `jakarta.enterprise:jakarta.enterprise.cdi-api`

## Workflow

### Step 1: Load CDI Aspects

**CRITICAL**: Load this standard for any CDI work.

```
Read: standards/cdi-aspects.md
```

This provides foundational rules for:
- Constructor injection (mandatory)
- Scope selection
- Producer methods
- Optional dependencies with Instance<T>

### Step 2: Load Additional Standards (As Needed)

**Security Standards** (load for security work):
```
Read: standards/cdi-security.md
```

Use when: Implementing security patterns or secure configuration.

## Key Rules Summary

### Constructor Injection (Mandatory)
```java
// CORRECT - Constructor injection
@ApplicationScoped
public class OrderService {
    private final PaymentService paymentService;
    private final InventoryService inventoryService;

    // No @Inject needed with single constructor
    public OrderService(PaymentService paymentService,
                       InventoryService inventoryService) {
        this.paymentService = paymentService;
        this.inventoryService = inventoryService;
    }
}

// WRONG - Field injection
@ApplicationScoped
public class OrderService {
    @Inject
    private PaymentService paymentService;  // FORBIDDEN
}
```

### Scope Selection
```java
// Application-wide singleton
@ApplicationScoped
public class ConfigurationService { }

// Request-scoped (HTTP request lifecycle)
@RequestScoped
public class RequestContext { }

// Dependent (new instance per injection)
@Dependent
public class HelperService { }
```

### Optional Dependencies
```java
@ApplicationScoped
public class NotificationService {
    private final Instance<EmailService> emailService;

    public NotificationService(Instance<EmailService> emailService) {
        this.emailService = emailService;
    }

    public void notify(String message) {
        if (emailService.isResolvable()) {
            emailService.get().send(message);
        }
    }
}
```

## Related Skills

- `pm-dev-java:java-cdi-quarkus` - Quarkus-specific CDI patterns
- `pm-dev-java:java-core` - Core Java patterns
- `pm-dev-java:junit-core` - CDI testing patterns

## Standards Reference

| Standard | Purpose |
|----------|---------|
| cdi-aspects.md | Constructor injection, scopes, producers |
| cdi-security.md | Security patterns for CDI applications |

**Note**: For container/Docker configuration, see `pm-dev-java:java-cdi-quarkus` skill (container.md).
