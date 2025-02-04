# Commit LLM Rules to Memory

## Command: [6] cp: commit llm-rules to memory

### Purpose
Performs a definitive one-time transfer of @llm-rules into memories. Once executed successfully, these memories become the authoritative source of truth, eliminating the need to regularly check @llm-rules for updates.

Note: This command is complementary to [7] `cp: persist memory to llm-rules`, which handles the reverse flow of persisting memory content to documentation.

### Process Steps

1. Rules Analysis
   - Scan all files in @llm-rules directory
   - Create structured representation of:
     * Command definitions
     * Process steps
     * Success criteria
     * Integration points
     * Constraints and rules

2. Memory Collection
   - List all existing memories containing "from llm-rules"
   - Create mapping between rules and memories
   - Identify:
     * Rules without memory representation
     * Memories without rule representation

3. Memory Creation/Update
   - For each rule without memory:
     * Create new memory with:
       - Title: "[Rule Name] from llm-rules"
       - Content: Exact rule content
       - Tags: ["from_llm_rules", "rule_type"]
       - CorpusNames: Relevant corpus names
   - For each existing memory needing update:
     * Update content to match current rules
     * Preserve existing metadata
     * Add "from llm-rules" if missing

4. Completeness Verification
   - For each rule in @llm-rules:
     * Verify corresponding memory exists
     * Check content matches exactly
     * Validate all aspects are covered

5. Exactness Verification
   - For each memory with "from llm-rules":
     * Compare with source rule
     * Verify no information loss
     * Check for unintended modifications

6. Orphaned Memory Review
   - Identify memories with "from llm-rules" without matching rule
   - For each orphaned memory:
     * Document:
       - Memory content
       - Last update time
       - Proposed action:
         1. Delete if obsolete
         2. Update if rule moved/renamed
         3. Keep if still relevant
   - Present findings to user

### Memory Creation Guidelines

1. Title Format
   - Must contain "from llm-rules"
   - Should be descriptive and match rule name
   - Example: "Java Maintenance Process from llm-rules"

2. Content Requirements
   - Exact copy of rule content
   - No interpretation or summarization
   - Include all:
     * Process steps
     * Success criteria
     * Constraints
     * Integration points

3. Tagging Requirements
   - Must include "from_llm_rules"
   - Additional tags based on:
     * Rule type (e.g., "maintenance", "documentation")
     * Command type (e.g., "java", "sonar")
     * Process stage (e.g., "prepare", "finalize")

### Success Criteria
1. Every rule has corresponding memory
2. All memories exactly match rules
3. No information loss in memories
4. All memories properly tagged
5. Orphaned memories reviewed
6. User notified of any discrepancies

### Important Notes
1. This is a one-time definitive transfer
2. After successful execution, memories become the source of truth
3. No need to check @llm-rules for future updates
4. Any future changes should be made directly to memories

### Error Prevention
1. Never modify rule content during memory creation
2. Preserve existing memory metadata
3. Document all discrepancies
4. Wait for user review of orphaned memories
5. Maintain audit trail of changes
6. Ensure complete transfer before finalizing
