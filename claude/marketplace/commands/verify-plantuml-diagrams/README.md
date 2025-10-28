# verify-plantuml-diagrams

Analyzes all PlantUML files in specified directory, verifies they reflect current codebase state, regenerates PNG images with quality checks, detects orphaned diagrams, and handles diagram splitting with user approval.

## Purpose

Automates PlantUML diagram maintenance by checking references, analyzing current implementation, identifying outdated elements, updating .puml files, generating PNGs with quality verification (especially black box issues), and optionally committing changes.

## Usage

```bash
# Verify diagrams in default directory (doc/plantuml)
/verify-plantuml-diagrams

# Verify diagrams in custom directory
/verify-plantuml-diagrams plantuml_dir=docs/architecture

# Verify and auto-commit/push changes
/verify-plantuml-diagrams push

# Custom directory with push
/verify-plantuml-diagrams plantuml_dir=doc/uml push
```

## What It Does

The command performs comprehensive PlantUML verification across 8 steps per diagram:

1. **Check for References** - Search documentation for PNG references, detect orphaned diagrams
2. **Analyze PlantUML File** - Read .puml, identify diagram type and components
3. **Verify Against Codebase** - Compare with actual classes/components/flows
4. **Identify Updates** - Document missing/renamed/removed/changed elements
5. **Assess Complexity** - Evaluate if diagram should be split, analyze approaches
6. **Update PlantUML File** - Edit .puml to reflect current architecture
7. **Generate & Verify PNG** - Run plantuml, check for black boxes and visual errors
8. **Repeat** - Continue for all diagrams

## Key Features

- **Orphaned Diagram Detection**: Searches .adoc, .md, .java files for PNG references
- **User Approval for Removal**: Prompts before deleting orphaned diagrams
- **Codebase Verification**: Compares diagrams with actual implementation
- **Confidence Checking**: Asks user if NOT 100% confident about changes
- **Diagram Splitting Analysis**: Thorough evaluation of splitting strategies with pros/cons
- **PNG Quality Verification**: Detects black boxes, syntax errors, layout issues
- **Black Box Fix**: Diagnoses and fixes missing participant colors in skin files
- **Documentation Updates**: Adds references to new diagrams after splitting
- **Git Integration**: Optional commit/push with descriptive messages
- **Comprehensive Report**: Summary of changes, splits, removals, documentation updates

## Parameters

### plantuml_dir (Optional)
- **Format**: `plantuml_dir=<path>`
- **Default**: `doc/plantuml`
- **Description**: Path to PlantUML directory containing .puml files
- **Examples**:
  - `docs/architecture`
  - `doc/uml`
  - `src/main/plantuml`

### push (Optional)
- **Format**: `push` (flag)
- **Description**: Automatically commits and pushes changes after successful verification
- **Usage**: `/verify-plantuml-diagrams push`
- **Default**: Changes remain uncommitted for manual review

## Workflow Detail

### Step 1: Check for References

**Before Analyzing Diagram:**
1. Search for PNG filename in:
   - `**/*.adoc` files (AsciiDoc documentation)
   - `**/*.md` files (Markdown documentation)
   - `**/*.java` files (Javadoc references)
2. Look for: image includes, links, javadoc @see tags

**If NO References Found (Orphaned):**
- **STOP** and prompt user:
  ```
  The diagram `{filename}` appears to be orphaned (not referenced in any .adoc, .md, or .java files).
  Would you like to remove both the .puml and .png files? (yes/no)
  ```
- **WAIT** for user approval
- If approved: Delete both .puml and .png files
- If not approved: Skip to next diagram

**If References ARE Found:**
- Read surrounding context to understand diagram's purpose
- Use context to improve diagram clarity
- Ensure diagram serves its documented purpose

### Step 2-3: Analyze and Verify

**Analyze PlantUML File:**
- Read .puml file
- Identify diagram type:
  - Architecture/Component diagrams
  - Sequence diagrams
  - Class diagrams
  - Data flow diagrams
  - Pipeline diagrams
