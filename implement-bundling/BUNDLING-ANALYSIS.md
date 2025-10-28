# Claude Marketplace Bundling Analysis

**Date**: 2025-10-28
**Purpose**: Analyze command/agent/skill dependencies and recommend plugin bundling strategy

---

## Current Dependency Map

### Commands → Agents Dependencies

| Command | Depends On Agents | Frequency |
|---------|------------------|-----------|
| `implement-task` | task-reviewer, task-breakdown-agent, task-executor, maven-project-builder, commit-changes | Core workflow |
| `handle-pull-request` | pr-review-responder, pr-quality-fixer, maven-project-builder, commit-changes | Core workflow |
| `build-and-verify` | maven-project-builder, commit-changes | Utility |
| `fix-intellij-diagnostics` | maven-project-builder, commit-changes | Utility |
| `review-technical-docs` | general-purpose (Explore), commit-changes | Documentation |

### Agents → Agents Dependencies

| Agent | Depends On Agents | Frequency |
|-------|------------------|-----------|
| `task-executor` | maven-project-builder, commit-changes | High |
| `pr-quality-fixer` | maven-project-builder, commit-changes | High |
| `pr-review-responder` | maven-project-builder, commit-changes | High |
| `task-reviewer` | research-best-practices | Medium |

### Agents → Skills Dependencies

| Agent | Depends On Skills | Frequency |
|-------|------------------|-----------|
| `task-executor` | cui-java-core, cui-java-unit-testing, cui-javadoc | High |
| `pr-quality-fixer` | cui-java-unit-testing | High |
| `maven-project-builder` | cui-javadoc | High |
| `asciidoc-reviewer` | cui-documentation | High |

---

## Identified Patterns

### Pattern 1: Build + Commit Core Services
**Components**: `maven-project-builder` + `commit-changes`

**Used Together By**:
- task-executor
- pr-quality-fixer
- pr-review-responder
- build-and-verify command
- fix-intellij-diagnostics command
- handle-pull-request command

**Co-change Frequency**: ALWAYS (100% correlation)

**Functional Cohesion**: HIGH
- Both are infrastructure services
- Always used sequentially (build → verify → commit)
- Shared purpose: Project quality gates

**Recommendation**: ✅ **STRONG CANDIDATE FOR BUNDLING**

---

### Pattern 2: Issue/Task Implementation Workflow
**Components**: `task-reviewer` + `task-breakdown-agent` + `task-executor`

**Used Together By**:
- implement-task command (orchestrates all three)

**Co-change Frequency**: HIGH (always deployed as complete workflow)

**Functional Cohesion**: HIGH
- Complete issue implementation lifecycle
- Sequential workflow: review → plan → execute
- Single business function: "implement issue"

**Recommendation**: ✅ **STRONG CANDIDATE FOR BUNDLING**

---

### Pattern 3: PR Quality Workflow
**Components**: `pr-review-responder` + `pr-quality-fixer`

**Used Together By**:
- handle-pull-request command (orchestrates both)

**Co-change Frequency**: HIGH (paired for PR handling)

**Functional Cohesion**: HIGH
- Both focused on PR quality
- Complementary responsibilities: respond to reviews + fix quality issues
- Single business function: "handle PR"

**Recommendation**: ✅ **CANDIDATE FOR BUNDLING**

---

### Pattern 4: Documentation Tooling
**Components**: `asciidoc-reviewer` + cui-documentation skill

**Used Together By**:
- review-technical-docs command
- asciidoc-reviewer agent (loads skill)

**Co-change Frequency**: HIGH (documentation standards evolve together)

**Functional Cohesion**: HIGH
- Both focused on documentation standards
- Skill provides standards, agent enforces them
- Single domain: CUI documentation

**Recommendation**: ✅ **CANDIDATE FOR BUNDLING**

---

### Pattern 5: Java Development Core Skills
**Components**: cui-java-core + cui-java-unit-testing + cui-javadoc

**Used Together By**:
- task-executor (loads all three)
- Various Java development agents

**Co-change Frequency**: MEDIUM (Java standards evolve, but not always together)

**Functional Cohesion**: MEDIUM-HIGH
- All Java-focused
- But represent different concerns: coding, testing, documentation
- Could be used independently

**Recommendation**: ⚠️ **KEEP SEPARATE** (already modular, good granularity)

---

## Claude Code Best Practices Applied

### From Research Findings

#### ✅ Progressive Disclosure
- Skills: Already implemented correctly
- Load only metadata initially (~50-100 tokens per skill)
- Full content loads on-demand

#### ✅ Functional Cohesion (HIGH Confidence Finding)
- "Functional cohesion is when parts of a module are grouped because they all contribute to a single well-defined task"
- **Build + Commit**: Single task = "verify and persist changes"
- **Issue Workflow**: Single task = "implement structured issue"
- **PR Workflow**: Single task = "handle PR quality"

#### ✅ Common Closure Principle (HIGH Confidence Finding)
- "Classes that change together belong together"
- **Build + Commit**: ALWAYS deployed together
- **Issue agents**: Change together when workflow evolves
- **PR agents**: Change together when PR process updates

#### ✅ Token Efficiency (HIGH Confidence Finding)
- Optimal range: 2-8 components per plugin
- Average successful plugins: 3.4 components
- Our proposed bundles fit this pattern

#### ✅ Single Responsibility Through Toggling
- Each plugin bundle represents ONE workflow or domain
- Users can toggle plugins on/off based on current task
- Reduces context when not needed

