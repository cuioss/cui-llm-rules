#!/usr/bin/env python3
"""
Analyze cross-file content within a skill directory.

Performs duplication detection, extraction candidate identification,
and terminology variant analysis across all markdown files in a skill's
subdirectories (references/, workflows/, templates/).

Usage:
    analyze-cross-file-content.py --skill-path <path> [--similarity-threshold 0.4]
    analyze-cross-file-content.py -h | --help

Output: JSON with structured analysis for LLM consumption
"""

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# Directories to analyze within a skill
CONTENT_DIRS = ['references', 'workflows', 'templates']

# Similarity thresholds
DEFAULT_SIMILARITY_THRESHOLD = 0.4
EXACT_THRESHOLD = 0.95

# Minimum content length for analysis (characters)
MIN_SECTION_LENGTH = 100
MIN_PARAGRAPH_LENGTH = 50

# Patterns for extraction candidate detection
PLACEHOLDER_PATTERNS = [
    r'\{\{[A-Z_]+\}\}',           # {{PLACEHOLDER}}
    r'\{[a-z_]+\}',                # {placeholder}
    r'\[INSERT [A-Z]+\]',          # [INSERT NAME]
    r'<[A-Z_]+>',                  # <PLACEHOLDER>
]

WORKFLOW_PATTERNS = [
    r'^###?\s+Step\s+\d+',         # ### Step 1, ## Step 2
    r'^###?\s+Phase\s+\d+',        # ### Phase 1
    r'^\d+\.\s+\*\*[^*]+\*\*:',    # 1. **Action**: description
]

# Patterns for terminology extraction
TERM_PATTERNS = {
    'definition': r'\*\*([^*]+)\*\*:',      # **Term**: definition
    'header': r'^#{2,4}\s+(.+)$',            # ## Header Term
    'emphasized': r'\*([^*]+)\*',            # *emphasized term*
    'backtick': r'`([^`]+)`',                # `term`
}

# Known synonym groups for terminology analysis
KNOWN_SYNONYM_GROUPS = [
    {'cross-reference', 'xref', 'internal link', 'cross-ref'},
    {'workflow', 'process', 'procedure', 'protocol'},
    {'must', 'shall', 'required', 'mandatory'},
    {'should', 'recommended', 'advisable'},
    {'may', 'optional', 'can'},
    {'skill', 'plugin', 'component'},
    {'agent', 'assistant', 'bot'},
    {'command', 'slash command', 'directive'},
]


def show_help():
    """Display help message."""
    help_text = """
Usage: analyze-cross-file-content.py --skill-path <path> [options]

Analyzes cross-file content within a skill directory for duplication,
extraction candidates, and terminology consistency.

Arguments:
  --skill-path <path>     Path to the skill directory (required)
  --similarity-threshold  Minimum similarity for candidate detection (default: 0.4)

Output: JSON with structured analysis including:
  - content_blocks: Extracted sections from all files
  - exact_duplicates: Hash-based exact matches (no LLM needed)
  - similarity_candidates: 40-95% similar pairs for LLM review
  - extraction_candidates: Patterns suggesting template/workflow extraction
  - terminology_variants: Term variations detected across files
  - summary: Aggregate counts and LLM review flag

Exit codes:
  0 - Success
  1 - Error (missing arguments, path not found)

Examples:
  analyze-cross-file-content.py --skill-path ./skills/plugin-doctor
  analyze-cross-file-content.py --skill-path ./skills/cui-java-core --similarity-threshold 0.5
"""
    print(help_text.strip())
    sys.exit(0)


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison by removing markdown formatting,
    code blocks, and normalizing whitespace.
    """
    # Remove code blocks
    text = re.sub(r'```[\s\S]*?```', '', text)
    # Remove inline code
    text = re.sub(r'`[^`]+`', '', text)
    # Remove markdown formatting
    text = re.sub(r'[#*_\[\]()]', '', text)
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    # Normalize whitespace
    return ' '.join(text.lower().split())


def compute_hash(text: str) -> str:
    """Compute SHA256 hash of normalized text."""
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]


def extract_sections(content: str, file_path: str) -> List[Dict]:
    """
    Extract sections from markdown content.
    Sections are delimited by ## or ### headers.
    """
    sections = []
    lines = content.split('\n')
    current_section = {
        'header': '_intro',
        'level': 0,
        'start_line': 1,
        'content_lines': []
    }

    for i, line in enumerate(lines, 1):
        # Check for section header
        header_match = re.match(r'^(#{2,4})\s+(.+)$', line)
        if header_match:
            # Save previous section if it has content
            if current_section['content_lines']:
                section_text = '\n'.join(current_section['content_lines'])
                if len(section_text.strip()) >= MIN_SECTION_LENGTH:
                    current_section['end_line'] = i - 1
                    current_section['text'] = section_text
                    current_section['content_hash'] = compute_hash(section_text)
                    current_section['normalized_length'] = len(normalize_text(section_text))
                    sections.append(current_section)

            # Start new section
            current_section = {
                'header': header_match.group(2).strip(),
                'level': len(header_match.group(1)),
                'start_line': i,
                'content_lines': []
            }
        else:
            current_section['content_lines'].append(line)

    # Save final section
    if current_section['content_lines']:
        section_text = '\n'.join(current_section['content_lines'])
        if len(section_text.strip()) >= MIN_SECTION_LENGTH:
            current_section['end_line'] = len(lines)
            current_section['text'] = section_text
            current_section['content_hash'] = compute_hash(section_text)
            current_section['normalized_length'] = len(normalize_text(section_text))
            sections.append(current_section)

    return sections


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity ratio between two normalized texts."""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    return SequenceMatcher(None, norm1, norm2).ratio()


