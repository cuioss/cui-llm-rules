#!/usr/bin/env python3
"""
Verify Java implementation parameters for ambiguity and completeness.

Detects ambiguous language, missing information, and unclear requirements
in implementation descriptions before code is written.

Output: JSON with detected issues for Claude to process.
"""

import argparse
import json
import re
import sys
from typing import List, Dict, Any


# Ambiguous language patterns
AMBIGUOUS_PATTERNS = [
    # Modal verbs indicating uncertainty
    (r'\b(should|could|might|may)\s+(probably|possibly|optionally|perhaps)\b', 'uncertain_requirement'),
    (r'\bshould\s+probably\b', 'uncertain_requirement'),
    (r'\bcould\s+(?:maybe|possibly)\b', 'uncertain_requirement'),

    # Vague quantities
    (r'\b(some|several|a few|many|various)\s+\w+', 'vague_quantity'),

    # Conditional/optional phrasing
    (r'\bif\s+needed\b', 'conditional_requirement'),
    (r'\bas\s+appropriate\b', 'conditional_requirement'),
    (r'\bwhen\s+necessary\b', 'conditional_requirement'),
    (r'\bas\s+required\b', 'conditional_requirement'),

    # Ambiguous actions
    (r'\bmaybe\s+\w+', 'uncertain_action'),
    (r'\bperhaps\s+\w+', 'uncertain_action'),
]

# Required information categories
REQUIRED_INFO_CHECKS = {
    'error_handling': [
        r'\b(exception|error|throw|catch)\b'
    ],
    'validation': [
        r'\b(validate|validation|check|verify)\b'
    ],
    'logging': [
        r'\b(log|logging|logger)\b'
    ],
    'return_value': [
        r'\breturn\b',
        r'\b(Optional|null)\b'
    ]
}


def detect_ambiguities(description: str) -> List[Dict[str, Any]]:
    """Detect ambiguous language patterns in description."""
    ambiguities = []

    for pattern, category in AMBIGUOUS_PATTERNS:
        matches = list(re.finditer(pattern, description, re.IGNORECASE))
        for match in matches:
            # Get context (50 chars before and after)
            start = max(0, match.start() - 50)
            end = min(len(description), match.end() + 50)
            context = description[start:end].strip()

            ambiguities.append({
                'pattern': match.group(0),
                'category': category,
                'context': context,
                'position': match.start(),
                'issue': get_issue_description(category)
            })

    return ambiguities


def get_issue_description(category: str) -> str:
    """Get human-readable issue description for category."""
    descriptions = {
        'uncertain_requirement': 'Uncertain requirement - needs definitive specification',
        'vague_quantity': 'Vague quantity - needs specific count or list',
        'conditional_requirement': 'Conditional requirement - needs clear condition',
        'uncertain_action': 'Uncertain action - needs confirmation'
    }
    return descriptions.get(category, 'Ambiguous phrasing detected')


def check_missing_information(description: str) -> List[Dict[str, Any]]:
    """Check for missing required information."""
    missing = []

    # Check error handling
    if re.search(REQUIRED_INFO_CHECKS['validation'][0], description, re.IGNORECASE):
        # Validation mentioned, check if failure behavior specified
        if not re.search(r'\b(throw|return|log)\b.*\b(exception|false|error)\b', description, re.IGNORECASE):
            missing.append({
                'category': 'error_handling',
                'issue': 'Validation mentioned but failure behavior not specified',
                'question': 'What should happen when validation fails? (throw exception, return boolean, return Optional.empty())'
            })

    # Check exception handling
    if re.search(r'\b(IOException|SQLException|Exception)\b', description):
        if not re.search(r'\b(wrap|catch|propagate|handle|throw)\b', description, re.IGNORECASE):
            missing.append({
                'category': 'error_handling',
                'issue': 'Checked exception mentioned but handling strategy not specified',
                'question': 'How should checked exceptions be handled? (wrap in RuntimeException, let propagate, catch and log)'
            })

    # Check logging
    if re.search(REQUIRED_INFO_CHECKS['logging'][0], description, re.IGNORECASE):
        if not re.search(r'\b(DEBUG|INFO|WARN|ERROR|TRACE)\b', description):
            missing.append({
                'category': 'logging',
                'issue': 'Logging mentioned but level not specified',
                'question': 'What logging level should be used? (DEBUG, INFO, WARN, ERROR)'
            })

    # Check return value clarity
    if re.search(r'\breturn\b', description, re.IGNORECASE):
        if not re.search(r'\b(void|Optional|null|empty)\b', description, re.IGNORECASE):
            missing.append({
                'category': 'return_value',
                'issue': 'Return mentioned but null/empty behavior not specified',
                'question': 'Should method return Optional<T>, allow null, or guarantee non-null?'
            })

    return missing


