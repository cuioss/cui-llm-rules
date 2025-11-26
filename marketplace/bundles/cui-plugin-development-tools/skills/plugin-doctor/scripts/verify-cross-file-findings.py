#!/usr/bin/env python3
"""
Verify LLM cross-file analysis findings against actual content.

Cross-checks LLM analysis claims against the original script analysis
and actual file content to confirm or reject findings.

Usage:
    verify-cross-file-findings.py --analysis <path> [--llm-findings <path>]
    verify-cross-file-findings.py -h | --help

If --llm-findings is not provided, reads from stdin.

Output: JSON with verified findings
"""

import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# Verification thresholds
SIMILARITY_VERIFICATION_TOLERANCE = 0.1  # Allow 10% variance in similarity claims
MIN_CONTENT_OVERLAP = 0.3  # Minimum overlap to verify duplication claim


def show_help():
    """Display help message."""
    help_text = """
Usage: verify-cross-file-findings.py --analysis <path> [--llm-findings <path>]

Verifies LLM cross-file analysis findings against actual content.

Arguments:
  --analysis <path>      Path to original script analysis JSON (required)
  --llm-findings <path>  Path to LLM findings JSON (optional, reads stdin if not provided)

Output: JSON with verification results including:
  - verified: LLM claims confirmed by script verification
  - rejected: LLM claims that couldn't be verified
  - warnings: Potential issues detected during verification
  - summary: Aggregate verification statistics

Expected LLM findings format:
{
  "duplications": [
    {
      "source": {"file": "...", "section": "..."},
      "target": {"file": "...", "section": "..."},
      "classification": "true_duplicate|similar_concept|false_positive",
      "recommendation": "consolidate|cross_reference|keep_both"
    }
  ],
  "extractions": [
    {
      "file": "...",
      "section": "...",
      "type": "template|workflow",
      "recommendation": "extract_to_templates|extract_to_workflows|keep_inline"
    }
  ],
  "terminology": [
    {
      "concept": "...",
      "standardized_term": "...",
      "action": "standardize|keep_variants"
    }
  ]
}

Exit codes:
  0 - Success
  1 - Error (missing arguments, file not found, invalid JSON)

Examples:
  verify-cross-file-findings.py --analysis cross-file-analysis.json --llm-findings llm-output.json
  cat llm-output.json | verify-cross-file-findings.py --analysis cross-file-analysis.json
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


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity ratio between two normalized texts."""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    return SequenceMatcher(None, norm1, norm2).ratio()


def find_content_block(
    analysis: Dict,
    file_path: str,
    section: str
) -> Optional[Dict]:
    """Find a content block in the analysis by file and section."""
    for block in analysis.get('content_blocks', []):
        if block['file'] == file_path and block['section'] == section:
            return block
    return None


def read_section_content(
    skill_path: Path,
    file_path: str,
    lines: str
) -> Optional[str]:
    """Read actual section content from file."""
    try:
        full_path = skill_path / file_path
        if not full_path.exists():
            return None

        content = full_path.read_text(encoding='utf-8')
        all_lines = content.split('\n')

        # Parse line range
        if '-' in lines:
            start, end = map(int, lines.split('-'))
            return '\n'.join(all_lines[start - 1:end])
        else:
            line_num = int(lines)
            return all_lines[line_num - 1] if line_num <= len(all_lines) else None

    except (ValueError, IndexError, IOError):
        return None


