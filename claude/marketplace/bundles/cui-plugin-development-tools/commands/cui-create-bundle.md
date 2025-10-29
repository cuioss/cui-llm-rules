---
name: cui-create-bundle
description: Create a new marketplace bundle with proper structure, plugin.json, and documentation
---

# Bundle Creation Wizard

Create a new, well-structured marketplace bundle with proper plugin manifest, directory structure, and comprehensive documentation.

## PARAMETERS

- **scope=marketplace** (default and ONLY option): Create bundle in marketplace (~/git/cui-llm-rules/claude/marketplace/bundles/)

**Note**: Bundles only exist in marketplace scope. Global and project scopes don't use bundles (flat directory structure).

## WORKFLOW INSTRUCTIONS

### Step 1: Display Welcome and Overview

Display:
```
╔════════════════════════════════════════════════════════════╗
║              Bundle Creation Wizard                        ║
╔════════════════════════════════════════════════════════════╝
║
║ This wizard will create a new marketplace bundle with:
║ - Proper directory structure (agents/, commands/, skills/)
║ - Valid plugin.json manifest
║ - Comprehensive README.md
║ - Naming conventions and best practices
║
║ Bundles are collections of related agents, commands, and
║ skills that work together for a specific purpose.
║
║ Let's begin!
║
╚════════════════════════════════════════════════════════════

Ready to start? Enter 'y' to continue:
```

Wait for user acknowledgment.

### Step 2: Collect Bundle Information

#### Question 2.1: Bundle Name

```
[Question 1/7] What is the bundle name?

Naming Convention:
- Use lowercase with hyphens
- Start with "cui-" prefix (recommended for CUI marketplace)
- Be descriptive of purpose
- Examples:
  - cui-project-quality-gates (build and quality checks)
  - cui-pull-request-workflow (PR management)
  - cui-documentation-standards (doc review tools)
  - cui-issue-implementation (issue workflow)

Bundle name:
```

Store response as `bundle_name`.

**Validation:**
- No spaces, lowercase, hyphens only
- Check if bundle already exists at: `~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/`
- If exists, display error and ask for different name

#### Question 2.2: Bundle Display Name

```
[Question 2/7] What is the display name?

This is the human-readable title shown in documentation and listings.

Examples:
- "CUI Project Quality Gates"
- "CUI Pull Request Workflow"
- "CUI Documentation Standards"

Display name:
```

Store response as `display_name`.

#### Question 2.3: Bundle Purpose

```
[Question 3/7] What is this bundle's purpose?

Provide a clear, 1-2 sentence description of what this bundle does.

Example:
"Provides tools for building, testing, and verifying Java projects with
Maven, ensuring code quality and test coverage standards are met."

Your purpose:
```

Store response as `purpose`.
Validate: 20-300 characters.

#### Question 2.4: Bundle Category

```
[Question 4/7] What category does this bundle belong to?

1. Development Tools (build, test, quality)
2. Workflow Automation (PR, issues, CI/CD)
3. Documentation (review, generation, standards)
4. Code Analysis (review, refactoring, patterns)
5. Project Setup (scaffolding, configuration)
6. Other (specify)

Enter 1-6:
```

Store response as `category`.

If "Other", prompt:
```
Specify category:
```

#### Question 2.5: Bundle Components

```
[Question 5/7] What components will this bundle include?

Select all that apply:
1. Agents (autonomous task executors)
2. Commands (slash commands for workflows)
3. Skills (knowledge bases and standards)

Enter as comma-separated numbers (e.g., "1,2,3" for all):
```

Store response, parse into `include_agents`, `include_commands`, `include_skills` booleans.

#### Question 2.6: Author Information

```
[Question 6/7] Author information

Author name (or organization):
```

Store as `author_name`.

```
Author email (optional, press Enter to skip):
```

Store as `author_email` (may be empty).

#### Question 2.7: Version and License

```
[Question 7/7] Version and license information

Initial version (default: 0.1.0):
```

Store as `version` (default to "0.1.0" if empty).
Validate: Must follow semver format (X.Y.Z).

```
License (default: MIT):
```

Store as `license` (default to "MIT" if empty).

### Step 3: Generate Bundle Structure

#### Step 3.1: Create Directory Structure

Create bundle directories:

```bash
mkdir -p ~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}
mkdir -p ~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/.claude-plugin
mkdir -p ~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/agents
mkdir -p ~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/commands
mkdir -p ~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/skills
```

Display progress:
```
Creating bundle structure...
✅ Created: ~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/
✅ Created: .claude-plugin/
✅ Created: agents/
✅ Created: commands/
✅ Created: skills/
```

