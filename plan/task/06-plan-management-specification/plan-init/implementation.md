# Implementation Init

**Purpose**: Init phase implementation for full development workflows

**Output**: 5-phase plan (init→refine→implement→verify→finalize)

**Use Cases**:
- Java implementation tasks
- JavaScript/frontend tasks
- Plugin/marketplace component tasks
- Requirements engineering with code artifacts

---

## Properties

| Property | Required | Default | Auto-Detection |
|----------|----------|---------|----------------|
| Branch | Yes | Current if feature branch | `git branch --show-current` |
| Issue | Recommended | None | Parse from branch or ask |
| Build System | Yes | Auto-detect | Scan for build files |
| Technology | Yes | Derived | From build system |
| Compatibility | No | `deprecations` | None |
| Commit Strategy | No | `fine-granular` | None |
| Finalizing | No | `pr-workflow` | None |

---

## Property Specifications

### Branch (Required)

**Detection**:
```bash
# Get current branch
git branch --show-current

# Check if on feature/fix/task branch
# Pattern: feature/*, fix/*, task/*, claude/*
```

**Logic**:
1. Get current branch name
2. If matches `feature/*`, `fix/*`, `task/*`, `claude/*` → propose current branch
3. If on `main`, `master`, `develop` → ask for target branch name

**Validation**:
- Must NOT be `main` or `master` for implementation work
- Should follow naming convention

**User Prompt** (if needed):
```
Current branch is '{branch}' (protected).
What branch should this task work on?

Suggested format: feature/{issue-id}-{short-description}
```

---

### Issue (Recommended)

**Detection Order**:
1. Command parameter: `issue=URL`
2. Parse from branch name: `feature/PROJ-123-description` → `PROJ-123`
3. Ask user if not found

**Supported Sources**:
| Source | URL Pattern | API |
|--------|-------------|-----|
| GitHub | `https://github.com/{org}/{repo}/issues/{num}` | `gh issue view` |
| GitLab | `https://gitlab.com/{org}/{repo}/-/issues/{num}` | `glab issue view` |
| Jira | `https://jira.{domain}/browse/{key}` | REST API |

**Auto-Analysis** (when URL provided):
```
Skill: cui-task-workflow:issue-analyzer

Fetch and extract:
- Title → Plan title
- Description → Overview section
- Acceptance criteria → Task acceptance criteria
- Labels → Technology hints
- Linked issues → Dependencies in references.md
```

**User Prompt** (if not detected):
```
No issue reference found. Select an option:

1. Enter issue URL
   e.g., https://github.com/org/repo/issues/123

2. Enter issue identifier
   e.g., PROJ-123

3. Skip (continue without issue reference)

Select (1-3):
```

**Follow-up** (if 1 or 2 selected):
```
Enter issue {URL|identifier}:
```

---

### Build System (Required)

**Detection via environment-detection Skill**:

Use the `builder:environment-detection` skill to detect available build systems:

```toon
from: plan-init-skill
to: environment-detection-skill
handoff_id: env-001

operation: get-build-environment

next_action: Detect available build systems
```

**Response**:
```toon
from: environment-detection-skill
to: plan-init-skill
handoff_id: env-002

status: success
available_systems: "maven,npm"
default_system: "maven"
source: detected|cached
```

**Priority Order** (from environment-detection):
- maven (1) > gradle (2) > npm (3)

**Values**:
| Value | Description | Technology |
|-------|-------------|------------|
| `maven` | Java/JVM with Maven | java |
| `gradle` | Java/JVM with Gradle | java |
| `npm` | JavaScript with npm | javascript |
| `npx` | JavaScript with npx scripts | javascript |
| `none` | No build system | none |

**User Prompt** (if multiple detected):
```
Multiple build systems detected via environment-detection:

1. maven (default - highest priority)
   → Java/JVM development

2. npm (also available)
   → JavaScript development

Select primary build system (1-2):
```

