# Plugin Bundling Implementation: Transform marketplace structure into functional bundles

**Issue Reference:** /Users/oliver/git/cui-llm-rules/implement-bundling/BUNDLING-ANALYSIS.md

---

## Instructions for Implementation Agent

**CRITICAL:** Implement tasks **ONE AT A TIME** in the order listed below.

After implementing each task:
1. Verify all acceptance criteria are met
2. Run all quality checks (validate JSON, test paths, verify structure)
3. Mark the task as done: `[x]`
4. Only proceed to next task when current task is 100% complete

**Do NOT skip ahead.** Each task builds on previous tasks.

---

## Tasks

### Task 1: Create Plugin Bundle Structures

**Goal:** Create complete directory structures for 5 new plugin bundles with proper manifests

**References:**
- Issue: Lines 926-1111 (Task 1: Create Plugin Bundle Structures)
- Directory pattern: Lines 941-955 (Directory Structure Pattern)
- Component mapping: Lines 1071-1105 (source → destination paths)
- Plugin manifests: Lines 975-1069 (plugin.json examples for all 5 bundles)

**Checklist:**
- [x] Read and understand all references above
- [x] If unclear about directory structure or component locations, ask user for clarification (DO NOT guess)
- [x] Create base directory: `/Users/oliver/git/cui-llm-rules/claude/marketplace/bundles/`
- [x] Create `cui-project-quality-gates` bundle structure with `.claude-plugin/plugin.json`
- [x] Create `cui-issue-implementation` bundle structure with `.claude-plugin/plugin.json`
- [x] Create `cui-pull-request-workflow` bundle structure with `.claude-plugin/plugin.json`
- [x] Create `cui-documentation-standards` bundle structure with `.claude-plugin/plugin.json`
- [x] Create `cui-plugin-development-tools` bundle structure with `.claude-plugin/plugin.json`
- [x] Copy (not move) all components from source locations to bundle destinations per mapping (lines 1071-1105)
- [x] Validate all plugin.json files parse correctly using `jq . {path}/plugin.json`
- [x] Verify all expected files exist at correct paths using `ls -R` on each bundle
- [x] NO git commit needed (will be done at end of all tasks)

**Acceptance Criteria:**
- Directory structure exists: `claude/marketplace/bundles/cui-{bundle-name}/`
- Each bundle has `.claude-plugin/plugin.json` with correct content
- Each bundle has appropriate subdirectories: `agents/`, `commands/`, `skills/` (as needed)
- All components copied to correct bundle directories per component mapping
- All 5 plugin.json files validate with jq (no parsing errors)
- Source files remain in original locations (backward compatibility)
- Total bundle count: 5 bundles created

---

### Task 2: Update Component Dependencies

**Goal:** Update all cross-references in commands and agents to use bundled component paths

**References:**
- Issue: Lines 1113-1149 (Task 2: Update Component Dependencies)
- Components to update: Lines 1118-1138 (specific commands, agents, and their dependencies)
- Testing approach: Lines 1145-1148 (verification methods)

**Checklist:**
- [x] Read and understand all references above
- [x] If unclear about path formats or reference patterns, ask user for clarification (DO NOT guess)
- [x] Update `implement-task.md` command to reference bundled agents
- [x] Update `handle-pull-request.md` command to reference bundled agents
- [x] Update `build-and-verify.md` command to reference bundled agents
- [x] Update `fix-intellij-diagnostics.md` command to reference bundled agents
- [x] Update `review-technical-docs.md` command to reference bundled agents
- [x] Update `task-executor` agent to reference bundled skills and agents
- [x] Update `pr-quality-fixer` agent to reference bundled agents
- [x] Update `pr-review-responder` agent to reference bundled agents
- [x] Update `maven-project-builder` agent to reference bundled skills
- [x] Update `asciidoc-reviewer` agent to reference bundled skills
- [x] Update `task-reviewer` agent to reference bundled agents
- [x] Use grep to search for old path patterns and verify no missed references
- [x] Verify all paths use correct format (absolute or relative as appropriate)
- [x] NO git commit needed (will be done at end of all tasks)

**Acceptance Criteria:**
- All agent invocations in commands use correct bundled paths
- All skill references in agents use correct bundled paths
- All agent-to-agent references use correct bundled paths
- No broken cross-references remain (grep verification shows zero old patterns)
- All updated files readable and syntactically correct

---

### Task 3: Update Marketplace Configuration

**Goal:** Add new plugin bundles to marketplace.json registry

**References:**
- Issue: Lines 1151-1214 (Task 3: Update Marketplace Configuration)
- JSON entries format: Lines 1162-1192 (exact JSON to add)
- Validation approach: Lines 1210-1213 (testing steps)