#### Step 3.2: Generate plugin.json

Create: `~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/.claude-plugin/plugin.json`

**Content:**
```json
{
  "name": "{bundle_name}",
  "displayName": "{display_name}",
  "version": "{version}",
  "description": "{purpose}",
  "author": {
    "name": "{author_name}"{if author_email: ,
    "email": "{author_email}"}
  },
  "license": "{license}",
  "category": "{category}",
  "homepage": "https://github.com/cuioss/cui-llm-rules/tree/main/claude/marketplace/bundles/{bundle_name}",
  "repository": {
    "type": "git",
    "url": "https://github.com/cuioss/cui-llm-rules.git"
  },
  "components": {
    "agents": {if include_agents: []{else: null},
    "commands": {if include_commands: []{else: null},
    "skills": {if include_skills: []{else: null}
  },
  "keywords": [
    "cui",
    "{category}",
    "marketplace"
  ],
  "engines": {
    "claude-code": ">=1.0.0"
  }
}
```

Display:
```
✅ Generated: .claude-plugin/plugin.json
```

#### Step 3.3: Generate README.md

Create: `~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/README.md`

**Content:**
```markdown
# {display_name}

{purpose}

## Overview

This bundle provides {expanded description based on category and components}.

## Components

{If include_agents:}
### Agents

Agents in this bundle:

*Add agents here as they are created*

- **agent-name** - Description of what this agent does
{End if}

{If include_commands:}
### Commands

Commands in this bundle:

*Add commands here as they are created*

- **/command-name** - Description of what this command does
{End if}

{If include_skills:}
### Skills

Skills in this bundle:

*Add skills here as they are created*

- **skill-name** - Description of what this skill provides
{End if}

## Installation

This bundle is part of the CUI marketplace and can be installed via:

```bash
# Clone the repository (if not already done)
git clone https://github.com/cuioss/cui-llm-rules.git

# Navigate to marketplace bundles
cd cui-llm-rules/claude/marketplace/bundles

# The bundle is at: {bundle_name}/
```

## Usage

### For Users

{If include_commands:}
**Commands**: Invoke commands directly in Claude Code:
```
/cui-command-name parameters
```
{End if}

{If include_agents:}
**Agents**: Agents are automatically activated by Claude Code when appropriate based on task context.
{End if}

{If include_skills:}
**Skills**: Skills are automatically loaded by agents that reference them.
{End if}

### For Developers

To add components to this bundle:

{If include_agents:}
**Create an agent**:
```
/cui-create-agent scope=marketplace
# Select "{bundle_name}" as the bundle
```
{End if}

{If include_commands:}
**Create a command**:
```
/cui-create-command scope=marketplace
# Select "{bundle_name}" as the bundle
```
{End if}

{If include_skills:}
**Create a skill**:
```
/cui-create-skill scope=marketplace
# Select "{bundle_name}" as the bundle
```
{End if}

## Architecture

### Bundle Structure

```
{bundle_name}/
├── .claude-plugin/
│   └── plugin.json          # Bundle manifest
{If include_agents:}
├── agents/
│   └── *.md                 # Agent definitions
{End if}
{If include_commands:}
├── commands/
│   └── *.md                 # Command definitions
{End if}
{If include_skills:}
├── skills/
│   └── */                   # Skill directories
│       ├── SKILL.md         # Skill definition
│       ├── standards/       # Standards files
│       └── README.md        # Skill documentation
{End if}
└── README.md                # This file
```

### Design Principles

{Based on category, provide relevant design principles:}

{If category = "Development Tools":}
- Automated quality checks
- Build verification
- Test coverage enforcement
- Consistent build processes
{End if}

{If category = "Workflow Automation":}
- Streamlined developer workflows
- Reduced manual steps
- Consistent processes
- Integration with development tools
{End if}

{If category = "Documentation":}
- Clear documentation standards
- Automated validation
- Consistency enforcement
- Accessibility best practices
{End if}

{If category = "Code Analysis":}
- Pattern recognition
- Best practices enforcement
- Code quality improvement
- Refactoring guidance
{End if}

{If category = "Project Setup":}
- Consistent project structure
- Best practice scaffolding
- Configuration management
- Dependency management
{End if}

## Dependencies

{If no dependencies yet:}
Currently no dependencies. Add dependencies here as needed:

```json
{
  "dependencies": {
    "other-bundle-name": "^1.0.0"
  }
}
```
{End if}

## Configuration

{Placeholder for bundle-specific configuration}

Bundle-specific configuration (if needed) can be added to:
- `.claude/run-configuration.md` (project-specific)
- Component-specific configuration in individual agent/command files

## Development

### Adding New Components

1. Use creation wizards:
   - `/cui-create-agent` for agents
   - `/cui-create-command` for commands
   - `/cui-create-skill` for skills

2. Update this README.md with component descriptions

3. Test components:
   - `/cui-diagnose-agents` for agents
   - `/cui-diagnose-commands` for commands
   - `/cui-diagnose-skills` for skills

4. Validate entire bundle:
   - `/cui-diagnose-bundle {bundle_name}`

### Quality Standards

All components must meet:
- ✅ Proper YAML frontmatter
- ✅ Clear documentation
- ✅ Appropriate tool access
- ✅ Integration with other components
- ✅ Zero critical issues in diagnosis

### Testing

Test the bundle:

```bash
# Test individual components
/cui-diagnose-agents scope=marketplace
/cui-diagnose-commands scope=marketplace
/cui-diagnose-skills scope=marketplace

