# Memory Persistence Process

## Command: [7] cp: persist memory to llm-rules

### Purpose
Persists the content of memories to @llm-rules documentation, ensuring that memory-based knowledge is properly documented in the repository.

### Process Overview

1. Memory Analysis
   - List all active memories
   - Identify memories requiring documentation updates
   - Map memories to corresponding documentation files

2. Documentation Update
   - Identify relevant `.md` files in @llm-rules
   - Create new files if needed for new topics
   - Update existing files with memory content
   - Ensure changes follow documentation guidelines
   - Verify all references exist

3. README.adoc Update
   - Update memory files overview
   - Keep file descriptions current
   - Ensure documentation structure reflects memory organization
   - Maintain cross-references

### File Organization

Documentation follows topic-specific organization:
- `README.adoc`: Overview and structure
- `core/standards/quality-standards.md`: Quality and testing standards
- `logging.md`: Logging conventions
- `project.md`: Build and project rules
- `technologies.md`: Core technology stack
- `testing.md`: Testing practices
- Other topic-specific files as needed

### Validation Requirements

Before completing the process:
1. Verify all references exist
2. Ensure no speculative features
3. Maintain consistent terminology
4. Follow documentation structure
5. Keep changes focused and atomic
6. Verify README.adoc accuracy

### Relationship with Memory Commands

Two complementary commands manage the memory-documentation relationship:

1. `cp: persist memory to llm-rules` (This command)
   - Direction: Memory → Documentation
   - Purpose: Persist memory content to @llm-rules
   - When to use: After significant memory updates
   - Ensures: Documentation reflects current memory state

2. `cp: commit llm-rules to memory`
   - Direction: Documentation → Memory
   - Purpose: Create/update memories from @llm-rules
   - When to use: After documentation updates
   - Ensures: Memories reflect current documentation

### Success Criteria
1. All relevant memories are documented
2. Documentation structure is maintained
3. README.adoc is accurate
4. All references are valid
5. Terminology is consistent