def find_exact_duplicates(all_sections: List[Dict]) -> List[Dict]:
    """
    Find exact duplicates using content hashes.
    Groups sections with identical normalized content.
    """
    hash_groups: Dict[str, List[Dict]] = defaultdict(list)

    for section in all_sections:
        content_hash = section.get('content_hash')
        if content_hash:
            hash_groups[content_hash].append(section)

    duplicates = []
    for content_hash, sections in hash_groups.items():
        if len(sections) > 1:
            duplicates.append({
                'hash': content_hash,
                'occurrences': [
                    {
                        'file': s['file'],
                        'section': s['header'],
                        'lines': f"{s['start_line']}-{s['end_line']}"
                    }
                    for s in sections
                ],
                'line_count': sections[0]['end_line'] - sections[0]['start_line'] + 1,
                'content_preview': normalize_text(sections[0]['text'])[:200] + '...',
                'recommendation': 'consolidate'
            })

    return duplicates


def find_similarity_candidates(
    all_sections: List[Dict],
    threshold: float,
    exact_hashes: Set[str]
) -> List[Dict]:
    """
    Find sections with similarity between threshold and EXACT_THRESHOLD.
    Skip sections that are exact duplicates (already reported).
    """
    candidates = []
    processed_pairs: Set[Tuple[str, str]] = set()

    for i, section1 in enumerate(all_sections):
        # Skip if exact duplicate
        if section1.get('content_hash') in exact_hashes:
            continue

        for j, section2 in enumerate(all_sections[i + 1:], i + 1):
            # Skip same file
            if section1['file'] == section2['file']:
                continue

            # Skip if exact duplicate
            if section2.get('content_hash') in exact_hashes:
                continue

            # Create unique pair ID
            pair_id = tuple(sorted([
                f"{section1['file']}:{section1['header']}",
                f"{section2['file']}:{section2['header']}"
            ]))

            if pair_id in processed_pairs:
                continue
            processed_pairs.add(pair_id)

            # Calculate similarity
            similarity = calculate_similarity(section1['text'], section2['text'])

            if threshold <= similarity < EXACT_THRESHOLD:
                candidates.append({
                    'source': {
                        'file': section1['file'],
                        'section': section1['header'],
                        'lines': f"{section1['start_line']}-{section1['end_line']}"
                    },
                    'target': {
                        'file': section2['file'],
                        'section': section2['header'],
                        'lines': f"{section2['start_line']}-{section2['end_line']}"
                    },
                    'similarity': round(similarity, 3),
                    'llm_analysis_required': True
                })

    # Sort by similarity descending
    candidates.sort(key=lambda x: x['similarity'], reverse=True)
    return candidates


def detect_extraction_candidates(all_sections: List[Dict]) -> List[Dict]:
    """
    Detect content that should be extracted to templates or workflows.
    """
    candidates = []

    for section in all_sections:
        text = section.get('text', '')

        # Check for template patterns (placeholders)
        placeholders_found = []
        for pattern in PLACEHOLDER_PATTERNS:
            matches = re.findall(pattern, text)
            placeholders_found.extend(matches)

        if placeholders_found:
            candidates.append({
                'type': 'template',
                'pattern': 'placeholder_structure',
                'file': section['file'],
                'section': section['header'],
                'lines': f"{section['start_line']}-{section['end_line']}",
                'detected_placeholders': list(set(placeholders_found)),
                'recommendation': 'extract_to_templates'
            })
            continue

        # Check for workflow patterns (step sequences)
        workflow_indicators = 0
        for pattern in WORKFLOW_PATTERNS:
            workflow_indicators += len(re.findall(pattern, text, re.MULTILINE))

        if workflow_indicators >= 3:
            candidates.append({
                'type': 'workflow',
                'pattern': 'step_sequence',
                'file': section['file'],
                'section': section['header'],
                'lines': f"{section['start_line']}-{section['end_line']}",
                'step_count': workflow_indicators,
                'recommendation': 'extract_to_workflows'
            })

    return candidates