# Test entire bundle integration
/cui-diagnose-bundle {bundle_name}
```

## Contributing

To contribute to this bundle:

1. Create components using creation wizards
2. Follow CUI coding standards
3. Add comprehensive documentation
4. Test thoroughly
5. Run quality checks
6. Submit for review

## Troubleshooting

### Common Issues

**Components not discovered**:
- Check YAML frontmatter is valid
- Verify file naming conventions
- Ensure bundle is in correct location

**Tool access issues**:
- Review tool permissions in component frontmatter
- Check for missing approvals
- Use appropriate tool restrictions

**Integration problems**:
- Verify cross-references are valid
- Check for circular dependencies
- Ensure proper loading order

## Version History

### Version {version} (Initial Release)

- Initial bundle structure created
- Ready for component development

## License

{license}

## Support

For issues, questions, or contributions:
- Repository: https://github.com/cuioss/cui-llm-rules
- Bundle: claude/marketplace/bundles/{bundle_name}/

## Acknowledgments

{Placeholder for acknowledgments}

---

*Generated by /cui-create-bundle - CUI Plugin Development Tools*
```

Display:
```
✅ Generated: README.md
```

#### Step 3.4: Create Component README Templates

**If include_agents = true:**

Create: `~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/agents/README.md`

```markdown
# Agents

This directory contains agents for the {display_name} bundle.

## Creating New Agents

Use the agent creation wizard:

```bash
/cui-create-agent scope=marketplace
# Select "{bundle_name}" as the bundle
```

## Agent Guidelines

All agents in this bundle should:
- Follow the bundle's purpose: {purpose}
- Use appropriate tool access
- Include comprehensive documentation
- Integrate with other bundle components
- Pass quality checks (/cui-diagnose-agents)

## Available Agents

*Add agents here as they are created*

### agent-name

**Purpose**: {agent purpose}

**Tools**: {tool list}

**Usage**: {when to invoke this agent}

---

*Add more agents as they are developed*
```

**If include_commands = true:**

Create: `~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/commands/README.md`

```markdown
# Commands

This directory contains slash commands for the {display_name} bundle.

## Creating New Commands

Use the command creation wizard:

```bash
/cui-create-command scope=marketplace
# Select "{bundle_name}" as the bundle
```

## Command Guidelines

All commands in this bundle should:
- Follow the bundle's purpose: {purpose}
- Have clear, unambiguous workflows
- Include parameter validation
- Provide comprehensive examples
- Pass quality checks (/cui-diagnose-commands)

## Available Commands

*Add commands here as they are created*

### /cui-command-name

**Purpose**: {command purpose}

**Parameters**: {parameter list}

**Usage**:
```
/cui-command-name param1=value param2=value
```

---

*Add more commands as they are developed*
```

**If include_skills = true:**

Create: `~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/skills/README.md`

```markdown
# Skills

This directory contains skills for the {display_name} bundle.

## Creating New Skills

Use the skill creation wizard:

```bash
/cui-create-skill scope=marketplace
# Select "{bundle_name}" as the bundle
```

## Skill Guidelines

All skills in this bundle should:
- Follow the bundle's purpose: {purpose}
- Use 'allowed-tools' (not 'tools') in YAML frontmatter
- Organize standards logically
- Use relative paths only
- Pass quality checks (/cui-diagnose-skills)

## Available Skills

*Add skills here as they are created*

### skill-name

**Purpose**: {skill purpose}

**Standards**: {count} files covering {topics}

**Tool Access**: {allowed-tools list}

---

*Add more skills as they are developed*
```