- Determine which codebase components it should represent

**Verify Against Current Codebase:**
- Search for and read actual classes/components/flows
- Compare with current implementation:
  - Class names, method signatures, fields
  - Component relationships, dependencies
  - Sequence flows, data flows
  - Architecture patterns (pipeline, factory, etc.)
- **IMPORTANT**: If NOT 100% confident, **ASK USER** before changes

### Step 4: Identify Required Updates

**Document What Needs to Change:**
- Missing components/classes/methods
- Renamed or removed elements
- Changed relationships or flows
- New architecture patterns
- Outdated naming or structure

### Step 5: Assess Diagram Complexity

**Before Making Updates:**

**If Diagram is Overly Complex:**
1. **THOROUGHLY ANALYZE** potential splitting strategies:
   - Consider multiple ways to split
   - Evaluate pros and cons of EACH approach
   - Think about logical groupings:
     - By layer (presentation, business, data)
     - By feature (auth, validation, processing)
     - By lifecycle (initialization, execution, cleanup)
     - By component type (services, controllers, repositories)
   - Consider impact on documentation readability
   - Assess if splitting actually improves clarity

2. **DOCUMENT YOUR REASONING**:
   - Present analysis to user
   - Show pros and cons of each approach
   - **Example Format**:
     ```
     I analyzed 3 splitting approaches for the validation pipeline:

     (1) Split by validation pipeline stage
         Pros: Clear flow separation, easier to understand individual stages
         Cons: Loses overview of complete pipeline

     (2) Split by token type
         Pros: Natural domain grouping, reduces complexity per diagram
         Cons: Duplicates pipeline structure across diagrams

     (3) Split by component layer (preprocessing, validation, post-processing)
         Pros: Architectural clarity, aligns with code structure
         Cons: Breaks logical validation flow

     I recommend approach (1) because it maintains the sequential nature
     while reducing cognitive load. Each stage is self-contained and can
     be understood independently, yet the pipeline flow remains clear.
     ```

3. **WAIT** for user approval:
   ```
   Do you approve this splitting approach? (yes/no)
   ```

4. Only proceed with split if user approves
5. If user declines, update existing diagram as-is

**If Splitting is Approved:**
- Create new .puml files for each split diagram
- Generate PNG files for all new diagrams
- **UPDATE DOCUMENTATION**: Find all files referencing original
- **ADD REFERENCES** to new diagrams in appropriate docs
- Explain to user where new diagram references were added

### Step 6: Update PlantUML File

**Edit .puml File:**
- Reflect current architecture
- Ensure PlantUML syntax is correct
- Maintain consistent styling with existing diagrams
- Use `!include plantuml.skin` if present

### Step 7: Generate and Verify PNG (CRITICAL)

**Generate PNG:**
```bash
plantuml {filename}.puml
```

**CRITICAL QUALITY CHECK** - Read and Verify Generated PNG:

**Check for Visual Issues:**
- ✅ Image is visually sensible and clear
- ❌ **Black boxes obscuring text/labels** (common issue!)
- ❌ Missing links or connections
- ❌ Broken references
- ❌ Improper layout (overlapping text, unreadable labels)
- ❌ Syntax error messages in the image
- ❌ Unreadable text due to poor color contrast

**SPECIAL CASE - Black Boxes Over Text:**

**Common in Sequence Diagrams** when participant/database colors not defined in skin

**DIAGNOSIS STEPS:**
1. Check if diagram is sequence diagram (uses `participant`, `database`, etc.)
2. Read `plantuml.skin` file (usually in same directory)
3. Check if these skinparam settings exist:
   - `ParticipantBackgroundColor`
   - `ParticipantBorderColor`
   - `ParticipantFontColor`
   - For databases: `DatabaseBackgroundColor`, `DatabaseBorderColor`, `DatabaseFontColor`
4. If missing → Likely causing black boxes