#### ⚠️ Avoid Nano-Services (MEDIUM Confidence Finding)
- "Eliminate nano-services where operational burden surpasses business value"
- Single-agent plugins might create too much management overhead
- Bundling reduces marketplace clutter

---

## Recommended Plugin Bundle Structure

### Plugin 1: `cui-project-quality-gates`
**Purpose**: Build verification and change management infrastructure

**Components** (3):
- Agent: `maven-project-builder`
- Agent: `commit-changes`
- Skill: `cui-javadoc` (used by maven-project-builder)

**Functional Cohesion**: HIGH (single task: quality verification)

**Token Estimate**: ~500 tokens (2 agents + 1 skill metadata)

**Use Case**: "Verify project builds correctly and commit changes"

**Why Bundle**:
- Always used together (100% co-occurrence)
- Change together (quality standards evolve as unit)
- Single responsibility: project quality gates
- Fits 2-8 component guideline

---

### Plugin 2: `cui-issue-implementation`
**Purpose**: Structured issue implementation workflow

**Components** (5):
- Agent: `task-reviewer`
- Agent: `task-breakdown-agent`
- Agent: `task-executor`
- Command: `/implement-task`
- Agent: `research-best-practices` (dependency of task-reviewer)

**Functional Cohesion**: HIGH (single workflow: issue → done)

**Token Estimate**: ~600 tokens (4 agents + 1 command metadata)

**Use Case**: "Complete end-to-end issue implementation"

**Why Bundle**:
- Sequential workflow components
- All serve single business function
- Command orchestrates the agents
- Fits 2-8 component guideline

---

### Plugin 3: `cui-pull-request-workflow`
**Purpose**: PR review response and quality fixing

**Components** (3):
- Agent: `pr-review-responder`
- Agent: `pr-quality-fixer`
- Command: `/handle-pull-request`

**Functional Cohesion**: HIGH (single workflow: PR handling)

**Token Estimate**: ~400 tokens (2 agents + 1 command metadata)

**Use Case**: "Handle PR reviews and fix quality issues"

**Why Bundle**:
- Paired for PR workflows
- Command orchestrates both agents
- Change together when PR process evolves
- Fits 2-8 component guideline

---

### Plugin 4: `cui-documentation-standards`
**Purpose**: AsciiDoc and documentation enforcement

**Components** (3):
- Agent: `asciidoc-reviewer`
- Skill: `cui-documentation`
- Command: `/review-technical-docs`

**Functional Cohesion**: HIGH (single domain: documentation)

**Token Estimate**: ~300 tokens (1 agent + 1 skill + 1 command metadata)

**Use Case**: "Review and enforce documentation standards"

**Why Bundle**:
- Agent loads skill for standards
- Command orchestrates review
- Documentation standards evolve together
- Fits 2-8 component guideline

---

### Pattern 5: Plugin Development Tools
**Components**: `create-agent` + `create-command` + `diagnose-agents` + `diagnose-commands` + `diagnose-skills`

**Used Together By**:
- Plugin developers creating new components
- Marketplace maintainers verifying quality
- Teams building custom agents/commands

**Co-change Frequency**: HIGH (tooling evolves together)

**Functional Cohesion**: HIGH
- All focused on plugin lifecycle management
- Create tools + diagnostic tools = complete development workflow
- Single domain: Plugin development
- Single user persona: Plugin developers

**Recommendation**: ✅ **CANDIDATE FOR BUNDLING**

---

### Keep Separate: General Utilities

**Not Bundled** (remain individual):
- `research-best-practices` - general-purpose research utility, used across many contexts
- `setup-project-permissions` - one-time project setup
- `manage-web-permissions` - web access configuration

**Why Separate**:
- General utilities without specific workflow coupling
- Used independently across many contexts
- Lower co-change frequency with other components
- Single-purpose tools that don't cluster with others

---

### Keep Modular: Skills

**Current Plugin Structure** (maintain as-is):
- `cui-java-skills` plugin → cui-java-core, cui-java-unit-testing, cui-javadoc, cui-java-cdi
- `cui-frontend-skills` plugin → cui-frontend-development
- `cui-documentation-skills` plugin → cui-documentation
- `cui-project-management-skills` plugin → cui-project-setup, cui-requirements

**Why This Works**:
- Already organized by domain (Java, Frontend, Documentation, PM)
- Skills are auto-invoked independently
- Good granularity for toggling domains
- Follows Anthropic's progressive disclosure pattern

---

## Implementation Recommendations

### Priority 1: Create Quality Gates Plugin ✅
**Why**: Highest co-occurrence (100%), used by 6+ components

**Structure**:
```
cui-project-quality-gates/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   ├── maven-project-builder/
│   │   └── AGENT.md
│   └── commit-changes/
│       └── AGENT.md
└── skills/
    └── cui-javadoc/
        └── SKILL.md
```

**plugin.json**:
```json
{
  "name": "cui-project-quality-gates",
  "version": "1.0.0",
  "description": "Build verification and change management for CUI projects",
  "keywords": ["maven", "build", "commit", "quality", "verification"],
  "category": "development"
}
```

---

### Priority 2: Create Issue Implementation Plugin ✅
**Why**: Complete workflow with high cohesion

**Structure**:
```
cui-issue-implementation/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   └── implement-task.md
└── agents/
    ├── task-reviewer/
    ├── task-breakdown-agent/
    ├── task-executor/
    └── research-best-practices/
```

---

### Priority 3: Create PR Workflow Plugin ✅
**Why**: PR-specific workflow with clear boundaries

**Structure**:
```
cui-pull-request-workflow/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   └── handle-pull-request.md
└── agents/
    ├── pr-review-responder/
    └── pr-quality-fixer/
```

