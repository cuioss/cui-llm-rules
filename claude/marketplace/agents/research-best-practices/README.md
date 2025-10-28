# Research Best Practices Agent

Performs comprehensive web research on any topic to find best practices, recommendations, and guidelines from authoritative sources with confidence scoring.

## Purpose

This agent automates in-depth web research by:
- Executing strategic web searches for best practices
- Fetching and analyzing content from top 10-15 sources
- Aggregating findings with source quality scoring
- Calculating confidence levels based on source quality and consensus
- Identifying contradictions across sources
- Maintaining complete reference trails for all findings
- Providing evidence-based, factual research results

## Usage

```bash
# Research a topic
"Research on TOPIC"

# Find best practices
"Best-Practices for TOPIC"

# Deep dive research
"Do a deep research for TOPIC"

# Gather information
"Find information about TOPIC"

# Investigate best practices
"Investigate TOPIC best practices"

# Find recommendations
"What are the recommendations for TOPIC"
```

## How It Works

1. **Execute Web Search**: Searches for "{TOPIC} Best-Practices 2025" with fallback strategies
2. **Fetch Top Links**: Fetches content from 10-15 prioritized sources (official docs, major tech blogs, etc.)
3. **Aggregate Findings**: Deduplicates and groups similar practices from multiple sources
4. **Calculate Confidence**: Scores source quality and determines confidence levels (HIGH/MEDIUM/LOW)
5. **Cross-Reference Validation**: Identifies contradictions and conflicts across sources
6. **Structure Results**: Formats findings with confidence justification, quality scores, and references

## Confidence Level System

**HIGH Confidence:**
- Mentioned in official documentation (quality score ≥3) OR
- Total quality score ≥6 (3+ sources including major company blog) OR
- 5+ sources with average quality score ≥1

**MEDIUM Confidence:**
- Total quality score 3-5 (2 sources including company blog) OR
- 3-4 sources with average quality score ≥0.7

**LOW Confidence:**
- Single source OR
- Total quality score <3 OR
- 2 sources (both individual blogs/forums with quality <2)

## Source Quality Scoring

- Official documentation: +3 points
- Major tech company blog: +2 points
- Individual expert blog: +1 point
- Forum/community: +0.5 points
- Recency multiplier: 2025 content ×1.0, 2024 content ×0.8, older ×0.6
- Snippet-only sources: ×0.7 multiplier

## Priority Domains

The agent prioritizes fetching from:
- Official documentation sites (docs.*, *.readthedocs.io, *.github.io/docs)
- Major tech company blogs (anthropic.com, microsoft.com, google.com, amazon.com, meta.com)
- Academic/research institutions (.edu, .ac.*)
- Recognized expert blogs and established tech publications

## Critical Rules

- **NEVER invent or fabricate results** - All findings from fetched sources only
- **NEVER be creative or interpretive** - Report facts as stated, no synthesis
- **ALWAYS provide confidence level** - Every finding includes justified confidence
- **ALWAYS maintain source references** - Every finding links to specific URLs
- **PREFER consensus** - Highlight when multiple sources converge
- **FACT-BASED ONLY** - No speculation, no assumptions, no interpretation

## Examples

### Example 1: Research Java Best Practices

```
User: "Research on Java logging best practices"

Agent:
- Searches: "Java logging Best-Practices 2025"
- Fetches 12 sources (10 successful, 2 snippet-only)
- Identifies 8 unique best practices
- HIGH confidence (4): Use SLF4J, Structured logging, Log levels, Avoid logging sensitive data
- MEDIUM confidence (3): Performance considerations, Log rotation, Contextual logging
- LOW confidence (1): Custom log formatters
- Conflicting: None
- Duration: 2 minutes 15 seconds
```

### Example 2: Research with Subtopic Deep Dive

```
User: "Best-Practices for REST API design"

Agent:
- Primary search: "REST API design Best-Practices 2025"
- Fetches 15 sources (13 successful, 2 failed)
- Identifies "Error handling" mentioned in 5 sources but lacks detail
- Subtopic deep dive: "REST API error handling details 2025"
- Fetches 3 additional sources for error handling specifics
- Total: 12 unique best practices
- HIGH confidence (6), MEDIUM (4), LOW (2)
- Conflicting (1): PUT vs PATCH usage
- Duration: 3 minutes 40 seconds
```

### Example 3: Limited Results

```
User: "Research on obscure-framework-v0.1 best practices"

Agent:
- Primary search: 2 results
- Fallback 1 ("recommendations 2025"): 1 result
- Fallback 2 ("guidelines official docs"): 0 results
- Fallback 3 ("industry standards"): 0 results
- Total: 3 sources fetched
- Identifies 2 unique best practices
- HIGH confidence (0), MEDIUM (0), LOW (2)
- Notes limitation: Limited sources available
- Duration: 1 minute 10 seconds
```

## Subtopic Deep Dive

**Triggered when:**
- Finding appears in 3+ sources but lacks detail
- Missing examples, implementation specifics, or concrete guidance

**Execution:**
- Focused follow-up search: "{TOPIC} {subtopic} details 2025"
- Fetches top 2-3 additional results
- Integrates into main research
- Limited to 2-3 deep dives per research session

## Contradiction Detection

The agent identifies and reports conflicting recommendations:

**Example:**
- Position A: "Always use PUT for updates" (3 sources)
- Position B: "Use PATCH for partial updates" (2 sources)
- Analysis: Context-dependent - both valid in different scenarios
- Confidence adjustment: Reduced by one level due to conflict

## Performance Optimization

- **Parallel WebFetch**: Makes multiple independent WebFetch calls simultaneously for speed
- **Smart fallback**: Extracts from search snippets when WebFetch fails
- **Priority domains**: Fetches official docs and major tech sources first
- **Loop termination**: Stops after 10 consecutive failures to avoid wasted time

## Tool Usage

- **WebSearch**: Strategic multi-query search with fallback patterns
- **WebFetch**: Parallel fetching with smart failure handling and snippet extraction

## Notes

- Uses ultrathink mode for complex query formulation and aggregation analysis
- Self-contained (no external file reads required)
- Tracks execution timing and tool usage metrics
- Reports lessons learned for manual improvement
- Model: opus (for advanced web research and analysis capabilities)

---

**Part of the CUI Marketplace** - Reusable components for AI-assisted development.