def extract_terminology(all_sections: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Extract terminology from content and group by file.
    """
    terms_by_file: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for section in all_sections:
        file_path = section['file']
        text = section.get('text', '')

        # Extract defined terms
        for term_type, pattern in TERM_PATTERNS.items():
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                # Normalize term
                term = match.strip().lower()
                if len(term) > 2 and len(term) < 50:  # Reasonable term length
                    terms_by_file[file_path][term] += 1

    return terms_by_file


def find_terminology_variants(terms_by_file: Dict[str, Dict[str, int]]) -> List[Dict]:
    """
    Find terminology variants using known synonym groups.
    """
    variants = []

    # Check each synonym group
    for synonym_group in KNOWN_SYNONYM_GROUPS:
        found_variants: Dict[str, List[Tuple[str, int]]] = defaultdict(list)

        for file_path, terms in terms_by_file.items():
            for term, count in terms.items():
                # Check if term matches any synonym in the group
                term_lower = term.lower()
                for synonym in synonym_group:
                    if synonym in term_lower or term_lower in synonym:
                        found_variants[term].append((file_path, count))
                        break

        # If multiple variants found across different terms
        if len(found_variants) > 1:
            variant_list = []
            for term, occurrences in found_variants.items():
                files = [occ[0] for occ in occurrences]
                total_count = sum(occ[1] for occ in occurrences)
                variant_list.append({
                    'term': term,
                    'files': list(set(files)),
                    'count': total_count
                })

            if variant_list:
                # Determine most common variant
                most_common = max(variant_list, key=lambda x: x['count'])
                variants.append({
                    'concept': list(synonym_group)[0],  # Use first synonym as concept name
                    'variants': variant_list,
                    'recommendation': f"standardize on '{most_common['term']}'"
                })

    return variants


def analyze_skill(skill_path: Path, similarity_threshold: float) -> Dict:
    """
    Main analysis function that orchestrates all cross-file checks.
    """
    skill_name = skill_path.name
    all_sections = []
    files_analyzed = 0
    total_lines = 0

    # Scan content directories
    for content_dir in CONTENT_DIRS:
        dir_path = skill_path / content_dir
        if not dir_path.exists():
            continue

        for md_file in dir_path.glob('**/*.md'):
            try:
                content = md_file.read_text(encoding='utf-8')
                rel_path = str(md_file.relative_to(skill_path))
                files_analyzed += 1
                total_lines += len(content.split('\n'))

                # Extract sections
                sections = extract_sections(content, rel_path)
                for section in sections:
                    section['file'] = rel_path
                all_sections.extend(sections)

            except Exception as e:
                # Skip files that can't be read
                continue

    # Build content blocks for output
    content_blocks = [
        {
            'id': f"{s['file']}:{s['header']}".replace('/', ':').replace(' ', '-').lower(),
            'file': s['file'],
            'section': s['header'],
            'lines': f"{s['start_line']}-{s['end_line']}",
            'content_hash': s.get('content_hash', ''),
            'normalized_length': s.get('normalized_length', 0)
        }
        for s in all_sections
    ]

    # Find exact duplicates
    exact_duplicates = find_exact_duplicates(all_sections)
    exact_hashes = {d['hash'] for d in exact_duplicates}

    # Find similarity candidates
    similarity_candidates = find_similarity_candidates(
        all_sections, similarity_threshold, exact_hashes
    )

    # Detect extraction candidates
    extraction_candidates = detect_extraction_candidates(all_sections)

    # Extract and analyze terminology
    terms_by_file = extract_terminology(all_sections)
    terminology_variants = find_terminology_variants(terms_by_file)

    # Build summary
    llm_review_required = (
        len(similarity_candidates) > 0 or
        len(extraction_candidates) > 0 or
        len(terminology_variants) > 0
    )

    return {
        'skill_path': str(skill_path),
        'skill_name': skill_name,
        'files_analyzed': files_analyzed,
        'total_lines': total_lines,
        'content_blocks': content_blocks,
        'exact_duplicates': exact_duplicates,
        'similarity_candidates': similarity_candidates,
        'extraction_candidates': extraction_candidates,
        'terminology_variants': terminology_variants,
        'summary': {
            'exact_duplicate_pairs': len(exact_duplicates),
            'similarity_candidates': len(similarity_candidates),
            'extraction_candidates': len(extraction_candidates),
            'terminology_issues': len(terminology_variants),
            'llm_review_required': llm_review_required
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description='Analyze cross-file content within a skill directory',
        add_help=False
    )
    parser.add_argument('--skill-path', required=False, help='Path to skill directory')
    parser.add_argument(
        '--similarity-threshold',
        type=float,
        default=DEFAULT_SIMILARITY_THRESHOLD,
        help=f'Minimum similarity threshold (default: {DEFAULT_SIMILARITY_THRESHOLD})'
    )
    parser.add_argument('-h', '--help', action='store_true', help='Show help')

    args = parser.parse_args()

    if args.help:
        show_help()

    if not args.skill_path:
        print(json.dumps({
            'error': 'Skill path required. Use --help for usage.'
        }), file=sys.stderr)
        sys.exit(1)

    skill_path = Path(args.skill_path)
    if not skill_path.exists():
        print(json.dumps({
            'error': f'Skill path not found: {args.skill_path}'
        }), file=sys.stderr)
        sys.exit(1)

    if not skill_path.is_dir():
        print(json.dumps({
            'error': f'Skill path is not a directory: {args.skill_path}'
        }), file=sys.stderr)
        sys.exit(1)

    try:
        result = analyze_skill(skill_path, args.similarity_threshold)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({
            'error': f'Analysis failed: {str(e)}'
        }), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