Display:
```
✅ Created: agents/README.md
✅ Created: commands/README.md
✅ Created: skills/README.md
```

### Step 4: Display Creation Summary

```
╔════════════════════════════════════════════════════════════╗
║          Bundle Created Successfully!                      ║
╔════════════════════════════════════════════════════════════╝

Bundle: {bundle_name}
Display Name: {display_name}
Location: ~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/

Structure Created:
✅ .claude-plugin/plugin.json (bundle manifest)
✅ README.md (comprehensive documentation)
{If include_agents: ✅ agents/ directory with README}
{If include_commands: ✅ commands/ directory with README}
{If include_skills: ✅ skills/ directory with README}

Configuration:
- Version: {version}
- License: {license}
- Category: {category}
- Author: {author_name}

Next Steps:
1. Review and customize README.md
2. Add components using creation wizards:
{If include_agents:   - /cui-create-agent scope=marketplace}
{If include_commands:   - /cui-create-command scope=marketplace}
{If include_skills:   - /cui-create-skill scope=marketplace}
3. Update component README files as you add items
4. Validate bundle: /cui-diagnose-bundle {bundle_name}

╚════════════════════════════════════════════════════════════
```

### Step 5: Offer to Create First Component

Display:
```
Would you like to create the first component now?

1. Create an agent
2. Create a command
3. Create a skill
4. No, I'll do it later

Enter 1, 2, 3, or 4:
```

**If 1:** Invoke `/cui-create-agent scope=marketplace` with bundle_name pre-selected
**If 2:** Invoke `/cui-create-command scope=marketplace` with bundle_name pre-selected
**If 3:** Invoke `/cui-create-skill scope=marketplace` with bundle_name pre-selected
**If 4:** Continue to completion

### Step 6: Final Completion

```
╔════════════════════════════════════════════════════════════╗
║          Setup Complete!                                   ║
╔════════════════════════════════════════════════════════════╝

Your new bundle is ready: {bundle_name}

The bundle follows marketplace best practices:
✅ Proper plugin.json manifest
✅ Complete directory structure
✅ Comprehensive README documentation
✅ Component templates ready
✅ Naming conventions followed
✅ Ready for component development

Location: ~/git/cui-llm-rules/claude/marketplace/bundles/{bundle_name}/

Start adding components with:
- /cui-create-agent scope=marketplace
- /cui-create-command scope=marketplace
- /cui-create-skill scope=marketplace

Running automatic bundle validation...

╚════════════════════════════════════════════════════════════
```

### Step 7: Automatic Bundle Diagnosis

**CRITICAL**: Automatically run bundle diagnosis to validate the newly created bundle.

**Execution:**

1. Use the SlashCommand tool to invoke bundle diagnosis:
   ```
   SlashCommand: /cui-diagnose-bundle {bundle_name}
   ```

2. Wait for diagnosis to complete

3. Display diagnosis results to user

**Expected Results:**

Since the bundle was just created with proper structure, diagnosis should show:
- ✅ plugin.json valid
- ✅ Directory structure complete
- ✅ README.md present
- ⚠️ No components yet (agents/, commands/, skills/ directories empty)

**If diagnosis reveals issues:**
- Display issues clearly to user
- Suggest immediate fixes if needed
- Note that these are baseline structural issues that should be addressed

**Success Message:**

```
╔════════════════════════════════════════════════════════════╗
║      Bundle Creation and Validation Complete!             ║
╔════════════════════════════════════════════════════════════╝

Bundle: {bundle_name}
Status: ✅ Validated and ready for component development

Diagnosis Results:
{summary of diagnosis results}

Next Steps:
1. Add components using creation wizards
2. Run /cui-diagnose-bundle {bundle_name} after adding components
3. Review and customize documentation

Happy bundle development! 🚀

╚════════════════════════════════════════════════════════════
```

**Benefits of Automatic Diagnosis:**
- Immediate validation of bundle structure
- Catches any issues right away
- Provides confidence that bundle is properly set up
- Demonstrates best practices (validate after creation)
- Sets expectation for regular diagnosis during development

## CRITICAL RULES

- **BUNDLES ONLY IN MARKETPLACE** - No global/project bundle concept
- **ALWAYS create .claude-plugin/plugin.json** - Required for bundle discovery
- **ALWAYS follow semver** for version numbers (X.Y.Z format)
- **ALWAYS create all three directories** (agents/, commands/, skills/) even if not immediately used
- **ALWAYS generate comprehensive README.md** - Documentation is critical
- **ALWAYS run automatic diagnosis** after creation (Step 7) - Validates structure immediately
- **VALIDATE bundle name** doesn't already exist before creating
- **USE lowercase-with-hyphens** for bundle names
- **INCLUDE "cui-" prefix** for CUI marketplace bundles (recommended)
- **GENERATE valid JSON** for plugin.json (no trailing commas, proper escaping)