---

### Priority 4: Create Documentation Plugin ✅
**Why**: Domain-specific with skill dependency

**Structure**:
```
cui-documentation-standards/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   └── review-technical-docs.md
├── agents/
│   └── asciidoc-reviewer/
└── skills/
    └── cui-documentation/
```

---

### Priority 5: Create Plugin Development Tools ✅
**Why**: Complete toolchain for plugin developers

**Structure**:
```
cui-plugin-development-tools/
├── .claude-plugin/
│   └── plugin.json
└── commands/
    ├── create-agent.md
    ├── create-command.md
    ├── diagnose-agents.md
    ├── diagnose-commands.md
    └── diagnose-skills.md
```

**plugin.json**:
```json
{
  "name": "cui-plugin-development-tools",
  "version": "1.0.0",
  "description": "Complete toolchain for creating and diagnosing Claude Code plugins, agents, commands, and skills",
  "keywords": ["plugin", "development", "tools", "diagnose", "create", "quality"],
  "category": "development"
}
```

**Components**: 5 commands = 5 components ✅

**Token Estimate**: ~300 tokens (5 command metadata)

**Use Case**: "Create and maintain high-quality Claude Code plugins"

**Why Bundle**:
- All serve plugin development lifecycle
- Create + diagnose = complete workflow
- Single user persona: plugin developers
- Tooling evolves together
- Fits 2-8 component guideline

---

## Migration Strategy

### Phase 1: Create Plugin Structures
1. Create directory structures for 5 new plugins
2. Move/copy component files into plugin directories
3. Create plugin.json manifests
4. Test local installation

### Phase 2: Update Dependencies
1. Update commands to reference bundled agents
2. Update agents to reference bundled skills
3. Test inter-plugin dependencies

### Phase 3: Marketplace Integration
1. Add plugins to marketplace.json
2. Test installation from marketplace
3. Document plugin usage

### Phase 4: Deprecate Individual Components
1. Mark individual agents as deprecated
2. Update documentation to recommend plugins
3. Maintain backwards compatibility for transition period

---

## Benefits of This Bundling Strategy

### For Users
✅ **Simplified Installation**: Install complete workflows with one command
✅ **Reduced Clutter**: 5 focused plugins vs 14+ individual components
✅ **Clear Purpose**: Each plugin name indicates its complete workflow or domain
✅ **Better Discovery**: Marketplace categories make finding functionality easier
✅ **Token Efficiency**: Toggle entire workflows on/off to manage context

### For Maintainers
✅ **Logical Organization**: Components that change together are packaged together
✅ **Easier Updates**: Update workflow components as a unit
✅ **Clear Boundaries**: Each plugin has well-defined scope
✅ **Version Management**: Version entire workflows together
✅ **Reduced Duplication**: Shared agents bundled once, not duplicated

### For System Performance
✅ **Context Optimization**: Progressive disclosure at plugin level
✅ **Token Management**: ~300-600 tokens per workflow vs scattered components
✅ **Follows Best Practices**: Aligns with Anthropic's 2-8 component guideline

---

## Validation Against Claude Code Principles

| Principle | Implementation | Status |
|-----------|----------------|--------|
| Progressive Disclosure | Skills load metadata, then full content on-demand | ✅ |
| Functional Cohesion | Each plugin = single workflow/domain | ✅ |
| Token Efficiency | 2-8 components per plugin (avg 3.5) | ✅ |
| Independent Installation | Each plugin stands alone | ✅ |
| Toggle-based Management | Users enable workflows as needed | ✅ |
| Common Closure | Components that change together bundled | ✅ |
| Avoid Nano-Services | No single-component plugins | ✅ |
| Single Responsibility | Each plugin serves one clear purpose | ✅ |

---

## Extensibility Strategy: Future Specialized Reviewers

### Planned Growth: Specialized Code Review Agents

**Upcoming Agents** (anticipated next iterations):
- `java-architecture-reviewer` - Review architectural patterns, layering, dependencies
- `java-api-reviewer` - Review public API design, contracts, documentation
- `java-unit-test-reviewer` - Review test quality, coverage, patterns
- `java-security-reviewer` - Review security vulnerabilities, authentication, authorization
- `java-performance-reviewer` - Review performance patterns, efficiency, scalability
- `frontend-component-reviewer` - Review web component structure and patterns
- `frontend-accessibility-reviewer` - Review WCAG compliance, a11y patterns
- Additional domain-specific reviewers as needed