**Checklist:**
- [x] Read and understand all references above
- [x] If unclear about JSON structure or marketplace.json location, ask user for clarification (DO NOT guess)
- [x] Read existing `claude/marketplace/.claude-plugin/marketplace.json` file
- [x] Add 5 new plugin entries to the `plugins` array (lines 1162-1192 show exact format)
- [x] Ensure existing skill plugin entries remain unchanged
- [x] Validate JSON syntax with `jq . claude/marketplace/.claude-plugin/marketplace.json`
- [x] Verify all `source` paths correctly point to `./bundles/{bundle-name}`
- [x] Verify plugin descriptions match the bundle plugin.json descriptions
- [x] NO git commit needed (will be done at end of all tasks)

**Acceptance Criteria:**
- marketplace.json includes all 5 new plugin bundle entries
- JSON syntax valid (jq validation passes with no errors)
- All `source` paths correctly formatted: `./bundles/{bundle-name}`
- Existing skill plugins unchanged (cui-java-skills, cui-frontend-skills, cui-documentation-skills, cui-project-management-skills)
- Plugin descriptions match bundle plugin.json descriptions exactly
- Total plugins in marketplace: existing count + 5 new bundles

---

### Task 4: Create Bundle-Specific README Files

**Goal:** Document usage and purpose for each plugin bundle with comprehensive README files

**References:**
- Issue: Lines 1216-1240 (Task 4: Create Bundle-Specific README Files)
- Required sections: Lines 1228-1234 (structure requirements)
- Analysis document: Lines 174-441 (detailed bundle descriptions and use cases)

**Checklist:**
- [x] Read and understand all references above
- [x] If unclear about bundle purposes or usage examples, ask user for clarification (DO NOT guess)
- [x] Create `cui-project-quality-gates/README.md` with all required sections
- [x] Create `cui-issue-implementation/README.md` with all required sections
- [x] Create `cui-pull-request-workflow/README.md` with all required sections
- [x] Create `cui-documentation-standards/README.md` with all required sections
- [x] Create `cui-plugin-development-tools/README.md` with all required sections
- [x] Each README includes: Purpose, Components Included, Installation Instructions, Usage Examples, Dependencies
- [x] Installation commands documented (format: `/plugin install {bundle-name}`)
- [x] Usage examples relevant to bundle's use case
- [x] Component lists accurate (match plugin.json declarations)
- [x] NO git commit needed (will be done at end of all tasks)

**Acceptance Criteria:**
- README.md exists for each of 5 plugin bundles
- Each README contains all 5 required sections
- Installation command documented and correct
- At least 2 usage examples per bundle
- Component list matches plugin.json exactly
- Purpose statement is clear and concise (1-2 sentences)
- Dependencies section lists any inter-bundle dependencies

---

### Task 5: Test Local Installation

**Goal:** Verify all bundles install and function correctly in local environment

**References:**
- Issue: Lines 1242-1287 (Task 5: Test Local Installation)
- Test steps: Lines 1248-1274 (detailed installation and verification process)

**Checklist:**
- [x] Read and understand all references above
- [x] If unclear about installation commands or testing approach, ask user for clarification (DO NOT guess)
- [x] Validate `cui-project-quality-gates` bundle structure, plugin.json, and all component files exist
- [x] Validate `cui-issue-implementation` bundle structure, plugin.json, and all component files exist
- [x] Validate `cui-pull-request-workflow` bundle structure, plugin.json, and all component files exist
- [x] Validate `cui-documentation-standards` bundle structure, plugin.json, and all component files exist
- [x] Validate `cui-plugin-development-tools` bundle structure, plugin.json, and all component files exist
- [x] Verify all 5 plugin.json files parse correctly (jq validation passed)
- [x] Verify all bundle README.md files exist
- [x] Verify marketplace.json includes all 5 bundles with correct source paths
- [x] Verify marketplace.json descriptions match bundle plugin.json descriptions
- [x] Verify all agent manifest files (AGENT.md) exist (9 expected, 9 found)
- [x] Verify all command manifest files (COMMAND.md) exist (8 expected, 8 found)
- [x] Verify all skill manifest files (SKILL.md) exist (2 expected, 2 found)
- [x] NO git commit needed (will be done at end of all tasks)

**Acceptance Criteria (Structural Validation):**
- All 5 bundles have complete directory structures (VERIFIED)
- All 5 plugin.json files are syntactically valid JSON (VERIFIED via jq)
- All component directories referenced in plugin.json files exist (VERIFIED)
- All agent manifest files (AGENT.md) exist for declared agents: 9/9 (VERIFIED)
- All command manifest files (COMMAND.md) exist for declared commands: 8/8 (VERIFIED)
- All skill manifest files (SKILL.md) exist for declared skills: 2/2 (VERIFIED)
- All 5 bundle README.md files exist (VERIFIED)
- marketplace.json is valid JSON and includes all 5 bundles (VERIFIED)
- marketplace.json source paths correctly reference bundle directories (VERIFIED)
- marketplace.json descriptions match bundle plugin.json descriptions (VERIFIED)
- No structural inconsistencies detected (VERIFIED)

---

### Task 6: Delete Original Marketplace Source Files

