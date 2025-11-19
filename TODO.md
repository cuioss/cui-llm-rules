# Command Diagnosis TODO

## CRITICAL - Missing/Invalid YAML Frontmatter

- [ ] doc-review-technical-docs.md - Add complete YAML frontmatter (name, description)
- [ ] doc-review-single-asciidoc.md - Add 'name' field to YAML
- [ ] js-maintain-tests.md - Add 'description' field to YAML
- [ ] java-refactor-code.md - Add 'description' field to YAML
- [ ] js-fix-jsdoc.md - Add 'model' field to YAML
- [ ] java-implement-code.md - Add 'parameters' field to YAML

## CRITICAL - Architectural Violations

- [ ] plugin-diagnose-metadata.md:89 - Fix reference to cui-requirements:cui-maintain-requirements (it's a COMMAND not AGENT)
- [ ] plugin-diagnose-skills.md:85 - Fix reference to non-existent "diagnose-skill" agent

## CRITICAL - BLOATED Commands (>500 lines, needs restructuring)

- [ ] plugin-inventory.md (663 lines) - Extract to skills, fix wrong CONTINUOUS IMPROVEMENT pattern
- [ ] plugin-verify-marketplace.md (585 lines) - Extract to skills, fix wrong CONTINUOUS IMPROVEMENT pattern
- [ ] plugin-diagnose-skills.md (563 lines) - Extract to skills
- [ ] plugin-update-agent.md (556 lines) - Extract to skills, remove duplicate content

## ~~WARNING - Missing CONTINUOUS IMPROVEMENT RULE~~

**FALSE POSITIVE - All 31 analyzed commands have this section**
Verified: All commands in cui-plugin-development-tools, cui-frontend-expert, cui-java-expert, and cui-documentation-standards have CONTINUOUS IMPROVEMENT RULE sections

## WARNING - Wrong CONTINUOUS IMPROVEMENT Pattern (2 commands)

- [ ] plugin-inventory.md - Change from caller-reporting to self-update pattern
- [ ] plugin-verify-marketplace.md - Change from caller-reporting to self-update pattern
- [ ] js-maintain-tests.md - Change from caller-reporting to self-update pattern

## WARNING - LARGE Commands (400-500 lines, monitor for bloat)

- [ ] plugin-create-bundle.md (447 lines)
- [ ] plugin-maintain-readme.md (445 lines)
- [ ] plugin-diagnose-agents.md (489 lines)
- [ ] plugin-update-command.md (434 lines)
- [ ] java-implement-code.md (487 lines)

## WARNING - Duplicate Content

- [ ] plugin-diagnose-agents.md
- [ ] plugin-diagnose-commands.md
- [ ] plugin-maintain-readme.md
- [ ] plugin-update-agent.md
- [ ] plugin-update-command.md
- [ ] java-implement-code.md
- [ ] java-fix-javadoc.md
- [ ] java-implement-tests.md

## WARNING - Over-specification

- [ ] plugin-diagnose-commands.md
- [ ] js-enforce-eslint.md
- [ ] js-fix-jsdoc.md
- [ ] java-implement-code.md
- [ ] java-fix-javadoc.md

## WARNING - Missing Error Handling

- [ ] js-enforce-eslint.md
- [ ] js-generate-coverage.md
- [ ] java-implement-code.md
- [ ] java-refactor-code.md

## WARNING - Ambiguous Instructions

- [ ] doc-review-single-asciidoc.md
- [ ] doc-review-technical-docs.md
- [ ] js-fix-jsdoc.md
- [ ] js-maintain-tests.md
- [ ] java-implement-code.md
- [ ] java-refactor-code.md

## WARNING - Missing Parameter Validation

- [ ] doc-review-single-asciidoc.md
- [ ] doc-review-technical-docs.md
- [ ] js-enforce-eslint.md
- [ ] js-fix-jsdoc.md
- [ ] js-generate-coverage.md
- [ ] java-refactor-code.md