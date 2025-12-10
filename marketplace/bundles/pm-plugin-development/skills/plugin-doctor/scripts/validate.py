#!/usr/bin/env python3
"""
validate.py - Plugin validation and inventory tools.

Consolidated from:
- validate-references.py → references subcommand
- verify-cross-file-findings.py → cross-file subcommand
- scan-skill-inventory.py → inventory subcommand

Validates plugin components and manages skill inventory.

Output: JSON to stdout.
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# =============================================================================
# Shared Functions
# =============================================================================

def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)
    text = re.sub(r'[#*_\[\]()]', '', text)
    text = re.sub(r'https?://\S+', '', text)
    return ' '.join(text.lower().split())


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity ratio between two normalized texts."""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    return SequenceMatcher(None, norm1, norm2).ratio()


def count_lines(file_path: Path) -> int:
    """Count lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return sum(1 for _ in f)
    except (OSError, IOError):
        return 0


# =============================================================================
# References Subcommand (from validate-references.py)
# =============================================================================

def detect_file_type(file_path: str) -> str:
    """Detect if file is agent, command, or skill."""
    if "/agents/" in file_path:
        return "agent"
    elif "/commands/" in file_path:
        return "command"
    elif "/skills/" in file_path:
        return "skill"
    return "unknown"


def pre_filter_documentation_lines(content: str) -> Set[int]:
    """Pre-filter documentation lines to exclude from reference detection."""
    lines = content.split('\n')
    excluded = set()

    in_example = False
    in_workflow_step = False
    in_related = False
    example_level = 0

    for i, line in enumerate(lines):
        example_match = re.match(r'^(#{2,3})\s+(Example|Usage|Demonstration|USAGE|EXAMPLES)', line, re.IGNORECASE)
        if example_match:
            in_example = True
            example_level = len(example_match.group(1))
            excluded.add(i)
            continue

        if in_example:
            header_match = re.match(r'^(#{2,3})\s+', line)
            if header_match and len(header_match.group(1)) <= example_level:
                in_example = False
            else:
                excluded.add(i)
                continue

        workflow_match = re.match(r'^(#{2,3})\s+Step\s+\d+:', line)
        if workflow_match:
            in_workflow_step = True
            excluded.add(i)
            continue

        if in_workflow_step:
            header_match = re.match(r'^#{2,3}\s+', line)
            if header_match:
                in_workflow_step = False
            elif re.match(r'^\s*-\s+\*\*[^*]+\*\*:', line):
                excluded.add(i)
                continue

        if re.search(r'caller can then invoke|invoke `/plugin-update', line, re.IGNORECASE):
            excluded.add(i)
            continue

        if re.match(r'^(Task|Agent|Command):$', line.strip()):
            excluded.add(i)
            for j in range(i + 1, min(i + 20, len(lines))):
                if lines[j].startswith((' ', '\t')):
                    excluded.add(j)
                elif lines[j].strip():
                    break
            continue

        if re.match(r'^#{2,3}\s+(RELATED|SEE ALSO|Related|See Also)', line, re.IGNORECASE):
            in_related = True
            excluded.add(i)
            continue

        if in_related:
            if re.match(r'^#{2,3}\s+', line):
                in_related = False
            else:
                excluded.add(i)
                continue

    return excluded


def extract_references(content: str, excluded_lines: Set[int]) -> List[Dict]:
    """Extract plugin references from content."""
    lines = content.split('\n')
    references = []

    slash_pattern = re.compile(r'SlashCommand:\s*/([a-z0-9:-]+)')
    task_pattern = re.compile(r'subagent_type[:\s]+["\']?([a-z0-9:-]+)["\']?')
    skill_pattern = re.compile(r'Skill:\s*([a-z0-9:-]+)')

    for i, line in enumerate(lines):
        if i in excluded_lines:
            continue

        for match in slash_pattern.finditer(line):
            references.append({
                "line": i + 1,
                "type": "SlashCommand",
                "reference": f"/{match.group(1)}",
                "raw_text": match.group(0)
            })

        for match in task_pattern.finditer(line):
            references.append({
                "line": i + 1,
                "type": "Task",
                "reference": match.group(1),
                "raw_text": match.group(0)
            })

        for match in skill_pattern.finditer(line):
            references.append({
                "line": i + 1,
                "type": "Skill",
                "reference": match.group(1),
                "raw_text": match.group(0)
            })

    return references


def cmd_references(args) -> int:
    """Validate plugin references in a markdown file."""
    file_path = Path(args.file)

    if not file_path.is_file():
        print(json.dumps({"error": f"File not found: {args.file}"}), file=sys.stderr)
        return 1

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(json.dumps({"error": f"Failed to read file: {str(e)}"}), file=sys.stderr)
        return 1

    file_type = detect_file_type(str(file_path))
    excluded_lines = pre_filter_documentation_lines(content)
    references = extract_references(content, excluded_lines)

    total_lines = len(content.split('\n'))
    excluded_count = len(excluded_lines)
    exclusion_rate = (excluded_count / total_lines * 100) if total_lines > 0 else 0.0

    result = {
        "file_path": str(file_path),
        "file_type": file_type,
        "total_lines": total_lines,
        "references": references,
        "pre_filter": {
            "excluded_lines_count": excluded_count,
            "exclusion_rate": round(exclusion_rate, 1)
        }
    }

    print(json.dumps(result, indent=2))
    return 0


# =============================================================================
# Cross-File Subcommand (from verify-cross-file-findings.py)
# =============================================================================

SIMILARITY_VERIFICATION_TOLERANCE = 0.1
MIN_CONTENT_OVERLAP = 0.3


def find_content_block(analysis: Dict, file_path: str, section: str) -> Optional[Dict]:
    """Find a content block in the analysis by file and section."""
    for block in analysis.get('content_blocks', []):
        if block['file'] == file_path and block['section'] == section:
            return block
    return None


def verify_duplication_claim(claim: Dict, analysis: Dict, skill_path: Path) -> Tuple[bool, str, Dict]:
    """Verify a duplication claim from LLM analysis."""
    source = claim.get('source', {})
    target = claim.get('target', {})
    classification = claim.get('classification', '')

    source_block = find_content_block(analysis, source.get('file', ''), source.get('section', ''))
    target_block = find_content_block(analysis, target.get('file', ''), target.get('section', ''))

    if not source_block or not target_block:
        return False, 'content_blocks_not_found', {
            'source_found': source_block is not None,
            'target_found': target_block is not None
        }

    in_candidates = False
    reported_similarity = None

    for candidate in analysis.get('similarity_candidates', []):
        cand_source = candidate.get('source', {})
        cand_target = candidate.get('target', {})

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

    in_exact = False
    for dup in analysis.get('exact_duplicates', []):
        files = [occ.get('file') for occ in dup.get('occurrences', [])]
        sections = [occ.get('section') for occ in dup.get('occurrences', [])]
        if (source.get('file') in files and target.get('file') in files and
            source.get('section') in sections and target.get('section') in sections):
            in_exact = True
            break

    if classification == 'true_duplicate':
        if in_exact:
            return True, 'confirmed_exact_duplicate', {'verification_method': 'hash_match'}
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
            return True, 'confirmed_similar_concept', {'similarity': reported_similarity}
        else:
            return False, 'pair_not_in_analysis', {}

    elif classification == 'false_positive':
        if in_candidates or in_exact:
            return True, 'false_positive_acknowledged', {
                'was_candidate': in_candidates,
                'was_exact': in_exact
            }
        else:
            return False, 'not_a_candidate_to_reject', {}

    return False, 'unknown_classification', {'classification': classification}


def verify_extraction_claim(claim: Dict, analysis: Dict, skill_path: Path) -> Tuple[bool, str, Dict]:
    """Verify an extraction recommendation from LLM analysis."""
    file_path = claim.get('file', '')
    section = claim.get('section', '')
    claim_type = claim.get('type', '')
    recommendation = claim.get('recommendation', '')

    matching_candidate = None
    for candidate in analysis.get('extraction_candidates', []):
        if candidate.get('file') == file_path and candidate.get('section') == section:
            matching_candidate = candidate
            break

    if matching_candidate:
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

    content_block = find_content_block(analysis, file_path, section)
    if content_block:
        return True, 'llm_identified_new_candidate', {
            'note': 'LLM found extraction opportunity not in script analysis',
            'requires_manual_review': True
        }

    return False, 'section_not_found', {'file': file_path, 'section': section}


def verify_terminology_claim(claim: Dict, analysis: Dict) -> Tuple[bool, str, Dict]:
    """Verify a terminology standardization claim from LLM analysis."""
    concept = claim.get('concept', '')
    standardized_term = claim.get('standardized_term', '')
    action = claim.get('action', '')

    matching_variant = None
    for variant in analysis.get('terminology_variants', []):
        if variant.get('concept', '').lower() == concept.lower():
            matching_variant = variant
            break

    if matching_variant:
        variant_terms = [v.get('term', '') for v in matching_variant.get('variants', [])]

        if action == 'standardize':
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
            return True, 'confirmed_keep_variants', {'variants': variant_terms}

    if action == 'keep_variants':
        return True, 'no_variants_found_keeping', {}

    return False, 'concept_not_in_analysis', {'concept': concept}


def verify_findings(analysis: Dict, llm_findings: Dict) -> Dict:
    """Main verification function that processes all LLM findings."""
    skill_path = Path(analysis.get('skill_path', ''))

    verified = []
    rejected = []
    warnings = []

    for claim in llm_findings.get('duplications', []):
        is_verified, reason, details = verify_duplication_claim(claim, analysis, skill_path)
        result = {'type': 'duplication', 'claim': claim, 'reason': reason, 'details': details}
        if is_verified:
            verified.append(result)
        else:
            rejected.append(result)

    for claim in llm_findings.get('extractions', []):
        is_verified, reason, details = verify_extraction_claim(claim, analysis, skill_path)
        result = {'type': 'extraction', 'claim': claim, 'reason': reason, 'details': details}
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

    for claim in llm_findings.get('terminology', []):
        is_verified, reason, details = verify_terminology_claim(claim, analysis)
        result = {'type': 'terminology', 'claim': claim, 'reason': reason, 'details': details}
        if is_verified:
            verified.append(result)
        else:
            rejected.append(result)

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

    total_claims = (
        len(llm_findings.get('duplications', [])) +
        len(llm_findings.get('extractions', [])) +
        len(llm_findings.get('terminology', []))
    )

    verification_rate = len(verified) / total_claims * 100 if total_claims > 0 else 100.0

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


def cmd_cross_file(args) -> int:
    """Verify LLM cross-file analysis findings."""
    analysis_path = Path(args.analysis)
    if not analysis_path.exists():
        print(json.dumps({'error': f'Analysis file not found: {args.analysis}'}), file=sys.stderr)
        return 1

    try:
        with open(analysis_path, 'r', encoding='utf-8') as f:
            analysis = json.load(f)
    except json.JSONDecodeError as e:
        print(json.dumps({'error': f'Invalid JSON in analysis file: {str(e)}'}), file=sys.stderr)
        return 1

    if args.llm_findings:
        findings_path = Path(args.llm_findings)
        if not findings_path.exists():
            print(json.dumps({'error': f'LLM findings file not found: {args.llm_findings}'}), file=sys.stderr)
            return 1

        try:
            with open(findings_path, 'r', encoding='utf-8') as f:
                llm_findings = json.load(f)
        except json.JSONDecodeError as e:
            print(json.dumps({'error': f'Invalid JSON in LLM findings file: {str(e)}'}), file=sys.stderr)
            return 1
    else:
        try:
            llm_findings = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(json.dumps({'error': f'Invalid JSON from stdin: {str(e)}'}), file=sys.stderr)
            return 1

    try:
        result = verify_findings(analysis, llm_findings)
        print(json.dumps(result, indent=2))
        return 0
    except Exception as e:
        print(json.dumps({'error': f'Verification failed: {str(e)}'}), file=sys.stderr)
        return 1


# =============================================================================
# Inventory Subcommand (from scan-skill-inventory.py)
# =============================================================================

def get_file_size(file_path: Path) -> int:
    """Get file size in bytes."""
    try:
        return file_path.stat().st_size
    except OSError:
        return 0


def should_skip_directory(dir_name: str, include_hidden: bool) -> bool:
    """Check if directory should be skipped."""
    skip_dirs = {'__pycache__', 'node_modules', '.git'}
    if dir_name in skip_dirs:
        return True
    if not include_hidden and dir_name.startswith('.'):
        return True
    return False


def should_skip_file(file_name: str, include_hidden: bool) -> bool:
    """Check if file should be skipped."""
    if not include_hidden and file_name.startswith('.'):
        return True
    return False


def scan_directory(skill_path: Path, include_hidden: bool) -> dict:
    """Scan skill directory and return inventory."""
    skill_name = skill_path.name
    abs_skill_path = str(skill_path.resolve())

    directories = []
    root_files = []
    total_dirs = 0
    total_files = 0
    total_lines = 0
    extensions = defaultdict(int)

    try:
        for entry in sorted(skill_path.iterdir()):
            if entry.is_dir():
                dir_name = entry.name

                if should_skip_directory(dir_name, include_hidden):
                    continue

                total_dirs += 1
                dir_files = []

                for file_entry in sorted(entry.iterdir()):
                    if not file_entry.is_file():
                        continue

                    file_name = file_entry.name
                    if should_skip_file(file_name, include_hidden):
                        continue

                    total_files += 1
                    lines = count_lines(file_entry)
                    total_lines += lines
                    size = get_file_size(file_entry)

                    if '.' in file_name:
                        ext = '.' + file_name.rsplit('.', 1)[1]
                        extensions[ext] += 1

                    rel_path = str(file_entry.relative_to(skill_path))

                    dir_files.append({
                        "name": file_name,
                        "path": rel_path,
                        "lines": lines,
                        "size_bytes": size
                    })

                directories.append({
                    "name": dir_name,
                    "path": f"{dir_name}/",
                    "files": dir_files
                })

            elif entry.is_file():
                file_name = entry.name
                if should_skip_file(file_name, include_hidden):
                    continue

                total_files += 1
                lines = count_lines(entry)
                total_lines += lines
                size = get_file_size(entry)

                if '.' in file_name:
                    ext = '.' + file_name.rsplit('.', 1)[1]
                    extensions[ext] += 1

                root_files.append({
                    "name": file_name,
                    "path": file_name,
                    "lines": lines,
                    "size_bytes": size
                })

    except OSError as e:
        return {"error": f"Failed to scan directory: {e}"}

    return {
        "skill_name": skill_name,
        "skill_path": abs_skill_path,
        "directories": directories,
        "root_files": root_files,
        "statistics": {
            "total_directories": total_dirs,
            "total_files": total_files,
            "total_lines": total_lines,
            "by_extension": dict(sorted(extensions.items()))
        }
    }


def cmd_inventory(args) -> int:
    """Scan skill directory and return structured inventory."""
    skill_path = Path(args.skill_path)

    if not skill_path.exists():
        print(json.dumps({"error": f"Directory not found: {args.skill_path}"}), file=sys.stderr)
        return 1

    if not skill_path.is_dir():
        print(json.dumps({"error": f"Not a directory: {args.skill_path}"}), file=sys.stderr)
        return 1

    skill_path = skill_path.resolve()
    result = scan_directory(skill_path, args.include_hidden)

    if "error" in result:
        print(json.dumps(result), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Plugin validation and inventory tools',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate plugin references
  %(prog)s references --file agent.md

  # Verify cross-file findings
  %(prog)s cross-file --analysis analysis.json --llm-findings findings.json

  # Scan skill inventory
  %(prog)s inventory --skill-path skills/plugin-doctor
"""
    )

    subparsers = parser.add_subparsers(dest='command', help='Operation to perform')

    # references subcommand
    p_refs = subparsers.add_parser('references', help='Validate plugin references')
    p_refs.add_argument('--file', '-f', required=True, help='Path to markdown file')
    p_refs.set_defaults(func=cmd_references)

    # cross-file subcommand
    p_cross = subparsers.add_parser('cross-file', help='Verify cross-file findings')
    p_cross.add_argument('--analysis', '-a', required=True, help='Path to script analysis JSON')
    p_cross.add_argument('--llm-findings', '-l', help='Path to LLM findings JSON (stdin if omitted)')
    p_cross.set_defaults(func=cmd_cross_file)

    # inventory subcommand
    p_inv = subparsers.add_parser('inventory', help='Scan skill inventory')
    p_inv.add_argument('--skill-path', '-s', required=True, help='Path to skill directory')
    p_inv.add_argument('--include-hidden', action='store_true', help='Include hidden files')
    p_inv.set_defaults(func=cmd_inventory)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
