# Issue #3: Fix NPE in UserService.findById

## Description

NullPointerException occurs when calling `UserService.findById()` with a non-existent user ID.

## Steps to Reproduce

1. Call `userService.findById("non-existent-id")`
2. Application throws NPE

## Expected Behavior

Method should return `Optional.empty()` for non-existent users.

## Actual Behavior

Method throws NullPointerException at line 45 of UserService.java.

## Acceptance Criteria

- [ ] Method returns Optional.empty() for non-existent IDs
- [ ] No NullPointerException thrown
- [ ] Existing tests still pass
- [ ] New test added for edge case

## Labels

- bug
- priority-high