**FIX APPROACH:**
- Add missing color definitions to `plantuml.skin`
- **Example additions:**
  ```
  ' Participant settings (for sequence diagrams)
  ParticipantBackgroundColor #ECF0F1
  ParticipantBorderColor #2C3E50
  ParticipantFontColor #000000

  ' Database settings
  DatabaseBackgroundColor #D5E8D4
  DatabaseBorderColor #82B366
  DatabaseFontColor #000000
  ```
- Ensure consistency with existing color scheme
- Regenerate PNG after updating skin file

**If Errors Found:**
- Determine root cause (diagram syntax vs skin file issue)
- Fix .puml file OR plantuml.skin file as appropriate
- Regenerate PNG
- **REPEAT** until image is completely correct and error-free

### Step 8: Repeat for All Diagrams

Continue with next diagram until all processed.

## Quality Criteria

All diagrams must meet these standards:
- ✅ Accurately reflect current codebase implementation
- ✅ PNG images are visually clear and readable
- ✅ No PlantUML syntax errors visible in images
- ✅ No broken links, missing connections, or layout issues
- ✅ Proper layout without overlapping elements
- ✅ All components/classes/methods shown actually exist in codebase
- ✅ Relationships and flows are correct
- ✅ Referenced in documentation (or explicitly approved as orphaned)

## Output Report

**Comprehensive Summary:**
- List of diagrams analyzed
- Changes made to each diagram
- Number of diagrams updated vs unchanged
- Any diagrams removed (with user approval)
- Any diagrams split into multiple diagrams (with user approval)
- Documentation files updated with new diagram references

**Example:**
```
==================================================
PlantUML Diagram Verification Complete
==================================================

Diagrams Analyzed: 8
- Updated: 5 diagrams
- Unchanged: 2 diagrams
- Removed: 1 diagram (orphaned, user approved)
- Split: 1 diagram → 3 focused diagrams

Changes by Diagram:
1. architecture-overview.puml
   - Updated component relationships
   - Added new validation service
   - PNG regenerated successfully

2. validation-pipeline.puml
   - SPLIT into 3 diagrams (user approved):
     - validation-pipeline-stage1.puml (preprocessing)
     - validation-pipeline-stage2.puml (validation)
     - validation-pipeline-stage3.puml (post-processing)
   - Documentation updated in architecture.adoc
   - All PNGs verified

3. orphaned-legacy-flow.puml
   - REMOVED (no references found, user approved)

Documentation Updates:
- architecture.adoc: Added 3 new diagram references
- README.md: Updated validation pipeline reference

PNG Quality:
- All images verified visually correct
- Fixed black box issue in validation-pipeline-stage2.puml
  (added missing ParticipantBackgroundColor to plantuml.skin)
```

## Commit and Push (Optional)

**If `push` Parameter Provided:**

1. **Verify Workspace Clean**:
   - Check no PlantUML artifacts remain
   - Verify workspace is clean

2. **Check for Changes**:
   - Look for uncommitted changes (staged or unstaged)

3. **Create Commit**:
   - If diagrams updated: "docs: Update PlantUML diagrams to reflect current architecture"
   - If diagrams added/removed: Include specifics
   - If documentation updated: Mention documentation updates

4. **Commit Format**:
   ```
   docs: Update PlantUML diagrams to reflect current architecture

   - Updated X diagrams to match current implementation
   - Split Y diagram into Z focused diagrams
   - Removed N orphaned diagrams
   - Updated documentation references in A files

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>
   ```

5. **Push to Remote**:
   ```bash
   git push
   ```

6. **Include in Report**:
   - Commit hash
   - Push status

## Important Notes

### User Approval Required:
- ❗ **ALWAYS** ask if NOT 100% confident about any change
- ❗ **ALWAYS** propose diagram splits for approval before implementing
- ❗ **NEVER** remove orphaned diagrams without explicit user approval

### Quality Verification:
- ✅ **ALWAYS** verify generated PNG images for visual correctness
- ✅ **ALWAYS** check for diagram references before analyzing
- ✅ **ALWAYS** check for black boxes obscuring text
- ✅ **REPEAT** PNG generation until completely error-free