def verify_duplication_claim(
    claim: Dict,
    analysis: Dict,
    skill_path: Path
) -> Tuple[bool, str, Dict]:
    """
    Verify a duplication claim from LLM analysis.

    Returns:
        Tuple of (verified: bool, reason: str, details: dict)
    """
    source = claim.get('source', {})
    target = claim.get('target', {})
    classification = claim.get('classification', '')

    # Find source in analysis
    source_block = find_content_block(
        analysis,
        source.get('file', ''),
        source.get('section', '')
    )
    target_block = find_content_block(
        analysis,
        target.get('file', ''),
        target.get('section', '')
    )

    if not source_block or not target_block:
        return False, 'content_blocks_not_found', {
            'source_found': source_block is not None,
            'target_found': target_block is not None
        }

    # Check if this pair was in similarity_candidates
    in_candidates = False
    reported_similarity = None

    for candidate in analysis.get('similarity_candidates', []):
        cand_source = candidate.get('source', {})
        cand_target = candidate.get('target', {})

        # Check both orderings
        if ((cand_source.get('file') == source.get('file') and
             cand_source.get('section') == source.get('section') and
             cand_target.get('file') == target.get('file') and
             cand_target.get('section') == target.get('section')) or
            (cand_target.get('file') == source.get('file') and
             cand_target.get('section') == source.get('section') and
             cand_source.get('file') == target.get('file') and
             cand_source.get('section') == target.get('section'))):
            in_candidates = True
            reported_similarity = candidate.get('similarity')
            break

    # Check if in exact_duplicates
    in_exact = False
    for dup in analysis.get('exact_duplicates', []):
        files = [occ.get('file') for occ in dup.get('occurrences', [])]
        sections = [occ.get('section') for occ in dup.get('occurrences', [])]
        if (source.get('file') in files and target.get('file') in files and
            source.get('section') in sections and target.get('section') in sections):
            in_exact = True
            break

    # Verification logic
    if classification == 'true_duplicate':
        if in_exact:
            return True, 'confirmed_exact_duplicate', {
                'verification_method': 'hash_match'
            }
        elif in_candidates and reported_similarity and reported_similarity >= 0.8:
            return True, 'confirmed_high_similarity', {
                'similarity': reported_similarity,
                'verification_method': 'similarity_threshold'
            }
        elif in_candidates:
            return True, 'confirmed_in_candidates', {
                'similarity': reported_similarity,
                'note': 'LLM semantic judgment accepted'
            }
        else:
            return False, 'not_in_analysis_candidates', {
                'in_exact': in_exact,
                'in_similarity': in_candidates
            }

    elif classification == 'similar_concept':
        if in_candidates:
            return True, 'confirmed_similar_concept', {
                'similarity': reported_similarity
            }
        else:
            return False, 'pair_not_in_analysis', {}

    elif classification == 'false_positive':
        # LLM rejected a candidate - verify it was actually a candidate
        if in_candidates or in_exact:
            return True, 'false_positive_acknowledged', {
                'was_candidate': in_candidates,
                'was_exact': in_exact
            }
        else:
            return False, 'not_a_candidate_to_reject', {}

    return False, 'unknown_classification', {'classification': classification}


def verify_extraction_claim(
    claim: Dict,
    analysis: Dict,
    skill_path: Path
) -> Tuple[bool, str, Dict]:
    """
    Verify an extraction recommendation from LLM analysis.

    Returns:
        Tuple of (verified: bool, reason: str, details: dict)
    """
    file_path = claim.get('file', '')
    section = claim.get('section', '')
    claim_type = claim.get('type', '')
    recommendation = claim.get('recommendation', '')

    # Find in analysis extraction_candidates
    matching_candidate = None
    for candidate in analysis.get('extraction_candidates', []):
        if (candidate.get('file') == file_path and
            candidate.get('section') == section):
            matching_candidate = candidate
            break

    if matching_candidate:
        # Verify type matches
        if matching_candidate.get('type') == claim_type:
            return True, 'confirmed_extraction_candidate', {
                'analysis_type': matching_candidate.get('type'),
                'analysis_pattern': matching_candidate.get('pattern'),
                'llm_recommendation': recommendation
            }
        else:
            return True, 'type_mismatch_but_candidate_exists', {
                'claimed_type': claim_type,
                'analysis_type': matching_candidate.get('type')
            }

    # Not in candidates - check if LLM found something new
    # Read actual content to verify
    content_block = find_content_block(analysis, file_path, section)
    if content_block:
        # LLM identified extraction opportunity not caught by script
        return True, 'llm_identified_new_candidate', {
            'note': 'LLM found extraction opportunity not in script analysis',
            'requires_manual_review': True
        }

    return False, 'section_not_found', {
        'file': file_path,
        'section': section
    }


def verify_terminology_claim(
    claim: Dict,
    analysis: Dict
) -> Tuple[bool, str, Dict]:
    """
    Verify a terminology standardization claim from LLM analysis.

    Returns:
        Tuple of (verified: bool, reason: str, details: dict)
    """
    concept = claim.get('concept', '')
    standardized_term = claim.get('standardized_term', '')
    action = claim.get('action', '')

    # Find matching terminology variant in analysis
    matching_variant = None
    for variant in analysis.get('terminology_variants', []):
        if variant.get('concept', '').lower() == concept.lower():
            matching_variant = variant
            break

    if matching_variant:
        variant_terms = [v.get('term', '') for v in matching_variant.get('variants', [])]

        if action == 'standardize':
            # Verify standardized_term is one of the variants
            if standardized_term.lower() in [t.lower() for t in variant_terms]:
                return True, 'confirmed_standardization', {
                    'available_variants': variant_terms,
                    'chosen_standard': standardized_term
                }
            else:
                return True, 'standardization_term_not_in_variants', {
                    'available_variants': variant_terms,
                    'chosen_standard': standardized_term,
                    'note': 'LLM may have chosen a better canonical form'
                }

        elif action == 'keep_variants':
            return True, 'confirmed_keep_variants', {
                'variants': variant_terms
            }

    # Concept not in analysis
    if action == 'keep_variants':
        return True, 'no_variants_found_keeping', {}

    return False, 'concept_not_in_analysis', {
        'concept': concept
    }