**User Prompt** (if none detected):
```
No build system detected. Select manually:

1. maven
   Java/JVM with Maven (pom.xml)

2. gradle
   Java/JVM with Gradle (build.gradle)

3. npm
   JavaScript with npm (package.json)

4. npx
   JavaScript with npx scripts

5. none
   No build system needed

Select (1-5):
```

---

### Technology (Required)

**Derived from Build System** (via environment-detection):

The `builder:environment-detection` skill provides technology mapping:

```python
technology_map = {
    "maven": "java",
    "gradle": "java",
    "npm": "javascript"
}
technology = technology_map.get(default_system, "unknown")
```

| Build System | Technology |
|--------------|------------|
| maven | java |
| gradle | java |
| npm | javascript |
| npx | javascript |
| none | none |

**Mixed Technology**: If `available_systems` contains both Java (maven/gradle) and JavaScript (npm), technology should be set to `mixed`.

**Override**: User can specify `mixed` if project has both Java and JavaScript.

**Values**:
- `java` - Java/JVM development
- `javascript` - JavaScript/TypeScript development
- `mixed` - Both Java and JavaScript
- `none` - No specific technology

**User Prompt** (when editing):
```
Select primary technology:

1. java
   Java/JVM development (Quarkus, Spring, etc.)

2. javascript
   JavaScript/TypeScript (Node.js, frontend)

3. mixed
   Both Java and JavaScript in this task

4. none
   No specific technology stack

Select (1-4):
```

---

### Compatibility (Optional)

**Default**: `deprecations`

**Values**:
| Value | Description | Version Impact |
|-------|-------------|----------------|
| `breaking` | Breaking changes allowed | Major version bump |
| `deprecations` | Deprecate old, introduce new | Minor version bump |

**Impacts**:
- Code review requirements
- Migration documentation needs
- API versioning strategy

**User Prompt** (when editing):
```
Select compatibility level:

1. deprecations (default)
   Deprecate old APIs, introduce new alongside
   → Minor version bump

2. breaking
   Allow breaking changes to existing APIs
   → Major version bump

Select (1-2):
```

---

### Commit Strategy (Optional)

**Default**: `fine-granular`

**Values**:
| Value | Description | When to Commit |
|-------|-------------|----------------|
| `fine-granular` | Commit after each task | Most traceability |
| `phase-specific` | Commit after each phase | Moderate grouping |
| `complete` | Single commit at end | Least commits |

**Recommendation**: `fine-granular` for:
- Easier rollback
- Better traceability
- Cleaner git history per feature

**User Prompt** (when editing):
```
Select commit strategy:

1. fine-granular (default, recommended)
   Commit after each completed task
   → Best traceability, easier rollback

2. phase-specific
   Commit at end of each phase
   → Moderate grouping, fewer commits

3. complete
   Single commit when all work done
   → Minimal commits, harder rollback

Select (1-3):
```

---

### Finalizing (Optional)

**Default**: `pr-workflow`

**Values**:
| Value | Description | Actions |
|-------|-------------|---------|
| `pr-workflow` | Full PR automation | Create PR, fix Sonar, request reviews |
| `manual-pr` | Create PR only | Create PR, manual follow-up |
| `commit-only` | No PR | Just commit changes |

**PR Workflow Actions** (when `pr-workflow`):
```
1. Create/update pull request
2. Run build verification
3. Execute: /pr-fix to handle issues
4. Request reviews if configured
```

**User Prompt** (when editing):
```
Select finalizing mode:

1. pr-workflow (default)
   Full automation: create PR, fix Sonar issues, request reviews
   → Handles entire PR lifecycle via /pr-fix

2. manual-pr
   Create PR only, manual follow-up
   → You handle Sonar fixes and reviews

3. commit-only
   Commit changes, no PR creation
   → For direct-to-main or local-only work

Select (1-3):
```

---

## Prompting Standard

**ALWAYS use `AskUserQuestion` tool** for all user interactions during init phase:
- Selection prompts (numbered lists)
- Free-form input requests
- Confirmation dialogs
- Property editing

This ensures consistent UX and proper conversation flow.

---

## Init Phase Workflow

### Step 1: Gather Information