## LESSONS LEARNED FROM PREVIOUS SESSIONS

### Lesson 1: Consistent Naming Conventions
**Issue**: Inconsistent bundle naming made marketplace browsing difficult
**Solution**: Enforce "cui-" prefix and kebab-case naming
**Prevention**: Wizard validates and suggests proper format

### Lesson 2: Complete Directory Structure
**Issue**: Creating directories on-demand led to inconsistent structure
**Solution**: Always create all three directories upfront
**Prevention**: Bundle creation creates complete structure immediately

### Lesson 3: Documentation from Day One
**Issue**: Bundles created without README led to confusion
**Solution**: Generate comprehensive README.md template
**Prevention**: README created automatically with structure guidance

### Lesson 4: Plugin Manifest Quality
**Issue**: Manual plugin.json creation had syntax errors
**Solution**: Generate valid JSON programmatically
**Prevention**: Wizard creates validated JSON structure

### Lesson 5: Scope Consistency
**Issue**: Confusion about where bundles should live
**Solution**: Bundles only in marketplace, clear scope handling
**Prevention**: Only marketplace scope supported for bundles

### Lesson 6: Integration Planning
**Issue**: Components created without considering bundle integration
**Solution**: Bundle README guides integration from start
**Prevention**: Component README templates show integration patterns

### Lesson 7: Immediate Validation
**Issue**: Bundle structural issues discovered much later during development
**Solution**: Run automatic diagnosis immediately after bundle creation
**Prevention**: Step 7 automatically validates bundle structure, catching issues early
**Benefit**: Developers get immediate feedback and confidence that bundle is properly set up

## VALIDATION RULES

Before creating bundle:

1. **Name Validation:**
   - Lowercase only
   - Hyphens for spaces
   - No special characters
   - Must not already exist
   - "cui-" prefix recommended

2. **Version Validation:**
   - Must follow semver (X.Y.Z)
   - Must be valid semantic version
   - Default: 0.1.0

3. **Path Validation:**
   - Bundle path doesn't exist
   - Parent directory accessible
   - Write permissions available

4. **JSON Validation:**
   - plugin.json is valid JSON
   - All required fields present
   - No syntax errors

5. **Structure Validation:**
   - All directories created
   - All required files present
   - README.md not empty

6. **Diagnosis Validation (Step 7):**
   - Automatically run /cui-diagnose-bundle after creation
   - Verify bundle structure is valid
   - Confirm plugin.json is properly formatted
   - Check all directories exist
   - Report any structural issues immediately

## USAGE

**Create a new marketplace bundle:**
```
/cui-create-bundle
```

**Note**: scope=marketplace is the only option (and default) for bundles.

The wizard will:
1. Guide you through configuration (7 questions)
2. Create complete bundle structure
3. Generate plugin.json and README.md
4. **Automatically validate** the bundle with /cui-diagnose-bundle
5. Report validation results

This ensures your bundle is properly structured and ready for component development.

## INTEGRATION WITH OTHER COMMANDS

After creating a bundle, use these commands to add components:

```bash
# Add an agent to the bundle
/cui-create-agent scope=marketplace
# Select your bundle name when prompted

# Add a command to the bundle
/cui-create-command scope=marketplace
# Select your bundle name when prompted

# Add a skill to the bundle
/cui-create-skill scope=marketplace
# Select your bundle name when prompted

# Validate the entire bundle (automatically run during creation, but can be run again)
/cui-diagnose-bundle your-bundle-name
```

**Note**: The bundle is automatically validated during creation (Step 7). Run diagnosis again after adding components to ensure everything integrates properly.

## MARKETPLACE CONVENTIONS

Bundles in the CUI marketplace should follow these conventions:

1. **Naming**: `cui-{purpose}-{type}`
   - Examples: cui-project-quality-gates, cui-pull-request-workflow

2. **Structure**: Standard directory layout (agents/, commands/, skills/)

3. **Documentation**: Comprehensive README with usage examples

4. **Versioning**: Semantic versioning (major.minor.patch)

5. **Licensing**: Clear license specification (default: MIT)

6. **Categories**: Use standard categories for discoverability

7. **Integration**: Components should work together cohesively