### Tools:
- Uses locally installed `plantuml` tool
- Verify with: `which plantuml`
- Updates both .puml source and .png output files

### Comprehensive Task:
- This is thorough verification - take time to ensure accuracy
- Multiple iterations may be needed for PNG quality
- User approval ensures correct changes

## Expected Duration

- **Small Project** (3-5 diagrams, no splits): 5-10 minutes
  - Reference checking: 30 sec per diagram
  - Codebase verification: 1-2 min per diagram
  - PNG generation: 10-20 sec per diagram
  - Quality checks: 30 sec per diagram

- **Medium Project** (10-15 diagrams, 1-2 splits): 15-30 minutes
  - Reference checking: 30 sec per diagram
  - Codebase verification: 2-3 min per diagram
  - Splitting analysis: 3-5 min per split
  - PNG generation: 10-20 sec per diagram
  - Quality checks with fixes: 1-2 min per diagram

- **Large Project** (20+ diagrams, multiple splits): 30-60 minutes
  - Reference checking: 30 sec per diagram
  - Codebase verification: 2-4 min per diagram
  - Splitting analysis: 5-10 min per split
  - PNG generation: 10-20 sec per diagram
  - Quality checks with fixes: 2-3 min per diagram
  - Documentation updates: 2-5 min

## Integration

Use this command:
- After significant architecture changes
- Before releasing documentation updates
- As part of architecture review process
- When diagrams appear outdated
- After refactoring major components
- Periodically to maintain diagram accuracy

Often used with:
- Architecture review meetings
- Documentation sprints
- Release preparation
- Code refactoring efforts

## Example Diagram Splitting Analysis

```
PlantUML Diagram Splitting Analysis
====================================

Diagram: authentication-flow.puml (Current: 85 lines, 12 participants)

Complexity Assessment:
- Diagram is large and complex
- Multiple distinct phases visible
- Could benefit from splitting

Splitting Approaches Analyzed:

(1) Split by Authentication Method
    Diagrams: auth-oauth.puml, auth-jwt.puml, auth-saml.puml
    Pros:
    - Clear separation by authentication type
    - Each diagram focused on specific flow
    - Easy to document per-method details
    Cons:
    - Loses overview of overall auth architecture
    - May duplicate common steps across diagrams
    - Harder to see authentication strategy pattern

(2) Split by Lifecycle Phase
    Diagrams: auth-initialization.puml, auth-validation.puml, auth-token-refresh.puml
    Pros:
    - Natural flow progression
    - Aligns with code structure (init, validate, refresh)
    - Each phase is self-contained
    Cons:
    - Splits related logic across diagrams
    - Method-specific details fragmented
    - May need to reference multiple diagrams for complete flow

(3) Split by Layer
    Diagrams: auth-presentation.puml, auth-business.puml, auth-data.puml
    Pros:
    - Architectural clarity
    - Aligns with layered architecture
    - Clear separation of concerns
    Cons:
    - Loses authentication flow continuity
    - User journey fragmented
    - May be confusing for flow understanding

Recommendation: Approach (2) - Split by Lifecycle Phase

Reasoning:
The lifecycle phase split maintains the sequential nature of authentication
while reducing cognitive load. Each phase (initialization, validation, refresh)
is self-contained and can be understood independently, yet the overall flow
remains clear when diagrams are reviewed in order. This approach aligns with
how authentication is implemented in the codebase and makes each diagram
actionable for developers working on specific phases.

Do you approve this splitting approach? (yes/no)
```

## Notes

- **Reference checking prevents orphaned diagrams** from accumulating
- **User approval required** for all uncertain changes and diagram removals
- **Splitting analysis must be thorough** with pros/cons for each approach
- **PNG quality verification is critical** - especially black box detection
- **Black box issue is common** in sequence diagrams with incomplete skin files
- **Documentation updates automatic** when diagrams are split
- **Git integration optional** - manual review recommended for first run
- **Comprehensive task** - accuracy over speed

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