**From Command Parameters**:
```
Parse parameters:
- task → Task description
- issue → Issue URL
- branch → Target branch
- type → (already determined)
```

**From Environment** (via `builder:environment-detection` skill):
```toon
from: plan-init-skill
to: environment-detection-skill
handoff_id: env-001

operation: get-build-environment

next_action: Detect available build systems
```

**Response**:
```json
{
  "available_systems": "maven,npm",
  "default_system": "maven",
  "source": "detected"
}
```

**Git State**:
```bash
git branch --show-current
git remote -v
```

**From Issue** (if URL provided):
```
Fetch issue details:
- Title, description
- Acceptance criteria
- Labels, assignees
- Linked issues
```

### Step 2: Determine Configuration

**Apply Detection Rules** (using environment-detection results):
```python
# Get build environment from environment-detection skill
env_result = environment_detection.get_build_environment()

# Derive technology from environment-detection
technology_map = {"maven": "java", "gradle": "java", "npm": "javascript"}
available = env_result["available_systems"].split(",")
default = env_result["default_system"]
technology = technology_map.get(default, "none")

# Check for mixed technology
if any(s in available for s in ["maven", "gradle"]) and "npm" in available:
    technology = "mixed"

config = {
    "type": "implementation",
    "branch": detect_branch(),
    "issue": detect_issue(),
    "build_system": default,  # from environment-detection
    "technology": technology,  # derived from environment-detection
    "compatibility": "deprecations",  # default
    "commit_strategy": "fine-granular",  # default
    "finalizing": "pr-workflow"  # default
}

missing = [k for k, v in config.items() if v is None and is_required(k)]
```

### Step 3: Present Configuration

**Display Format**:
```
## Detected Configuration

**Plan Type**: Implementation
**Branch**: feature/PROJ-123-jwt-auth ✓ (current branch)
**Issue**: [PROJ-123](https://jira.company.com/browse/PROJ-123) ✓
**Build System**: maven ✓ (pom.xml detected)
**Technology**: java ✓ (derived from maven)

**Defaults Applied**:
- Compatibility: deprecations
- Commit Strategy: fine-granular
- Finalizing: pr-workflow

**Warnings**:
- None

Proceed with this configuration? (yes/no/edit)
```

### Step 4: User Confirmation

**If user agrees** → Persist and proceed

**If user says "edit"**:
```
Which property to change?

1. Branch         - Target git branch
2. Issue          - Issue reference (URL or ID)
3. Build System   - maven | gradle | npm | npx | none
4. Technology     - java | javascript | mixed | none
5. Compatibility  - deprecations | breaking
6. Commit Strategy - fine-granular | phase-specific | complete
7. Finalizing     - pr-workflow | manual-pr | commit-only

Select (1-7):
```

**Property-Specific Prompts**:
- Properties 1-2 (Branch, Issue): Free-form text input
- Properties 3-7: Selection from predefined list (see property sections above)

**Iterate** until user confirms.

### Step 5: Persist Configuration

