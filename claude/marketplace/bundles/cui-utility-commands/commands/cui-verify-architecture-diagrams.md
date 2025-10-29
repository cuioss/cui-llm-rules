---
name: cui-verify-architecture-diagrams
description: Analyze and update PlantUML diagrams to reflect current codebase state and regenerate PNG images
---

# Verify and Update PlantUML Diagrams

Analyze all PlantUML files in the specified directory (default: doc/plantuml), verify they reflect the current codebase state, and regenerate PNG images.

## Parameters
- `plantuml_dir` (optional): Path to PlantUML directory, defaults to "doc/plantuml"
- `push` (optional): When provided, automatically commits all changes with a descriptive message and pushes to remote repository after successful verification

## Process

Execute the following steps for each `.puml` file found in the directory:

### 1. Check for References
Before analyzing any diagram, check if the PNG image is referenced in documentation:
- Search for references in `**/*.adoc`, `**/*.md`, and `**/*.java` files
- Look for the PNG filename in image includes, links, and javadoc references
- If NO references are found (orphaned diagram):
  - **STOP** and prompt the user: "The diagram `{filename}` appears to be orphaned (not referenced in any .adoc, .md, or .java files). Would you like to remove both the .puml and .png files? (yes/no)"
  - **WAIT** for user approval before proceeding
  - If approved, delete both files
  - If not approved, skip to next diagram
- If references ARE found:
  - Read the surrounding context to understand the diagram's purpose
  - Use this context to improve diagram clarity and ensure it serves its documented purpose

### 2. Analyze PlantUML File
For each referenced diagram:
- Read the `.puml` file
- Identify what the diagram represents (architecture, sequence, class hierarchy, etc.)
- Determine which codebase components/classes/flows it should represent

### 3. Verify Against Current Codebase
- Search for and read the actual classes/components/flows shown in the diagram
- Compare diagram content with current implementation:
  - Class names, method signatures, fields
  - Component relationships, dependencies
  - Sequence flows, data flows
  - Architecture patterns (pipeline, factory, etc.)
- **IMPORTANT**: If you are NOT 100% confident about any aspect of the diagram or proposed changes, **ASK THE USER** for clarification before making changes

### 4. Identify Required Updates
Document what needs to change:
- Missing components/classes/methods
- Renamed or removed elements
- Changed relationships or flows
- New architecture patterns
- Outdated naming or structure

### 5. Assess Diagram Complexity
Before making updates, evaluate if the diagram is becoming too large or complex:
- If the diagram is overly complex or large:
  - **THOROUGHLY ANALYZE** potential splitting strategies:
    - Consider multiple ways to split the diagram
    - Evaluate pros and cons of each approach
    - Think about logical groupings (by layer, by feature, by lifecycle, etc.)
    - Consider impact on documentation readability
    - Assess if splitting actually improves clarity or just fragments information
  - **DOCUMENT YOUR REASONING**:
    - Present the analysis to the user
    - Show the pros and cons of each splitting approach
    - Recommend your preferred approach with justification
    - Example: "I analyzed 3 splitting approaches: (1) by validation pipeline [pros: X, cons: Y], (2) by token type [pros: A, cons: B], (3) by component layer [pros: M, cons: N]. I recommend approach (1) because..."
  - **WAIT** for user approval: "Do you approve this splitting approach? (yes/no)"
  - Only proceed with the split if user approves
  - If user declines, update the existing diagram as-is
- **If splitting is approved**:
  - Create the new `.puml` files for each split diagram
  - Generate PNG files for all new diagrams
  - **UPDATE DOCUMENTATION**: Find all `.adoc`, `.md`, and `.java` files that reference the original diagram
  - **ADD REFERENCES** to the new diagrams in appropriate documentation files
  - Explain to the user where the new diagram references were added

### 6. Update PlantUML File
- Edit the `.puml` file to reflect current architecture
- Ensure PlantUML syntax is correct
- Maintain consistent styling with existing diagrams (use `!include plantuml.skin` if present)