**Challenge**: How to organize 5-10+ specialized reviewers without creating:
- ❌ Marketplace clutter (too many individual plugins)
- ❌ Monolithic bundle (one massive "reviewers" plugin)
- ❌ Poor discoverability (users can't find relevant reviewer)
- ❌ Context bloat (loading all reviewers when only need one)

---

### Extensibility Pattern Analysis

#### Option A: Monolithic Review Plugin ❌ **NOT RECOMMENDED**

**Structure**:
```
cui-code-review-suite/
└── agents/
    ├── java-architecture-reviewer/
    ├── java-api-reviewer/
    ├── java-unit-test-reviewer/
    ├── java-security-reviewer/
    ├── java-performance-reviewer/
    ├── frontend-component-reviewer/
    └── frontend-accessibility-reviewer/
```

**Pros**:
- Single installation for all reviewers
- Centralized version management

**Cons**:
- ❌ Violates 2-8 component guideline (7+ agents)
- ❌ Loads all reviewer metadata even when only need one
- ❌ Forces users to install reviewers they don't need
- ❌ Changes to one reviewer require entire plugin version bump
- ❌ Poor token efficiency (~700+ tokens for all reviewers)
- ❌ Violates single responsibility (multiple review domains)

**Verdict**: Conflicts with Claude Code best practices

---

#### Option B: Individual Reviewer Plugins ⚠️ **MANAGEABLE BUT RISKY**

**Structure**:
```
Separate plugins:
- cui-java-architecture-reviewer (1 agent)
- cui-java-api-reviewer (1 agent)
- cui-java-unit-test-reviewer (1 agent)
- cui-java-security-reviewer (1 agent)
- cui-java-performance-reviewer (1 agent)
- cui-frontend-component-reviewer (1 agent)
- cui-frontend-accessibility-reviewer (1 agent)
```

**Pros**:
- Maximum granularity and user choice
- Perfect single responsibility
- Independent versioning
- Optimal token efficiency (load only what's needed)

**Cons**:
- ⚠️ Marketplace clutter (7+ additional plugins)
- ⚠️ Single-component plugins (violates 2-8 guideline)
- ⚠️ Installation overhead (users run 7+ install commands)
- ⚠️ Shared dependencies duplicated across plugins
- ⚠️ Discoverability challenges (reviewers scattered)

**Verdict**: Viable but creates "nano-service" problem

---

#### Option C: Domain-Clustered Review Plugins ✅ **RECOMMENDED**

**Structure**: Group reviewers by **functional domain** with 2-5 agents each

**Plugin 1: `cui-java-code-review`**
```
cui-java-code-review/
├── .claude-plugin/plugin.json
├── agents/
│   ├── java-architecture-reviewer/
│   ├── java-api-reviewer/
│   └── java-unit-test-reviewer/
└── skills/
    ├── cui-java-core/
    └── cui-java-unit-testing/
```

**Components**: 3 agents + 2 skills = 5 components ✅
**Token Estimate**: ~600 tokens
**Use Case**: "Review Java code for architecture, API design, and testing"

---

**Plugin 2: `cui-java-quality-review`**
```
cui-java-quality-review/
├── .claude-plugin/plugin.json
├── agents/
│   ├── java-security-reviewer/
│   └── java-performance-reviewer/
└── skills/
    └── cui-java-core/
```

**Components**: 2 agents + 1 skill = 3 components ✅
**Token Estimate**: ~400 tokens
**Use Case**: "Review Java code for security and performance"

---

**Plugin 3: `cui-frontend-code-review`**
```
cui-frontend-code-review/
├── .claude-plugin/plugin.json
├── agents/
│   ├── frontend-component-reviewer/
│   └── frontend-accessibility-reviewer/
└── skills/
    └── cui-frontend-development/
```

**Components**: 2 agents + 1 skill = 3 components ✅
**Token Estimate**: ~400 tokens
**Use Case**: "Review frontend code for components and accessibility"

---

**Pros**:
- ✅ Fits 2-8 component guideline (3-5 components per plugin)
- ✅ Logical domain grouping (Java core vs quality vs frontend)
- ✅ Balanced granularity (not too fine, not too coarse)
- ✅ Shared skills bundled with related reviewers
- ✅ Users install domain-relevant bundles
- ✅ Functional cohesion (review domains align with project needs)
- ✅ Token efficiency (~400-600 per domain)
- ✅ Reduced marketplace clutter (3 plugins vs 7+)

**Cons**:
- ⚠️ Users wanting only one reviewer must install entire domain bundle
- ⚠️ Requires careful domain boundary decisions

**Verdict**: Best balance of modularity, usability, and scalability

---

### Extensibility Design Principles

#### Principle 1: Domain-Based Clustering
**Rule**: Group reviewers by **what they review**, not by technical layer

**Good Clustering** (functional domains):
- Java architectural concerns (architecture, API, testing)
- Java quality concerns (security, performance)
- Frontend concerns (components, accessibility)

**Bad Clustering** (technical layers):
- All "reviewers" together
- All "Java" together
- All "static analysis" together

**Why**: Users think in domains ("I need Java review") not layers ("I need reviewer agents")

---

#### Principle 2: 2-5 Agents Per Review Plugin
**Rule**: Target 2-5 specialized reviewers per plugin + shared skills

**Calculation**:
- 2-5 agents (reviewers)
- 0-2 skills (domain knowledge)
- 0-1 command (orchestration)
- **Total: 2-8 components** ✅

**Example**:
- `cui-java-code-review`: 3 agents + 2 skills = 5 ✅
- `cui-java-quality-review`: 2 agents + 1 skill = 3 ✅
- `cui-frontend-code-review`: 2 agents + 1 skill = 3 ✅

---

#### Principle 3: Independent Agent Invocation
**Rule**: Each reviewer agent should be independently invokable

**Pattern**:
```markdown
User: "Review the architecture of UserService.java"
→ Claude auto-invokes: java-architecture-reviewer from cui-java-code-review plugin

User: "Check this API for security issues"
→ Claude auto-invokes: java-security-reviewer from cui-java-quality-review plugin
```

**Implementation**:
- Agents have clear, specific descriptions for auto-invocation
- Users can also invoke explicitly: `@java-architecture-reviewer`
- Skills auto-load when reviewers activate

**Benefit**: Users don't need to know plugin structure, just ask for reviews

---

#### Principle 4: Progressive Plugin Installation
**Rule**: Users install review plugins as project needs grow

**Adoption Path**:
1. **New project**: Install `cui-project-quality-gates` (build + commit)
2. **Add code review**: Install `cui-java-code-review` (architecture + API + tests)
3. **Pre-production**: Install `cui-java-quality-review` (security + performance)
4. **Frontend work**: Install `cui-frontend-code-review` (components + a11y)

**Benefit**: Pay-as-you-grow, no forced bundles

---

#### Principle 5: Shared Skills Co-location
**Rule**: Bundle domain skills with their primary reviewers

**Pattern**:
```
cui-java-code-review plugin includes:
├── agents/
│   └── java-architecture-reviewer (uses cui-java-core skill)
└── skills/
    └── cui-java-core (bundled here, not separate plugin)
```

**Why**:
- Avoids plugin dependency hell
- Ensures reviewers have needed knowledge
- Simplifies installation (one plugin has everything)

**Exception**: Skills used by >3 plugins remain separate (e.g., cui-documentation)

---

### Scalability Roadmap

#### Phase 1: Core Workflows (Current)
**Status**: 5 plugins
- cui-project-quality-gates (build + commit infrastructure)
- cui-issue-implementation (complete issue workflow)
- cui-pull-request-workflow (PR handling)
- cui-documentation-standards (doc review)
- cui-plugin-development-tools (plugin creation + diagnostics)

**Focus**: Essential infrastructure, workflows, and development tooling

---

#### Phase 2: Code Review Domains (Next Iteration)
**Add**: 3 review plugins
- cui-java-code-review (architecture, API, testing)
- cui-java-quality-review (security, performance)
- cui-frontend-code-review (components, accessibility)

**Marketplace Total**: 8 plugins
**Average Components**: 3.6 per plugin ✅

---

#### Phase 3: Specialized Extensions (Future)
**Add**: Domain-specific utilities as needed
- cui-database-tools (migration reviewers, query optimizers)
- cui-devops-automation (deployment reviewers, config validators)
- cui-api-design (REST/GraphQL reviewers, contract validators)

**Growth Pattern**: Add 1-3 plugins per quarter based on demand

**Marketplace Total**: 10-15 plugins (target)

**Management**: Category-based browsing prevents overwhelming users

---

### Review Plugin Discovery

#### Marketplace Categories

**Current Categories**:
- `development` - Core workflows
- `quality` - Testing, building, verification
- `documentation` - Doc standards and review

**New Categories** (for reviewers):
- `code-review-java` - Java-specific reviewers
- `code-review-frontend` - Frontend-specific reviewers
- `security` - Security-focused reviewers

#### Plugin Naming Convention

**Pattern**: `cui-<domain>-<function>`

**Examples**:
- ✅ `cui-java-code-review` - Clear domain (Java) + function (code review)
- ✅ `cui-frontend-code-review` - Clear domain (Frontend) + function (code review)
- ✅ `cui-java-quality-review` - Clear domain (Java) + function (quality review)

**Anti-patterns**:
- ❌ `cui-reviewers` - Too generic
- ❌ `cui-java-stuff` - Unclear function
- ❌ `cui-all-in-one-review` - Implies monolith

---

### Integration with Existing Plugins

#### Skills Plugin Relationship

**Current Skills Plugins** (keep as-is):
- `cui-java-skills` - Auto-invoked Java knowledge
- `cui-frontend-skills` - Auto-invoked frontend knowledge

**Review Plugins** (new):
- `cui-java-code-review` - Explicit review agents

**Relationship**:
- Skills: Passive knowledge (auto-invoked by context)
- Review agents: Active analysis (invoked for reviews)
- Review agents USE skills for domain knowledge

**Example Flow**:
1. User: "Review UserService.java architecture"
2. Claude invokes: `@java-architecture-reviewer` (from cui-java-code-review)
3. Reviewer activates: `cui-java-core` skill (for Java standards)
4. Reviewer uses skill knowledge to analyze architecture
5. Returns findings

---

#### Workflow Plugin Integration

**Existing Workflow**: `cui-issue-implementation`
- task-reviewer → task-breakdown → task-executor

**Extension Point**: task-executor can invoke review agents

**Enhanced Flow**:
1. task-executor implements code
2. task-executor invokes `@java-architecture-reviewer` for self-review
3. Reviewer analyzes implementation
4. task-executor fixes issues
5. Continues to next task

**Benefit**: Quality checks integrated into implementation workflow

---

### Extensibility Guidelines Summary

| Guideline | Recommendation |
|-----------|----------------|
| **Bundling Strategy** | Domain-clustered (3-5 agents per domain plugin) |
| **Components per Plugin** | 2-8 (target 3-5 agents + skills) |
| **Plugin Naming** | `cui-<domain>-<function>` pattern |
| **Installation Model** | Progressive (install domains as needed) |
| **Skill Co-location** | Bundle domain skills with primary users |
| **Agent Invocation** | Independent (each reviewer invokable separately) |
| **Growth Rate** | 1-3 plugins per quarter, max 15-20 total |
| **Discovery** | Category-based browsing, clear naming |
| **Version Management** | Domain plugins version independently |

---

### Long-Term Marketplace Vision

**Target Structure** (18-24 months):

**Infrastructure** (5 plugins):
- cui-project-quality-gates
- cui-issue-implementation
- cui-pull-request-workflow
- cui-documentation-standards
- cui-plugin-development-tools

**Code Review** (6 plugins):
- cui-java-code-review
- cui-java-quality-review
- cui-frontend-code-review
- cui-frontend-quality-review
- cui-api-design-review
- cui-database-review

**Specialized Tools** (5 plugins):
- cui-devops-automation
- cui-testing-utilities
- cui-refactoring-tools
- cui-performance-profiling
- cui-security-scanning

**Total**: 16 plugins
**Average**: 3-4 components per plugin
**Token Efficiency**: Load only relevant domains

**User Experience**:
- Browse by category
- Install progressively
- Toggle plugins per project type
- Clear, discoverable functionality

---

## Implementation Tasks

### Task 1: Create Plugin Bundle Structures

**Objective**: Create directory structures for 5 new plugin bundles

**Location**: Create bundles at `claude/marketplace/bundles/`

**Acceptance Criteria**:
- [ ] Directory structure created for `cui-project-quality-gates`
- [ ] Directory structure created for `cui-issue-implementation`
- [ ] Directory structure created for `cui-pull-request-workflow`
- [ ] Directory structure created for `cui-documentation-standards`
- [ ] Directory structure created for `cui-plugin-development-tools`
- [ ] Each plugin has `.claude-plugin/plugin.json` manifest
- [ ] All components moved/copied to correct plugin directories

**Directory Structure Pattern**:
```
claude/marketplace/bundles/cui-{plugin-name}/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── {agent-name}/
│       └── AGENT.md
├── commands/
│   └── {command-name}.md
├── skills/
│   └── {skill-name}/
│       └── SKILL.md
└── README.md
```

**Concrete Example - cui-project-quality-gates**:
```
claude/marketplace/bundles/cui-project-quality-gates/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   ├── maven-project-builder/
│   │   └── AGENT.md
│   └── commit-changes/
│       └── AGENT.md
├── skills/
│   └── cui-javadoc/
│       ├── SKILL.md
│       └── standards/
│           └── javadoc-standards.adoc
└── README.md
```

**plugin.json Examples for Each Bundle**:

**Bundle 1: cui-project-quality-gates/plugin.json**
```json
{
  "name": "cui-project-quality-gates",
  "version": "1.0.0",
  "description": "Build verification and change management infrastructure for CUI projects",
  "keywords": ["maven", "build", "commit", "quality", "verification"],
  "category": "development",
  "agents": [
    "./agents/maven-project-builder",
    "./agents/commit-changes"
  ],
  "skills": [
    "./skills/cui-javadoc"
  ]
}
```

**Bundle 2: cui-issue-implementation/plugin.json**
```json
{
  "name": "cui-issue-implementation",
  "version": "1.0.0",
  "description": "Complete issue implementation workflow from review to execution",
  "keywords": ["issue", "task", "implementation", "workflow"],
  "category": "development",
  "agents": [
    "./agents/task-reviewer",
    "./agents/task-breakdown-agent",
    "./agents/task-executor",
    "./agents/research-best-practices"
  ],
  "commands": [
    "./commands/implement-task.md"
  ]
}
```

**Bundle 3: cui-pull-request-workflow/plugin.json**
```json
{
  "name": "cui-pull-request-workflow",
  "version": "1.0.0",
  "description": "PR review response and quality fixing workflow",
  "keywords": ["pull-request", "pr", "review", "quality"],
  "category": "quality",
  "agents": [
    "./agents/pr-review-responder",
    "./agents/pr-quality-fixer"
  ],
  "commands": [
    "./commands/handle-pull-request.md"
  ]
}
```

**Bundle 4: cui-documentation-standards/plugin.json**
```json
{
  "name": "cui-documentation-standards",
  "version": "1.0.0",
  "description": "AsciiDoc and documentation standards enforcement for CUI projects",
  "keywords": ["documentation", "asciidoc", "standards", "review"],
  "category": "documentation",
  "agents": [
    "./agents/asciidoc-reviewer"
  ],
  "commands": [
    "./commands/review-technical-docs.md"
  ],
  "skills": [
    "./skills/cui-documentation"
  ]
}
```

**Bundle 5: cui-plugin-development-tools/plugin.json**
```json
{
  "name": "cui-plugin-development-tools",
  "version": "1.0.0",
  "description": "Complete toolchain for creating and diagnosing Claude Code plugins",
  "keywords": ["plugin", "development", "tools", "diagnose", "create"],
  "category": "development",
  "commands": [
    "./commands/create-agent.md",
    "./commands/create-command.md",
    "./commands/diagnose-agents.md",
    "./commands/diagnose-commands.md",
    "./commands/diagnose-skills.md"
  ]
}
```

**Component Mapping** (source → destination):

**Bundle 1: cui-project-quality-gates**
- `claude/marketplace/agents/maven-project-builder/` → `bundles/cui-project-quality-gates/agents/maven-project-builder/`
- `claude/marketplace/agents/commit-changes/` → `bundles/cui-project-quality-gates/agents/commit-changes/`
- `claude/marketplace/skills/cui-javadoc/` → `bundles/cui-project-quality-gates/skills/cui-javadoc/`

**Bundle 2: cui-issue-implementation**
- `claude/marketplace/agents/task-reviewer/` → `bundles/cui-issue-implementation/agents/task-reviewer/`
- `claude/marketplace/agents/task-breakdown-agent/` → `bundles/cui-issue-implementation/agents/task-breakdown-agent/`
- `claude/marketplace/agents/task-executor/` → `bundles/cui-issue-implementation/agents/task-executor/`
- `claude/marketplace/agents/research-best-practices/` → `bundles/cui-issue-implementation/agents/research-best-practices/`
- `claude/marketplace/commands/implement-task.md` → `bundles/cui-issue-implementation/commands/implement-task.md`

**Bundle 3: cui-pull-request-workflow**
- `claude/marketplace/agents/pr-review-responder/` → `bundles/cui-pull-request-workflow/agents/pr-review-responder/`
- `claude/marketplace/agents/pr-quality-fixer/` → `bundles/cui-pull-request-workflow/agents/pr-quality-fixer/`
- `claude/marketplace/commands/handle-pull-request.md` → `bundles/cui-pull-request-workflow/commands/handle-pull-request.md`

**Bundle 4: cui-documentation-standards**
- `claude/marketplace/agents/asciidoc-reviewer/` → `bundles/cui-documentation-standards/agents/asciidoc-reviewer/`
- `claude/marketplace/skills/cui-documentation/` → `bundles/cui-documentation-standards/skills/cui-documentation/`
- `claude/marketplace/commands/review-technical-docs.md` → `bundles/cui-documentation-standards/commands/review-technical-docs.md`

**Bundle 5: cui-plugin-development-tools**
- `claude/marketplace/commands/create-agent.md` → `bundles/cui-plugin-development-tools/commands/create-agent.md`
- `claude/marketplace/commands/create-command.md` → `bundles/cui-plugin-development-tools/commands/create-command.md`
- `claude/marketplace/commands/diagnose-agents.md` → `bundles/cui-plugin-development-tools/commands/diagnose-agents.md`
- `claude/marketplace/commands/diagnose-commands.md` → `bundles/cui-plugin-development-tools/commands/diagnose-commands.md`
- `claude/marketplace/commands/diagnose-skills.md` → `bundles/cui-plugin-development-tools/commands/diagnose-skills.md`

**Components NOT moved** (remain in original location):
- All utility commands: `build-and-verify.md`, `fix-intellij-diagnostics.md`, `setup-project-permissions.md`, `manage-web-permissions.md`, `create-update-agents-md.md`, `verify-architecture-diagrams.md`
- All skill-only plugins: `cui-java-skills`, `cui-frontend-skills`, `cui-documentation-skills`, `cui-project-management-skills`

**Testing**:
- Verify all files exist at expected paths
- Validate all plugin.json files parse correctly (use `jq . plugin.json`)
- Check no broken internal references
- Verify source files copied (not moved) for backward compatibility

---

### Task 2: Update Component Dependencies

**Objective**: Update all cross-references to use bundled component paths

**Components to Update**:

1. **Commands referencing agents**:
   - `implement-task.md` → Update agent invocations
   - `handle-pull-request.md` → Update agent invocations
   - `build-and-verify.md` → Update agent invocations
   - `fix-intellij-diagnostics.md` → Update agent invocations
   - `review-technical-docs.md` → Update agent invocations

2. **Agents referencing skills**:
   - `task-executor` → Update skill paths for cui-java-* skills
   - `pr-quality-fixer` → Update skill paths
   - `maven-project-builder` → Update skill paths for cui-javadoc
   - `asciidoc-reviewer` → Update skill paths for cui-documentation

3. **Agents referencing other agents**:
   - `task-executor` → Update paths to maven-project-builder, commit-changes
   - `pr-quality-fixer` → Update paths to maven-project-builder, commit-changes
   - `pr-review-responder` → Update paths to maven-project-builder, commit-changes
   - `task-reviewer` → Update path to research-best-practices

**Acceptance Criteria**:
- [ ] All agent invocations use correct bundled paths
- [ ] All skill references use correct bundled paths
- [ ] No broken cross-references remain
- [ ] All paths use relative format (./plugin/component/file)

**Testing**:
- Read each updated file and verify paths
- Grep for old path patterns to catch missed references
- Test agent invocation in local environment

---

### Task 3: Update Marketplace Configuration

**Objective**: Add new plugin bundles to marketplace.json

**File to Update**: `claude/marketplace/.claude-plugin/marketplace.json`

**Changes Required**:

Add 5 new plugin entries to the `plugins` array (after existing skill plugins). Each bundle reference points to the bundle's root directory:

```json
{
  "name": "cui-project-quality-gates",
  "description": "Build verification and change management infrastructure for CUI projects",
  "source": "./bundles/cui-project-quality-gates",
  "strict": false
},
{
  "name": "cui-issue-implementation",
  "description": "Complete issue implementation workflow from review to execution",
  "source": "./bundles/cui-issue-implementation",
  "strict": false
},
{
  "name": "cui-pull-request-workflow",
  "description": "PR review response and quality fixing workflow",
  "source": "./bundles/cui-pull-request-workflow",
  "strict": false
},
{
  "name": "cui-documentation-standards",
  "description": "AsciiDoc and documentation standards enforcement for CUI projects",
  "source": "./bundles/cui-documentation-standards",
  "strict": false
},
{
  "name": "cui-plugin-development-tools",
  "description": "Complete toolchain for creating and diagnosing Claude Code plugins",
  "source": "./bundles/cui-plugin-development-tools",
  "strict": false
}
```

**Note**: The marketplace.json references the bundle root. The bundle's own plugin.json (in `.claude-plugin/`) declares the specific agents/commands/skills.

**Existing skill plugins remain unchanged**:
- cui-java-skills
- cui-frontend-skills
- cui-documentation-skills
- cui-project-management-skills

**Acceptance Criteria**:
- [ ] marketplace.json includes all 5 new plugin bundles
- [ ] JSON syntax valid (no parsing errors)
- [ ] All `source` paths correctly point to `./bundles/{bundle-name}`
- [ ] Existing skill plugins remain unchanged
- [ ] Plugin descriptions match bundle plugin.json descriptions

**Testing**:
- Validate JSON with `jq . claude/marketplace/.claude-plugin/marketplace.json`
- Verify output shows all plugins including new bundles
- Test marketplace installation in fresh environment

---

### Task 4: Create Bundle-Specific README Files

**Objective**: Document usage and purpose for each plugin bundle

**Files to Create**:
- `cui-project-quality-gates/README.md`
- `cui-issue-implementation/README.md`
- `cui-pull-request-workflow/README.md`
- `cui-documentation-standards/README.md`
- `cui-plugin-development-tools/README.md`

**Required Sections**:
1. Purpose (1-2 sentences)
2. Components Included (list of agents/commands/skills)
3. Installation Instructions
4. Usage Examples
5. Dependencies (if any)

**Acceptance Criteria**:
- [ ] README exists for each plugin bundle
- [ ] Installation command documented
- [ ] Usage examples provided
- [ ] Component list accurate

---

### Task 5: Test Local Installation

**Objective**: Verify bundles install and function correctly

**Test Steps**:

1. **Add local marketplace**:
   ```bash
   /plugin marketplace add file:///Users/oliver/git/cui-llm-rules/claude/marketplace
   ```

2. **Install each bundle**:
   ```bash
   /plugin install cui-project-quality-gates
   /plugin install cui-issue-implementation
   /plugin install cui-pull-request-workflow
   /plugin install cui-documentation-standards
   /plugin install cui-plugin-development-tools
   ```

3. **Verify component discovery**:
   ```bash
   /agents list  # Should show bundled agents
   /commands list  # Should show bundled commands
   /skills list  # Should show bundled skills
   ```

4. **Test invocation**:
   - Test agent invocation via Task tool
   - Test command invocation via /command-name
   - Test skill loading

**Acceptance Criteria**:
- [ ] All 5 bundles install without errors
- [ ] All agents appear in /agents list
- [ ] All commands appear in /commands list
- [ ] All skills appear in /skills list
- [ ] At least one agent from each bundle successfully invokes
- [ ] At least one command from each bundle successfully runs

**Testing Documentation**:
- Record any installation errors
- Document resolution steps
- Note any path resolution issues

---

### Task 6: Backward Compatibility Strategy

**Objective**: Ensure existing users can migrate smoothly

**Approach**: Maintain original marketplace structure while adding bundles

**Implementation**:

1. **Keep original components in place** (don't delete)
2. **Add deprecation notices** to individual components
3. **Document migration path** in marketplace README
4. **Provide transition period** (e.g., 3 months)

**Files to Update**:
- `claude/marketplace/README.md` - Add migration guide section
- Individual agent/command files - Add deprecation notice

**Acceptance Criteria**:
- [ ] Original marketplace structure unchanged
- [ ] Deprecation notices added to individual components
- [ ] Migration guide written in README.md
- [ ] Clear timeline for deprecation communicated

---

### Task 7: Create Bundling Architecture Document

**Objective**: Document the bundling architecture for future reference

**Location**: `claude/doc/bundling-architecture.adoc`

**Required Content**:

1. **Overview** - What is bundling and why we do it
2. **Bundle Patterns** - The 5 bundle types and their rationale
3. **Design Principles** - Functional cohesion, 2-8 components, domain clustering
4. **Bundle Structure** - Directory layout and plugin.json format
5. **Component Distribution** - Which components go in which bundles
6. **Extensibility** - How to add new bundles (domain-clustered pattern)
7. **Installation Model** - How users install and use bundles
8. **Cross-References** - Links to plugin-architecture.adoc and plugin-specifications.adoc

**Style Guidelines**:
- **Focused**: Architecture only, no analysis or research findings
- **Concise**: Similar length to plugin-architecture.adoc (~300 lines)
- **Prescriptive**: What IS, not what was considered
- **AsciiDoc format**: Consistent with existing doc standards

**Acceptance Criteria**:
- [ ] Document created at `claude/doc/bundling-architecture.adoc`
- [ ] Follows AsciiDoc conventions (toc:left, sectnums, etc.)
- [ ] Contains required sections listed above
- [ ] Cross-references other architecture documents
- [ ] Length approximately 250-350 lines
- [ ] No duplication of analysis content
- [ ] Focused on current architecture decisions

**Integration**:
- [ ] Update `claude/doc/README.adoc` to reference bundling architecture
- [ ] Add xref links from plugin-architecture.adoc if relevant

---

## Success Metrics

**Overall Implementation Complete When**:

- [ ] All 5 plugin bundle structures created
- [ ] All component dependencies updated
- [ ] marketplace.json updated with bundles
- [ ] Bundle READMEs written
- [ ] Local installation tested successfully
- [ ] Backward compatibility maintained
- [ ] Architecture document created and integrated
- [ ] All acceptance criteria above marked complete

**Quality Gates**:
- Zero broken references in updated components
- All JSON files validate
- All bundles install without errors
- Architecture document follows style guidelines
- Deprecation notices clear and helpful

---

## References

- Research findings from deep web analysis (95+ sources)
- Current marketplace structure analysis
- Claude Code official documentation
- Anthropic plugin best practices
- Community marketplace patterns

---

**Conclusion**: The current marketplace has clear bundling opportunities with a strong extensibility strategy. Grouping by functional cohesion (workflows and domains) rather than technical layers (all agents together) provides better UX and follows Claude Code best practices. The recommended initial 5-plugin structure reduces marketplace complexity while maintaining modularity. The domain-clustered extensibility strategy (3 additional review plugins) provides a scalable path to 15-20 plugins that maintains optimal token efficiency, clear discovery, and progressive installation. This approach balances current needs with future growth, avoiding both marketplace clutter and monolithic bundles.