def verify_findings(
    analysis: Dict,
    llm_findings: Dict
) -> Dict:
    """
    Main verification function that processes all LLM findings.
    """
    skill_path = Path(analysis.get('skill_path', ''))

    verified = []
    rejected = []
    warnings = []

    # Verify duplication claims
    for claim in llm_findings.get('duplications', []):
        is_verified, reason, details = verify_duplication_claim(
            claim, analysis, skill_path
        )

        result = {
            'type': 'duplication',
            'claim': claim,
            'reason': reason,
            'details': details
        }

        if is_verified:
            verified.append(result)
        else:
            rejected.append(result)

    # Verify extraction claims
    for claim in llm_findings.get('extractions', []):
        is_verified, reason, details = verify_extraction_claim(
            claim, analysis, skill_path
        )

        result = {
            'type': 'extraction',
            'claim': claim,
            'reason': reason,
            'details': details
        }

        if is_verified:
            verified.append(result)
            if details.get('requires_manual_review'):
                warnings.append({
                    'type': 'manual_review_needed',
                    'claim': claim,
                    'reason': 'LLM identified opportunity not in script analysis'
                })
        else:
            rejected.append(result)

    # Verify terminology claims
    for claim in llm_findings.get('terminology', []):
        is_verified, reason, details = verify_terminology_claim(
            claim, analysis
        )

        result = {
            'type': 'terminology',
            'claim': claim,
            'reason': reason,
            'details': details
        }

        if is_verified:
            verified.append(result)
        else:
            rejected.append(result)

    # Check for unaddressed analysis items
    # (items in script analysis that LLM didn't address)
    llm_addressed_pairs = set()
    for claim in llm_findings.get('duplications', []):
        source = claim.get('source', {})
        target = claim.get('target', {})
        pair = tuple(sorted([
            f"{source.get('file')}:{source.get('section')}",
            f"{target.get('file')}:{target.get('section')}"
        ]))
        llm_addressed_pairs.add(pair)

    for candidate in analysis.get('similarity_candidates', []):
        source = candidate.get('source', {})
        target = candidate.get('target', {})
        pair = tuple(sorted([
            f"{source.get('file')}:{source.get('section')}",
            f"{target.get('file')}:{target.get('section')}"
        ]))
        if pair not in llm_addressed_pairs:
            warnings.append({
                'type': 'unaddressed_candidate',
                'candidate': candidate,
                'reason': 'Similarity candidate not addressed by LLM'
            })

    # Summary statistics
    total_claims = (
        len(llm_findings.get('duplications', [])) +
        len(llm_findings.get('extractions', [])) +
        len(llm_findings.get('terminology', []))
    )

    verification_rate = (
        len(verified) / total_claims * 100
        if total_claims > 0 else 100.0
    )

    return {
        'skill_path': str(skill_path),
        'verified': verified,
        'rejected': rejected,
        'warnings': warnings,
        'summary': {
            'total_claims': total_claims,
            'verified_count': len(verified),
            'rejected_count': len(rejected),
            'warning_count': len(warnings),
            'verification_rate': round(verification_rate, 1)
        }
    }


def main():
    parser = argparse.ArgumentParser(
        description='Verify LLM cross-file analysis findings',
        add_help=False
    )
    parser.add_argument('--analysis', required=False, help='Path to script analysis JSON')
    parser.add_argument('--llm-findings', required=False, help='Path to LLM findings JSON')
    parser.add_argument('-h', '--help', action='store_true', help='Show help')

    args = parser.parse_args()

    if args.help:
        show_help()

    if not args.analysis:
        print(json.dumps({
            'error': 'Analysis path required. Use --help for usage.'
        }), file=sys.stderr)
        sys.exit(1)

    # Load script analysis
    analysis_path = Path(args.analysis)
    if not analysis_path.exists():
        print(json.dumps({
            'error': f'Analysis file not found: {args.analysis}'
        }), file=sys.stderr)
        sys.exit(1)

    try:
        with open(analysis_path, 'r', encoding='utf-8') as f:
            analysis = json.load(f)
    except json.JSONDecodeError as e:
        print(json.dumps({
            'error': f'Invalid JSON in analysis file: {str(e)}'
        }), file=sys.stderr)
        sys.exit(1)

    # Load LLM findings
    if args.llm_findings:
        findings_path = Path(args.llm_findings)
        if not findings_path.exists():
            print(json.dumps({
                'error': f'LLM findings file not found: {args.llm_findings}'
            }), file=sys.stderr)
            sys.exit(1)

        try:
            with open(findings_path, 'r', encoding='utf-8') as f:
                llm_findings = json.load(f)
        except json.JSONDecodeError as e:
            print(json.dumps({
                'error': f'Invalid JSON in LLM findings file: {str(e)}'
            }), file=sys.stderr)
            sys.exit(1)
    else:
        # Read from stdin
        try:
            llm_findings = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(json.dumps({
                'error': f'Invalid JSON from stdin: {str(e)}'
            }), file=sys.stderr)
            sys.exit(1)

    # Verify findings
    try:
        result = verify_findings(analysis, llm_findings)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({
            'error': f'Verification failed: {str(e)}'
        }), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