def detect_vague_scope(description: str) -> List[Dict[str, Any]]:
    """Detect vague scope or boundaries."""
    vague_scope = []

    # Check for vague modification targets
    vague_targets = [
        (r'\badd\s+(?:to|in)\s+\w+\s+(?:class|method|interface)\b', 'Vague modification target'),
        (r'\bupdate\s+\w+\b(?!\s+(?:class|method|field))', 'Vague update target'),
        (r'\bmodify\s+(?:the|existing)\b', 'Vague modification scope')
    ]

    for pattern, issue in vague_targets:
        matches = list(re.finditer(pattern, description, re.IGNORECASE))
        for match in matches:
            context = description[max(0, match.start()-30):min(len(description), match.end()+30)].strip()
            vague_scope.append({
                'pattern': match.group(0),
                'issue': issue,
                'context': context,
                'question': 'Specify exact class/method/field names to modify or create'
            })

    return vague_scope


def generate_suggestions(ambiguities: List, missing_info: List, vague_scope: List) -> List[str]:
    """Generate actionable suggestions based on detected issues."""
    suggestions = []

    if ambiguities:
        suggestions.append('Replace uncertain language (should probably, maybe, if needed) with definitive requirements')

    if any(item['category'] == 'error_handling' for item in missing_info):
        suggestions.append('Specify exception handling strategy (throw, wrap, catch and log)')

    if any(item['category'] == 'validation' for item in missing_info):
        suggestions.append('Define validation failure behavior (throw exception, return boolean)')

    if any(item['category'] == 'logging' for item in missing_info):
        suggestions.append('Specify logging level (DEBUG, INFO, WARN, ERROR)')

    if any(item['category'] == 'return_value' for item in missing_info):
        suggestions.append('Clarify null/empty return behavior (Optional, null, guarantee non-null)')

    if vague_scope:
        suggestions.append('Specify exact targets (fully qualified class names, method signatures)')

    if any('vague_quantity' in str(item) for item in ambiguities):
        suggestions.append('Replace vague quantities (some, several, a few) with specific counts or lists')

    return suggestions


def calculate_clarity_score(description: str, ambiguities: List, missing_info: List, vague_scope: List) -> int:
    """Calculate clarity score (0-100)."""
    # Start at 100, deduct for issues
    score = 100

    # Deduct for ambiguities
    score -= len(ambiguities) * 10

    # Deduct for missing information
    score -= len(missing_info) * 15

    # Deduct for vague scope
    score -= len(vague_scope) * 10

    # Bonus for explicit specifications
    if re.search(r'\bthrow\s+\w+Exception\b', description):
        score += 5

    if re.search(r'\b(DEBUG|INFO|WARN|ERROR)\s+level\b', description):
        score += 5

    if re.search(r'\bOptional<\w+>\b', description):
        score += 5

    return max(0, min(100, score))


def verify_parameters(description: str) -> Dict[str, Any]:
    """Main verification function."""
    ambiguities = detect_ambiguities(description)
    missing_info = check_missing_information(description)
    vague_scope = detect_vague_scope(description)
    suggestions = generate_suggestions(ambiguities, missing_info, vague_scope)
    clarity_score = calculate_clarity_score(description, ambiguities, missing_info, vague_scope)

    result = {
        'clarity_score': clarity_score,
        'verification_passed': clarity_score >= 80,
        'total_issues': len(ambiguities) + len(missing_info) + len(vague_scope),
        'ambiguities': ambiguities,
        'missing_information': missing_info,
        'vague_scope': vague_scope,
        'suggestions': suggestions,
        'description_length': len(description),
        'description_word_count': len(description.split())
    }

    return result


def main():
    parser = argparse.ArgumentParser(
        description='Verify Java implementation parameters for ambiguity and completeness',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify implementation description
  %(prog)s --description "Add some validation to UserService"

  # Read from stdin
  echo "Should probably validate email" | %(prog)s

  # Output to file
  %(prog)s --description "..." --output verification.json

Output:
  {
    "clarity_score": 85,
    "verification_passed": true,
    "total_issues": 2,
    "ambiguities": [...],
    "missing_information": [...],
    "suggestions": [...]
  }

Clarity Score:
  100: Perfect clarity, no issues
  80-99: Minor issues, acceptable
  50-79: Moderate issues, needs clarification
  0-49: Severe issues, cannot implement
        """
    )

    parser.add_argument(
        '--description',
        type=str,
        help='Implementation description text to verify'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output JSON file (default: stdout)'
    )

    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty-print JSON output'
    )

    args = parser.parse_args()

    # Read description
    if args.description:
        description = args.description
    else:
        # Read from stdin
        description = sys.stdin.read().strip()

    if not description:
        print("Error: No description provided", file=sys.stderr)
        sys.exit(1)

    # Verify
    result = verify_parameters(description)

    # Output
    indent = 2 if args.pretty else None
    output_json = json.dumps(result, indent=indent)

    if args.output:
        try:
            with open(args.output, 'w') as f:
                f.write(output_json)
        except IOError as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output_json)

    # Exit with status based on verification
    sys.exit(0 if result['verification_passed'] else 1)


if __name__ == '__main__':
    main()
