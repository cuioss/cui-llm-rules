---
name: maven-antipattern-test
description: Test agent with Maven calls (not maven-builder)
tools: [Read, Bash]
---

# Test Agent - Maven Anti-Pattern

## Step 1: Read POM file

Use Read tool:
```
Read: pom.xml
```

## Step 2: Run Maven build

Use Bash tool:
```
Bash: ./mvnw clean install
```

This is an anti-pattern - only maven-builder agent should call Maven directly.
