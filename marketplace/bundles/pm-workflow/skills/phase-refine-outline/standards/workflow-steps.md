# Workflow Steps

Detailed step-by-step guide for the architecture-driven solution outline workflow.

---

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `plan_id` | string | Yes | Plan identifier |
| `feedback` | string | No | User feedback from review (for revision iterations) |

---

## Step 1: Load Architecture Context

Query project architecture before any codebase exploration. Architecture data is pre-computed and compact (~500 tokens). Loading it first prevents wasteful re-discovery.

**EXECUTE**:
```bash
python3 .plan/execute-script.py plan-marshall:analyze-project-architecture:architecture info
```

Output format: `plan-marshall:analyze-project-architecture/standards/client-api.md`

**If status=error or architecture not found**: Abort with "Run /marshall-steward first".

---

## Step 2: Load and Understand Requirements

Load the request document and extract actionable requirements.

**EXECUTE**:
```bash
python3 .plan/execute-script.py pm-workflow:manage-plan-documents:manage-plan-documents read \
  --plan-id {plan_id} --type request
```

Output format: `pm-workflow:manage-plan-documents/documents/request.toon`

**Parse for**:
- Functional requirements (what to build)
- Constraints (technology, patterns, compatibility)
- Explicit test requirements (unit, integration, E2E)
- Acceptance criteria

Understanding requirements BEFORE architecture assessment ensures correct module selection and complexity evaluation.

---

## Step 3: Assess Complexity (Simple vs Complex)

Determine if task is single-module (simple) or multi-module (complex):

| Scope | Workflow | Action |
|-------|----------|--------|
| Single module affected | **Simple** | Proceed to module selection |
| Multiple modules affected | **Complex** | Decompose first, then simple workflow per sub-task |

### Simple Workflow (single module)

```
┌───────────────────────────────┐
│       SIMPLE WORKFLOW         │
├───────────────────────────────┤
│ 1. Select target module       │
│ 2. Select target package      │
│ 3. Create deliverables        │
└───────────────────────────────┘
```

### Complex Workflow (multi-module)

```
┌───────────────────────────────┐
│       COMPLEX WORKFLOW        │
├───────────────────────────────┤
│ 1. Decompose into sub-tasks   │
│ 2. Run simple workflow each   │
│ 3. Aggregate deliverables     │
│ 4. Order by dependencies      │
└───────────────────────────────┘
```

### Decomposition (Complex Only)

**EXECUTE**:
```bash
python3 .plan/execute-script.py plan-marshall:analyze-project-architecture:architecture module \
  --name {module} --full
```

Use `internal_dependencies` from output to order deliverables - changes in dependent modules must come BEFORE changes in modules that depend on them.

---

## Step 4: Select Target Modules

For simple tasks: identify the single affected module. For complex tasks: select module for each sub-task.

Score by responsibility match, purpose fit, and package alignment.

**Detail**: See [module-selection.md](module-selection.md#scoring-heuristics)

---

## Step 5: Determine Package Placement

For each module, determine where new code belongs. Always use `--full` to see complete package structure.

**Detail**: See [module-selection.md](module-selection.md#package-placement)

---

## Step 6: Create Deliverables with Profile Skills

Create deliverables with module context and skills organized by profile. Include relevant tips and best practices from architecture data.

**Core constraint**: One deliverable = one module.

**Profile inclusion** (per deliverable):
- `skills-implementation`: Always included
- `skills-testing`: Only if module has test infrastructure (`architecture modules --command module-tests`)

**Detail**: See [skills-by-profile.md](skills-by-profile.md)

---

## Step 7: Create IT Deliverable (Optional)

If integration tests are needed, create a **separate deliverable** targeting the IT module.

**When to create**:
- Explicit request mentions "integration test", "IT", "E2E"
- Change is external-facing (API, UI, public library API, config)

**Prerequisite**: Project has IT infrastructure (`architecture modules --command integration-tests` returns non-empty)

**Detail**: See [integration-tests.md](integration-tests.md)

---

## Deliverable Template

Follows the deliverable contract from `pm-workflow:plan-wf-skill-api/standards/deliverable-contract.md`.

```markdown
### {N}. {Deliverable Title}

**Metadata:**
- change_type: {create|modify|delete}
- execution_mode: {automated|manual|mixed}
- domain: {domain from config}
- depends: {none|reference to other deliverable}

**Module Context:**
- module: {module from architecture}
- package: {package from architecture}
- placement_rationale: {reasoning for placement}

**Skills by Profile:**
- skills-implementation: [{skills from module.skills_by_profile}]
- skills-testing: [{skills from module.skills_by_profile, if test infra exists}]

**Affected files:**
- `{module}/src/main/java/{package path}/{ClassName}.java`

**Change per file:** {description of changes}

**Pattern:** {optional code pattern if applicable}

**Verification:**
- Command: {build/test command}
- Criteria: {success criteria}

**Success Criteria:**
- {acceptance criterion 1}
- {acceptance criterion 2}

**Implementation Guidance:**
- tips: "{from architecture tips}"
- best_practices: "{from architecture best_practices}"
```

**Required fields** (per contract):
- `change_type`, `execution_mode`, `domain`, `depends`
- Module context (module, package, placement_rationale)
- Skills by Profile (`skills-implementation` always; `skills-testing` if module has test infra)
- Explicit file list (not "all files matching X")
- Verification command and criteria

**Skills source**: `module.skills_by_profile` from architecture data. Task-plan splits into profile-specific tasks.