**Write to config.md** (see [persistence.md](../plan-files/persistence.md#file-configmd)):
```markdown
# Configuration

**Created**: {date}
**Plan Type**: implementation

---

## Build Configuration

| Property | Value |
|----------|-------|
| Technology | {technology} |
| Build System | {build_system} |

---

## Workflow Configuration

| Property | Value |
|----------|-------|
| Compatibility | {compatibility} |
| Commit Strategy | {commit_strategy} |
| Finalizing | {finalizing} |

---

## Context

| Property | Value |
|----------|-------|
| Branch | {branch} |
| Issue | {issue_reference} |

---

**Generated by**: plan-init skill
```

**Write to plan.md** (tasks-only):
```markdown
# Task Plan: {task_title}

**Configuration**: See [config.md](./config.md)
**References**: See [references.md](./references.md)

**Status**: in_progress
**Current Phase**: init
**Current Task**: task-1
```

**Write to references.md**:
```markdown
## Issue and Branch

**Issue**: [{issue_id}: {issue_title}]({issue_url})
**Branch**: `{branch}`
**Base Branch**: `main`
```

**Transition**: Move to `refine` phase.

---

## Init Phase Tasks

```markdown
## Phase: init (in_progress)

### Task 1: Detect Environment
**Status**: [ ]
**Goal**: Gather information from command parameters and environment

**Checklist**:
- [ ] Check current git branch
- [ ] Detect build system via `builder:environment-detection` skill
- [ ] Parse issue from parameters or branch name
- [ ] Determine technology stack from environment-detection results

### Task 2: Fetch Issue Details
**Status**: [ ]
**Goal**: Retrieve and analyze issue information (if URL provided)

**Checklist**:
- [ ] Fetch issue title and description
- [ ] Extract acceptance criteria
- [ ] Identify related issues/dependencies
- [ ] Pre-populate plan with issue content

### Task 3: Validate Configuration
**Status**: [ ]
**Goal**: Ensure configuration is complete and valid

**Checklist**:
- [ ] Verify branch is not main/master
- [ ] Confirm issue reference (or explicit skip)
- [ ] Validate environment-detection results
- [ ] Check for conflicting settings

### Task 4: User Confirmation
**Status**: [ ]
**Goal**: Present configuration and get user approval

**Checklist**:
- [ ] Display detected configuration (from environment-detection)
- [ ] Highlight warnings or recommendations
- [ ] Allow property overrides
- [ ] Confirm final configuration

### Task 5: Persist and Transition
**Status**: [ ]
**Goal**: Save configuration and move to refine phase

**Checklist**:
- [ ] Write config.md with build and workflow configuration
- [ ] Write plan.md (tasks-only)
- [ ] Update references.md with issue/branch
- [ ] Transition to refine phase
```

---

## Init Output: Phase Structure

This init produces the complete phase structure for the plan. When init completes, the following phases exist in plan.md:

```markdown
## Phase Progress Table

| Phase | Status | Tasks | Completed |
|-------|--------|-------|-----------|
| init | in_progress | 5 | 0 |
| refine | pending | 3 | 0 |
| implement | pending | {dynamic} | 0 |
| verify | pending | 4 | 0 |
| finalize | pending | 3 | 0 |

---

## Phase: init (in_progress)

### Task 1: Detect Environment
**Status**: [ ]
**Goal**: Gather information from command parameters and environment

**Checklist**:
- [ ] Check current git branch
- [ ] Detect build system via `builder:environment-detection` skill
- [ ] Parse issue from parameters or branch name
- [ ] Determine technology stack from environment-detection results

### Task 2: Fetch Issue Details
**Status**: [ ]
**Goal**: Retrieve and analyze issue information

**Checklist**:
- [ ] Fetch issue title and description
- [ ] Extract acceptance criteria
- [ ] Identify related issues/dependencies
- [ ] Pre-populate plan with issue content

### Task 3: Validate Configuration
**Status**: [ ]
**Goal**: Ensure configuration is complete and valid

**Checklist**:
- [ ] Verify branch is not main/master
- [ ] Confirm issue reference (or explicit skip)
- [ ] Validate environment-detection results

### Task 4: User Confirmation
**Status**: [ ]
**Goal**: Present configuration and get user approval

**Checklist**:
- [ ] Display detected configuration (from environment-detection)
- [ ] Allow property overrides
- [ ] Confirm final configuration

### Task 5: Persist and Transition
**Status**: [ ]
**Goal**: Save configuration and move to refine phase

**Checklist**:
- [ ] Write config.md with build and workflow configuration
- [ ] Write plan.md (tasks-only)
- [ ] Update references.md with issue/branch
- [ ] Transition to refine phase

---

## Phase: refine (pending)

### Task 1: Analyze Requirements
**Status**: [ ]
**Goal**: Break down task into implementable units

**Checklist**:
- [ ] Review issue requirements
- [ ] Identify implementation components
- [ ] Define acceptance criteria per task

### Task 2: Plan Implementation Tasks
**Status**: [ ]
**Goal**: Create detailed task list for implement phase

**Checklist**:
- [ ] Generate implementation tasks
- [ ] Order by dependencies
- [ ] Estimate complexity

### Task 3: Identify Documentation Needs
**Status**: [ ]
**Goal**: Determine ADRs and interfaces needed

**Checklist**:
- [ ] Check if ADR needed for architectural decisions
- [ ] Check if interface specs needed
- [ ] Add references to references.md

---

## Phase: implement (pending)

{Tasks generated dynamically based on refine phase output}

**Template per task**:
### Task N: {Task Title}
**Status**: [ ]
**Goal**: {Goal description}

**Acceptance Criteria**:
- {Criterion 1}
- {Criterion 2}

**Checklist**:
- [ ] {Implementation step 1}
- [ ] {Implementation step 2}
- [ ] Write/update tests
- [ ] Verify build passes

**Note**: Technology is defined in config.md (use `read-config` operation to access)

---

## Phase: verify (pending)

### Task 1: Run Full Build
**Status**: [ ]
**Goal**: Ensure all code compiles and tests pass

**Checklist**:
- [ ] Delegate to `maven-builder` or `npm-builder` agent
- [ ] Fix any failures
- [ ] Verify coverage thresholds

### Task 2: Code Quality Check
**Status**: [ ]
**Goal**: Verify code meets quality standards

**Checklist**:
- [ ] Run linter/static analysis
- [ ] Fix violations
- [ ] Review Sonar issues (if applicable)

### Task 3: Manual Testing
**Status**: [ ]
**Goal**: Verify functionality works as expected

**Checklist**:
- [ ] Test happy path scenarios
- [ ] Test edge cases
- [ ] Document test results

### Task 4: Documentation Review
**Status**: [ ]
**Goal**: Ensure documentation is complete

**Checklist**:
- [ ] Verify JavaDoc/JSDoc complete
- [ ] Update README if needed
- [ ] Check ADR/interface docs

---

## Phase: finalize (pending)

### Task 1: Commit Changes
**Status**: [ ]
**Goal**: Create final commit(s) per commit strategy

**Checklist**:
- [ ] Stage all changes
- [ ] Create commit with descriptive message
- [ ] Push to remote branch

### Task 2: Create/Update Pull Request
**Status**: [ ]
**Goal**: Prepare PR for review

**Checklist**:
- [ ] Create PR with summary
- [ ] Link to issue
- [ ] Add reviewers

### Task 3: PR Workflow
**Status**: [ ]
**Goal**: Handle PR feedback and fixes

**Checklist**:
- [ ] Execute /pr-fix if configured
- [ ] Address review comments
- [ ] Merge when approved
```

---

## Example: config.md

```markdown
# Configuration

**Created**: 2025-01-15
**Plan Type**: implementation

---

## Build Configuration

| Property | Value |
|----------|-------|
| Technology | java |
| Build System | maven |

---

## Workflow Configuration

| Property | Value |
|----------|-------|
| Compatibility | deprecations |
| Commit Strategy | fine-granular |
| Finalizing | pr-workflow |

---

## Context

| Property | Value |
|----------|-------|
| Branch | feature/PROJ-123-jwt-authentication |
| Issue | [PROJ-123](https://jira.company.com/browse/PROJ-123) |

---

**Generated by**: plan-init skill
```

---

## Related

- [Handoff Protocol](handoff.md) - TOON incoming/outgoing specifications
- [Plan Types](../plan-types.md) - Init phase router
- [Simple Init](simple.md) - Lightweight alternative (3 phases)
- [Refine Phase](../plan-refine/refine.md) - Refine phase specification
- [Implement Phase](../plan-implement/implement.md) - Implement phase specification
- [Verify Phase](../plan-verify/verify.md) - Verify phase specification
- [Finalize Phase](../plan-finalize/finalize.md) - Finalize phase specification
- [Persistence](../plan-files/persistence.md) - File format specifications
- [Templates & Workflow](../templates-workflow.md) - Phase workflow details
- [environment-detection Skill](../../../../marketplace/bundles/builder/skills/environment-detection/SKILL.md) - Build system detection