### 7. Generate and Verify PNG
- Generate PNG using: `plantuml {filename}.puml`
- **CRITICAL QUALITY CHECK**: Read and verify the generated PNG image:
  - Check that the image is visually sensible and clear
  - Verify there are NO errors such as:
    - **Black boxes obscuring text/labels** (common in sequence diagrams - indicates missing color settings in skin)
    - Missing links or connections
    - Broken references
    - Improper layout (overlapping text, unreadable labels)
    - Syntax error messages in the image
    - Unreadable text due to poor color contrast
  - **SPECIAL CASE - Black Boxes Over Text**:
    - This commonly occurs in sequence diagrams when participant/database colors are not defined in the skin file
    - **DIAGNOSIS STEPS**:
      1. Check if the diagram is a sequence diagram (uses `participant`, `database`, etc.)
      2. Read the `plantuml.skin` file (usually in same directory)
      3. Check if these skinparam settings exist:
         - `ParticipantBackgroundColor`
         - `ParticipantBorderColor`
         - `ParticipantFontColor`
         - For databases: `DatabaseBackgroundColor`, `DatabaseBorderColor`, `DatabaseFontColor`
      4. If missing, these are likely causing the black boxes
    - **FIX APPROACH**:
      - Add missing color definitions to `plantuml.skin`
      - Example additions:
        ```
        ' Participant settings (for sequence diagrams)
        ParticipantBackgroundColor #ECF0F1
        ParticipantBorderColor #2C3E50
        ParticipantFontColor #000000
        ```
      - Ensure consistency with existing color scheme in the skin file
      - Regenerate PNG after updating skin file
  - If errors are found:
    - Determine root cause (diagram syntax vs skin file issue)
    - Fix the `.puml` file OR the `plantuml.skin` file as appropriate
    - Regenerate the PNG
    - **REPEAT** until the image is completely correct and error-free

### 8. Repeat for All Diagrams
Continue with the next diagram until all have been processed.

## Quality Criteria
All diagrams must meet these standards:
- ✅ Accurately reflect current codebase implementation
- ✅ PNG images are visually clear and readable
- ✅ No PlantUML syntax errors visible in images
- ✅ No broken links, missing connections, or layout issues
- ✅ Proper layout without overlapping elements
- ✅ All components/classes/methods shown actually exist in the codebase
- ✅ Relationships and flows are correct
- ✅ Referenced in documentation (or explicitly approved as orphaned)

## Output
Provide a summary report:
- List of diagrams analyzed
- Changes made to each diagram
- Number of diagrams updated vs unchanged
- Any diagrams removed (with user approval)
- Any diagrams split into multiple diagrams (with user approval)
- Documentation files updated with new diagram references

## Commit and Push (Optional)
If the `push` parameter is provided:
1. Verify no PlantUML artifacts remain (PlantUML typically doesn't create persistent artifacts, but verify workspace is clean)
2. Check for any uncommitted changes (staged or unstaged)
3. If changes exist, create a commit with a descriptive message:
   - If diagrams were updated: "docs: Update PlantUML diagrams to reflect current architecture"
   - If diagrams were added/removed: Include specifics about what was added/removed
   - If documentation was updated: Mention documentation updates
4. Use the standard commit format with Claude Code footer:
   ```
   docs: Update PlantUML diagrams to reflect current architecture

   - Updated X diagrams to match current implementation
   - Split Y diagram into Z focused diagrams
   - Removed N orphaned diagrams
   - Updated documentation references in A files

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   ```
5. Push the commit to the remote repository
6. Include the commit hash and push status in the final report

## Important Notes
- **ALWAYS** ask the user if you're not 100% confident about any change
- **ALWAYS** verify generated PNG images for visual correctness and errors
- **ALWAYS** check for diagram references before analyzing
- **ALWAYS** propose diagram splits for approval before implementing
- **NEVER** remove orphaned diagrams without explicit user approval
- Use the locally installed `plantuml` tool (verify with `which plantuml`)
- Update both `.puml` source and `.png` output files
- This is a comprehensive verification task - take time to ensure accuracy