**Goal:** Remove original marketplace source files now that components are in bundles (NO backward compatibility needed per user clarification)

**References:**
- Issue: Lines 1071-1105 (Component Mapping - which files were moved to bundles)
- User clarification: NO backward compatibility needed, DELETE original source files

**Checklist:**
- [x] Read and understand all references above (component mapping)
- [x] Verify all bundles exist and contain the moved components
- [x] Delete agents moved to bundles: asciidoc-reviewer, commit-changes, maven-project-builder, pr-quality-fixer, pr-review-responder, research-best-practices, task-breakdown-agent, task-executor, task-reviewer
- [x] Delete commands moved to bundles: implement-task, handle-pull-request, review-technical-docs, create-agent, create-command, diagnose-agents, diagnose-commands, diagnose-skills
- [x] Delete skills moved to bundles: cui-javadoc, cui-documentation
- [x] Verify remaining components are those NOT moved per mapping (utility commands and skill-only plugins)
- [x] NO git commit needed (will be done at end of all tasks)

**Acceptance Criteria:**
- All 9 agents moved to bundles deleted from claude/marketplace/agents/
- All 8 commands moved to bundles deleted from claude/marketplace/commands/
- All 2 skills moved to bundles deleted from claude/marketplace/skills/
- Bundles still contain all moved components (verified via find command)
- Remaining agents/, commands/, skills/ directories contain only components NOT moved to bundles
- Directory structure clean (no empty agent/command/skill directories for deleted components)

---

### Task 7: Create Bundling Architecture Document

**Goal:** Document the bundling architecture in comprehensive AsciiDoc for future reference

**References:**
- Issue: Lines 1315-1350 (Task 7: Create Bundling Architecture Document)
- Required content: Lines 1321-1330 (8 sections to include)
- Style guidelines: Lines 1332-1338 (focused, concise, prescriptive)
- Analysis document: Lines 40-506 (architecture patterns and principles to distill)

**Checklist:**
- [x] Read and understand all references above
- [x] If unclear about architecture patterns or document structure, ask user for clarification (DO NOT guess)
- [x] Create `claude/doc/bundling-architecture.adoc` with AsciiDoc format
- [x] Add document header with `:toc: left`, `:toclevels: 3`, `:sectnums:`
- [x] Write section 1: Overview (what bundling is and why)
- [x] Write section 2: Bundle Patterns (the 5 bundle types and their rationale)
- [x] Write section 3: Design Principles (functional cohesion, 2-8 components, domain clustering)
- [x] Write section 4: Bundle Structure (directory layout and plugin.json format)
- [x] Write section 5: Component Distribution (which components in which bundles)
- [x] Write section 6: Extensibility (domain-clustered pattern for future bundles)
- [x] Write section 7: Installation Model (how users install and use bundles)
- [x] Write section 8: Cross-References (xref links to other architecture docs)
- [x] Read existing `claude/doc/README.adoc`
- [x] Update README.adoc to reference bundling-architecture.adoc
- [x] Read existing `claude/doc/plugin-architecture.adoc` (if exists)
- [x] Add xref links from plugin-architecture.adoc to bundling-architecture.adoc if relevant
- [x] Verify document length approximately 250-350 lines
- [x] Verify no duplication of analysis content (focused on architecture only)
- [x] Verify AsciiDoc formatting with blank lines before lists
- [x] NO git commit needed (will be done at end of all tasks)

**Acceptance Criteria:**
- Document exists at `claude/doc/bundling-architecture.adoc`
- Follows AsciiDoc conventions (`:toc: left`, `:sectnums:`, etc.)
- Contains all 8 required sections listed above
- Cross-references other architecture documents using xref syntax
- Document length between 250-350 lines
- No duplication of analysis content from BUNDLING-ANALYSIS.md
- Focused on current architecture decisions (prescriptive, not exploratory)
- `claude/doc/README.adoc` updated with reference to new document
- AsciiDoc formatting correct (blank lines before all lists)

---

## Completion Criteria

All tasks above must be marked `[x]` before the bundling implementation is considered complete.

**Final verification:**
1. All 5 plugin bundle structures created with correct manifests
2. All component dependencies updated to reference bundled paths
3. marketplace.json updated with 5 new bundle entries
4. All 5 bundle README files created with complete documentation
5. Local installation tested successfully for all bundles
6. Backward compatibility maintained with deprecation notices
7. Architecture document created and integrated with documentation

**Quality Gates:**
- Zero broken references in updated components (grep verification)
- All JSON files validate (jq passes on all plugin.json and marketplace.json)
- All bundles install without errors (tested locally)
- Architecture document follows AsciiDoc style guidelines
- Deprecation notices clear and helpful
- All acceptance criteria for all 7 tasks verified

**Final Step:**
- After ALL tasks complete and ALL acceptance criteria verified, create git commit with message describing bundling implementation

---

**Plan created by:** issue-manager agent
**Date:** 2025-10-28
**Total tasks:** 7
